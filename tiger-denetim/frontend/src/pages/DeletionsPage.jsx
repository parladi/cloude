import { useState, useEffect } from 'react';
import { api } from '../api';
import DataTable from '../components/DataTable';
import RefreshButton from '../components/RefreshButton';

const TABLE_LABELS = {
  INVOICE: 'Fatura', STFICHE: 'Stok Fis', STLINE: 'Stok Satir', SLTRANS: 'Lot Hareket',
  SERILOTN: 'Lot Kart', CHANGELOG: 'Changelog', CLCARD: 'Cari Kart', BNFICHE: 'Banka Fis',
  BNFLINE: 'Banka Satir', BNCARD: 'Banka Kart', CLFICHE: 'Cari Fis', CLFLINE: 'Cari Satir',
  CSCARD: 'Cek/Senet Kart', CSTRANS: 'Cek/Senet Hareket', CSROLL: 'Cek/Senet Ciro',
  PAYTRANS: 'Odeme', KSLINES: 'Kasa', EMUHACC: 'Hesap Plani',
};

export default function DeletionsPage() {
  const [summary, setSummary] = useState(null);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  const loadSummary = async () => {
    setLoading(true);
    const result = await api.deletionSummary();
    setSummary(result?.tables || []);
    setLoading(false);
  };

  const loadDetail = async (tableName) => {
    setSelected(tableName);
    setDetailLoading(true);
    const result = await api.deletionDetail(tableName, 100);
    setDetail(result);
    setDetailLoading(false);
  };

  useEffect(() => { loadSummary(); }, []);

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-text-primary">Silme Detaylari</h2>
        <RefreshButton onClick={loadSummary} loading={loading} />
      </div>

      {/* Tablo Bazli Grid Kartlari */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {(summary || []).map(t => {
          const isActive = selected === t.kategori;
          const hasDeletions = t.sayi > 0;
          return (
            <button
              key={t.kategori}
              onClick={() => loadDetail(t.kategori)}
              className={`p-4 rounded-xl border-2 text-left transition-all duration-200 ${
                isActive
                  ? 'border-brand-500 bg-brand-50 shadow-md'
                  : hasDeletions
                    ? 'border-danger bg-red-50 hover:shadow-md'
                    : 'border-brand-200 bg-white hover:border-brand-300'
              }`}
            >
              <p className="text-xs text-text-secondary truncate">{TABLE_LABELS[t.kategori] || t.kategori}</p>
              <p className={`text-xl font-bold mt-1 ${hasDeletions ? 'text-danger' : 'text-text-secondary'}`}>
                {t.sayi.toLocaleString('tr-TR')}
              </p>
              <p className="text-[10px] font-mono text-text-secondary mt-1 truncate">{t.kategori}</p>
            </button>
          );
        })}
      </div>

      {/* Secilen Tablonun Detaylari */}
      {selected && (
        <div>
          {detailLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin w-6 h-6 border-4 border-brand-500 border-t-transparent rounded-full" />
            </div>
          ) : detail ? (
            <DataTable
              title={`${TABLE_LABELS[selected] || selected} - Silme Kayitlari`}
              columns={detail.columns}
              rows={detail.rows}
            />
          ) : null}
        </div>
      )}
    </div>
  );
}
