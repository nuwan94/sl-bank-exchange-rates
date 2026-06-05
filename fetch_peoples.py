#!/usr/bin/env python3
"""
Peoples Bank rate fetcher.
"""

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from bank_utils import BankFetcher, PEOPLES_URL, parse_peoples_rates

OUTPUT = Path("output")
OUTPUT.mkdir(parents=True, exist_ok=True)


class PeoplesBankFetcher(BankFetcher):
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        super().__init__("Peoples Bank", PEOPLES_URL, headers=headers)

    def fetch_all_rates(self) -> dict[str, float]:
        return parse_peoples_rates(self.fetch_text())


def main():
    fetcher = PeoplesBankFetcher()
    rate = fetcher.fetch_rate()
    payload = {
        "bank": "PEOPLES",
        "rate": rate,
        "fetched_at": datetime.now(ZoneInfo("Asia/Colombo")).isoformat(),
    }
    path = OUTPUT / "peoples.json"
    path.write_text(__import__('json').dumps(payload), encoding="utf-8")
    print(f"✅ Peoples Bank rate saved to {path}")


if __name__ == "__main__":
    main()
