from fastapi import APIRouter
from app.api.endpoints import competitions, projects

api_router = APIRouter()
api_router.include_router(competitions.router, prefix="/competitions", tags=["Competitions"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])