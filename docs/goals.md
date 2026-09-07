# Product goals

Concrete things the owner wants the agent to do. Every phase should serve one of these.

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
- Results are saved (database, and optionally a Markdown file / Obsidian note).
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

## G4. Assign new automations through Telegram

- Owner can say "review repo X every night" or "send my work log at 6 pm"
  and the agent creates the scheduled job.
- Implemented as a catalog of job types with parameters, not free-form code.
  A message becomes `{intent: create_job, type, config, schedule}`, validated,
  then stored in `scheduled_jobs` and registered with APScheduler.
- Truly new behaviour (a job type that does not exist yet) goes through the
  coding agent (Phase 11) against this repository, with human approval of
  the diff. The agent never rewires itself silently.

## Practical constraint

Scheduled jobs only fire while the process is running. A laptop that is asleep
at 01:00 will miss the job. Plan: run the backend on an always-on host
(Phase 14) and configure APScheduler to catch up on missed runs.
