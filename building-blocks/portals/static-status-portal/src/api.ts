import { CustomerSafeStatus, FriendlyFailure, PipelineStatus, PipelineStep, StepStatus } from './types';

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
    ],
    steps: [
      {
        run_id: 'run-001',
        name: 'Document Upload',
        status: 'completed',
        input_summary: 'invoice_123.pdf',
        output_summary: 'Upload successful',
        started_at: '2024-05-01T10:00:05Z',
        finished_at: '2024-05-01T10:00:10Z'
      },
      {
        run_id: 'run-001',
        name: 'AI Text Extraction',
        status: 'completed',
        input_summary: 'Processing PDF content...',
        output_summary: 'Successfully extracted 1,500 tokens',
        started_at: '2024-05-01T10:00:12Z',
        finished_at: '2024-05-01T10:01:45Z'
      },
      {
        run_id: 'run-001',
        name: 'Validation & Publishing',
        status: 'completed',
        input_summary: 'Checking extracted fields...',
        output_summary: 'All fields valid. Published to database.',
        started_at: '2024-05-01T10:01:48Z',
        finished_at: '2024-05-01T10:02:30Z'
      }
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
    safe_artifacts: [],
    steps: [
      {
        run_id: 'run-002',
        name: 'Document Upload',
        status: 'completed',
        input_summary: 'corrupted_file.dat',
        output_summary: 'Upload successful',
        started_at: '2024-05-02T11:00:10Z',
        finished_at: '2024-05-02T11:00:15Z'
      },
      {
        run_id: 'run-002',
        name: 'Format Validation',
        status: 'failed',
        input_summary: 'Validating file extension...',
        output_summary: 'Unsupported format detected',
        friendly_error: 'The uploaded file is not in a supported format. Please provide a PDF.',
        started_at: '2024-05-02T11:00:18Z',
        finished_at: '2024-05-02T11:01:45Z'
      }
    ]
  },
  {
    id: 'run-003',
    status: 'running',
    business_summary: 'Extracting entities from provided text...',
    progress_percent: 65,
    created_at: '2024-05-03T09:30:00Z',
    started_at: '2024-05-03T09:30:15Z',
    steps: [
      {
        run_id: 'run-003',
        name: 'Text Submission',
        status: 'completed',
        input_summary: 'Text provided via API',
        output_summary: 'Input received',
        started_at: '2024-05-03T09:30:15Z',
        finished_at: '2024-05-03T09:30:18Z'
      },
      {
        run_id: 'run-003',
        name: 'AI Extraction',
        status: 'running',
        input_summary: 'Running LLM analysis...',
        started_at: '2024-05-03T09:30:20Z'
      },
      {
        run_id: 'run-003',
        name: 'Result Generation',
        status: 'pending'
      }
    ]
  }
];

const FIXTURE_FAILURES: Record<string, FriendlyFailure> = {
  'run-002': {
    error_code: 'INVALID_INPUT_FORMAT',
    message: 'The uploaded file is not in a supported format. Please provide a PDF or high-resolution image.',
    correlation_id: 'err-12345-abcd'
  }
};

const VALID_STATUSES: PipelineStatus[] = ['pending', 'running', 'waiting_input', 'failed', 'completed', 'cancelled'];
const VALID_STEP_STATUSES: StepStatus[] = ['pending', 'running', 'waiting_input', 'failed', 'completed', 'skipped', 'cancelled'];

// Constants for payload bounds (aligned with shared/contracts)
const MAX_STR_LEN = 64;
const MAX_LONG_STR_LEN = 2048;
const MAX_ARTIFACTS = 100;

/**
 * Validates and sanitizes a single pipeline step.
 */
