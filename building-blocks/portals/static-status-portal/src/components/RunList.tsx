import React from 'react';
import { CustomerSafeStatus } from '../types';
import { StatusBadge } from './StatusBadge';

interface RunListProps {
  runs: CustomerSafeStatus[];
  onSelectRun: (id: string) => void;
}

export const RunList: React.FC<RunListProps> = ({ runs, onSelectRun }) => {
  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0 }}>Recent Activity</h2>
      </div>

      {runs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', backgroundColor: '#f9fafb', borderRadius: '8px', color: '#6b7280' }}>
          <p style={{ margin: '0 0 8px 0', fontSize: '1.125rem', fontWeight: 500 }}>No runs found</p>
          <p style={{ margin: 0 }}>Active and past pipeline runs will appear here.</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e5e7eb', textAlign: 'left' }}>
                <th style={{ padding: '12px', fontWeight: 600 }}>ID</th>
                <th style={{ padding: '12px', fontWeight: 600 }}>Status</th>
                <th style={{ padding: '12px', fontWeight: 600 }}>Summary</th>
                <th style={{ padding: '12px', fontWeight: 600 }}>Created At</th>
                <th style={{ padding: '12px', fontWeight: 600 }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={{ padding: '12px', fontSize: '0.875rem', fontWeight: 500 }}>{run.id}</td>
                  <td style={{ padding: '12px' }}>
                    <StatusBadge status={run.status} />
                  </td>
                  <td style={{ padding: '12px', fontSize: '0.875rem', color: '#4b5563', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {run.business_summary || '--'}
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
                        fontWeight: 500,
                        textDecoration: 'none'
                      }}
                    >
                      View details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
