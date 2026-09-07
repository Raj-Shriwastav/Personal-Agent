# Product goals

Concrete things the owner wants the agent to do. Every phase should serve one of these.
Decisions recorded here override the generic plan in the project brief.

## G1. Daily work log for the company

- Owner names the company repositories through Telegram.
- Every day the agent reads the owner's own commits (and PRs) in those repos.
- It groups related commits and writes a log in the company's required style.
  The style is a stored template the owner can change through Telegram.
- "What did I do today?" returns the ready-to-submit log.

Data: GitHub commits filtered by author and date. Stored in `github_activity`,
rendered into `daily_reports`.

## G2. Nightly repository review

- Owner registers a repository for review through Telegram.
- A scheduled job runs at 01:00: security review plus exactly one recommended
  feature. Slow work is fine because nobody is waiting.
- Results are saved (database and the Obsidian ledger, see G5).
- Later, "show me the suggestions" fetches them; the owner picks one, and it
  becomes a task.

Security findings must come from deterministic scanners where possible
(dependency audit, static analysis). The LLM explains and prioritizes; it
does not invent vulnerabilities.

## G3. Daily learning suggestion

- The agent keeps an ordered learning queue.
- Each day it suggests the *current* topic. It does not advance until the
  owner marks the topic finished through Telegram.

Data: `learning_topics` with status `queued | active | done`.

## G4. Assign automations through Telegram (job templates)

- Owner can say "review repo X every night" or "send my work log at 6 pm"
  and the agent creates the scheduled job.
- Implemented as a **catalog of job templates** with parameters, not free-form
  code. A message becomes `{intent: create_job, template, config, schedule}`,
  validated, then stored in `scheduled_jobs` and registered with APScheduler.
- Owner can list, pause, resume and delete jobs from chat.
- Initial templates: `github_daily_log`, `repo_review`, `learning_suggestion`,
  `daily_task_digest` (what is due / what was done), `custom_daily_prompt`
  (a recurring question or briefing the owner defines in plain language).

**Decision (2026-09-07):** the agent does not write code for itself yet.
Self-extension (agent writes, tests and pushes a new job template on request)
is a later phase and always goes through human approval of the diff.

## G5. Obsidian as a human-readable ledger

- Everything the agent produces or learns about the owner is written as
  Markdown into the Obsidian vault so the owner can read and verify it daily:
  `Agent/Daily/YYYY-MM-DD.md`, `Agent/Reviews/<repo>/YYYY-MM-DD.md`,
  `Agent/Learning.md`, `Agent/Profile.md` (facts the agent has inferred).
- PostgreSQL stays the source of truth; the vault is a mirror plus a place
  the owner reads. The agent also reads the owner's own notes for context.

Open question: the vault lives on the laptop, the agent will live on a server.
Candidate answers: vault as a git repository (server commits, laptop pulls via
the Obsidian Git plugin), Syncthing, or a synced cloud folder. Decide in the
Obsidian phase.

## G6. Always-on operation

- The backend and scheduler run 24/7 on an always-on host and execute jobs
  without the owner present. The owner assigns new jobs daily via Telegram.
- APScheduler is configured to catch up on missed runs after a restart.
- Deployment therefore moves earlier: a first cloud deploy happens as soon
  as Telegram and the scheduler work, not at the end.
- Budget: zero. Candidate free stack (verified 2026-09-07, re-check before
  deploying): Oracle Cloud Always Free ARM VM (2 OCPU / 12 GB) or Google
  Cloud e2-micro; PostgreSQL + pgvector in Docker on the VM; Gemini API free
  tier (Groq as fallback) behind our provider-agnostic LLM wrapper; Telegram
  via long polling (no domain or HTTPS needed); dashboard reached over
  Tailscale rather than the public internet; Obsidian vault as a private
  GitHub repo synced with the Obsidian Git plugin; healthchecks.io for
  missed-job alerts.

## G7. Private dashboard

- Single owner, password protected. No public sign-up. Password hash stored
  server-side; login issues a session token; every `/api/*` route except
  login and health requires it.
- Shows: scheduled jobs and their next run, agent runs currently executing
  in parallel, runs waiting (queued or awaiting approval), run history with
  steps and tool calls, past tasks and their status, reports, and settings.
- Concurrency model: each job execution is an `agent_run` row with a status
  (`queued | running | waiting_approval | completed | failed`). The dashboard
  reads these rows; it does not talk to the scheduler directly.

## Revised phase order

```text
1  Foundation                    (current, checkpoint pending)
2  Database + owner auth         (users, tasks, projects, agent_runs, scheduled_jobs, login)
3  Telegram assistant            (commands + intent extraction)
4  Tasks and projects
5  Scheduler + job templates     (APScheduler, catalog, create jobs from Telegram)
6  First always-on deployment    (Docker on a small VPS, so jobs actually run)
7  GitHub read integration
8  Daily work log (G1)
9  Obsidian ledger, read + write (G5)
10 Nightly repo review (G2)      (scanners first, LLM second)
11 Learning queue (G3)
12 Dashboard: runs, jobs, history (G7)
13 Memory + retrieval, LangGraph orchestration
14 Coding agent with approval gates
15 Evaluation and production polish
```
