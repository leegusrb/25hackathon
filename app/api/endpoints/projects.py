import os
import shutil

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.schemas.project import ProjectCreate, ProjectResponse
from app.models.project import Project
from app.db.database import get_db, engine, Base
from app.services.ai_service import generate_project_analysis
from app.services.generate_ux_sections import generate_ux_sections

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

    project_info = {
        "team_name": project.team_name,
        "answers": answers_data
    }

    generated_docs = generate_ux_sections(project_info)

    db_project = Project(
        team_name=project.team_name,
        answers_json=answers_data,
        generated_docs=generated_docs
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
        generated_docs=db_project.generated_docs
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
        generated_docs=db_project.generated_docs
    )


# [추가 기능] 프로젝트 답변을 바탕으로 AI 분석/요약 실행 후 DB 저장
@router.post("/{project_id}/analyze", response_model=ProjectResponse)
def analyze_project_answers(project_id: int, db: Session = Depends(get_db)):
    """
    특정 프로젝트의 인터뷰 내용(answers)을 AI로 분석하여
    generated_docs 컬럼에 JSON 형태로 저장합니다.
    """
    # 1. 프로젝트 조회
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. 분석할 데이터가 있는지 확인
    if not db_project.answers_json:
        raise HTTPException(status_code=400, detail="인터뷰 답변 데이터가 없습니다.")

    # 3. AI 서비스 호출 (project_info를 dict로 구성해서 전달)
    project_info = {
        "team_name": db_project.team_name,
        "answers": db_project.answers_json
    }

    # AI가 반환한 Dict (JSON 구조)
    ai_result_json = generate_project_analysis(project_info)

    # 4. DB 업데이트 (JSON 컬럼에 저장)
    # SQLAlchemy가 JSON 변경을 감지하도록 새로운 값을 할당
    db_project.generated_docs = ai_result_json

    db.commit()
    db.refresh(db_project)

    # 5. 결과 반환
    return ProjectResponse(
        id=db_project.id,
        team_name=db_project.team_name,
        answers=db_project.answers_json,
        generated_docs=db_project.generated_docs
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