# Aero — Project Context Document (Hackathon Scope)

**How to use this file:** Paste this entire document into the first message of every new Claude / Claude Code session about Aero. Save it as `PROJECT_PLAN.md` and also as `PROJECT_NOTES.md` at the project root so Claude Code auto-reads it. Section 11 (Current Status) is updated automatically at end-of-session per the rules in section 10.

---

## 1\. Project Vision (Hackathon Scope)

**Aero** is a portfolio-grade aviation intelligence demo: a live map of aircraft pulling real ADS-B data, with one solid ML capability layered on top of historical SFO flight data. Think "weekend hackathon polished over two weeks," not "production startup."

### What it does (user-facing, minimum viable)

- Live map showing real aircraft positions, updated every \~10 seconds, with smooth marker movement  
- Click any plane to see callsign, altitude, speed, heading, origin country  
- A second view: historical SFO flight analytics with one clear ML insight (anomaly detection OR delay prediction — pick one)  
- A clean README with a screenshot/GIF that looks impressive in a thumbnail

### What this project is NOT

- Not a startup, not a real product, not deployed to production AWS  
- No Terraform, no CI/CD pipelines, no Secrets Manager, no multi-region anything  
- No WebSocket complexity — frontend polling every 10s is fine for a demo  
- No microservices — one FastAPI app, one frontend, two Docker containers  
- No comprehensive test suite — meaningful tests on the ML and ingestion logic only

### Why this scope

Recruiters spend 30 seconds to 2 minutes on a portfolio project. They look at: the README, a screenshot, and a sample of code quality on 2-3 files. A focused, polished demo with a great README beats a sprawling half-finished platform every time. Anything beyond this scope is a "phase 2" decision made after the demo is working end-to-end.

### Owner role

Owner (Micheal) is the architect and reviewer. Claude Code is the implementation partner. The point of building this is to be able to talk about it confidently in interviews — so every architectural and ML choice should be presented as a proposal first, with tradeoffs, and approved before implementation. Code you can't explain is worse than no code.

---

## 2\. Technical Stack (Minimal)

| Layer | Technology | Why |
| :---- | :---- | :---- |
| Backend | Python 3.11, FastAPI | Async, auto OpenAPI docs, easy to explain |
| DB | PostgreSQL 16 | Standard, reliable |
| Cache | Redis 7 (optional, only if needed) | Add if polling OpenSky causes rate-limit pain |
| Data | Pandas, NumPy | For historical SFO pipeline |
| ML | scikit-learn | One model done well — pick anomaly detection (DBSCAN) OR delay prediction (gradient boosting) |
| Frontend | React 18, TypeScript, Vite | Fast iteration, types matter for resume signal |
| Map | react-leaflet | Free, no API keys, good enough |
| Styling | Tailwind CSS | Fast, clean defaults |
| Local infra | Docker Compose | One command to run everything |
| Deploy (optional) | Render, Railway, or Fly.io | Free/cheap tier, push-to-deploy |
| Testing | pytest, vitest | Targeted tests on the parts that matter |

**Notably absent:** AWS, Terraform, Kubernetes, Kafka, Airflow, Celery, microservices, WebSockets, monorepo tooling. All of those would be valid in a bigger version, but they're cost without benefit at this scope.

---

## 3\. Data Sources

| Source | What it gives | How |
| :---- | :---- | :---- |
| **OpenSky Network REST API** | Live worldwide ADS-B state vectors (lat/lon/alt/velocity/heading/callsign) | `https://opensky-network.org/api/states/all` — free, anonymous tier supports 10s polling |
| **BTS On-Time Performance** | Historical US flight records — scheduled/actual times, delays, carrier, origin/dest | Bulk CSV from `transtats.bts.gov`, filter to SFO, one year is plenty |

That's it. Two sources. Don't add more.

---

## 4\. Directory Layout

aeroshift/

├── PROJECT_NOTES.md                \# Same as PROJECT\_PLAN.md; Claude Code auto-reads this

├── README.md                \# Public-facing; the highest-leverage file in the repo

├── docker-compose.yml       \# One command starts everything

├── .env.example

├── backend/

│   ├── app/

│   │   ├── main.py          \# FastAPI entry

│   │   ├── api.py           \# Route handlers (keep it flat — one file is fine)

│   │   ├── models.py        \# SQLAlchemy models

│   │   ├── schemas.py       \# Pydantic schemas

