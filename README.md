# Content Analytics Dashboard

> **Resumen:** Simula tres años de datos de audiencia de una operación regional de TV abierta + OTT y genera un tablero: crecimiento anual, tendencia mensual, desempeño por género, mapa de programación por horario, costo por vista de contenidos y mezcla de plataformas. Todos los datos son sintéticos (generador con semilla); sirve para demostrar el método de análisis, no reporta audiencias reales.

*Part of Giovanni Oliveira's Hybrid Intelligence portfolio — see https://github.com/Neckr0ik*

**Business problem:** a broadcast network that produces hours of daily live TV wants to know which genres, time slots and content acquisitions drive audience growth, and which cost a lot for little return.

The project generates **synthetic** audience data for a regional broadcast + OTT operation and runs the analysis a programming team would use: growth by year, scheduling heatmap, platform mix and content cost efficiency.

> Inspired by audience analytics work at a Mexican broadcast network. No real ratings or audience data are included.

---

## What it does

| Output | Insight |
|---|---|
| `01_audience_growth.png` | Total audience per 12-month period, with growth vs. Year 1 |
| `02_monthly_trend.png` | Monthly audience trend with seasonality |
| `03_genre_performance.png` | Average audience by genre, and each genre's share of channel audience |
| `04_scheduling_heatmap.png` | Average audience by time slot × genre |
| `05_content_roi.png` | Cost per episode view: the 10 most efficient titles, and cost per episode view by genre |
| `06_platform_breakdown.png` | Monthly viewers by platform (Linear TV, iOS, Android, CTV, Web) |

Run with the defaults (`python main.py`), the console summary shows:

```
  Year 1 (from Jun 2022)     Total audience:   629,562,607  YoY: baseline  vs. Year 1: baseline
  Year 2 (from Jun 2023)     Total audience:   951,242,545  YoY:   +51.1%  vs. Year 1: +51%
  Year 3 (from Jun 2024)     Total audience: 1,271,699,339  YoY:   +33.7%  vs. Year 1: +102%
```

These figures are synthetic and follow from the generator's assumptions. The daily audience level rises linearly from 1× to 3× over the window (`--growth 3.0`), so Year 3's total ends up about twice Year 1's.

---

## Synthetic data model

`src/data_generator.py` (seeded with `numpy.random.default_rng`, default seed 42):

- **Daily ratings:** 7 time slots × 7 genres per day. The audience is a random base (8k–40k) × a linear growth factor × ±15% annual seasonality × a 1.4 prime-time multiplier (18:00, 21:00) × ±15% noise. `rating_pct` uses a hypothetical universe of 1.2M households.
- **Platform metrics:** total monthly viewers grow linearly from `peak/2` to `--peak-viewers` (default 50,000). Fixed shares: Linear TV 45%, iOS 20%, Android 18%, CTV 12%, Web 5%.
- **Content ROI:** 80 titles with random acquisition cost, episodes and audience per episode. `total_audience` sums the episode audiences, so `cost_per_viewer` is a **cost per episode view**, not a cost per unique viewer.

Growth is reported per **12-month period counted from the start date**: Year *k* runs from `start + (k−1) years` to the day before `start + k years` (calendar years via `pandas.DateOffset`, so leap years are handled). A period counts only if the data reaches its last day; incomplete trailing periods are dropped. (Earlier versions grouped by calendar year, so a June–May window produced partial years and a misleading −56% "drop" in the final year.)

---

## Install, run, test

```bash
git clone https://github.com/Neckr0ik/content-analytics-dashboard.git
cd content-analytics-dashboard
pip install -r requirements.txt

python main.py                                   # defaults: Jun 2022 – May 2025
python main.py --start 2023-01-01 --end 2025-12-31 --growth 2.0 --seed 7
python main.py --peak-viewers 80000 --titles 120
python main.py --no-charts --csv                 # export the generated data as CSV

pytest -q                                        # offline test suite
```

Python 3.11+. CI runs the tests on Python 3.11 and 3.12 (`.github/workflows/tests.yml`).

## Project structure

```
content-analytics-dashboard/
├── main.py                  # CLI: generate -> analyze -> charts / CSV / summary
├── src/
│   ├── data_generator.py    # synthetic ratings, platform metrics, content ROI
│   ├── analyzer.py          # AudienceAnalyzer (12-month periods, slots, genres) + ROIAnalyzer
│   └── visualizer.py        # matplotlib/seaborn charts
└── tests/
```

## Limitations

- **All data is synthetic.** Trends, rankings and "best genre" results come from the generator's random draws and assumptions. They say nothing about any real channel. To analyse real data, load your own data into the `AudienceAnalyzer`/`ROIAnalyzer` DataFrames (same column names).
- **Genre and slot effects are mostly noise.** Apart from the prime-time multiplier, the generator gives no genre or slot a built-in advantage, so differences between genres are random.
- **There is no causal analysis.** The dashboard describes patterns and does not estimate what caused growth.
- **Cost efficiency ignores** licence length, ad revenue and unique reach.

## License

MIT © 2026 Giovanni Oliveira
