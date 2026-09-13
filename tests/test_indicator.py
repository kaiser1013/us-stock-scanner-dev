from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from scanner.indicator as indicator


SPY_RETURNS = {
    21: 2.0,
    63: 5.0,
    126: 8.0,
    252: 12.0,
}


def create_ohlcv_dataframe(
    periods=320,
    start_price=100.0,
    daily_change=0.25,
    base_volume=1_000_000,
):
    """Create deterministic OHLCV data for indicator tests."""

    dates = pd.date_range(
        "2024-01-02",
        periods=periods,
        freq="B",
    )

    close = np.array(
        [
            start_price + daily_change * index
            for index in range(periods)
        ],
        dtype=float,
    )

    open_price = close - 0.25
    high = close + 1.0
    low = close - 1.0

    volume = np.array(
        [
            base_volume + index * 1_000
            for index in range(periods)
        ],
        dtype=float,
    )

    return pd.DataFrame(
        {
            "Open": open_price,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": volume,
        },
        index=dates,
    )


def create_flat_dataframe(
    periods=320,
    price=100.0,
    volume=1_000_000,
):
    """Create flat OHLCV data for boundary-condition tests."""

    dates = pd.date_range(
        "2024-01-02",
        periods=periods,
        freq="B",
    )

    return pd.DataFrame(
        {
            "Open": [price] * periods,
            "High": [price] * periods,
            "Low": [price] * periods,
            "Close": [price] * periods,
            "Volume": [volume] * periods,
        },
        index=dates,
        dtype=float,
    )


def create_declining_dataframe(
    periods=320,
    start_price=300.0,
    daily_change=0.30,
    base_volume=1_000_000,
):
    """Create deterministic declining OHLCV data."""

    dates = pd.date_range(
        "2024-01-02",
        periods=periods,
        freq="B",
    )

    close = np.array(
        [
            start_price - daily_change * index
            for index in range(periods)
        ],
        dtype=float,
    )

    volume = np.array(
        [
            base_volume + index * 1_000
            for index in range(periods)
        ],
        dtype=float,
    )

    return pd.DataFrame(
        {
            "Open": close + 0.25,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": volume,
        },
        index=dates,
    )


def call_calculate_indicators(
    dataframe,
    spy_returns=None,
):
    """
    Call calculate_indicators using the v2.5.x interface.

    This helper keeps test calls consistent and makes any future
    signature adjustment easier.
    """

    benchmark_returns = (
        SPY_RETURNS
        if spy_returns is None
        else spy_returns
    )

    return indicator.calculate_indicators(
        dataframe,
        benchmark_returns,
    )


# ============================================================
# select_completed_volume_index tests
# ============================================================


def test_before_cutoff_selects_previous_session():
    dataframe = create_ohlcv_dataframe(periods=10)

    current_time = datetime(
        2026,
        9,
        10,
        15,
        30,
        tzinfo=ZoneInfo("America/New_York"),
    )

    selected_index, source = (
        indicator.select_completed_volume_index(
            dataframe,
            current_time,
        )
    )

    assert selected_index == -2
    assert isinstance(source, str)
    assert source


def test_after_cutoff_selects_latest_session():
    dataframe = create_ohlcv_dataframe(periods=10)

    current_time = datetime(
        2026,
        9,
        10,
        16,
        30,
        tzinfo=ZoneInfo("America/New_York"),
    )

    selected_index, source = (
        indicator.select_completed_volume_index(
            dataframe,
            current_time,
        )
    )

    assert selected_index == -1
    assert isinstance(source, str)
    assert source


def test_volume_index_returns_correct_types():
    dataframe = create_ohlcv_dataframe(periods=10)

    current_time = datetime(
        2026,
        9,
        10,
        17,
        0,
        tzinfo=ZoneInfo("America/New_York"),
    )

    selected_index, source = (
        indicator.select_completed_volume_index(
            dataframe,
            current_time,
        )
    )

    assert isinstance(selected_index, int)
    assert isinstance(source, str)


# ============================================================
# Relative Strength tests
# ============================================================


def test_relative_strength_metrics_returns_required_fields():
    dataframe = create_ohlcv_dataframe()

    result = indicator.calculate_relative_strength_metrics(
        dataframe["Close"],
        SPY_RETURNS,
    )

    expected_fields = {
        "RS21",
        "RS63",
        "RS126",
        "RS252",
        "RSComposite",
        "RelativeStrength",
    }

    assert expected_fields.issubset(result)


def test_relative_strength_values_are_numeric():
    dataframe = create_ohlcv_dataframe()

    result = indicator.calculate_relative_strength_metrics(
        dataframe["Close"],
        SPY_RETURNS,
    )

    for field in (
        "RS21",
        "RS63",
        "RS126",
        "RS252",
        "RSComposite",
        "RelativeStrength",
    ):
        assert isinstance(
            result[field],
            (int, float, np.integer, np.floating),
        )
        assert np.isfinite(result[field])


def test_relative_strength_alias_equals_rs63():
    dataframe = create_ohlcv_dataframe()

    result = indicator.calculate_relative_strength_metrics(
        dataframe["Close"],
        SPY_RETURNS,
    )

    assert result["RelativeStrength"] == pytest.approx(
        result["RS63"]
    )


