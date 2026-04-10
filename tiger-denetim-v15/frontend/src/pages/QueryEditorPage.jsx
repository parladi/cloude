import { useState } from 'react';
import { api } from '../api';
import DataTable from '../components/DataTable';

const QUERY_TEMPLATES = [
  {
    category: 'Stok Silmeleri',
    queries: [
      { label: 'Son Stok Fis Silmeleri', sql: "SELECT TOP 50 CAPIPOLICYDATE AS Zaman, CAPIPOLICYUSER AS Hesap, CAPIPOLICYHOST AS Bilgisayar, FICHENO AS Fis_No, TRCODE, FORMAT(DATE_, 'dd.MM.yyyy') AS Fis_Tarihi FROM L_CAPIDEL_SFLOG ORDER BY CAPIPOLICYDATE DESC" },
      { label: 'Son Stok Satir Silmeleri', sql: "SELECT TOP 100 CAPIPOLICYDATE AS Zaman, CAPIPOLICYUSER AS Hesap, CAPIPOLICYHOST AS Bilgisayar, STFICHEREF, STOCKREF, AMOUNT AS Miktar_KG, TRCODE FROM L_CAPIDEL_STLLOG ORDER BY CAPIPOLICYDATE DESC" },
      { label: 'Son Lot Hareket Silmeleri', sql: "SELECT TOP 100 CAPIPOLICYDATE AS Zaman, CAPIPOLICYUSER AS Hesap, CAPIPOLICYHOST AS Bilgisayar, STTRANSREF, SLREF, AMOUNT AS Miktar_KG FROM L_CAPIDEL_SLTLOG ORDER BY CAPIPOLICYDATE DESC" },
    ]
  },
  {
    category: 'Finans Silmeleri',
    queries: [
      { label: 'Son Fatura Silmeleri', sql: "SELECT TOP 50 CAPIPOLICYDATE AS Zaman, CAPIPOLICYUSER AS Hesap, CAPIPOLICYHOST AS Bilgisayar, CAPIPOLICYIP AS IP, FICHESSION AS Fatura_No, NETTOTAL AS Tutar, TRCODE FROM L_CAPIDEL_INVLOG ORDER BY CAPIPOLICYDATE DESC" },
      { label: 'Son Odeme Silmeleri', sql: "SELECT TOP 50 CAPIPOLICYDATE AS Zaman, CAPIPOLICYUSER AS Hesap, CAPIPOLICYHOST AS Bilgisayar, TOTAL AS Tutar, TRCODE FROM L_CAPIDEL_PAYLOG ORDER BY CAPIPOLICYDATE DESC" },
      { label: 'Son Banka Fis Silmeleri', sql: "SELECT TOP 50 CAPIPOLICYDATE AS Zaman, CAPIPOLICYUSER AS Hesap, CAPIPOLICYHOST AS Bilgisayar, FICHENO, NETTOTAL AS Tutar, TRCODE FROM L_CAPIDEL_BNFLOG ORDER BY CAPIPOLICYDATE DESC" },
      { label: 'Son Cari Fis Silmeleri', sql: "SELECT TOP 50 CAPIPOLICYDATE AS Zaman, CAPIPOLICYUSER AS Hesap, CAPIPOLICYHOST AS Bilgisayar, FICHENO, NETTOTAL AS Tutar, TRCODE FROM L_CAPIDEL_CFFLOG ORDER BY CAPIPOLICYDATE DESC" },
    ]
  },
  {
    category: 'Analizler',
    queries: [
      { label: 'Bilgisayar Bazli Dagilim', sql: "SELECT CAPIPOLICYHOST AS Bilgisayar, COUNT(*) AS Toplam_Silme, MIN(CAPIPOLICYDATE) AS Ilk_Silme, MAX(CAPIPOLICYDATE) AS Son_Silme FROM (SELECT CAPIPOLICYHOST, CAPIPOLICYDATE FROM L_CAPIDEL_SFLOG UNION ALL SELECT CAPIPOLICYHOST, CAPIPOLICYDATE FROM L_CAPIDEL_STLLOG UNION ALL SELECT CAPIPOLICYHOST, CAPIPOLICYDATE FROM L_CAPIDEL_SLTLOG UNION ALL SELECT CAPIPOLICYHOST, CAPIPOLICYDATE FROM L_CAPIDEL_PAYLOG UNION ALL SELECT CAPIPOLICYHOST, CAPIPOLICYDATE FROM L_CAPIDEL_INVLOG) AS t GROUP BY CAPIPOLICYHOST ORDER BY Toplam_Silme DESC" },
      { label: 'Gunluk Silme Trendi', sql: "SELECT CAST(CAPIPOLICYDATE AS DATE) AS Gun, COUNT(*) AS Silme_Sayisi FROM (SELECT CAPIPOLICYDATE FROM L_CAPIDEL_SFLOG UNION ALL SELECT CAPIPOLICYDATE FROM L_CAPIDEL_STLLOG UNION ALL SELECT CAPIPOLICYDATE FROM L_CAPIDEL_SLTLOG UNION ALL SELECT CAPIPOLICYDATE FROM L_CAPIDEL_PAYLOG) AS t GROUP BY CAST(CAPIPOLICYDATE AS DATE) ORDER BY Gun" },
      { label: 'Trigger Durumu', sql: "SELECT name AS Trigger_Adi, OBJECT_NAME(parent_id) AS Tablo, CASE is_disabled WHEN 0 THEN 'AKTIF' ELSE 'KAPALI' END AS Durum, create_date AS Olusturma, modify_date AS Son_Degisiklik FROM sys.triggers WHERE name LIKE 'LG_%_DEL_321%' OR name LIKE 'LG_%CK_DEL_321%' ORDER BY name" },
    ]
  },
  {
    category: 'CHANGELOG',
    queries: [
      { label: 'CHANGELOG Karsilastirma', sql: "SELECT '320_KAYNAK' AS Tablo, COUNT(*) AS Sayi FROM LG_320_CHANGELOG WITH(NOLOCK) UNION ALL SELECT '321_KAYNAK', COUNT(*) FROM LG_321_CHANGELOG WITH(NOLOCK)" },
      { label: 'Son CHANGELOG Kayitlari (321)', sql: "SELECT TOP 100 LOGICALREF, RECORDREF, USERNR, OPERATION, FORMID, DESCRIPTION, DATE_ AS Tarih, TIME_ AS Saat FROM LG_321_CHANGELOG ORDER BY LOGICALREF DESC" },
    ]
  }
];

