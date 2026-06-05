#!/usr/bin/env python3
"""
Peoples Bank rate fetcher.
"""

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from bank_utils import BankFetcher
from html.parser import HTMLParser

PEOPLES_URL = "https://www.peoplesbank.lk/exchange-rates/"


class PeoplesRatesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_tbody = False
        self.in_row = False
        self.in_cell = False
        self.cells = []
        self.current = ""
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table" and "table-striped" in attrs.get("class", ""):
            self.in_table = True
        if self.in_table and tag == "tbody":
            self.in_tbody = True
        if self.in_tbody and tag == "tr":
            self.in_row = True
            self.cells = []
        if self.in_row and tag in ("td", "th"):
            self.in_cell = True
            self.current = ""

    def handle_data(self, data):
        if self.in_cell:
            self.current += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.in_cell:
            self.cells.append(self.current.strip())
            self.in_cell = False
        if tag == "tr" and self.in_row:
            if self.cells:
                self.rows.append(self.cells)
            self.in_row = False
        if tag == "tbody":
            self.in_tbody = False
        if tag == "table":
            self.in_table = False


def parse_peoples_rates(html: str) -> dict[str, float]:
    rates = {}
    parser = PeoplesRatesParser()
    parser.feed(html)

    names = {
        "US Dollars": "USD",
        "Japanese Yen": "JPY",
        "British Pound Sterling": "GBP",
        "Euro": "EUR",
        "Australian Dollar": "AUD",
        "Thai Baht": "THB",
        "Singapore Dollar": "SGD",
        "Swedish Krona": "SEK",
        "Saudi Riyal": "SAR",
        "Qatari Rial": "QAR",
        "Omani Rial": "OMR",
        "New Zealand Dollar": "NZD",
        "Norwegian Krone": "NOK",
        "Malaysian Ringgit": "MYR",
        "Kuwaiti Dinar": "KWD",
        "Jordanian Dinar": "JOD",
        "Indian Rupee": "INR",
        "Hong Kong Dollar": "HKD",
        "Danish Krone": "DKK",
        "Chinese Yuan": "CNY",
        "Swiss Franc": "CHF",
        "Canadian Dollar": "CAD",
        "Bahraini Dinar": "BHD",
        "UAE Dirham": "AED",
    }

    for row in parser.rows:
        if len(row) < 8:
            continue
        name = row[1].strip()
        if not name:
            continue
        code = names.get(name)
        if not code:
            continue
        tt_buy = row[6].strip() if len(row) > 6 else ""
        if not tt_buy or tt_buy == "0.0000":
            tt_buy = row[2].strip() if len(row) > 2 else ""
        try:
            rates[code] = float(tt_buy)
        except Exception:
            continue
    return rates

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
