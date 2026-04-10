import { useNavigate } from 'react-router-dom';

export default function StatCard({ title, value, subtitle, status, link, icon }) {
  const navigate = useNavigate();
  const isDanger = status === 'danger';
  const isOk = status === 'ok';
  return (
    <div onClick={() => link && navigate(link)} className={`${isDanger ? 'bg-red-50 border-danger' : 'bg-white border-brand-200'} rounded-xl shadow-sm border-2 p-5 ${link ? 'cursor-pointer hover:shadow-md' : ''} transition-all duration-200`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-text-secondary mb-1">{title}</p>
          <p className={`text-2xl font-bold ${isDanger ? 'text-danger' : isOk ? 'text-success' : 'text-text-primary'}`}>{value}</p>
          {subtitle && <p className="text-xs text-text-secondary mt-1">{subtitle}</p>}
        </div>
        {icon && <div className={`p-2 rounded-lg ${isDanger ? 'bg-red-100 text-danger' : isOk ? 'bg-green-100 text-success' : 'bg-brand-100 text-brand-500'}`}>{icon}</div>}
      </div>
    </div>
  );
}
