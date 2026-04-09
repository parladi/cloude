import { useState, useEffect } from 'react';
import { api } from '../api';
import RefreshButton from '../components/RefreshButton';

function ChangelogCard({ title, data }) {
  if (!data) return null;
  const isOk = data.ok;
  const fark = data.yedek - data.kaynak;

  return (
    <div className={`bg-white rounded-xl shadow-sm border-2 p-6 ${isOk ? 'border-success' : 'border-danger'}`}>
      <h3 className="text-sm text-text-secondary mb-4">{title}</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-text-secondary">Kaynak</p>
          <p className="text-2xl font-bold text-text-primary">{data.kaynak?.toLocaleString('tr-TR')}</p>
        </div>
        <div>
          <p className="text-xs text-text-secondary">Yedek</p>
          <p className="text-2xl font-bold text-text-primary">{data.yedek?.toLocaleString('tr-TR')}</p>
        </div>
      </div>
      <div className={`mt-4 p-3 rounded-lg ${isOk ? 'bg-green-50' : 'bg-red-50'}`}>
        {isOk ? (
          <p className="text-sm text-success font-medium flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
            Butunluk OK - Kayip yok
          </p>
        ) : (
          <div>
            <p className="text-sm text-danger font-bold flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              ALARM: CHANGELOG'dan {fark.toLocaleString('tr-TR')} kayit SILINMIS!
            </p>
            <p className="text-xs text-text-secondary mt-1">Fark: {data.fark}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChangelogPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const result = await api.changelog();
    setData(result);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-text-primary">CHANGELOG Karsilastirma</h2>
        <RefreshButton onClick={load} loading={loading} />
      </div>

      <p className="text-sm text-text-secondary">
        Kaynak tablodaki kayit sayisi ile yedek tablodaki kayit sayisi karsilastirilir.
        Yedek {">"} Kaynak ise CHANGELOG'dan kayit silinmis demektir.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ChangelogCard title="Firma 320" data={data?.firma_320} />
        <ChangelogCard title="Firma 321" data={data?.firma_321} />
      </div>
    </div>
  );
}
