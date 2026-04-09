const API_BASE = '/api';

async function fetchAPI(endpoint) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error(`API hatasi: ${endpoint}`, error);
    return null;
  }
}

async function postAPI(endpoint, body) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return await res.json();
}

export const api = {
  // Baglanti
  health:            () => fetchAPI('/health'),
  getConnection:     () => fetchAPI('/connection'),
  testConnection:    (config) => postAPI('/connection/test', config),
  saveConnection:    (config) => postAPI('/connection/save', config),

  // Dashboard
  summary:       () => fetchAPI('/summary'),

  // Trigger
  triggers:      () => fetchAPI('/triggers'),

  // Silmeler
  deletionSummary:  () => fetchAPI('/deletions/summary'),
  deletionDetail:   (table, limit = 50) => fetchAPI(`/deletions/${table}?limit=${limit}`),
  deletionRecent:   (limit = 20) => fetchAPI(`/deletions/recent?limit=${limit}`),
  deletionByPC:     () => fetchAPI('/deletions/by-computer'),

  // Changelog
  changelog:     () => fetchAPI('/changelog'),

  // Snapshot
  snapshot:      () => fetchAPI('/snapshot'),

  // Jobs
  jobs:          () => fetchAPI('/jobs'),

  // Sorgu Editoru
  executeQuery:  (sql, database = 'TIGERDB') => postAPI('/query', { sql, database }),

  // Raporlar
  reportTimeline:  () => fetchAPI('/reports/timeline'),
  reportComputers: () => fetchAPI('/reports/risk-computers'),
};
