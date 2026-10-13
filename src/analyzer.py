"""Core analytics: growth metrics, slot performance, genre rankings, ROI."""
import pandas as pd

class AudienceAnalyzer:
    def __init__(self, ratings: pd.DataFrame):
        self.df = ratings.copy()
        dates = pd.to_datetime(self.df["date"])
        self.df["month"] = dates.dt.to_period("M")
        # Year 1, Year 2, ... counted from the first date (12-month periods), so a
        # window like Jun-2022..May-2025 is three full years instead of four partial
        # calendar years (which made the last partial year look like a collapse).
        start = dates.min()
        months = (dates.dt.year - start.year) * 12 + (dates.dt.month - start.month)
        months -= (dates.dt.day < start.day).astype(int)
        self.df["period_year"] = months // 12 + 1
        self.start = start

    def yoy_growth(self) -> pd.DataFrame:
        """Totals per 12-month period from the start date. Incomplete trailing periods are dropped."""
        grp = self.df.groupby("period_year")
        annual = grp["audience"].sum().reset_index(name="total_audience")
        annual["days"] = grp["date"].nunique().values
        annual = annual[annual["days"] >= 365].drop(columns="days").reset_index(drop=True)
        annual = annual.rename(columns={"period_year": "year"})
        annual["label"] = [f"Year {y} (from {(self.start + pd.DateOffset(years=y - 1)):%b %Y})"
                           for y in annual["year"]]
        annual["yoy_growth_pct"] = annual["total_audience"].pct_change() * 100
        baseline = annual["total_audience"].iloc[0] if len(annual) else float("nan")
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
