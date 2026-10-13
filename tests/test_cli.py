import main


def test_full_run_with_charts_and_csv(tmp_path):
    out = tmp_path / "out"
    assert main.main(["--start", "2023-01-01", "--end", "2024-12-31", "--csv", "--out", str(out)]) == 0
    for i, name in enumerate(["audience_growth", "monthly_trend", "genre_performance",
                              "scheduling_heatmap", "content_roi", "platform_breakdown"], 1):
        assert (out / f"{i:02d}_{name}.png").exists()
    assert (out / "daily_ratings.csv").exists()


def test_short_window_no_charts(tmp_path, capsys):
    assert main.main(["--start", "2024-01-01", "--end", "2024-06-30", "--no-charts", "--out", str(tmp_path)]) == 0
    assert "Fewer than 12 months" in capsys.readouterr().out
