"""create aircraft_states

Revision ID: 0001
Revises:
Create Date: 2026-05-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "aircraft_states",
        sa.Column("icao24", sa.String(length=6), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("callsign", sa.String(length=8), nullable=True),
        sa.Column("origin_country", sa.String(), nullable=True),
        sa.Column("last_contact", sa.DateTime(timezone=True), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("baro_altitude_m", sa.Float(), nullable=True),
        sa.Column("geo_altitude_m", sa.Float(), nullable=True),
        sa.Column("on_ground", sa.Boolean(), nullable=False),
        sa.Column("velocity_ms", sa.Float(), nullable=True),
        sa.Column("true_track_deg", sa.Float(), nullable=True),
        sa.Column("vertical_rate_ms", sa.Float(), nullable=True),
        sa.Column("squawk", sa.String(length=4), nullable=True),
        sa.Column("position_source", sa.SmallInteger(), nullable=True),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("icao24", "observed_at"),
    )
    op.create_index(
        "ix_aircraft_states_observed_at",
        "aircraft_states",
        [sa.text("observed_at DESC")],
    )
    op.create_index(
        "ix_aircraft_states_icao24_observed_at",
        "aircraft_states",
        ["icao24", sa.text("observed_at DESC")],
    )
    op.create_index(
        "ix_aircraft_states_airborne",
        "aircraft_states",
        ["observed_at"],
        postgresql_where=sa.text("on_ground = false"),
    )


def downgrade() -> None:
    op.drop_index("ix_aircraft_states_airborne", table_name="aircraft_states")
    op.drop_index("ix_aircraft_states_icao24_observed_at", table_name="aircraft_states")
    op.drop_index("ix_aircraft_states_observed_at", table_name="aircraft_states")
    op.drop_table("aircraft_states")
