import React from 'react';
import { CustomerSafeStatus, FriendlyFailure } from '../types';
import { StatusBadge } from './StatusBadge';

interface RunDetailProps {
  run: CustomerSafeStatus;
  failure: FriendlyFailure | null;
  onBack: () => void;
}

export const RunDetail: React.FC<RunDetailProps> = ({ run, failure, onBack }) => {
  return (
    <div style={{ padding: '20px' }}>
      <button
        onClick={onBack}
        style={{ marginBottom: '20px', cursor: 'pointer', background: 'none', border: 'none', color: '#2563eb', padding: 0, fontSize: '0.875rem' }}
      >
        &larr; Back to Activity
      </button>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '30px', flexWrap: 'wrap', gap: '20px' }}>
        <div>
          <h2 style={{ margin: '0 0 8px 0' }}>Run {run.id}</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <StatusBadge status={run.status} />
            <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              Created {new Date(run.created_at).toLocaleString()}
            </span>
          </div>
        </div>
        {run.estimated_cost != null && (
          <div style={{ padding: '12px 16px', backgroundColor: '#f0f9ff', border: '1px solid #e0f2fe', borderRadius: '8px', textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: '#0369a1', textTransform: 'uppercase', letterSpacing: '0.025em', fontWeight: 600 }}>Est. Cost</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0c4a6e' }}>${run.estimated_cost.toFixed(2)}</div>
          </div>
        )}
      </div>

      <div style={{ backgroundColor: '#f9fafb', padding: '24px', borderRadius: '12px', marginBottom: '30px' }}>
        <h3 style={{ margin: '0 0 12px 0', fontSize: '0.875rem', textTransform: 'uppercase', color: '#6b7280', letterSpacing: '0.05em' }}>Progress Summary</h3>
        <p style={{ margin: '0 0 20px 0', fontSize: '1.125rem', fontWeight: 500 }}>{run.business_summary || 'No summary available.'}</p>

        {run.status === 'running' && run.progress_percent != null && (
          <div style={{ width: '100%', height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
            <div
              style={{
                width: `${run.progress_percent}%`,
                height: '100%',
                backgroundColor: '#3b82f6',
                transition: 'width 0.5s ease-out'
              }}
            />
          </div>
        )}
      </div>

      {run.status === 'failed' && failure && (
        <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fee2e2', color: '#991b1b', padding: '20px', borderRadius: '12px', marginBottom: '30px' }}>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '1rem', fontWeight: 700 }}>Something went wrong</h3>
          <p style={{ margin: '0 0 16px 0', lineHeight: 1.5 }}>{failure.message}</p>
          <div style={{ display: 'flex', gap: '24px', fontSize: '0.75rem', opacity: 0.8 }}>
            <div><span style={{ fontWeight: 600 }}>Error Code:</span> {failure.error_code}</div>
            {failure.correlation_id && <div><span style={{ fontWeight: 600 }}>Correlation ID:</span> {failure.correlation_id}</div>}
          </div>
        </div>
      )}

      {/* Pipeline Steps Timeline */}
      <div style={{ border: '1px solid #e5e7eb', borderRadius: '12px', overflow: 'hidden', marginBottom: '30px' }}>
        <div style={{ backgroundColor: '#f8fafc', padding: '16px 20px', borderBottom: '1px solid #e5e7eb' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>Pipeline Execution Timeline</h3>
        </div>
        <div style={{ padding: '20px' }}>
          {!run.steps || run.steps.length === 0 ? (
            <p style={{ color: '#6b7280', margin: 0, fontStyle: 'italic' }}>No detailed step information available.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
              {run.steps.map((step, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '16px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={{
                      width: '12px',
                      height: '12px',
                      borderRadius: '50%',
                      backgroundColor: step.status === 'completed' ? '#22c55e' : step.status === 'running' ? '#3b82f6' : step.status === 'failed' ? '#ef4444' : '#d1d5db',
                      marginTop: '4px',
                      zIndex: 1
                    }} />
                    {idx < run.steps!.length - 1 && (
                      <div style={{ width: '2px', flexGrow: 1, backgroundColor: '#e5e7eb', margin: '4px 0' }} />
                    )}
                  </div>
                  <div style={{ paddingBottom: idx < run.steps!.length - 1 ? '24px' : '0', flexGrow: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
                      <div style={{ fontWeight: 600, fontSize: '0.9375rem' }}>{step.name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                        {step.status.toUpperCase()}
                      </div>
                    </div>
                    {step.input_summary && <div style={{ fontSize: '0.8125rem', color: '#4b5563', marginBottom: '4px' }}>{step.input_summary}</div>}
                    {step.output_summary && <div style={{ fontSize: '0.8125rem', color: '#059669', fontStyle: 'italic' }}>{step.output_summary}</div>}
                    {step.friendly_error && <div style={{ fontSize: '0.8125rem', color: '#dc2626', marginTop: '4px' }}>{step.friendly_error}</div>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div style={{ border: '1px solid #e5e7eb', borderRadius: '12px', overflow: 'hidden' }}>
        <div style={{ backgroundColor: '#f8fafc', padding: '16px 20px', borderBottom: '1px solid #e5e7eb' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>Output Artifacts</h3>
        </div>
        <div style={{ padding: '20px' }}>
          {!run.safe_artifacts || run.safe_artifacts.length === 0 ? (
            <p style={{ color: '#6b7280', margin: 0, fontStyle: 'italic' }}>No artifacts are available for this run.</p>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '16px' }}>
              {run.safe_artifacts.map((artifact, idx) => (
                <div key={idx} style={{ padding: '16px', border: '1px solid #f3f4f6', borderRadius: '8px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px', wordBreak: 'break-all' }}>{artifact.name}</div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '12px' }}>
                      {(artifact.size_bytes / 1024).toFixed(1)} KB • {artifact.content_type || 'Unknown'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
