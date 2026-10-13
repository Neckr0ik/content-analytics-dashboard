"""Generates all dashboard visualizations (PNG files in the output directory)."""
import os

import matplotlib
matplotlib.use("Agg")  # headless: works in CI and over SSH
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="darkgrid", palette="muted")
NAVY = "#1F3864"
OUT = "output"


def _save(name: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  saved -> {path}")
    return path

def plot_growth(annual: pd.DataFrame, out_dir: str = OUT) -> str:
    fig, ax1 = plt.subplots(figsize=(8, 4))
    x = [f"Year {y}" for y in annual["year"]]
    ax1.bar(x, annual["total_audience"] / 1e6,
            color=NAVY, alpha=0.75, label="Total Audience (M)")
    ax1.set_ylabel("Total Annual Audience (millions)")
    ax2 = ax1.twinx()
    ax2.plot(x, annual["cumulative_growth_pct"],
             color="#E87722", marker="o", linewidth=2.5, label="Cumulative Growth %")
    ax2.set_ylabel("Cumulative Growth (%)")
    final = annual["cumulative_growth_pct"].iloc[-1]
    ax1.set_title(f"Audience Growth Over {len(annual)} Years — {final:+.0f}% vs. Year 1 (synthetic data)",
                  fontweight="bold")
    lines = ax1.lines + ax2.lines
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left")
    return _save("01_audience_growth.png", out_dir)

def plot_monthly_trend(monthly: pd.DataFrame, out_dir: str = OUT) -> str:
    plt.figure(figsize=(12, 4))
    plt.plot(monthly["month"], monthly["monthly_total"] / 1e6,
             color=NAVY, linewidth=2)
    plt.fill_between(monthly["month"], monthly["monthly_total"] / 1e6,
                     alpha=0.15, color=NAVY)
    plt.xticks(monthly["month"][::3], rotation=45, ha="right")
    plt.ylabel("Monthly Audience (millions)")
    plt.title(f"Monthly Audience Trend — {len(monthly)} Months (synthetic data)", fontweight="bold")
    return _save("02_monthly_trend.png", out_dir)

def plot_genre_performance(genre_df: pd.DataFrame, out_dir: str = OUT) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    genre_df_sorted = genre_df.sort_values("avg_audience")
    axes[0].barh(genre_df_sorted["genre"], genre_df_sorted["avg_audience"] / 1e3,
                 color=NAVY, alpha=0.8)
    axes[0].set_xlabel("Avg Audience per Slot (thousands)")
    axes[0].set_title("Average Audience by Genre", fontweight="bold")
    axes[1].pie(genre_df["share_pct"], labels=genre_df["genre"],
                autopct="%1.1f%%", startangle=140,
                colors=sns.color_palette("muted", len(genre_df)))
    axes[1].set_title("Audience Share by Genre", fontweight="bold")
    return _save("03_genre_performance.png", out_dir)

def plot_scheduling_heatmap(heatmap_df: pd.DataFrame, out_dir: str = OUT) -> str:
    pivot = heatmap_df.pivot(index="slot", columns="genre", values="avg_audience")
    plt.figure(figsize=(12, 5))
    sns.heatmap(pivot / 1e3, annot=True, fmt=".0f", cmap="Blues",
                linewidths=0.5, cbar_kws={"label": "Avg Audience (thousands)"})
    plt.title("Scheduling Heatmap: Audience by Time Slot × Genre", fontweight="bold")
    plt.ylabel("Time Slot")
    return _save("04_scheduling_heatmap.png", out_dir)

def plot_roi(roi_df: pd.DataFrame, genre_roi: pd.DataFrame, out_dir: str = OUT) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    top = roi_df.head(10)
    axes[0].barh(top["title_id"], top["cost_per_viewer"],
                 color="#2E8B57", alpha=0.85)
    axes[0].set_xlabel("Cost per Episode View (USD)")
    axes[0].set_title("Top 10 Titles by Cost Efficiency", fontweight="bold")
    genre_roi_s = genre_roi.sort_values("avg_cost_per_viewer")
    axes[1].barh(genre_roi_s["genre"], genre_roi_s["avg_cost_per_viewer"],
                 color=NAVY, alpha=0.8)
    axes[1].set_xlabel("Avg Cost per Episode View (USD)")
    axes[1].set_title("Content ROI by Genre", fontweight="bold")
    return _save("05_content_roi.png", out_dir)

def plot_platform_breakdown(app_df: pd.DataFrame, out_dir: str = OUT) -> str:
    monthly_pivot = app_df.pivot_table(
        index="month", columns="channel", values="monthly_viewers", aggfunc="sum")
    monthly_pivot.plot(kind="area", stacked=True, figsize=(12, 5),
                       colormap="tab10", alpha=0.75)
    plt.ylabel("Monthly Viewers")
    peak = monthly_pivot.sum(axis=1).max()
    plt.title(f"Monthly Viewers by Platform — peak {peak:,.0f} (synthetic data)", fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    plt.legend(loc="upper left", fontsize=8)
    return _save("06_platform_breakdown.png", out_dir)
