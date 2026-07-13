import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api, setUseFixtures, ValidationError } from './api';

describe('API Adapter (Strict Validation & Defense in Depth)', () => {
  beforeEach(() => {
    setUseFixtures(false);
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    setUseFixtures(true);
  });

  it('filters out unexpected extra fields while preserving valid data', async () => {
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
      created_at: '2024-01-01T00:00:00Z'
    });

    // Verify forbidden fields are truly gone
    expect(result[0]).not.toHaveProperty('internal_field');
    expect(result[0]).not.toHaveProperty('raw_logs');
    expect(result[0]).not.toHaveProperty('customer_id');
  });

  it('fails closed when a required field is missing', async () => {
    const malformedData = {
      id: 'run-missing-status',
      // status is missing
      created_at: '2024-01-01T00:00:00Z'
    };

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => malformedData
    } as Response);

    await expect(api.getRunDetail('run-missing-status')).rejects.toThrow(ValidationError);
    await expect(api.getRunDetail('run-missing-status')).rejects.toThrow(/Invalid status/);
  });

  it('fails closed when an enum value is invalid', async () => {
    const invalidStatusData = {
      id: 'run-invalid-status',
      status: 'INTERNAL_DEBUG_STATE', // Not in enum
      created_at: '2024-01-01T00:00:00Z'
    };

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => invalidStatusData
    } as Response);

    await expect(api.getRunDetail('run-invalid-status')).rejects.toThrow(ValidationError);
  });

  it('fails closed when a field type is invalid', async () => {
    const invalidTypeData = {
      id: 'run-invalid-type',
      status: 'running',
      created_at: '2024-01-01T00:00:00Z',
      progress_percent: 'not-a-number' // Should be number
    };

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => invalidTypeData
    } as Response);

    await expect(api.getRunDetail('run-invalid-type')).rejects.toThrow(ValidationError);
  });

  it('strictly validates nested safe_artifacts', async () => {
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
      size_bytes: 100
    });
    expect(result.safe_artifacts![0]).not.toHaveProperty('internal_storage_path');
  });

  it('fails closed when nested artifacts are malformed', async () => {
    const rawData = {
      id: 'run-artifacts-bad',
      status: 'completed',
      created_at: '2024-01-01T00:00:00Z',
      safe_artifacts: [
        {
          name: 'broken.txt'
          // size_bytes is missing
        }
      ]
    };

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => rawData
    } as Response);

    await expect(api.getRunDetail('run-artifacts-bad')).rejects.toThrow(ValidationError);
  });

  it('strictly validates failure details', async () => {
    const rawFailure = {
        error_code: 'ERR_001',
        message: 'Friendly error',
        technical_detail: 'stack trace'
    };

    vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => rawFailure
    } as Response);

    const result = await api.getRunFailure('run-1');
    expect(result).toEqual({
        error_code: 'ERR_001',
        message: 'Friendly error'
    });
    expect(result).not.toHaveProperty('technical_detail');
  });
});
