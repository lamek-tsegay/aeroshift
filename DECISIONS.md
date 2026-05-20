# Architectural & Technical Decisions

One line per decision, newest at the bottom. Format: `YYYY-MM-DD — Chose X over Y because Z.`

2026-05-20 — Chose a composite primary key `(icao24, observed_at)` on `aircraft_states` over a synthetic `id` because the pair is naturally unique per observation and lets the ingestion worker upsert idempotently within a polling tick via `ON CONFLICT DO NOTHING`.
2026-05-20 — Chose to run ingestion as a separate container sharing the backend image over embedding the poller in the FastAPI process because it lets us scale, restart, or kill ingestion independently of the web layer while reusing one Dockerfile.
2026-05-20 — Chose to persist SI units (meters, m/s) in the database over storing imperial units because OpenSky emits SI natively; conversion to feet/knots happens at the frontend so the API stays the single source of truth.
2026-05-20 — Chose to split `src/backend/ingestion/` from `src/backend/app/` over keeping the poller inside the FastAPI package because the worker container shouldn't pull in routing code and the boundary keeps responsibilities clear.
