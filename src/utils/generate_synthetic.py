# src/utils/generate_synthetic.py
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class SynthConfig:
    n_flights: int = 300
    seed: int = 7
    dt_s: int = 5               # time step
    n_points: int = 180         # 180 * 5s = 15 minutes
    start_alt_ft: int = 12000
    end_alt_ft: int = 0

    # "SFO-ish" center (rough, just for synthetic geometry)
    center_lat: float = 37.6213
    center_lon: float = -122.3790


def _add_noise(x: np.ndarray, scale: float) -> np.ndarray:
    return x + np.random.normal(0, scale, size=x.shape)


def _straight_in(cfg: SynthConfig) -> pd.DataFrame:
    # Approach from west-ish to the runway center
    t = np.arange(cfg.n_points) * cfg.dt_s

    # Simple line in lat/lon
    lat0, lon0 = cfg.center_lat + 0.15, cfg.center_lon - 0.35
    lat1, lon1 = cfg.center_lat, cfg.center_lon

    lat = np.linspace(lat0, lat1, cfg.n_points)
    lon = np.linspace(lon0, lon1, cfg.n_points)

    # Smooth descent
    alt = np.linspace(cfg.start_alt_ft, cfg.end_alt_ft, cfg.n_points)

    # Mild speed decay
    gs = np.linspace(240, 140, cfg.n_points)

    lat = _add_noise(lat, 0.0006)
    lon = _add_noise(lon, 0.0006)
    alt = _add_noise(alt, 40)
    gs = _add_noise(gs, 3)

    df = pd.DataFrame({"time_s": t, "lat": lat, "lon": lon, "altitude": alt, "groundspeed": gs})
    df["type"] = "straight_in"
    return df


def _downwind(cfg: SynthConfig) -> pd.DataFrame:
    # Two legs: downwind (parallel-ish) then base to final
    t = np.arange(cfg.n_points) * cfg.dt_s

    n1 = int(cfg.n_points * 0.55)
    n2 = cfg.n_points - n1

    # downwind leg
    lat_a, lon_a = cfg.center_lat + 0.10, cfg.center_lon - 0.05
    lat_b, lon_b = cfg.center_lat + 0.10, cfg.center_lon - 0.45

    lat1 = np.linspace(lat_a, lat_b, n1)
    lon1 = np.linspace(lon_a, lon_b, n1)

    # base-to-final curve back to center
    lat2 = np.linspace(lat_b, cfg.center_lat, n2)
    lon2 = np.linspace(lon_b, cfg.center_lon, n2)

    lat = np.concatenate([lat1, lat2])
    lon = np.concatenate([lon1, lon2])

    # add a gentle curve near the join
    k = np.linspace(0, 1, cfg.n_points)
    lat = lat + 0.01 * np.sin(2 * math.pi * k) * np.exp(-3 * (k - 0.6) ** 2)

    alt = np.linspace(cfg.start_alt_ft, cfg.end_alt_ft, cfg.n_points)
    gs = np.linspace(250, 135, cfg.n_points)

    lat = _add_noise(lat, 0.0009)
    lon = _add_noise(lon, 0.0009)
    alt = _add_noise(alt, 70)
    gs = _add_noise(gs, 4)

    df = pd.DataFrame({"time_s": t, "lat": lat, "lon": lon, "altitude": alt, "groundspeed": gs})
    df["type"] = "downwind"
    return df


def _holding(cfg: SynthConfig) -> pd.DataFrame:
    # Start inbound, do a holding loop, then continue to center
    t = np.arange(cfg.n_points) * cfg.dt_s
    lat0, lon0 = cfg.center_lat + 0.12, cfg.center_lon - 0.30

    lat = np.zeros(cfg.n_points)
    lon = np.zeros(cfg.n_points)

    # segments
    n_in = int(cfg.n_points * 0.35)
    n_loop = int(cfg.n_points * 0.35)
    n_out = cfg.n_points - (n_in + n_loop)

    # inbound segment
    lat[:n_in] = np.linspace(lat0, cfg.center_lat + 0.08, n_in)
    lon[:n_in] = np.linspace(lon0, cfg.center_lon - 0.22, n_in)

    # loop (ellipse)
    loop_center_lat = cfg.center_lat + 0.07
    loop_center_lon = cfg.center_lon - 0.22
    theta = np.linspace(0, 2 * math.pi, n_loop)
    lat[n_in:n_in + n_loop] = loop_center_lat + 0.03 * np.cos(theta)
    lon[n_in:n_in + n_loop] = loop_center_lon + 0.06 * np.sin(theta)

    # final segment to runway center
    lat[n_in + n_loop:] = np.linspace(loop_center_lat, cfg.center_lat, n_out)
    lon[n_in + n_loop:] = np.linspace(loop_center_lon, cfg.center_lon, n_out)

    # altitude: descend, flatten during hold, then descend again
    alt = np.linspace(cfg.start_alt_ft, 7000, n_in)
    alt_hold = np.linspace(7000, 6500, n_loop)
    alt_out = np.linspace(6500, cfg.end_alt_ft, n_out)
    alt = np.concatenate([alt, alt_hold, alt_out])

    # speed: steady during hold
    gs_in = np.linspace(240, 210, n_in)
    gs_hold = np.linspace(210, 200, n_loop)
    gs_out = np.linspace(200, 135, n_out)
    gs = np.concatenate([gs_in, gs_hold, gs_out])

    lat = _add_noise(lat, 0.0010)
    lon = _add_noise(lon, 0.0010)
    alt = _add_noise(alt, 90)
    gs = _add_noise(gs, 5)

    df = pd.DataFrame({"time_s": t, "lat": lat, "lon": lon, "altitude": alt, "groundspeed": gs})
    df["type"] = "holding"
    return df


def generate_dataset(cfg: SynthConfig) -> pd.DataFrame:
    np.random.seed(cfg.seed)
    random.seed(cfg.seed)

    makers = [_straight_in, _downwind, _holding]
    weights = [0.6, 0.25, 0.15]  # baseline mix

    flights = []
    for i in range(cfg.n_flights):
        maker = random.choices(makers, weights=weights, k=1)[0]
        df = maker(cfg).copy()
        df["flight_id"] = f"syn_{i:05d}"
        flights.append(df)

    return pd.concat(flights, ignore_index=True)


def main():
    cfg = SynthConfig()
    out_dir = Path("data/processed/synthetic")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = generate_dataset(cfg)
    out_path = out_dir / "sfo_synthetic_arrivals.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote: {out_path}  rows={len(df):,} flights={cfg.n_flights}")


if __name__ == "__main__":
    main()
