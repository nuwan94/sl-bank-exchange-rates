#!/usr/bin/env python3
"""
HNB Bank rate fetcher.
"""

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from bank_utils import BankFetcher

HNB_API_URL = "https://venus.hnb.lk/api/get_exchange_rates_contents_web"


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

OUTPUT = Path("output")
OUTPUT.mkdir(parents=True, exist_ok=True)


class HNBBankFetcher(BankFetcher):
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        super().__init__("hnb", HNB_API_URL, headers=headers)

    def fetch_all_rates(self) -> dict[str, float]:
        return parse_hnb_rates(self.fetch_json())


def main():
    fetcher = HNBBankFetcher()
    rate = fetcher.fetch_rate()
    payload = {
        "bank": "HNB",
        "rate": rate,
        "fetched_at": datetime.now(ZoneInfo("Asia/Colombo")).isoformat(),
    }
    path = OUTPUT / "hnb.json"
    path.write_text(__import__('json').dumps(payload), encoding="utf-8")
    print(f"✅ HNB rate saved to {path}")


if __name__ == "__main__":
    main()
