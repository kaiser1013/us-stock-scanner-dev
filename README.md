| Version     | 內容                             |    優先 |
| ----------- | ------------------------------ | ----: |
| v2.0 Stable | 現有 Scanner                     |     ✅ |
| v2.1        | Scoring Ranking System         | ⭐⭐⭐⭐⭐ |
| v2.2        | Market Regime Filter           | ⭐⭐⭐⭐⭐ |
| v2.3        | Relative Strength Filter       |  ⭐⭐⭐⭐ |
| v2.4        | Advanced Volume Analysis       |  ⭐⭐⭐⭐ |
| v2.5        | Chart Pattern Detection        |   ⭐⭐⭐ |
| v2.6        | Backtesting Engine             | ⭐⭐⭐⭐⭐ |
| v3.0        | TradingView + Python 全自動交易決策平台 | ⭐⭐⭐⭐⭐ |

Stable

Version 2.0
2026-06-10
Features:
MA20
MA50
RSI
Volume
Breakout
Market Filter

--------------

Dev

Version 2.1 Score Engine

v2.1.1：加入 ADX（Trend Strength）+DI > -DI 代表強勢上升趨勢

v2.1.2：Top Picks Ranking System

  ✅ 修正 ma200
  ✅ 修正 strength_score / rs_score bug
  ✅ 修正 plus_di / minus_di
  ✅ 加 upper_band
  ✅ 移除 ADX import 位置問題（假設已在檔案最上面import）
  ✅ 保留你原本 scoring 架構
  ✅ 不破壞你現有 dev workflow
  保留現有 Hard Filters；
  修正 high/low 未定義嘅 ADX bug；
  所有通過 Hard Filter 嘅股票都計 Score（唔再 score < 60: return None）；
  results 按 Score 排序；
  自動產生：
  📧 Email：Top 10（簡潔版）；
  📄 CSV：Top 20（完整技術數據）；
  Email 附上一句 summary
