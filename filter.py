def liquidity_filter(metrics) :
" If metrics["Price"] < 20: return False, "Price filter" if metrics["Avgvolume"] < 1 000_000: return False, "Volume filter"
return True, "OK"
def trend_filter(metrics):
if metin Forse," price belon
return False.
if metrics["MA20"] ‹ metrics["MA50"]:
return False,
"MAZe below MASe"
return True, "OK"
def momentum filter(metrics):
if metrics["RSI" 1 < 40:
return False, "RSI too weak"
if metrics["RSI] > 80:
return False, "RSI over-extended"
if metrics["VolumeRatio"] < 0.8:
return ralses
"Low volume ratio"
if metrics[ "MACD" ] ‹ metrics["SignalLine"] - 0.1:
return False,
"MACD below signal"
return True. "OK"
def relative strength_ filter metrics) : if metric["RelativeStrength 1 -5:
return False. "Weak Relative Strength"
return True, OK"
def run_filters (ticker, metrics):
- Run scanner filters in clear production order."* filters - 1
liquidity filter, trend_filter-momentum_filter» relative_strength_filter.
for rule in filters:
passed, reason - rule(metrics)
if not passed:
print(f"(ticker): (reason}")
return False, reason
return True, "PASS"