│   │   ├── ingestion.py     \# OpenSky polling worker

│   │   ├── ml.py            \# Model loading \+ inference

│   │   └── config.py

│   ├── tests/

│   ├── Dockerfile

│   └── pyproject.toml

├── frontend/

│   ├── src/

│   │   ├── App.tsx

│   │   ├── components/

│   │   ├── api.ts           \# API client

│   │   └── types.ts

│   ├── Dockerfile

│   ├── package.json

│   └── vite.config.ts

├── data/                    \# Gitignored except samples/

│   ├── raw/

│   └── processed/

├── notebooks/               \# Jupyter exploration

└── ml/

    ├── train.py             \# Training script (one file)

    └── artifacts/           \# Saved model (gitignored)

Flat is good. Resist the urge to add `services/`, `repositories/`, `domain/` subdirectories. This is a demo.

---

## 5\. Milestones (Hackathon Scope)

| \# | Milestone | Sessions | Deliverable |
| :---- | :---- | :---- | :---- |
| 1 | Skeleton \+ live ingestion | 2–3 | `docker-compose up` runs Postgres \+ FastAPI; worker writes live OpenSky data to DB |
| 2 | Frontend live map | 3–4 | React app with animated aircraft markers polling the backend every 10s |
| 3 | Historical pipeline \+ one ML model | 3–4 | BTS data cleaned, features engineered, ONE model trained with honest metrics |
| 4 | Wire ML into UI | 1–2 | Second page in frontend showing the ML insight (chart \+ a few flagged examples) |
| 5 | Polish: README, screenshot, optional deploy | 2–3 | Repo looks great when a recruiter opens it |

**Total: 11–16 sessions over 2–3 weeks.** Stop after Milestone 5 unless you decide you actually want to grow this into something bigger.

---

## 6\. Session Workflow

1. **Start:** `cd ~/projects/aeroshift && claude`. Send session opener.  
2. **Plan first:** For non-trivial sessions, ask Claude to propose an approach before writing code. Review.  
3. **Implement small:** Changes in small diffs. Use `/diff` to review.  
4. **Test the important parts:** Tests on ingestion parsing, ML feature math, and ML inference. Skip exhaustive UI tests.  
5. **Commit:** Conventional commits (`feat:`, `fix:`, `chore:`, etc.).  
6. **Close:** Say "done" (or any closing phrase). Claude Code auto-runs the end-of-session routine in section 10.

**When to start a new session:** switching layers (backend ↔ frontend ↔ ML), 90+ minutes in, or feature is done and committed. Use `/compact` mid-task, `/clear` for in-terminal reset, quit and restart `claude` for a true fresh start.

---

## 7\. Milestone-by-Milestone Prompts

### Milestone 1 — Skeleton \+ live ingestion

**Session 1.1 — Setup and plan:**

Read PROJECT\_PLAN.md. Look at current contents of the aeroshift directory. Summarize what's already here. Then propose a concrete plan for Milestone 1: restructure to match section 4, write docker-compose.yml with Postgres and a FastAPI service, define the schema for an `aircraft_states` table, and sketch the OpenSky polling worker. Don't write code yet — I want to review the plan.

**Session 1.2 — Build the skeleton:**

Read PROJECT_NOTES.md. We approved the Milestone 1 plan. Implement the skeleton: directory structure, docker-compose.yml, stub FastAPI app with /health, Alembic setup, the aircraft\_states model and initial migration, and pyproject.toml. After everything is created, verify `docker-compose up` starts the services and /health returns 200\. Make changes one file at a time so I can review.

**Session 1.3 — Live ingestion worker:**

Read PROJECT_NOTES.md. Now build the OpenSky ingestion. A single async worker that polls `https://opensky-network.org/api/states/all` every 10 seconds, parses state vectors, and writes rows to aircraft\_states. Include sensible retry/backoff on errors. Add a `/api/aircraft/current` endpoint returning the latest position per icao24. Write pytest tests for the parser using a saved sample OpenSky response. Don't worry about WebSockets — polling is fine.

### Milestone 2 — Frontend live map

**Session 2.1 — Plan \+ scaffold:**

Read PROJECT_NOTES.md. Milestone 2: React \+ TS \+ Vite frontend with a live aircraft map. First propose: directory structure under `frontend/`, the map approach (react-leaflet), and how we'll handle the 10-second polling cycle plus smooth marker animation between updates. No code yet — show me the plan.

**Session 2.2 — Build the map:**

