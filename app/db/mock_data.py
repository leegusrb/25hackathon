# 공모전 데이터 (하드코딩)
fake_competitions = {
    1: {
        "id": 1,
        "name": "2024 학생 창업 유망팀 300",
        "required_docs": [
            {
                "doc_type": "사업계획서",
                "sections": ["문제정의", "솔루션", "시장분석", "경쟁우위", "비즈니스모델"]
            },
            {
                "doc_type": "팀소개서",
                "sections": ["팀원구성", "팀역량", "포부"]
            }
        ]
    }
}

# 프로젝트 저장소 (메모리 DB)
fake_projects = {}