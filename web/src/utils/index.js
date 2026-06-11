export const bankLabels = {
  peoples: "Peoples",
  sampath: "Sampath",
  hnb: "HNB",
  ndb: "NDB",
};

export function sortBankKeys(keys) {
  const priority = ["peoples", "sampath", "hnb"];
  return keys.sort((a, b) => {
    const ia = priority.indexOf(a);
    const ib = priority.indexOf(b);
    if (ia !== -1 && ib !== -1) return ia - ib;
    if (ia !== -1) return -1;
    if (ib !== -1) return 1;
    return a.localeCompare(b);
  });
}

export function formatRate(value) {
  return value == null ? "—" : Number(value).toFixed(2);
}

export function getErrorMessage(err) {
  if (err == null) return "Unknown error";
  return typeof err === "string" ? err : err.message || String(err);
}

export function hexToRgba(hex, alpha) {
  if (!hex) return `rgba(0,0,0,${alpha})`;
  const cleaned = hex.replace("#", "");
  const full =
    cleaned.length === 3
      ? cleaned
          .split("")
          .map((char) => char + char)
          .join("")
      : cleaned;
  const intValue = parseInt(full, 16);
  const r = (intValue >> 16) & 255;
  const g = (intValue >> 8) & 255;
  const b = intValue & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export function setActiveTab(root, activeTab) {
  const buttons = root.querySelectorAll("[data-tab]");
  buttons.forEach((button) => {
    button.classList.toggle("tab-active", button.dataset.tab === activeTab);
  });
  const panels = root.querySelectorAll(".tab-panel");
  panels.forEach((panel) => {
    panel.classList.toggle("hidden", panel.id !== `tab-${activeTab}`);
  });
}

export function getCurrencyName(code) {
  const currencyNames = {
    USD: "US Dollar",
    EUR: "Euro",
    GBP: "British Pound",
    JPY: "Japanese Yen",
    AUD: "Australian Dollar",
    CAD: "Canadian Dollar",
    CHF: "Swiss Franc",
    CNY: "Chinese Yuan",
    SEK: "Swedish Krona",
    NZD: "New Zealand Dollar",
    SGD: "Singapore Dollar",
    HKD: "Hong Kong Dollar",
    THB: "Thai Baht",
    SAR: "Saudi Riyal",
    QAR: "Qatari Riyal",
    OMR: "Omani Rial",
    INR: "Indian Rupee",
    KWD: "Kuwaiti Dinar",
    BHD: "Bahraini Dinar",
    AED: "United Arab Emirates Dirham",
    DKK: "Danish Krone",
    JOD: "Jordanian Dinar",
    MYR: "Malaysian Ringgit",
    NOK: "Norwegian Krone",
    ZAR: "South African Rand",
  };
  return currencyNames[code] || "";
}
