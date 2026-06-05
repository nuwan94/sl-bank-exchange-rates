import { useState, useEffect, useMemo } from "react";
import RateTable from "./components/RateTable.jsx";
import ChartSection from "./components/ChartSection.jsx";
import Footer from "./components/Footer.jsx";
import TabNav from "./components/TabNav.jsx";
import {
  bankLabels,
  sortBankKeys,
  formatRate,
  getErrorMessage,
} from "./utils/index.js";
import { renderUsdChart } from "./chart.js";

const TAB_RATES = "rates";
const TAB_CHARTS = "charts";

export default function App() {
  const [rates, setRates] = useState({});
  const [fetchedAt, setFetchedAt] = useState("unknown");
  const [historyEntries, setHistoryEntries] = useState([]);
  const [activeTab, setActiveTab] = useState(TAB_RATES);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const ratesResponse = await fetch("/data/rates.json", {
          cache: "no-store",
        });
        if (!ratesResponse.ok) throw new Error(await ratesResponse.text());
        const ratesData = await ratesResponse.json();
        setRates(ratesData.rates || {});
        setFetchedAt(ratesData.fetched_at || "unknown");

        const historyResponse = await fetch("/data/history.json", {
          cache: "no-store",
        });
        if (historyResponse.ok) {
          const historyData = await historyResponse.json();
          setHistoryEntries(historyData.entries || []);
        }
      } catch (fetchError) {
        setError(fetchError.message || String(fetchError));
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  useEffect(() => {
    if (activeTab === TAB_CHARTS && historyEntries.length > 0) {
      renderUsdChart(historyEntries, "chart-container");
    }
  }, [activeTab, historyEntries]);

  const bankKeys = useMemo(() => sortBankKeys(Object.keys(rates)), [rates]);
  const currencies = useMemo(
    () =>
      Array.from(
        new Set(bankKeys.flatMap((bank) => Object.keys(rates[bank] || {}))),
      ).sort(),
    [bankKeys, rates],
  );
  const currencyOrder = useMemo(() => {
    const priorityCurrencies = ["USD", "EUR"];
    return [
      ...priorityCurrencies.filter((code) => currencies.includes(code)),
      ...currencies.filter((code) => !priorityCurrencies.includes(code)),
    ];
  }, [currencies]);

  if (error) {
    return <div className="alert alert-error">{getErrorMessage(error)}</div>;
  }

  return (
    <div className="space-y-5">
      <TabNav activeTab={activeTab} onTabChange={setActiveTab} />

      <div className={activeTab !== TAB_RATES ? "hidden" : ""}>
        <RateTable
          rates={rates}
          bankKeys={bankKeys}
          currencyOrder={currencyOrder}
          bankLabels={bankLabels}
          formatRate={formatRate}
          loading={loading}
        />
      </div>

      <div className={activeTab !== TAB_CHARTS ? "hidden" : ""}>
        <ChartSection loading={loading} entries={historyEntries} />
      </div>

      <Footer fetchedAt={fetchedAt} />
    </div>
  );
}
