import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

OUTPUT = Path("output")

ALERT_METHOD = os.environ.get("ALERT_METHOD", "ntfy").lower()
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
NTFY_TOPIC_SAMPATH = os.environ.get("NTFY_TOPIC_SAMPATH", "")
NTFY_TOPIC_HNB = os.environ.get("NTFY_TOPIC_HNB", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def load_results():
    results = []
    if not OUTPUT.exists():
        raise RuntimeError("No output directory found. Run fetch scripts first.")
    for path in sorted(OUTPUT.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "bank" in data and "rate" in data:
            results.append((data["bank"], float(data["rate"])))
    if not results:
        raise RuntimeError("No bank results found in output directory.")
    return results


def get_ntfy_topic(bank: str) -> tuple[str | None, bool]:
    bank = bank.strip().upper()
    if bank == "SAMPATH" and NTFY_TOPIC_SAMPATH:
        return NTFY_TOPIC_SAMPATH, True
    if bank == "HNB" and NTFY_TOPIC_HNB:
        return NTFY_TOPIC_HNB, True
    return (NTFY_TOPIC or None), False


def send_ntfy(bank: str, rate: float, topic: str):
    if not topic:
        raise RuntimeError(f"NTFY topic not configured for {bank}.")
    now = datetime.now(ZoneInfo("Asia/Colombo")).strftime('%Y-%m-%d %H:%M')
    message = (
        f"{bank} USD Buying: LKR {rate:.2f}\n"
        f"Checked: {now} (LK time)"
    )
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}",
        data=message.encode("utf-8"),
        headers={
            "Title": f"{bank} Rate Alert",
            "Priority": "high",
            "Content-Type": "text/plain; charset=utf-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(f"✅ ntfy alert sent for {bank}: {resp.status}")


def send_telegram(results):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID secret is not set.")
    now = datetime.now(ZoneInfo("Asia/Colombo")).strftime('%Y-%m-%d %H:%M')
    lines = ["🏦 *Bank Rate Notification*\n\n"]
    for bank, rate in results:
        lines.append(f"*{bank}*: LKR {rate:.2f}")
    lines.append(f"\n🕐 {now} (LK time)")
    message = "\n".join(lines)
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("ok"):
            print("✅ Telegram alert sent.")
        else:
            raise RuntimeError(f"Telegram API error: {result}")


def main():
    results = load_results()
    if ALERT_METHOD == "telegram":
        send_telegram(results)
        return

    for bank, rate in results:
        topic, mapped = get_ntfy_topic(bank)
        if not topic:
            print(f"⚠️  Skipping {bank}: no NTFY topic configured.")
            continue
        if mapped:
            print(f"ℹ️  Using per-bank topic for {bank}: {topic}")
        else:
            print(f"ℹ️  Using default topic for {bank}: {topic}")
        send_ntfy(bank, rate, topic)


if __name__ == "__main__":
    main()
