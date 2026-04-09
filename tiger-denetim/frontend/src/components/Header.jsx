export default function Header({ connected, connInfo, onRefresh, onSettings }) {
  const server = connInfo?.server || '-';
  const database = connInfo?.database || '-';

  return (
    <header className="bg-brand-500 text-white h-16 flex items-center justify-between px-6 shadow-md">
      <div>
        <h1 className="text-lg font-bold tracking-wide">LOGO TIGER DENETIM PANELI</h1>
        <p className="text-xs text-brand-200">{server} - {database} / Firma 321</p>
      </div>
      <div className="flex items-center gap-3">
        {/* Ayarlar butonu */}
        <button
          onClick={onSettings}
          className="flex items-center gap-1.5 bg-brand-600/50 hover:bg-brand-600 px-3 py-2 rounded-lg text-sm transition-all duration-200"
          title="Baglanti Ayarlari"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Ayarlar
        </button>

        {/* Yenile butonu */}
        <button
          onClick={onRefresh}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 px-4 py-2 rounded-lg text-sm transition-all duration-200"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Yenile
        </button>

        {/* Baglanti durumu */}
        <div className="flex items-center gap-2 text-sm">
          <span className={`w-2.5 h-2.5 rounded-full ${connected ? 'bg-green-400' : connected === false ? 'bg-red-400 animate-pulse-danger' : 'bg-yellow-400'}`} />
          {connected ? 'Bagli' : connected === false ? 'Baglanti Yok' : 'Kontrol Ediliyor...'}
        </div>
      </div>
    </header>
  );
}
