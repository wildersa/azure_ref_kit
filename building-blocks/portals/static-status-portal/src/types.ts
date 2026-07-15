/**
 * Customer-Safe Status Types
 * Strictly aligned with building-blocks/security/customer-safe-status-boundary/src/schemas/
 * and shared/contracts/
 */

export type PipelineStatus = 'pending' | 'running' | 'waiting_input' | 'failed' | 'completed' | 'cancelled';

export type StepStatus = 'pending' | 'running' | 'waiting_input' | 'failed' | 'completed' | 'skipped' | 'cancelled';

export interface PipelineStep {
  run_id: string;
  name: string;
  status: StepStatus;
  input_summary?: string | null;
  output_summary?: string | null;
  friendly_error?: string | null;
  artifacts?: string[];
  retry_count?: number;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface SafeArtifact {
  name: string;
  size_bytes: number;
  content_type?: string;
}

export interface CustomerSafeStatus {
  id: string;
  status: PipelineStatus;
  business_summary?: string;
  progress_percent?: number;
  estimated_cost?: number;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
  safe_artifacts?: SafeArtifact[];
  steps?: PipelineStep[];
}

export interface FriendlyFailure {
  error_code: string;
  message: string;
  correlation_id?: string | null;
}
