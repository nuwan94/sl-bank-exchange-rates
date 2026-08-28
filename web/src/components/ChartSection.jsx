export default function ChartSection({ loading, entries }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
      <div id="chart-container" className="h-[340px] w-full sm:h-[420px]">
        {loading ? (
          <div className="flex h-full items-center justify-center text-center text-slate-500">
            <p className="text-lg">📊 Loading chart data...</p>
          </div>
        ) : entries.length === 0 ? (
          <div className="flex h-full items-center justify-center text-center text-slate-500">
            <p className="text-lg">Waiting for rate changes...</p>
          </div>
        ) : null}
      </div>
      <p className="mt-2 text-center text-xs text-slate-400 sm:hidden">
        Tap a bank in the legend to show or hide it
      </p>
    </div>
  );
}
