# PolyTail backtest report (overall)
Run 2026-11-19 02:40 UTC. Training window 150 days, test window 90 days.
Wallet pool 313, usable 142, bot-like skipped 133, selected by training score 27.
**Hedgers removed:** 8 wallets put more than 25% of their money into games where they held both sides. They're left out of the scored, sharp and proven lists and the live watchlist, and every wallet is judged on one-sided bets only.

**Verdict:** ✅ Edge found: whole pool wallets, N=5, min $5,000 → +31.2% per bet over 72 settled bets (90% range +10.9% to +53.3%).

Bets placed at the price 15 min after the signal where price history was available (87452 of 87754 rows; the rest use the wallet's own fill price +1¢, which is optimistic), minus Polymarket's taker fee (4% x (1 - price), about 2.0% of a 50¢ bet). The bid/ask spread is NOT included, so real results would be roughly 1-2% per bet worse.
Profit-scored wallets did NOT beat the whole pool (N=3, $1K).
**Sharp wallets (closing-line value):** 6 wallets beat the closing price consistently in training (20+ bets, avg 1¢+, t≥2). Too few sharp signals to judge (need 30+ settled). Whole pool best: +31.2%/bet. Following sharps did NOT clearly beat the pool.
**Proven winners (profitable AND beat the close):** 5 wallets. Too few signals to judge (need 30+ settled). Did NOT clearly beat the pool.

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| proven (profit+CLV) | 1 | 1,000 | 762 | 678 | 55% | 54¢ | +1.0% | -5.8% to +7.3% | $653 |
| proven (profit+CLV) | 1 | 5,000 | 596 | 546 | 56% | 54¢ | +4.5% | -2.9% to +12.6% | $2K |
| proven (profit+CLV) | 2 | 1,000 | 12 | 11 | 55% | 57¢ | -20.6% | -59.7% to +18.6% | -$226 |
| proven (profit+CLV) | 2 | 5,000 | 8 | 7 | 86% | 72¢ | +22.6% | -14.4% to +54.4% | $158 |
| proven (profit+CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 1 | 1,000 | 2188 | 2065 | 56% | 53¢ | +3.7% | -0.1% to +7.6% | $8K |
| sharp (CLV) | 1 | 5,000 | 1013 | 957 | 58% | 55¢ | +3.9% | -1.4% to +9.3% | $4K |
| sharp (CLV) | 2 | 1,000 | 27 | 26 | 62% | 51¢ | +11.7% | -20.5% to +41.3% | $304 |
| sharp (CLV) | 2 | 5,000 | 20 | 19 | 74% | 54¢ | +33.8% | +0.7% to +68.1% | $642 |
| sharp (CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 1 | 1,000 | 3157 | 2720 | 56% | 54¢ | +5.0% | +1.2% to +8.8% | $14K |
| scored | 1 | 5,000 | 2023 | 1858 | 56% | 54¢ | +4.6% | +0.6% to +8.7% | $9K |
| scored | 2 | 1,000 | 122 | 110 | 59% | 51¢ | +13.2% | -2.7% to +29.6% | $1K |
| scored | 2 | 5,000 | 87 | 78 | 59% | 51¢ | +16.6% | -4.7% to +37.1% | $1K |
| scored | 3 | 1,000 | 7 | 6 | 67% | 59¢ | +13.6% | -46.2% to +80.5% | $82 |
| scored | 3 | 5,000 | 6 | 4 | 50% | 60¢ | -29.6% | n/a to n/a | -$118 |
| scored | 4 | 1,000 | 1 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| one-sided pool | 1 | 1,000 | 18289 | 15369 | 54% | 53¢ | +0.5% | -1.0% to +2.0% | $7K |
| one-sided pool | 1 | 5,000 | 11558 | 9651 | 55% | 53¢ | +0.8% | -1.0% to +2.7% | $8K |
| one-sided pool | 2 | 1,000 | 3287 | 2754 | 56% | 54¢ | +0.9% | -2.7% to +4.4% | $3K |
| one-sided pool | 2 | 5,000 | 2093 | 1779 | 56% | 54¢ | +2.1% | -2.0% to +6.1% | $4K |
| one-sided pool | 3 | 1,000 | 878 | 721 | 59% | 54¢ | +7.5% | +0.9% to +14.4% | $5K |
| one-sided pool | 3 | 5,000 | 556 | 473 | 60% | 55¢ | +7.0% | -0.6% to +15.1% | $3K |
| one-sided pool | 4 | 1,000 | 298 | 242 | 62% | 57¢ | +10.0% | -2.0% to +22.5% | $2K |
| one-sided pool | 4 | 5,000 | 178 | 143 | 66% | 58¢ | +19.6% | +3.8% to +34.9% | $3K |
| one-sided pool | 5 | 1,000 | 122 | 98 | 72% | 62¢ | +16.3% | +1.3% to +31.9% | $2K |
| one-sided pool | 5 | 5,000 | 73 | 53 | 79% | 63¢ | +26.7% | +7.8% to +46.1% | $1K |
| whole pool | 1 | 1,000 | 19483 | 16414 | 54% | 53¢ | +0.2% | -1.3% to +1.7% | $4K |
| whole pool | 1 | 5,000 | 12257 | 10279 | 54% | 53¢ | +0.7% | -1.1% to +2.6% | $7K |
| whole pool | 2 | 1,000 | 3705 | 3107 | 55% | 53¢ | +1.2% | -2.1% to +4.5% | $4K |
| whole pool | 2 | 5,000 | 2355 | 2009 | 56% | 54¢ | +0.8% | -3.0% to +4.6% | $2K |
| whole pool | 3 | 1,000 | 1061 | 878 | 58% | 55¢ | +5.9% | -0.1% to +11.8% | $5K |
| whole pool | 3 | 5,000 | 676 | 581 | 57% | 55¢ | +1.7% | -5.5% to +8.6% | $1K |
| whole pool | 4 | 1,000 | 378 | 311 | 59% | 56¢ | +3.3% | -6.6% to +13.0% | $1K |
| whole pool | 4 | 5,000 | 231 | 189 | 60% | 57¢ | +6.2% | -6.2% to +18.8% | $1K |
| whole pool | 5 | 1,000 | 152 | 124 | 65% | 58¢ | +9.9% | -5.2% to +25.9% | $1K |
| whole pool | 5 | 5,000 | 95 | 72 | 78% | 61¢ | +31.2% | +10.9% to +53.3% | $2K |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| under 30¢ | 7 | +56.1% |
| 30–60¢ | 24 | +43.4% |
| 60¢+ | 41 | +19.8% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 29580 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