export default function QueryEditorPage() {
  const [sql, setSql] = useState('SELECT TOP 100 * FROM L_CAPIDEL_SFLOG ORDER BY CAPIPOLICYDATE DESC');
  const [database, setDatabase] = useState('TIGERDB');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const execute = async () => {
    if (!sql.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.executeQuery(sql, database);
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      execute();
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-text-primary">Canli SQL Editoru</h2>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sol Panel - Sablonlar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-brand-200 p-4 space-y-4 max-h-[600px] overflow-y-auto">
            <h3 className="font-semibold text-sm text-text-primary">Hazir Sablonlar</h3>
            {QUERY_TEMPLATES.map(cat => (
              <div key={cat.category}>
                <p className="text-xs font-medium text-text-secondary mb-1">{cat.category}</p>
                <div className="space-y-1">
                  {cat.queries.map(q => (
                    <button
                      key={q.label}
                      onClick={() => setSql(q.sql)}
                      className="w-full text-left px-3 py-2 text-xs rounded-lg hover:bg-brand-50 text-text-primary transition-colors"
                    >
                      {q.label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sag Panel - Editor + Sonuc */}
        <div className="lg:col-span-3 space-y-4">
          {/* Editor */}
          <div className="bg-white rounded-xl shadow-sm border border-brand-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <select
                  value={database}
                  onChange={e => setDatabase(e.target.value)}
                  className="px-3 py-1.5 text-sm border border-brand-200 rounded-lg focus:outline-none focus:border-brand-400"
                >
                  <option value="TIGERDB">TIGERDB</option>
                  <option value="VeribanLocalDB">VeribanLocalDB</option>
                  <option value="msdb">msdb</option>
                </select>
                <span className="text-xs text-text-secondary">Ctrl+Enter ile calistir</span>
              </div>
              <button
                onClick={execute}
                disabled={loading}
                className="flex items-center gap-2 bg-brand-500 hover:bg-brand-600 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
              >
                {loading ? (
                  <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  </svg>
                )}
                Calistir
              </button>
            </div>
            <textarea
              value={sql}
              onChange={e => setSql(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={10}
              className="w-full font-mono text-sm p-3 border border-brand-200 rounded-lg focus:outline-none focus:border-brand-400 resize-y bg-brand-50"
              placeholder="SELECT sorgunuzu buraya yazin..."
            />
          </div>

          {/* Hata */}
          {error && (
            <div className="p-4 rounded-xl bg-red-50 border border-danger text-danger text-sm">
              <p className="font-bold">Hata:</p>
              <p>{error}</p>
            </div>
          )}

          {/* Sonuc */}
          {result && (
            <div>
              <div className="flex items-center gap-4 mb-2 text-sm text-text-secondary">
                <span>{result.row_count} kayit</span>
                <span>{result.execution_time_ms} ms</span>
              </div>
              <DataTable
                title="Sorgu Sonucu"
                columns={result.columns}
                rows={result.rows}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
