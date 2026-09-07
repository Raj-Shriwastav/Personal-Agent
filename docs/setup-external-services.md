# External services: what to create, where, and why

This guide covers everything the agent needs from *outside* the codebase:
accounts, bots, API keys, and free AI models. Read it once end to end, then
come back to each section when the matching phase needs it.

Golden rules for every key you create:

1. A key is a password. Never paste it into code, chat, screenshots, or commits.
2. Every key lives in `.env` on the machine that runs the backend. `.env` is
   git-ignored. `.env.example` lists the variable names with empty values.
3. The LLM never sees a key. Our code reads keys from `Settings` and uses
   them inside integration modules; the model only sees tool results.
4. If a key leaks, revoke it on the provider's site and create a new one.
   Do not try to "delete it from git"; history keeps it.

Checklist of what you will end up with:

| Service | Needed from phase | Env variable | Cost |
|---|---|---|---|
| Telegram bot | 3 | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_OWNER_ID` | free |
| Gemini API (primary LLM + embeddings) | 3 | `GEMINI_API_KEY` | free tier |
| Groq API (fallback LLM) | 3 | `GROQ_API_KEY` | free tier |
| GitHub personal access token | 7 | `GITHUB_TOKEN` | free |
| Private GitHub repo for the Obsidian vault | 9 | `OBSIDIAN_VAULT_PATH` | free |
| Always-on VM (Oracle or Google) | 6 | none, it is where `.env` lives | free tier |
| Tailscale | 6 | none | free |
| healthchecks.io | 6 | `HEALTHCHECK_PING_URL` | free |

---

## 1. Telegram bot

### What it is

Telegram lets anyone create a "bot": a special account that your program
controls through an HTTP API. When you message the bot, Telegram stores the
message and hands it to your program. When your program replies, Telegram
delivers it to your phone.

```text
You (phone)  <-->  Telegram servers  <-->  our backend (getUpdates / sendMessage)
```

There are two ways for our backend to receive messages:

- **Long polling.** Our backend repeatedly asks Telegram "anything new?".
  No public URL, no HTTPS certificate needed. Works from a laptop or a VM
  with no domain. This is what we will use.
- **Webhook.** Telegram pushes messages to a public HTTPS URL we own.
  Slightly faster, but needs a domain and certificate. Optional later.

### Create the bot

1. In Telegram, open a chat with **@BotFather** (verify the blue checkmark).
2. Send `/newbot`.
3. Choose a display name, for example `Raj Work Agent`.
4. Choose a username ending in `bot`, for example `raj_work_agent_bot`.
5. BotFather replies with a token that looks like
   `123456789:AAH6kDkKvkkkT-PyaUC_5XvE1V5Y1a2b3c4`. That is
   `TELEGRAM_BOT_TOKEN`.
6. Optional but recommended: `/setprivacy` → your bot → `Disable` is **not**
   needed for a private chat. Leave the default.

### Lock the bot to you only

Anyone who finds the username can message the bot. The backend must ignore
everyone except you. For that it needs your numeric Telegram user id.

1. Message **@userinfobot** and it replies with your id, for example `987654321`.
2. Put it in `.env` as `TELEGRAM_OWNER_ID=987654321`.

The backend will drop every message whose sender id is not this value.

### Verify

```bash
curl "https://api.telegram.org/bot<TOKEN>/getMe"
```

Expected: JSON with `"ok": true` and your bot's username.

Send the bot any message from your phone, then:

```bash
curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
```

Expected: a `result` array containing your message and your `from.id`.

---

## 2. Free AI models

### How to think about model choice

Our agent needs three different model capabilities:

| Capability | Used for | What matters |
|---|---|---|
| Chat / reasoning | intent extraction, writing reports, planning | quality, **function calling**, **JSON mode** |
| Embeddings | semantic memory in pgvector | cheap, consistent, available forever |
| Long context | reading many commits or notes at once | big context window |

"Function calling" (also called tool use) means the model can answer with a
structured request like `{"tool": "create_task", "args": {...}}` instead of
prose. "JSON mode" means the model is forced to return valid JSON matching a
schema. LangGraph tool calling and our Pydantic validation depend on both.
Pick models that support them.

Our code never depends on one provider. There will be one module,
`backend/app/core/llm.py`, that exposes `chat(...)` and `embed(...)`. Every
provider below plugs in there. Switching providers is a config change.

### Primary: Google Gemini API (free tier, no card)

Why: the free tier includes current Flash models with function calling, JSON
mode, a very large context window, and a free embedding model. That covers
all three capabilities from one key.

1. Go to <https://aistudio.google.com> and sign in with a Google account.
2. Click **Get API key** → **Create API key**. Copy it. That is `GEMINI_API_KEY`.
3. Do **not** enable billing on this Google Cloud project. Free tier only
   applies while billing is off.
4. Rate limits are shown inside AI Studio per model. They change; check there
   rather than trusting blog posts.

Which models: pick the newest **Flash** model for chat (fast, generous free
quota) and the newest **embedding** model for vectors. Model names change
every few months, so ask the API instead of memorizing:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=<GEMINI_API_KEY>"
```

