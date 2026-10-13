"""
Generates synthetic broadcast/OTT audience data for analysis.

All numbers are simulated from the parameters below with a seeded RNG. They
illustrate the analysis pipeline; they are not real ratings or real audience data.
"""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

DEFAULT_SEED = 42
GENRES   = ["News", "Sports", "Drama", "Entertainment", "Documentary", "Reality", "Kids"]
SLOTS    = ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00", "23:00"]
PRIME_SLOTS = ("18:00", "21:00")
PLATFORMS = {"Linear TV": 0.45, "App - iOS": 0.20, "App - Android": 0.18, "CTV": 0.12, "Web": 0.05}
UNIVERSE = 1_200_000   # hypothetical TV-household universe used for rating_pct


def _rng(seed: int | None) -> np.random.Generator:
    return np.random.default_rng(DEFAULT_SEED if seed is None else seed)


def generate_daily_ratings(start: date, end: date, growth_multiple: float = 3.0,
                           seed: int | None = None) -> pd.DataFrame:
    """Daily audience per time slot x genre.

    The underlying audience level rises linearly from 1x on `start` to
    `growth_multiple`x on `end`, with ±15% annual seasonality, a 1.4x prime-time
    multiplier and ±15% day-to-day noise.
    """
    if end <= start:
        raise ValueError("end must be after start")
    rng = _rng(seed)
    total_days = (end - start).days
    rows = []
    for day_idx in range(total_days + 1):
        current = start + timedelta(days=day_idx)
        growth_factor = 1.0 + (growth_multiple - 1.0) * (day_idx / total_days)
        seasonal = 1.0 + 0.15 * np.sin(2 * np.pi * day_idx / 365)
        for slot in SLOTS:
            prime = 1.4 if slot in PRIME_SLOTS else 1.0
            for genre in GENRES:
                base = rng.integers(8_000, 40_000)
                audience = int(base * growth_factor * seasonal * prime * rng.uniform(0.85, 1.15))
                rows.append({
                    "date": current,
                    "slot": slot,
                    "genre": genre,
                    "audience": audience,
                    "rating_pct": round(audience / UNIVERSE * 100, 2),
                })
    return pd.DataFrame(rows)


def generate_platform_metrics(start: date, end: date, start_viewers: int = 25_000,
                              peak_viewers: int = 50_000, seed: int | None = None) -> pd.DataFrame:
    """Monthly viewers per platform (linear TV + apps + CTV + web).

    Total monthly viewers grow linearly from `start_viewers` in the first month to
    `peak_viewers` in the last month (±8% noise per platform), split by fixed shares.
    """
    rng = _rng(seed)
    total_months = (end.year - start.year) * 12 + end.month - start.month + 1
    rows = []
    for m in range(total_months):
        month = date(start.year + (start.month + m - 1) // 12, (start.month + m - 1) % 12 + 1, 1)
        frac = m / max(total_months - 1, 1)
        total = start_viewers + (peak_viewers - start_viewers) * frac
        for platform, share in PLATFORMS.items():
            rows.append({"month": month, "channel": platform,
                         "monthly_viewers": int(total * share * rng.uniform(0.92, 1.08))})
    return pd.DataFrame(rows)


def generate_content_roi(n: int = 80, seed: int | None = None) -> pd.DataFrame:
    """Acquisition cost vs. audience delivered per title.

    `total_audience` is the sum of per-episode audiences (episode views, not unique
    viewers), so `cost_per_viewer` is cost per episode view.
    """
    rng = _rng(seed)
    genres = rng.choice(GENRES, n)
    costs = rng.integers(5_000, 120_000, n)
    audience_per_ep = rng.integers(15_000, 280_000, n)
    episodes = rng.integers(1, 26, n)
    return pd.DataFrame({
        "title_id": [f"T{i:03d}" for i in range(n)],
        "genre": genres,
        "acquisition_cost_usd": costs,
        "episodes": episodes,
        "avg_audience_per_ep": audience_per_ep,
        "total_audience": audience_per_ep * episodes,
        "cost_per_viewer": (costs / (audience_per_ep * episodes)).round(4),
    })