def test_rs_composite_uses_expected_weights():
    dataframe = create_ohlcv_dataframe()

    result = indicator.calculate_relative_strength_metrics(
        dataframe["Close"],
        SPY_RETURNS,
    )

    expected_composite = (
        result["RS21"] * 0.10
        + result["RS63"] * 0.40
        + result["RS126"] * 0.30
        + result["RS252"] * 0.20
    )

    assert result["RSComposite"] == pytest.approx(
        expected_composite,
        rel=1e-6,
    )


def test_stronger_stock_produces_positive_relative_strength():
    dataframe = create_ohlcv_dataframe(
        daily_change=0.50,
    )

    neutral_spy_returns = {
        21: 0.0,
        63: 0.0,
        126: 0.0,
        252: 0.0,
    }

    result = indicator.calculate_relative_strength_metrics(
        dataframe["Close"],
        neutral_spy_returns,
    )

    assert result["RS21"] > 0
    assert result["RS63"] > 0
    assert result["RS126"] > 0
    assert result["RS252"] > 0
    assert result["RSComposite"] > 0


def test_declining_stock_produces_negative_relative_strength():
    dataframe = create_declining_dataframe()

    result = indicator.calculate_relative_strength_metrics(
        dataframe["Close"],
        SPY_RETURNS,
    )

    assert result["RS21"] < 0
    assert result["RS63"] < 0
    assert result["RS126"] < 0
    assert result["RS252"] < 0
    assert result["RSComposite"] < 0


def test_relative_strength_requires_sufficient_history():
    dataframe = create_ohlcv_dataframe(periods=100)

    with pytest.raises(
        (ValueError, IndexError),
    ):
        indicator.calculate_relative_strength_metrics(
            dataframe["Close"],
            SPY_RETURNS,
        )


# ============================================================
# calculate_indicators basic tests
# ============================================================


def test_calculate_indicators_returns_dictionary():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert isinstance(result, dict)


def test_calculate_indicators_returns_required_fields():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    expected_fields = {
        "Price",
        "MA20",
        "MA50",
        "MA200",
        "RSI",
        "MACD",
        "SignalLine",
        "MiddleBB",
        "UpperBB",
        "ADX",
        "PlusDI",
        "MinusDI",
        "LastVolume",
        "AvgVolume",
        "VolumeRatio",
        "RelativeVolumeLatest",
        "RelativeVolumePrevious",
        "VolumeSource",
        "RS21",
        "RS63",
        "RS126",
        "RS252",
        "RSComposite",
        "RelativeStrength",
    }

    assert expected_fields.issubset(result)


def test_indicator_output_values_are_finite():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    numeric_fields = (
        "Price",
        "MA20",
        "MA50",
        "MA200",
        "RSI",
        "MACD",
        "SignalLine",
        "MiddleBB",
        "UpperBB",
        "ADX",
        "PlusDI",
        "MinusDI",
        "LastVolume",
        "AvgVolume",
        "VolumeRatio",
        "RelativeVolumeLatest",
        "RelativeVolumePrevious",
        "RS21",
        "RS63",
        "RS126",
        "RS252",
        "RSComposite",
        "RelativeStrength",
    )

    for field in numeric_fields:
        assert field in result
        assert isinstance(
            result[field],
            (int, float, np.integer, np.floating),
        )
        assert np.isfinite(result[field])


def test_price_equals_latest_close():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert result["Price"] == pytest.approx(
        dataframe["Close"].iloc[-1]
    )


def test_ma20_matches_manual_calculation():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    expected = dataframe["Close"].rolling(20).mean().iloc[-1]

    assert result["MA20"] == pytest.approx(expected)


def test_ma50_matches_manual_calculation():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    expected = dataframe["Close"].rolling(50).mean().iloc[-1]

    assert result["MA50"] == pytest.approx(expected)


def test_ma200_matches_manual_calculation():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    expected = dataframe["Close"].rolling(200).mean().iloc[-1]

    assert result["MA200"] == pytest.approx(expected)


def test_uptrend_has_ordered_moving_averages():
    dataframe = create_ohlcv_dataframe(
        daily_change=0.50,
    )

    result = call_calculate_indicators(dataframe)

    assert result["Price"] > result["MA20"]
    assert result["MA20"] > result["MA50"]
    assert result["MA50"] > result["MA200"]


def test_downtrend_has_reverse_moving_average_order():
    dataframe = create_declining_dataframe()

    result = call_calculate_indicators(dataframe)

    assert result["Price"] < result["MA20"]
    assert result["MA20"] < result["MA50"]
    assert result["MA50"] < result["MA200"]


# ============================================================
# RSI, MACD, Bollinger Band and ADX tests
# ============================================================


def test_rsi_is_within_valid_range():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert 0 <= result["RSI"] <= 100


def test_macd_and_signal_line_are_numeric():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert isinstance(
        result["MACD"],
        (int, float, np.integer, np.floating),
    )
    assert isinstance(
        result["SignalLine"],
        (int, float, np.integer, np.floating),
    )


