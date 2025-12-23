from sqlalchemy import Column, Integer, String, JSON, Text
from app.db.database import Base


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)

    # 1. 식별자
    external_id = Column(String, unique=True, index=True)

    # 2. 필수 요청 항목들
    name = Column(String, index=True)
    deadline = Column(String)
    tracks = Column(JSON, default=[])
    region = Column(String)
    target = Column(String)
    age = Column(String)
    period = Column(String)
    experience = Column(String)
    organizer = Column(String)

    # [수정됨] Text -> JSON으로 변경하여 리스트 저장을 지원하게 함
    required_docs = Column(JSON, default=[])

    url = Column(String)