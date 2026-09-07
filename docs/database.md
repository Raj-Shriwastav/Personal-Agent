# Database

## Phase 1

No application tables yet. Phase 1 only proves connectivity.

- Engine: PostgreSQL 16 (`pgvector/pgvector:pg16` image)
- Driver: psycopg 3 via SQLAlchemy 2.0
- Connection URL is assembled in `backend/app/core/config.py` from `POSTGRES_*` env vars.

## Planned schema (Phase 2)

```text
users, projects, tasks, goals, deadlines, work_sessions,
messages, daily_reports, agent_runs, tool_calls
```

Later: `memory_items`, `embeddings`, `github_repositories`,
`github_activity`, `obsidian_documents`, `approval_requests`.
