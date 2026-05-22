import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bank_utils import fetch_hnb_rate

OUTPUT = Path("output")
OUTPUT.mkdir(parents=True, exist_ok=True)


def main():
    rate = fetch_hnb_rate()
    payload = {
        "bank": "HNB",
        "rate": rate,
        "fetched_at": datetime.now(ZoneInfo("Asia/Colombo")).isoformat(),
    }
    path = OUTPUT / "hnb.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    print(f"✅ HNB rate saved to {path}")


if __name__ == "__main__":
    main()
