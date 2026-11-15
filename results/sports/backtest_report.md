# PolyTail backtest report (sports)
Run 2026-11-15 00:35 UTC. Training window 150 days, test window 90 days.
Wallet pool 293, usable 154, bot-like skipped 115, selected by training score 42.

**Verdict:** ✅ Edge found: whole pool wallets, N=4, min $5,000 → +16.1% per bet over 218 settled bets (90% range +5.8% to +26.4%).

Bets placed at the price 15 min after the signal, minus a 1% fee. A random bet at market price averages about -1% after that fee, so that's the bar to beat.
Profit-scored wallets did NOT beat the whole pool (N=3, $1K).
**Sharp wallets (closing-line value):** 9 wallets beat the closing price consistently in training (20+ bets, avg 1¢+, t≥2). Best sharp setting: N=2, $5,000 → +4.3%/bet over 66 bets. Whole pool best: +16.1%/bet. Following sharps did NOT clearly beat the pool.
**Proven winners (profitable AND beat the close):** 5 wallets. Too few signals to judge (need 30+ settled). Did NOT clearly beat the pool.

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| proven (profit+CLV) | 1 | 1,000 | 463 | 463 | 50% | 52¢ | -1.9% | -10.9% to +7.2% | -$878 |
| proven (profit+CLV) | 1 | 5,000 | 115 | 115 | 48% | 52¢ | -4.8% | -21.2% to +13.9% | -$555 |
| proven (profit+CLV) | 2 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 2 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 1 | 1,000 | 3879 | 3845 | 52% | 52¢ | +0.6% | -2.1% to +3.4% | $2K |
| sharp (CLV) | 1 | 5,000 | 903 | 899 | 57% | 54¢ | +4.1% | -1.4% to +9.7% | $4K |
| sharp (CLV) | 2 | 1,000 | 415 | 415 | 52% | 51¢ | +1.0% | -7.1% to +9.2% | $425 |
| sharp (CLV) | 2 | 5,000 | 66 | 66 | 59% | 56¢ | +4.3% | -15.0% to +23.1% | $284 |
| sharp (CLV) | 3 | 1,000 | 13 | 13 | 54% | 46¢ | +14.9% | -37.0% to +67.7% | $193 |
| sharp (CLV) | 3 | 5,000 | 1 | 1 | 0% | 30¢ | -101.0% | n/a to n/a | -$101 |
| sharp (CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 1 | 1,000 | 3239 | 3229 | 52% | 51¢ | +0.4% | -2.6% to +3.4% | $1K |
| scored | 1 | 5,000 | 2224 | 2223 | 52% | 51¢ | +0.5% | -3.2% to +4.1% | $1K |
| scored | 2 | 1,000 | 309 | 309 | 50% | 50¢ | +0.2% | -11.0% to +10.5% | $60 |
| scored | 2 | 5,000 | 202 | 202 | 50% | 51¢ | -2.8% | -14.7% to +9.5% | -$559 |
| scored | 3 | 1,000 | 39 | 39 | 49% | 53¢ | -10.6% | -36.1% to +14.6% | -$414 |
| scored | 3 | 5,000 | 22 | 22 | 50% | 51¢ | -2.2% | -38.0% to +34.2% | -$49 |
| scored | 4 | 1,000 | 1 | 1 | 100% | 50¢ | +97.0% | n/a to n/a | $97 |
| scored | 4 | 5,000 | 1 | 1 | 100% | 50¢ | +97.0% | n/a to n/a | $97 |
| scored | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| whole pool | 1 | 1,000 | 13786 | 13308 | 53% | 52¢ | +0.4% | -1.1% to +1.9% | $5K |
| whole pool | 1 | 5,000 | 7810 | 7532 | 53% | 52¢ | +0.5% | -1.5% to +2.5% | $4K |
| whole pool | 2 | 1,000 | 3589 | 3532 | 53% | 52¢ | +1.6% | -1.2% to +4.4% | $6K |
| whole pool | 2 | 5,000 | 1694 | 1676 | 55% | 53¢ | +2.2% | -1.6% to +6.1% | $4K |
| whole pool | 3 | 1,000 | 1316 | 1302 | 55% | 52¢ | +4.7% | +0.1% to +9.5% | $6K |
| whole pool | 3 | 5,000 | 563 | 561 | 57% | 53¢ | +7.9% | +0.8% to +14.8% | $4K |
| whole pool | 4 | 1,000 | 577 | 571 | 56% | 52¢ | +5.5% | -1.3% to +12.3% | $3K |
| whole pool | 4 | 5,000 | 220 | 218 | 62% | 53¢ | +16.1% | +5.8% to +26.4% | $4K |
| whole pool | 5 | 1,000 | 257 | 256 | 55% | 52¢ | +3.2% | -7.1% to +13.5% | $809 |
| whole pool | 5 | 5,000 | 91 | 90 | 53% | 53¢ | -2.5% | -19.7% to +13.2% | -$229 |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| under 30¢ | 4 | -101.0% |
| 30–60¢ | 167 | +15.2% |
| 60¢+ | 47 | +29.1% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 4000 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
