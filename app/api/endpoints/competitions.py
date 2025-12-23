from fastapi import APIRouter, HTTPException
from app.schemas.competition import CompetitionDetail
from app.db.mock_data import fake_competitions

router = APIRouter()

@router.get("/{competition_id}", response_model=CompetitionDetail)
def get_competition_detail(competition_id: int):
    if competition_id not in fake_competitions:
        raise HTTPException(status_code=404, detail="Competition not found")
    return fake_competitions[competition_id]