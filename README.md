# US Stock Scanner v2.5.0

## Overview

v2.5.0 is an additive multi-timeframe Relative Strength upgrade built directly on the stable v2.4.1 diagnostics release.

The release deliberately preserves:

- The modular scanner structure
- The completed-session Volume Engine
- The v2.4.1 production filters
- The v2.4.1 Score Engine and score thresholds
- ATR stops, targets and position sizing
- Structured scan outcomes and rejection diagnostics
- Five-sheet Excel reporting
- Diagnostic email reporting
- Bear-market early-exit behaviour

The only production-facing enhancement is additional Relative Strength information for research, diagnostics and future ranking validation.

## File Structure

```text
scanner.py       Scan flow, diagnostics, reporting, ranking and email
download.py      yfinance download, S&P500 universe and market context
indicator.py     Technical indicators, Volume Engine and multi-timeframe RS
filter.py        Existing v2.4.1 production filter rules
score.py         Existing v2.4.1 scoring formula, version-labelled for v2.5
risk.py          Existing ATR stops, targets and position sizing
requirements.txt Runtime dependencies
CHANGELOG.md      Full project history through v2.5.0
UPGRADE_PLAN_V3.md Incremental roadmap from v2.5 to v3.0
```

## v2.5 Relative Strength Expansion

v2.4.1 calculated one 63-session Relative Strength value:

```text
RelativeStrength = Stock 63-session return - benchmark 63-session return
```

v2.5.0 retains that field unchanged and adds:

```text
RS21  = Stock 21-session return  - benchmark 21-session return
RS63  = Stock 63-session return  - benchmark 63-session return
RS126 = Stock 126-session return - benchmark 126-session return
RS252 = Stock 252-session return - benchmark 252-session return
```

`RelativeStrength` remains an alias of `RS63`, so the existing filter and score behaviour remain compatible.

## RSComposite

The release adds an informational composite:

```text
RSComposite = 0.15 * RS21
            + 0.50 * RS63
            + 0.25 * RS126
            + 0.10 * RS252
```

The composite is included in console, Excel, email and market-breadth diagnostics. It does not change production score, filter or ranking logic in v2.5.0. This separation allows the new Alpha factor to be observed before it is promoted into ranking logic.

## Data History Change

The default yfinance history increases from one year to two years. At least 253 observations are required to calculate a complete 252-session return.

Stocks without enough history continue to use the existing `Indicator Failure` structured outcome with reason:

```text
Indicators unavailable or insufficient history
```

## Production Filters

The v2.4.1 rules are unchanged:

- Price at least $20
- Average volume at least 1,000,000 shares
- Price above MA20
- MA20 above MA50
- RSI between 40 and 80
- Completed-session VolumeRatio at least 0.8
- MACD not materially below signal
- 63-session RelativeStrength at least -5

## Score Engine

The v2.4.1 categories and thresholds are unchanged:

- TrendScore
- MomentumScore
- StrengthScore based on 63-session RelativeStrength
- VolumeScore
- MarketScore
- ADXScore
- RiskPenalty

Multi-timeframe RS does not alter Score in v2.5.0.

## Candidate Ranking

The v2.4.1 order remains unchanged:

1. TradePlan
2. Score
3. RiskReward

RSComposite is output for observation but is not yet a ranking tie-breaker.

## Completed-Session Volume Engine

The v2.4.1 logic remains unchanged:

- Before 16:15 New York time, today's daily bar is treated as incomplete and the preceding completed session is used.
- After 16:15 New York time, or when the latest bar is from an earlier date, the latest bar is used.
- Average volume uses the 20 sessions before the selected session.

## Diagnostics

Structured outcomes remain:

- Passed
- Filtered
- Data Failure
- Indicator Failure
- Processing Error

The filter engine still records:

- First rejection reason
- Every failed condition
- Market breadth

v2.5 adds `Non-negative RSComposite` to market breadth while keeping every existing breadth measure.

## Excel Workbook

Every successful bull-market scan creates the same five worksheets:

1. `Top20`
2. `Scan Summary`
3. `First Rejections`
4. `All Failed Conditions`
5. `Market Breadth`

The `Top20` sheet now includes `RS21`, `RS63`, `RS126`, `RS252` and `RSComposite`.

## Environment Variables

### Risk

```text
ACCOUNT_SIZE=10000
RISK_PER_TRADE=0.01
ATR_STOP_MULTIPLIER=1.5
TP1_R_MULTIPLE=1.5
TP2_R_MULTIPLE=2.0
```

### Email

```text
EMAIL_USER
EMAIL_PASSWORD
EMAIL_TO
```

## Installation

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python scanner.py
```

## v2.5 Validation Checklist

Before treating v2.5.0 as the new production baseline, compare it with a recent v2.4.1 run:

- Stocks Scanned should remain close to the loaded universe size.
- Data Failures should remain zero or explainably low.
- Processing Errors should remain zero.
- Indicator Failures may increase for stocks with fewer than 253 observations.
- Passed/Filtered behaviour should match v2.4.1 for stocks with sufficient history.
- Score and TradePlan should match v2.4.1 for the same market data.
- Five Excel sheets must be generated.
- Every Top20 row must contain all five RS fields.
- `RelativeStrength` and `RS63` must be equal.
- Email must include the multi-timeframe RS fields.

## Next Planned Release

v2.6.0 is planned to add a three-state market regime and RegimeScore, but only after v2.5 multi-timeframe RS output has been observed and validated. Production filters and stable diagnostics should continue to be changed only through additive, testable releases.

## Disclaimer

This project is research software and does not constitute financial advice. Market data may contain errors or revisions. Validate outputs independently before making any investment decision.
