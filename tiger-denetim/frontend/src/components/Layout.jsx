import { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import StatusBar from './StatusBar';

export default function Layout({ children }) {
  const [connected, setConnected] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const checkHealth = async () => {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();
      setConnected(data.connected);
      setLastRefresh(new Date().toLocaleString('tr-TR'));
    } catch {
      setConnected(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="flex h-screen bg-brand-50">
      <Sidebar open={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex flex-col flex-1 min-w-0">
        <Header connected={connected} onRefresh={() => window.location.reload()} />
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
        <StatusBar connected={connected} lastRefresh={lastRefresh} />
      </div>
    </div>
  );
}
