import { Artifact, PipelineRun, PipelineRunDetail, CostSummary } from './types';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = 'An error occurred while fetching data.';
    try {
      const errorData = await response.json();
      errorMessage = errorData.error?.message || errorMessage;
    } catch {
      // Ignore JSON parsing error
    }
    throw new ApiError(response.status, errorMessage);
  }
  return response.json();
}

export const api = {
  async getRuns(): Promise<PipelineRun[]> {
    const response = await fetch('/api/runs');
    return handleResponse<PipelineRun[]>(response);
  },

  async getRunDetail(id: string): Promise<PipelineRunDetail> {
    const response = await fetch(`/api/runs/${id}`);
    const run = await handleResponse<PipelineRun>(response);

    return {
        ...run,
        steps: (run as any).steps || []
    };
  },

  async getArtifacts(runId: string): Promise<Artifact[]> {
    const response = await fetch(`/api/runs/${runId}/artifacts`);
    return handleResponse<Artifact[]>(response);
  },

  async getCost(runId: string): Promise<CostSummary> {
    const response = await fetch(`/api/runs/${runId}/cost`);
    return handleResponse<CostSummary>(response);
  },

  getDownloadUrl(artifactId: string): string {
    return `/api/artifacts/${artifactId}/download`;
  }
};