def test_bollinger_upper_band_is_not_below_middle_band():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert result["UpperBB"] >= result["MiddleBB"]


def test_bollinger_middle_band_matches_ma20():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert result["MiddleBB"] == pytest.approx(
        result["MA20"],
        rel=1e-6,
    )


def test_adx_is_non_negative():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert result["ADX"] >= 0


def test_directional_indicators_are_non_negative():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert result["PlusDI"] >= 0
    assert result["MinusDI"] >= 0


# ============================================================
# Volume Engine tests
# ============================================================


def test_average_volume_is_positive():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert result["AvgVolume"] > 0


def test_last_volume_is_positive():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert result["LastVolume"] > 0


def test_volume_ratio_matches_last_volume_divided_by_average():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    expected = (
        result["LastVolume"]
        / result["AvgVolume"]
    )

    assert result["VolumeRatio"] == pytest.approx(
        expected,
        rel=1e-6,
    )


def test_constant_volume_produces_ratio_of_one():
    dataframe = create_flat_dataframe(
        volume=1_000_000,
    )

    result = call_calculate_indicators(dataframe)

    assert result["AvgVolume"] == pytest.approx(
        1_000_000
    )
    assert result["LastVolume"] == pytest.approx(
        1_000_000
    )
    assert result["VolumeRatio"] == pytest.approx(
        1.0
    )


def test_latest_volume_spike_increases_relative_volume():
    dataframe = create_ohlcv_dataframe()
    dataframe.loc[dataframe.index[-1], "Volume"] = 5_000_000

    result = call_calculate_indicators(dataframe)

    assert result["RelativeVolumeLatest"] > 1.0


def test_previous_volume_metric_is_non_negative():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert result["RelativeVolumePrevious"] >= 0


def test_volume_source_is_non_empty_string():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert isinstance(result["VolumeSource"], str)
    assert result["VolumeSource"].strip()


# ============================================================
# Input validation and failure tests
# ============================================================


def test_calculate_indicators_rejects_none():
    with pytest.raises(
        (TypeError, ValueError, AttributeError),
    ):
        call_calculate_indicators(None)


def test_calculate_indicators_rejects_empty_dataframe():
    with pytest.raises(
        (TypeError, ValueError, IndexError, KeyError),
    ):
        call_calculate_indicators(pd.DataFrame())


@pytest.mark.parametrize(
    "missing_column",
    [
        "High",
        "Low",
        "Close",
        "Volume",
    ],
)
def test_calculate_indicators_rejects_missing_columns(
    missing_column,
):
    dataframe = create_ohlcv_dataframe()
    dataframe = dataframe.drop(columns=[missing_column])

    with pytest.raises(
        (KeyError, TypeError, ValueError),
    ):
        call_calculate_indicators(dataframe)


def test_calculate_indicators_rejects_insufficient_history():
    dataframe = create_ohlcv_dataframe(periods=50)

    with pytest.raises(
        (ValueError, IndexError),
    ):
        call_calculate_indicators(dataframe)


def test_calculate_indicators_handles_missing_latest_close():
    dataframe = create_ohlcv_dataframe()
    dataframe.loc[dataframe.index[-1], "Close"] = np.nan

    result = call_calculate_indicators(dataframe)

    assert result is None or isinstance(result, dict)


def test_calculate_indicators_handles_missing_latest_volume():
    dataframe = create_ohlcv_dataframe()
    dataframe.loc[dataframe.index[-1], "Volume"] = np.nan

    result = call_calculate_indicators(dataframe)

    assert result is None or isinstance(result, dict)


def test_calculate_indicators_does_not_modify_input_dataframe():
    dataframe = create_ohlcv_dataframe()
    original = dataframe.copy(deep=True)

    call_calculate_indicators(dataframe)

    pd.testing.assert_frame_equal(
        dataframe,
        original,
    )


def test_calculate_indicators_accepts_integer_volume():
    dataframe = create_ohlcv_dataframe()
    dataframe["Volume"] = dataframe["Volume"].astype(int)

    result = call_calculate_indicators(dataframe)

    assert isinstance(result, dict)
    assert result["AvgVolume"] > 0


def test_relative_strength_uses_supplied_spy_returns():
    dataframe = create_ohlcv_dataframe()

    weak_benchmark = {
        21: 0.0,
        63: 0.0,
        126: 0.0,
        252: 0.0,
    }

    strong_benchmark = {
        21: 20.0,
        63: 20.0,
        126: 20.0,
        252: 20.0,
    }

    weak_benchmark_result = call_calculate_indicators(
        dataframe,
        weak_benchmark,
    )
    strong_benchmark_result = call_calculate_indicators(
        dataframe,
        strong_benchmark,
    )

    assert (
        weak_benchmark_result["RSComposite"]
        > strong_benchmark_result["RSComposite"]
    )


def test_relative_strength_alias_preserved_in_full_result():
    dataframe = create_ohlcv_dataframe()

    result = call_calculate_indicators(dataframe)

    assert result["RelativeStrength"] == pytest.approx(
        result["RS63"]
    )
