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
    # Pydantic 모델(.dict())을 JSON으로 변환해서 저장
    db_project = Project(
        team_name=project.team_name,
        domain=project.domain,
        stage=project.stage,
        target_award=project.target_award,

        # 여기서 계층형 데이터를 JSON으로 넣습니다.
        answers_json=project.answers.model_dump()
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # 반환할 때도 DB JSON -> Pydantic 스키마 매핑됨
    return ProjectResponse(
        id=db_project.id,
        team_name=db_project.team_name,
        domain=db_project.domain,
        stage=db_project.stage,
        target_award=db_project.target_award,
        answers=db_project.answers_json,  # 이름 맞춤
        generated_docs=db_project.generated_docs
    )


# [조회] 저장된 프로젝트 확인용
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # DB 모델 -> Pydantic 스키마 매핑
    return ProjectResponse(
        id=db_project.id,
        team_name=db_project.team_name,
        domain=db_project.domain,
        stage=db_project.stage,
        target_award=db_project.target_award,
        answers=db_project.answers_json,
        generated_docs=db_project.generated_docs
    )