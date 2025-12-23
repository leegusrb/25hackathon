from fastapi import APIRouter, HTTPException
from typing import List
import random

from app.schemas.competition import CompetitionDetail
from app.db.mock_data import fake_competitions

router = APIRouter()


# [기능 1-2] 공모전 추천 API (현재: 랜덤 3개 반환)
# 나중에는 POST로 바꾸고 사용자 입력(domain, interest)을 받아서 필터링해야 함
@router.get("/recommend", response_model=List[CompetitionDetail])
def recommend_competitions():
    """
    전체 공모전 목록 중 랜덤으로 3개를 선택하여 반환합니다.
    (데이터가 3개 미만이면 전체를 반환)
    """
    all_competitions = list(fake_competitions.values())

    # 데이터가 적을 경우 에러 방지
    if len(all_competitions) <= 3:
        return all_competitions

    return random.sample(all_competitions, 3)


# [기능 1-3] 공모전 상세 조회
@router.get("/{competition_id}", response_model=CompetitionDetail)
def get_competition_detail(competition_id: int):
    if competition_id not in fake_competitions:
        raise HTTPException(status_code=404, detail="Competition not found")
    return fake_competitions[competition_id]