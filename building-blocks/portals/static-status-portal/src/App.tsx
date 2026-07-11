import { useState, useEffect } from 'react';
import { api } from './api';
import { PipelineRun, PipelineRunDetail, Artifact, CostSummary } from './types';
import { RunList } from './components/RunList';
import { RunDetail } from './components/RunDetail';

function App() {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [runDetail, setRunDetail] = useState<PipelineRunDetail | null>(null);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [costSummary, setCostSummary] = useState<CostSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRuns();
  }, []);

  useEffect(() => {
    if (selectedRunId) {
      fetchRunDetail(selectedRunId);
    } else {
      setRunDetail(null);
      setArtifacts([]);
      setCostSummary(null);
    }
  }, [selectedRunId]);

  const fetchRuns = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRuns();
      setRuns(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch runs');
    } finally {
      setLoading(false);
    }
  };

  const fetchRunDetail = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const [detail, artifactData, costData] = await Promise.all([
        api.getRunDetail(id),
        api.getArtifacts(id),
        api.getCost(id)
      ]);
      setRunDetail(detail);
      setArtifacts(artifactData);
      setCostSummary(costData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch run details');
    } finally {
      setLoading(false);
    }
  };

  if (loading && runs.length === 0 && !selectedRunId) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading portal...</div>;
  }

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', fontFamily: 'system-ui, sans-serif' }}>
      <header style={{ padding: '20px', borderBottom: '1px solid #e5e7eb', marginBottom: '20px' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem' }}>AI Status Portal</h1>
      </header>

      <main>
        {error && (
          <div style={{ margin: '20px', padding: '16px', backgroundColor: '#fef2f2', color: '#991b1b', borderRadius: '4px' }}>
            <strong>Error:</strong> {error}
            <button
              onClick={() => selectedRunId ? fetchRunDetail(selectedRunId) : fetchRuns()}
              style={{ marginLeft: '16px', textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', color: '#991b1b' }}
            >
              Retry
            </button>
          </div>
        )}

        {selectedRunId && runDetail ? (
          <RunDetail
            run={runDetail}
            artifacts={artifacts}
            costSummary={costSummary}
            onBack={() => setSelectedRunId(null)}
            getDownloadUrl={api.getDownloadUrl}
          />
        ) : (
          <RunList
            runs={runs}
            onSelectRun={setSelectedRunId}
          />
        )}
      </main>

      {loading && (
        <div style={{ position: 'fixed', bottom: '20px', right: '20px', backgroundColor: 'white', padding: '8px 16px', borderRadius: '9999px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: '0.875rem' }}>
          Refreshing...
        </div>
      )}
    </div>
  );
}

export default App;
