import { useState, useEffect } from 'react';
import { api } from '../api';
import AlertBadge from '../components/AlertBadge';
import RefreshButton from '../components/RefreshButton';

export default function SnapshotPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const result = await api.snapshot();
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

  const tables = data?.tables || [];
  const alarms = tables.filter(t => t.durum === 'ALARM');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-text-primary">Snapshot Karsilastirma</h2>
        <RefreshButton onClick={load} loading={loading} />
      </div>

      {alarms.length > 0 && (
        <div className="p-4 rounded-xl bg-red-50 border-2 border-danger">
          <p className="text-danger font-bold">
            DIKKAT: {alarms.length} tabloda kayit azalmasi tespit edildi!
          </p>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-brand-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-brand-50">
                <th className="px-4 py-3 text-left font-medium text-text-secondary">#</th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">Tablo</th>
                <th className="px-4 py-3 text-right font-medium text-text-secondary">Snapshot Kayit</th>
                <th className="px-4 py-3 text-right font-medium text-text-secondary">Guncel Kayit</th>
                <th className="px-4 py-3 text-right font-medium text-text-secondary">Fark</th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">Durum</th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">Snapshot Zamani</th>
              </tr>
            </thead>
            <tbody>
              {tables.map((t, i) => {
                const rowClass = t.durum === 'ALARM' ? 'bg-red-50' : t.durum === 'NORMAL' ? 'bg-blue-50' : '';
                return (
                  <tr key={t.tablo} className={`border-t border-brand-100 ${rowClass}`}>
                    <td className="px-4 py-2.5 text-text-secondary">{i + 1}</td>
                    <td className="px-4 py-2.5 font-mono text-xs">{t.tablo}</td>
                    <td className="px-4 py-2.5 text-right">{(t.snapshot_kayit ?? 0).toLocaleString('tr-TR')}</td>
                    <td className="px-4 py-2.5 text-right">{(t.guncel_kayit ?? '-').toLocaleString?.('tr-TR') ?? t.guncel_kayit}</td>
                    <td className={`px-4 py-2.5 text-right font-bold ${t.fark < 0 ? 'text-danger' : t.fark > 0 ? 'text-blue-600' : 'text-success'}`}>
                      {t.fark > 0 ? '+' : ''}{t.fark?.toLocaleString?.('tr-TR') ?? t.fark}
                    </td>
                    <td className="px-4 py-2.5">
                      <AlertBadge status={t.durum} label={
                        t.durum === 'ALARM' ? `${Math.abs(t.fark)} kayit SILINMIS` :
                        t.durum === 'NORMAL' ? 'Yeni kayit' : 'OK'
                      } />
                    </td>
                    <td className="px-4 py-2.5 text-xs text-text-secondary">{t.snapshot_zamani || '-'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
