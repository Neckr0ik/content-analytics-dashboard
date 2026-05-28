"""Generates realistic synthetic broadcast/OTT audience data for analysis."""
import numpy as np
import pandas as pd
from datetime import date, timedelta

RNG = np.random.default_rng(42)

GENRES = ["News", "Sports", "Drama", "Entertainment", "Documentary", "Reality", "Kids"]
SLOTS  = ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00", "23:00"]
CHANNELS = ["Linear TV", "App - iOS", "App - Android", "CTV", "Web"]

def generate_daily_ratings(start: date, end: date) -> pd.DataFrame:
    """Daily audience ratings per time slot, simulating 300% growth over 3 years."""
    rows = []
    total_days = (end - start).days
    current = start
    while current <= end:
        day_idx = (current - start).days
        growth_factor = 1.0 + 2.0 * (day_idx / total_days)  # 1x → 3x over period
        seasonal = 1.0 + 0.15 * np.sin(2 * np.pi * day_idx / 365)
        for slot in SLOTS:
            for genre in GENRES:
                prime = 1.4 if slot in ("18:00", "21:00") else 1.0
                base = RNG.integers(8_000, 40_000)
                audience = int(base * growth_factor * seasonal * prime * RNG.uniform(0.85, 1.15))
                rows.append({
                    "date": current,
                    "slot": slot,
                    "genre": genre,
                    "audience": audience,
                    "rating_pct": round(audience / 1_200_000 * 100, 2),
                })
        current += timedelta(days=1)
    return pd.DataFrame(rows)

def generate_app_metrics(start: date, end: date) -> pd.DataFrame:
    """Monthly app viewer counts across platforms, targeting 50k MAU at peak."""
    rows = []
    total_months = ((end.year - start.year) * 12 + end.month - start.month) + 1
    for m in range(total_months):
        month = date(start.year + (start.month + m - 1) // 12,
                     (start.month + m - 1) % 12 + 1, 1)
        growth = 1.0 + 49_000 / 50_000 * (m / total_months)
        for channel in CHANNELS:
            weights = {"Linear TV": 0.45, "App - iOS": 0.20,
                       "App - Android": 0.18, "CTV": 0.12, "Web": 0.05}
            base = int(50_000 * weights[channel] * growth * RNG.uniform(0.92, 1.08))
            rows.append({"month": month, "channel": channel, "monthly_viewers": base})
    return pd.DataFrame(rows)

def generate_content_roi(n: int = 80) -> pd.DataFrame:
    """Content acquisition cost vs. audience delivered per title."""
    genres = RNG.choice(GENRES, n)
    costs  = RNG.integers(5_000, 120_000, n)
    audience_per_ep = RNG.integers(15_000, 280_000, n)
    episodes = RNG.integers(1, 26, n)
    return pd.DataFrame({
        "title_id": [f"T{i:03d}" for i in range(n)],
        "genre": genres,
        "acquisition_cost_usd": costs,
        "episodes": episodes,
        "avg_audience_per_ep": audience_per_ep,
        "total_audience": audience_per_ep * episodes,
        "cost_per_viewer": (costs / (audience_per_ep * episodes)).round(4),
    })
