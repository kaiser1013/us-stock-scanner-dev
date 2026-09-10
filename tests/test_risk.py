import pandas as pd

from scanner risk import calculate_risk

def create_price_df():
    
    data = {
        "High": [101 + i for i in range(50)],
        "Low": [99 + i for i in range(50)],
        "Close": [100 + i for i in range(50)],
    }
    
    return pd.DataFrame(data)

def create_metrics(price=150):
    
    return {
        "Price": price,
    }

def test_risk_returns_fields():

    result = calculate_risk(
        create_price_df(),
        create_metrics(),
        score=80,
    )
    
    required = [
        "ATR14",
        "StopLoss",
        "TakeProfit1",
        "TakeProfit2",
        "RiskPerShare",
        "RewardPerShare",
        "RiskReward",
        "PositionShares",
        "CapitalRequired",
        "PlannedRiskAmount",
        "TradePlan",
    ]
    
    for field in required:
        assert field in result
        
def test_stop_loss_below_entry():
    
    result = calculate_risk(
        create_price_df(),
        create_metrics(),
        score=80,
    )
    
    assert (
        result["StopLoss"]
        <
        150
    )
    

        
        