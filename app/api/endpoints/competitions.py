from fastapi import APIRouter, Depends
from openai import project
from sqlalchemy.orm import Session

from app.db.database import get_db, engine, Base
from app.models.competition import Competition
from app.models.project import Project
from app.services.competition_service import get_active_competitions_for_ai
from app.services.crawling_service import crawl_k_startup
from app.services.recommend import recommend_with_gpt

Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.post("/sync")
def sync_competitions(db: Session = Depends(get_db)):
    """
    K-Startup 공고를 크롤링하여 요청된 11가지 항목을 DB에 저장합니다.
    """
    crawled_data = crawl_k_startup(page_limit=1)

    saved_count = 0
    updated_count = 0

    for item in crawled_data:
        # 이미 존재하는 공고인지 확인 (external_id 기준)
        existing = db.query(Competition).filter(Competition.external_id == item["external_id"]).first()

        if existing:
            # 이미 있으면 업데이트 (선택 사항)
            existing.name = item["name"]
            existing.deadline = item["deadline"]
            existing.tracks = item["tracks"]
            existing.region = item["region"]
            existing.target = item["target"]
            existing.age = item["age"]
            existing.period = item["period"]
            existing.experience = item["experience"]
            existing.organizer = item["organizer"]
            existing.required_docs = item["required_docs"]
            existing.url = item["url"]
            updated_count += 1
        else:
            # 없으면 신규 생성
            new_comp = Competition(
                external_id=item["external_id"],
                name=item["name"],
                deadline=item["deadline"],
                tracks=item["tracks"],
                region=item["region"],
                target=item["target"],
                age=item["age"],
                period=item["period"],
                experience=item["experience"],
                organizer=item["organizer"],
                required_docs=item["required_docs"],
                url=item["url"]
            )
            db.add(new_comp)
            saved_count += 1

    db.commit()
    return {
        "status": "success",
        "message": f"총 {len(crawled_data)}개 탐색. 신규: {saved_count}, 업데이트: {updated_count}"
    }


# [실제 AI 추천 로직 구현 예시]
@router.post("/recommend/{id}")
def recommend_by_ai(id: int, db: Session = Depends(get_db)):
    """
    사용자의 입력(user_input)과 DB의 공고 정보를 합쳐서 AI에게 추천을 요청합니다.
    """

    db_project = db.query(Project).filter(Project.id == id).first()
    startup_profile = db_project.startup_item_core

    context_data = get_active_competitions_for_ai(db)

    competitions_list = recommend_with_gpt(startup_profile, context_data)

    return competitions_list