Expected: a list of models. Choose the Flash model with the highest version
that lists `generateContent` in `supportedGenerationMethods`, and the
`embedding` model that lists `embedContent`. Put them in `.env` as
`LLM_MODEL` and `EMBEDDING_MODEL`.

Verify a chat call:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/<LLM_MODEL>:generateContent?key=<GEMINI_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Reply with the single word OK"}]}]}'
```

Expected: JSON containing `"text": "OK"`.

### Fallback: Groq (free tier, no card)

Why: very fast inference of open models (Llama, gpt-oss). Useful when the
Gemini daily cap is hit, and as a second opinion. Supports function calling
and JSON mode on its main models. Free tier is limited per model per day.

1. Go to <https://console.groq.com>, sign up.
2. **API Keys** → **Create API Key**. That is `GROQ_API_KEY`.
3. Model list and limits: **Settings → Limits** in the console.

Verify:

```bash
curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer <GROQ_API_KEY>"
```

Expected: JSON list of models. Groq uses the OpenAI-compatible API format,
so any OpenAI-style client works with a changed base URL.

### Other free options worth knowing

- **OpenRouter** (<https://openrouter.ai>): one key, many providers, several
  models tagged `:free`. Good for experiments; free models rotate.
- **Mistral AI** free tier: decent models with function calling.
- **Cloudflare Workers AI**: free daily neuron budget, open models.
- **Ollama** (<https://ollama.com>): run open models on your own machine.
  Fully free and private, but on a free VM with 12 GB RAM only small models
  fit and they are slow. Fine for embeddings later; not for the main agent.

### Why not OpenAI or Claude

Both are excellent but have no standing free tier. The original brief named
OpenAI; because the budget is zero we start with Gemini. The provider wrapper
means you can switch by changing three env variables if that changes.

### Budget the free quota

Daily caps are the real constraint. Rules we will follow in code:

- One LLM call per Telegram message, not a chain of five.
- Nightly jobs batch their inputs (one call per repo, not per commit).
- Deterministic code (grouping commits, scoring priorities, scanners) does
  the bulk of the work; the model summarizes and explains.
- Every call is logged with token counts in `agent_runs` so you can see
  where the quota goes on the dashboard.

---

## 3. GitHub personal access token

### What it is

A token that lets our backend call the GitHub API as you, with only the
permissions you grant. We use it to read commits, PRs and issues, and
(Phase 9) to push the Obsidian vault repo.

### Create it

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens**
   → **Fine-grained tokens** → **Generate new token**.
2. Name: `personal-agent`. Expiration: 90 days is a good habit (you will
   rotate it).
3. **Repository access**: "Only select repositories", then pick the company
   repositories you must report on and the vault repository.
   If the company repos live in an organisation, the org may need to approve
   fine-grained tokens; if that is blocked, use a classic token with the
   `repo` scope instead.
4. **Permissions** → Repository permissions:
   - Contents: Read (Read and write only for the vault repo, use a second token if you prefer)
   - Metadata: Read
   - Pull requests: Read
   - Issues: Read
   - Commit statuses: Read
5. Generate, copy, store as `GITHUB_TOKEN`.

### Verify

```bash
curl -H "Authorization: Bearer <GITHUB_TOKEN>" https://api.github.com/user
```

Expected: JSON with your `login`.

```bash
curl -H "Authorization: Bearer <GITHUB_TOKEN>" \
  "https://api.github.com/repos/<owner>/<repo>/commits?author=<your-login>&per_page=5"
