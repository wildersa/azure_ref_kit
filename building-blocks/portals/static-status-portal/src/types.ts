/**
 * Customer-Safe Status Types
 * Strictly aligned with building-blocks/security/customer-safe-status-boundary/src/schemas/
 */

export type PipelineStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

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
}

export interface FriendlyFailure {
  error_code: string;
  message: string;
  correlation_id?: string | null;
}
