"""
Health endpoints.

GET /api/health     -> is the FastAPI process alive?
GET /api/health/db  -> can the backend reach PostgreSQL?

Keeping these separate lets us tell "app is down" apart from "database is down".
"""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.db.session import check_database_connection
from app.schemas.health import DatabaseHealthResponse, HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name, environment=settings.app_env)


@router.get("/db", response_model=DatabaseHealthResponse)
def database_health() -> DatabaseHealthResponse:
    if check_database_connection():
        return DatabaseHealthResponse(
            status="ok", database="connected", detail="SELECT 1 succeeded"
        )
    return DatabaseHealthResponse(
        status="error",
        database="unreachable",
        detail="Could not connect to PostgreSQL. Check POSTGRES_* environment variables.",
    )
