import { CustomerSafeStatus, FriendlyFailure } from './types';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

// In a real SWA, these would come from the /api route.
// For the minimal shell, we support a fixture-backed mode for testing and local dev.
let useFixtures = true;

export const setUseFixtures = (value: boolean) => {
  useFixtures = value;
};

const FIXTURE_RUNS: CustomerSafeStatus[] = [
  {
    id: 'run-001',
    status: 'completed',
    business_summary: 'AI Analysis complete. All documents processed successfully.',
    progress_percent: 100,
    estimated_cost: 0.42,
    created_at: '2024-05-01T10:00:00Z',
    started_at: '2024-05-01T10:00:05Z',
    finished_at: '2024-05-01T10:02:30Z',
    safe_artifacts: [
      { name: 'summary.pdf', size_bytes: 125000, content_type: 'application/pdf' },
      { name: 'results.json', size_bytes: 4500, content_type: 'application/json' }
    ]
  },
  {
    id: 'run-002',
    status: 'failed',
    business_summary: 'Processing stopped due to an invalid document format.',
    progress_percent: 45,
    estimated_cost: 0.15,
    created_at: '2024-05-02T11:00:00Z',
    started_at: '2024-05-02T11:00:10Z',
    finished_at: '2024-05-02T11:01:45Z',
    safe_artifacts: []
  },
  {
    id: 'run-003',
    status: 'running',
    business_summary: 'Extracting entities from provided text...',
    progress_percent: 65,
    created_at: '2024-05-03T09:30:00Z',
    started_at: '2024-05-03T09:30:15Z'
  }
];

const FIXTURE_FAILURES: Record<string, FriendlyFailure> = {
  'run-002': {
    error_code: 'INVALID_INPUT_FORMAT',
    message: 'The uploaded file is not in a supported format. Please provide a PDF or high-resolution image.',
    correlation_id: 'err-12345-abcd'
  }
};

/**
 * Sanitizes raw status data to ensure only allowlisted fields are used.
 * This acts as the final client-side boundary enforcement.
 */
function sanitizeStatus(data: any): CustomerSafeStatus {
  return {
    id: String(data.id),
    status: data.status as any,
    business_summary: data.business_summary ? String(data.business_summary) : undefined,
    progress_percent: typeof data.progress_percent === 'number' ? data.progress_percent : undefined,
    estimated_cost: typeof data.estimated_cost === 'number' ? data.estimated_cost : undefined,
    created_at: String(data.created_at),
    started_at: data.started_at ? String(data.started_at) : undefined,
    finished_at: data.finished_at ? String(data.finished_at) : undefined,
    safe_artifacts: Array.isArray(data.safe_artifacts)
      ? data.safe_artifacts.map((a: any) => ({
          name: String(a.name),
          size_bytes: Number(a.size_bytes),
          content_type: a.content_type ? String(a.content_type) : undefined
        }))
      : undefined
  };
}

/**
 * Sanitizes raw failure data.
 */
function sanitizeFailure(data: any): FriendlyFailure {
  return {
    error_code: String(data.error_code),
    message: String(data.message),
    correlation_id: data.correlation_id ? String(data.correlation_id) : undefined
  };
}

export const api = {
  async getRuns(): Promise<CustomerSafeStatus[]> {
    if (useFixtures) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 500));
      return FIXTURE_RUNS.map(sanitizeStatus);
    }

    const response = await fetch('/api/runs');
    if (!response.ok) {
      throw new ApiError(response.status, 'Failed to fetch runs');
    }
    const data = await response.json();
    return (Array.isArray(data) ? data : []).map(sanitizeStatus);
  },

  async getRunDetail(id: string): Promise<CustomerSafeStatus> {
    if (useFixtures) {
      await new Promise(resolve => setTimeout(resolve, 300));
      const run = FIXTURE_RUNS.find(r => r.id === id);
      if (!run) throw new ApiError(404, 'Run not found');
      return sanitizeStatus(run);
    }

    const response = await fetch(`/api/runs/${id}`);
    if (!response.ok) {
      throw new ApiError(response.status, 'Failed to fetch run details');
    }
    const data = await response.json();
    return sanitizeStatus(data);
  },

  async getRunFailure(id: string): Promise<FriendlyFailure | null> {
    if (useFixtures) {
      return FIXTURE_FAILURES[id] ? sanitizeFailure(FIXTURE_FAILURES[id]) : null;
    }

    const response = await fetch(`/api/runs/${id}/failure`);
    if (response.status === 404) return null;
    if (!response.ok) return null;
    const data = await response.json();
    return sanitizeFailure(data);
  },

  getDownloadUrl(runId: string, artifactName: string): string {
    return `/api/runs/${runId}/artifacts/${encodeURIComponent(artifactName)}/download`;
  }
};
