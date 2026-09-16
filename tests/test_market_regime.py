import pytest

from scanner.download import (
    classify_market_regime,
    REGIME_BULL,
    REGIME_NEUTRAL,
    REGIME_BEAR,
    REGIME_SCORE_BULL,
    REGIME_SCORE_NEUTRAL,
    REGIME_SCORE_BEAR,
)


def test_bull_regime():
    assert classify_market_regime(
        spy_close=105,
        ma200=100,
    ) == REGIME_BULL


def test_neutral_regime():
    assert classify_market_regime(
        spy_close=101,
        ma200=100,
    ) == REGIME_NEUTRAL


def test_bear_regime():
    assert classify_market_regime(
        spy_close=95,
        ma200=100,
    ) == REGIME_BEAR


def test_regime_score_bull():
    assert REGIME_SCORE_BULL == 15


def test_regime_score_neutral():
    assert REGIME_SCORE_NEUTRAL == 7


def test_regime_score_bear():
    assert REGIME_SCORE_BEAR == 0
