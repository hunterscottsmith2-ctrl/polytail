# PolyTail backtest report (overall)
Run 2026-11-19 16:01 UTC. Training window 150 days, test window 90 days.
Wallet pool 595, usable 299, bot-like skipped 221, selected by training score 62.
**Hedgers removed:** 22 wallets put more than 25% of their money into games where they held both sides. They're left out of the scored, sharp and proven lists and the live watchlist, and every wallet is judged on one-sided bets only.

**Verdict:** ✅ Edge found: scored wallets, N=3, min $1,000 → +33.9% per bet over 110 settled bets (90% range +15.9% to +53.4%).

Bets placed at the price 15 min after the signal where price history was available (159668 of 162361 rows; the rest use the wallet's own fill price +1¢, which is optimistic), minus Polymarket's taker fee (4% x (1 - price), about 2.0% of a 50¢ bet). The bid/ask spread is NOT included, so real results would be roughly 1-2% per bet worse.
Profit-scored wallets beat the whole pool (N=3, $1K).
**Sharp wallets (closing-line value):** 13 wallets beat the closing price consistently in training (20+ bets, avg 1¢+, t≥2). Best sharp setting: N=2, $5,000 → +9.4%/bet over 121 bets. Whole pool best: +4.8%/bet. Following sharps did NOT clearly beat the pool.
**Proven winners (profitable AND beat the close):** 10 wallets. Best: N=2, $5,000 → +8.2%/bet over 106 bets. Did NOT clearly beat the pool.

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| proven (profit+CLV) | 1 | 1,000 | 4989 | 4822 | 53% | 52¢ | +0.6% | -2.1% to +3.0% | $3K |
| proven (profit+CLV) | 1 | 5,000 | 1679 | 1600 | 56% | 54¢ | +2.9% | -1.4% to +7.0% | $5K |
| proven (profit+CLV) | 2 | 1,000 | 455 | 447 | 52% | 51¢ | +1.1% | -6.9% to +9.2% | $492 |
| proven (profit+CLV) | 2 | 5,000 | 110 | 106 | 64% | 57¢ | +8.2% | -5.6% to +22.4% | $874 |
| proven (profit+CLV) | 3 | 1,000 | 23 | 21 | 62% | 49¢ | +37.0% | -7.6% to +86.8% | $777 |
| proven (profit+CLV) | 3 | 5,000 | 3 | 3 | 33% | 32¢ | +10.3% | n/a to n/a | $31 |
| proven (profit+CLV) | 4 | 1,000 | 1 | 1 | 100% | 30¢ | +236.2% | n/a to n/a | $236 |
| proven (profit+CLV) | 4 | 5,000 | 1 | 1 | 100% | 30¢ | +230.5% | n/a to n/a | $231 |
| proven (profit+CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 1 | 1,000 | 5105 | 4930 | 53% | 52¢ | +0.2% | -2.4% to +2.7% | $745 |
| sharp (CLV) | 1 | 5,000 | 1778 | 1694 | 56% | 54¢ | +2.3% | -1.8% to +6.5% | $4K |
| sharp (CLV) | 2 | 1,000 | 485 | 477 | 53% | 51¢ | +3.4% | -5.0% to +12.1% | $2K |
| sharp (CLV) | 2 | 5,000 | 125 | 121 | 63% | 56¢ | +9.4% | -5.0% to +23.6% | $1K |
| sharp (CLV) | 3 | 1,000 | 28 | 26 | 65% | 50¢ | +38.5% | +0.2% to +78.3% | $1000 |
| sharp (CLV) | 3 | 5,000 | 6 | 6 | 50% | 49¢ | -4.7% | -79.9% to +74.8% | -$28 |
| sharp (CLV) | 4 | 1,000 | 1 | 1 | 100% | 30¢ | +236.2% | n/a to n/a | $236 |
| sharp (CLV) | 4 | 5,000 | 1 | 1 | 100% | 30¢ | +230.5% | n/a to n/a | $231 |
| sharp (CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 1 | 1,000 | 6238 | 5652 | 54% | 53¢ | +1.8% | -0.7% to +4.3% | $10K |
| scored | 1 | 5,000 | 4211 | 3882 | 55% | 54¢ | +2.3% | -0.7% to +5.4% | $9K |
| scored | 2 | 1,000 | 721 | 649 | 57% | 54¢ | +7.0% | -1.1% to +15.0% | $5K |
| scored | 2 | 5,000 | 490 | 441 | 58% | 56¢ | +2.4% | -5.5% to +10.6% | $1K |
| scored | 3 | 1,000 | 131 | 110 | 72% | 60¢ | +33.9% | +15.9% to +53.4% | $4K |
| scored | 3 | 5,000 | 78 | 64 | 73% | 64¢ | +23.7% | +3.8% to +43.6% | $2K |
| scored | 4 | 1,000 | 32 | 26 | 73% | 62¢ | +16.3% | -10.3% to +40.9% | $423 |
| scored | 4 | 5,000 | 17 | 13 | 77% | 63¢ | +27.0% | -11.7% to +66.1% | $351 |
| scored | 5 | 1,000 | 12 | 11 | 82% | 68¢ | +26.0% | -11.8% to +59.7% | $286 |
| scored | 5 | 5,000 | 8 | 7 | 86% | 71¢ | +25.4% | -15.2% to +62.1% | $178 |
| one-sided pool | 1 | 1,000 | 29229 | 22383 | 54% | 53¢ | +1.2% | -0.1% to +2.4% | $26K |
| one-sided pool | 1 | 5,000 | 16633 | 13521 | 55% | 53¢ | +1.3% | -0.3% to +2.9% | $17K |
| one-sided pool | 2 | 1,000 | 7277 | 6193 | 54% | 52¢ | +1.5% | -0.8% to +3.8% | $10K |
| one-sided pool | 2 | 5,000 | 4231 | 3636 | 56% | 54¢ | +2.4% | -0.5% to +5.5% | $9K |
| one-sided pool | 3 | 1,000 | 2871 | 2383 | 55% | 53¢ | +3.7% | -0.1% to +8.1% | $9K |
| one-sided pool | 3 | 5,000 | 1603 | 1362 | 59% | 55¢ | +5.2% | +0.5% to +9.8% | $7K |
| one-sided pool | 4 | 1,000 | 1346 | 1063 | 58% | 55¢ | +5.5% | -0.1% to +11.0% | $6K |
| one-sided pool | 4 | 5,000 | 702 | 569 | 61% | 57¢ | +6.7% | -0.4% to +14.0% | $4K |
| one-sided pool | 5 | 1,000 | 705 | 506 | 61% | 57¢ | +4.4% | -3.0% to +12.4% | $2K |
| one-sided pool | 5 | 5,000 | 356 | 275 | 61% | 57¢ | +8.1% | -2.3% to +19.4% | $2K |
| whole pool | 1 | 1,000 | 31212 | 23916 | 54% | 53¢ | +0.7% | -0.5% to +2.0% | $18K |
| whole pool | 1 | 5,000 | 17563 | 14272 | 55% | 53¢ | +1.1% | -0.5% to +2.6% | $15K |
| whole pool | 2 | 1,000 | 8088 | 6811 | 54% | 53¢ | +1.8% | -0.5% to +4.1% | $12K |
| whole pool | 2 | 5,000 | 4729 | 3998 | 56% | 54¢ | +2.8% | -0.0% to +5.7% | $11K |
| whole pool | 3 | 1,000 | 3332 | 2761 | 56% | 53¢ | +4.8% | +0.9% to +8.8% | $13K |
| whole pool | 3 | 5,000 | 1928 | 1624 | 57% | 55¢ | +2.9% | -1.3% to +7.3% | $5K |
| whole pool | 4 | 1,000 | 1609 | 1282 | 57% | 54¢ | +4.3% | -0.5% to +9.5% | $6K |
| whole pool | 4 | 5,000 | 889 | 727 | 60% | 56¢ | +4.1% | -2.0% to +10.3% | $3K |
| whole pool | 5 | 1,000 | 875 | 651 | 60% | 56¢ | +4.7% | -2.1% to +11.4% | $3K |
| whole pool | 5 | 5,000 | 455 | 361 | 61% | 57¢ | +4.7% | -4.0% to +13.7% | $2K |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| under 30¢ | 11 | +150.7% |
| 30–60¢ | 45 | +34.1% |
| 60¢+ | 54 | +9.9% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 23450 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
