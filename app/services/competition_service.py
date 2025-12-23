from datetime import datetime
from sqlalchemy.orm import Session
from app.models.competition import Competition
from typing import List, Dict

def get_active_competitions_for_ai(db: Session) -> List[Dict]:
    """
    AI에게 전달하기 위해 현재 유효한(마감일이 지나지 않은) 공고들의
    핵심 정보(지원분야, 대상, 제출서류 등)를 JSON 호환 리스트로 반환합니다.
    """
    # 1. 오늘 날짜 구하기 (YYYY-MM-DD 형식)
    today = datetime.now().strftime("%Y-%m-%d")

    # 2. DB에서 마감일이 오늘 이후(포함)인 공고만 조회
    # deadline 컬럼이 문자열("YYYY-MM-DD") 형식이므로 직접 비교 가능합니다.
    active_competitions = db.query(Competition).filter(Competition.deadline >= today).all()

    competitions_data = []

    for comp in active_competitions:
        # 3. AI에게 필요한 필드만 추출하여 딕셔너리 구성
        comp_info = {
            "id": comp.id,
            "name": comp.name,                  # 공고명 (식별을 위해 필수)
            "tracks": comp.tracks,              # 지원 분야 (List)
            "target": comp.target,              # 대상
            "required_docs": comp.required_docs, # 제출서류 (상세 내용)
        }
        competitions_data.append(comp_info)

    return competitions_data