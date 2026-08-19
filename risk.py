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
        
