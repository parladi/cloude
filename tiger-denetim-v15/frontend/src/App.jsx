import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import TriggersPage from './pages/TriggersPage';
import DeletionsPage from './pages/DeletionsPage';
import ChangelogPage from './pages/ChangelogPage';
import SnapshotPage from './pages/SnapshotPage';
import JobsPage from './pages/JobsPage';
import QueryEditorPage from './pages/QueryEditorPage';
import ReportsPage from './pages/ReportsPage';
import ConnectionPage from './pages/ConnectionPage';

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/triggers" element={<TriggersPage />} />
          <Route path="/deletions" element={<DeletionsPage />} />
          <Route path="/changelog" element={<ChangelogPage />} />
          <Route path="/snapshot" element={<SnapshotPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/sql" element={<QueryEditorPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/connection" element={<ConnectionPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
