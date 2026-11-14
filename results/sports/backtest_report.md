# PolyTail backtest report (sports)
Run 2026-11-14 22:05 UTC. Training window 150 days, test window 90 days.
Wallet pool 295, usable 132, bot-like skipped 139, selected by training score 35.

**Verdict:** ✅ Edge found: whole pool wallets, N=4, min $5,000 → +22.2% per bet over 59 settled bets (90% range +2.3% to +42.5%).

Bets placed at the price 15 min after the signal, minus a 1% fee. A random bet at market price averages about -1% after that fee, so that's the bar to beat.
Scoring wallets did NOT beat using the whole pool (N=3, $1K).

| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |
|---|---|---|---|---|---|---|---|---|---|
| scored | 1 | 1,000 | 1076 | 1075 | 51% | 50¢ | +1.7% | -3.7% to +6.7% | $2K |
| scored | 1 | 5,000 | 789 | 788 | 52% | 50¢ | +3.7% | -2.6% to +10.0% | $3K |
| scored | 2 | 1,000 | 24 | 24 | 54% | 51¢ | +7.7% | -26.5% to +44.7% | $184 |
| scored | 2 | 5,000 | 18 | 18 | 50% | 48¢ | +7.4% | -34.8% to +50.3% | $134 |
| scored | 3 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 3 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 4 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 4 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 1,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| scored | 5 | 5,000 | 0 | 0 | 0% | 0¢ | +0.0% | n/a to n/a | $0 |
| whole pool | 1 | 1,000 | 9612 | 9229 | 53% | 52¢ | +0.7% | -1.0% to +2.5% | $7K |
| whole pool | 1 | 5,000 | 5963 | 5696 | 54% | 53¢ | +1.0% | -1.2% to +3.3% | $6K |
| whole pool | 2 | 1,000 | 1592 | 1575 | 55% | 52¢ | +4.1% | -0.0% to +8.1% | $6K |
| whole pool | 2 | 5,000 | 926 | 915 | 55% | 53¢ | +3.5% | -1.9% to +8.9% | $3K |
| whole pool | 3 | 1,000 | 378 | 378 | 58% | 53¢ | +9.7% | +1.4% to +17.9% | $4K |
| whole pool | 3 | 5,000 | 207 | 207 | 62% | 53¢ | +15.5% | +4.6% to +26.7% | $3K |
| whole pool | 4 | 1,000 | 115 | 115 | 60% | 52¢ | +14.0% | -1.3% to +29.1% | $2K |
| whole pool | 4 | 5,000 | 59 | 59 | 64% | 53¢ | +22.2% | +2.3% to +42.5% | $1K |
| whole pool | 5 | 1,000 | 32 | 32 | 69% | 53¢ | +26.4% | -1.0% to +51.9% | $846 |
| whole pool | 5 | 5,000 | 12 | 12 | 67% | 55¢ | +19.3% | -24.7% to +59.7% | $232 |

## Best setting by entry price
| Price | Bets | Mean ROI |
|---|---|---|
| 30–60¢ | 50 | +20.0% |
| 60¢+ | 9 | +34.4% |

## Caveats
- The wallet pool comes from today's leaderboards, which partly reflect test-window profits. The volume boards and training-only scoring reduce this, but results may still be a bit optimistic.
- 4000 prices pulled from history; others use trigger price +1¢.
- Past results don't guarantee future ones. Markets adapt when edges get crowded.
