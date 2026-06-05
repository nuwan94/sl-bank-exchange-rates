export default function TabNav({ activeTab, onTabChange }) {
  return (
    <div className="tabs tabs-boxed rounded-3xl bg-slate-50 border border-slate-200 p-1 shadow-sm">
      <button
        type="button"
        className={`tab rounded-3xl ${activeTab === 'rates' ? 'tab-active' : ''}`}
        onClick={() => onTabChange('rates')}
      >
        Rates
      </button>
      <button
        type="button"
        className={`tab rounded-3xl ${activeTab === 'charts' ? 'tab-active' : ''}`}
        onClick={() => onTabChange('charts')}
      >
        Charts
      </button>
    </div>
  );
}
