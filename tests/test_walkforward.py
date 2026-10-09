from pathlib import Path

import pandas as pd
import pytest

from scanner.walkforward import (
    EvaluationResult,
    WalkForwardConfig,
    WalkForwardResult,
    WalkForwardWindow,
    build_walkforward_report,
    build_walkforward_summary,
    export_walkforward_report,
    factor_results_to_frame,
    generate_windows,
    results_to_frame,
    run_walkforward,
    run_walkforward_window,
)


def make_evaluator(calls: list[tuple[int, str]]):
    def evaluator(window: WalkForwardWindow, sample: str) -> EvaluationResult:
        calls.append((window.window_id, sample))
        multiplier = float(window.window_id if sample == "test" else 0.5)
        return EvaluationResult(
            metrics={"total_return": 0.10 * multiplier, "sharpe_ratio": 1.0 * multiplier},
            trade_count=window.window_id,
            benchmark_metrics={"alpha": 0.02 * multiplier, "beta": 1.0},
            factor_metrics={"RSComposite_Positive": 0.03 * multiplier},
        )

    return evaluator


def window(window_id: int = 1) -> WalkForwardWindow:
    return WalkForwardWindow(
        window_id,
        pd.Timestamp("2020-01-01"),
        pd.Timestamp("2022-12-31"),
        pd.Timestamp("2023-01-01"),
        pd.Timestamp("2023-12-31"),
    )


def test_config_rejects_non_positive_values() -> None:
    with pytest.raises(ValueError, match="train_years"):
        WalkForwardConfig(train_years=0)
    with pytest.raises(ValueError, match="test_years"):
        WalkForwardConfig(test_years=0)
    with pytest.raises(ValueError, match="step_years"):
        WalkForwardConfig(step_years=0)


def test_generate_windows_uses_three_year_train_and_one_year_test() -> None:
    windows = generate_windows("2020-01-01", "2025-12-31")
    assert len(windows) == 3
    assert windows[0].train_start == pd.Timestamp("2020-01-01")
    assert windows[0].train_end == pd.Timestamp("2022-12-31")
    assert windows[0].test_start == pd.Timestamp("2023-01-01")
    assert windows[0].test_end == pd.Timestamp("2023-12-31")
    assert windows[1].train_start == pd.Timestamp("2021-01-01")


def test_generate_windows_supports_expanding_training_period() -> None:
    windows = generate_windows("2020-01-01", "2025-12-31", expanding=True)
    assert windows[0].train_start == pd.Timestamp("2020-01-01")
    assert windows[1].train_start == pd.Timestamp("2020-01-01")
    assert windows[1].train_end == pd.Timestamp("2023-12-31")


def test_generate_windows_returns_only_complete_test_periods() -> None:
    windows = generate_windows("2020-01-01", "2023-06-30")
    assert windows == []


def test_generate_windows_rejects_invalid_date_order() -> None:
    with pytest.raises(ValueError, match="start_date"):
        generate_windows("2025-01-01", "2024-01-01")


def test_window_rejects_overlap() -> None:
    with pytest.raises(ValueError, match="chronological"):
        WalkForwardWindow(
            1,
            pd.Timestamp("2020-01-01"),
            pd.Timestamp("2022-12-31"),
            pd.Timestamp("2022-12-31"),
            pd.Timestamp("2023-12-31"),
        )


def test_run_walkforward_window_runs_train_then_test() -> None:
    calls: list[tuple[int, str]] = []
    result = run_walkforward_window(window(), make_evaluator(calls))
    assert calls == [(1, "train"), (1, "test")]
    assert result.train.metrics["total_return"] == pytest.approx(0.05)
    assert result.test.metrics["total_return"] == pytest.approx(0.10)


def test_run_walkforward_window_rejects_invalid_evaluator_result() -> None:
    def bad_evaluator(_window: WalkForwardWindow, _sample: str):
        return {}

    with pytest.raises(TypeError, match="EvaluationResult"):
        run_walkforward_window(window(), bad_evaluator)  # type: ignore[arg-type]


