import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def safe_json_load(text: str):
    text = (text or "").strip()

    # ```json ... ``` 제거
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1].strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

    # 제어문자 제거(Invalid control character 방지)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)

    # 앞뒤 군더더기 제거
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        text = text[first:last + 1]

    return json.loads(text)

def recommend_with_gpt(startup_profile, competitions, top_k=5):
    system_prompt = """
너는 창업 공모전 추천 AI다.
사전에 정의된 평가 기준에 따라 공모전을 점수화하고,
상위 공모전 목록과 추천 이유 키워드, 그리고 필수 제출서류 목록을 도출한다.

중요:
- competitions에 있는 정보만 사용해라. 없는 제출서류를 지어내지 마라.
- 제출서류는 가능한 한 리스트로 정규화하되, 애매하면 원문을 그대로 한 항목으로 넣어라.
- 출력은 반드시 JSON만.
"""

    user_prompt = {
        "task": "창업 아이템 정보와 공모전 목록을 비교해 추천하라.",
        "evaluation_criteria": {
            "target_fit": "대학생·예비창업자·초기팀 대상 여부 (0~4점)",
            "stage_fit": "아이디어/초기 MVP 단계 적합성 (0~3점)",
            "support_match": "지원 유형과 현재 니즈의 일치도 (0~3점)",
            "preparation_effort": "제출 서류·증빙 부담 (0~-2점)"
        },
        "startup_profile": startup_profile,
        "competitions": competitions,
        "instructions": [
            "각 공모전에 대해 평가 기준에 따라 점수를 산정하라.",
            f"총점 기준 상위 {top_k}개 공모전을 추천하라.",
            "각 추천 공모전에 대해 핵심 추천 이유를 키워드 2~4개로 도출하라.",
            "추가로, 각 추천 공모전의 '필수 제출서류'를 competitions 데이터에서 찾아 리스트로 정리하라.",
            "제출서류는 공모전 데이터의 제출/서류/제출서류/필수서류/attachments 같은 필드 또는 설명 텍스트에서 추출하라.",
            "제출서류를 찾지 못하면 required_documents는 빈 리스트([])로 둬라.",
            "아래 output_schema 형식으로만 출력하라."
        ],
        "output_schema": {
            "recommendations": [
                {
                    "competition_id": "",
                    "score": 0,
                    "keywords": [],
                    "required_documents": []
                }
            ]
        }
    }

    # ✅ 동적 키 제거: recommendations 배열로 고정
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "competition_id": {"type": "string"},
                        "score": {"type": "number"},
                        "keywords": {"type": "array", "items": {"type": "string"}},
                        "required_documents": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["competition_id", "score", "keywords", "required_documents"]
                }
            }
        },
        "required": ["recommendations"]
    }

    resp = client.responses.create(
        model="gpt-5-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
        ],
        text={"format": {"type": "json_schema", "name": "reco_output", "schema": schema}}
    )

    try:
        return safe_json_load(resp.output_text)
    except Exception:
        # 재시도
        resp2 = client.responses.create(
            model="gpt-5-mini",
            input=[
                {"role": "system", "content": system_prompt + "\n반드시 JSON 스키마를 만족하는 순수 JSON만 출력해라."},
                {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
            ],
            text={"format": {"type": "json_schema", "name": "reco_output", "schema": schema}}
        )
        return safe_json_load(resp2.output_text)
