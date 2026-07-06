import { useState, useEffect } from "react";
import { getCurrencyName } from "../utils/index.js";

export default function RateTable({
  rates,
  bankKeys,
  currencyOrder,
  bankLabels,
  bankSourceUrls,
  formatRate,
  loading,
}) {

  const [searchQuery, setSearchQuery] = useState('');
  const [currencies, setCurrencies] = useState([]);

  useEffect(() => {
      if (currencyOrder.length > 0) {
        const currencyWithNames = currencyOrder.map((code) => ({
          code,
          name: getCurrencyName(code),
        }));
        setCurrencies(currencyWithNames);
      }
  }, [currencyOrder]);

  const handleSearch = (e) => {
    setSearchQuery(e.target.value.toLowerCase());
  };

  if (loading) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm text-center text-slate-500">
        Loading rates...
      </div>
    );
  }



  return (
    <div className="overflow-x-auto border border-slate-200 bg-white shadow-sm">

      {/* input group search */}
      <div className="p-2 border-b border-slate-200">

      <input
        type="text"
        placeholder="Filter currency"
        className="w-full px-4 py-3 border-b focus:outline-none"
        onChange={handleSearch}
        value={searchQuery || ''}
      />
      </div>
      

      <table className="table-auto border-collapse w-full text-xs sm:text-sm">
        <thead>
          <tr className="bg-slate-100 text-slate-700">
            <th className="text-left px-3 py-3 border-r border-slate-200 font-semibold uppercase tracking-[0.08em]">
              Currency
            </th>
            {bankKeys.map((bank) => (
              <th
                key={bank}
                className="text-right px-3 py-3 border-slate-200 font-semibold uppercase tracking-[0.08em]"
              >
                <div className="flex items-center justify-end gap-1">
                  <span>{bankLabels[bank] || bank}</span>
                  {bankSourceUrls?.[bank] ? (
                    <a
                      href={bankSourceUrls[bank]}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex text-slate-500 transition hover:text-slate-900"
                      aria-label={`Open ${bankLabels[bank] || bank} exchange rate page`}
                      title={`Open ${bankLabels[bank] || bank} exchange rate page`}
                    >
                      <svg
                        className="h-3.5 w-3.5"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        aria-hidden="true"
                      >
                        <path d="M7 17L17 7" />
                        <path d="M7 7h10v10" />
                      </svg>
                    </a>
                  ) : null}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {currencies.map((currency) => {
            const values = bankKeys.map((bank) => rates[bank]?.[currency.code] ?? null);
            const maxValue = values.filter((v) => v != null).length
              ? Math.max(...values.filter((v) => v != null))
              : null;
            return (
              <tr
                key={currency.code}
                className="border-b border-slate-200 last:border-b-0 hover:bg-slate-50"
                style={{ display: currency.code.toLowerCase().includes(searchQuery) || currency.name.toLowerCase().includes(searchQuery) ? '' : 'none' }}
              >
                <td className="font-semibold px-3 py-3 border-r border-slate-200">
                  {currency.code}
                  <div className="text-xs text-slate-500">{currency.name}</div>
                </td>
                {values.map((value, index) => (
                  <td
                    key={bankKeys[index]}
                    className={`text-right px-3 py-3 border-slate-200 ${
                      value != null && maxValue != null && value === maxValue
                        ? "bg-green-50 font-semibold text-slate-900"
                        : "text-slate-700"
                    }`}
                  >
                    {formatRate(value)}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
