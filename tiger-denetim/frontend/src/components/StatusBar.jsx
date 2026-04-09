export default function StatusBar({ connected, lastRefresh, connInfo }) {
  return (
    <footer className="bg-white border-t border-brand-200 h-10 flex items-center justify-between px-6 text-xs text-text-secondary">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span>Durum:</span>
          <span className={`flex items-center gap-1 ${connected ? 'text-success' : 'text-danger'}`}>
            <span className={`w-2 h-2 rounded-full ${connected ? 'bg-success' : 'bg-danger'}`} />
            {connected ? 'Bagli' : 'Baglanti Yok'}
          </span>
        </div>
        {connInfo && (
          <span className="text-text-secondary">
            {connInfo.server}:{connInfo.port} / {connInfo.database}
          </span>
        )}
      </div>
      <div>
        Son yenileme: {lastRefresh || '-'}
      </div>
      <div>v1.5</div>
    </footer>
  );
}
