import { useState, useEffect, useCallback } from 'react';
import { api } from './api';
import { CustomerSafeStatus, FriendlyFailure } from './types';
import { RunList } from './components/RunList';
import { RunDetail } from './components/RunDetail';

function App() {
  const [runs, setRuns] = useState<CustomerSafeStatus[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [runDetail, setRunDetail] = useState<CustomerSafeStatus | null>(null);
  const [failureDetail, setFailureDetail] = useState<FriendlyFailure | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{message: string, isNotFound?: boolean} | null>(null);

  const fetchRuns = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRuns();
      setRuns(data);
    } catch (_err: any) {
      // Redact technical details even here, just in case
      setError({ message: 'The status service is temporarily unavailable. Please try again later.' });
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchRunDetail = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const detail = await api.getRunDetail(id);
      setRunDetail(detail);

      if (detail.status === 'failed') {
        const failure = await api.getRunFailure(id);
        setFailureDetail(failure);
      }
    } catch (err: any) {
      const isNotFound = err.status === 404;
      setError({
        message: isNotFound
          ? 'The requested run could not be found or you do not have permission to view it.'
          : 'Failed to load run details. Please try again.',
        isNotFound
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  useEffect(() => {
    if (selectedRunId) {
      fetchRunDetail(selectedRunId);
    } else {
      // Use functional updates or move these to handleBack to avoid cascading renders in effect
      // But for the shell, we'll keep it simple by moving to handleBack and resetting here only if needed.
    }
  }, [selectedRunId, fetchRunDetail]);

  const handleBack = () => {
    setSelectedRunId(null);
    setRunDetail(null);
    setFailureDetail(null);
    setError(null);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#ffffff', color: '#111827', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      <header style={{ backgroundColor: '#ffffff', borderBottom: '1px solid #e5e7eb', position: 'sticky', top: 0, zIndex: 10 }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '32px', height: '32px', backgroundColor: '#2563eb', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>A</div>
            <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.025em' }}>Status Portal</h1>
          </div>
          <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Customer View</div>
        </div>
      </header>

      <main style={{ maxWidth: '1000px', margin: '0 auto', padding: '24px 0' }}>
        {error && (
          <div style={{ margin: '0 20px 24px 20px', padding: '20px', backgroundColor: error.isNotFound ? '#f9fafb' : '#fef2f2', border: `1px solid ${error.isNotFound ? '#e5e7eb' : '#fee2e2'}`, borderRadius: '8px', textAlign: 'center' }}>
            <h2 style={{ margin: '0 0 8px 0', fontSize: '1.125rem', color: error.isNotFound ? '#374151' : '#991b1b' }}>
              {error.isNotFound ? 'Run Not Found' : 'Service Unavailable'}
            </h2>
            <p style={{ margin: '0 0 16px 0', color: error.isNotFound ? '#6b7280' : '#b91c1c' }}>{error.message}</p>
            <button
              onClick={error.isNotFound ? handleBack : () => selectedRunId ? fetchRunDetail(selectedRunId) : fetchRuns()}
              style={{
                padding: '8px 16px',
                backgroundColor: error.isNotFound ? '#ffffff' : '#991b1b',
                color: error.isNotFound ? '#374151' : '#ffffff',
                border: error.isNotFound ? '1px solid #d1d5db' : 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 500,
                fontSize: '0.875rem'
              }}
            >
              {error.isNotFound ? 'Back to Activity' : 'Retry Request'}
            </button>
          </div>
        )}

        {loading && !error && (
          <div style={{ padding: '60px', textAlign: 'center', color: '#6b7280' }}>
            <div style={{ display: 'inline-block', width: '24px', height: '24px', border: '3px solid #e5e7eb', borderTopColor: '#2563eb', borderRadius: '50%', animation: 'spin 1s linear infinite', marginBottom: '16px' }} />
            <p style={{ margin: 0, fontSize: '0.875rem' }}>Loading information...</p>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </div>
        )}

        {!loading && !error && (
          selectedRunId && runDetail ? (
            <RunDetail
              run={runDetail}
              failure={failureDetail}
              onBack={handleBack}
            />
          ) : (
            <RunList
              runs={runs}
              onSelectRun={setSelectedRunId}
            />
          )
        )}
      </main>

      <footer style={{ marginTop: 'auto', padding: '40px 20px', textAlign: 'center', borderTop: '1px solid #f3f4f6', color: '#9ca3af', fontSize: '0.75rem' }}>
        &copy; {new Date().getFullYear()} Azure Reference Kit • Customer-Safe Status Shell
      </footer>
    </div>
  );
}

export default App;
