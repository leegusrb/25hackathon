from pydantic import BaseModel
from typing import Dict, Optional

# 공통 정보 입력용
class ProjectInfo(BaseModel):
    team_name: str
    item_stage: str
    domain: str
    common_info: Dict[str, str]

# AI 생성 요청용
class GenerateRequest(BaseModel):
    project_id: int
    doc_type: str
    section: str

# AI 생성 응답용
class GenerateResponse(BaseModel):
    section: str
    content: str
    status: str = "completed"