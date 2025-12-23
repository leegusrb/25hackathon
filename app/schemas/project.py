from pydantic import BaseModel
from typing import List, Optional, Dict

# [수정] 질문-답변 쌍 하나를 나타내는 스키마
class QAPair(BaseModel):
    question_id: str  # 예: "1-1"
    question: str     # 예: "서비스 이름이 뭔가요?"
    answer: str       # 예: "STARTMATE"

# [수정] 메인 생성 스키마
class ProjectCreate(BaseModel):
    # 필터링용 핵심 데이터 (DB 컬럼으로 따로 관리되는 애들)
    team_name: str
    domain: str
    stage: str
    target_award: str

    # [핵심 변경] 계층형 객체 대신 -> 질문/답변 리스트로 변경
    answers: List[QAPair]

class ProjectResponse(ProjectCreate):
    id: int
    generated_docs: Optional[Dict] = {}

    class Config:
        from_attributes = True