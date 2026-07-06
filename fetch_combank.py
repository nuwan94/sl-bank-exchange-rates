#!/usr/bin/env python3
"""
Commercial Bank rate fetcher.
"""

import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from bank_utils import BankFetcher

COMBANK_URL = "https://www.combank.lk/rates-tariff#exchange-rates"

OUTPUT = Path("output")
OUTPUT.mkdir(parents=True, exist_ok=True)


def _normalize_currency_code(name: str) -> str | None:
    if not name:
        return None
    normalized = re.sub(r"\s+", " ", name.strip()).upper()
    aliases = {
        "US DOLLARS": "USD",
        "EURO": "EUR",
        "STERLING POUNDS": "GBP",
        "JAPANESE YEN": "JPY",
        "SINGAPORE DOLLARS": "SGD",
        "AUSTRALIAN DOLLARS": "AUD",
        "SWISS FRANCS": "CHF",
        "CHINESE YUAN": "CNY",
        "DANISH KRONER": "DKK",
        "NORWEGIAN KRONE": "NOK",
        "NEW ZEALAND DOLLARS": "NZD",
        "SWEDISH KRONOR": "SEK",
        "THAI BAHT": "THB",
        "UAE DIRHAM": "AED",
        "SAUDI RIYAL": "SAR",
        "QATARI RIAL": "QAR",
        "OMAN RIYAL": "OMR",
        "INDIAN RUPEE": "INR",
        "INDIAN RUPEES": "INR",
        "HONG KONG DOLLAR": "HKD",
        "CANADIAN DOLLARS": "CAD",
        "BAHRAINI DINAR": "BHD",
        "KUWAITI DINAR": "KWD",
        "JORDANIAN DINAR": "JOD",
        "MALAYSIAN RINGGIT": "MYR",
        "SOUTH AFRICAN RAND": "ZAR",
    }
    return aliases.get(normalized)


def parse_combank_rates(html: str) -> dict[str, float]:
    rates = {}
    table_match = re.search(r'<table[^>]*class="with-border"[^>]*>(.*?)</table>', html, re.S | re.I)
    if not table_match:
        return rates

    table_html = table_match.group(1)
    for row_html in re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.S | re.I):
        cells = [
            re.sub(r'<[^>]+>', ' ', cell).strip()
            for cell in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row_html, re.S | re.I)
        ]
        if len(cells) < 7:
            continue

        first_cell = cells[0].strip()
        if not first_cell:
            continue
        if any(char.isdigit() for char in first_cell):
            continue

        code = _normalize_currency_code(first_cell)
        if not code:
            continue

        buy_cell = cells[-2].strip() if len(cells) > 1 else ""
        if buy_cell in {"-", ""}:
            buy_cell = cells[1].strip()
        try:
            rates[code] = float(buy_cell.replace(",", ""))
        except Exception:
            continue
    return rates


class ComBankBankFetcher(BankFetcher):
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        super().__init__("combank", COMBANK_URL, headers=headers)

    def fetch_all_rates(self) -> dict[str, float]:
        return parse_combank_rates(self.fetch_text())


def main():
    fetcher = ComBankBankFetcher()
    rate = fetcher.fetch_rate()
    payload = {
        "bank": "COMBANK",
        "rate": rate,
        "fetched_at": datetime.now(ZoneInfo("Asia/Colombo")).isoformat(),
    }
    path = OUTPUT / "combank.json"
    path.write_text(__import__('json').dumps(payload), encoding="utf-8")
    print(f"✅ ComBank rate saved to {path}")


if __name__ == "__main__":
    main()
