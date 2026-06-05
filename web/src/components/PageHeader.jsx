export default function PageHeader({ fetchedAt }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4 sm:px-5 sm:py-5 shadow-sm">
      <p className="text-sm text-slate-600">
        Last updated <span className="font-semibold text-slate-900">{new Date(fetchedAt).toLocaleString()}</span>
      </p>
    </div>
  );
}
