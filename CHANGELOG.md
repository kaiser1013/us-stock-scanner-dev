# CHANGELOG

## v2.5.0 Multi-Timeframe Relative Strength

### Added

- Added benchmark returns for 21, 63, 126 and 252 sessions.
- Added stock-versus-benchmark Relative Strength fields:
  - RS21
  - RS63
  - RS126
  - RS252
- Added `RSComposite` using 15% RS21, 50% RS63, 25% RS126 and 10% RS252.
- Added the five v2.5 RS fields to candidate results, console output, Excel and email.
- Added `Non-negative RSComposite` to Market Breadth.
- Added helper functions for period-return and multi-horizon Relative Strength calculation.
- Added a v2.5 validation checklist to README.
- Added `UPGRADE_PLAN_V3.md` with the incremental roadmap to v3.0.

### Changed

- Updated scanner version, email subject and Excel filename to v2.5.0.
- Increased default price-history download from one year to two years.
- Increased minimum indicator history to 253 observations for RS252.
- Expanded market context with `spy_returns`, while preserving the existing `spy_return` 63-session key.
- Updated module documentation to distinguish new research factors from unchanged production logic.

### Preserved

- Preserved all v2.4.1 structured diagnostic outcomes.
- Preserved the five-sheet diagnostic workbook.
- Preserved first-rejection and all-failed-condition reporting.
- Preserved completed-session Volume Engine behaviour and 16:15 New York cutoff.
- Preserved all production filters and their order.
- Preserved the v2.4.1 Score Engine formula and signal thresholds.
- Preserved ranking by TradePlan, Score and RiskReward.
- Preserved ATR stops, targets and position sizing.
- Preserved email attachment and bear-market alert behaviour.

### Compatibility

- `RelativeStrength` remains equal to `RS63`.
- Existing filtering and scoring therefore continue to use the same 63-session Relative Strength concept.
- RSComposite is informational in v2.5.0 and does not change filter, score or ranking outcomes.

### Validation Notes

- Stocks with fewer than 253 observations are reported through the existing Indicator Failure path.
- Compare v2.5.0 against v2.4.1 using the same market snapshot before setting v2.5.0 as the production baseline.

## v2.4.1 Diagnostic Reporting

### Added

- Added structured scan outcomes for Passed, Filtered, Data Failure, Indicator Failure and Processing Error.
- Added first-rejection statistics for the production filter funnel.
- Added all-failed-condition statistics by evaluating every applicable filter.
- Added market-breadth counts for MA, RSI, volume and relative strength conditions.
- Added a five-sheet Excel diagnostic workbook:
  - Top20
  - Scan Summary
  - First Rejections
  - All Failed Conditions
  - Market Breadth
- Added Excel filtering, frozen headers and automatic column widths.
- Added a diagnostic email body with summary, rejection and breadth sections.
- Added an Excel attachment even when zero stocks pass.
- Added console Scan Summary and Top First-Fail Reasons.

### Changed

- Updated scanner version, email subject and Excel filename to v2.4.1.
- Changed scanner outcomes from a simple result-or-None pattern to a structured diagnostic result.
- Preserved the v2.4 candidate ranking order: TradePlan, Score and RiskReward.
- Kept the v2.4 completed-session Volume Engine and Risk Engine logic unchanged.

### Purpose

- Makes `No stocks passed the technical filters` an auditable scanner result.
- Helps distinguish a weak market from overly restrictive filters, incomplete data or processing errors.

## v2.4 Final

### Added

- Added ATR-based risk management, stop loss, take-profit targets and position sizing.
- Added the automatic completed-session Volume Engine.
- Added risk and volume fields to Excel and email output.
- Added TradePlan ranking.

### Fixed

- Fixed partial intraday volume distorting VolumeRatio.
- Fixed capital-required calculation.
- Fixed ranking parameter consistency and Signal spelling.

## v2.3 Modular Stable

### Added

- Split the scanner into download, indicator, filter, score and scanner modules.

## v3.0 Planned

- Enhanced market regime and historical breadth.
- Sector rotation and sector-relative strength.
- Breakout and pocket-pivot detection.
- Portfolio allocation and exposure control.
- Trade journal, outcome tracking and backtesting.
