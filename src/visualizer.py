"""Generates all dashboard visualizations and saves to output/."""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import os

sns.set_theme(style="darkgrid", palette="muted")
NAVY = "#1F3864"
OUT  = os.path.join(os.path.dirname(__file__), "..", "output")

def _save(name: str):
    os.makedirs(OUT, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  saved -> output/{name}")

def plot_growth(annual: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(annual["year"].astype(str), annual["total_audience"] / 1e6,
            color=NAVY, alpha=0.75, label="Total Audience (M)")
    ax1.set_ylabel("Total Annual Audience (millions)")
    ax2 = ax1.twinx()
    ax2.plot(annual["year"].astype(str), annual["cumulative_growth_pct"],
             color="#E87722", marker="o", linewidth=2.5, label="Cumulative Growth %")
    ax2.set_ylabel("Cumulative Growth (%)")
    ax1.set_title("Audience Growth Over 3 Years — 300% Cumulative", fontweight="bold")
    lines = ax1.lines + ax2.lines
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left")
    _save("01_audience_growth.png")

def plot_monthly_trend(monthly: pd.DataFrame):
    plt.figure(figsize=(12, 4))
    plt.plot(monthly["month"], monthly["monthly_total"] / 1e6,
             color=NAVY, linewidth=2)
    plt.fill_between(monthly["month"], monthly["monthly_total"] / 1e6,
                     alpha=0.15, color=NAVY)
    plt.xticks(monthly["month"][::3], rotation=45, ha="right")
    plt.ylabel("Monthly Audience (millions)")
    plt.title("Monthly Audience Trend — 36 Months", fontweight="bold")
    _save("02_monthly_trend.png")

def plot_genre_performance(genre_df: pd.DataFrame):
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
    _save("03_genre_performance.png")

def plot_scheduling_heatmap(heatmap_df: pd.DataFrame):
    pivot = heatmap_df.pivot(index="slot", columns="genre", values="avg_audience")
    plt.figure(figsize=(12, 5))
    sns.heatmap(pivot / 1e3, annot=True, fmt=".0f", cmap="Blues",
                linewidths=0.5, cbar_kws={"label": "Avg Audience (thousands)"})
    plt.title("Scheduling Heatmap: Audience by Time Slot × Genre", fontweight="bold")
    plt.ylabel("Time Slot")
    _save("04_scheduling_heatmap.png")

def plot_roi(roi_df: pd.DataFrame, genre_roi: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    top = roi_df.head(10)
    axes[0].barh(top["title_id"], top["cost_per_viewer"],
                 color="#2E8B57", alpha=0.85)
    axes[0].set_xlabel("Cost per Viewer (USD)")
    axes[0].set_title("Top 10 Titles by Cost Efficiency", fontweight="bold")
    genre_roi_s = genre_roi.sort_values("avg_cost_per_viewer")
    axes[1].barh(genre_roi_s["genre"], genre_roi_s["avg_cost_per_viewer"],
                 color=NAVY, alpha=0.8)
    axes[1].set_xlabel("Avg Cost per Viewer (USD)")
    axes[1].set_title("Content ROI by Genre", fontweight="bold")
    _save("05_content_roi.png")

def plot_platform_breakdown(app_df: pd.DataFrame):
    monthly_pivot = app_df.pivot_table(
        index="month", columns="channel", values="monthly_viewers", aggfunc="sum")
    monthly_pivot.plot(kind="area", stacked=True, figsize=(12, 5),
                       colormap="tab10", alpha=0.75)
    plt.ylabel("Monthly Viewers")
    plt.title("Monthly Viewers by Platform — Growth to 50,000 MAU", fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    plt.legend(loc="upper left", fontsize=8)
    _save("06_platform_breakdown.png")
