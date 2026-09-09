from scanner.score import (
    calculate_score,
)

def create_metrics(**overrides):
    
    metrics = {
        "Price": 100,
        "MA20": 95,
        "MA50": 90,
        "MA200": 80,
        "RSI": 60,
        "MACD": 2,
        "SignalLine": 1,
        "RelativeStrength": 15,
        "VolumeRatio": 1.5,
        "UpperBB": 110,
        "ADX": 28,
        "PlusDI": 30,
        "MinusDI": 20,
    }
        
    metrics.update(overrides)
    
    return metrics
    
def
    test_score_returns_required_fields():
    
    result = calculate_score(
        create_metrics(),
        market_bull=True,
    )
    
    required = [
        "Score",
        "Signal",
        "TrendScore",
        "MomentumScore",
        "StrengthScore",
        "VolumeScore",
        "MarketScore",
        "ADXScore",
        "RiskPenalty",
    ]
    
    for field in required:
        assert field in result
    
def test_bull_market_bonus():

    bullish = calculate_score(
        create_metrics(),
        market_bull=True,
    )
    
    bearish = calculate_score(
        create_metrics(),
        market_bull=False,
    )
    
    assert bullish["Score"] > bearish["Score"]
    
    
    
    