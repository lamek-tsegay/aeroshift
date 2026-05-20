"""Convert OpenSky state vector tuples into AircraftState row dicts.

OpenSky /states/all returns each aircraft as a positional array. Indices:
    0  icao24            str
    1  callsign          str | None
    2  origin_country    str
    3  time_position     int seconds | None  (drop row if None)
    4  last_contact      int seconds
    5  longitude         float | None
    6  latitude          float | None
    7  baro_altitude     float | None  (meters)
    8  on_ground         bool
    9  velocity          float | None  (m/s)
    10 true_track        float | None  (degrees)
    11 vertical_rate     float | None  (m/s)
    12 sensors           list[int] | None         (unused)
    13 geo_altitude      float | None  (meters)
    14 squawk            str | None
    15 spi               bool                     (unused)
    16 position_source   int
"""
from datetime import datetime, timezone
from typing import Any


def _epoch_to_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    return datetime.fromtimestamp(int(value), tz=timezone.utc)


def _clean_str(value: Any, max_len: int) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return s[:max_len]


def normalize_state(vector: list[Any]) -> dict[str, Any] | None:
    """Return a row dict for AircraftState, or None if the row should be dropped."""
    if len(vector) < 17:
        return None

    icao_raw = vector[0]
    if not icao_raw:
        return None
    icao24 = str(icao_raw).strip().lower()
    if len(icao24) != 6:
        return None

    observed_at = _epoch_to_dt(vector[3])
    if observed_at is None:
        # No position fix; drop — PK requires non-null observed_at.
        return None

    return {
        "icao24": icao24,
        "observed_at": observed_at,
        "callsign": _clean_str(vector[1], 8),
        "origin_country": _clean_str(vector[2], 255),
        "last_contact": _epoch_to_dt(vector[4]),
        "longitude": vector[5],
        "latitude": vector[6],
        "baro_altitude_m": vector[7],
        "on_ground": bool(vector[8]),
        "velocity_ms": vector[9],
        "true_track_deg": vector[10],
        "vertical_rate_ms": vector[11],
        "geo_altitude_m": vector[13],
        "squawk": _clean_str(vector[14], 4),
        "position_source": vector[16],
    }


def normalize_batch(vectors: list[list[Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for v in vectors:
        row = normalize_state(v)
        if row is not None:
            rows.append(row)
    return rows
