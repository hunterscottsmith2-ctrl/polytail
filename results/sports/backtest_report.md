# PolyTail backtest report (sports)
Run 2026-11-28 10:01 UTC. Training window 150 days, test window 90 days.
Wallet pool 288, usable 145, bot-like skipped 118, selected by training score 41.
**Hedgers removed:** 8 wallets put more than 25% of their money into games where they held both sides. They're left out of the scored, sharp and proven lists and the live watchlist, and every wallet is judged on one-sided bets only.

**Verdict:** ✅ Edge found: whole pool wallets, N=4, min $1,000 → +9.8% per bet over 331 settled bets (90% range +0.3% to +19.1%).

Bets placed at the price 15 min after the signal where price history was available (62705 of 62705 rows; the rest use the wallet's own fill price +1¢, which is optimistic), minus Polymarket's taker fee (3% x (1 - price), about 1.5% of a 50¢ bet). The bid/ask spread is NOT included, so real results would be roughly 1-2% per bet worse.
Profit-scored wallets did NOT beat the whole pool (N=3, $1K).
**Sharp wallets (closing-line value):** 5 wallets beat the closing price consistently in training (20+ bets, avg 1¢+, t≥2). Too few sharp signals to judge (need 30+ settled). Whole pool best: +12.3%/bet. Following sharps did NOT clearly beat the pool.
**Proven winners (profitable AND beat the close):** 4 wallets. Too few signals to judge (need 30+ settled). Did NOT clearly beat the pool.

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| proven (profit+CLV) | 1 | 1,000 | 528 | 528 | 50% | 52¢ | -4.0% | -12.0% to +4.4% | -$2K |
| proven (profit+CLV) | 1 | 5,000 | 112 | 112 | 48% | 53¢ | -8.1% | -24.7% to +10.5% | -$906 |
| proven (profit+CLV) | 2 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 2 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 1 | 1,000 | 528 | 528 | 50% | 52¢ | -4.0% | -12.0% to +4.4% | -$2K |
| sharp (CLV) | 1 | 5,000 | 112 | 112 | 48% | 53¢ | -8.1% | -24.7% to +10.5% | -$906 |
| sharp (CLV) | 2 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 2 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 1 | 1,000 | 3348 | 3323 | 53% | 52¢ | +2.6% | -0.4% to +5.7% | $9K |
| scored | 1 | 5,000 | 1785 | 1781 | 54% | 52¢ | +3.3% | -0.7% to +7.1% | $6K |
| scored | 2 | 1,000 | 163 | 163 | 51% | 50¢ | -1.5% | -14.5% to +11.8% | -$244 |
| scored | 2 | 5,000 | 95 | 95 | 52% | 51¢ | +0.5% | -16.2% to +16.9% | $46 |
| scored | 3 | 1,000 | 8 | 8 | 75% | 49¢ | +50.3% | -1.1% to +100.8% | $402 |
| scored | 3 | 5,000 | 4 | 4 | 50% | 48¢ | +0.5% | n/a to n/a | $2 |
| scored | 4 | 1,000 | 1 | 1 | 0% | 57¢ | -101.3% | n/a to n/a | -$101 |
| scored | 4 | 5,000 | 1 | 1 | 0% | 57¢ | -101.3% | n/a to n/a | -$101 |
| scored | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| one-sided pool | 1 | 1,000 | 13464 | 13021 | 53% | 52¢ | +0.4% | -1.1% to +2.0% | $6K |
| one-sided pool | 1 | 5,000 | 7452 | 7128 | 54% | 52¢ | +0.8% | -1.2% to +2.8% | $5K |
| one-sided pool | 2 | 1,000 | 3005 | 2989 | 54% | 52¢ | +3.5% | +0.5% to +6.7% | $10K |
| one-sided pool | 2 | 5,000 | 1376 | 1368 | 55% | 53¢ | +2.6% | -1.7% to +7.1% | $4K |
| one-sided pool | 3 | 1,000 | 875 | 874 | 52% | 51¢ | -0.3% | -6.1% to +5.5% | -$271 |
| one-sided pool | 3 | 5,000 | 373 | 373 | 57% | 53¢ | +5.5% | -2.6% to +13.8% | $2K |
| one-sided pool | 4 | 1,000 | 276 | 276 | 55% | 51¢ | +6.8% | -3.7% to +16.9% | $2K |
| one-sided pool | 4 | 5,000 | 106 | 106 | 58% | 52¢ | +8.1% | -7.6% to +24.6% | $864 |
| one-sided pool | 5 | 1,000 | 73 | 73 | 55% | 52¢ | +3.7% | -16.2% to +23.4% | $271 |
| one-sided pool | 5 | 5,000 | 27 | 27 | 67% | 51¢ | +25.6% | -3.5% to +54.3% | $691 |
| whole pool | 1 | 1,000 | 14334 | 13891 | 53% | 52¢ | +0.3% | -1.2% to +1.8% | $4K |
| whole pool | 1 | 5,000 | 7879 | 7555 | 53% | 52¢ | +0.5% | -1.4% to +2.6% | $4K |
| whole pool | 2 | 1,000 | 3234 | 3218 | 53% | 52¢ | +3.2% | +0.2% to +6.4% | $10K |
| whole pool | 2 | 5,000 | 1502 | 1494 | 54% | 53¢ | +0.6% | -3.8% to +5.2% | $824 |
| whole pool | 3 | 1,000 | 994 | 993 | 52% | 51¢ | -0.4% | -5.8% to +5.1% | -$351 |
| whole pool | 3 | 5,000 | 444 | 444 | 56% | 52¢ | +6.5% | -1.4% to +14.4% | $3K |
| whole pool | 4 | 1,000 | 331 | 331 | 56% | 51¢ | +9.8% | +0.3% to +19.1% | $3K |
| whole pool | 4 | 5,000 | 131 | 131 | 57% | 52¢ | +8.4% | -6.5% to +22.8% | $1K |
| whole pool | 5 | 1,000 | 100 | 100 | 55% | 51¢ | +9.5% | -8.4% to +27.4% | $947 |
| whole pool | 5 | 5,000 | 44 | 44 | 57% | 49¢ | +12.3% | -14.0% to +37.6% | $543 |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| under 30¢ | 8 | +42.0% |
| 30–60¢ | 260 | +9.1% |
| 60¢+ | 63 | +8.6% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 3750 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
