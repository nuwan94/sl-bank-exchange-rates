import { sortBankKeys, hexToRgba, bankLabels } from './utils.js';

export function renderUsdChart(entries, containerId = 'chart-container') {
  const container = document.getElementById(containerId);
  if (!container) return;

  const timestamps = entries.map(e => {
    const d = new Date(e.timestamp);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  });

  const allBankKeys = sortBankKeys(Array.from(new Set(entries.flatMap(e => Object.keys(e.rates || {})))));

  const palette = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316', '#64748b', '#0ea5e9'];

  const datasets = allBankKeys.map((bank, idx) => {
    const data = entries.map(e => e.rates?.[bank]?.USD ?? null);
    const color = palette[idx % palette.length];
    return {
      label: `${bankLabels[bank] || bank} USD`,
      data,
      borderColor: color,
      backgroundColor: hexToRgba(color, 0.08),
      tension: 0.3,
      fill: true,
    };
  });

  const canvasId = 'rateChart';
  container.innerHTML = `<canvas id="${canvasId}"></canvas>`;
  const ctx = document.getElementById(canvasId).getContext('2d');

  // Destroy previous chart if any
  if (ctx._chartInstance) {
    try { ctx._chartInstance.destroy(); } catch (e) { /* ignore */ }
  }

  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: timestamps,
      datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: true },
        title: { display: true, text: 'USD Exchange Rate Trend (Last 7 days)' },
      },
      scales: { y: { beginAtZero: false } },
    },
  });

  // store instance for later cleanup
  ctx._chartInstance = chart;
}