Read PROJECT_NOTES.md. Plan approved. Scaffold the frontend (Vite \+ React \+ TS \+ Tailwind \+ ESLint), create a typed API client for `/api/aircraft/current`, and render aircraft as Leaflet markers. Update every 10 seconds. Verify `npm run dev` shows real planes on the map.

**Session 2.3 — Animation and detail panel:**

Read PROJECT_NOTES.md. Two improvements: (1) smoothly animate markers from previous position to new position over the 10s polling interval — small visual win that makes the demo feel alive; (2) clicking a marker opens a side panel showing callsign, altitude (m and ft), ground speed (m/s and knots), heading, and origin country.

### Milestone 3 — Historical pipeline \+ one ML model

**Session 3.1 — Decide and plan:**

Read PROJECT_NOTES.md. Milestone 3: historical SFO pipeline plus ONE ML capability. Two options on the table — (A) DBSCAN anomaly detection on engineered trajectory features, or (B) gradient boosting classifier for delay prediction. Walk me through which is more impressive for a portfolio project, easier to explain in an interview, and faster to get a real result on. Recommend one, then propose the BTS data download plan, the cleaning steps, and the features we'll engineer. No code.

**Session 3.2 — Data download and clean:**

Read PROJECT_NOTES.md. Write a one-shot script `ml/download_and_clean.py` that downloads one year of BTS On-Time data filtered to SFO (origin or destination), cleans it, and saves `data/processed/sfo_flights.parquet`. Print row counts, date range, and summary stats after running. Handle missing values and timezone alignment.

**Session 3.3 — Features and train:**

Read PROJECT_NOTES.md. Write `ml/train.py` that loads sfo\_flights.parquet, engineers the features we agreed on, trains the chosen model with a time-based train/test split, prints honest metrics (with a baseline for comparison), and saves the model \+ scaler to `ml/artifacts/`. Include a brief EDA notebook at `notebooks/eda.ipynb` for sanity checks.

**Session 3.4 — Inference endpoint:**

Read PROJECT_NOTES.md. Wire the trained model into FastAPI: load artifacts at app startup, add an endpoint that takes inputs and returns the prediction (anomaly score or delay probability) plus the top contributing features. Write tests with fixture artifacts.

### Milestone 4 — Wire ML into UI

**Session 4.1 — Plan the view:**

Read PROJECT_NOTES.md. Add a second page to the frontend showing the ML insight. Propose the layout — a chart (Recharts is fine) summarizing model output across the SFO dataset, plus a table of the top flagged or highest-risk flights with their key features. Don't overdesign. No code yet.

**Session 4.2 — Build the view:**

Read PROJECT_NOTES.md. Implement the analytics page. Add a nav switcher between Live Map and Analytics. Hit the backend for aggregated data — add backend endpoints as needed. Use Tailwind for styling.

### Milestone 5 — Polish

**Session 5.1 — README:**

Read PROJECT_NOTES.md. Write a real README.md. Sections: what Aero is (2-3 sentences), screenshot placeholder, tech stack, architecture diagram (Mermaid), local dev quickstart (literally `docker-compose up`), how the ML works (one paragraph), honest metrics from train.py, what I'd add next. Aim for under 250 lines but make every section count.

**Session 5.2 — Capture screenshot \+ audit:**

Read PROJECT_NOTES.md. Two tasks. First, walk me through capturing a good screenshot/GIF of the live map and adding it to README.md (referencing it from an `assets/` folder). Second, audit the codebase for embarrassing issues: dead code, console.logs, hardcoded localhost URLs, missing type hints, TODO comments. List them, don't fix them — I'll triage.

**Session 5.3 — Optional deploy:**

Read PROJECT_NOTES.md. I want to deploy this cheaply. Propose options between Render, Railway, and Fly.io for this stack (FastAPI \+ Postgres \+ a static frontend bundle). Pick one based on free-tier viability and simplest setup. Walk me through the deploy steps. We're not doing AWS.

---

## 8\. Conventions (Light)

### Python

- Type hints on function signatures (not obsessively everywhere)  
- Ruff for lint \+ format  
- pytest for tests on ingestion parsing, ML math, and the inference endpoint  
- Pydantic v2 for API schemas

### TypeScript

- Strict mode on, no `any`  
- ESLint \+ Prettier defaults  
- Functional components, hooks only

### Git

- Conventional commits (`feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`)  
- Commit per logical change

### Secrets

