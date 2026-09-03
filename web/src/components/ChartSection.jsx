import { resetChartZoom } from "../chart.js";

export default function ChartSection({ loading, entries }) {
  const hasData = !loading && entries.length > 0;

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
      {hasData ? (
        <div className="mb-2 flex items-center justify-between gap-2 text-xs text-slate-400">
          <span>
            <span className="hidden sm:inline">Ctrl+scroll to zoom</span>
            <span className="sm:hidden">Pinch to zoom</span>
            {" · drag to pan"}
          </span>
          <button
            type="button"
            onClick={() => resetChartZoom()}
            className="shrink-0 rounded-full border border-slate-200 px-3 py-1 font-medium text-slate-500 transition hover:border-slate-300 hover:text-slate-700"
          >
            Reset zoom
          </button>
        </div>
      ) : null}
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
