from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# [수정] 질문-답변 쌍 하나를 나타내는 스키마
class QAPair(BaseModel):
    question_id: str  # 예: "1-1"
    question: str     # 예: "서비스 이름이 뭔가요?"
    answer: str       # 예: "STARTMATE"

# [수정] 메인 생성 스키마
class ProjectCreate(BaseModel):
    # 필터링용 핵심 데이터 (DB 컬럼으로 따로 관리되는 애들)
    team_name: str

    # [핵심 변경] 계층형 객체 대신 -> 질문/답변 리스트로 변경
    answers: List[QAPair]

# [추가] AI 분석 결과 내부의 'sections' 리스트 아이템
class AnalysisSection(BaseModel):
    key: str
    title: str
    content: str
    bullets: List[str]

# [추가] AI 분석 결과 전체 구조
class AnalysisResult(BaseModel):
    language: str
    sections: List[AnalysisSection]

# [수정] ProjectResponse 업데이트 (generated_docs의 타입을 명확히 하거나 Dict 유지)
class ProjectResponse(ProjectCreate):
    id: int
    generated_docs: Optional[Dict[str, Any]] = {}  # 유연성을 위해 Dict로 유지하되, 내용은 위 AnalysisResult 형태임

    class Config:
        from_attributes = True