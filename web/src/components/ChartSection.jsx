export default function ChartSection({ loading, entries }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
      <div id="chart-container" className="min-h-[320px] w-full">
        {loading ? (
          <div className="text-center text-slate-500 py-12">
            <p className="text-lg">📊 Loading chart data...</p>
          </div>
        ) : entries.length === 0 ? (
          <div className="text-center text-slate-500 py-12">
            <p className="text-lg">Waiting for rate changes...</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}
