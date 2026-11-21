# PolyTail backtest report (overall)
Run 2026-11-21 08:58 UTC. Training window 150 days, test window 90 days.
Wallet pool 304, usable 136, bot-like skipped 131, selected by training score 25.
**Hedgers removed:** 8 wallets put more than 25% of their money into games where they held both sides. They're left out of the scored, sharp and proven lists and the live watchlist, and every wallet is judged on one-sided bets only.

**Verdict:** ✅ Edge found: one-sided pool wallets, N=5, min $5,000 → +42.9% per bet over 55 settled bets (90% range +20.2% to +69.0%).

Bets placed at the price 15 min after the signal where price history was available (83113 of 83235 rows; the rest use the wallet's own fill price +1¢, which is optimistic), minus Polymarket's taker fee (4% x (1 - price), about 2.0% of a 50¢ bet). The bid/ask spread is NOT included, so real results would be roughly 1-2% per bet worse.
Profit-scored wallets did NOT beat the whole pool (N=3, $1K).
**Sharp wallets (closing-line value):** 4 wallets beat the closing price consistently in training (20+ bets, avg 1¢+, t≥2). Too few sharp signals to judge (need 30+ settled). Whole pool best: +33.8%/bet. Following sharps did NOT clearly beat the pool.
**Proven winners (profitable AND beat the close):** 4 wallets. Too few signals to judge (need 30+ settled). Did NOT clearly beat the pool.

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| proven (profit+CLV) | 1 | 1,000 | 393 | 316 | 61% | 60¢ | +0.0% | -9.3% to +9.6% | $11 |
| proven (profit+CLV) | 1 | 5,000 | 294 | 248 | 62% | 60¢ | +4.9% | -6.0% to +15.6% | $1K |
| proven (profit+CLV) | 2 | 1,000 | 1 | 1 | 0% | 65¢ | -101.4% | n/a to n/a | -$101 |
| proven (profit+CLV) | 2 | 5,000 | 1 | 1 | 100% | 94¢ | +6.7% | n/a to n/a | $7 |
| proven (profit+CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 1 | 1,000 | 393 | 316 | 61% | 60¢ | +0.0% | -9.3% to +9.6% | $11 |
| sharp (CLV) | 1 | 5,000 | 294 | 248 | 62% | 60¢ | +4.9% | -6.0% to +15.6% | $1K |
| sharp (CLV) | 2 | 1,000 | 1 | 1 | 0% | 65¢ | -101.4% | n/a to n/a | -$101 |
| sharp (CLV) | 2 | 5,000 | 1 | 1 | 100% | 94¢ | +6.7% | n/a to n/a | $7 |
| sharp (CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 1 | 1,000 | 2459 | 2301 | 54% | 52¢ | +4.4% | +0.3% to +8.4% | $10K |
| scored | 1 | 5,000 | 1771 | 1702 | 54% | 53¢ | +3.4% | -0.9% to +7.8% | $6K |
| scored | 2 | 1,000 | 111 | 104 | 57% | 52¢ | +6.4% | -10.0% to +22.5% | $664 |
| scored | 2 | 5,000 | 79 | 73 | 56% | 51¢ | +9.7% | -10.8% to +30.5% | $705 |
| scored | 3 | 1,000 | 5 | 5 | 60% | 55¢ | +11.2% | -68.3% to +90.6% | $56 |
| scored | 3 | 5,000 | 5 | 4 | 50% | 60¢ | -29.6% | n/a to n/a | -$118 |
| scored | 4 | 1,000 | 1 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| one-sided pool | 1 | 1,000 | 18064 | 15422 | 54% | 53¢ | +0.7% | -0.8% to +2.3% | $12K |
| one-sided pool | 1 | 5,000 | 11611 | 9805 | 55% | 53¢ | +1.1% | -0.7% to +3.0% | $11K |
| one-sided pool | 2 | 1,000 | 3200 | 2787 | 55% | 53¢ | +0.8% | -2.7% to +4.3% | $2K |
| one-sided pool | 2 | 5,000 | 2112 | 1831 | 56% | 54¢ | +0.9% | -3.0% to +4.8% | $2K |
| one-sided pool | 3 | 1,000 | 870 | 729 | 59% | 54¢ | +8.0% | +1.8% to +14.6% | $6K |
| one-sided pool | 3 | 5,000 | 576 | 490 | 60% | 55¢ | +5.5% | -2.0% to +13.1% | $3K |
| one-sided pool | 4 | 1,000 | 285 | 240 | 62% | 56¢ | +9.6% | -1.8% to +21.2% | $2K |
| one-sided pool | 4 | 5,000 | 182 | 146 | 67% | 57¢ | +22.8% | +7.9% to +37.9% | $3K |
| one-sided pool | 5 | 1,000 | 99 | 77 | 83% | 64¢ | +34.7% | +18.1% to +51.2% | $3K |
| one-sided pool | 5 | 5,000 | 71 | 55 | 84% | 64¢ | +42.9% | +20.2% to +69.0% | $2K |
| whole pool | 1 | 1,000 | 19399 | 16590 | 54% | 53¢ | +0.6% | -0.9% to +2.1% | $10K |
| whole pool | 1 | 5,000 | 12298 | 10436 | 54% | 53¢ | +1.0% | -0.9% to +2.8% | $10K |
| whole pool | 2 | 1,000 | 3679 | 3176 | 55% | 53¢ | +0.9% | -2.0% to +4.2% | $3K |
| whole pool | 2 | 5,000 | 2400 | 2074 | 55% | 54¢ | -0.1% | -3.8% to +3.6% | -$252 |
| whole pool | 3 | 1,000 | 1052 | 890 | 58% | 54¢ | +8.0% | +1.9% to +14.0% | $7K |
| whole pool | 3 | 5,000 | 705 | 607 | 58% | 55¢ | +2.0% | -4.8% to +8.7% | $1K |
| whole pool | 4 | 1,000 | 360 | 302 | 59% | 55¢ | +3.0% | -6.5% to +12.4% | $900 |
| whole pool | 4 | 5,000 | 234 | 194 | 63% | 57¢ | +11.0% | -1.8% to +24.0% | $2K |
| whole pool | 5 | 1,000 | 137 | 115 | 70% | 59¢ | +17.8% | +2.5% to +34.3% | $2K |
| whole pool | 5 | 5,000 | 92 | 75 | 81% | 64¢ | +33.8% | +15.3% to +53.1% | $3K |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| under 30¢ | 3 | +268.6% |
| 30–60¢ | 21 | +51.9% |
| 60¢+ | 31 | +14.9% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 1041 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
