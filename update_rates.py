import json
import urllib.request
import urllib.error
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from bank_utils import fetch_sampath_rate, fetch_hnb_rate

SAMPATH_API_URL = "https://www.sampath.lk/api/exchange-rates"
HNB_API_URL = "https://venus.hnb.lk/api/get_exchange_rates_contents_web"


def fetch_raw(url: str, headers: dict | None = None):
    headers = headers or {"User-Agent": "python-urllib/3"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        print(f"HTTP error fetching {url}: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        print(f"Network error fetching {url}: {e.reason}")
    except Exception as e:
        print(f"Unexpected error fetching {url}: {e}")
    return None


def parse_sampath_rates(data):
    rates = {}
    if isinstance(data, dict):
        items = data.get("data") or data.get("rates") or data.get("exchangeRates") or []
    else:
        items = data or []

    if not isinstance(items, list):
        return rates

    for item in items:
        if not isinstance(item, dict):
            continue

        lower = { (k or "").lower(): v for k, v in item.items() }
        code = (
            lower.get("currency")
            or lower.get("currencycode")
            or lower.get("currcode")
            or lower.get("curr")
            or ""
        )
        if not isinstance(code, str):
            continue
        code = code.strip().upper()
        if not code:
            continue

        rate_val = (
            lower.get("ttbuy")
            or lower.get("ttbuying")
            or lower.get("tt_buying")
            or lower.get("buying")
            or lower.get("buyingrate")
            or lower.get("ttsel")
            or lower.get("sellingrate")
        )
        if rate_val is None:
            continue
        try:
            rates[code] = float(str(rate_val).strip())
        except Exception:
            continue
    return rates


def parse_hnb_rates(data):
    rates = {}
    if not isinstance(data, list):
        return rates

    for item in data:
        if not isinstance(item, dict):
            continue
        code = item.get("currencyCode")
        rate_val = item.get("buyingRate")
        if not isinstance(code, str) or rate_val is None:
            continue
        try:
            rates[code.strip().upper()] = float(rate_val)
        except Exception:
            continue
    return rates


def main():
    out_dir = Path("web/data")
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(ZoneInfo("Asia/Colombo"))
    fetched_at = now.isoformat()

    sampath_raw = fetch_raw(SAMPATH_API_URL, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.sampath.lk/",
        "Accept": "application/json",
    })
    hnb_raw = fetch_raw(HNB_API_URL, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })

    parsed = {}
    try:
        parsed["sampath"] = fetch_sampath_rate()
    except Exception as e:
        parsed["sampath"] = None
        print(f"Could not parse Sampath USD rate: {e}")

    try:
        parsed["hnb"] = fetch_hnb_rate()
    except Exception as e:
        parsed["hnb"] = None
        print(f"Could not parse HNB USD rate: {e}")

    rates = {
        "sampath": parse_sampath_rates(sampath_raw),
        "hnb": parse_hnb_rates(hnb_raw),
    }

    payload = {
        "fetched_at": fetched_at,
        "sources": {
            "sampath": sampath_raw,
            "hnb": hnb_raw,
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
        # Check if any rate changed
        for bank in ["sampath", "hnb"]:
            if rates.get(bank) != latest.get(bank):
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