def test_run_walkforward_sorts_windows_deterministically() -> None:
    calls: list[tuple[int, str]] = []
    first = window(1)
    second = WalkForwardWindow(
        2,
        pd.Timestamp("2021-01-01"),
        pd.Timestamp("2023-12-31"),
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-12-31"),
    )
    results = run_walkforward([second, first], make_evaluator(calls))
    assert [result.window_id for result in results] == [1, 2]


def test_run_walkforward_rejects_duplicate_window_ids() -> None:
    with pytest.raises(ValueError, match="unique"):
        run_walkforward([window(), window()], make_evaluator([]))


def test_build_summary_uses_out_of_sample_metrics() -> None:
    evaluator = make_evaluator([])
    results = run_walkforward(generate_windows("2020-01-01", "2024-12-31"), evaluator)
    summary = build_walkforward_summary(results)
    assert summary.window_count == 2
    assert summary.profitable_windows == 2
    assert summary.consistency_score == pytest.approx(1.0)
    assert summary.average_test_return == pytest.approx(0.15)
    assert summary.average_test_sharpe == pytest.approx(1.5)
    assert summary.average_test_alpha == pytest.approx(0.03)


def test_consistency_score_counts_only_positive_windows() -> None:
    base = window()
    results = [
        WalkForwardResult(base, EvaluationResult({}), EvaluationResult({"total_return": 0.1})),
        WalkForwardResult(base, EvaluationResult({}), EvaluationResult({"total_return": -0.1})),
        WalkForwardResult(base, EvaluationResult({}), EvaluationResult({"total_return": 0.0})),
    ]
    assert build_walkforward_summary(results).consistency_score == pytest.approx(1 / 3)


def test_summary_rejects_empty_results() -> None:
    with pytest.raises(ValueError, match="At least one"):
        build_walkforward_summary([])


def test_results_to_frame_flattens_window_metrics() -> None:
    result = run_walkforward_window(window(), make_evaluator([]))
    frame = results_to_frame([result])
    assert frame.loc[0, "window_id"] == 1
    assert frame.loc[0, "test_total_return"] == pytest.approx(0.10)
    assert frame.loc[0, "test_benchmark_alpha"] == pytest.approx(0.02)


def test_factor_results_to_frame_is_long_format() -> None:
    result = run_walkforward_window(window(), make_evaluator([]))
    frame = factor_results_to_frame([result])
    assert frame["sample"].tolist() == ["train", "test"]
    assert set(frame["factor"]) == {"RSComposite_Positive"}


def test_build_report_contains_required_sheets() -> None:
    result = run_walkforward_window(window(), make_evaluator([]))
    report = build_walkforward_report([result])
    assert set(report) == {"Summary", "Windows", "Benchmark", "Factor Validation"}


def test_export_report_to_csv_directory(tmp_path: Path) -> None:
    result = run_walkforward_window(window(), make_evaluator([]))
    destination = export_walkforward_report(
        build_walkforward_report([result]),
        tmp_path / "walkforward_report",
    )
    assert destination.is_dir()
    assert (destination / "summary.csv").exists()
    assert (destination / "factor_validation.csv").exists()


def test_export_report_to_excel(tmp_path: Path) -> None:
    pytest.importorskip("openpyxl")
    result = run_walkforward_window(window(), make_evaluator([]))
    destination = export_walkforward_report(
        build_walkforward_report([result]),
        tmp_path / "walkforward_report.xlsx",
    )
    assert destination.exists()
    workbook = pd.ExcelFile(destination, engine="openpyxl")
    assert set(workbook.sheet_names) == {
        "Summary",
        "Windows",
        "Benchmark",
        "Factor Validation",
    }


def test_export_rejects_unknown_extension(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="xlsx"):
        export_walkforward_report({}, tmp_path / "report.json")
