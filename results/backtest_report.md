# PolyTail backtest report (overall)
Run 2026-11-15 00:47 UTC. Training window 150 days, test window 90 days.
Wallet pool 308, usable 135, bot-like skipped 135, selected by training score 32.

**Verdict:** ❌ No setting showed a reliable edge (needs 30+ settled bets with the whole 90% range above zero). Don't bet real money on these alerts yet.

Bets placed at the price 15 min after the signal, minus a 1% fee. A random bet at market price averages about -1% after that fee, so that's the bar to beat.
Profit-scored wallets beat the whole pool (N=3, $1K).
**Sharp wallets (closing-line value):** 5 wallets beat the closing price consistently in training (20+ bets, avg 1¢+, t≥2). Too few sharp signals to judge (need 30+ settled). Whole pool best: +6.9%/bet. Following sharps did NOT clearly beat the pool.
**Proven winners (profitable AND beat the close):** 4 wallets. Too few signals to judge (need 30+ settled). Did NOT clearly beat the pool.

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| proven (profit+CLV) | 1 | 1,000 | 408 | 294 | 57% | 58¢ | -1.4% | -11.7% to +9.2% | -$398 |
| proven (profit+CLV) | 1 | 5,000 | 289 | 225 | 58% | 58¢ | +1.6% | -10.3% to +13.4% | $349 |
| proven (profit+CLV) | 2 | 1,000 | 4 | 4 | 75% | 81¢ | -14.3% | n/a to n/a | -$57 |
| proven (profit+CLV) | 2 | 5,000 | 3 | 3 | 100% | 89¢ | +11.3% | n/a to n/a | $34 |
| proven (profit+CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 1 | 1,000 | 1863 | 1706 | 56% | 54¢ | +3.7% | -0.4% to +7.9% | $6K |
| sharp (CLV) | 1 | 5,000 | 705 | 633 | 59% | 58¢ | +1.8% | -4.6% to +8.0% | $1K |
| sharp (CLV) | 2 | 1,000 | 14 | 14 | 50% | 58¢ | -17.9% | -57.2% to +26.5% | -$251 |
| sharp (CLV) | 2 | 5,000 | 10 | 10 | 70% | 61¢ | +17.3% | -32.9% to +69.6% | $173 |
| sharp (CLV) | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 1 | 1,000 | 5319 | 4659 | 52% | 51¢ | +2.9% | -0.1% to +5.7% | $13K |
| scored | 1 | 5,000 | 3763 | 3432 | 53% | 52¢ | +1.5% | -1.7% to +4.8% | $5K |
| scored | 2 | 1,000 | 616 | 537 | 50% | 50¢ | +1.1% | -7.4% to +10.6% | $589 |
| scored | 2 | 5,000 | 404 | 369 | 51% | 52¢ | +0.1% | -10.2% to +10.2% | $42 |
| scored | 3 | 1,000 | 110 | 95 | 56% | 53¢ | +2.5% | -15.0% to +20.5% | $239 |
| scored | 3 | 5,000 | 75 | 63 | 54% | 57¢ | -8.0% | -28.3% to +12.3% | -$501 |
| scored | 4 | 1,000 | 27 | 21 | 48% | 48¢ | +37.1% | -44.4% to +155.0% | $779 |
| scored | 4 | 5,000 | 17 | 12 | 42% | 47¢ | +67.7% | -68.9% to +274.4% | $813 |
| scored | 5 | 1,000 | 8 | 6 | 50% | 46¢ | +2.6% | -78.3% to +83.5% | $16 |
| scored | 5 | 5,000 | 4 | 3 | 67% | 56¢ | -0.6% | n/a to n/a | -$2 |
| whole pool | 1 | 1,000 | 20705 | 17614 | 53% | 53¢ | +1.1% | -0.3% to +2.5% | $19K |
| whole pool | 1 | 5,000 | 12433 | 10529 | 54% | 53¢ | +1.2% | -0.6% to +2.9% | $13K |
| whole pool | 2 | 1,000 | 5113 | 4391 | 55% | 54¢ | +1.4% | -1.3% to +4.1% | $6K |
| whole pool | 2 | 5,000 | 2800 | 2475 | 55% | 54¢ | +1.0% | -2.4% to +4.4% | $3K |
| whole pool | 3 | 1,000 | 2181 | 1832 | 57% | 56¢ | -0.2% | -4.3% to +3.6% | -$458 |
| whole pool | 3 | 5,000 | 1053 | 928 | 58% | 56¢ | +0.9% | -4.9% to +6.7% | $791 |
| whole pool | 4 | 1,000 | 1150 | 932 | 59% | 57¢ | +0.0% | -5.0% to +5.2% | $47 |
| whole pool | 4 | 5,000 | 468 | 389 | 61% | 58¢ | +4.1% | -4.0% to +12.7% | $2K |
| whole pool | 5 | 1,000 | 535 | 413 | 59% | 57¢ | +0.5% | -7.3% to +9.3% | $209 |
| whole pool | 5 | 5,000 | 194 | 154 | 63% | 59¢ | +6.9% | -6.3% to +20.8% | $1K |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 4000 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
