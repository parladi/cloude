import { useState, useEffect } from 'react';
import { api } from '../api';
import AlertBadge from '../components/AlertBadge';
import RefreshButton from '../components/RefreshButton';

const TRIGGER_MAP = [
  { trigger: 'LG_INVOICE_DEL_321_01',    table: 'LG_321_01_INVOICE',    backup: 'L_CAPIDEL_INVLOG',  label: 'Fatura' },
  { trigger: 'LG_STFCHCK_DEL_321_01',    table: 'LG_321_01_STFICHE',   backup: 'L_CAPIDEL_SFLOG',   label: 'Stok Fis' },
  { trigger: 'LG_STLINECK_DEL_321_01',   table: 'LG_321_01_STLINE',    backup: 'L_CAPIDEL_STLLOG',  label: 'Stok Satir' },
  { trigger: 'LG_SLLINECK_DEL_321_01',   table: 'LG_321_01_SLTRANS',   backup: 'L_CAPIDEL_SLTLOG',  label: 'Lot Hareket' },
  { trigger: 'LG_SERILOTN_DEL_321_01',   table: 'LG_321_01_SERILOTN',  backup: 'L_CAPIDEL_SERLOG',  label: 'Lot Kart' },
  { trigger: 'LG_CHANGELOG_DEL_321',     table: 'LG_321_CHANGELOG',    backup: 'L_CAPIDEL_CLLOG',   label: 'Changelog' },
  { trigger: 'LG_CLCARD_DEL_321',        table: 'LG_321_CLCARD',       backup: 'L_CAPIDEL_CCLOG',   label: 'Cari Kart' },
  { trigger: 'LG_BNFICHE_DEL_321_01',    table: 'LG_321_01_BNFICHE',   backup: 'L_CAPIDEL_BNFLOG',  label: 'Banka Fis' },
  { trigger: 'LG_BNFLINECK_DEL_321_01',  table: 'LG_321_01_BNFLINE',   backup: 'L_CAPIDEL_BNLLOG',  label: 'Banka Satir' },
  { trigger: 'LG_BNCARD_DEL_321',        table: 'LG_321_BNCARD',       backup: 'L_CAPIDEL_BNCLOG',  label: 'Banka Kart' },
  { trigger: 'LG_CLFICHE_DEL_321_01',    table: 'LG_321_01_CLFICHE',   backup: 'L_CAPIDEL_CFFLOG',  label: 'Cari Fis' },
  { trigger: 'LG_CLFLINECK_DEL_321_01',  table: 'LG_321_01_CLFLINE',   backup: 'L_CAPIDEL_CFLLOG',  label: 'Cari Satir' },
  { trigger: 'LG_CSCARD_DEL_321_01',     table: 'LG_321_01_CSCARD',    backup: 'L_CAPIDEL_CSCLOG',  label: 'Cek/Senet Kart' },
  { trigger: 'LG_CSTRANS_DEL_321_01',    table: 'LG_321_01_CSTRANS',   backup: 'L_CAPIDEL_CSTLOG',  label: 'Cek/Senet Hareket' },
  { trigger: 'LG_CSROLL_DEL_321_01',     table: 'LG_321_01_CSROLL',    backup: 'L_CAPIDEL_CSRLOG',  label: 'Cek/Senet Ciro' },
  { trigger: 'LG_PAYTRANS_DEL_321_01',   table: 'LG_321_01_PAYTRANS',  backup: 'L_CAPIDEL_PAYLOG',  label: 'Odeme' },
  { trigger: 'LG_KSLINECK_DEL_321_01',   table: 'LG_321_01_KSLINES',   backup: 'L_CAPIDEL_KSLLOG',  label: 'Kasa' },
  { trigger: 'LG_EMUHACCK_DEL_321',      table: 'LG_321_EMUHACC',      backup: 'L_CAPIDEL_EMLOG',   label: 'Hesap Plani' },
];

export default function TriggersPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const result = await api.triggers();
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

  const disabled = data?.disabled || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-text-primary">Trigger Durumu</h2>
        <RefreshButton onClick={load} loading={loading} />
      </div>

      {/* Ozet */}
      <div className={`p-4 rounded-xl border-2 ${disabled.length ? 'bg-red-50 border-danger' : 'bg-green-50 border-success'}`}>
        <p className={`font-bold ${disabled.length ? 'text-danger' : 'text-success'}`}>
          {data?.active}/{data?.total} Aktif
        </p>
        {disabled.length > 0 && (
          <p className="text-sm text-danger mt-1">
            DIKKAT: {disabled.length} trigger devre disi birakilmis! ({disabled.join(', ')})
          </p>
        )}
      </div>

      {/* Trigger Tablosu */}
      <div className="bg-white rounded-xl shadow-sm border border-brand-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-brand-50">
                <th className="px-4 py-3 text-left font-medium text-text-secondary">#</th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">Trigger Adi</th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">Etiket</th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">Kaynak Tablo</th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">Yedek Tablo</th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">Durum</th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">Olusturma</th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">Son Degisiklik</th>
              </tr>
            </thead>
            <tbody>
              {TRIGGER_MAP.map((tm, i) => {
                const triggerData = (data?.triggers || []).find(t => t.trigger_adi === tm.trigger);
                const status = triggerData?.durum || 'BILINMIYOR';
                return (
                  <tr key={tm.trigger} className="border-t border-brand-100 hover:bg-brand-50/50">
                    <td className="px-4 py-2.5 text-text-secondary">{i + 1}</td>
                    <td className="px-4 py-2.5 font-mono text-xs">{tm.trigger}</td>
                    <td className="px-4 py-2.5">{tm.label}</td>
                    <td className="px-4 py-2.5 font-mono text-xs text-text-secondary">{tm.table}</td>
                    <td className="px-4 py-2.5 font-mono text-xs text-text-secondary">{tm.backup}</td>
                    <td className="px-4 py-2.5">
                      <AlertBadge status={status} />
                    </td>
                    <td className="px-4 py-2.5 text-xs text-text-secondary">
                      {triggerData?.olusturma_tarihi ? new Date(triggerData.olusturma_tarihi).toLocaleDateString('tr-TR') : '-'}
                    </td>
                    <td className="px-4 py-2.5 text-xs text-text-secondary">
                      {triggerData?.son_degisiklik ? new Date(triggerData.son_degisiklik).toLocaleDateString('tr-TR') : '-'}
                    </td>
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
