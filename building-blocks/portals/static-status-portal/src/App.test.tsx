import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';
import { api } from './api';

vi.mock('./api', () => ({
  api: {
    getRuns: vi.fn(),
    getRunDetail: vi.fn(),
    getArtifacts: vi.fn(),
    getCost: vi.fn(),
    startRun: vi.fn(),
    getDownloadUrl: vi.fn((id) => `/api/artifacts/${id}/download`)
  }
}));

const mockRuns = [
  {
    id: 'run-1',
    customer_id: 'cust-1',
    pipeline_type: 'OCR',
    status: 'completed',
    created_at: new Date().toISOString()
  }
];

const mockDetail = {
  ...mockRuns[0],
  business_summary: 'Success summary',
  steps: [
    { name: 'OCR Step', status: 'completed', output_summary: 'Text extracted' }
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
    vi.mocked(api.getArtifacts).mockResolvedValue([]);
    vi.mocked(api.getCost).mockResolvedValue(1.50);

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
    expect(screen.getByText('Est. Cost: $1.50')).toBeInTheDocument();
  });

  it('goes back to list view when clicking Back', async () => {
    vi.mocked(api.getRuns).mockResolvedValue(mockRuns);
    vi.mocked(api.getRunDetail).mockResolvedValue(mockDetail);
    vi.mocked(api.getArtifacts).mockResolvedValue([]);
    vi.mocked(api.getCost).mockResolvedValue(0);

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
