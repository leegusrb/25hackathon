from sqlalchemy import Column, Integer, String, JSON
from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    team_name = Column(String, index=True)  # 팀명
    answers_json = Column(JSON)
    startup_item_core = Column(JSON, default={})
    startup_reco_profile = Column(JSON, default={})
    pdf_file_path = Column(String, nullable=True)