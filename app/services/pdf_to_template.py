import os
import json
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from pypdf import PdfReader
from jsonschema import validate, ValidationError
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# (NEW) 기본 공모전 어필 전략 예시(고정 텍스트)
# ----------------------------
DEFAULT_CONTEST_STRATEGY = {
    "contest_pitch": (
        "본 아이템은 대학 기반 창업팀이 공모전 준비 과정에서 겪는 반복적인 서류 작성·정보 탐색·일정 관리 부담을 줄여 "
        "지원사업 준비의 리스크(마감 누락, 평가포인트 누락)를 낮추는 도구입니다. "
        "또한 창업지원단/캠퍼스타운 운영 측면에서는 지원팀 관리의 표준화와 운영 효율을 높여, "
        "동일 자원으로 더 많은 팀을 지원하고 성과 확산을 촉진하는 방향으로 연결될 수 있습니다."
    ),
    "contest_keywords": [
        "캠퍼스타운", "대학 창업", "운영 효율", "표준화", "성과 확산", "실행력", "파일럿", "확장성"
    ],
    "contest_do_dont": {
        "do": [
            "대학/캠퍼스타운 환경에서 즉시 파일럿 가능한 범위로 계획을 좁혀 제시",
            "지원기관(B2B) 관점 효익(운영시간 절감, 서류 품질 균일화, 지원팀 확대 가능성)을 명확히 강조",
            "협약기간 내 달성 가능한 산출물(와이어프레임→프로토타입→파일럿) 중심으로 로드맵 구체화"
        ],
        "dont": [
            "확보하지 않은 성과/수치(사용자 수, 제휴, 매출)를 단정적으로 기재",
            "너무 광범위한 시장(전국 모든 스타트업)부터 언급해 초점을 흐리기",
            "기술 설명만 길고 공모전/캠퍼스타운 취지와의 연결이 약한 서술"
        ]
    }
}

