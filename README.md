# 🏦 USD Bank Rate Monitor

Monitors one or more banks' USD rates every 30 minutes and sends a push notification on every run — completely **free**, no server required.

**Stack:** GitHub Actions (free) + Python (stdlib only) + ntfy.sh or Telegram

---

## Quick Setup

### Step 1 — Set your GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:

| Secret name | Value | Required |
|---|---|---|
| `BANKS` | `SAMPATH,HNB` | Optional |
| `ALERT_METHOD` | `ntfy` or `telegram` | ✅ Always |
| `NTFY_TOPIC` | e.g. `sampath-usd-nuwan-xyz` | Optional — default topic for all banks |
| `NTFY_TOPIC_SAMPATH` | e.g. `sampath-usd-nuwan-xyz` | Optional — overrides default for Sampath |
| `NTFY_TOPIC_HNB` | e.g. `hnB-usd-nuwan-xyz` | Optional — overrides default for HNB |
| `TELEGRAM_BOT_TOKEN` | From @BotFather | If using Telegram |
| `TELEGRAM_CHAT_ID` | Your chat ID | If using Telegram |
If you want separate topics per bank, set `NTFY_TOPIC_SAMPATH` and/or `NTFY_TOPIC_HNB`. If `NTFY_TOPIC` is set, it is used for banks without a specific per-bank setting.
---

### Step 3 — Choose your alert method

#### Option A: ntfy.sh (Simplest — 2 minutes)
1. Install the **ntfy** app on your phone ([Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) / [iOS](https://apps.apple.com/app/ntfy/id1625396347))
2. Pick a unique topic name, e.g. `sampath-usd-nuwan-abc123` (keep it unguessable)
3. In the app, tap **Subscribe** and enter your topic name
4. Set `NTFY_TOPIC` secret to that topic name, or set `NTFY_TOPIC_SAMPATH` / `NTFY_TOPIC_HNB` to assign different topics per bank
5. Set `ALERT_METHOD` secret to `ntfy`

#### Option B: Telegram Bot (Recommended — 5 minutes)
1. Open Telegram → search **@BotFather** → send `/newbot`
2. Follow prompts → copy the **bot token** → set as `TELEGRAM_BOT_TOKEN`
3. Send any message to your new bot
4. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in browser
5. Find `"chat":{"id":XXXXXXX}` → that number is your `TELEGRAM_CHAT_ID`
6. Set `ALERT_METHOD` secret to `telegram`

---

### Step 4 — Test it manually

Go to your repo → **Actions** tab → **Sampath Bank USD Rate Monitor** → **Run workflow**

If you use ntfy with multiple banks, set `NTFY_TOPIC_SAMPATH` and/or `NTFY_TOPIC_HNB` to route Sampath and HNB to different topics.

---

## Customising the Schedule

Edit `.github/workflows/check-rate.yml`:

```yaml
# Every 30 minutes (default)
- cron: "0,30 * * * *"

# Every 15 minutes
- cron: "*/15 * * * *"

# Every hour
- cron: "0 * * * *"

# Weekdays only, every 30 min, 8am–6pm Sri Lanka time (UTC+5:30 = UTC 2:30–12:30)
- cron: "0,30 3-12 * * 1-5"
```

---

## Troubleshooting

**Rate not found / parsing error:**
The script prints the raw API response when it can't parse the rate.
Check the Actions log and update the field names in `check_rate.py` under `fetch_usd_tt_buying_rate()`.

**GitHub Actions not running:**
GitHub pauses scheduled workflows on repos with no activity for 60 days.
Just push a small commit or run it manually to re-activate.

**Alert not arriving:**
- ntfy: make sure you subscribed to the exact same topic name (case-sensitive)
- Telegram: make sure you sent at least one message to the bot before running

---

## GitHub Actions Free Tier

- Free: **2,000 minutes/month** on public repos, **500 minutes/month** on private
- Each run takes ~20–30 seconds
- Running every 30 min = 48 runs/day × 0.5 min = **~24 min/day** = well within free limits

---

## File Structure

```
usd-rate-monitor/
├── .github/
│   └── workflows/
│       └── check-rate.yml   ← schedule + secrets wiring
└── check_rate.py            ← fetch rate + send alert logic
```
