#!/usr/bin/env python3
"""
NDB Bank rate fetcher.
"""

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from html.parser import HTMLParser

from bank_utils import BankFetcher

OUTPUT = Path("output")
OUTPUT.mkdir(parents=True, exist_ok=True)


class NDBRatesParser(HTMLParser):
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
        if tag == "table" and "table" in attrs.get("class", ""):
            # pick the first main table on the page
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


def parse_ndb_rates(html: str) -> dict[str, float]:
    rates = {}
    parser = NDBRatesParser()
    parser.feed(html)

    for row in parser.rows:
        # Expecting columns: 0=Currency,1=Code,2=Currency Buying,3=Currency Selling,
        # 4=DD Buying,5=DD Selling,6=TT Buying,7=TT Selling
        if len(row) < 7:
            continue
        code = row[1].strip()
        if (code == 'CNH'):
            code = 'CNY'  # Convert CNH to CNY
        if not code:
            continue
        tt_buy = row[6].strip() if len(row) > 6 else ""
        if not tt_buy:
            continue
        try:
            rates[code] = float(tt_buy.replace(',', ''))
        except Exception:
            continue
    return rates


class NDBBankFetcher(BankFetcher):
    def __init__(self):
        url = "https://www.ndbbank.com/rates/exchange-rates"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        super().__init__("national_development_bank", url, headers=headers)

    def fetch_all_rates(self) -> dict[str, float]:
        return parse_ndb_rates(self.fetch_text())


def main():
    fetcher = NDBBankFetcher()
    rate = fetcher.fetch_rate()
    payload = {
        "bank": "NDB",
        "rate": rate,
        "fetched_at": datetime.now(ZoneInfo("Asia/Colombo")).isoformat(),
    }
    path = OUTPUT / "ndb.json"
    path.write_text(__import__('json').dumps(payload), encoding="utf-8")
    print(f"✅ NDB rate saved to {path}")


if __name__ == "__main__":
    main()
