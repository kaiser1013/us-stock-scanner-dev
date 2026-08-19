from ta.volatility import AverageTrueRange

# =======================
# Portfolio Settings
# =======================

ACCOUNT_SIZE = 10000

RISK_PER_TRADE = 0.01

ATR_STOP_MULTIPLIER = 1.5

TP1_MULTIPLIER = 2.0

TP2_MULTIPLIER = 3.0

def create_trade_plan(score, rr_ratio):

    if score >= 80 and rr_ratio >= 2:
    
        return "✅ ACTIONABLE"
        
    elif score >= 70 and rr_ratio >= 1.5:
        
        return "👀 WATCH"
        
    else:

        return "❌ SKIP"
        
def calculate_position_size(
    account_size,
    risk_percent,
    risk_per_share
):

    risk_amount = account_size * risk_percent
    
    if risk per_share <= 0:
        
        return 0, 0
        
    shares = int(
        risk_amount / risk_per_share
    )
    
    capital_required = (
        shares * risk_per_share
    )
    
    return shares, capital_required

def calculate_risk(
    df,
    metrics,
    score
):

    atr_indicator = AverageTrueRange(
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        window=14
    )
    
    atr = float(
        atr_indicator.average_true_range().iloc[-1]
