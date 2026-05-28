"""
Content Analytics Dashboard
Run:  python main.py
Outputs six charts to output/ and prints a summary report to stdout.
"""
from datetime import date
from src.data_generator import generate_daily_ratings, generate_app_metrics, generate_content_roi
from src.analyzer import AudienceAnalyzer, ROIAnalyzer
from src.visualizer import (plot_growth, plot_monthly_trend, plot_genre_performance,
                             plot_scheduling_heatmap, plot_roi, plot_platform_breakdown)

def main():
    print("Content Analytics Dashboard")
    print("=" * 50)

    START = date(2022, 6, 1)
    END   = date(2025, 5, 31)

    print("\n[1/3] Generating synthetic audience data...")
    ratings  = generate_daily_ratings(START, END)
    app_data = generate_app_metrics(START, END)
    content  = generate_content_roi(n=80)

    print("[2/3] Running analysis...")
    aa = AudienceAnalyzer(ratings)
    ra = ROIAnalyzer(content)

    annual        = aa.yoy_growth()
    top_slots     = aa.top_slots()
    genre_perf    = aa.genre_performance()
    monthly_trend = aa.monthly_trend()
    heatmap_data  = aa.scheduling_heatmap_data()
    top_roi       = ra.top_roi_titles()
    genre_roi     = ra.genre_roi_summary()

    print("\n[3/3] Generating charts...")
    plot_growth(annual)
    plot_monthly_trend(monthly_trend)
    plot_genre_performance(genre_perf)
    plot_scheduling_heatmap(heatmap_data)
    plot_roi(top_roi, genre_roi)
    plot_platform_breakdown(app_data)

    print("\n" + "=" * 50)
    print("KEY FINDINGS")
    print("=" * 50)
    for _, row in annual.iterrows():
        growth = f"{row['yoy_growth_pct']:+.1f}%" if not __import__('math').isnan(row['yoy_growth_pct']) else "baseline"
        cum    = f"{row['cumulative_growth_pct']:.0f}%" if row['cumulative_growth_pct'] > 0 else "baseline"
        print(f"  {int(row['year'])}  Total Audience: {row['total_audience']:>12,.0f}  YoY: {growth:>8}  Cumulative: {cum}")

    print(f"\nTop performing time slots:")
    for _, r in top_slots.iterrows():
        print(f"  {r['slot']}  ->  avg {r['avg_audience']:,.0f} viewers")

    print(f"\nBest content ROI genre: {genre_roi.iloc[0]['genre']}  "
          f"(${genre_roi.iloc[0]['avg_cost_per_viewer']:.4f}/viewer)")

    peak_app = app_data.groupby("month")["monthly_viewers"].sum().max()
    print(f"\nPeak monthly app viewers: {peak_app:,.0f}")
    print("\nAll charts saved to output/")

if __name__ == "__main__":
    main()
