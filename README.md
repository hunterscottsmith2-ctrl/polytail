# PolyTail v2

Sends a Telegram alert when several proven Polymarket traders hold the same side of the same market. It also checks whether following those traders would actually have made money. It never places bets.

## What's in here
| File | What it does |
|---|---|
| `tracker.py` | Every 10 min: checks watched wallets and alerts you on consensus bets. Logs every alert to `signals_log.csv`. |
| `backtest.py` | Run on demand: replays recent history to see if tailing would have paid. It also builds the watchlist (`wallets.json`). |
| `scorecard.py` | Every Sunday: grades the live alerts once their markets settle and texts you the results. |
| `common.py` | Shared code used by the other three. |
| `.github/workflows/*.yml` | The schedules that run everything on GitHub for free. |

## Setup (about 20 minutes, on a computer)

### 1. Telegram bot
1. In Telegram, message **@BotFather**, send `/newbot`, and copy the **bot token**.
2. Send your new bot any message.
3. Open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser. Copy the number after `"chat":{"id":`. That's your **chat ID**.

### 2. GitHub repo
1. Create a **private** repo called `polytail` at github.com.
2. Unzip polytail.zip.
3. **Add file → Upload files**, and drag in the 4 `.py` files and this README. Commit.
4. For each of the 3 workflow files, click **Add file → Create new file**, type the name exactly, paste in that file's contents, and commit:
   - `.github/workflows/polytail.yml`
   - `.github/workflows/backtest.yml`
   - `.github/workflows/scorecard.yml`

   (On a Mac, the `.github` folder is hidden in Finder. Press Cmd+Shift+. to show it, or open the files from a text editor.)

### 3. Secrets
In the repo, go to **Settings → Secrets and variables → Actions** and add:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### 4. Run it
1. **Actions → PolyTail backtest → Run workflow** (keep the defaults). It takes roughly 20–60 min and sends you a Telegram summary when done.
2. **Actions → PolyTail scan → Run workflow** to test alerts. After that it runs on its own every ~10 min.
3. The scorecard runs on its own every Sunday morning.

## Reading the backtest
- **Verdict ✅:** a setting beat the market by a margin that's unlikely to be luck (30+ settled bets, with the whole 90% range above zero).
- **Verdict ❌:** no reliable edge was found. Treat the alerts as information, not as bets to tail.
- **"Scoring wallets beat the whole pool":** the backtest then writes `wallets.json`, and the live bot switches to watching only those vetted wallets. If scoring didn't help, the bot keeps using the leaderboard.
- `results/backtest_report.md` has the full table. Paste it to Claude to talk through it.

## Applying recommended settings
If the backtest finds an edge, it writes `results/recommended_settings.json`. To use it, create `settings.json` in the repo root with those values, for example:
```json
{"MIN_WALLETS_AGREEING": 3, "MIN_POSITION_USD": 5000}
```
Any setting listed at the top of `tracker.py` can go in that file.

## Notes
- Re-run the backtest every couple of weeks. `wallets.json` expires after 21 days, and the bot then falls back to the leaderboard.
- Results assume you bet 15 minutes after the signal and pay a 1% fee. Past results don't guarantee future ones.
- Make sure the version of Polymarket you use is legal where you live.
