export default function AlertBadge({ status, label }) {
  if (status === 'ok' || status === 'AKTIF' || status === 'BASARILI')
    return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"><span className="w-1.5 h-1.5 rounded-full bg-green-500" />{label || status}</span>;
  if (status === 'danger' || status === 'KAPALI' || status === 'BASARISIZ' || status === 'ALARM')
    return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 animate-pulse-danger"><span className="w-1.5 h-1.5 rounded-full bg-red-500" />{label || status}</span>;
  if (status === 'warning' || status === 'NORMAL')
    return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"><span className="w-1.5 h-1.5 rounded-full bg-blue-500" />{label || status}</span>;
  return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">{label || status}</span>;
}
