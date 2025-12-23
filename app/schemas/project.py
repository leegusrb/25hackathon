from pydantic import BaseModel
from typing import Dict, Optional, List


# ==========================================
# [카테고리 1] 서비스 핵심 정보 (Service Core)
# ==========================================
class ServiceInfo(BaseModel):
    service_name: str  # 1-1. 서비스(아이템) 이름
    one_line_desc: str  # 1-2. 한 줄 설명
    motivation: str  # 1-3. 계기 및 문제 상황


# ==========================================
# [카테고리 2] 문제 인식 & 고객 정의 (Problem & Market)
# ==========================================
class ProblemInfo(BaseModel):
    core_problem: str  # 2-1. 핵심 문제
    target_user: str  # 2-2. 핵심 타겟 (페르소나)
    existing_solution: str  # 2-3. 기존 해결 방식
    existing_pain_point: str  # 2-4. 기존 방식의 불편함


# ==========================================
# [카테고리 3] 솔루션 개요 & 실현 가능성 (Solution)
# ==========================================
class SolutionInfo(BaseModel):
    core_features: str  # 3-1. 핵심 기능 (3가지)
    differentiation: str  # 3-2. 기존 대비 차별점
    current_status: str  # 3-3. 현재 구현 수준 (아이디어/MVP 등)


# ==========================================
# [카테고리 4] 성장 전략 & 사업화 (Business)
# ==========================================
class BusinessInfo(BaseModel):
    revenue_model: str  # 4-1. 수익 모델
    initial_target: str  # 4-2. 초기 진입 대상
    expansion_plan: str  # 4-3. 확장 전략


# ==========================================
# [카테고리 5] 팀 구성 & 역량 (Team)
# ==========================================
class TeamInfo(BaseModel):
    members_roles: str  # 5-1. 팀원 및 역할
    team_fit: str  # 5-2. 팀 역량/적합성
    external_help: Optional[str] = None  # 5-3. 외부 협력 (선택사항)


# ==========================================
# [전체 답변 래퍼] 5개 카테고리를 하나로 묶음
# ==========================================
class CategorizedAnswers(BaseModel):
    service: ServiceInfo
    problem: ProblemInfo
    solution: SolutionInfo
    business: BusinessInfo
    team: TeamInfo


# ==========================================
# [API 요청용 메인 스키마]
# ==========================================
class ProjectCreate(BaseModel):
    # [검색/필터링용 핵심 데이터]
    # 프론트엔드에서 위 답변 내용 중 일부를 매핑하거나 별도 선택으로 보내줘야 함
    team_name: str  # -> 1-1과 동일하거나 팀명 별도 입력
    domain: str  # -> AI, 헬스케어 등 (추천 알고리즘용)
    stage: str  # -> 3-3과 연동 (추천 알고리즘용)
    target_award: str  # -> 목표 (추천 알고리즘용)

    # [16가지 상세 답변 데이터]
    answers: CategorizedAnswers


class ProjectResponse(ProjectCreate):
    id: int
    generated_docs: Optional[Dict] = {}

    class Config:
        from_attributes = True