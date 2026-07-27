import unittest

from fetch_combank import parse_combank_rates
from update_rates import compact_rates


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


if __name__ == "__main__":
    unittest.main()
