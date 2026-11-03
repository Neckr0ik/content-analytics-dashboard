# CLAUDE.md — content-analytics-dashboard

Portfolio project (Neckr0ik / Giovanni Oliveira, "Hybrid Intelligence" portfolio). Generates **synthetic**, seeded audience data for a regional broadcast TV + OTT operation and produces a dashboard: 12-month-period growth, monthly trend, genre performance, time-slot × genre heatmap, content cost per episode view, platform mix. No real audience data.

## Stack

Python 3.11+, pandas, numpy, matplotlib, seaborn, pytest (`requirements.txt`). No API keys, no network.

## Structure

```
main.py                 # CLI: generate -> analyze -> charts / CSV / console summary
src/data_generator.py   # synthetic daily ratings, platform metrics, content ROI (numpy default_rng, seed 42)
src/analyzer.py         # AudienceAnalyzer (12-month periods, slots, genres) + ROIAnalyzer
src/visualizer.py       # 6 PNG charts (01_audience_growth ... 06_platform_breakdown)
tests/                  # test_pipeline.py, test_cli.py
```

## Commands

```bash
pip install -r requirements.txt
python main.py                                   # defaults: 2022-06-01 .. 2025-05-31, charts in output/
python main.py --start 2023-01-01 --end 2025-12-31 --growth 2.0 --seed 7
python main.py --peak-viewers 80000 --titles 120
python main.py --no-charts --csv                 # export generated data as CSV
python main.py --help                            # also: --out DIR (default output)
pytest -q                                        # 19 tests, offline
```

## Gotchas

- Growth is per **12-month period from the start date** (`pandas.DateOffset`), not calendar year; incomplete trailing periods are dropped. Calendar-year grouping caused a fake −56% "drop" earlier — don't reintroduce it.
- `cost_per_viewer` is cost per **episode view**, not per unique viewer.
- Apart from the 1.4× prime-time multiplier (18:00, 21:00), genre/slot differences are random noise by design.
- `--growth`, `--peak-viewers`, `--titles` are validated as positive; keep CLI validation when adding flags.
- The console figures quoted in the README come from the default seed; if you change the generator, re-run and update them.

## Conventions (shared across the owner's portfolio repos)

- Plain Python 3.11+ CLI: `main.py` (argparse) at the root, logic in `src/`, tests in `tests/`. No package build, no lint/format config.
- `pytest.ini` sets `testpaths = tests` and `pythonpath = .`, so run `pytest` from the repo root.
- CI (`.github/workflows/tests.yml`): `pip install -r requirements.txt` + `pytest -q` on Python 3.11 and 3.12, on every push and PR. Tests must stay offline (no network, no API keys).
- Generated files go to `output/` (gitignored). Never commit them.
- README is English with a Spanish `> **Resumen:**` blurb at the top; it documents formulas and limitations precisely. When you change behaviour, update the README in the same change (tests often pin the documented formulas).
- Be honest about scope: the README's "Limitations" section is part of the product. Don't add claims the code doesn't support.

## Memoria persistente (Graphiti MCP)
Este proyecto usa el connector **Graphiti** (memoria en grafo compartida entre sesiones).
- `group_id` de este repo: `content-analytics-dashboard`. Datos del usuario y transversales: `neckr0ik-global`.
- Al empezar una tarea: busca contexto con `search_memory_facts` y `search_nodes` usando `group_ids: ["content-analytics-dashboard", "neckr0ik-global"]`.
- Al terminar algo relevante (decisión de arquitectura, convención nueva, bug resuelto y su causa, preferencia del usuario, estado de un despliegue): guárdalo con `add_memory` (`group_id: "content-analytics-dashboard"`, `source: "text"`) con un nombre descriptivo.
- Nunca guardes secretos, API keys, tokens, contraseñas ni datos personales sensibles.
- Si Graphiti no está disponible en la sesión, continúa normalmente.
