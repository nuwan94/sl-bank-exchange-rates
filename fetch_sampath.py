#!/usr/bin/env python3
"""
Sampath Bank rate fetcher.
"""

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from bank_utils import BankFetcher

SAMPATH_API_URL = "https://www.sampath.lk/api/exchange-rates"


def _parse_rate_value(lower: dict):
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
        return None
    try:
        return float(str(rate_val).strip())
    except Exception:
        return None


def extract_rate_item(item: dict):
    if not isinstance(item, dict):
        return None
    lower = {(k or "").lower(): v for k, v in item.items()}
    code = (
        lower.get("currency")
        or lower.get("currencycode")
        or lower.get("currcode")
        or lower.get("curr")
        or ""
    )
    if not isinstance(code, str):
        return None
    code = code.strip().upper()
    if not code:
        return None
    rate = _parse_rate_value(lower)
    if rate is None:
        return None
    return code, rate


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
        parsed = extract_rate_item(item)
        if parsed is None:
            continue
        code, rate = parsed
        rates[code] = rate
    return rates

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
