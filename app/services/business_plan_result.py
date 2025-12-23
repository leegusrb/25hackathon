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


    # (Invalid control character 방지)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)


    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        text = text[first:last + 1]

    return json.loads(text)

def filter_eval_points(template: dict, emphasize_ids: list) -> list:
    all_points = template.get("evaluation_points", [])
    id_set = set(emphasize_ids or [])
    if not id_set:
        return []
    return [p for p in all_points if p.get("id") in id_set]

def generate_section_draft(section_meta: dict, core: dict, template: dict) -> dict:
    system_prompt = (
        "너는 공모전 사업계획서 작성 보조 AI다.\n"
        "사용자가 제공한 core(창업 아이템 의미 구조)만 근거로 해당 섹션 초안을 작성하라.\n"
        "core에 없는 사실(성과/수치/제휴/검증결과/사용자 수 등)을 절대 만들지 마라.\n"
        "평가포인트는 '강조 방향'일 뿐, 없는 내용을 만들어내는 근거가 아니다.\n"
        "반드시 JSON만 출력하라."
    )

    emphasize_ids = section_meta.get("emphasize_points", template.get("priorities", []))
    emphasize_points = filter_eval_points(template, emphasize_ids)

    user_prompt = {
        "task": "문서 섹션 초안 작성",
        "section": {
            "section_id": section_meta.get("section_id", ""),
            "title": section_meta.get("title", ""),
            "guideline": section_meta.get("guideline", ""),
            "target_chars": section_meta.get("target_chars", 500)
        },
        "core": core,
        "evaluation_focus": {
            "points": emphasize_points,
            "instruction": [
                "아래 평가포인트를 문장에 자연스럽게 반영하라.",
                "core에 없는 내용은 새로 만들지 말고, 표현을 '목표/계획/의도' 중심으로 작성하라."
            ]
        },
        "writing_rules": [
            "한국어로 자연스럽게 작성",
            "target_chars ±15% 범위로 맞추기",
            "문단은 2~4개로 나누고, 너무 장황하지 않게",
            "심사위원 관점에서 읽히도록, 주장-근거-효과 흐름을 유지",
            "불릿을 억지로 만들지 말고 자연스러운 문장형으로 작성"
        ],
        "output_schema": {
            "section_id": "",
            "title": "",
            "draft_text": ""
        }
    }


    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "section_id": {"type": "string"},
            "title": {"type": "string"},
            "draft_text": {"type": "string"}
        },
        "required": ["section_id", "title", "draft_text"]
    }

    def call_llm(extra_system_note=""):
        return client.responses.create(
            model="gpt-5-mini",
            input=[
                {"role": "system", "content": system_prompt + extra_system_note},
                {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
            ],
            text={"format": {"type": "json_schema", "name": "section_draft", "schema": schema}}
        )

    # 1차 호출
    resp = call_llm()

    try:
        return safe_json_load(resp.output_text)
    except Exception:
        resp2 = call_llm("\n주의: 반드시 위 JSON 스키마를 만족하는 '순수 JSON'만 출력해라.")
        return safe_json_load(resp2.output_text)

def generate_business_plan(core: dict, template: dict) -> dict:
    output = {"sections": []}

    for sec in template.get("sections", []):
        draft = generate_section_draft(sec, core, template)

        cleaned = {
            "section_id": draft.get("section_id", sec.get("section_id", "")),
            "title": draft.get("title", sec.get("title", "")),
            "draft_text": draft.get("draft_text", "")
        }
        output["sections"].append(cleaned)

    return output

def load_startup_core(path="startup_item_core.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1) {"startup_item_core": {"core": {...}}}
    if isinstance(data, dict) and "startup_item_core" in data:
        return data["startup_item_core"].get("core", {})

    # 2) {"language":"ko","core": {...}}
    return data.get("core", {})

if __name__ == "__main__":
    core = load_startup_core("startup_item_core.json")

    with open("template.json", "r", encoding="utf-8") as f:
        template = json.load(f)

    result = generate_business_plan(core, template)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    with open("business_plan_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("business_plan_result.json 생성 완료")
