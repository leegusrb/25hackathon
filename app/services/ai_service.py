import time
import json
from typing import List, Dict


# 반환 타입을 str -> dict로 변경
def generate_project_analysis(project_info: dict, doc_type: str = "기획서") -> Dict:
    """
    DB에 저장된 리스트(project_info['answers'])를 바탕으로
    분석 결과(JSON)를 생성하여 반환합니다.
    """

    # 1. 데이터 준비
    ai_input_data = project_info.get("answers", [])

    # 프롬프트 구성 (실제 AI 호출 시 사용)
    prompt_context = "\n".join([
        f"Q({item['question_id']}): {item['question']}\nA: {item['answer']}"
        for item in ai_input_data
    ])

    print(f"[AI Service] Prompt Context Generated ({len(prompt_context)} chars)")

    # 2. AI 로직 시뮬레이션 (OpenAI 호출 대기)
    time.sleep(2)

    # 3. [Mock] 결과 반환 (제공해주신 sections_result.json 내용)
    # 실제 구현 시에는 OpenAI의 'Function Calling'이나 'JSON Mode'를 사용하여 이 구조를 받아야 함
    mock_result = {
        "language": "ko",
        "sections": [
            {
                "key": "overview",
                "title": "서비스 개요",
                "content": "STARTMATE는 대학생 창업팀이 공모전 준비를 쉽게 하도록 추천·서류·일정을 자동화하는 서비스입니다. 반복되는 양식 작성과 촉박한 마감 관리를 줄여 팀이 아이디어와 개발에 더 집중하도록 돕습니다.",
                "bullets": [
                    "공모전 추천·서류 자동 생성·마감 역산 일정 관리를 목표로 설계됨",
                    "공모전 준비 과정을 한곳에서 관리해 작업 중복을 줄임",
                    "팀이 빠르게 준비하고 마감에 대응하도록 지원"
                ]
            },
            {
                "key": "problem_target",
                "title": "문제 & 타겟",
                "content": "공모전마다 요구 양식이 달라 문서 작성이 반복되고 마감 대응이 어려운 것이 핵심 문제입니다. 이 문제를 가장 크게 겪는 대상은 아이디어~MVP 단계에 있는 대학생 창업팀입니다.",
                "bullets": [
                    "공모전별 문서 양식 차이로 매번 새로 작성해야 함",
                    "마감 직전에 일정 관리가 되지 않아 문제가 발생함",
                    "기존 대응: 템플릿 복붙, GPT로 일부 작성, 노션/엑셀 일정 관리"
                ]
            },
            {
                "key": "solution_diff",
                "title": "솔루션 & 차별성",
                "content": "핵심 기능은 공모전 추천, 서류 자동 생성, 마감 역산 일정 관리이며, 이를 통해 준비 과정을 자동화합니다. 단순 문장 생성이 아니라 창업 정보를 구조화해 공모전 양식에 맞게 조합하는 점이 주요 차별성입니다.",
                "bullets": [
                    "핵심 기능: 공모전 추천 / 서류 자동 생성 / 마감 역산 일정 관리",
                    "창업 정보를 구조화해 공모전 양식에 맞게 조합하는 방식으로 차별화",
                    "현재 구현 수준은 아이디어 단계"
                ]
            },
            {
                "key": "biz",
                "title": "사업화 방향",
                "content": "초기에는 대학생 팀에게는 무료로 제공하고, 창업지원단에는 B2B 라이선스로 수익을 창출하는 모델을 염두에 두고 있습니다. 먼저 교내 창업동아리와 캠퍼스타운 참여팀 도입에 집중해 사용 사례를 만들 계획입니다.",
                "bullets": [
                    "수익 모델: 대학생 팀은 무료, 창업지원단 대상 B2B 라이선스",
                    "초기 집중 도입 대상: 교내 창업동아리, 캠퍼스타운 참여팀",
                    "확장 방향: 타 대학 확장 / 다른 공모전 DB 추가 / 초기 스타트업 시장 진출"
                ]
            },
            {
                "key": "team",
                "title": "팀 역량",
                "content": "팀은 공모전 준비 경험을 공유하고 AI·웹 개발 역량을 보유해 서비스 구현에 적합합니다. 역할 분담이 명확해 아이디어를 제품으로 구체화할 준비가 되어 있습니다.",
                "bullets": [
                    "구성: 홍길동 – AI (문서 구조화 모델 구현), 김OO – FE (웹 UI/UX 구현)",
                    "팀 전원이 공모전 준비 경험 보유",
                    "AI와 웹 개발을 직접 구현할 수 있는 기술 역량 보유"
                ]
            }
        ]
    }

    return mock_result