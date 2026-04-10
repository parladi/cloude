import { useState, useEffect } from 'react';
import { api } from '../api';

const DEFAULT_CONFIG = {
  server: '192.168.0.9',
  port: 1433,
  user: 'sa',
  password: '',
  database: 'TIGERDB',
  database_backup: 'VeribanLocalDB',
};

export default function ConnectionPage() {
  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [error, setError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [currentConn, setCurrentConn] = useState(null);

  useEffect(() => {
    // localStorage'dan onceki ayarlari yukle
    const saved = localStorage.getItem('tiger_connection');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setConfig(parsed);
        setCurrentConn(parsed);
      } catch {}
    }
    // Backend'den mevcut ayarlari al
    api.getConnection().then(data => {
      if (data) {
        setConfig(data);
        setCurrentConn(data);
      }
    });
  }, []);

  const update = (field, value) => {
    setConfig(prev => ({ ...prev, [field]: value }));
    setTestResult(null);
    setError(null);
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    setError(null);
    try {
      const result = await api.testConnection(config);
      setTestResult(result);
    } catch (err) {
      setError(err.message);
    }
    setTesting(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const result = await api.saveConnection(config);
      if (result.success) {
        localStorage.setItem('tiger_connection', JSON.stringify(config));
        setCurrentConn(config);
        setTestResult({ success: true, message: 'Ayarlar kaydedildi ve baglanti kuruldu!' });
      }
    } catch (err) {
      setError(err.message);
    }
    setSaving(false);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-xl font-bold text-text-primary">Baglanti Ayarlari</h2>

      {/* Mevcut baglanti bilgisi */}
      {currentConn && (
        <div className="bg-green-50 border border-success rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2.5 h-2.5 rounded-full bg-success" />
            <span className="text-sm font-medium text-success">Aktif Baglanti</span>
          </div>
          <p className="text-sm text-text-primary">
            {currentConn.server}:{currentConn.port} / {currentConn.database} ({currentConn.user})
          </p>
        </div>
      )}

      {/* Form */}
      <div className="bg-white rounded-xl shadow-sm border border-brand-200 p-6 space-y-5">
        {/* Sunucu + Port */}
        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-text-primary mb-1.5">Sunucu Adresi</label>
            <input
              type="text"
              value={config.server}
              onChange={e => update('server', e.target.value)}
              placeholder="192.168.0.9"
              className="w-full px-3 py-2.5 border border-brand-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">Port</label>
            <input
              type="number"
              value={config.port}
              onChange={e => update('port', parseInt(e.target.value) || 1433)}
              placeholder="1433"
              className="w-full px-3 py-2.5 border border-brand-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-sm"
            />
          </div>
        </div>

        {/* Kullanici + Sifre */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">Kullanici Adi</label>
            <input
              type="text"
              value={config.user}
              onChange={e => update('user', e.target.value)}
              placeholder="sa"
              className="w-full px-3 py-2.5 border border-brand-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">Sifre</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={config.password}
                onChange={e => update('password', e.target.value)}
                placeholder="(bos birakilabilir)"
                className="w-full px-3 py-2.5 border border-brand-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-sm pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  {showPassword ? (
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                  ) : (
                    <>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </>
                  )}
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Veritabanlari */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">Ana Veritabani</label>
            <input
              type="text"
              value={config.database}
              onChange={e => update('database', e.target.value)}
              placeholder="TIGERDB"
              className="w-full px-3 py-2.5 border border-brand-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">Yedek Veritabani</label>
            <input
              type="text"
              value={config.database_backup}
              onChange={e => update('database_backup', e.target.value)}
              placeholder="VeribanLocalDB"
              className="w-full px-3 py-2.5 border border-brand-200 rounded-lg focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-sm"
            />
          </div>
        </div>

        {/* Test Sonucu */}
        {testResult && (
          <div className={`p-4 rounded-lg text-sm ${testResult.success ? 'bg-green-50 border border-success text-green-800' : 'bg-red-50 border border-danger text-red-800'}`}>
            <p className="font-medium">{testResult.message}</p>
            {testResult.server_name && (
              <p className="text-xs mt-1 opacity-75">Sunucu: {testResult.server_name}</p>
            )}
            {testResult.version && (
              <p className="text-xs mt-0.5 opacity-75">{testResult.version}</p>
            )}
          </div>
        )}

        {/* Hata */}
        {error && (
          <div className="p-4 rounded-lg text-sm bg-red-50 border border-danger text-red-800">
            <p className="font-medium">{error}</p>
          </div>
        )}

        {/* Butonlar */}
        <div className="flex gap-3 pt-2">
          <button
            onClick={handleTest}
            disabled={testing || !config.server || !config.user}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 border-2 border-brand-500 text-brand-500 rounded-lg hover:bg-brand-50 transition-colors text-sm font-medium disabled:opacity-50"
          >
            {testing ? (
              <span className="animate-spin w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full" />
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            )}
            Baglanti Test Et
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !config.server || !config.user}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-colors text-sm font-medium disabled:opacity-50"
          >
            {saving ? (
              <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            )}
            Kaydet ve Baglan
          </button>
        </div>
      </div>

      {/* Bilgi */}
      <div className="bg-brand-50 rounded-xl border border-brand-200 p-4 text-sm text-text-secondary">
        <p className="font-medium text-text-primary mb-2">Bilgi</p>
        <ul className="space-y-1 list-disc list-inside">
          <li>Baglanti ayarlari tarayicida saklanir, tekrar girmenize gerek kalmaz.</li>
          <li>Sifre bos birakilabilir (SQL Server ayarina gore).</li>
          <li>Varsayilan port: 1433</li>
          <li>Yedek veritabani CHANGELOG karsilastirmasi icin kullanilir.</li>
        </ul>
      </div>
    </div>
  );
}
