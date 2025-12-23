from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any


# [기존 코드 유지] 질문-답변 쌍
class QAPair(BaseModel):
    question_id: str
    question: str
    answer: str


# [기존 코드 유지] 프로젝트 생성 스키마
class ProjectCreate(BaseModel):
    team_name: str
    answers: List[QAPair]


# [신규] 프론트엔드 응답용 섹션 모델 (bullets 제외)
class SectionContent(BaseModel):
    key: str
    title: str
    content: str


# [수정] 프로젝트 응답 스키마
class ProjectResponse(ProjectCreate):
    id: int

    # [수정] 반환 타입을 Dict가 아닌 '요약된 섹션 리스트'로 변경
    generated_docs: Optional[List[SectionContent]] = []

    class Config:
        from_attributes = True

    # [추가] DB의 전체 JSON 데이터에서 'content' 부분만 추출하여 응답 형식으로 변환
    @validator('generated_docs', pre=True)
    def extract_content_only(cls, v):
        # 1. 값이 없으면 빈 리스트 반환
        if not v:
            return []

        # 2. DB에 저장된 값이 전체 JSON(Dict) 형태인 경우 -> 필터링 수행
        if isinstance(v, dict) and "sections" in v:
            return [
                {
                    "key": section.get("key"),
                    "title": section.get("title"),
                    "content": section.get("content")
                    # bullets는 여기서 제외됨
                }
                for section in v["sections"]
            ]

        # 3. 그 외의 경우(이미 리스트이거나 형식이 안 맞는 경우) 그대로 반환 시도
        return v