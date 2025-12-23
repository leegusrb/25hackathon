# 공모전 데이터 (하드코딩)
fake_competitions = {
    1: {
        "id": 1,
        "name": "2025 학생 창업 유망팀 300 (U300)",
        "organizer": "교육부/과학기술정보통신부",
        "deadline": "2025-03-31",
        "tracks": ["전분야", "기술창업", "교육"],
        "eligibility": "전국 대학(원)생 및 휴학생 (팀 단위)",
        "url": "https://www.u300.or.kr",
        "description": "대학생이라면 무조건 도전해야 하는 입문 창업 대회. MVP가 없어도 아이디어만으로 도전 가능.",
        "required_docs": [
            {
                "doc_type": "사업계획서(PSST)",
                "sections": ["문제인식", "해결방안", "성장전략", "팀구성"]
            }
        ]
    },
    2: {
        "id": 2,
        "name": "제13회 범정부 공공데이터 활용 창업경진대회",
        "organizer": "행정안전부",
        "deadline": "2025-05-10",
        "tracks": ["아이디어 기획", "제품/서비스 개발", "공공데이터"],
        "eligibility": "공공데이터를 활용한 창업 아이디어를 가진 누구나",
        "url": "https://www.startupidea.kr",
        "description": "공공데이터포털 API를 활용해야 함. 사회적 가치 창출이 중요 포인트.",
        "required_docs": [
            {
                "doc_type": "기획서",
                "sections": ["활용데이터", "서비스개요", "창출가치"]
            }
        ]
    },
    3: {
        "id": 3,
        "name": "2025 예비창업패키지 (일반 분야)",
        "organizer": "창업진흥원",
        "deadline": "2025-02-28",
        "tracks": ["전분야", "IT/SW", "제조"],
        "eligibility": "사업자 등록이 없는 예비창업자",
        "url": "https://www.k-startup.go.kr",
        "description": "최대 1억 원 지원. 서류 양이 많고 구체적인 BM 필수.",
        "required_docs": [
            {
                "doc_type": "사업계획서(표준양식)",
                "sections": ["문제인식", "실현가능성", "성장전략", "팀구성"]
            }
        ]
    },
    4: {
        "id": 4,
        "name": "제5회 인공지능(AI) 챔피언십",
        "organizer": "중소벤처기업부",
        "deadline": "2025-06-15",
        "tracks": ["AI", "빅데이터", "알고리즘"],
        "eligibility": "AI 기술을 보유한 스타트업 및 예비창업팀",
        "url": "https://www.k-startup.go.kr",
        "description": "대기업이 제시한 난제를 AI로 해결하는 대회. 기술력이 핵심.",
        "required_docs": [
            {
                "doc_type": "기술제안서",
                "sections": ["해결알고리즘", "데이터활용방안", "기대성능"]
            }
        ]
    },
    5: {
        "id": 5,
        "name": "2025 핀테크 아이디어톤",
        "organizer": "한국핀테크지원센터",
        "deadline": "2025-04-20",
        "tracks": ["핀테크", "금융", "보안"],
        "eligibility": "핀테크 서비스에 관심 있는 대학생 및 일반인",
        "url": "https://fintech.or.kr",
        "description": "금융 API를 활용한 참신한 서비스 기획.",
        "required_docs": [
            {
                "doc_type": "아이디어제안서",
                "sections": ["서비스컨셉", "타겟고객", "수익모델"]
            }
        ]
    }
}

# 프로젝트 저장소 (메모리 DB)
fake_projects = {}