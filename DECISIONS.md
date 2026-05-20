# Architectural & Technical Decisions

One line per decision, newest at the bottom. Format: `YYYY-MM-DD — Chose X over Y because Z.`

2026-05-20 — Chose a composite primary key `(icao24, observed_at)` on `aircraft_states` over a synthetic `id` because the pair is naturally unique per observation and lets the ingestion worker upsert idempotently within a polling tick via `ON CONFLICT DO NOTHING`.
2026-05-20 — Chose to run ingestion as a separate container sharing the backend image over embedding the poller in the FastAPI process because it lets us scale, restart, or kill ingestion independently of the web layer while reusing one Dockerfile.
2026-05-20 — Chose to persist SI units (meters, m/s) in the database over storing imperial units because OpenSky emits SI natively; conversion to feet/knots happens at the frontend so the API stays the single source of truth.
2026-05-20 — Chose to split `src/backend/ingestion/` from `src/backend/app/` over keeping the poller inside the FastAPI package because the worker container shouldn't pull in routing code and the boundary keeps responsibilities clear.
2026-05-20 — Chose to split the context doc into `PROJECT_PLAN.md` (immutable plan) and `PROJECT_NOTES.md` (auto-updated working copy) over a single `CLAUDE.md` because the rename lets the master plan stay stable while the per-session log mutates independently, and both can now be tracked publicly.
2026-05-20 — Chose to keep `CLAUDE.md` as a gitignored symlink to `PROJECT_NOTES.md` over renaming the file Claude Code reads because the auto-read still keys on `CLAUDE.md`; the symlink preserves that hook without polluting git history.
2026-05-20 — Chose a closing-phrase trigger for the end-of-session routine over explicit per-session prompts because the user wants the update + commit + push to run automatically without confirmation.
