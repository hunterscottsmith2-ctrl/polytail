# PolyTail backtest report
Run 2026-11-14 16:56 UTC. Training window 150 days, test window 90 days.
Wallet pool 310, usable 116, bot-like skipped 157, selected by training score 26.

**Verdict:** ✅ Edge found: whole pool wallets, N=4, min $5,000 → +26.8% per bet over 115 settled bets (90% range +6.0% to +50.6%).

Bets placed at the price 15 min after the signal, minus a 1% fee. A random bet at market price averages about -1% after that fee, so that's the bar to beat.
Scoring wallets did NOT beat using the whole pool (N=3, $1K).

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| scored | 1 | 1,000 | 2622 | 2294 | 54% | 52¢ | +3.4% | -0.9% to +7.5% | $8K |
| scored | 1 | 5,000 | 1670 | 1511 | 55% | 54¢ | +4.4% | -0.3% to +9.2% | $7K |
| scored | 2 | 1,000 | 205 | 171 | 55% | 51¢ | +10.7% | -6.5% to +31.6% | $2K |
| scored | 2 | 5,000 | 116 | 95 | 58% | 54¢ | +16.2% | -7.5% to +45.5% | $2K |
| scored | 3 | 1,000 | 30 | 24 | 58% | 55¢ | -1.5% | -32.1% to +30.5% | -$37 |
| scored | 3 | 5,000 | 17 | 12 | 50% | 61¢ | -29.4% | -65.4% to +6.3% | -$352 |
| scored | 4 | 1,000 | 5 | 5 | 60% | 60¢ | -7.7% | -77.6% to +62.8% | -$38 |
| scored | 4 | 5,000 | 2 | 2 | 100% | 87¢ | +14.0% | n/a to n/a | $28 |
| scored | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| whole pool | 1 | 1,000 | 15502 | 12931 | 53% | 52¢ | +0.5% | -1.2% to +2.2% | $6K |
| whole pool | 1 | 5,000 | 9386 | 7627 | 54% | 54¢ | +0.3% | -1.7% to +2.2% | $2K |
| whole pool | 2 | 1,000 | 2584 | 2081 | 55% | 54¢ | +3.9% | -0.2% to +7.9% | $8K |
| whole pool | 2 | 5,000 | 1552 | 1304 | 58% | 55¢ | +3.4% | -1.2% to +8.0% | $4K |
| whole pool | 3 | 1,000 | 817 | 602 | 57% | 56¢ | +0.8% | -6.1% to +8.2% | $482 |
| whole pool | 3 | 5,000 | 448 | 357 | 60% | 56¢ | +6.8% | -2.5% to +16.0% | $2K |
| whole pool | 4 | 1,000 | 341 | 230 | 60% | 57¢ | +3.9% | -8.9% to +17.8% | $902 |
| whole pool | 4 | 5,000 | 156 | 115 | 70% | 60¢ | +26.8% | +6.0% to +50.6% | $3K |
| whole pool | 5 | 1,000 | 193 | 109 | 69% | 63¢ | +12.1% | -3.1% to +27.2% | $1K |
| whole pool | 5 | 5,000 | 76 | 51 | 71% | 62¢ | +21.9% | -1.9% to +48.1% | $1K |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| under 30¢ | 10 | +119.5% |
| 30–60¢ | 48 | +37.9% |
| 60¢+ | 57 | +1.3% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 4000 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
