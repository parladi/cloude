export default function Header({ connected, onRefresh }) {
  return (
    <header className="bg-brand-500 text-white h-16 flex items-center justify-between px-6 shadow-md">
      <div>
        <h1 className="text-lg font-bold tracking-wide">LOGO TIGER DENETIM PANELI</h1>
        <p className="text-xs text-brand-200">192.168.0.9 - TIGERDB / Firma 321</p>
      </div>
      <div className="flex items-center gap-4">
        <button
          onClick={onRefresh}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 px-4 py-2 rounded-lg text-sm transition-all duration-200"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Yenile
        </button>
        <div className="flex items-center gap-2 text-sm">
          <span className={`w-2.5 h-2.5 rounded-full ${connected ? 'bg-green-400' : connected === false ? 'bg-red-400 animate-pulse-danger' : 'bg-yellow-400'}`} />
          {connected ? 'Bagli' : connected === false ? 'Baglanti Yok' : 'Kontrol Ediliyor...'}
        </div>
      </div>
    </header>
  );
}
