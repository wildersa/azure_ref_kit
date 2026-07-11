import { Artifact, PipelineRun, PipelineRunDetail } from './types';

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

    // In a real implementation, the API might return steps within the run detail
    // or we might need a separate call. Based on the README, GET /runs/{id}
    // should include the timeline components (steps).
    // If the API doesn't include them, we'd mock it here or adjust.
    // For now, we'll assume it returns them or we'll need to mock them for the UI.
    return {
        ...run,
        steps: (run as any).steps || []
    };
  },

  async getArtifacts(runId: string): Promise<Artifact[]> {
    const response = await fetch(`/api/runs/${runId}/artifacts`);
    return handleResponse<Artifact[]>(response);
  },

  async getCost(runId: string): Promise<number> {
    const response = await fetch(`/api/runs/${runId}/cost`);
    return handleResponse<number>(response);
  },

  async startRun(): Promise<PipelineRun> {
    const response = await fetch('/api/runs/start', {
      method: 'POST',
    });
    return handleResponse<PipelineRun>(response);
  },

  getDownloadUrl(artifactId: string): string {
    return `/api/artifacts/${artifactId}/download`;
  }
};
