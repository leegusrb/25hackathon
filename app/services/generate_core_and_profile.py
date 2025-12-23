import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

STAGE_MAP = {
    "아이디어": "idea",
    "와이어프레임": "wireframe",
    "MVP": "mvp_partial",
    "MVP 일부": "mvp_partial",
    "데모": "demo_ready",
    "데모 가능": "demo_ready",
}

DOMAIN_CANDIDATES = ["AI", "교육", "헬스케어", "핀테크", "커뮤니티", "생산성", "기타"]
SUPPORT_CANDIDATES = [
    "사업화", "기술개발(R&D)", "시설·공간·보육", "멘토링·컨설팅·교육",
    "네트워킹·행사", "융자", "인력", "글로벌"
]

def safe_json_load(text: str):
    text = (text or "").strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1].strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()
    first_brace = text.find("{")
    first_bracket = text.find("[")
    candidates = [i for i in [first_brace, first_bracket] if i != -1]
    start = min(candidates) if candidates else -1
    if start > 0:
        text = text[start:]
    return json.loads(text)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def generate_core_and_profile(items: list) -> dict:
    system_prompt = (
        "너는 질문-답변(items)을 기반으로 창업 아이템 정보를 '의미 구조(semantic slots)'로 정리하는 AI다.\n"
        "중요:\n"
        "- 입력에 없는 사실(성과/수치/제휴/검증/사용자수 등)을 절대 만들지 마라.\n"
        "- 가능한 한 입력의 표현을 보존하되, 문서 생성에 쓰기 좋게 간결히 정리하라.\n"
        "- 출력은 JSON만.\n"
    )

    output_schema = {
        "startup_item_core": {
            "language": "ko",
            "core": {
                "service_name": "",
                "one_liner": "",
                "motivation": "",
                "problem": {
                    "summary": "",
                    "pain_points": [],
                    "root_causes": []
                },
                "target_customer": {
                    "primary": "",
                    "persona": "",
                    "needs": []
                },
                "current_alternatives": [],
                "solution": {
                    "summary": "",
                    "core_features": [],
                    "differentiation": ""
                },
                "feasibility": {
                    "stage_raw": "",
                    "stage": "idea|wireframe|mvp_partial|demo_ready",
                    "evidence": "",
                    "next_steps": []
                },
                "business_model": {
                    "summary": "",
                    "revenue_model": "",
                    "pricing_hint": ""
                },
                "go_to_market": {
                    "initial_target": "",
                    "channels": []
                },
                "growth_expansion": {
                    "summary": "",
                    "directions": []
                },
                "team": {
                    "members": [],
                    "fit_reason": ""
                }
            }
        },
        "startup_reco_profile": {
            "team_type": "university_student",
            "stage": "idea|wireframe|mvp_partial|demo_ready",
            "domains": [],
            "core_features": [],
            "needed_support": [],
            "doc_readiness": {
                "problem_defined": True,
                "solution_defined": True,
                "business_defined": True,
                "team_defined": True
            }
        }
    }

    user_prompt = {
        "task": "Generate semantic core JSON + reco profile",
        "items": items,
        "constraints": {
            "stage_map": STAGE_MAP,
            "domain_candidates": DOMAIN_CANDIDATES,
            "support_candidates": SUPPORT_CANDIDATES
        },
        "rules": [
            "startup_item_core.core 하위의 모든 필드는 존재해야 한다(값이 없으면 빈 문자열/빈 리스트).",
            "문장/리스트는 중복 제거, 너무 길지 않게.",
            "feasibility.stage는 stage_map으로 정규화해 1개 선택.",
            "startup_reco_profile.core_features는 5~8개 항목으로 구성(현재 단계 1개 + 기능/차별점 중심).",
            "domains는 1~3개 선택, 근거 부족하면 ['기타'].",
            "needed_support는 support_candidates 중 0~5개 선택.",
            "doc_readiness는 각 영역 관련 답변이 있으면 true."
        ],
        "output_schema": output_schema
    }

    resp = client.responses.create(
        model="gpt-5-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
        ]
    )

    return safe_json_load(resp.output_text)

if __name__ == "__main__":
    items = load_json("question.json")
    out = generate_core_and_profile(items)

    save_json("startup_item_core.json", out["startup_item_core"])
    save_json("startup_reco_profile.json", out["startup_reco_profile"])

    print("startup_item_core.json / startup_reco_profile.json 생성 완료")