# ----------------------------
# 1) PDF 텍스트 추출
# ----------------------------
def extract_pdf_text(pdf_path: str, max_chars: int = 120_000) -> str:
    reader = PdfReader(pdf_path)
    chunks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            chunks.append(f"\n\n[PAGE {i+1}]\n{text}")
    full_text = "".join(chunks).strip()

    if len(full_text) > max_chars:
        head = full_text[: max_chars // 2]
        tail = full_text[-max_chars // 2 :]
        full_text = head + "\n\n...[TRUNCATED]...\n\n" + tail

    return full_text


# ----------------------------
# 2) template.json 스키마(최소 보장)
#   - contest_* 필드 추가(선택 필드)
# ----------------------------
TEMPLATE_SCHEMA = {
    "type": "object",
    "required": ["competition_id", "competition_name", "doc_type", "evaluation_points", "priorities", "sections"],
    "properties": {
        "competition_id": {"type": "string"},
        "competition_name": {"type": "string"},
        "doc_type": {"type": "string", "enum": ["business_plan"]},
        "evaluation_points": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "label", "hint"],
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string"},
                    "hint": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "priorities": {"type": "array", "items": {"type": "string"}},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["section_id", "title", "guideline", "target_chars", "use_from", "emphasize_points"],
                "properties": {
                    "section_id": {"type": "string"},
                    "title": {"type": "string"},
                    "guideline": {"type": "string"},
                    "target_chars": {"type": "integer"},
                    "use_from": {"type": "array", "items": {"type": "string"}},
                    "emphasize_points": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": False,
            },
        },

        # ✅ NEW (optional)
        "contest_pitch": {"type": "string"},
        "contest_keywords": {"type": "array", "items": {"type": "string"}},
        "contest_do_dont": {
            "type": "object",
            "required": ["do", "dont"],
            "properties": {
                "do": {"type": "array", "items": {"type": "string"}},
                "dont": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}


# ----------------------------
# 3) LLM에게 PDF -> template.json 생성
#    + (NEW) contest_* 예시글도 포함하도록 유도
# ----------------------------
def llm_make_template(pdf_text: str, default_competition_id: str = "unknown_competition") -> Dict[str, Any]:
    system = (
        "너는 '공모전 사업계획서 PDF 양식/안내문'을 읽고, "
        "해당 문서가 요구하는 사업계획서 작성 구조를 JSON 템플릿으로 정리하는 도우미다.\n\n"
        "중요:\n"
        "- 출력은 반드시 JSON 하나만 반환한다(설명/마크다운 금지).\n"
        "- 섹션(목차)이 PDF에 명시되어 있으면 그걸 우선 반영한다.\n"
        "- 평가항목(심사기준)이 PDF에 있으면 evaluation_points에 반영한다.\n"
        "- target_chars가 PDF에 없으면, 섹션 성격에 따라 300~800 사이로 합리적으로 추정한다.\n"
        "- priorities는 PDF에서 '가중치/중요도' 언급이 있으면 반영하고, 없으면 상위 3개를 합리적으로 선택한다.\n"
        "- section_id, evaluation id는 snake_case로 만들고 중복되지 않게 한다.\n"
        "- doc_type은 business_plan으로 고정한다.\n"
        "- 추가로 contest_pitch/contest_keywords/contest_do_dont 필드를 포함하라.\n"
        "  (PDF에 특화 전략이 명시되어 있으면 반영하고, 없으면 입력으로 주어진 예시를 그대로 사용해도 된다.)\n"
        " PDF에 번호가 붙은 목차(예: 4-1, 4-2)가 존재하면 절대 합치지 말고 각각 별도 섹션으로 유지하라.\n"
        "섹션 제목(title)은 PDF의 제목 문구를 최대한 그대로 사용하라(의미 요약/병합 금지)."
    )

    user = {
        "task": "다음 PDF 텍스트를 기반으로 template.json을 생성하라.",
        "default_competition_id": default_competition_id,
        "contest_strategy_example": DEFAULT_CONTEST_STRATEGY,  # ✅ 예시 제공(그대로 써도 됨)
        "output_format_example": {
            "competition_id": "sejong_campustown_2025",
            "competition_name": "세종대학교 캠퍼스타운 입주경진대회(예시)",
            "doc_type": "business_plan",
            "contest_pitch": DEFAULT_CONTEST_STRATEGY["contest_pitch"],
            "contest_keywords": DEFAULT_CONTEST_STRATEGY["contest_keywords"],
            "contest_do_dont": DEFAULT_CONTEST_STRATEGY["contest_do_dont"],
            "evaluation_points": [
                {"id": "problem_urgency", "label": "문제의 명확성/시급성", "hint": "..."}
            ],
            "priorities": ["problem_urgency", "impact", "feasibility"],
            "sections": [
                {
                    "section_id": "bg_need",
                    "title": "1-1. 배경 및 필요성",
                    "guideline": "왜 이 문제가 중요한지...",
                    "target_chars": 500,
                    "use_from": ["overview", "problem_target"],
                    "emphasize_points": ["problem_urgency", "impact"]
                }
            ]
        },
        "pdf_text": pdf_text
    }

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)}
        ],
    )

    content = resp.choices[0].message.content.strip()

    # LLM이 JSON 외 텍스트를 섞는 경우 대비
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        data = json.loads(content[start:end + 1])

    # ✅ NEW: contest_* 필드가 빠졌으면 기본 예시 주입
    if "contest_pitch" not in data:
        data["contest_pitch"] = DEFAULT_CONTEST_STRATEGY["contest_pitch"]
    if "contest_keywords" not in data:
        data["contest_keywords"] = DEFAULT_CONTEST_STRATEGY["contest_keywords"]
    if "contest_do_dont" not in data:
        data["contest_do_dont"] = DEFAULT_CONTEST_STRATEGY["contest_do_dont"]

    return data


# ----------------------------
# 5) 실행 엔트리
# ----------------------------
def main(pdf_path: str, competition_id: Optional[str] = None):
    pdf_text = extract_pdf_text(pdf_path)
    if not pdf_text:
        raise ValueError("PDF에서 텍스트를 추출하지 못했습니다. (스캔본 PDF일 가능성)")

    default_id = competition_id or "unknown_competition"
    return llm_make_template(pdf_text, default_competition_id=default_id)
