import { h, render } from 'https://unpkg.com/preact@10.11.0?module';
import htm from 'https://unpkg.com/htm@3.1.1?module';
import { bankLabels, sortBankKeys, formatRate, getErrorMessage, setActiveTab } from './utils.js';
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
        <div class="space-y-5">
          <div class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4 sm:px-5 sm:py-5 shadow-sm">
            <p class="text-sm text-slate-600">Last updated <span class="font-semibold text-slate-900">${new Date(fetched).toLocaleString()}</span></p>
          </div>

          <div class="tabs tabs-boxed rounded-3xl bg-slate-50 border border-slate-200 p-1 shadow-sm">
            <button type="button" class="tab tab-active rounded-3xl" data-tab="rates">Rates</button>
            <button type="button" class="tab rounded-3xl" data-tab="charts">Charts</button>
          </div>

          <div id="tab-rates" class="tab-panel">
            <div class="overflow-x-auto rounded-3xl border border-slate-200 bg-white shadow-sm">
              <table class="table-auto border-collapse w-full text-xs sm:text-sm">
                <thead>
                  <tr class="bg-slate-100 text-slate-700">
                    <th class="text-left px-3 py-3 border-r border-slate-200 font-semibold uppercase tracking-[0.08em]">Currency</th>
                    ${bankKeys.map(bank => html`<th class="text-right px-3 py-3 border-slate-200 font-semibold uppercase tracking-[0.08em]">${bankLabels[bank] || bank}</th>`)}
                  </tr>
                </thead>
                <tbody>
                  ${currencyOrder.map(code => {
                    const values = bankKeys.map(bank => rates[bank]?.[code] ?? null);
                    const maxValue = values.filter(v => v != null).length
                      ? Math.max(...values.filter(v => v != null))
                      : null;
                    return html`
                      <tr class="border-b border-slate-200 last:border-b-0 hover:bg-slate-50">
                        <td class="font-semibold px-3 py-3 border-r border-slate-200">${code}</td>
                        ${values.map(value => html`
                          <td class="text-right px-3 py-3 ${value != null && maxValue != null && value === maxValue ? 'bg-green-50 font-semibold text-slate-900' : 'text-slate-700'} border-slate-200">${formatRate(value)}</td>
                        `)}
                      </tr>
                    `;
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div id="tab-charts" class="tab-panel hidden">
            <div class="rounded-3xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
              <div id="chart-container" class="min-h-[320px] w-full">
                <div class="text-center text-slate-500 py-12">
                  <p class="text-lg">📊 Loading chart data...</p>
                </div>
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
