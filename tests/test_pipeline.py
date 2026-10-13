from datetime import date

import pandas as pd
import pytest

from src.analyzer import AudienceAnalyzer, ROIAnalyzer
from src.data_generator import (GENRES, SLOTS, generate_content_roi, generate_daily_ratings,
                                generate_platform_metrics)

START, END = date(2022, 6, 1), date(2025, 5, 31)


@pytest.fixture(scope="module")
def ratings():
    return generate_daily_ratings(START, END)


def test_ratings_shape_and_reproducibility(ratings):
    days = (END - START).days + 1
    assert len(ratings) == days * len(SLOTS) * len(GENRES)
    assert ratings["audience"].min() > 0
    again = generate_daily_ratings(START, date(2022, 6, 10))
    assert again.equals(generate_daily_ratings(START, date(2022, 6, 10)))
    assert not again.equals(generate_daily_ratings(START, date(2022, 6, 10), seed=1))


def test_yoy_uses_full_12_month_periods(ratings):
    annual = AudienceAnalyzer(ratings).yoy_growth()
    # Jun-2022..May-2025 is exactly three full years, not four partial calendar years
    assert list(annual["year"]) == [1, 2, 3]
    assert annual["label"].iloc[0].startswith("Year 1 (from Jun 2022)")
    # steadily growing input must never show a negative year (the old calendar-year bug)
    assert (annual["yoy_growth_pct"].dropna() > 0).all()


def test_partial_trailing_year_is_dropped():
    r = generate_daily_ratings(date(2022, 1, 1), date(2023, 3, 31))
    annual = AudienceAnalyzer(r).yoy_growth()
    assert list(annual["year"]) == [1]


def test_growth_multiple_controls_trend():
    flat = AudienceAnalyzer(generate_daily_ratings(START, END, growth_multiple=1.0)).yoy_growth()
    assert abs(flat["cumulative_growth_pct"].iloc[-1]) < 3
    # linear 1x -> 3x: period means ~1.33x, 2x, 2.67x -> Year 3 is ~+100% vs Year 1
    steep = AudienceAnalyzer(generate_daily_ratings(START, END, growth_multiple=3.0)).yoy_growth()
    assert 90 < steep["cumulative_growth_pct"].iloc[-1] < 115


def test_prime_time_slots_lead(ratings):
    top = AudienceAnalyzer(ratings).top_slots(2)
    assert set(top["slot"]) == {"18:00", "21:00"}


def test_genre_share_sums_to_100(ratings):
    g = AudienceAnalyzer(ratings).genre_performance()
    assert g["share_pct"].sum() == pytest.approx(100, abs=0.5)


def test_platform_metrics_reach_target_peak():
    p = generate_platform_metrics(START, END, start_viewers=25_000, peak_viewers=50_000)
    monthly = p.groupby("month")["monthly_viewers"].sum()
    assert len(monthly) == 36
    assert 45_000 <= monthly.iloc[-1] <= 55_000
    assert 22_000 <= monthly.iloc[0] <= 28_000


def test_roi_tables():
    content = generate_content_roi(n=50)
    ra = ROIAnalyzer(content)
    top = ra.top_roi_titles(5)
    assert len(top) == 5 and top["cost_per_viewer"].is_monotonic_increasing
    summary = ra.genre_roi_summary()
    assert summary["title_count"].sum() == 50
    assert summary["avg_cost_per_viewer"].is_monotonic_increasing


def test_rejects_bad_dates():
    with pytest.raises(ValueError):
        generate_daily_ratings(END, START)
