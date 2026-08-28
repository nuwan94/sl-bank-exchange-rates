import { useMemo } from "react";

export default function BestRateCard({
  rates,
  bankKeys,
  bankLabels,
  bankSourceUrls,
  formatRate,
  currency = "USD",
}) {
  const best = useMemo(() => {
    let bestBank = null;
    let bestValue = -Infinity;
    for (const bank of bankKeys) {
      const value = rates[bank]?.[currency];
      if (value != null && value > bestValue) {
        bestValue = value;
        bestBank = bank;
      }
    }
    return bestBank ? { bank: bestBank, value: bestValue } : null;
  }, [rates, bankKeys, currency]);

  if (!best) return null;

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-3xl border border-emerald-200 bg-emerald-50 px-5 py-4 shadow-sm">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.08em] text-emerald-700">
          Best {currency} buying rate right now
        </p>
        <p className="text-2xl font-bold text-emerald-900">
          {formatRate(best.value)}{" "}
          <span className="text-base font-medium text-emerald-700">LKR</span>
        </p>
      </div>
      {bankSourceUrls?.[best.bank] ? (
        <a
          href={bankSourceUrls[best.bank]}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
        >
          {bankLabels[best.bank] || best.bank}
        </a>
      ) : (
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white">
          {bankLabels[best.bank] || best.bank}
        </span>
      )}
    </div>
  );
}
