"""
Database connection layer.

Concepts:
- Engine: a pool of TCP connections to PostgreSQL. Created once per process.
- Session: a short-lived "unit of work" that borrows a connection from the pool,
  runs queries, then commits or rolls back. One session per HTTP request.

`get_db` is a FastAPI *dependency*: any route that declares
`db: Session = Depends(get_db)` receives a session, and FastAPI guarantees
it is closed when the request finishes, even if an exception is raised.
"""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # test a pooled connection before reusing it (survives DB restarts)
    echo=settings.debug,  # log every SQL statement when DEBUG=true
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """All ORM models (Phase 2 onward) will inherit from this."""


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """Return True if a trivial query succeeds. Never raises."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
