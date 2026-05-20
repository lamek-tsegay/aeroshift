from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AircraftState
from app.schemas.aircraft_state import AircraftStateRead

router = APIRouter(prefix="/states", tags=["states"])


@router.get("", response_model=list[AircraftStateRead])
def list_latest_states(
    limit: int = Query(default=500, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> list[AircraftState]:
    """Latest known state per aircraft (one row per icao24)."""
    latest = (
        select(
            AircraftState.icao24,
            AircraftState.observed_at,
        )
        .distinct(AircraftState.icao24)
        .order_by(AircraftState.icao24, AircraftState.observed_at.desc())
        .subquery()
    )
    stmt = (
        select(AircraftState)
        .where(
            tuple_(AircraftState.icao24, AircraftState.observed_at).in_(
                select(latest.c.icao24, latest.c.observed_at)
            )
        )
        .order_by(AircraftState.observed_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


@router.get("/{icao24}", response_model=list[AircraftStateRead])
def get_history(
    icao24: str,
    limit: int = Query(default=200, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> list[AircraftState]:
    icao = icao24.lower().strip()
    if len(icao) != 6:
        raise HTTPException(status_code=400, detail="icao24 must be 6 hex chars")
    stmt = (
        select(AircraftState)
        .where(AircraftState.icao24 == icao)
        .order_by(AircraftState.observed_at.desc())
        .limit(limit)
    )
    rows = list(db.scalars(stmt).all())
    if not rows:
        raise HTTPException(status_code=404, detail="aircraft not found")
    return rows
