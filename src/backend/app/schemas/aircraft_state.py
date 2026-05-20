from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AircraftStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    icao24: str
    observed_at: datetime
    callsign: str | None
    origin_country: str | None
    last_contact: datetime | None
    longitude: float | None
    latitude: float | None
    baro_altitude_m: float | None
    geo_altitude_m: float | None
    on_ground: bool
    velocity_ms: float | None
    true_track_deg: float | None
    vertical_rate_ms: float | None
    squawk: str | None
    position_source: int | None
