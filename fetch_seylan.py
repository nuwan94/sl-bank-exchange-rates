#!/usr/bin/env python3
"""
Seylan Bank rate fetcher.
"""

import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from bank_utils import BankFetcher

SEYLAN_URL = "https://www.seylan.lk/exchange-rates"

OUTPUT = Path("output")
OUTPUT.mkdir(parents=True, exist_ok=True)

NAME_TO_CODE = {
    "US DOLLAR": "USD",
    "EURO": "EUR",
    "STERLING POUND": "GBP",
    "YEN": "JPY",
    "AUSTRALIAN DOLLAR": "AUD",
    "CANADIAN DOLLAR": "CAD",
    "SWISS FRANC": "CHF",
    "DANISH KRONE": "DKK",
    "NORWEGIAN KRONE": "NOK",
    "NEW ZEALAND DOLLAR": "NZD",
    "SINGAPORE DOLLAR": "SGD",
    "HONG KONG DOLLAR": "HKD",
    "THAI BAHT": "THB",
    "SAUDI RIYAL": "SAR",
    "QATARI RIAL": "QAR",
    "OMAN RIYAL": "OMR",
    "INDIAN RUPEE": "INR",
    "KUWAITI DINAR": "KWD",
    "BAHRAINI DINAR": "BHD",
    "UAE DIRHAM": "AED",
    "MALAYSIAN RINGGIT": "MYR",
    "CHINESE YUAN": "CNY",
    "SOUTH AFRICAN RAND": "ZAR",
}


def _normalize_currency_code(code: str | None, name: str | None) -> str | None:
    if code:
        normalized = code.strip().upper()
        if normalized in {"CNH"}:
            return "CNY"
        if normalized:
            return normalized
    if not name:
        return None
    normalized = re.sub(r"\s+", " ", name.strip()).upper()
    return NAME_TO_CODE.get(normalized)


def parse_seylan_rates(html: str) -> dict[str, float]:
    rates = {}
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S | re.I)
    for row_html in rows:
        cells = [
            re.sub(r'<[^>]+>', ' ', cell).strip()
            for cell in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row_html, re.S | re.I)
        ]
        if len(cells) < 2:
            continue

        code = _normalize_currency_code(cells[1], cells[0])
        if not code:
            continue

        buy_cell = ""
        for pattern in [
            r'<td[^>]*class="[^"]*tt-value[^"]*"[^>]*>(.*?)</td>',
            r'<td[^>]*class="[^"]*tc-value[^"]*"[^>]*>(.*?)</td>',
            r'<td[^>]*class="[^"]*cn-value[^"]*"[^>]*>(.*?)</td>',
        ]:
            matches = re.findall(pattern, row_html, re.S | re.I)
            if matches:
                buy_cell = re.sub(r'<[^>]+>', ' ', matches[0]).strip()
                break

        if not buy_cell:
            for cell in cells[2:]:
                if re.search(r'\d', cell):
                    buy_cell = cell
                    break

        if not buy_cell:
            continue

        try:
            rates[code] = float(re.sub(r"[^0-9.-]", "", buy_cell))
        except Exception:
            continue
    return rates


class SeylanBankFetcher(BankFetcher):
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        super().__init__("seylan", SEYLAN_URL, headers=headers)

    def fetch_all_rates(self) -> dict[str, float]:
        return parse_seylan_rates(self.fetch_text())


def main():
    fetcher = SeylanBankFetcher()
    rate = fetcher.fetch_rate()
    payload = {
        "bank": "SEYLAN",
        "rate": rate,
        "fetched_at": datetime.now(ZoneInfo("Asia/Colombo")).isoformat(),
    }
    path = OUTPUT / "seylan.json"
    path.write_text(__import__('json').dumps(payload), encoding="utf-8")
    print(f"✅ Seylan rate saved to {path}")


if __name__ == "__main__":
    main()
