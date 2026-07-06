import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from fetch_boc import BOCBankFetcher
from fetch_combank import ComBankBankFetcher
from fetch_hnb import HNBBankFetcher
from fetch_ndb import NDBBankFetcher
from fetch_peoples import PeoplesBankFetcher
from fetch_sampath import SampathBankFetcher


TZ = ZoneInfo("Asia/Colombo")
OUT_DIR = Path("web/public/data")
RATES_PATH = OUT_DIR / "rates.json"
HISTORY_PATH = OUT_DIR / "history.json"
ENTRY_RETENTION_DAYS = 7


def fetch_all_rates():
    fetchers = [
        SampathBankFetcher(),
        HNBBankFetcher(),
        PeoplesBankFetcher(),
        NDBBankFetcher(),
        BOCBankFetcher(),
        ComBankBankFetcher(),
    ]

    rates = {}
    for fetcher in fetchers:
        try:
            rates[fetcher.name] = fetcher.fetch_all_rates()
        except Exception as e:
            print(f"⚠️  Could not fetch {fetcher.name} rates: {e}")

    return rates


def load_history():
    if not HISTORY_PATH.exists():
        return {}

    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠️  Could not read history: {e}")
        return {}


def rates_changed(new_rates, history):
    latest = history.get("latest")
    if latest is None:
        return True

    # Any bank missing or changed?
    for bank, bank_rates in new_rates.items():
        if bank_rates != latest.get(bank):
            return True

    # Detect banks removed from the latest record
    for bank in latest.keys():
        if bank not in new_rates:
            return True

    return False


def prune_entries(entries, cutoff_dt):
    return [
        e
        for e in entries
        if datetime.fromisoformat(e["timestamp"]) > cutoff_dt
    ]


def log_history_if_changed(rates, fetched_at):
    history = load_history()

    changed = rates_changed(rates, history)
    if not changed:
        print("ℹ️  No rate changes detected")
        return

    if "entries" not in history:
        history["entries"] = []

    history["entries"].append({"timestamp": fetched_at, "rates": rates})

    cutoff_dt = datetime.fromisoformat(fetched_at) - timedelta(days=ENTRY_RETENTION_DAYS)
    history["entries"] = prune_entries(history["entries"], cutoff_dt)

    history["latest"] = rates
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Logged rate change to {HISTORY_PATH}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(TZ).isoformat()

    rates = fetch_all_rates()

    payload = {"fetched_at": fetched_at, "rates": rates}
    RATES_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Written {RATES_PATH}")

    log_history_if_changed(rates, fetched_at)


if __name__ == "__main__":
    main()
