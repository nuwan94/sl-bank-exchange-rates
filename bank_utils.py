import json
import urllib.request
import urllib.error

SAMPATH_API_URL = "https://www.sampath.lk/api/exchange-rates"
HNB_API_URL = "https://venus.hnb.lk/api/get_exchange_rates_contents_web"


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


def fetch_sampath_rate() -> float:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.sampath.lk/",
        "Accept": "application/json",
    }
    req = urllib.request.Request(SAMPATH_API_URL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP error fetching Sampath rate: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching Sampath rate: {e.reason}")

    if isinstance(data, dict):
        rates = data.get("data") or data.get("rates") or data.get("exchangeRates") or []
    else:
        rates = data

    if isinstance(rates, list):
        for item in rates:
            rate = _extract_rate_from_item(item)
            if rate is not None:
                return rate

    raise RuntimeError("USD TT Buying rate not found in Sampath API response.")


def fetch_hnb_rate() -> float:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    req = urllib.request.Request(HNB_API_URL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP error fetching HNB rate: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching HNB rate: {e.reason}")

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("currencyCode") == "USD":
                rate = item.get("buyingRate")
                if rate is not None:
                    return float(rate)

    raise RuntimeError("USD buying rate not found in HNB API response.")
