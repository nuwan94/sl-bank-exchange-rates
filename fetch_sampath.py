#!/usr/bin/env python3
"""
Sampath Bank rate fetcher.
"""

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from bank_utils import BankFetcher, SAMPATH_API_URL, parse_sampath_rates

OUTPUT = Path("output")
OUTPUT.mkdir(parents=True, exist_ok=True)


class SampathBankFetcher(BankFetcher):
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.sampath.lk/",
            "Accept": "application/json",
        }
        super().__init__("Sampath", SAMPATH_API_URL, headers=headers)

    def fetch_all_rates(self) -> dict[str, float]:
        return parse_sampath_rates(self.fetch_json())


def main():
    fetcher = SampathBankFetcher()
    rate = fetcher.fetch_rate()
    payload = {
        "bank": "SAMPATH",
        "rate": rate,
        "fetched_at": datetime.now(ZoneInfo("Asia/Colombo")).isoformat(),
    }
    path = OUTPUT / "sampath.json"
    path.write_text(__import__('json').dumps(payload), encoding="utf-8")
    print(f"✅ Sampath rate saved to {path}")


if __name__ == "__main__":
    main()