- `.env` gitignored, `.env.example` in repo

---

## 9\. Honesty rules

The original resume bullets included specific numbers ("85% accuracy", "100K+ records"). Rule for this project: **no number appears in the README or on a resume unless it comes out of a script in this repo.** If the model lands at 71% F1 instead of 85%, the README says 71%. Two reasons:

1. Interviewers will ask how you computed it. If the answer is "I asked Claude to write something that sounds good," you'll be caught.  
2. An honestly-reported real result is more impressive than a fake high number — it shows you know what evaluation actually means.

For the chosen model:

- Time-based train/test split (not random — this is time-series-ish)  
- Report accuracy, precision, recall, F1, AND a baseline (e.g., "always predict majority class")  
- Save metrics to a JSON alongside the model artifact so the README references the same numbers

After the project is done, rewrite the resume bullets based on what you actually built. Honest bullets you can defend in interviews beat impressive bullets you can't.

---

## 10\. Auto-update behavior

At the end of every session — triggered by the user typing "done", "wrapping up", "end session", "bye", "goodbye", "that's it", or any similar closing phrase — Claude Code automatically performs the following without asking for confirmation:

(a) **Updates section 11 (Current Status)** with: date, milestone number and name, bullet list of what was accomplished, tests passing status, open issues / gotchas / things to remember, and a single concrete next-session goal.

(b) **Appends a one-line entry to `DECISIONS.md`** (creates the file if it doesn't exist) for any architectural or technical decision made this session, in the format: `YYYY-MM-DD — Chose X over Y because Z.`

(c) **Runs `git add -A`**, commits with a conventional commit message describing the session's work (no Claude attribution), and pushes to `origin` if a remote exists.

---

## 11\. Current Status

**Last session:** 2026-05-20
**Milestone:** 1 — Skeleton + live ingestion

**Completed this session:**
- Scaffolded `src/backend/` with FastAPI app, SQLAlchemy `AircraftState` ORM model, Pydantic v2 schemas, `/health` and `/api/v1/states` endpoints
- Alembic configured with initial migration `0001_create_aircraft_states` (composite PK on `(icao24, observed_at)`, indexes for recent-window and per-aircraft queries, partial index for airborne rows)
- OpenSky client (`httpx`), normalizer (drops null `time_position`, lowercases icao24, trims callsign), and polling worker that upserts via `INSERT … ON CONFLICT DO NOTHING` and publishes per-aircraft updates to Redis `aircraft.updates`
- `infra/docker-compose.yml` with `postgres`, `redis`, one-shot `migrate`, `backend`, `ingestion`; `infra/Dockerfile.backend`; `.env.example`

**Tests passing:** Yes — 7/7 normalizer unit tests (`tests/unit/test_normalizer.py`).

**Open issues / gotchas / things to remember:**
- Nothing has been run end-to-end yet — `docker compose up` not exercised, no real OpenSky tick verified
- Currently using `/Users/micheal/projects/depsched/.venv` instead of aeroshift's own venv — must fix next session
- Dockerfile duplicates the dep list from `pyproject.toml` inline; consolidate later
- No retention/partitioning on `aircraft_states` — table will grow unbounded
- `/states` latest-per-icao24 query uses `DISTINCT ON` subquery; fine for thousands but materialize at scale

**Next session goal:** Create aeroshift's own venv, bring up `docker compose`, and verify `/health` + `/api/v1/states` + Redis pub/sub end-to-end with real OpenSky data.

---

## 12\. Useful mid-session prompts

- *"Explain this code to me as if an interviewer is asking why I wrote it this way."*  
- *"Stop. Before more code, walk me through your plan and the tradeoffs."*  
- *"What's the simpler version of this? I think we're overengineering."*  
- *"Write a failing test first, then implement."*  
- *"What would a senior engineer flag in this PR?"*

---

## 13\. Phase 2 (only if you decide to grow this)

If after Milestone 5 you want to expand Aero into something bigger, the natural next steps in order would be:

1. Add the second ML model (whichever you didn't pick in Milestone 3\)  
2. Replace polling with WebSockets and Redis pub/sub  
3. Deploy to AWS with proper IaC  
4. Add CI/CD via GitHub Actions  
5. Add historical trajectory replay

But don't pre-plan for phase 2\. Finish the demo, see how you feel about the project, then decide.

---

*End of context document. Section 11 (Current Status) is maintained automatically by the end-of-session routine in section 10\.*  
