import time


def generate_draft(project_info: dict, section: str, doc_type: str) -> str:
    """
    DB에 저장된 리스트(project_info['answers'])를 그대로 프롬프트에 넣습니다.
    """

    # 1. 데이터 준비 (이제 변환 과정 불필요!)
    # DB에는 이미 [{"question_id":..., "answer":...}, ...] 형태로 저장되어 있음
    ai_input_data = project_info.get("answers", [])

    # 2. 프롬프트 구성
    # 리스트를 문자열로 변환해서 AI에게 던져줍니다.
    prompt_context = "\n".join([
        f"Q({item['question_id']}): {item['question']}\nA: {item['answer']}"
        for item in ai_input_data
    ])

    prompt = f"""
    당신은 해커톤 멘토입니다. 아래 인터뷰 내용을 바탕으로 '{doc_type}'의 '{section}' 파트를 작성해주세요.

    [인터뷰 데이터]
    {prompt_context}

    [작성 요청]
    - 전문적인 어조로 작성할 것
    - 문단 구분 명확히 할 것
    """

    # 3. AI 로직 시뮬레이션 (OpenAI 호출)
    time.sleep(2)

    return f"[AI Draft 결과]\n'{section}'에 대한 초안입니다.\n\n(내용 기반 생성됨...)"