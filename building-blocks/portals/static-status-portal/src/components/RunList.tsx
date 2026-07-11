import React from 'react';
import { PipelineRun } from '../types';
import { StatusBadge } from './StatusBadge';

interface RunListProps {
  runs: PipelineRun[];
  onSelectRun: (id: string) => void;
  onStartRun: () => void;
}

export const RunList: React.FC<RunListProps> = ({ runs, onSelectRun, onStartRun }) => {
  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Pipeline Runs</h2>
        <button
          onClick={onStartRun}
          style={{
            backgroundColor: '#2563eb',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '4px',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          New Processing Run
        </button>
      </div>

      {runs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          No runs found. Start a new run to see it here.
        </div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #e5e7eb', textAlign: 'left' }}>
              <th style={{ padding: '12px' }}>ID</th>
              <th style={{ padding: '12px' }}>Type</th>
              <th style={{ padding: '12px' }}>Status</th>
              <th style={{ padding: '12px' }}>Created At</th>
              <th style={{ padding: '12px' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px', fontSize: '0.875rem' }}>{run.id}</td>
                <td style={{ padding: '12px' }}>{run.pipeline_type}</td>
                <td style={{ padding: '12px' }}>
                  <StatusBadge status={run.status} />
                </td>
                <td style={{ padding: '12px', fontSize: '0.875rem', color: '#6b7280' }}>
                  {new Date(run.created_at).toLocaleString()}
                </td>
                <td style={{ padding: '12px' }}>
                  <button
                    onClick={() => onSelectRun(run.id)}
                    style={{
                      color: '#2563eb',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: 0,
                      textDecoration: 'underline'
                    }}
                  >
                    View Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
