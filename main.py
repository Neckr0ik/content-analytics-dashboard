"""
Content Analytics Dashboard

    python main.py                                  # 3 years of synthetic data -> 6 charts in output/
    python main.py --start 2023-01-01 --end 2025-12-31 --growth 2.0 --seed 7
    python main.py --no-charts --csv                # summary + CSV exports only

All data is synthetic (seeded RNG); see src/data_generator.py for the assumptions.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from datetime import date

from src.analyzer import AudienceAnalyzer, ROIAnalyzer
from src.data_generator import generate_content_roi, generate_daily_ratings, generate_platform_metrics


def _positive(kind):
    def check(value: str):
        try:
            v = kind(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{value!r} is not a valid number")
        if v <= 0:
            raise argparse.ArgumentTypeError(f"must be greater than 0 (got {value})")
        return v
    return check


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Broadcast/OTT content analytics on synthetic data")
    p.add_argument("--start", type=date.fromisoformat, default=date(2022, 6, 1), help="YYYY-MM-DD")
    p.add_argument("--end", type=date.fromisoformat, default=date(2025, 5, 31), help="YYYY-MM-DD")
    p.add_argument("--growth", type=_positive(float), default=3.0,
                   help="daily audience level at --end as a multiple of --start (default 3.0)")
    p.add_argument("--peak-viewers", type=_positive(int), default=50_000,
                   help="total monthly platform viewers in the last month (default 50,000)")
    p.add_argument("--titles", type=_positive(int), default=80,
                   help="number of titles in the ROI table (at least 1)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="output")
    p.add_argument("--csv", action="store_true", help="also export the generated data as CSV")
    p.add_argument("--no-charts", action="store_true")
    args = p.parse_args(argv)
    if args.end <= args.start:
        p.error(f"--end ({args.end}) must be after --start ({args.start})")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    print("Content Analytics Dashboard  (synthetic data)")
    print("=" * 50)

    print("\n[1/3] Generating synthetic audience data...")
    ratings = generate_daily_ratings(args.start, args.end, growth_multiple=args.growth, seed=args.seed)
    platforms = generate_platform_metrics(args.start, args.end, peak_viewers=args.peak_viewers,
                                          start_viewers=args.peak_viewers // 2, seed=args.seed)
    content = generate_content_roi(n=args.titles, seed=args.seed)

    print("[2/3] Running analysis...")
    aa = AudienceAnalyzer(ratings)
    ra = ROIAnalyzer(content)
    annual = aa.yoy_growth()
    top_slots = aa.top_slots()
    genre_roi = ra.genre_roi_summary()

    if args.csv:
        os.makedirs(args.out, exist_ok=True)
        for name, df in [("daily_ratings", ratings), ("platform_metrics", platforms), ("content_roi", content)]:
            df.to_csv(os.path.join(args.out, f"{name}.csv"), index=False)
        print(f"  CSV exports -> {args.out}/")

    if not args.no_charts:
        print("\n[3/3] Generating charts...")
        from src import visualizer as viz  # matplotlib only when needed
        if not annual.empty:
            viz.plot_growth(annual, args.out)
        viz.plot_monthly_trend(aa.monthly_trend(), args.out)
        viz.plot_genre_performance(aa.genre_performance(), args.out)
        viz.plot_scheduling_heatmap(aa.scheduling_heatmap_data(), args.out)
        viz.plot_roi(ra.top_roi_titles(), genre_roi, args.out)
        viz.plot_platform_breakdown(platforms, args.out)

    print("\n" + "=" * 50)
    print("KEY FINDINGS (synthetic data)")
    print("=" * 50)
    if annual.empty:
        print("  Fewer than 12 months of data: no full-year comparison.")
    for _, row in annual.iterrows():
        yoy = row["yoy_growth_pct"]
        growth = "baseline" if math.isnan(yoy) else f"{yoy:+.1f}%"
        cum = "baseline" if row["year"] == 1 else f"{row['cumulative_growth_pct']:+.0f}%"
        print(f"  {row['label']:<26} Total audience: {row['total_audience']:>13,.0f}  "
              f"YoY: {growth:>8}  vs. Year 1: {cum}")

    print("\nTop performing time slots:")
    for _, r in top_slots.iterrows():
        print(f"  {r['slot']}  ->  avg {r['avg_audience']:,.0f} viewers")

    best = genre_roi.iloc[0]
    print(f"\nMost cost-efficient genre: {best['genre']}  (${best['avg_cost_per_viewer']:.4f} per episode view)")

    peak = platforms.groupby("month")["monthly_viewers"].sum().max()
    print(f"\nPeak monthly viewers across platforms: {peak:,.0f}")
    print(f"\nOutputs saved to {args.out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
