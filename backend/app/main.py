"""
FastAPI application entry point.

Run locally:   uvicorn app.main:app --reload
Docs (auto):   http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

# CORS: browsers block cross-origin requests by default. The React dev server
# (port 5173) and the API (port 8000) are different origins, so we must
# explicitly allow the frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All routes live under /api so the frontend can proxy a single prefix.
app.include_router(health_router, prefix="/api")
