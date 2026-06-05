#!/usr/bin/env python3
"""
Sampath Bank USD TT Buying Rate Monitor
Fetches the rate, compares with threshold, sends alert via Telegram or ntfy.sh
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from zoneinfo import ZoneInfo
from fetch_sampath import SampathBankFetcher
from fetch_hnb import HNBBankFetcher

# ── Configuration (set these as GitHub Secrets) ─────────────────────────────
ALERT_METHOD      = os.environ.get("ALERT_METHOD", "ntfy")             # "ntfy" or "telegram"
BANKS             = [bank.strip().upper() for bank in os.environ.get("BANKS", "SAMPATH,HNB").split(",") if bank.strip()]

# ntfy.sh config
NTFY_TOPIC        = os.environ.get("NTFY_TOPIC", "")                   # default topic for all banks
NTFY_TOPIC_SAMPATH = os.environ.get("NTFY_TOPIC_SAMPATH", "")
NTFY_TOPIC_HNB     = os.environ.get("NTFY_TOPIC_HNB", "")

# Telegram config
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

## ── Fetch Rate ───────────────────────────────────────────────────────────────


def get_ntfy_topic_for_bank(bank: str) -> tuple[str | None, bool]:
    bank = bank.strip().upper()
    if bank == "SAMPATH":
        if NTFY_TOPIC_SAMPATH:
            return NTFY_TOPIC_SAMPATH, True
    elif bank == "HNB":
        if NTFY_TOPIC_HNB:
            return NTFY_TOPIC_HNB, True
    return (NTFY_TOPIC or None), False


def fetch_rate_for_bank(bank: str) -> float:
    bank = bank.strip().upper()
    if bank == "SAMPATH":
        return SampathBankFetcher().fetch_rate()
    if bank == "HNB":
        return HNBBankFetcher().fetch_rate()
    raise RuntimeError(f"Unsupported bank: {bank}")


# ── Send Alerts ──────────────────────────────────────────────────────────────
def send_ntfy(rate: float, bank: str, topic: str):
    """Send push notification via ntfy.sh (free, no signup)."""
    if not topic:
        raise RuntimeError(f"NTFY topic not set for {bank}.")

    now = datetime.now(ZoneInfo("Asia/Colombo")).strftime('%Y-%m-%d %H:%M')
    message = (
        f"{bank} USD TT Buying: LKR {rate:.2f}\n"
        f"Checked: {now} (LK time)"
    )
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}",
        data=message.encode("utf-8"),
        headers={
            "Title":    f"{bank} Rate Alert",
            "Priority": "high",
            "Tags":     "dollar,moneybag",
            "Content-Type": "text/plain; charset=utf-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"✅ ntfy alert sent for {bank}: {resp.status}")


def send_telegram(rates: list[tuple[str, float]]):
    """Send a combined message via Telegram Bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID secret is not set.")

    now = datetime.now(ZoneInfo("Asia/Colombo")).strftime('%Y-%m-%d %H:%M')
    lines = [f"🏦 *Bank Rate Notification*\n\n"]
    for bank, rate in rates:
        lines.append(f"*{bank}*: LKR {rate:.2f}")
    lines.append(f"\n🕐 {now} (LK time)")
    message = "\n".join(lines)

    payload = json.dumps({
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("ok"):
            print(f"✅ Telegram alert sent.")
        else:
            raise RuntimeError(f"Telegram API error: {result}")


def send_ntfy_notifications(rates: list[tuple[str, float]]):
    for bank, rate in rates:
        topic, mapped = get_ntfy_topic_for_bank(bank)
        if not topic:
            print(f"⚠️  Skipping {bank}: no NTFY topic configured.")
            continue
        if mapped:
            print(f"ℹ️  Using per-bank topic for {bank}: {topic}")
        else:
            print(f"ℹ️  Using default topic for {bank}: {topic}")
        send_ntfy(rate, bank, topic)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print(f"{'='*50}")
    print(f"  Bank USD Rate Monitor")
    print(f"  {datetime.now(ZoneInfo('Asia/Colombo')).strftime('%Y-%m-%d %H:%M:%S')} (SL)")
    print(f"{'='*50}")
    print(f"  Banks: {', '.join(BANKS)}")
    print(f"  Alerts every run (no threshold)")
    print(f"  Alert via : {ALERT_METHOD.upper()}")
    print()

    rates = []
    for bank in BANKS:
        print(f"📡 Fetching rate from {bank}...")
        rate = fetch_rate_for_bank(bank)
        print(f"💵 {bank} USD Buying Rate: LKR {rate:.2f}")
        rates.append((bank, rate))
        print()

    print("🔔 Sending notifications...")
    if ALERT_METHOD.lower() == "telegram":
        send_telegram(rates)
    else:
        send_ntfy_notifications(rates)

    print()
    print("✅ Done.")


if __name__ == "__main__":
    main()
