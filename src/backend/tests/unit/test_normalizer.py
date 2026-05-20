from datetime import datetime, timezone

from ingestion.normalizer import normalize_batch, normalize_state


def _vector(**overrides: object) -> list[object]:
    base: list[object] = [
        "abc123",          # 0 icao24
        "UAL245  ",        # 1 callsign (OpenSky pads with spaces)
        "United States",   # 2 origin_country
        1_700_000_000,     # 3 time_position
        1_700_000_005,     # 4 last_contact
        -122.4,            # 5 longitude
        37.6,              # 6 latitude
        10000.0,           # 7 baro_altitude
        False,             # 8 on_ground
        250.0,             # 9 velocity
        90.0,              # 10 true_track
        -1.5,              # 11 vertical_rate
        None,              # 12 sensors
        10100.0,           # 13 geo_altitude
        "1200",            # 14 squawk
        False,             # 15 spi
        0,                 # 16 position_source
    ]
    for k, v in overrides.items():
        idx = {
            "icao24": 0, "callsign": 1, "origin_country": 2, "time_position": 3,
            "last_contact": 4, "longitude": 5, "latitude": 6, "baro_altitude": 7,
            "on_ground": 8, "velocity": 9, "true_track": 10, "vertical_rate": 11,
            "geo_altitude": 13, "squawk": 14, "position_source": 16,
        }[k]
        base[idx] = v
    return base


def test_normalize_state_happy_path() -> None:
    row = normalize_state(_vector())
    assert row is not None
    assert row["icao24"] == "abc123"
    assert row["callsign"] == "UAL245"
    assert row["observed_at"] == datetime.fromtimestamp(1_700_000_000, tz=timezone.utc)
    assert row["latitude"] == 37.6
    assert row["on_ground"] is False
    assert row["squawk"] == "1200"


def test_normalize_state_lowercases_icao24() -> None:
    row = normalize_state(_vector(icao24="ABC123"))
    assert row is not None
    assert row["icao24"] == "abc123"


def test_normalize_state_drops_when_time_position_is_null() -> None:
    assert normalize_state(_vector(time_position=None)) is None


def test_normalize_state_drops_when_icao24_invalid() -> None:
    assert normalize_state(_vector(icao24="")) is None
    assert normalize_state(_vector(icao24="xx")) is None
    assert normalize_state(_vector(icao24=None)) is None


def test_normalize_state_handles_empty_callsign() -> None:
    row = normalize_state(_vector(callsign="        "))
    assert row is not None
    assert row["callsign"] is None


def test_normalize_state_handles_short_vector() -> None:
    assert normalize_state(["abc123", "UAL245"]) is None


def test_normalize_batch_filters_invalid_rows() -> None:
    good = _vector()
    bad_time = _vector(time_position=None)
    bad_icao = _vector(icao24="")
    rows = normalize_batch([good, bad_time, bad_icao])
    assert len(rows) == 1
    assert rows[0]["icao24"] == "abc123"
