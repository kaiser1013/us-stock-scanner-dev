import pandas as pd

from scanner.replay import (
    HistoricalSignal,
    point_in_time_history,
    generate_signal,
    replay_symbol,
    replay_universe,
)


def make_history():

    dates = pd.date_range(
        "2024-01-01",
        periods=10,
        freq="D",
    )

    return pd.DataFrame(
        {
            "Close": range(
                100,
                110,
            )
        },
        index=dates,
    )


def test_point_in_time_history():
    history = make_history()

    result = point_in_time_history(
        history,
        pd.Timestamp(
            "2024-01-05"
        ),
    )

    assert (
        result.index.max()
        == pd.Timestamp(
            "2024-01-05"
        )
    )


def test_generate_signal():
    history = make_history()

    signal = generate_signal(
        ticker="AAPL",
        history=history,
        signal_date=pd.Timestamp(
            "2024-01-05"
        ),
    )

    assert signal is not None

    assert (
        signal.price
        == 104
    )


def test_generate_signal_returns_none_when_no_history():
    history = make_history()

    signal = generate_signal(
        ticker="AAPL",
        history=history,
        signal_date=pd.Timestamp(
            "2023-01-01"
        ),
    )

    assert signal is None


def test_generate_signal_returns_historical_signal():
    history = make_history()

    signal = generate_signal(
        ticker="AAPL",
        history=history,
        signal_date=pd.Timestamp(
            "2024-01-05"
        ),
    )

    assert isinstance(
        signal,
        HistoricalSignal,
    )


def test_replay_symbol():
    history = make_history()

    result = replay_symbol(
        ticker="AAPL",
        history=history,
        start_date=pd.Timestamp(
            "2024-01-03"
        ),
        end_date=pd.Timestamp(
            "2024-01-05"
        ),
    )

    assert len(result) == 3


def test_replay_universe():
    history = make_history()

    universe = {
        "AAPL": history,
        "MSFT": history,
    }

    result = replay_universe(
        universe,
        start_date=pd.Timestamp(
            "2024-01-03"
        ),
        end_date=pd.Timestamp(
            "2024-01-05"
        ),
    )

    assert len(result) == 6


def test_signal_contains_required_fields():
    history = make_history()

    signal = generate_signal(
        ticker="AAPL",
        history=history,
        signal_date=pd.Timestamp(
            "2024-01-05"
        ),
        market_regime="BULL",
        regime_score=15,
        rs_composite=10,
        breakout55=True,
    )

    assert (
        signal.market_regime
        == "BULL"
    )

    assert (
        signal.regime_score
        == 15
    )

    assert (
        signal.rs_composite
        == 10
    )

    assert (
        signal.breakout55
        is True
    )


def test_future_rows_do_not_change_signal():

    history = make_history()

    signal_date = pd.Timestamp(
        "2024-01-05"
    )

    original = generate_signal(
        ticker="AAPL",
        history=history,
        signal_date=signal_date,
    )

    history.loc[
        pd.Timestamp(
            "2024-12-31"
        ),
        "Close"
    ] = 99999

    replay = generate_signal(
        ticker="AAPL",
        history=history,
        signal_date=signal_date,
    )

    assert (
        original.price
        == replay.price
    )


def test_signal_is_repeatable():

    history = make_history()

    date = pd.Timestamp(
        "2024-01-05"
    )

    first = generate_signal(
        ticker="AAPL",
        history=history,
        signal_date=date,
    )

    second = generate_signal(
        ticker="AAPL",
        history=history,
        signal_date=date,
    )

    assert (
        first.price
        == second.price
    )

    assert (
        first.signal_date
        == second.signal_date
    )