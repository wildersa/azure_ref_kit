import { CustomerSafeStatus, FriendlyFailure, PipelineStatus } from './types';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
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

const VALID_STATUSES: PipelineStatus[] = ['pending', 'running', 'completed', 'failed', 'cancelled'];

/**
 * Validates and sanitizes raw status data against the CustomerSafeStatus schema.
 * Fails closed if required fields are missing or types are invalid.
 */
function validateAndSanitizeStatus(data: any): CustomerSafeStatus {
  if (!data || typeof data !== 'object') throw new ValidationError('Invalid status object');

  // Required fields
  if (typeof data.id !== 'string' || !data.id) throw new ValidationError('Missing or invalid id');
  if (!VALID_STATUSES.includes(data.status)) throw new ValidationError(`Invalid status: ${data.status}`);
  if (typeof data.created_at !== 'string' || isNaN(Date.parse(data.created_at))) throw new ValidationError('Missing or invalid created_at');

  const sanitized: CustomerSafeStatus = {
    id: data.id,
    status: data.status,
    created_at: data.created_at
  };

  // Optional fields with strict type checking
  if (data.business_summary !== undefined) {
    if (typeof data.business_summary !== 'string') throw new ValidationError('Invalid business_summary');
    sanitized.business_summary = data.business_summary;
  }

  if (data.progress_percent !== undefined && data.progress_percent !== null) {
    if (typeof data.progress_percent !== 'number' || data.progress_percent < 0 || data.progress_percent > 100) {
        throw new ValidationError('Invalid progress_percent');
    }
    sanitized.progress_percent = data.progress_percent;
  }

  if (data.estimated_cost !== undefined && data.estimated_cost !== null) {
    if (typeof data.estimated_cost !== 'number') throw new ValidationError('Invalid estimated_cost');
    sanitized.estimated_cost = data.estimated_cost;
  }

  if (data.started_at) {
    if (typeof data.started_at !== 'string' || isNaN(Date.parse(data.started_at))) throw new ValidationError('Invalid started_at');
    sanitized.started_at = data.started_at;
  }

  if (data.finished_at) {
    if (typeof data.finished_at !== 'string' || isNaN(Date.parse(data.finished_at))) throw new ValidationError('Invalid finished_at');
    sanitized.finished_at = data.finished_at;
  }

  if (Array.isArray(data.safe_artifacts)) {
    sanitized.safe_artifacts = data.safe_artifacts.map((a: any, idx: number) => {
      if (typeof a.name !== 'string' || !a.name) throw new ValidationError(`Artifact at index ${idx} missing name`);
      if (typeof a.size_bytes !== 'number') throw new ValidationError(`Artifact at index ${idx} missing or invalid size_bytes`);

      return {
        name: a.name,
        size_bytes: a.size_bytes,
        content_type: typeof a.content_type === 'string' ? a.content_type : undefined
      };
    });
  }

  return sanitized;
}

/**
 * Validates and sanitizes raw failure data.
 */
function validateAndSanitizeFailure(data: any): FriendlyFailure {
  if (!data || typeof data !== 'object') throw new ValidationError('Invalid failure object');

  if (typeof data.error_code !== 'string' || !data.error_code) throw new ValidationError('Missing or invalid error_code');
  if (typeof data.message !== 'string' || !data.message) throw new ValidationError('Missing or invalid message');

  return {
    error_code: data.error_code,
    message: data.message,
    correlation_id: typeof data.correlation_id === 'string' ? data.correlation_id : undefined
  };
}

export const api = {
  async getRuns(): Promise<CustomerSafeStatus[]> {
    if (useFixtures) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 500));
      return FIXTURE_RUNS.map(validateAndSanitizeStatus);
    }

    const response = await fetch('/api/runs');
    if (!response.ok) {
      throw new ApiError(response.status, 'Failed to fetch runs');
    }
    const data = await response.json();
    if (!Array.isArray(data)) throw new ValidationError('API response for runs is not an array');
    return data.map(validateAndSanitizeStatus);
  },

  async getRunDetail(id: string): Promise<CustomerSafeStatus> {
    if (useFixtures) {
      await new Promise(resolve => setTimeout(resolve, 300));
      const run = FIXTURE_RUNS.find(r => r.id === id);
      if (!run) throw new ApiError(404, 'Run not found');
      return validateAndSanitizeStatus(run);
    }

    const response = await fetch(`/api/runs/${id}`);
    if (!response.ok) {
      throw new ApiError(response.status, 'Failed to fetch run details');
    }
    const data = await response.json();
    return validateAndSanitizeStatus(data);
  },

  async getRunFailure(id: string): Promise<FriendlyFailure | null> {
    if (useFixtures) {
      return FIXTURE_FAILURES[id] ? validateAndSanitizeFailure(FIXTURE_FAILURES[id]) : null;
    }

    const response = await fetch(`/api/runs/${id}/failure`);
    if (response.status === 404) return null;
    if (!response.ok) return null;
    const data = await response.json();
    return validateAndSanitizeFailure(data);
  },

  getDownloadUrl(runId: string, artifactName: string): string {
    return `/api/runs/${runId}/artifacts/${encodeURIComponent(artifactName)}/download`;
  }
};
