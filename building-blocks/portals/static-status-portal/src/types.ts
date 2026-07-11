export type PipelineStatus = 'pending' | 'running' | 'waiting_input' | 'failed' | 'completed' | 'cancelled';

export interface PipelineRun {
  id: string;
  customer_id: string;
  pipeline_type: string;
  status: PipelineStatus;
  current_step?: string | null;
  progress_percent?: number | null;
  business_summary?: string | null;
  friendly_error?: string | null;
  correlation_id?: string | null;
  estimated_cost?: number | null;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
}

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

export interface Artifact {
  id: string;
  run_id: string;
  step_name?: string | null;
  kind: string;
  safe_name: string;
  storage_ref: string;
  content_type?: string | null;
  size_bytes?: number | null;
  is_customer_visible: boolean;
  created_at?: string | null;
}

export interface CostLedgerEntry {
  run_id: string;
  step_name?: string | null;
  category: 'ai_tokens' | 'document_ai' | 'storage' | 'function_execution' | 'integration' | 'other';
  provider?: string | null;
  model_or_service?: string | null;
  input_units?: number | null;
  output_units?: number | null;
  unit_name?: string | null;
  estimated_amount: number;
  currency: string;
  created_at?: string | null;
}

export interface PipelineRunDetail extends PipelineRun {
  steps: PipelineStep[];
}
