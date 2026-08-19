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
    )
    
    current_price = metrics["Price"]
    
    # =======================
    # Stop Loss
    # =======================
    
    stop_loss = (
        current_price -
        atr * ATR_STOP_MULTIPLIER
    )
    
    # =======================
    # Take Profit
    # =======================
    
    tp1 = (
        current_price + 
        atr * TP1_MULTIPLIER
    )
    
    tp2 = (
        current_price +
        atr * TP2_MULTIPLIER
    )
    
    # =======================
    # Risk Reward
    # =======================
    
    risk_per_share = (
        current_price - 
        stop_loss
    )
    
    reward_per_share = (
        tp1 -
        current_price
    )
    
    rr_ratio = (
        reward_per_share /
        risk_per_share
    )

    # =======================
    # Position Size
    # =======================
    
    shares, capital_required = (
        calculate_position_size(
            ACCOUNT_SIZE,
            RISK_PER_TRADE,
            risk_per_share
        )
    )
    
    trade_plan = create_trade_plan(
        score,
        ro_ratio
    )
    
    return {
        
        "ATR14":
        round(atr, 2),
        
        "StopLoss":
        round(stop_loss, 2),
        
        "TakeProfit1":
        round(tp1, 2),
        
        "TakeProfit2":
        round(tp2,2),

        "RiskPerShare":
        round(risk_per_share, 2),
        
        "RewardPerShare":
        round(reward_per_share, 2),
        
        "RiskReward":
        round(rr_ratio, 2),
        
        "PositionShares":
        shares,
        
        "CapitalRequired":
        round(capital_required, 2),
        
        "TradePlan":
        trade_plan
        
    }
        