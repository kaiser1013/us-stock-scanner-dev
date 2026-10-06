from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass(slots=True)
class HistoricalSignal:
    signal_date: pd.Timestamp

    ticker: str

    price: float

    score: float
    signal: str

    trade_plan: str
    risk_reward: float

    market_regime: str
    regime_score: float

    rs21: float
    rs63: float
    rs126: float
    rs252: float
    rs_composite: float

    breakout55: bool
    distance_to_high55: float


def point_in_time_history(
    history: pd.DataFrame,
    signal_date: pd.Timestamp,
) -> pd.DataFrame:

    history = history.copy()
    
    history.index = pd.to_datetime(
        history.index
    )
    
    """
    Return only data available on the signal date.
    Prevents look-ahead bias.
    """

    return history.loc[
        history.index <= signal_date
    ].copy()


def generate_signal(
    *,
    ticker: str,
    history: pd.DataFrame,
    signal_date: pd.Timestamp,
    score: float = 0.0,
    signal: str = "",
    trade_plan: str = "",
    risk_reward: float = 0.0,
    market_regime: str = "",
    regime_score: float = 0.0,
    rs21: float = 0.0,
    rs63: float = 0.0,
    rs126: float = 0.0,
    rs252: float = 0.0,
    rs_composite: float = 0.0,
    breakout55: bool = False,
    distance_to_high55: float = 0.0,
) -> HistoricalSignal | None:

    pit_history = point_in_time_history(
        history,
        signal_date,
    )

    if pit_history.empty:
        return None

    latest_close = float(
        pit_history["Close"].iloc[-1]
    )

    return HistoricalSignal(
        signal_date=signal_date,
        ticker=ticker,
        price=latest_close,
        score=score,
        signal=signal,
        trade_plan=trade_plan,
        risk_reward=risk_reward,
        market_regime=market_regime,
        regime_score=regime_score,
        rs21=rs21,
        rs63=rs63,
        rs126=rs126,
        rs252=rs252,
        rs_composite=rs_composite,
        breakout55=breakout55,
        distance_to_high55=distance_to_high55,
    )


def replay_symbol(
    *,
    ticker: str,
    history: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> list[HistoricalSignal]:
    mask = (
        (history.index >= start_date)
        & (history.index <= end_date)
    )

    dates = history.loc[mask].index

    signals: list[
        HistoricalSignal
    ] = []

    for signal_date in dates:
    
        signal = generate_signal(
            ticker=ticker,
            history=history,
            signal_date=signal_date,
        )

        if signal is not None:
            signals.append(signal)

    return signals


def replay_universe(
    universe_data: dict[str, pd.DataFrame],
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:

    rows: list[dict] = []

    for (
        ticker,
        history,
    ) in universe_data.items():

        signals = replay_symbol(
            ticker=ticker,
            history=history,
            start_date=start_date,
            end_date=end_date,
        )

        for signal in signals:
            rows.append(
                {
                    "SignalDate": signal.signal_date,
                    "Ticker": signal.ticker,
                    "Price": signal.price,
                    "Score": signal.score,
                    "Signal": signal.signal,
                    "TradePlan": signal.trade_plan,
                    "RiskReward": signal.risk_reward,
                    "MarketRegime": signal.market_regime,
                    "RegimeScore": signal.regime_score,
                    "RS21": signal.rs21,
                    "RS63": signal.rs63,
                    "RS126": signal.rs126,
                    "RS252": signal.rs252,
                    "RSComposite": signal.rs_composite,
                    "Breakout55": signal.breakout55,
                    "DistanceToHigh55": signal.distance_to_high55,
                }
            )

    return pd.DataFrame(rows)