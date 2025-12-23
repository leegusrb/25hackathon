import os
import shutil

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.schemas.project import ProjectCreate, ProjectResponse
from app.models.project import Project
from app.db.database import get_db, engine, Base
from app.services.generate_core_and_profile import generate_core_and_profile

# DB 테이블 생성 (앱 시작 시 테이블이 없으면 자동 생성)
Base.metadata.create_all(bind=engine)

router = APIRouter()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# [기능 1] 질문/답변 페이지 제출 -> DB 저장
@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # [수정됨] project.answers가 이제 List[QAPair] 형식이므로,
    # 각 항목을 dict로 변환하여 리스트 형태로 DB에 저장해야 합니다.
    answers_data = [answer.model_dump() for answer in project.answers]

    generated_docs = generate_core_and_profile(answers_data)

    db_project = Project(
        team_name=project.team_name,
        answers_json=answers_data,
        startup_item_core=generated_docs["startup_item_core"],
        startup_reco_profile=generated_docs["startup_reco_profile"]
    )

    print(generated_docs)

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # 반환할 때는 Pydantic이 DB의 JSON(dict list)을
    # 다시 List[QAPair] 스키마로 자동 변환해줍니다.
    return ProjectResponse(
        id=db_project.id,
        team_name=db_project.team_name,
        answers=db_project.answers_json,
        startup_item_core=db_project.startup_item_core,
        startup_reco_profile=db_project.startup_reco_profile
    )


# [조회] 저장된 프로젝트 확인용
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=db_project.id,
        team_name=db_project.team_name,
        # DB에 저장된 리스트형 JSON이 스키마의 List[QAPair]로 자동 매핑됨
        answers=db_project.answers_json,
        startup_item_core=db_project.startup_item_core,
        startup_reco_profile=db_project.startup_reco_profile
    )


@router.post("/{project_id}/upload-pdf")
async def upload_project_pdf(
        project_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """
    PDF를 1)서버에 저장, 2)텍스트 추출, 3)AI(OpenAI)에 업로드합니다.
    """
    # 1. 프로젝트 확인
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. 로컬 파일 저장
    safe_filename = f"{project_id}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        with open(file_location, "wb+") as buffer:
            shutil.copyfileobj(file.file, buffer)

        await file.seek(0)  # 파일 포인터 초기화

        db_project.pdf_file_path = file_location

        db.commit()
        db.refresh(db_project)

        return {
            "status": "success",
            "message": "파일 처리 완료 (로컬 저장 + 텍스트 추출 + AI 전송)",
            "file_path": file_location,
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="파일 처리 중 오류가 발생했습니다.")