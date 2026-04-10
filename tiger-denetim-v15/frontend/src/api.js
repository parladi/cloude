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
  health: () => fetchAPI('/health'),
  getConnection: () => fetchAPI('/connection'),
  testConnection: (c) => postAPI('/connection/test', c),
  saveConnection: (c) => postAPI('/connection/save', c),
  summary: () => fetchAPI('/summary'),
  triggers: () => fetchAPI('/triggers'),
  deletionSummary: () => fetchAPI('/deletions/summary'),
  deletionDetail: (t, l = 50) => fetchAPI(`/deletions/${t}?limit=${l}`),
  deletionRecent: (l = 20) => fetchAPI(`/deletions/recent?limit=${l}`),
  deletionByPC: () => fetchAPI('/deletions/by-computer'),
  changelog: () => fetchAPI('/changelog'),
  snapshot: () => fetchAPI('/snapshot'),
  jobs: () => fetchAPI('/jobs'),
  executeQuery: (sql, db = 'TIGERDB') => postAPI('/query', { sql, database: db }),
  reportTimeline: () => fetchAPI('/reports/timeline'),
  reportComputers: () => fetchAPI('/reports/risk-computers'),
};
