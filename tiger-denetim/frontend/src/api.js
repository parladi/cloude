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

export const api = {
  health:        () => fetchAPI('/health'),
  summary:       () => fetchAPI('/summary'),

  triggers:      () => fetchAPI('/triggers'),

  deletionSummary:  () => fetchAPI('/deletions/summary'),
  deletionDetail:   (table, limit = 50) => fetchAPI(`/deletions/${table}?limit=${limit}`),
  deletionRecent:   (limit = 20) => fetchAPI(`/deletions/recent?limit=${limit}`),
  deletionByPC:     () => fetchAPI('/deletions/by-computer'),

  changelog:     () => fetchAPI('/changelog'),

  snapshot:      () => fetchAPI('/snapshot'),

  jobs:          () => fetchAPI('/jobs'),

  executeQuery:  async (sql, database = 'TIGERDB') => {
    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sql, database }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      return await res.json();
    } catch (error) {
      console.error('Sorgu hatasi:', error);
      throw error;
    }
  },

  reportTimeline:  () => fetchAPI('/reports/timeline'),
  reportComputers: () => fetchAPI('/reports/risk-computers'),
};
