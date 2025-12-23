from fastapi import APIRouter, HTTPException
from typing import Dict
from app.schemas.project import ProjectInfo, GenerateRequest, GenerateResponse
from app.db.mock_data import fake_projects
from app.services import ai_service # 서비스 로직 가져오기

router = APIRouter()

# 프로젝트 정보 저장
@router.post("/", response_model=Dict)
def create_project_info(project: ProjectInfo):
    project_id = len(fake_projects) + 1
    fake_projects[project_id] = project.dict()
    return {"project_id": project_id, "message": "Saved"}

# 프로젝트 정보 조회
@router.get("/{project_id}", response_model=ProjectInfo)
def get_project_info(project_id: int):
    if project_id not in fake_projects:
        raise HTTPException(status_code=404, detail="Not found")
    return fake_projects[project_id]

# AI 문서 생성 요청 (핵심)
@router.post("/ai/generate", response_model=GenerateResponse)
def generate_doc_section(req: GenerateRequest):
    project_data = fake_projects.get(req.project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")

    # 서비스 계층(AI 로직) 호출 -> 코드가 깔끔해짐
    content = ai_service.generate_draft(
        project_info=project_data,
        section=req.section,
        doc_type=req.doc_type
    )

    return {
        "section": req.section,
        "content": content,
        "status": "completed"
    }