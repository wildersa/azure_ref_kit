import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';
import { api } from './api';
import { CustomerSafeStatus, FriendlyFailure } from './types';

vi.mock('./api', () => ({
  api: {
    getRuns: vi.fn(),
    getRunDetail: vi.fn(),
    getRunFailure: vi.fn(),
    getDownloadUrl: vi.fn((runId, name) => `/api/runs/${runId}/artifacts/${name}/download`)
  }
}));

const mockRuns: CustomerSafeStatus[] = [
  {
    id: 'run-1',
    status: 'completed',
    business_summary: 'Success summary',
    created_at: new Date().toISOString()
  }
];

const mockDetail: CustomerSafeStatus = {
  ...mockRuns[0],
  progress_percent: 100,
  estimated_cost: 1.50,
  safe_artifacts: [
    { name: 'result.pdf', size_bytes: 1024, content_type: 'application/pdf' }
  ]
};

const mockFailure: FriendlyFailure = {
  error_code: 'ERR_001',
  message: 'Friendly error message',
  correlation_id: 'corr-123'
};

describe('App Component (P0 Boundary Proof)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state with non-technical indicator', async () => {
    vi.mocked(api.getRuns).mockReturnValue(new Promise(() => {}));
    render(<App />);
    expect(screen.getByText(/Loading information.../i)).toBeInTheDocument();
    expect(screen.queryByText(/debug/i)).not.toBeInTheDocument();
  });

  it('renders empty state when no runs found', async () => {
    vi.mocked(api.getRuns).mockResolvedValue([]);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/No runs found/i)).toBeInTheDocument();
    });
  });

  it('renders friendly not-found state', async () => {
    vi.mocked(api.getRuns).mockResolvedValue(mockRuns);
    vi.mocked(api.getRunDetail).mockRejectedValue({ status: 404, message: 'Not Found' });

    render(<App />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('View details'));
    });

    await waitFor(() => {
      expect(screen.getByText(/Run Not Found/i)).toBeInTheDocument();
      expect(screen.getByText(/requested run could not be found/i)).toBeInTheDocument();
    });
  });

  it('renders friendly service unavailable state', async () => {
    vi.mocked(api.getRuns).mockRejectedValue(new Error('Fatal exception'));
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Service Unavailable/i)).toBeInTheDocument();
      expect(screen.getByText(/status service is temporarily unavailable/i)).toBeInTheDocument();
    });
    // Ensure "Fatal exception" or stack trace is NOT rendered
    expect(screen.queryByText(/Fatal exception/i)).not.toBeInTheDocument();
  });

  it('proves forbidden fields are NOT rendered in detail view', async () => {
    // Inject forbidden fields into the raw data mock (API adapter should filter them,
    // but we test the component boundary here as well)
    const dataWithForbiddenFields = {
      ...mockDetail,
      internal_id: 'sub-123-abc',
      raw_logs: 'SELECT * FROM secret_table',
      system_prompt: 'You are a helpful assistant...'
    } as any;

    vi.mocked(api.getRuns).mockResolvedValue(mockRuns);
    vi.mocked(api.getRunDetail).mockResolvedValue(dataWithForbiddenFields);

    render(<App />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('View details'));
    });

    await waitFor(() => {
      expect(screen.getByText('Run run-1')).toBeInTheDocument();
    });

    // Verify allowed fields
    expect(screen.getByText('Success summary')).toBeInTheDocument();

    // Verify forbidden fields are MISSING
    expect(screen.queryByText(/sub-123-abc/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/secret_table/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/helpful assistant/i)).not.toBeInTheDocument();
  });

  it('renders progress bar for running status', async () => {
    const runningRun = {
        ...mockRuns[0],
        status: 'running' as const,
        progress_percent: 42,
        business_summary: 'Working on it'
    };
    vi.mocked(api.getRuns).mockResolvedValue([runningRun]);
    vi.mocked(api.getRunDetail).mockResolvedValue(runningRun);

    render(<App />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('View details'));
    });

    await waitFor(() => {
      expect(screen.getByText('Working on it')).toBeInTheDocument();
    });

    // Check for progress bar (div with width 42%)
    const progressBar = screen.getByRole('main').querySelector('div[style*="width: 42%"]');
    expect(progressBar).toBeInTheDocument();
  });

  it('renders friendly failure in detail view', async () => {
    const failedRun = { ...mockRuns[0], id: 'run-failed', status: 'failed' as const };
    vi.mocked(api.getRuns).mockResolvedValue([failedRun]);
    vi.mocked(api.getRunDetail).mockResolvedValue(failedRun);
    vi.mocked(api.getRunFailure).mockResolvedValue(mockFailure);

    render(<App />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('View details'));
    });

    await waitFor(() => {
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    expect(screen.getByText('Friendly error message')).toBeInTheDocument();
    expect(screen.getByText(/ERR_001/)).toBeInTheDocument();
    expect(screen.getByText(/corr-123/)).toBeInTheDocument();
  });
});
