# 공모전 데이터 (하드코딩)
# 필드 설명:
# - tracks: 추천 알고리즘이 'domain'과 매칭할 태그 (AI, 헬스케어, 핀테크 등)
# - difficulty: 준비 난이도 (쉬움/보통/어려움)
# - target: 지원 대상 (대학생, 예비창업패키지, 일반 등)
# - d_day_label: 마감일 표시용 (가상)

fake_competitions = {
    1: {
        "id": 1,
        "name": "2025 학생 창업 유망팀 300",
        "organizer": "교육부/과학기술정보통신부",
        "d_day_label": "D-14",
        "deadline": "2025-03-31",
        "target": "대학생",
        "difficulty": "보통",
        "tracks": ["전분야", "교육", "플랫폼"],
        "description": "대학생이라면 무조건 도전해야 하는 입문 창업 대회. MVP가 없어도 아이디어만으로 도전 가능.",
        "required_docs": [
            {
                "doc_type": "사업계획서(PSST)",
                "sections": ["문제인식", "해결방안", "성장전략", "팀구성"]
            }
        ],
        "evaluation_points": ["아이디어 독창성", "시장 파급력"]
    },
    2: {
        "id": 2,
        "name": "제10회 AI 활용 캡스톤 디자인 경진대회",
        "organizer": "인공지능산업협회",
        "d_day_label": "D-7",
        "deadline": "2025-02-28",
        "target": "대학생",
        "difficulty": "쉬움",
        "tracks": ["AI", "빅데이터", "SW"],
        "description": "졸업작품이나 캡스톤 디자인 결과물을 그대로 낼 수 있는 대회. 기술 구현도가 중요함.",
        "required_docs": [
            {
                "doc_type": "개발기획서",
                "sections": ["개발동기", "시스템아키텍처", "사용기술", "기대효과"]
            },
            {
                "doc_type": "시연영상",
                "sections": ["기능시연", "코드설명"]
            }
        ],
        "evaluation_points": ["기술 완성도", "AI 모델 성능"]
    },
    3: {
        "id": 3,
        "name": "2025 예비창업패키지 (일반 분야)",
        "organizer": "창업진흥원",
        "d_day_label": "D-25",
        "deadline": "2025-04-15",
        "target": "예비창업자",
        "difficulty": "어려움",
        "tracks": ["전분야", "O2O", "제조"],
        "description": "최대 1억 원 지원. 사업자 등록이 없는 예비 대표자만 지원 가능. 서류 양이 많고 구체적인 BM 필수.",
        "required_docs": [
            {
                "doc_type": "사업계획서(표준양식)",
                "sections": ["문제인식", "실현가능성", "성장전략", "팀구성"]
            },
            {
                "doc_type": "자금소요계획",
                "sections": ["인건비", "마케팅비", "개발비"]
            }
        ],
        "evaluation_points": ["사업화 가능성", "자금 집행 계획"]
    },
    4: {
        "id": 4,
        "name": "공공데이터 활용 비즈니스 아이디어 공모전",
        "organizer": "행정안전부",
        "d_day_label": "D-40",
        "deadline": "2025-05-10",
        "target": "전국민",
        "difficulty": "보통",
        "tracks": ["공공데이터", "앱개발", "사회문제해결"],
        "description": "공공데이터포털의 API를 활용한 서비스 기획. 사회적 가치 창출이 중요 포인트.",
        "required_docs": [
            {
                "doc_type": "기획서",
                "sections": ["활용데이터", "서비스개요", "창출가치"]
            }
        ],
        "evaluation_points": ["데이터 활용 적절성", "사회적 가치"]
    },
    5: {
        "id": 5,
        "name": "2025 헬스케어 스타트업 챌린지",
        "organizer": "보건산업진흥원",
        "d_day_label": "D-10",
        "deadline": "2025-03-15",
        "target": "스타트업",
        "difficulty": "어려움",
        "tracks": ["헬스케어", "바이오", "디지털치료제"],
        "description": "병원/의료 데이터 연계 필수. 규제 샌드박스 관련 내용이 포함되면 가산점.",
        "required_docs": [
            {
                "doc_type": "IR Deck",
                "sections": ["Problem", "Solution", "Market", "Regulatory", "Team"]
            }
        ],
        "evaluation_points": ["임상 적용 가능성", "규제 해결 방안"]
    },
    6: {
        "id": 6,
        "name": "핀테크 아이디어톤",
        "organizer": "금융결제원",
        "d_day_label": "D-3",
        "deadline": "2025-02-25",
        "target": "대학생/일반인",
        "difficulty": "쉬움",
        "tracks": ["핀테크", "금융", "보안"],
        "description": "무박 2일 해커톤 형식. 오픈뱅킹 API를 활용한 참신한 아이디어 발굴.",
        "required_docs": [
            {
                "doc_type": "참가신청서",
                "sections": ["참가동기", "아이디어요약"]
            }
        ],
        "evaluation_points": ["아이디어 참신성", "현장 구현 능력"]
    }
}

# 프로젝트 저장소 (메모리 DB - 초기화 상태)
fake_projects = {}