"""Core analytics: growth metrics, slot performance, genre rankings, ROI."""
import pandas as pd
import numpy as np

class AudienceAnalyzer:
    def __init__(self, ratings: pd.DataFrame):
        self.df = ratings.copy()
        self.df["year"] = pd.to_datetime(self.df["date"]).dt.year
        self.df["month"] = pd.to_datetime(self.df["date"]).dt.to_period("M")

    def yoy_growth(self) -> pd.DataFrame:
        annual = (self.df.groupby("year")["audience"].sum()
                  .reset_index(name="total_audience"))
        annual["yoy_growth_pct"] = annual["total_audience"].pct_change() * 100
        baseline = annual["total_audience"].iloc[0]
        annual["cumulative_growth_pct"] = (annual["total_audience"] / baseline - 1) * 100
        return annual

    def top_slots(self, top_n: int = 3) -> pd.DataFrame:
        return (self.df.groupby("slot")["audience"]
                .mean().reset_index(name="avg_audience")
                .sort_values("avg_audience", ascending=False)
                .head(top_n))

    def genre_performance(self) -> pd.DataFrame:
        g = self.df.groupby("genre").agg(
            avg_audience=("audience", "mean"),
            peak_audience=("audience", "max"),
            total_audience=("audience", "sum"),
        ).reset_index().sort_values("avg_audience", ascending=False)
        g["share_pct"] = (g["total_audience"] / g["total_audience"].sum() * 100).round(1)
        return g

    def monthly_trend(self) -> pd.DataFrame:
        return (self.df.groupby("month")["audience"]
                .sum().reset_index(name="monthly_total")
                .assign(month=lambda x: x["month"].astype(str)))

    def scheduling_heatmap_data(self) -> pd.DataFrame:
        return (self.df.groupby(["slot", "genre"])["audience"]
                .mean().reset_index(name="avg_audience"))

class ROIAnalyzer:
    def __init__(self, content: pd.DataFrame):
        self.df = content.copy()

    def top_roi_titles(self, top_n: int = 10) -> pd.DataFrame:
        return self.df.nsmallest(top_n, "cost_per_viewer")[
            ["title_id", "genre", "acquisition_cost_usd",
             "total_audience", "cost_per_viewer"]
        ]

    def genre_roi_summary(self) -> pd.DataFrame:
        return (self.df.groupby("genre").agg(
            avg_cost_per_viewer=("cost_per_viewer", "mean"),
            avg_total_audience=("total_audience", "mean"),
            title_count=("title_id", "count"),
        ).reset_index().sort_values("avg_cost_per_viewer"))
