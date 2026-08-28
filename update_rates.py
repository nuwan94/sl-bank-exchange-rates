import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from fetch_boc import BOCBankFetcher
from fetch_combank import ComBankBankFetcher
from fetch_hnb import HNBBankFetcher
from fetch_ndb import NDBBankFetcher
from fetch_peoples import PeoplesBankFetcher
from fetch_sampath import SampathBankFetcher
from fetch_seylan import SeylanBankFetcher


TZ = ZoneInfo("Asia/Colombo")
OUT_DIR = Path("web/public/data")
RATES_PATH = OUT_DIR / "rates.json"
HISTORY_PATH = OUT_DIR / "history.json"
DEBUG_ERRORS_PATH = OUT_DIR / "debug_errors.json"
ENTRY_RETENTION_DAYS = 30


def fetch_all_rates():
    fetchers = [
        SampathBankFetcher(),
        HNBBankFetcher(),
        PeoplesBankFetcher(),
        NDBBankFetcher(),
        BOCBankFetcher(),
        ComBankBankFetcher(),
        SeylanBankFetcher(),
    ]

    rates = {}
    errors = {}
    for fetcher in fetchers:
        try:
            bank_rates = fetcher.fetch_all_rates()
            if not bank_rates:
                # fetch_text() succeeded (no HTTP/browser exception) but the
                # page didn't contain the expected table — e.g. a WAF
                # challenge/interstitial rendered instead of the real page.
                # Treat this as a failure rather than silently publishing an
                # empty bank entry that looks "present" with no data.
                text = getattr(fetcher, "_cached_text", None) or ""
                preview = text[:300].replace("\n", " ")
                raise RuntimeError(
                    f"No rates parsed (fetched {len(text)} chars, preview: {preview!r})"
                )
            rates[fetcher.name] = bank_rates
        except Exception as e:
            print(f"⚠️  Could not fetch {fetcher.name} rates: {e}")
            errors[fetcher.name] = str(e)

    return rates, errors


def load_history():
    if not HISTORY_PATH.exists():
        return {}

    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠️  Could not read history: {e}")
        return {}


def compact_rates(rates, previous_rates):
    if not previous_rates:
        return rates

    compacted = {}
    for bank, bank_rates in rates.items():
        previous_bank_rates = previous_rates.get(bank)
        if not isinstance(previous_bank_rates, dict):
            compacted[bank] = bank_rates
            continue

        changed_rates = {}
        for currency, value in bank_rates.items():
            previous_value = previous_bank_rates.get(currency)
            if previous_value != value:
                changed_rates[currency] = value

        if changed_rates:
            compacted[bank] = changed_rates

    return compacted


def rates_changed(new_rates, history):
    latest = history.get("latest")
    if latest is None:
        return True

    compacted_rates = compact_rates(new_rates, latest)
    if compacted_rates != {}:
        return True

    # Detect banks removed from the latest record
    for bank in latest.keys():
        if bank not in new_rates:
            return True

    return False


def prune_entries(entries, cutoff_dt):
    return [
        e
        for e in entries
        if datetime.fromisoformat(e["timestamp"]) > cutoff_dt
    ]


def log_history_if_changed(rates, fetched_at, history):
    if "entries" not in history:
        history["entries"] = []

    previous_rates = None
    if history["entries"]:
        previous_rates = history["entries"][-1].get("rates", {})
    else:
        previous_rates = history.get("latest")

    compacted_rates = compact_rates(rates, previous_rates or {}) if previous_rates is not None else rates
    if not history["entries"]:
        compacted_rates = rates

    changed = bool(compacted_rates)
    if not changed and history["entries"]:
        print("ℹ️  No rate changes detected")
        return

    history["entries"].append({"timestamp": fetched_at, "rates": compacted_rates})

    cutoff_dt = datetime.fromisoformat(fetched_at) - timedelta(days=ENTRY_RETENTION_DAYS)
    history["entries"] = prune_entries(history["entries"], cutoff_dt)

    history["latest"] = rates
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Logged rate change to {HISTORY_PATH}")


def write_debug_errors(errors, fetched_at):
    if not errors:
        if DEBUG_ERRORS_PATH.exists():
            DEBUG_ERRORS_PATH.unlink()
        return
    payload = {"fetched_at": fetched_at, "errors": errors}
    DEBUG_ERRORS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"⚠️  Wrote fetch errors to {DEBUG_ERRORS_PATH}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(TZ).isoformat()

    rates, errors = fetch_all_rates()

    history = load_history()
    # The full snapshot as of the previous run — before this run's data
    # overwrites it below. Exposed so the UI can show "moved since last
    # fetch" indicators without the client having to reconstruct it from
    # the (deliberately sparse) history entries.
    previous_rates = history.get("latest")

    payload = {"fetched_at": fetched_at, "rates": rates, "previous_rates": previous_rates}
    RATES_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Written {RATES_PATH}")

    write_debug_errors(errors, fetched_at)
    log_history_if_changed(rates, fetched_at, history)


if __name__ == "__main__":
    main()
