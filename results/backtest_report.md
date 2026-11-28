# PolyTail backtest report (overall)
Run 2026-11-28 09:19 UTC. Training window 150 days, test window 90 days.
Wallet pool 302, usable 133, bot-like skipped 133, selected by training score 26.
**Hedgers removed:** 5 wallets put more than 25% of their money into games where they held both sides. They're left out of the scored, sharp and proven lists and the live watchlist, and every wallet is judged on one-sided bets only.

**Verdict:** ✅ Edge found: whole pool wallets, N=5, min $5,000 → +34.7% per bet over 56 settled bets (90% range +0.7% to +76.9%).

Bets placed at the price 15 min after the signal where price history was available (88385 of 88397 rows; the rest use the wallet's own fill price +1¢, which is optimistic), minus Polymarket's taker fee (4% x (1 - price), about 2.0% of a 50¢ bet). The bid/ask spread is NOT included, so real results would be roughly 1-2% per bet worse.
Profit-scored wallets did NOT beat the whole pool (N=3, $1K).
**Sharp wallets (closing-line value):** 4 wallets beat the closing price consistently in training (20+ bets, avg 1¢+, t≥2). Too few sharp signals to judge (need 30+ settled). Whole pool best: +34.7%/bet. Following sharps did NOT clearly beat the pool.
**Proven winners (profitable AND beat the close):** 2 wallets. Too few signals to judge (need 30+ settled). Did NOT clearly beat the pool.

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| proven (profit+CLV) | 1 | 1,000 | 322 | 285 | 60% | 58¢ | +3.9% | -6.5% to +13.7% | $1K |
| proven (profit+CLV) | 1 | 5,000 | 254 | 230 | 62% | 59¢ | +6.5% | -4.1% to +17.9% | $1K |
| proven (profit+CLV) | 2 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 2 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 1 | 1,000 | 401 | 322 | 61% | 59¢ | +0.6% | -8.3% to +9.7% | $204 |
| sharp (CLV) | 1 | 5,000 | 301 | 253 | 63% | 60¢ | +7.1% | -3.9% to +18.2% | $2K |
| sharp (CLV) | 2 | 1,000 | 1 | 1 | 0% | 65¢ | -101.4% | n/a to n/a | -$101 |
| sharp (CLV) | 2 | 5,000 | 1 | 1 | 100% | 94¢ | +6.7% | n/a to n/a | $7 |
| sharp (CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 1 | 1,000 | 4111 | 3665 | 53% | 51¢ | +6.6% | +3.2% to +10.1% | $24K |
| scored | 1 | 5,000 | 2352 | 2113 | 55% | 53¢ | +6.1% | +1.6% to +10.7% | $13K |
| scored | 2 | 1,000 | 139 | 131 | 56% | 53¢ | +10.0% | -6.4% to +26.5% | $1K |
| scored | 2 | 5,000 | 93 | 88 | 60% | 55¢ | +20.6% | -4.6% to +51.5% | $2K |
| scored | 3 | 1,000 | 4 | 3 | 33% | 29¢ | -36.2% | n/a to n/a | -$108 |
| scored | 3 | 5,000 | 3 | 2 | 0% | 19¢ | -103.2% | n/a to n/a | -$206 |
| scored | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| one-sided pool | 1 | 1,000 | 19580 | 16699 | 54% | 53¢ | +0.6% | -0.9% to +2.1% | $11K |
| one-sided pool | 1 | 5,000 | 11728 | 9837 | 55% | 53¢ | +2.0% | +0.1% to +4.0% | $20K |
| one-sided pool | 2 | 1,000 | 3599 | 3091 | 55% | 54¢ | +3.6% | +0.3% to +7.2% | $11K |
| one-sided pool | 2 | 5,000 | 2020 | 1737 | 58% | 55¢ | +2.1% | -1.9% to +6.2% | $4K |
| one-sided pool | 3 | 1,000 | 960 | 783 | 58% | 55¢ | +3.9% | -2.2% to +10.0% | $3K |
| one-sided pool | 3 | 5,000 | 539 | 436 | 62% | 58¢ | +6.4% | -1.2% to +14.5% | $3K |
| one-sided pool | 4 | 1,000 | 349 | 262 | 61% | 58¢ | +5.0% | -5.5% to +16.7% | $1K |
| one-sided pool | 4 | 5,000 | 188 | 141 | 64% | 60¢ | +15.5% | -3.7% to +37.1% | $2K |
| one-sided pool | 5 | 1,000 | 128 | 93 | 72% | 64¢ | +10.7% | -4.3% to +26.0% | $994 |
| one-sided pool | 5 | 5,000 | 65 | 48 | 79% | 68¢ | +17.9% | -0.9% to +37.3% | $861 |
| whole pool | 1 | 1,000 | 20568 | 17558 | 53% | 53¢ | +0.2% | -1.2% to +1.6% | $4K |
| whole pool | 1 | 5,000 | 12182 | 10247 | 54% | 53¢ | +1.7% | -0.3% to +3.5% | $17K |
| whole pool | 2 | 1,000 | 3898 | 3323 | 56% | 54¢ | +4.3% | +1.1% to +7.6% | $14K |
| whole pool | 2 | 5,000 | 2182 | 1859 | 57% | 55¢ | +2.1% | -1.6% to +5.9% | $4K |
| whole pool | 3 | 1,000 | 1041 | 858 | 58% | 55¢ | +4.9% | -1.1% to +11.0% | $4K |
| whole pool | 3 | 5,000 | 599 | 493 | 63% | 58¢ | +5.6% | -1.3% to +12.7% | $3K |
| whole pool | 4 | 1,000 | 372 | 281 | 61% | 58¢ | +5.9% | -4.7% to +16.6% | $2K |
| whole pool | 4 | 5,000 | 201 | 154 | 66% | 60¢ | +10.8% | -3.4% to +26.0% | $2K |
| whole pool | 5 | 1,000 | 141 | 107 | 70% | 62¢ | +10.2% | -3.6% to +24.7% | $1K |
| whole pool | 5 | 5,000 | 75 | 56 | 77% | 66¢ | +34.7% | +0.7% to +76.9% | $2K |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| under 30¢ | 5 | +233.6% |
| 30–60¢ | 14 | +28.8% |
| 60¢+ | 37 | +10.1% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 4775 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
