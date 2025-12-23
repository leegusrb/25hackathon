from sqlalchemy import Column, Integer, String, JSON, Text
from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    # 1. 핵심 식별 정보
    team_name = Column(String, index=True)  # 팀명

    # 2. 추천 알고리즘 필터링용 핵심 데이터
    domain = Column(String)  # 분야 (예: AI, 헬스케어)
    stage = Column(String)  # 단계 (예: 아이디어, MVP)
    target_award = Column(String)  # 목표 (예: 예비창업패키지, 수상)

    # 3. 인터뷰 질문/답변 데이터
    # 기존: Key-Value 객체 -> 변경: List[Dict] 형태
    # 예: [{"question_id": "1-1", "question": "...", "answer": "..."}, ...]
    answers_json = Column(JSON)

    # 4. 생성된 서류 저장 (나중을 위해 미리 공간 확보)
    generated_docs = Column(JSON, default={})