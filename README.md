# Content Analytics Dashboard

**Business problem:** A broadcast network producing 10 hours of daily live TV needs to know which genres, time slots, and content acquisitions are actually driving audience growth — and which are burning budget for minimal return.

This project simulates three years of audience data for a regional broadcast + OTT operation and produces a full analytics dashboard: growth trends, scheduling optimization, platform breakdown, and content ROI.

> Inspired by real audience analytics work at a Mexican broadcast network, where data-informed programming decisions drove 300% audience growth over three years, verified by independent INRA ratings.

---

## What it does

| Output | Insight |
|---|---|
| `01_audience_growth.png` | Year-over-year and cumulative growth curve |
| `02_monthly_trend.png` | 36-month audience trend with seasonal patterns |
| `03_genre_performance.png` | Audience share and average viewers by genre |
| `04_scheduling_heatmap.png` | Optimal time slots per genre (scheduling matrix) |
| `05_content_roi.png` | Cost-per-viewer ranking across 80 titles and genres |
| `06_platform_breakdown.png` | Monthly viewer growth by platform (Linear, iOS, Android, CTV, Web) |

---

## Quick start

```bash
git clone https://github.com/Neckr0ik/content-analytics-dashboard.git
cd content-analytics-dashboard
pip install -r requirements.txt
python main.py
```

Charts are saved to `output/`. Runtime: ~10 seconds.

---

## Project structure

```
content-analytics-dashboard/
├── main.py                  # Entry point — orchestrates full pipeline
├── src/
│   ├── data_generator.py    # Synthetic audience data (ratings, app metrics, content ROI)
│   ├── analyzer.py          # AudienceAnalyzer + ROIAnalyzer classes
│   └── visualizer.py        # All chart generation (matplotlib + seaborn)
├── output/                  # Generated charts (git-ignored)
└── requirements.txt
```

---

## Key design decisions

- **Synthetic data with realistic patterns** — seeded RNG ensures reproducibility; growth curve is calibrated to 3× over 36 months with seasonal variation and prime-time multipliers
- **Separation of concerns** — data generation, analysis logic, and visualization are decoupled so each layer can be swapped independently
- **Business-first output** — every chart answers a real programming or acquisition decision, not just a technical exercise

---

## Skills demonstrated

`Python` · `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `Data Modeling` · `Business Analytics` · `Content ROI` · `Audience Segmentation`

---

## License

MIT © 2026 Giovanni Oliveira
