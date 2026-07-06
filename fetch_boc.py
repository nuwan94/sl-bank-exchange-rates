#!/usr/bin/env python3
"""
BOC Bank rate fetcher.
"""

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from html.parser import HTMLParser

from bank_utils import BankFetcher

BOC_URL = "https://www.boc.lk/rates-tariff"

OUTPUT = Path("output")
OUTPUT.mkdir(parents=True, exist_ok=True)


class BOCRatesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_tbody = False
        self.in_row = False
        self.in_cell = False
        self.current = ""
        self.cells = []
        self.rows = []
        self._skip_table = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table" and "light-table" in attrs.get("class", ""):
            self.in_table = True
            self._skip_table = False
        elif tag == "table" and self.in_table:
            self._skip_table = True

        if self.in_table and not self._skip_table and tag == "tbody":
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
        if tag == "tbody" and self.in_tbody:
            self.in_tbody = False
        if tag == "table" and self.in_table:
            self.in_table = False
            self._skip_table = False


def parse_boc_rates(html: str) -> dict[str, float]:
    rates = {}
    parser = BOCRatesParser()
    parser.feed(html)

    for row in parser.rows:
        if len(row) < 7:
            continue
        code = row[0].strip().upper()
        if not code:
            continue
        # Use the Telegraphic/PFCA/BFCA buying rate when available; fallback to the first buying rate.
        buy_cell = row[5].strip() if len(row) > 5 else ""
        if buy_cell in {"-", ""}:
            buy_cell = row[1].strip() if len(row) > 1 else ""
        try:
            rates[code] = float(buy_cell.replace(",", ""))
        except Exception:
            continue
    return rates


class BOCBankFetcher(BankFetcher):
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        super().__init__("boc", BOC_URL, headers=headers)

    def fetch_all_rates(self) -> dict[str, float]:
        return parse_boc_rates(self.fetch_text())


def main():
    fetcher = BOCBankFetcher()
    rate = fetcher.fetch_rate()
    payload = {
        "bank": "BOC",
        "rate": rate,
        "fetched_at": datetime.now(ZoneInfo("Asia/Colombo")).isoformat(),
    }
    path = OUTPUT / "boc.json"
    path.write_text(__import__('json').dumps(payload), encoding="utf-8")
    print(f"✅ BOC rate saved to {path}")


if __name__ == "__main__":
    main()
