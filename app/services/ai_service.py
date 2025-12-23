import time


def generate_draft(project_info: dict, section: str, doc_type: str) -> str:
    """
    AI 담당자가 구현할 함수.
    지금은 Mock이지만, 나중에 여기에 OpenAI API 호출 코드를 넣으면 됩니다.
    """

    # 1. AI 로직 시뮬레이션 (시간 소요)
    time.sleep(2)

    # 2. 프롬프트 구성 (나중에 구현)
    item_desc = project_info.get("common_info", {}).get("item_desc", "아이템")

    # 3. 결과 반환
    result_text = (
        f"[AI Draft] '{item_desc}' 아이템을 위한 '{doc_type}'의 '{section}' 파트입니다.\n\n"
        f"저희 팀은 기술적 해결책을 통해 학생 창업의 진입 장벽을 낮추고자 합니다.\n"
        f"(여기에 실제 GPT가 생성한 문장이 들어갑니다...)"
    )

    return result_text