import tempfile
import unittest
from pathlib import Path

import update_rates
from fetch_combank import parse_combank_rates
from update_rates import compact_rates, log_history_if_changed


class ComBankParserTests(unittest.TestCase):
    def test_parses_currency_rows_from_generic_table_markup(self):
        html = """
        <html><body>
        <table>
          <tbody>
            <tr>
              <td>US DOLLARS</td>
              <td>330.30</td>
              <td>340.25</td>
              <td>330.44</td>
              <td>340.25</td>
              <td>332.25</td>
              <td>340.25</td>
            </tr>
            <tr>
              <td>EURO</td>
              <td>373.00</td>
              <td>389.00</td>
              <td>374.00</td>
              <td>390.00</td>
              <td>375.00</td>
              <td>391.00</td>
            </tr>
          </tbody>
        </table>
        </body></html>
        """

        rates = parse_combank_rates(html)

        self.assertEqual(rates["USD"], 332.25)
        self.assertEqual(rates["EUR"], 375.0)

    def test_compact_rates_only_keeps_changed_currency_values(self):
        previous = {
            "bank_a": {"USD": 330.0, "EUR": 360.0},
            "bank_b": {"USD": 331.0},
        }
        current = {
            "bank_a": {"USD": 332.25, "EUR": 360.0},
            "bank_b": {"USD": 331.0},
        }

        compacted = compact_rates(current, previous)

        self.assertEqual(compacted["bank_a"], {"USD": 332.25})
        self.assertNotIn("bank_b", compacted)

    def test_compact_rates_returns_empty_when_nothing_changed(self):
        previous = {"bank_a": {"USD": 330.0}}
        current = {"bank_a": {"USD": 330.0}}

        compacted = compact_rates(current, previous)

        self.assertEqual(compacted, {})

    def test_latest_snapshot_keeps_failed_banks_last_known_values(self):
        # A bank that fails to fetch this run (e.g. boc/combank behind a WAF)
        # must not lose its last-known values from history["latest"] just
        # because a different bank changed and triggered a write — otherwise
        # a later "moved since last fetch" comparison for that bank would
        # compare against nothing, or against a stale run from before the
        # bank even existed in the data, instead of its own last fetch.
        with tempfile.TemporaryDirectory() as tmpdir:
            original_path = update_rates.HISTORY_PATH
            update_rates.HISTORY_PATH = Path(tmpdir) / "history.json"
            try:
                history = {
                    "entries": [],
                    "latest": {
                        "boc": {"USD": 320.0},
                        "sampath": {"USD": 300.0},
                    },
                }
                # This run: sampath changed, boc failed to fetch (absent).
                new_rates = {"sampath": {"USD": 301.0}}

                log_history_if_changed(new_rates, "2026-01-01T00:00:00+05:30", history)

                self.assertEqual(history["latest"]["boc"], {"USD": 320.0})
                self.assertEqual(history["latest"]["sampath"], {"USD": 301.0})
            finally:
                update_rates.HISTORY_PATH = original_path


if __name__ == "__main__":
    unittest.main()
