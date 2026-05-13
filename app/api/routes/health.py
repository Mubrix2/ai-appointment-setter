# app/api/routes/health.py
from fastapi import APIRouter
from app.api.schemas import HealthResponse
from app.config import APP_ENV

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", env=APP_ENV)