import { h, render } from 'https://unpkg.com/preact@10.11.0?module';
import htm from 'https://unpkg.com/htm@3.1.1?module';
import { bankLabels, sortBankKeys, getCurrencyLabel, formatRate, getErrorMessage, setActiveTab } from './utils.js';
import { renderUsdChart } from './chart.js';

const html = htm.bind(h);

function App() {
  const root = document.createElement('div');

  async function load() {
    try {
      const res = await fetch('./data/rates.json', { cache: 'no-store' });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      const fetched = data.fetched_at || 'unknown';
      const rates = data.rates || {};

      const bankKeys = sortBankKeys(Object.keys(rates));

      const currencies = Array.from(
        new Set(bankKeys.flatMap(bank => Object.keys(rates[bank] || {})))
      ).sort();

      const priorityCurrencies = ['USD', 'EUR'];
      const currencyOrder = [
        ...priorityCurrencies.filter(c => currencies.includes(c)),
        ...currencies.filter(c => !priorityCurrencies.includes(c)),
      ];

      render(html`
        <div>
          <div class="mb-4 text-sm text-gray-600">
            <strong>Last Updated:</strong> ${new Date(fetched).toLocaleString()}
          </div>

          <div class="tabs tabs-boxed mb-4">
            <button type="button" class="tab tab-active" data-tab="rates">Rates</button>
            <button type="button" class="tab" data-tab="charts">Charts</button>
          </div>

          <div id="tab-rates" class="tab-panel">
            <div class="overflow-x-auto">
              <table class="table table-zebra w-full">
                <thead>
                  <tr class="bg-gray-100">
                    <th class="text-left">Currency</th>
                    ${bankKeys.map(bank => html`<th class="text-right">${bankLabels[bank] || bank}</th>`)}
                  </tr>
                </thead>
                <tbody>
                  ${currencyOrder.map(code => {
                    const values = bankKeys.map(bank => rates[bank]?.[code] ?? null);
                    const maxValue = values.filter(v => v != null).length
                      ? Math.max(...values.filter(v => v != null))
                      : null;
                    return html`
                      <tr>
                        <td class="font-semibold">${getCurrencyLabel(code)}</td>
                        ${values.map(value => html`
                          <td class="text-right ${value != null && maxValue != null && value === maxValue ? 'bg-yellow-100 font-bold text-yellow-900' : ''}">${formatRate(value)}</td>
                        `)}
                      </tr>
                    `;
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div id="tab-charts" class="tab-panel hidden p-6">
            <div id="chart-container" class="w-full">
              <div class="text-center text-gray-500 py-12">
                <p class="text-lg">📊 Loading chart data...</p>
              </div>
            </div>
          </div>
        </div>
      `, root);

      setActiveTab(root, 'rates');

      // Wire tab buttons
      root.querySelectorAll('[data-tab]').forEach(button => {
        button.addEventListener('click', () => setActiveTab(root, button.dataset.tab));
      });

      // Load and render chart after DOM is ready
      setTimeout(() => loadChart(), 100);
    } catch (err) {
      render(html`<div class="alert alert-error">${getErrorMessage(err)}</div>`, root);
    }
  }

  async function loadChart() {
    try {
      const res = await fetch('./data/history.json', { cache: 'no-store' });
      if (!res.ok) {
        document.getElementById('chart-container').innerHTML = '<div class="text-center text-gray-500 py-12"><p class="text-lg">No historical data yet</p></div>';
        return;
      }
      const history = await res.json();
      const entries = history.entries || [];

      if (entries.length === 0) {
        document.getElementById('chart-container').innerHTML = '<div class="text-center text-gray-500 py-12"><p class="text-lg">Waiting for rate changes...</p></div>';
        return;
      }

      renderUsdChart(entries, 'chart-container');
    } catch (err) {
      console.error('Chart error:', err);
      const chartContainer = document.getElementById('chart-container');
      if (chartContainer) {
        chartContainer.innerHTML = '<div class="text-center text-red-500 py-12"><p>' + (err.message || String(err)) + '</p></div>';
      }
    }
  }

  load();
  return root;
}

const app = App();
const mount = document.getElementById('app');
if (mount) mount.replaceWith(app);
