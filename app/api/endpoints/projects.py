from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.project import ProjectCreate, ProjectResponse
from app.models.project import Project
from app.db.database import get_db, engine, Base

# DB 테이블 생성 (앱 시작 시 테이블이 없으면 자동 생성)
Base.metadata.create_all(bind=engine)

router = APIRouter()

# [기능 1] 질문/답변 페이지 제출 -> DB 저장
@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # [수정됨] project.answers가 이제 List[QAPair] 형식이므로,
    # 각 항목을 dict로 변환하여 리스트 형태로 DB에 저장해야 합니다.
    answers_data = [answer.model_dump() for answer in project.answers]

    db_project = Project(
        team_name=project.team_name,

        # JSON 컬럼에 리스트(List[dict])를 그대로 저장
        answers_json=answers_data
    )

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