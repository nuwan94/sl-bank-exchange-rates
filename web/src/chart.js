import Chart from "chart.js/auto";
import zoomPlugin from "chartjs-plugin-zoom";
import { sortBankKeys, bankLabels, bankColors } from "./utils/index.js";

Chart.register(zoomPlugin);

const FALLBACK_COLOR = "#52514e"; // secondary ink — only if an unknown bank shows up
const CANVAS_ID = "rateChart";
const Y_AXIS_PADDING = 5;

function getChartInstance() {
  const canvas = document.getElementById(CANVAS_ID);
  return canvas?.getContext("2d")?._chartInstance ?? null;
}

// Zooming/panning the x-axis leaves the y-axis fixed to the full dataset's
// range by default, which makes a zoomed-in window look artificially flat.
// Recompute y bounds from whatever's actually visible instead.
function rescaleYToVisibleWindow(chart, dataLength) {
  const xScale = chart.scales.x;
  if (!xScale) return;
  const startIdx = Math.max(0, Math.floor(xScale.min ?? 0));
  const endIdx = Math.min(dataLength - 1, Math.ceil(xScale.max ?? dataLength - 1));

  let min = Infinity;
  let max = -Infinity;
  for (const dataset of chart.data.datasets) {
    const data = dataset.data;
    // A series only carries a point where its rate changed (spanGaps), so
    // the line may be flat through this whole window with no literal point
    // in it — carry forward whatever value was in effect entering the window.
    let carried = null;
    for (let i = 0; i <= startIdx; i++) {
      if (typeof data[i] === "number") carried = data[i];
    }
    if (carried != null) {
      min = Math.min(min, carried);
      max = Math.max(max, carried);
    }
    for (let i = startIdx; i <= endIdx; i++) {
      const value = data[i];
      if (typeof value === "number" && !Number.isNaN(value)) {
        min = Math.min(min, value);
        max = Math.max(max, value);
      }
    }
  }
  if (!Number.isFinite(min) || !Number.isFinite(max)) return;

  chart.options.scales.y.min = Math.max(0, min - Y_AXIS_PADDING);
  chart.options.scales.y.max = max + Y_AXIS_PADDING;
  chart.update("none");
}

/** Restores the full time range and the matching y-axis scale. */
export function resetChartZoom() {
  const chart = getChartInstance();
  if (!chart) return;
  chart.resetZoom();
  rescaleYToVisibleWindow(chart, chart.data.labels.length);
}

function formatTimestamp(timestamp) {
  const d = new Date(timestamp);
  const [datePart, timePart] = d
    .toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
    .split(", ");
  return [datePart, timePart];
}

export function renderUsdChart(entries, containerId = "chart-container") {
  const container = document.getElementById(containerId);
  if (!container) return;

  const isMobile = container.clientWidth < 480;
  const labels = entries.map((e) => formatTimestamp(e.timestamp));

  const allBankKeys = sortBankKeys(
    Array.from(new Set(entries.flatMap((e) => Object.keys(e.rates || {})))),
  );

  const datasets = allBankKeys.map((bank) => {
    let lastValue = null;
    let lastValidIndex = -1;
    const data = entries.map((e, i) => {
      const value = e.rates?.[bank]?.USD ?? null;
      if (value == null) return null;
      if (lastValue == null || value !== lastValue) {
        lastValue = value;
        lastValidIndex = i;
        return value;
      }
      return null;
    });
    // The line only carries a point where the rate actually changed, so
    // trailing nulls (no change since) would hide the true last value —
    // carry it forward to the final index so the end-marker below has
    // something to land on.
    if (lastValidIndex !== -1 && lastValidIndex !== data.length - 1) {
      data[data.length - 1] = lastValue;
      lastValidIndex = data.length - 1;
    }

    const color = bankColors[bank] || FALLBACK_COLOR;

    // Only the current-rate point gets a marker — labeling every point is
    // noise, so the line ends in a small dot instead (see dataviz marks spec).
    const pointRadius = data.map((_, i) => (i === lastValidIndex ? 4 : 0));
    const pointHoverRadius = data.map(() => 5);

    return {
      label: bankLabels[bank] || bank,
      data,
      borderColor: color,
      backgroundColor: color,
      borderWidth: 2,
      tension: 0.25,
      fill: false, // area fills from 7 overlapping series would just blend into mud
      spanGaps: true,
      pointRadius,
      pointHoverRadius,
      pointBackgroundColor: color,
      pointBorderColor: "#fcfcfb",
      pointBorderWidth: 2,
      pointHitRadius: 12, // bigger-than-the-mark touch target
    };
  });

  container.innerHTML = `<canvas id="${CANVAS_ID}"></canvas>`;
  const ctx = document.getElementById(CANVAS_ID).getContext("2d");

  if (ctx._chartInstance) {
    try {
      ctx._chartInstance.destroy();
    } catch (e) {
      /* ignore */
    }
  }

  const numericValues = datasets.flatMap((dataset) =>
    dataset.data.filter(
      (value) => typeof value === "number" && !Number.isNaN(value),
    ),
  );
  const minValue = numericValues.length ? Math.min(...numericValues) : null;
  const maxValue = numericValues.length ? Math.max(...numericValues) : null;
  const yMin =
    minValue != null ? Math.max(0, minValue - Y_AXIS_PADDING) : undefined;
  const yMax = maxValue != null ? maxValue + Y_AXIS_PADDING : undefined;
  const dataLength = labels.length;

  const chart = new Chart(ctx, {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false, // height is set by the container's CSS, not a fixed ratio
      interaction: {
        mode: "index", // hovering/tapping anywhere on the X shows every series at once
        intersect: false,
      },
      plugins: {
        legend: {
          display: true,
          position: "bottom",
          labels: {
            usePointStyle: true,
            pointStyle: "line",
            boxWidth: 24,
            padding: 12,
            font: { size: 11 },
            color: "#52514e",
          },
        },
        title: {
          display: true,
          text: "USD Exchange Rate Trend (Last 30 days)",
          color: "#0b0b0b",
          font: { size: isMobile ? 13 : 15, weight: "600" },
          padding: { bottom: 12 },
        },
        tooltip: {
          usePointStyle: true,
          boxPadding: 4,
          padding: 10,
          titleColor: "#ffffff",
          bodyColor: "#ffffff",
          callbacks: {
            // Values lead, labels follow: "324.19  Peoples" not "Peoples: 324.19"
            label: (item) =>
              `${item.formattedValue}  ${item.dataset.label}`,
          },
        },
        zoom: {
          limits: {
            // Index bounds on the category x-axis — can't pan/zoom past
            // the actual data, and can't zoom in past a few points.
            x: { min: 0, max: dataLength - 1, minRange: 3 },
          },
          pan: {
            enabled: true,
            mode: "x",
            onPanComplete: ({ chart }) => rescaleYToVisibleWindow(chart, dataLength),
          },
          zoom: {
            wheel: { enabled: true, modifierKey: "ctrl" }, // plain scroll still scrolls the page
            pinch: { enabled: true },
            mode: "x",
            onZoomComplete: ({ chart }) => rescaleYToVisibleWindow(chart, dataLength),
          },
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          min: yMin,
          max: yMax,
          grid: { color: "#e1e0d9" },
          ticks: { color: "#898781", font: { size: isMobile ? 10 : 11 } },
        },
        x: {
          grid: { display: false },
          ticks: {
            autoSkip: true,
            maxTicksLimit: isMobile ? 5 : 10,
            color: "#898781",
            font: { size: isMobile ? 10 : 11 },
          },
        },
      },
    },
  });

  ctx._chartInstance = chart;
}
