import unittest

from fetch_combank import parse_combank_rates


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


if __name__ == "__main__":
    unittest.main()
