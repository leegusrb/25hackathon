from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

from app.db.database import get_db, engine, Base
from app.models.competition import Competition
from app.services.competition_service import get_active_competitions_for_ai
from app.services.crawling_service import crawl_k_startup

# DB 테이블 생성 (새로 수정된 Competition 모델 반영)
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


# [AI 추천을 위한 데이터 준비 테스트용 API]
@router.get("/ai-context")
def get_competitions_context(db: Session = Depends(get_db)):
    """
    AI에게 보낼 공고문 데이터셋을 미리 확인하는 API입니다.
    날짜가 지난 공고는 제외되고, 필요한 필드만 JSON으로 반환됩니다.
    """
    # 1. 서비스 함수 호출 -> 필터링된 데이터 리스트 획득
    context_data = get_active_competitions_for_ai(db)

    # 2. 결과 확인 (실제 AI 호출 시에는 이 데이터를 prompt에 포함시킵니다)
    return {
        "count": len(context_data),
        "data": context_data
    }


# [실제 AI 추천 로직 구현 예시]
@router.post("/recommend/ai")
def recommend_by_ai(user_input: str, db: Session = Depends(get_db)):
    """
    사용자의 입력(user_input)과 DB의 공고 정보를 합쳐서 AI에게 추천을 요청합니다.
    """
    # 1. DB에서 유효한 공고 데이터 가져오기
    competitions_list = get_active_competitions_for_ai(db)

    # 2. AI에게 보낼 프롬프트 구성 (JSON 문자열로 변환)
    system_prompt = f"""
    아래는 현재 지원 가능한 창업 공고 목록이야. JSON 형식으로 제공할게.
    사용자의 상황에 가장 적합한 공고 3개를 골라서 추천해줘.

    [공고 목록]
    {json.dumps(competitions_list, ensure_ascii=False, indent=2)}
    """

    # 3. 여기서 AI 서비스 호출 (openai.ChatCompletion 등)
    # response = call_openai(system_prompt, user_input)

    # return response

    # (테스트용 반환)
    return {"message": "AI 프롬프트가 준비되었습니다.", "prompt_preview": system_prompt[:500] + "..."}