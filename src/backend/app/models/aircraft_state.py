from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AircraftState(Base):
    __tablename__ = "aircraft_states"

    icao24: Mapped[str] = mapped_column(String(6), primary_key=True)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True
    )

    callsign: Mapped[str | None] = mapped_column(String(8), nullable=True)
    origin_country: Mapped[str | None] = mapped_column(String, nullable=True)
    last_contact: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    baro_altitude_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    geo_altitude_m: Mapped[float | None] = mapped_column(Float, nullable=True)

    on_ground: Mapped[bool] = mapped_column(Boolean, nullable=False)

    velocity_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    true_track_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    vertical_rate_ms: Mapped[float | None] = mapped_column(Float, nullable=True)

    squawk: Mapped[str | None] = mapped_column(String(4), nullable=True)
    position_source: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
