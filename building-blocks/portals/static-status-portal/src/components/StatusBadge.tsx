import React from 'react';
import { PipelineStatus } from '../types';

interface StatusBadgeProps {
  status: PipelineStatus;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getColor = () => {
    switch (status) {
      case 'completed':
        return { bg: '#dcfce7', text: '#166534' }; // Green
      case 'failed':
        return { bg: '#fee2e2', text: '#991b1b' }; // Red
      case 'running':
        return { bg: '#dbeafe', text: '#1e40af' }; // Blue
      case 'pending':
        return { bg: '#f3f4f6', text: '#374151' }; // Gray
      case 'cancelled':
        return { bg: '#f3f4f6', text: '#374151' }; // Gray
      default:
        return { bg: '#f3f4f6', text: '#374151' };
    }
  };

  const { bg, text } = getColor();

  return (
    <span
      style={{
        backgroundColor: bg,
        color: text,
        padding: '2px 8px',
        borderRadius: '9999px',
        fontSize: '0.875rem',
        fontWeight: 500,
        textTransform: 'capitalize'
      }}
    >
      {status}
    </span>
  );
};
