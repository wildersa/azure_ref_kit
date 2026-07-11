import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';
import { api } from './api';
import { Artifact, CostSummary, PipelineRun, PipelineRunDetail } from './types';

vi.mock('./api', () => ({
  api: {
    getRuns: vi.fn(),
    getRunDetail: vi.fn(),
    getArtifacts: vi.fn(),
    getCost: vi.fn(),
    getDownloadUrl: vi.fn((id) => `/api/artifacts/${id}/download`)
  }
}));

const mockRuns: PipelineRun[] = [
  {
    id: 'run-1',
    customer_id: 'cust-1',
    pipeline_type: 'OCR',
    status: 'completed',
    created_at: new Date().toISOString()
  }
];

const mockDetail: PipelineRunDetail = {
  ...mockRuns[0],
  business_summary: 'Success summary',
  steps: [
    { run_id: 'run-1', name: 'OCR Step', status: 'completed', output_summary: 'Text extracted' }
  ]
};

const mockCostSummary: CostSummary = {
  run_id: 'run-1',
  total_estimated_amount: 1.50,
  currency: 'USD',
  breakdown: [
    { category: 'ai_tokens', estimated_amount: 1.00 },
    { category: 'storage', estimated_amount: 0.50 }
  ]
};

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', async () => {
    vi.mocked(api.getRuns).mockReturnValue(new Promise(() => {})); // Never resolves
    render(<App />);
    expect(screen.getByText(/Loading portal.../i)).toBeInTheDocument();
  });

  it('renders run list after loading', async () => {
    vi.mocked(api.getRuns).mockResolvedValue(mockRuns);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('AI Status Portal')).toBeInTheDocument();
    });

    expect(screen.getByText('run-1')).toBeInTheDocument();
    expect(screen.getByText('OCR')).toBeInTheDocument();
    expect(screen.getByText('completed')).toBeInTheDocument();
  });

  it('renders error state on fetch failure', async () => {
    vi.mocked(api.getRuns).mockRejectedValue(new Error('Network error'));
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/Network error/i)).toBeInTheDocument();
  });

  it('switches to detail view when clicking View Details', async () => {
    vi.mocked(api.getRuns).mockResolvedValue(mockRuns);
    vi.mocked(api.getRunDetail).mockResolvedValue(mockDetail);
    vi.mocked(api.getArtifacts).mockResolvedValue([] as Artifact[]);
    vi.mocked(api.getCost).mockResolvedValue(mockCostSummary);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('View Details')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('View Details'));

    await waitFor(() => {
      expect(screen.getByText('Run Details: run-1')).toBeInTheDocument();
    });

    expect(screen.getByText('Success summary')).toBeInTheDocument();
    expect(screen.getByText('OCR Step')).toBeInTheDocument();
    expect(screen.getByText('Est. Cost: 1.50 USD')).toBeInTheDocument();
    expect(screen.getByText(/ai tokens/i)).toBeInTheDocument();
    expect(screen.getByText('1.00 USD')).toBeInTheDocument();
  });

  it('goes back to list view when clicking Back', async () => {
    vi.mocked(api.getRuns).mockResolvedValue(mockRuns);
    vi.mocked(api.getRunDetail).mockResolvedValue(mockDetail);
    vi.mocked(api.getArtifacts).mockResolvedValue([] as Artifact[]);
    vi.mocked(api.getCost).mockResolvedValue(mockCostSummary);

    render(<App />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('View Details'));
    });

    await waitFor(() => {
      expect(screen.getByText(/Back to Dashboard/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Back to Dashboard/i));

    await waitFor(() => {
      expect(screen.getByText('Pipeline Runs')).toBeInTheDocument();
    });
  });
});
