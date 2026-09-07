# Personal AI Work & Productivity Agent

A personal assistant that understands your goals, tasks, projects, notes and
GitHub activity, and helps you decide what to work on and execute it, with a
human approving every important action.

Built incrementally, one phase at a time. See [docs/architecture.md](docs/architecture.md).

## Current phase: 1 — Foundation

```text
React (5173) --> FastAPI (8000) --> PostgreSQL (5432)
```

## Prerequisites

- Docker Desktop (runs PostgreSQL, and optionally the whole stack)
- Python 3.10+
- Node.js 22+

## Quick start (everything in Docker)

```bash
cp .env.example .env          # edit POSTGRES_PASSWORD
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health and /api/health/db

## Local development (DB in Docker, code on host)

```bash
docker compose up -d db

# backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
pytest
```

## Repository layout

```text
backend/    FastAPI app  (app/api, core, db, models, schemas, services, tools, agents, integrations)
frontend/   React + Vite + Tailwind
docs/       architecture, database, agent, integrations
```
