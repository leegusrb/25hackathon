from pydantic import BaseModel
from typing import List, Optional


class DocTemplate(BaseModel):
    doc_type: str  # 예: "사업계획서"
    sections: List[str]  # 예: ["문제정의", "솔루션", "시장분석"]


class CompetitionDetail(BaseModel):
    id: int
    name: str
    organizer: str  # [추가] 주최 기관
    deadline: str  # [추가] 마감일 (YYYY-MM-DD)
    tracks: List[str]  # [추가] 공모 분야 리스트
    eligibility: str  # [추가] 공모 자격
    url: Optional[str] = None  # [추가] 홈페이지 URL (없는 경우 대비 Optional)
    description: Optional[str] = None  # [추가] 설명

    required_docs: List[DocTemplate]