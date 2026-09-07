# Architecture

This document grows with each phase. It records *what exists now* and *why*.

## Phase 1 — Foundation (current)

```text
Browser
   |
   |  http://localhost:5173
   v
React + Vite (frontend/)
   |
   |  /api/* proxied by Vite dev server
   v
FastAPI (backend/app/main.py)
   |
   |  SQLAlchemy engine, psycopg driver
   v
PostgreSQL 16 + pgvector (docker "db" service)
```

### Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| Frontend  | `frontend/` | Dashboard UI. Talks only to `/api`. |
| Backend   | `backend/app/` | HTTP API, business logic, agent (later). |
| Database  | docker service `db` | Persistent state. |

### Backend layout

```text
backend/app/
├── main.py          FastAPI app object, middleware, router registration
├── api/             HTTP routers (one file per resource)
├── core/            config, security, shared utilities
├── db/              engine, session, Base
├── models/          SQLAlchemy ORM tables        (Phase 2)
├── schemas/         Pydantic request/response models
├── services/        business logic, called by api/ and agents/
├── tools/           allow-listed functions the agent may call (Phase 6)
├── agents/          LangGraph graphs and state (Phase 6)
└── integrations/    Telegram, GitHub, Obsidian clients (Phases 3, 8, 9)
```

Rule: `api/` never touches the database directly. It calls `services/`,
which use `models/`. Agents also call `services/`. This keeps one code path
for every operation whether it came from the UI, Telegram, or the agent.

### Request flow for `/api/health/db`

1. Browser calls `GET /api/health/db`.
2. Vite dev server forwards it to `http://localhost:8000/api/health/db`.
3. FastAPI routes to `app.api.health.database_health`.
4. It calls `check_database_connection()` which borrows a pooled connection and runs `SELECT 1`.
5. Result is validated against `DatabaseHealthResponse` and returned as JSON.

### Why these choices

- **FastAPI**: async-capable, typed, auto-generates OpenAPI docs at `/docs`. Pydantic validation is built in.
- **Pydantic settings**: one typed `Settings` object instead of `os.environ` scattered everywhere.
- **SQLAlchemy 2.0**: the standard Python ORM. Gives us migrations (Alembic, Phase 2) and keeps SQL out of the LLM's hands.
- **psycopg 3**: the modern PostgreSQL driver; works sync now and async later.
- **pgvector image**: PostgreSQL plus the vector extension. Same DB for structured and semantic memory.
- **Vite**: fast dev server with a built-in `/api` proxy, so the browser sees one origin.
- **Tailwind v4**: utility classes, no separate CSS build config.
- **Docker Compose**: reproducible three-service environment with one command.
