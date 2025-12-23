from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any

from sqlalchemy import JSON


# [기존 코드 유지] 질문-답변 쌍
class QAPair(BaseModel):
    question_id: str
    question: str
    answer: str


# [기존 코드 유지] 프로젝트 생성 스키마
class ProjectCreate(BaseModel):
    team_name: str
    answers: List[QAPair]


# [수정] 프로젝트 응답 스키마
class ProjectResponse(ProjectCreate):
    id: int
    answers: List[QAPair]
    startup_item_core: Dict[str, Any] = {}
    startup_reco_profile: Dict[str, Any] = {}
