"""Integrated walk-forward validation for US Stock Scanner v3.0.0.

The module coordinates sequential in-sample and out-of-sample evaluation while
keeping production filters, scoring, TradePlan and ranking unchanged. External
replay, portfolio, benchmark and factor engines are injected as callables so
this orchestration layer remains deterministic and independently testable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import pandas as pd
from dateutil.relativedelta import relativedelta

Metrics = Mapping[str, float]
WindowRunner = Callable[["WalkForwardWindow", str], "EvaluationResult"]


@dataclass(frozen=True)
class WalkForwardConfig:
    """Configuration for rolling or expanding walk-forward windows."""

    train_years: int = 3
    test_years: int = 1
    step_years: int = 1
    expanding: bool = False

    def __post_init__(self) -> None:
        if self.train_years <= 0:
            raise ValueError("train_years must be positive")
        if self.test_years <= 0:
            raise ValueError("test_years must be positive")
        if self.step_years <= 0:
            raise ValueError("step_years must be positive")


@dataclass(frozen=True)
class WalkForwardWindow:
    """One chronological train/test split."""

    window_id: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp

    def __post_init__(self) -> None:
        dates = (
            self.train_start,
            self.train_end,
            self.test_start,
            self.test_end,
        )
        if any(pd.isna(value) for value in dates):
            raise ValueError("Window dates must be valid")
        if self.window_id <= 0:
            raise ValueError("window_id must be positive")
        if not self.train_start <= self.train_end < self.test_start <= self.test_end:
            raise ValueError("Window dates must be chronological and non-overlapping")

    def to_dict(self) -> dict[str, Any]:
        return {
            "window_id": self.window_id,
            "train_start": self.train_start.date().isoformat(),
            "train_end": self.train_end.date().isoformat(),
            "test_start": self.test_start.date().isoformat(),
            "test_end": self.test_end.date().isoformat(),
        }


@dataclass(frozen=True)
class EvaluationResult:
    """Metrics and artifacts returned by one train or test evaluation."""

    metrics: Mapping[str, float]
    trade_count: int = 0
    benchmark_metrics: Mapping[str, float] = field(default_factory=dict)
    factor_metrics: Mapping[str, float] = field(default_factory=dict)
    signals: pd.DataFrame = field(default_factory=pd.DataFrame, compare=False)
    equity_curve: pd.Series = field(default_factory=lambda: pd.Series(dtype=float), compare=False)
    trade_log: pd.DataFrame = field(default_factory=pd.DataFrame, compare=False)

    def __post_init__(self) -> None:
        if self.trade_count < 0:
            raise ValueError("trade_count cannot be negative")


@dataclass(frozen=True)
class WalkForwardResult:
    """Integrated train/test result for one walk-forward window."""

    window: WalkForwardWindow
    train: EvaluationResult
    test: EvaluationResult

    @property
    def window_id(self) -> int:
        return self.window.window_id

    def to_dict(self) -> dict[str, Any]:
        row = self.window.to_dict()
        row.update(
            {
                "train_trades": self.train.trade_count,
                "test_trades": self.test.trade_count,
            }
        )
        row.update(_prefixed_metrics("train", self.train.metrics))
        row.update(_prefixed_metrics("test", self.test.metrics))
        row.update(_prefixed_metrics("train_benchmark", self.train.benchmark_metrics))
        row.update(_prefixed_metrics("test_benchmark", self.test.benchmark_metrics))
        return row


@dataclass(frozen=True)
class WalkForwardSummary:
    """Cross-window out-of-sample summary."""

    window_count: int
    profitable_windows: int
    consistency_score: float
    average_test_return: float
    average_test_sharpe: float
    average_test_alpha: float
    best_test_return: float
    worst_test_return: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _timestamp(value: Any) -> pd.Timestamp:
    result = pd.Timestamp(value)
    if pd.isna(result):
        raise ValueError("Date must be valid")
    if result.tzinfo is not None:
        result = result.tz_convert(None)
    return result.normalize()


def generate_windows(
    start_date: Any,
    end_date: Any,
    train_years: int = 3,
    test_years: int = 1,
    step_years: int = 1,
    expanding: bool = False,
) -> list[WalkForwardWindow]:
    """Generate deterministic chronological train/test windows.

    End dates are inclusive. The test period starts on the calendar day after
    the training period, preventing overlap. Only complete test windows are
    returned.
    """
    config = WalkForwardConfig(train_years, test_years, step_years, expanding)
    start = _timestamp(start_date)
    end = _timestamp(end_date)
    if start >= end:
        raise ValueError("start_date must be earlier than end_date")

    windows: list[WalkForwardWindow] = []
    anchor = start
    window_id = 1
    while True:
        train_start = start if config.expanding else anchor
        train_end = anchor + relativedelta(years=config.train_years) - pd.Timedelta(days=1)
        test_start = train_end + pd.Timedelta(days=1)
        test_end = test_start + relativedelta(years=config.test_years) - pd.Timedelta(days=1)
        if test_end > end:
            break
        windows.append(
            WalkForwardWindow(
                window_id=window_id,
                train_start=train_start,
                train_end=train_end,
                test_start=test_start,
                test_end=test_end,
            )
        )
        anchor += relativedelta(years=config.step_years)
        window_id += 1
    return windows


def run_walkforward_window(
    window: WalkForwardWindow,
    evaluator: WindowRunner,
) -> WalkForwardResult:
    """Run injected integration logic for one train/test window."""
    train = evaluator(window, "train")
    test = evaluator(window, "test")
    if not isinstance(train, EvaluationResult) or not isinstance(test, EvaluationResult):
        raise TypeError("evaluator must return EvaluationResult")
    return WalkForwardResult(window=window, train=train, test=test)


def run_walkforward(
    windows: Sequence[WalkForwardWindow],
    evaluator: WindowRunner,
) -> list[WalkForwardResult]:
    """Run all windows in deterministic window-id order."""
    ordered = sorted(windows, key=lambda item: item.window_id)
    identifiers = [window.window_id for window in ordered]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("window_id values must be unique")
    return [run_walkforward_window(window, evaluator) for window in ordered]


def _metric(metrics: Mapping[str, float], *names: str) -> float:
    for name in names:
        if name in metrics:
            return float(metrics[name])
    return 0.0


def build_walkforward_summary(
    results: Sequence[WalkForwardResult],
) -> WalkForwardSummary:
    """Aggregate out-of-sample results across all complete windows."""
    if not results:
        raise ValueError("At least one walk-forward result is required")

    returns = [_metric(result.test.metrics, "total_return", "TotalReturn") for result in results]
    sharpes = [_metric(result.test.metrics, "sharpe_ratio", "SharpeRatio") for result in results]
    alphas = [
        _metric(
            result.test.benchmark_metrics or result.test.metrics,
            "alpha",
            "Alpha",
        )
        for result in results
    ]
    profitable = sum(value > 0 for value in returns)
    count = len(results)
    return WalkForwardSummary(
        window_count=count,
        profitable_windows=profitable,
        consistency_score=profitable / count,
        average_test_return=sum(returns) / count,
        average_test_sharpe=sum(sharpes) / count,
        average_test_alpha=sum(alphas) / count,
        best_test_return=max(returns),
        worst_test_return=min(returns),
    )


def _prefixed_metrics(prefix: str, metrics: Mapping[str, float]) -> dict[str, float]:
    return {f"{prefix}_{key}": float(value) for key, value in metrics.items()}


def results_to_frame(results: Iterable[WalkForwardResult]) -> pd.DataFrame:
    """Convert window results into a flat report table."""
    return pd.DataFrame([result.to_dict() for result in results])


def factor_results_to_frame(results: Iterable[WalkForwardResult]) -> pd.DataFrame:
    """Convert train/test factor metrics into a long report table."""
    rows: list[dict[str, Any]] = []
    for result in results:
        for sample_name, evaluation in (("train", result.train), ("test", result.test)):
            for factor_name, value in evaluation.factor_metrics.items():
                rows.append(
                    {
                        "window_id": result.window_id,
                        "sample": sample_name,
                        "factor": factor_name,
                        "value": float(value),
                    }
                )
    return pd.DataFrame(rows, columns=["window_id", "sample", "factor", "value"])


def build_walkforward_report(
    results: Sequence[WalkForwardResult],
) -> dict[str, pd.DataFrame]:
    """Build stable Summary, Windows, Benchmark and Factor Validation tables."""
    summary = build_walkforward_summary(results)
    windows = results_to_frame(results)
    benchmark_columns = [
        column
        for column in windows.columns
        if column.startswith("train_benchmark_") or column.startswith("test_benchmark_")
    ]
    benchmark = windows[["window_id", *benchmark_columns]].copy()
    return {
        "Summary": pd.DataFrame([summary.to_dict()]),
        "Windows": windows,
        "Benchmark": benchmark,
        "Factor Validation": factor_results_to_frame(results),
    }


def export_walkforward_report(
    report: Mapping[str, pd.DataFrame],
    output_path: str | Path,
) -> Path:
    """Export the walk-forward report to Excel or a directory of CSV files."""
    destination = Path(output_path)
    if destination.suffix.lower() == ".xlsx":
        destination.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(destination, engine="openpyxl") as writer:
            for sheet_name, frame in report.items():
                frame.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        return destination
    if destination.suffix:
        raise ValueError("output_path must be an .xlsx file or a directory")
    destination.mkdir(parents=True, exist_ok=True)
    for name, frame in report.items():
        frame.to_csv(destination / f"{name.lower().replace(' ', '_')}.csv", index=False)
    return destination
