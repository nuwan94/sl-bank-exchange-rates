import json
import re
import urllib.request
import urllib.error
from html.parser import HTMLParser

SAMPATH_API_URL = "https://www.sampath.lk/api/exchange-rates"
HNB_API_URL = "https://venus.hnb.lk/api/get_exchange_rates_contents_web"
PEOPLES_URL = "https://www.peoplesbank.lk/exchange-rates/"

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class BankFetcher:
    def __init__(self, name: str, url: str, headers: dict | None = None):
        self.name = name
        self.url = url
        self.headers = headers or {"User-Agent": DEFAULT_USER_AGENT}
        self._cached_text: str | None = None
        self._cached_json: object | None = None

    def fetch_text(self) -> str:
        if self._cached_text is None:
            req = urllib.request.Request(self.url, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    self._cached_text = response.read().decode("utf-8", errors="ignore")
            except urllib.error.HTTPError as e:
                raise RuntimeError(f"HTTP error fetching {self.name}: {e.code} {e.reason}")
            except urllib.error.URLError as e:
                raise RuntimeError(f"Network error fetching {self.name}: {e.reason}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error fetching {self.name}: {e}")
        return self._cached_text

    def fetch_json(self):
        if self._cached_json is None:
            self._cached_json = json.loads(self.fetch_text())
        return self._cached_json

    def fetch_all_rates(self) -> dict[str, float]:
        raise NotImplementedError

    def fetch_rate(self) -> float:
        rates = self.fetch_all_rates()
        if "USD" in rates and rates["USD"] is not None:
            return rates["USD"]
        raise RuntimeError(f"USD rate not found for {self.name}")


def _extract_rate_from_item(item: dict):
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
    if isinstance(code, str) and code.upper() == "USD":
        return _parse_rate_value(lower)
    return None


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


def fetch_peoples_rate() -> float:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    req = urllib.request.Request(PEOPLES_URL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP error fetching Peoples Bank rate: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching Peoples Bank rate: {e.reason}")

    rates = parse_peoples_rates(html)
    if "USD" in rates:
        return rates["USD"]
    raise RuntimeError("USD TT Buying rate not found in Peoples Bank HTML response.")
