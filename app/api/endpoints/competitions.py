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
    AI 추천 결과를 기반으로 DB에서 상세 정보를 조회하여 프론트엔드에 필요한 형태로 반환합니다.
    동시에 AI가 정제한 제출서류 목록을 DB에 업데이트합니다.
    """
    # 1. 프로젝트 정보 조회
    db_project = db.query(Project).filter(Project.id == id).first()
    if not db_project:
        return {"status": "error", "message": "Project not found"}

    startup_profile = db_project.startup_item_core

    # 2. 추천 대상 공모전 후보군 조회
    context_data = get_active_competitions_for_ai(db)

    # 3. GPT를 통한 추천 실행
    ai_result = recommend_with_gpt(startup_profile, context_data)

    # ai_result 구조: {"recommendations": [{"competition_id": "...", ...}, ...]}
    raw_recommendations = ai_result.get("recommendations", [])

    # 4. [정렬] 점수(score) 내림차순 정렬
    raw_recommendations.sort(key=lambda x: int(x.get("score", 0)), reverse=True)

    final_result = []

    # 5. [DB 상세 정보 병합] AI 결과 + DB 상세 정보 합치기
    for rec in raw_recommendations:
        try:
            comp_id = int(rec["competition_id"])
        except ValueError:
            continue

        # DB에서 해당 공모전 상세 정보 조회
        comp_record = db.query(Competition).filter(Competition.id == comp_id).first()

        if comp_record:
            # (1) DB 업데이트: AI가 정제해준 서류 목록(List) 저장
            # 주의: Competition 모델의 required_docs가 JSON 타입이어야 함
            comp_record.required_docs = rec["required_documents"]

            # (2) 프론트엔드 응답 구성: 필요한 필드 모두 포함
            item = {
                "id": comp_record.id,
                "title": comp_record.name,  # 제목
                "organizer": comp_record.organizer,  # 주관기관
                "deadline": comp_record.deadline,  # 마감일
                "score": rec["score"],
                "keywords": rec["keywords"],
                "required_documents": rec["required_documents"]
            }
            final_result.append(item)

    # 변경된 서류 목록 DB 저장
    db.commit()

    # 6. 최종 결과 반환
    return {
        "status": "success",
        "recommendations": final_result
    }