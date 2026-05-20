"""ADS-B ingestion worker.

Polls OpenSky on a fixed interval, upserts state vectors, publishes per-aircraft
updates to Redis for live consumers.
"""
import json
import logging
import signal
import time
from types import FrameType
from typing import Any

import httpx
import redis
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.models import AircraftState
from ingestion.normalizer import normalize_batch
from ingestion.opensky_client import OpenSkyClient

log = logging.getLogger(__name__)


class _Stop:
    def __init__(self) -> None:
        self.stopped = False

    def request(self, signum: int, _frame: FrameType | None) -> None:
        log.info("received signal %s, stopping", signum)
        self.stopped = True


def _upsert(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    stmt = pg_insert(AircraftState).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=["icao24", "observed_at"])
    with SessionLocal() as session:
        result = session.execute(stmt)
        session.commit()
        return result.rowcount or 0


def _publish(client: "redis.Redis[bytes]", channel: str, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        payload = {**row}
        payload["observed_at"] = row["observed_at"].isoformat()
        if row.get("last_contact") is not None:
            payload["last_contact"] = row["last_contact"].isoformat()
        client.publish(channel, json.dumps(payload))


def run() -> None:
    configure_logging()
    settings = get_settings()
    stop = _Stop()
    signal.signal(signal.SIGINT, stop.request)
    signal.signal(signal.SIGTERM, stop.request)

    opensky = OpenSkyClient()
    redis_client: "redis.Redis[bytes]" = redis.Redis.from_url(settings.redis_url)
    interval = settings.opensky_poll_seconds
    channel = settings.redis_updates_channel

    log.info("ingestion worker starting (interval=%ss)", interval)
    while not stop.stopped:
        started = time.monotonic()
        try:
            payload = opensky.fetch_states()
            vectors: list[list[Any]] = payload.get("states") or []
            rows = normalize_batch(vectors)
            inserted = _upsert(rows)
            _publish(redis_client, channel, rows)
            log.info(
                "tick: received=%d normalized=%d inserted=%d",
                len(vectors),
                len(rows),
                inserted,
            )
        except httpx.HTTPError as exc:
            log.warning("opensky fetch failed: %s", exc)
        except Exception:
            log.exception("ingestion tick failed")

        elapsed = time.monotonic() - started
        sleep_for = max(0.0, interval - elapsed)
        # Sleep in small slices so SIGTERM is responsive.
        end = time.monotonic() + sleep_for
        while not stop.stopped and time.monotonic() < end:
            time.sleep(min(0.5, end - time.monotonic()))

    opensky.close()
    redis_client.close()
    log.info("ingestion worker stopped")


if __name__ == "__main__":
    run()
