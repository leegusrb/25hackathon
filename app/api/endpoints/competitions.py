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


@router.post("/recommend/{id}")
def recommend_by_ai(id: int, db: Session = Depends(get_db)):
    """
    AI 추천 결과를 반환하며, AI가 정제한 제출서류 목록을 DB에 업데이트합니다.
    """
    # 1. 프로젝트 정보 조회
    db_project = db.query(Project).filter(Project.id == id).first()
    startup_profile = db_project.startup_item_core

    # 2. 추천 대상 공모전 후보군 조회
    context_data = get_active_competitions_for_ai(db)

    # 3. GPT를 통한 추천 실행
    ai_result = recommend_with_gpt(startup_profile, context_data)

    # ai_result 구조 예시: {"recommendations": [...]}
    recommendations = ai_result.get("recommendations", [])

    # 4. [정렬] 점수(score) 내림차순 정렬 (Python 레벨에서 확실하게 처리)
    recommendations.sort(key=lambda x: int(x.get("score", 0)), reverse=True)

    # 5. [DB 저장] AI가 정제해준 서류 목록(List)을 DB에 저장 (업데이트)
    for rec in recommendations:
        comp_id = int(rec["competition_id"])
        clean_docs = rec["required_documents"]  # 리스트 형태

        # 해당 공모전 DB 레코드 찾기
        comp_record = db.query(Competition).filter(Competition.id == comp_id).first()
        if comp_record:
            # 기존 텍스트 대신 깔끔한 리스트로 덮어쓰기
            comp_record.required_docs = clean_docs

    db.commit()  # 변경사항 저장

    # 6. 프론트엔드에 결과 반환 (정렬된 리스트)
    return {
        "status": "success",
        "recommendations": recommendations
    }