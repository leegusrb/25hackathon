from sqlalchemy import Column, Integer, String, JSON, Text
from app.db.database import Base


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)

    # 1. 식별자
    external_id = Column(String, unique=True, index=True)  # 공고 ID

    # 2. 필수 요청 항목들
    name = Column(String, index=True)  # 공고명
    deadline = Column(String)  # 마감일 (YYYY-MM-DD)
    tracks = Column(JSON, default=[])  # 지원분야 (리스트)
    region = Column(String)  # 지역
    target = Column(String)  # 대상
    age = Column(String)  # 대상연령
    period = Column(String)  # 접수기간 (전체 문자열)
    experience = Column(String)  # 창업업력
    organizer = Column(String)  # 주관기관명
    required_docs = Column(Text)  # 제출서류 (긴 텍스트)
    url = Column(String)  # URL