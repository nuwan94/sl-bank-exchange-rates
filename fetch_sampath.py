import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bank_utils import fetch_sampath_rate

OUTPUT = Path("output")
OUTPUT.mkdir(parents=True, exist_ok=True)


def main():
    rate = fetch_sampath_rate()
    payload = {
        "bank": "SAMPATH",
        "rate": rate,
        "fetched_at": datetime.now(ZoneInfo("Asia/Colombo")).isoformat(),
    }
    path = OUTPUT / "sampath.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    print(f"✅ Sampath rate saved to {path}")


if __name__ == "__main__":
    main()
