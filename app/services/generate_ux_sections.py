import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def safe_json_load(text: str):
    """모델 출력이 코드펜스/앞뒤 텍스트를 섞어도 최대한 JSON만 파싱."""
    text = text.strip()

    # ```json ... ``` 형태 제거
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1].strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

    # JSON 객체/배열 시작 위치부터 잘라보기
    first_brace = text.find("{")
    first_bracket = text.find("[")
    candidates = [i for i in [first_brace, first_bracket] if i != -1]
    start = min(candidates) if candidates else -1
    if start > 0:
        text = text[start:]

    return json.loads(text)

def generate_ux_sections(items):
    system_prompt = (
        "너는 대학생 창업팀을 위한 PM 비서 AI다.\n"
        "입력은 질문-답변 목록(items[])이며,\n"
        "출력은 사용자가 바로 읽을 수 있는 '파트별 요약 글' JSON이다.\n"
        "반드시 JSON만 출력하고, JSON 이외의 텍스트를 절대 출력하지 마라.\n"
        "입력에 없는 사실을 과장하거나 만들어내지 마라."
    )

    user_prompt = {
        "instruction": [
            "items를 종합해 아래 5개 파트로 '그럴싸한 소개/정리 글'을 작성하라.",
            "각 파트는 content(2~3문장) + bullets(2~4개)로 작성하라.",
            "문서처럼 딱딱하지 않게, 해커톤 데모에서 설득력 있게 정리하라.",
            "입력에 없는 사실(성과/지표/제휴/수치 등)은 절대 만들지 마라.",
            "출력은 output_schema 구조를 정확히 따르는 JSON만 반환하라."
        ],
        "parts": [
            "서비스 개요",
            "문제 & 타겟",
            "솔루션 & 차별성",
            "사업화 방향",
            "팀 역량"
        ],
        "items": items,
        "output_schema": {
            "language": "ko",
            "sections": [
                {"key": "overview", "title": "서비스 개요", "content": "", "bullets": []},
                {"key": "problem_target", "title": "문제 & 타겟", "content": "", "bullets": []},
                {"key": "solution_diff", "title": "솔루션 & 차별성", "content": "", "bullets": []},
                {"key": "biz", "title": "사업화 방향", "content": "", "bullets": []},
                {"key": "team", "title": "팀 역량", "content": "", "bullets": []}
            ]
        }
    }

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
        ]
    )

    return safe_json_load(response.output_text)
