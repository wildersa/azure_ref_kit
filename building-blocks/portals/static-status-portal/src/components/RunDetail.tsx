import React from 'react';
import { PipelineRunDetail, Artifact, CostSummary } from '../types';
import { StatusBadge } from './StatusBadge';

interface RunDetailProps {
  run: PipelineRunDetail;
  artifacts: Artifact[];
  costSummary: CostSummary | null;
  onBack: () => void;
  getDownloadUrl: (id: string) => string;
}

export const RunDetail: React.FC<RunDetailProps> = ({ run, artifacts, costSummary, onBack, getDownloadUrl }) => {
  return (
    <div style={{ padding: '20px' }}>
      <button
        onClick={onBack}
        style={{ marginBottom: '20px', cursor: 'pointer', background: 'none', border: 'none', color: '#2563eb' }}
      >
        &larr; Back to Dashboard
      </button>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '30px' }}>
        <div>
          <h2 style={{ margin: '0 0 8px 0' }}>Run Details: {run.id}</h2>
          <p style={{ color: '#6b7280', margin: 0 }}>{run.pipeline_type}</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <StatusBadge status={run.status} />
          {costSummary !== null && (
            <div style={{ marginTop: '8px', fontWeight: 'bold' }}>
              Est. Cost: {costSummary.total_estimated_amount.toFixed(2)} {costSummary.currency}
            </div>
          )}
        </div>
      </div>

      {run.business_summary && (
        <div style={{ backgroundColor: '#f9fafb', padding: '16px', borderRadius: '8px', marginBottom: '30px' }}>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '1rem' }}>Business Summary</h3>
          <p style={{ margin: 0 }}>{run.business_summary}</p>
        </div>
      )}

      {run.friendly_error && (
        <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fee2e2', color: '#991b1b', padding: '16px', borderRadius: '8px', marginBottom: '30px' }}>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '1rem' }}>Friendly Error</h3>
          <p style={{ margin: 0 }}>{run.friendly_error}</p>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px' }}>
        <div>
          <h3 style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: '8px' }}>Timeline</h3>
          <div style={{ marginTop: '16px' }}>
            {run.steps.length === 0 ? (
              <p style={{ color: '#6b7280' }}>No steps recorded yet.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {run.steps.map((step, idx) => (
                  <div key={idx} style={{ borderLeft: '2px solid #e5e7eb', paddingLeft: '16px', position: 'relative' }}>
                    <div style={{
                      position: 'absolute',
                      left: '-9px',
                      top: '0',
                      width: '16px',
                      height: '16px',
                      borderRadius: '50%',
                      backgroundColor: step.status === 'completed' ? '#10b981' : '#e5e7eb'
                    }} />
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: 'bold' }}>{step.name}</span>
                      <StatusBadge status={step.status} />
                    </div>
                    {step.output_summary && (
                      <p style={{ fontSize: '0.875rem', color: '#4b5563', margin: '4px 0 0 0' }}>{step.output_summary}</p>
                    )}
                    {step.friendly_error && (
                      <p style={{ fontSize: '0.875rem', color: '#dc2626', margin: '4px 0 0 0' }}>{step.friendly_error}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <h3 style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: '8px' }}>Artifacts</h3>
          <div style={{ marginTop: '16px' }}>
            {artifacts.length === 0 ? (
              <p style={{ color: '#6b7280' }}>No artifacts available.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {artifacts.map((artifact) => (
                  <li key={artifact.id} style={{ marginBottom: '12px', padding: '8px', border: '1px solid #f3f4f6', borderRadius: '4px' }}>
                    <div style={{ fontWeight: 500, fontSize: '0.875rem' }}>{artifact.safe_name}</div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                      <span>{artifact.kind}</span>
                      {artifact.size_bytes && <span>{(artifact.size_bytes / 1024).toFixed(1)} KB</span>}
                    </div>
                    <a
                      href={artifact.download_url || getDownloadUrl(artifact.id)}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'block',
                        marginTop: '8px',
                        fontSize: '0.875rem',
                        color: '#2563eb',
                        textDecoration: 'none'
                      }}
                    >
                      Download
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {costSummary && costSummary.breakdown.length > 0 && (
            <div style={{ marginTop: '30px' }}>
              <h3 style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: '8px' }}>Cost Breakdown</h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: '16px 0 0 0', fontSize: '0.875rem' }}>
                {costSummary.breakdown.map((item, idx) => (
                  <li key={idx} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ textTransform: 'capitalize' }}>{item.category.replace('_', ' ')}</span>
                    <span>{item.estimated_amount.toFixed(2)} {costSummary.currency}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
