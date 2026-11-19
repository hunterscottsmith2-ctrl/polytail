# PolyTail backtest report (sports)
Run 2026-11-19 02:17 UTC. Training window 150 days, test window 90 days.
Wallet pool 297, usable 154, bot-like skipped 119, selected by training score 38.
**Hedgers removed:** 6 wallets put more than 25% of their money into games where they held both sides. They're left out of the scored, sharp and proven lists and the live watchlist, and every wallet is judged on one-sided bets only.

**Verdict:** ✅ Edge found: one-sided pool wallets, N=4, min $1,000 → +12.5% per bet over 235 settled bets (90% range +2.1% to +23.3%).

Bets placed at the price 15 min after the signal where price history was available (60341 of 60341 rows; the rest use the wallet's own fill price +1¢, which is optimistic), minus Polymarket's taker fee (3% x (1 - price), about 1.5% of a 50¢ bet). The bid/ask spread is NOT included, so real results would be roughly 1-2% per bet worse.
Profit-scored wallets did NOT beat the whole pool (N=3, $1K).
**Sharp wallets (closing-line value):** 8 wallets beat the closing price consistently in training (20+ bets, avg 1¢+, t≥2). Best sharp setting: N=2, $1,000 → +7.8%/bet over 50 bets. Whole pool best: +12.9%/bet. Following sharps did NOT clearly beat the pool.
**Proven winners (profitable AND beat the close):** 5 wallets. Too few signals to judge (need 30+ settled). Did NOT clearly beat the pool.

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| proven (profit+CLV) | 1 | 1,000 | 787 | 787 | 51% | 51¢ | -0.4% | -7.0% to +6.1% | -$282 |
| proven (profit+CLV) | 1 | 5,000 | 388 | 388 | 51% | 50¢ | +2.7% | -6.4% to +11.8% | $1K |
| proven (profit+CLV) | 2 | 1,000 | 16 | 16 | 38% | 49¢ | -30.6% | -67.6% to +8.5% | -$489 |
| proven (profit+CLV) | 2 | 5,000 | 5 | 5 | 20% | 53¢ | -55.4% | -101.4% to +36.3% | -$277 |
| proven (profit+CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 1 | 1,000 | 2184 | 2153 | 54% | 52¢ | +2.8% | -1.0% to +6.7% | $6K |
| sharp (CLV) | 1 | 5,000 | 835 | 831 | 56% | 54¢ | +2.7% | -3.2% to +8.6% | $2K |
| sharp (CLV) | 2 | 1,000 | 50 | 50 | 54% | 48¢ | +7.8% | -16.2% to +33.8% | $392 |
| sharp (CLV) | 2 | 5,000 | 22 | 22 | 45% | 49¢ | -6.7% | -43.9% to +30.9% | -$147 |
| sharp (CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 1 | 1,000 | 2414 | 2405 | 54% | 53¢ | +3.0% | -0.6% to +6.6% | $7K |
| scored | 1 | 5,000 | 1325 | 1324 | 53% | 51¢ | +3.1% | -1.7% to +7.8% | $4K |
| scored | 2 | 1,000 | 104 | 104 | 48% | 51¢ | -7.4% | -23.8% to +8.5% | -$769 |
| scored | 2 | 5,000 | 51 | 51 | 45% | 52¢ | -10.3% | -33.3% to +14.3% | -$525 |
| scored | 3 | 1,000 | 2 | 2 | 50% | 51¢ | +8.4% | n/a to n/a | $17 |
| scored | 3 | 5,000 | 1 | 1 | 0% | 56¢ | -101.3% | n/a to n/a | -$101 |
| scored | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| one-sided pool | 1 | 1,000 | 12297 | 11933 | 53% | 52¢ | +0.6% | -1.0% to +2.2% | $8K |
| one-sided pool | 1 | 5,000 | 7326 | 7071 | 54% | 52¢ | +1.3% | -0.7% to +3.3% | $9K |
| one-sided pool | 2 | 1,000 | 2696 | 2685 | 54% | 51¢ | +3.6% | +0.1% to +7.0% | $10K |
| one-sided pool | 2 | 5,000 | 1416 | 1410 | 55% | 52¢ | +3.3% | -1.0% to +7.8% | $5K |
| one-sided pool | 3 | 1,000 | 748 | 747 | 55% | 51¢ | +5.4% | -0.5% to +11.8% | $4K |
| one-sided pool | 3 | 5,000 | 373 | 373 | 57% | 52¢ | +5.9% | -2.4% to +14.0% | $2K |
| one-sided pool | 4 | 1,000 | 235 | 235 | 59% | 52¢ | +12.5% | +2.1% to +23.3% | $3K |
| one-sided pool | 4 | 5,000 | 126 | 126 | 60% | 51¢ | +13.6% | -0.3% to +28.2% | $2K |
| one-sided pool | 5 | 1,000 | 77 | 77 | 58% | 52¢ | +9.8% | -8.8% to +28.7% | $751 |
| one-sided pool | 5 | 5,000 | 43 | 43 | 58% | 51¢ | +12.5% | -12.9% to +37.8% | $538 |
| whole pool | 1 | 1,000 | 12870 | 12506 | 53% | 52¢ | +0.3% | -1.3% to +1.8% | $4K |
| whole pool | 1 | 5,000 | 7678 | 7423 | 53% | 52¢ | +0.8% | -1.2% to +2.7% | $6K |
| whole pool | 2 | 1,000 | 2867 | 2856 | 53% | 51¢ | +3.2% | -0.1% to +6.5% | $9K |
| whole pool | 2 | 5,000 | 1539 | 1533 | 55% | 52¢ | +2.8% | -1.4% to +7.0% | $4K |
| whole pool | 3 | 1,000 | 847 | 846 | 55% | 51¢ | +5.9% | -0.1% to +11.5% | $5K |
| whole pool | 3 | 5,000 | 443 | 443 | 55% | 52¢ | +4.9% | -2.9% to +12.8% | $2K |
| whole pool | 4 | 1,000 | 278 | 278 | 57% | 51¢ | +12.4% | +1.9% to +22.1% | $3K |
| whole pool | 4 | 5,000 | 146 | 146 | 60% | 51¢ | +12.9% | -0.1% to +26.5% | $2K |
| whole pool | 5 | 1,000 | 97 | 97 | 58% | 51¢ | +10.9% | -6.7% to +28.3% | $1K |
| whole pool | 5 | 5,000 | 55 | 55 | 56% | 52¢ | +6.2% | -15.9% to +28.8% | $341 |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| under 30¢ | 3 | -102.3% |
| 30–60¢ | 193 | +13.1% |
| 60¢+ | 39 | +18.4% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 18622 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