function validateAndSanitizeStep(data: any): PipelineStep {
  if (!data || typeof data !== 'object') throw new ValidationError('Invalid step object');

  if (typeof data.run_id !== 'string' || !data.run_id || data.run_id.length > MAX_STR_LEN) throw new ValidationError('Step missing or invalid run_id');
  if (typeof data.name !== 'string' || !data.name || data.name.length > MAX_STR_LEN) throw new ValidationError('Step missing or invalid name');
  if (!VALID_STEP_STATUSES.includes(data.status)) throw new ValidationError(`Invalid step status: ${data.status}`);

  const sanitized: PipelineStep = {
    run_id: data.run_id,
    name: data.name,
    status: data.status
  };

  if (data.input_summary !== undefined && data.input_summary !== null) {
    if (typeof data.input_summary !== 'string' || data.input_summary.length > MAX_LONG_STR_LEN) throw new ValidationError('Invalid step input_summary');
    sanitized.input_summary = data.input_summary;
  }

  if (data.output_summary !== undefined && data.output_summary !== null) {
    if (typeof data.output_summary !== 'string' || data.output_summary.length > MAX_LONG_STR_LEN) throw new ValidationError('Invalid step output_summary');
    sanitized.output_summary = data.output_summary;
  }

  if (data.friendly_error !== undefined && data.friendly_error !== null) {
    if (typeof data.friendly_error !== 'string' || data.friendly_error.length > MAX_LONG_STR_LEN) throw new ValidationError('Invalid step friendly_error');
    sanitized.friendly_error = data.friendly_error;
  }

  if (data.started_at) {
    if (typeof data.started_at !== 'string' || isNaN(Date.parse(data.started_at))) throw new ValidationError('Invalid step started_at');
    sanitized.started_at = data.started_at;
  }

  if (data.finished_at) {
    if (typeof data.finished_at !== 'string' || isNaN(Date.parse(data.finished_at))) throw new ValidationError('Invalid step finished_at');
    sanitized.finished_at = data.finished_at;
  }

  if (Array.isArray(data.artifacts)) {
    if (data.artifacts.length > MAX_ARTIFACTS) throw new ValidationError('Too many step artifacts');
    sanitized.artifacts = data.artifacts.map((a: any, idx: number) => {
        if (typeof a !== 'string' || a.length > 128) throw new ValidationError(`Step artifact at index ${idx} is invalid`);
        return a;
    });
  }

  if (data.retry_count !== undefined && data.retry_count !== null) {
    if (typeof data.retry_count !== 'number' || data.retry_count < 0) throw new ValidationError('Invalid step retry_count');
    sanitized.retry_count = data.retry_count;
  }

  return sanitized;
}

/**
 * Validates and sanitizes raw status data against the CustomerSafeStatus schema.
 * Fails closed if required fields are missing or types are invalid.
 */
function validateAndSanitizeStatus(data: any): CustomerSafeStatus {
  if (!data || typeof data !== 'object') throw new ValidationError('Invalid status object');

  // Required fields
  if (typeof data.id !== 'string' || !data.id || data.id.length > MAX_STR_LEN) throw new ValidationError('Missing or invalid id');
  if (!VALID_STATUSES.includes(data.status)) throw new ValidationError(`Invalid status: ${data.status}`);
  if (typeof data.created_at !== 'string' || isNaN(Date.parse(data.created_at))) throw new ValidationError('Missing or invalid created_at');

  const sanitized: CustomerSafeStatus = {
    id: data.id,
    status: data.status,
    created_at: data.created_at
  };

  // Optional fields with strict type checking
  if (data.business_summary !== undefined) {
    if (typeof data.business_summary !== 'string' || data.business_summary.length > MAX_LONG_STR_LEN) throw new ValidationError('Invalid business_summary');
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
    if (data.safe_artifacts.length > MAX_ARTIFACTS) throw new ValidationError('Too many artifacts');
    sanitized.safe_artifacts = data.safe_artifacts.map((a: any, idx: number) => {
      if (typeof a.name !== 'string' || !a.name || a.name.length > 128) throw new ValidationError(`Artifact at index ${idx} invalid name`);
      if (typeof a.size_bytes !== 'number') throw new ValidationError(`Artifact at index ${idx} missing or invalid size_bytes`);

      return {
        name: a.name,
        size_bytes: a.size_bytes,
        content_type: typeof a.content_type === 'string' ? a.content_type : undefined
      };
    });
  }

  if (Array.isArray(data.steps)) {
    if (data.steps.length > 50) throw new ValidationError('Too many steps');
    sanitized.steps = data.steps.map(validateAndSanitizeStep);
  }

  return sanitized;
}

/**
 * Validates and sanitizes raw failure data.
 */
function validateAndSanitizeFailure(data: any): FriendlyFailure {
  if (!data || typeof data !== 'object') throw new ValidationError('Invalid failure object');

  if (typeof data.error_code !== 'string' || !data.error_code || data.error_code.length > MAX_STR_LEN) throw new ValidationError('Missing or invalid error_code');
  if (typeof data.message !== 'string' || !data.message || data.message.length > MAX_LONG_STR_LEN) throw new ValidationError('Missing or invalid message');

  return {
    error_code: data.error_code,
    message: data.message,
    correlation_id: (typeof data.correlation_id === 'string' && data.correlation_id.length <= MAX_STR_LEN) ? data.correlation_id : undefined
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
