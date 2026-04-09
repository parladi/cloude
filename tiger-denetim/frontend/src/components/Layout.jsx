import { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import StatusBar from './StatusBar';

export default function Layout({ children }) {
  const [connected, setConnected] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [connInfo, setConnInfo] = useState(null);

  const checkHealth = async () => {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();
      setConnected(data.connected);
      if (data.connected) {
        setConnInfo({
          server: data.server,
          port: data.port,
          database: data.database,
          database_backup: data.database_backup,
        });
      }
      setLastRefresh(new Date().toLocaleString('tr-TR'));
    } catch {
      setConnected(false);
    }
  };

  // localStorage'dan kayitli ayar varsa backend'e gonder
  const restoreSavedConnection = async () => {
    const saved = localStorage.getItem('tiger_connection');
    if (saved) {
      try {
        await fetch('/api/connection/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: saved,
        });
      } catch {}
    }
    await checkHealth();
  };

  useEffect(() => {
    restoreSavedConnection();
  }, []);

  return (
    <div className="flex h-screen bg-brand-50">
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        connInfo={connInfo}
      />
      <div className="flex flex-col flex-1 min-w-0">
        <Header
          connected={connected}
          connInfo={connInfo}
          onRefresh={() => window.location.reload()}
        />
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
        <StatusBar connected={connected} lastRefresh={lastRefresh} connInfo={connInfo} />
      </div>
    </div>
  );
}
