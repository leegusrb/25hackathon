import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def recommend_with_gpt(startup_profile, competitions, top_k=5):
    system_prompt = """
너는 창업 공모전 추천 AI다.
사전에 정의된 평가 기준에 따라 공모전을 점수화하고,
추천 공모전과 추천 이유 키워드를 도출한다.
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
            f"각 공모전에 대해 평가 기준에 따라 점수를 산정하라.",
            f"총점 기준 상위 {top_k}개 공모전을 추천하라.",
            "각 추천 공모전에 대해 핵심 추천 이유를 키워드 2~4개로 도출하라.",
            "추천 이유는 UI에서 바로 사용할 수 있는 짧은 키워드여야 한다.",
            "아래 JSON 형식으로만 출력하라."
        ],
        "output_format": {
            "recommendation_reasons": {
                "competition_id": {
                    "score": 0,
                    "keywords": []
                }
            }
        }
    }

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
        ]
    )

    return json.loads(response.output_text)
