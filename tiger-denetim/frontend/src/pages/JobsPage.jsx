import { useState, useEffect } from 'react';
import { api } from '../api';
import AlertBadge from '../components/AlertBadge';
import RefreshButton from '../components/RefreshButton';

export default function JobsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const result = await api.jobs();
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

  const jobs = data?.jobs || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-text-primary">Job Durumu</h2>
        <RefreshButton onClick={load} loading={loading} />
      </div>

      <div className={`p-4 rounded-xl border-2 ${data?.active === data?.total ? 'bg-green-50 border-success' : 'bg-red-50 border-danger'}`}>
        <p className={`font-bold ${data?.active === data?.total ? 'text-success' : 'text-danger'}`}>
          {data?.active}/{data?.total} Job Aktif
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {jobs.map(job => (
          <div key={job.job_adi} className="bg-white rounded-xl shadow-sm border border-brand-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-bold text-text-primary">{job.job_adi}</h3>
              </div>
              <AlertBadge status={job.durum} />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Durum:</span>
                <AlertBadge status={job.durum} />
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Son Calisma Durumu:</span>
                <AlertBadge status={job.son_calisma_durumu} />
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Son Calisma Tarihi:</span>
                <span className="text-text-primary">{job.tarih || '-'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Son Calisma Saati:</span>
                <span className="text-text-primary">{job.saat || '-'}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
