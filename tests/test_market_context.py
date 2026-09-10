import pandas as pd

def classify_market(price, ma200):
    """
    Same logic as get_market_context().
    """
    
    return price > ma200
    
def test_bull_market():
    
    result = classify_market(
        price=6000,
        ma200=5500,
    )
    
    assert result is True
    
def test_bear_market():
    
    result = classify_market(
        price=5000,
        ma200=5500,
    )
    
    assert result is False
    
def test_price_equal_ma200():
    
    result = classify_market(
        price=5500,
        ma200=5500,
    )
    
    assert result is False
    
def test_market_context_return_structure():
    
    market = {
        "spy_price": 6000,
        "spy_ma200": 5500,
        "spy_return": 12,
        "spy_returns": {
            21: 2,
            63: 5,
            126: 8,
            252: 12,
        },
        "market_bull": True,
    }
    
    assert "spy price" in market
    assert "spy_ma200" in market
    assert
    "spy_return" in market