export const currencyNames = {
  USD: 'United States Dollar',
  EUR: 'Euro',
  GBP: 'British Pound',
  JPY: 'Japanese Yen',
  AUD: 'Australian Dollar',
  CAD: 'Canadian Dollar',
  SGD: 'Singapore Dollar',
  HKD: 'Hong Kong Dollar',
  NZD: 'New Zealand Dollar',
  CHF: 'Swiss Franc',
  CNY: 'Chinese Yuan',
  INR: 'Indian Rupee',
  MYR: 'Malaysian Ringgit',
  THB: 'Thai Baht',
  IDR: 'Indonesian Rupiah',
  PHP: 'Philippine Peso',
  VND: 'Vietnamese Dong',
  KRW: 'South Korean Won',
  TWD: 'Taiwan Dollar',
  SEK: 'Swedish Krona',
  NOK: 'Norwegian Krone',
  DKK: 'Danish Krone',
};

export const bankLabels = {
  peoples: 'Peoples Bank',
  sampath: 'Sampath',
  hnb: 'HNB',
  ndb: 'NDB',
};

export function sortBankKeys(keys) {
  const priority = ['peoples', 'sampath', 'hnb'];
  return keys.sort((a, b) => {
    const ia = priority.indexOf(a);
    const ib = priority.indexOf(b);
    if (ia !== -1 && ib !== -1) return ia - ib;
    if (ia !== -1) return -1;
    if (ib !== -1) return 1;
    return a.localeCompare(b);
  });
}

export function hexToRgba(hex, alpha) {
  if (!hex) return `rgba(0,0,0,${alpha})`;
  const h = hex.replace('#', '');
  const full = h.length === 3 ? h.split('').map(c => c + c).join('') : h;
  const bigint = parseInt(full, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export function getCurrencyLabel(code) {
  const name = currencyNames[code] || code;
  return `${name} (${code})`;
}

export function formatRate(value) {
  return value == null ? '—' : Number(value).toFixed(2);
}

export function getErrorMessage(err) {
  if (err == null) return 'Unknown error';
  return typeof err === 'string' ? err : err.message || String(err);
}

export function setActiveTab(root, activeTab) {
  const buttons = root.querySelectorAll('[data-tab]');
  buttons.forEach(button => {
    button.classList.toggle('tab-active', button.dataset.tab === activeTab);
  });
  const panels = root.querySelectorAll('.tab-panel');
  panels.forEach(panel => {
    panel.classList.toggle('hidden', panel.id !== `tab-${activeTab}`);
  });
}
