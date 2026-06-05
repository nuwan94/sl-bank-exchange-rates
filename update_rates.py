import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from fetch_sampath import SampathBankFetcher
from fetch_hnb import HNBBankFetcher
from fetch_peoples import PeoplesBankFetcher
from fetch_ndb import NDBBankFetcher
def main():
    out_dir = Path("web/data")
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(ZoneInfo("Asia/Colombo"))
    fetched_at = now.isoformat()

    sampath_fetcher = SampathBankFetcher()
    hnb_fetcher = HNBBankFetcher()
    peoples_fetcher = PeoplesBankFetcher()
    ndb_fetcher = NDBBankFetcher()

    sampath_rates = sampath_fetcher.fetch_all_rates()
    hnb_rates = hnb_fetcher.fetch_all_rates()
    peoples_rates = peoples_fetcher.fetch_all_rates()
    ndb_rates = ndb_fetcher.fetch_all_rates()

    parsed = {
        "sampath": sampath_rates.get("USD"),
        "hnb": hnb_rates.get("USD"),
        "peoples": peoples_rates.get("USD"),
        "ndb": ndb_rates.get("USD"),
    }

    rates = {
        "sampath": sampath_rates,
        "hnb": hnb_rates,
        "peoples": peoples_rates,
        "ndb": ndb_rates,
    }

    payload = {
        "fetched_at": fetched_at,
        "sources": {
            "sampath": sampath_fetcher.fetch_json(),
            "hnb": hnb_fetcher.fetch_json(),
            "peoples": peoples_fetcher.fetch_text(),
        },
        "parsed": parsed,
        "rates": rates,
    }

    path = out_dir / "rates.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Written {path}")

    # Track historical changes
    history_path = out_dir / "history.json"
    history = {}
    if history_path.exists():
        try:
            history = json.loads(history_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"⚠️  Could not read history: {e}")

    # Check if rates changed and log new entry
    changed = False
    if "latest" not in history:
        history["latest"] = rates
        changed = True
    else:
        latest = history["latest"]
        # Check if any bank or currency rate changed
        for bank, bank_rates in rates.items():
            if bank_rates != latest.get(bank):
                changed = True
                break
        if not changed:
            # Also detect banks removed from the latest record
            for bank in latest.keys():
                if bank not in rates:
                    changed = True
                    break

    if changed:
        if "entries" not in history:
            history["entries"] = []
        
        history["entries"].append({
            "timestamp": fetched_at,
            "rates": rates,
        })
        
        # Keep only last 7 days of entries
        cutoff_time = datetime.fromisoformat(fetched_at).timestamp() - (7 * 24 * 3600)
        history["entries"] = [
            e for e in history["entries"]
            if datetime.fromisoformat(e["timestamp"]).timestamp() > cutoff_time
        ]
        
        history["latest"] = rates
        history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ Logged rate change to {history_path}")
    else:
        print("ℹ️  No rate changes detected")


if __name__ == "__main__":
    main()
