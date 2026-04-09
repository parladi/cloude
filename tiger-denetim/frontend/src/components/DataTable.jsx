import { useState, useMemo } from 'react';

export default function DataTable({ columns, rows, title, onExport }) {
  const [sortCol, setSortCol] = useState(null);
  const [sortDir, setSortDir] = useState('asc');
  const [filter, setFilter] = useState('');

  const handleSort = (col) => {
    if (sortCol === col) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortCol(col);
      setSortDir('asc');
    }
  };

  const filteredRows = useMemo(() => {
    if (!filter) return rows || [];
    const f = filter.toLowerCase();
    return (rows || []).filter(row =>
      Object.values(row).some(v => String(v).toLowerCase().includes(f))
    );
  }, [rows, filter]);

  const sortedRows = useMemo(() => {
    if (!sortCol) return filteredRows;
    return [...filteredRows].sort((a, b) => {
      const va = a[sortCol] ?? '';
      const vb = b[sortCol] ?? '';
      const cmp = String(va).localeCompare(String(vb), 'tr', { numeric: true });
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [filteredRows, sortCol, sortDir]);

  const exportCSV = () => {
    if (!columns || !sortedRows.length) return;
    const header = columns.join(';');
    const body = sortedRows.map(r => columns.map(c => String(r[c] ?? '')).join(';')).join('\n');
    const blob = new Blob(['\uFEFF' + header + '\n' + body], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title || 'veri'}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!columns || !columns.length) {
    return <div className="text-text-secondary text-sm p-4">Veri yok</div>;
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-brand-200 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-brand-200">
        <div className="flex items-center gap-3">
          {title && <h3 className="font-semibold text-text-primary">{title}</h3>}
          <span className="text-xs text-text-secondary bg-brand-50 px-2 py-1 rounded-full">
            {sortedRows.length} kayit
          </span>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Filtrele..."
            value={filter}
            onChange={e => setFilter(e.target.value)}
            className="px-3 py-1.5 text-sm border border-brand-200 rounded-lg focus:outline-none focus:border-brand-400"
          />
          <button
            onClick={onExport || exportCSV}
            className="px-3 py-1.5 text-sm bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-colors"
          >
            CSV
          </button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-brand-50">
              {columns.map(col => (
                <th
                  key={col}
                  onClick={() => handleSort(col)}
                  className="px-4 py-3 text-left font-medium text-text-secondary cursor-pointer hover:text-brand-500 select-none whitespace-nowrap"
                >
                  {col}
                  {sortCol === col && (
                    <span className="ml-1">{sortDir === 'asc' ? '\u2191' : '\u2193'}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedRows.map((row, i) => (
              <tr key={i} className="border-t border-brand-100 hover:bg-brand-50/50 transition-colors">
                {columns.map(col => (
                  <td key={col} className="px-4 py-2.5 whitespace-nowrap text-text-primary">
                    {row[col] ?? '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
