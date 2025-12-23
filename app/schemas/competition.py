from pydantic import BaseModel
from typing import List

class DocTemplate(BaseModel):
    doc_type: str       # 예: "사업계획서"
    sections: List[str] # 예: ["문제정의", "솔루션", "시장분석"]

class CompetitionDetail(BaseModel):
    id: int
    name: str
    required_docs: List[DocTemplate]