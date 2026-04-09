import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { api } from '../api';
import StatCard from '../components/StatCard';
import DataTable from '../components/DataTable';
import RefreshButton from '../components/RefreshButton';

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [recent, setRecent] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const [summary, recentData] = await Promise.all([
      api.summary(),
      api.deletionRecent(20),
    ]);
    setData(summary);
    setRecent(recentData);
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

  if (!data) {
    return <div className="text-danger p-4">Veri yuklenemedi. Baglanti kontrol edin.</div>;
  }

  const triggerStatus = data.triggers?.active === data.triggers?.total ? 'ok' : 'danger';
  const deletionStatus = data.deletions?.total > 0 ? 'danger' : 'ok';
  const changelogOk = data.changelog?.firm320_ok && data.changelog?.firm321_ok;
  const changelogStatus = changelogOk ? 'ok' : data.changelog?.firm320_ok === null ? 'neutral' : 'danger';

  const chartData = (data.deletions?.by_table || []).map(t => ({
    name: t.kategori,
    sayi: t.sayi,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-text-primary">Ozet Dashboard</h2>
        <RefreshButton onClick={load} loading={loading} />
      </div>

      {/* 4 Ozet Kart */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Trigger Durumu"
          value={`${data.triggers?.active}/${data.triggers?.total} AKTIF`}
          subtitle={data.triggers?.disabled?.length ? `Kapali: ${data.triggers.disabled.join(', ')}` : 'Tum triggerlar aktif'}
          status={triggerStatus}
          link="/triggers"
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          }
        />
        <StatCard
          title="Yakalanan Silmeler"
          value={data.deletions?.total?.toLocaleString('tr-TR') || '0'}
          subtitle={data.deletions?.total > 0 ? 'Silme tespit edildi!' : 'Silme tespit edilmedi'}
          status={deletionStatus}
          link="/deletions"
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          }
        />
        <StatCard
          title="CHANGELOG Butunlugu"
          value={changelogOk ? '320 \u2713 / 321 \u2713' : changelogStatus === 'neutral' ? 'Kontrol Edilemedi' : 'ALARM'}
          subtitle={!changelogOk && changelogStatus === 'danger' ? 'Changelog kaybi tespit edildi!' : 'Kayip yok'}
          status={changelogStatus}
          link="/changelog"
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          }
        />
        <StatCard
          title="Job Durumu"
          value={`${data.jobs?.active || 0}/${data.jobs?.total || 0} AKTIF`}
          subtitle={data.jobs?.last_run ? `Son: ${data.jobs.last_run}` : ''}
          status={data.jobs?.active === data.jobs?.total ? 'ok' : 'danger'}
          link="/jobs"
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            </svg>
          }
        />
      </div>

      {/* Bar Grafik */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-brand-200 p-6">
          <h3 className="font-semibold text-text-primary mb-4">Tablo Bazli Silme Dagilimi</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E3F2FD" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={80} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ borderRadius: '8px', border: '1px solid #BBDEFB' }}
                formatter={(value) => [value.toLocaleString('tr-TR'), 'Silme']}
              />
              <Bar dataKey="sayi" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.sayi > 0 ? '#F44336' : '#E0E0E0'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Son Silmeler Tablosu */}
      {recent && recent.rows && (
        <DataTable
          title="Son Yakalanan Silmeler"
          columns={recent.columns?.filter(c => c !== 'sira')}
          rows={recent.rows}
        />
      )}
    </div>
  );
}
