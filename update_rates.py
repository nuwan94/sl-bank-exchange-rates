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

    # also include parsed USD rates using existing helpers
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

    payload = {
        "fetched_at": fetched_at,
        "sources": {
            "sampath": sampath_raw,
            "hnb": hnb_raw,
        },
        "parsed": parsed,
    }

    path = out_dir / "rates.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Written {path}")


if __name__ == "__main__":
    main()
