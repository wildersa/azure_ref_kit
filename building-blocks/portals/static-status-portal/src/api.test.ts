import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api, setUseFixtures } from './api';

describe('API Adapter (Defense in Depth Sanitization)', () => {
  beforeEach(() => {
    setUseFixtures(false);
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    setUseFixtures(true);
  });

  it('filters out unexpected/forbidden fields from getRuns', async () => {
    const rawData = [
      {
        id: 'run-1',
        status: 'completed',
        created_at: '2024-01-01T00:00:00Z',
        internal_field: 'should-be-removed',
        raw_logs: 'technical info',
        customer_id: 'cust-123'
      }
    ];

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => rawData
    } as Response);

    const result = await api.getRuns();

    expect(result[0]).toEqual({
      id: 'run-1',
      status: 'completed',
      created_at: '2024-01-01T00:00:00Z',
      business_summary: undefined,
      progress_percent: undefined,
      estimated_cost: undefined,
      started_at: undefined,
      finished_at: undefined,
      safe_artifacts: undefined
    });

    // Verify forbidden fields are truly gone
    expect(result[0]).not.toHaveProperty('internal_field');
    expect(result[0]).not.toHaveProperty('raw_logs');
    expect(result[0]).not.toHaveProperty('customer_id');
  });

  it('filters out unexpected fields from getRunDetail', async () => {
    const rawData = {
      id: 'run-detail-1',
      status: 'running',
      created_at: '2024-01-01T00:00:00Z',
      system_prompt: 'You are an internal tool',
      azure_resource_id: '/subscriptions/...'
    };

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => rawData
    } as Response);

    const result = await api.getRunDetail('run-detail-1');

    expect(result.id).toBe('run-detail-1');
    expect(result).not.toHaveProperty('system_prompt');
    expect(result).not.toHaveProperty('azure_resource_id');
  });

  it('sanitizes nested safe_artifacts', async () => {
    const rawData = {
      id: 'run-artifacts',
      status: 'completed',
      created_at: '2024-01-01T00:00:00Z',
      safe_artifacts: [
        {
          name: 'safe.txt',
          size_bytes: 100,
          internal_storage_path: 'secret/path/to/file'
        }
      ]
    };

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => rawData
    } as Response);

    const result = await api.getRunDetail('run-artifacts');

    expect(result.safe_artifacts![0]).toEqual({
      name: 'safe.txt',
      size_bytes: 100,
      content_type: undefined
    });
    expect(result.safe_artifacts![0]).not.toHaveProperty('internal_storage_path');
  });
});
