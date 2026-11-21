# PolyTail backtest report (sports)
Run 2026-11-21 09:31 UTC. Training window 150 days, test window 90 days.
Wallet pool 296, usable 155, bot-like skipped 116, selected by training score 38.
**Hedgers removed:** 8 wallets put more than 25% of their money into games where they held both sides. They're left out of the scored, sharp and proven lists and the live watchlist, and every wallet is judged on one-sided bets only.

**Verdict:** ✅ Edge found: one-sided pool wallets, N=4, min $1,000 → +12.7% per bet over 255 settled bets (90% range +2.4% to +22.5%).

Bets placed at the price 15 min after the signal where price history was available (61386 of 61386 rows; the rest use the wallet's own fill price +1¢, which is optimistic), minus Polymarket's taker fee (3% x (1 - price), about 1.5% of a 50¢ bet). The bid/ask spread is NOT included, so real results would be roughly 1-2% per bet worse.
Profit-scored wallets did NOT beat the whole pool (N=3, $1K).
**Sharp wallets (closing-line value):** 6 wallets beat the closing price consistently in training (20+ bets, avg 1¢+, t≥2). Too few sharp signals to judge (need 30+ settled). Whole pool best: +14.6%/bet. Following sharps did NOT clearly beat the pool.
**Proven winners (profitable AND beat the close):** 6 wallets. Too few signals to judge (need 30+ settled). Did NOT clearly beat the pool.

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| proven (profit+CLV) | 1 | 1,000 | 990 | 981 | 56% | 55¢ | +1.4% | -4.3% to +7.0% | $1K |
| proven (profit+CLV) | 1 | 5,000 | 146 | 145 | 50% | 54¢ | -6.7% | -21.2% to +9.0% | -$966 |
| proven (profit+CLV) | 2 | 1,000 | 4 | 4 | 25% | 49¢ | -46.6% | n/a to n/a | -$186 |
| proven (profit+CLV) | 2 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 1 | 1,000 | 990 | 981 | 56% | 55¢ | +1.4% | -4.3% to +7.0% | $1K |
| sharp (CLV) | 1 | 5,000 | 146 | 145 | 50% | 54¢ | -6.7% | -21.2% to +9.0% | -$966 |
| sharp (CLV) | 2 | 1,000 | 4 | 4 | 25% | 49¢ | -46.6% | n/a to n/a | -$186 |
| sharp (CLV) | 2 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 1 | 1,000 | 2568 | 2553 | 54% | 53¢ | +1.9% | -1.6% to +5.4% | $5K |
| scored | 1 | 5,000 | 1385 | 1381 | 52% | 51¢ | +0.7% | -3.9% to +5.7% | $1K |
| scored | 2 | 1,000 | 114 | 114 | 47% | 51¢ | -10.0% | -25.2% to +6.7% | -$1K |
| scored | 2 | 5,000 | 56 | 56 | 45% | 51¢ | -12.4% | -34.4% to +10.1% | -$695 |
| scored | 3 | 1,000 | 5 | 5 | 40% | 50¢ | -16.3% | -101.4% to +68.8% | -$81 |
| scored | 3 | 5,000 | 2 | 2 | 50% | 52¢ | +1.7% | n/a to n/a | $3 |
| scored | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| one-sided pool | 1 | 1,000 | 12871 | 12506 | 53% | 52¢ | +1.1% | -0.4% to +2.7% | $14K |
| one-sided pool | 1 | 5,000 | 7588 | 7329 | 53% | 52¢ | +0.8% | -1.2% to +2.8% | $6K |
| one-sided pool | 2 | 1,000 | 2904 | 2887 | 53% | 51¢ | +3.1% | -0.1% to +6.4% | $9K |
| one-sided pool | 2 | 5,000 | 1477 | 1470 | 55% | 52¢ | +3.6% | -0.7% to +8.1% | $5K |
| one-sided pool | 3 | 1,000 | 816 | 815 | 55% | 51¢ | +6.0% | +0.1% to +11.9% | $5K |
| one-sided pool | 3 | 5,000 | 392 | 392 | 58% | 52¢ | +8.3% | +0.4% to +16.5% | $3K |
| one-sided pool | 4 | 1,000 | 255 | 255 | 59% | 52¢ | +12.7% | +2.4% to +22.5% | $3K |
| one-sided pool | 4 | 5,000 | 123 | 123 | 61% | 52¢ | +14.1% | -0.2% to +27.6% | $2K |
| one-sided pool | 5 | 1,000 | 84 | 84 | 58% | 53¢ | +9.3% | -9.1% to +27.5% | $783 |
| one-sided pool | 5 | 5,000 | 44 | 44 | 55% | 52¢ | +5.0% | -20.2% to +29.8% | $218 |
| whole pool | 1 | 1,000 | 13696 | 13331 | 53% | 52¢ | +0.9% | -0.5% to +2.4% | $13K |
| whole pool | 1 | 5,000 | 7993 | 7734 | 53% | 52¢ | +0.5% | -1.5% to +2.5% | $4K |
| whole pool | 2 | 1,000 | 3125 | 3108 | 53% | 51¢ | +2.6% | -0.6% to +5.7% | $8K |
| whole pool | 2 | 5,000 | 1606 | 1599 | 54% | 52¢ | +2.9% | -1.4% to +7.2% | $5K |
| whole pool | 3 | 1,000 | 921 | 920 | 55% | 51¢ | +6.4% | +1.0% to +11.9% | $6K |
| whole pool | 3 | 5,000 | 463 | 463 | 56% | 52¢ | +7.0% | -0.2% to +14.5% | $3K |
| whole pool | 4 | 1,000 | 308 | 308 | 57% | 51¢ | +11.5% | +2.3% to +21.0% | $4K |
| whole pool | 4 | 5,000 | 144 | 144 | 59% | 52¢ | +11.0% | -2.5% to +23.9% | $2K |
| whole pool | 5 | 1,000 | 107 | 107 | 60% | 52¢ | +14.6% | -1.4% to +31.0% | $2K |
| whole pool | 5 | 5,000 | 59 | 59 | 54% | 52¢ | +2.4% | -18.7% to +23.1% | $142 |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| under 30¢ | 2 | -102.2% |
| 30–60¢ | 206 | +13.1% |
| 60¢+ | 47 | +15.9% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 2655 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
