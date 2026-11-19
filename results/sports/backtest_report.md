# PolyTail backtest report (sports)
Run 2026-11-19 15:30 UTC. Training window 150 days, test window 90 days.
Wallet pool 596, usable 340, bot-like skipped 188, selected by training score 81.
**Hedgers removed:** 17 wallets put more than 25% of their money into games where they held both sides. They're left out of the scored, sharp and proven lists and the live watchlist, and every wallet is judged on one-sided bets only.

**Verdict:** ✅ Edge found: one-sided pool wallets, N=3, min $5,000 → +5.7% per bet over 973 settled bets (90% range +0.5% to +10.9%).

Bets placed at the price 15 min after the signal where price history was available (107774 of 107774 rows; the rest use the wallet's own fill price +1¢, which is optimistic), minus Polymarket's taker fee (3% x (1 - price), about 1.5% of a 50¢ bet). The bid/ask spread is NOT included, so real results would be roughly 1-2% per bet worse.
Profit-scored wallets did NOT beat the whole pool (N=3, $1K).
**Sharp wallets (closing-line value):** 18 wallets beat the closing price consistently in training (20+ bets, avg 1¢+, t≥2). Best sharp setting: N=2, $5,000 → +8.3%/bet over 138 bets. Whole pool best: +7.3%/bet. Following sharps did NOT clearly beat the pool.
**Proven winners (profitable AND beat the close):** 11 wallets. Best: N=2, $5,000 → +10.4%/bet over 83 bets. Did NOT clearly beat the pool.

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| proven (profit+CLV) | 1 | 1,000 | 4288 | 4250 | 53% | 52¢ | +1.4% | -1.2% to +4.0% | $6K |
| proven (profit+CLV) | 1 | 5,000 | 1125 | 1120 | 56% | 54¢ | +4.0% | -1.1% to +9.2% | $5K |
| proven (profit+CLV) | 2 | 1,000 | 487 | 487 | 53% | 51¢ | +2.9% | -5.1% to +10.8% | $1K |
| proven (profit+CLV) | 2 | 5,000 | 83 | 83 | 64% | 56¢ | +10.4% | -5.5% to +26.3% | $866 |
| proven (profit+CLV) | 3 | 1,000 | 53 | 53 | 51% | 51¢ | +1.7% | -21.2% to +27.9% | $91 |
| proven (profit+CLV) | 3 | 5,000 | 5 | 5 | 40% | 66¢ | -57.3% | -101.5% to -13.1% | -$287 |
| proven (profit+CLV) | 4 | 1,000 | 2 | 2 | 100% | 48¢ | +107.3% | n/a to n/a | $215 |
| proven (profit+CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| proven (profit+CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 1 | 1,000 | 4557 | 4513 | 53% | 52¢ | +1.8% | -0.8% to +4.5% | $8K |
| sharp (CLV) | 1 | 5,000 | 1372 | 1365 | 55% | 53¢ | +4.7% | +0.0% to +9.2% | $6K |
| sharp (CLV) | 2 | 1,000 | 585 | 585 | 54% | 50¢ | +5.6% | -1.7% to +12.5% | $3K |
| sharp (CLV) | 2 | 5,000 | 138 | 138 | 59% | 54¢ | +8.3% | -5.3% to +22.0% | $1K |
| sharp (CLV) | 3 | 1,000 | 79 | 79 | 52% | 50¢ | +3.0% | -16.8% to +23.0% | $238 |
| sharp (CLV) | 3 | 5,000 | 15 | 15 | 47% | 54¢ | -22.1% | -60.4% to +15.1% | -$331 |
| sharp (CLV) | 4 | 1,000 | 8 | 8 | 62% | 51¢ | +24.3% | -28.2% to +76.5% | $194 |
| sharp (CLV) | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| sharp (CLV) | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 1 | 1,000 | 4623 | 4592 | 52% | 51¢ | +0.9% | -1.8% to +3.7% | $4K |
| scored | 1 | 5,000 | 2208 | 2200 | 51% | 51¢ | +1.2% | -2.7% to +5.2% | $3K |
| scored | 2 | 1,000 | 401 | 400 | 49% | 51¢ | -6.7% | -14.9% to +1.5% | -$3K |
| scored | 2 | 5,000 | 135 | 135 | 45% | 50¢ | -12.0% | -25.8% to +2.6% | -$2K |
| scored | 3 | 1,000 | 47 | 47 | 49% | 48¢ | -1.5% | -27.8% to +22.7% | -$68 |
| scored | 3 | 5,000 | 10 | 10 | 30% | 44¢ | -32.3% | -82.5% to +28.7% | -$323 |
| scored | 4 | 1,000 | 7 | 7 | 57% | 51¢ | +8.7% | -49.7% to +70.1% | $61 |
| scored | 4 | 5,000 | 1 | 1 | 100% | 52¢ | +92.7% | n/a to n/a | $93 |
| scored | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| one-sided pool | 1 | 1,000 | 18728 | 18217 | 53% | 52¢ | -0.0% | -1.3% to +1.3% | -$750 |
| one-sided pool | 1 | 5,000 | 10396 | 10102 | 53% | 52¢ | -0.3% | -1.9% to +1.3% | -$3K |
| one-sided pool | 2 | 1,000 | 5590 | 5547 | 53% | 52¢ | +2.0% | -0.3% to +4.4% | $11K |
| one-sided pool | 2 | 5,000 | 2591 | 2579 | 54% | 52¢ | +2.1% | -1.4% to +5.6% | $5K |
| one-sided pool | 3 | 1,000 | 2281 | 2272 | 53% | 52¢ | +1.8% | -1.7% to +5.2% | $4K |
| one-sided pool | 3 | 5,000 | 974 | 973 | 56% | 52¢ | +5.7% | +0.5% to +10.9% | $6K |
| one-sided pool | 4 | 1,000 | 1065 | 1062 | 53% | 52¢ | +1.5% | -3.7% to +6.9% | $2K |
| one-sided pool | 4 | 5,000 | 418 | 417 | 56% | 52¢ | +4.5% | -3.7% to +12.7% | $2K |
| one-sided pool | 5 | 1,000 | 517 | 517 | 56% | 52¢ | +6.2% | -0.7% to +13.7% | $3K |
| one-sided pool | 5 | 5,000 | 207 | 207 | 57% | 51¢ | +5.9% | -5.6% to +16.7% | $1K |
| whole pool | 1 | 1,000 | 19444 | 18931 | 52% | 52¢ | -0.2% | -1.5% to +1.1% | -$4K |
| whole pool | 1 | 5,000 | 10847 | 10553 | 52% | 52¢ | -0.5% | -2.3% to +1.2% | -$6K |
| whole pool | 2 | 1,000 | 5809 | 5766 | 53% | 52¢ | +2.2% | -0.2% to +4.4% | $13K |
| whole pool | 2 | 5,000 | 2730 | 2718 | 54% | 52¢ | +1.6% | -1.7% to +4.9% | $4K |
| whole pool | 3 | 1,000 | 2419 | 2410 | 53% | 51¢ | +0.7% | -2.8% to +4.2% | $2K |
| whole pool | 3 | 5,000 | 1064 | 1063 | 56% | 52¢ | +4.9% | -0.4% to +9.7% | $5K |
| whole pool | 4 | 1,000 | 1157 | 1154 | 53% | 51¢ | +2.0% | -2.9% to +6.9% | $2K |
| whole pool | 4 | 5,000 | 474 | 473 | 55% | 52¢ | +3.6% | -4.2% to +11.4% | $2K |
| whole pool | 5 | 1,000 | 587 | 587 | 55% | 51¢ | +4.6% | -2.0% to +11.4% | $3K |
| whole pool | 5 | 5,000 | 247 | 247 | 57% | 51¢ | +7.3% | -2.7% to +17.7% | $2K |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| under 30¢ | 24 | -54.3% |
| 30–60¢ | 757 | +6.7% |
| 60¢+ | 192 | +9.5% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 19357 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
