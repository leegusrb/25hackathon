from sqlalchemy import Column, Integer, String, JSON, Text
from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    # 1. 핵심 식별 정보
    team_name = Column(String, index=True)  # 팀명

    # 2. 추천 알고리즘 필터링용 핵심 데이터 (별도 컬럼으로 관리)
    domain = Column(String)  # 분야 (예: AI, 헬스케어)
    stage = Column(String)  # 단계 (예: 아이디어, MVP)
    target_award = Column(String)  # 목표 (예: 예비창업패키지, 수상)

    # 3. 16가지 질문 전체 데이터 (나중에 서류 생성할 때 프롬프트 재료로 씀)
    # 질문1:답변1, 질문2:답변2 ... 형태의 JSON으로 저장
    answers_json = Column(JSON)

    # 4. 생성된 서류 저장 (나중을 위해 미리 공간 확보)
    generated_docs = Column(JSON, default={})