```

Expected: your five latest commits in that repo. This is exactly the call
the daily work log will make.

---

## 4. Obsidian vault as a git repository

### What it is and why

Obsidian is a Markdown editor over a folder. The agent will write its daily
reports, reviews, learning log and inferred profile into that folder so you
can read and correct them. The agent runs on a server; your vault is on your
laptop. Git bridges the two: the server commits and pushes, your laptop pulls.

```text
Server (agent writes .md, git push)  -->  private GitHub repo  -->  laptop (Obsidian Git plugin pulls)
```

### Set up

1. Create a **private** GitHub repository, for example `obsidian-vault`.
2. On your laptop, inside the vault folder: `git init`, add the remote, push.
   If the vault already exists, add a `.gitignore` for `.obsidian/workspace*`
   (per-device UI state that causes conflicts).
3. In Obsidian: **Settings → Community plugins → Browse → "Git"** (Obsidian
   Git). Enable auto pull on startup and every few minutes.
4. On the server, `git clone` the same repo to a path and set
   `OBSIDIAN_VAULT_PATH=/home/agent/obsidian-vault`.
5. The server needs push rights: either the `GITHUB_TOKEN` above with
   Contents: Read and write on this repo, or an SSH deploy key with write
   access (GitHub → repo → Settings → Deploy keys).

The agent will only write inside an `Agent/` folder in the vault, so your own
notes are never touched by it.

---

## 5. Always-on server

### Why

Scheduled jobs (01:00 review, daily log) only run while the backend process
is alive. A laptop that sleeps misses them. A small free VM is enough.

### Option A: Oracle Cloud Always Free (preferred)

- What you get: an Arm VM with 2 OCPU and 12 GB RAM, forever free, plus
  block storage. More than enough for Docker with Postgres and the backend.
- Sign up at <https://www.oracle.com/cloud/free/>. A card is required for
  identity verification; Always Free resources are not billed.
- Choose a home region close to you. You cannot change it later.
- Create a VM: shape **VM.Standard.A1.Flex**, 2 OCPU, 12 GB, Ubuntu image,
  and upload your SSH public key.
- Known problem: "Out of capacity" errors for A1 shapes. Retry at different
  times of day, or use a small script that retries. It can take days.
- Do **not** upgrade the account to pay-as-you-go unless you understand that
  resources outside the free limits will then be billed.

### Option B: Google Cloud e2-micro

- One e2-micro VM (shared vCPU, 1 GB RAM, 30 GB disk) free with no expiry,
  only in `us-west1`, `us-central1`, `us-east1`.
- 1 GB RAM is tight. If you go this way, put PostgreSQL on Neon's free tier
  (<https://neon.com>, supports pgvector) instead of on the VM.
- Sign up at <https://cloud.google.com/free>. Card required for verification.

### On the VM, install

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER   # log out and back in
```

Then clone this repository, create `.env` from `.env.example`, and run
`docker compose up -d`. Deployment details come in Phase 6.

---

## 6. Tailscale: private access to the dashboard

### Why

The dashboard shows everything about your work. It should not be reachable
from the public internet at all. Tailscale creates a private network between
your laptop, phone and the VM. The dashboard listens only on that network.
Password login is still required on top.

1. Sign up at <https://tailscale.com> (free personal plan).
2. Install on laptop, phone and the VM (`curl -fsSL https://tailscale.com/install.sh | sh` then `sudo tailscale up`).
3. Each device gets a stable private IP like `100.x.y.z`. The dashboard URL
   becomes `http://100.x.y.z:5173`.

---

## 7. healthchecks.io: know when a job did not run

### Why

A scheduler that silently stops is worse than none. healthchecks.io gives you
a unique URL per job. Our job pings it when it finishes. If a ping does not
arrive on schedule, you get a Telegram or email alert.

1. Sign up at <https://healthchecks.io> (free plan).
2. Create a check named `nightly-review`, schedule `0 1 * * *`, grace time 60 minutes.
3. Copy its ping URL into `.env` as `HEALTHCHECK_PING_URL`.
4. Under **Integrations**, add Telegram so alerts reach your phone.

---

## 8. Putting it together: `.env` on the server

```text
APP_ENV=production
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=personal_agent
POSTGRES_USER=agent
POSTGRES_PASSWORD=<long random string>

OWNER_PASSWORD=<dashboard login password>
SECRET_KEY=<long random string for session tokens>

TELEGRAM_BOT_TOKEN=
TELEGRAM_OWNER_ID=

LLM_PROVIDER=gemini
LLM_MODEL=
EMBEDDING_MODEL=
GEMINI_API_KEY=
GROQ_API_KEY=

GITHUB_TOKEN=
GITHUB_USERNAME=
OBSIDIAN_VAULT_PATH=/home/agent/obsidian-vault

HEALTHCHECK_PING_URL=
```

Generate random strings with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Variables are added to `Settings` in `backend/app/core/config.py` in the
phase that first needs them, never earlier.

---

## Order to do this in

You do not need any of it for Phase 1. Suggested timing:

- Before Phase 3: Telegram bot, owner id, Gemini key, Groq key.
- Before Phase 6: Oracle or Google VM, Tailscale, healthchecks.io.
- Before Phase 7: GitHub token.
- Before Phase 9: vault repository and Obsidian Git plugin.
