import { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../api';
import RefreshButton from '../components/RefreshButton';

export default function ReportsPage() {
  const [computers, setComputers] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('computers');

  const load = async () => {
    setLoading(true);
    const [comp, time] = await Promise.all([
      api.reportComputers(),
      api.reportTimeline(),
    ]);
    setComputers(comp);
    setTimeline(time);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  if (loading && !computers) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  const tabs = [
    { id: 'computers', label: 'Bilgisayar Risk Skoru' },
    { id: 'timeline', label: 'Zaman Cizelgesi' },
  ];

  const computerData = (computers?.computers || []).map(c => ({
    name: c.bilgisayar || 'Bilinmiyor',
    silme: c.toplam_silme,
    ilk: c.ilk_silme,
    son: c.son_silme,
  }));

  const timelineData = (timeline?.rows || []).map(r => ({
    gun: r.gun,
    sayi: r.silme_sayisi,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-text-primary">Forensik Raporlar</h2>
        <RefreshButton onClick={load} loading={loading} />
      </div>

      {/* Tab Menu */}
      <div className="flex gap-2 border-b border-brand-200 pb-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm rounded-t-lg transition-colors ${
              activeTab === tab.id
                ? 'bg-brand-500 text-white'
                : 'text-text-secondary hover:bg-brand-100'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Bilgisayar Risk Skoru */}
      {activeTab === 'computers' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-brand-200 p-6">
            <h3 className="font-semibold text-text-primary mb-4">Bilgisayar Bazli Silme Sayilari</h3>
            {computerData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={computerData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E3F2FD" />
                  <XAxis type="number" tick={{ fontSize: 12 }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={120} />
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: '1px solid #BBDEFB' }}
                    formatter={(value) => [value.toLocaleString('tr-TR'), 'Silme']}
                  />
                  <Bar dataKey="silme" fill="#F44336" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-text-secondary text-sm">Veri bulunamadi</p>
            )}
          </div>

          {/* Tablo */}
          {computerData.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-brand-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-brand-50">
                    <th className="px-4 py-3 text-left font-medium text-text-secondary">#</th>
                    <th className="px-4 py-3 text-left font-medium text-text-secondary">Bilgisayar</th>
                    <th className="px-4 py-3 text-right font-medium text-text-secondary">Toplam Silme</th>
                    <th className="px-4 py-3 text-left font-medium text-text-secondary">Ilk Silme</th>
                    <th className="px-4 py-3 text-left font-medium text-text-secondary">Son Silme</th>
                  </tr>
                </thead>
                <tbody>
                  {computerData.map((c, i) => (
                    <tr key={c.name} className={`border-t border-brand-100 ${i === 0 ? 'bg-red-50' : ''}`}>
                      <td className="px-4 py-2.5 text-text-secondary">{i + 1}</td>
                      <td className={`px-4 py-2.5 font-medium ${i === 0 ? 'text-danger' : 'text-text-primary'}`}>{c.name}</td>
                      <td className="px-4 py-2.5 text-right font-bold text-danger">{c.silme.toLocaleString('tr-TR')}</td>
                      <td className="px-4 py-2.5 text-xs text-text-secondary">{c.ilk ? new Date(c.ilk).toLocaleString('tr-TR') : '-'}</td>
                      <td className="px-4 py-2.5 text-xs text-text-secondary">{c.son ? new Date(c.son).toLocaleString('tr-TR') : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Zaman Cizelgesi */}
      {activeTab === 'timeline' && (
        <div className="bg-white rounded-xl shadow-sm border border-brand-200 p-6">
          <h3 className="font-semibold text-text-primary mb-4">Gunluk Silme Trendi</h3>
          {timelineData.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E3F2FD" />
                <XAxis dataKey="gun" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={80} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: '1px solid #BBDEFB' }}
                  formatter={(value) => [value.toLocaleString('tr-TR'), 'Silme']}
                  labelFormatter={(label) => `Tarih: ${label}`}
                />
                <Line
                  type="monotone"
                  dataKey="sayi"
                  stroke="#F44336"
                  strokeWidth={2}
                  dot={{ fill: '#F44336', r: 3 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-text-secondary text-sm">Veri bulunamadi</p>
          )}
        </div>
      )}
    </div>
  );
}
