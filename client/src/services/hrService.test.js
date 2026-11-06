import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api, broadcastTelemetry } = vi.hoisted(() => ({
  api: { put: vi.fn() },
  broadcastTelemetry: vi.fn().mockResolvedValue(undefined),
}));

vi.mock('./api', () => ({ default: api }));
vi.mock('../utils/telemetryHelper', () => ({ broadcastTelemetry }));
vi.mock('../utils/logger', () => ({ default: { error: vi.fn() } }));

import { approveTimeOff, denyTimeOff } from './hrService.js';

describe('People OS time-off decision transport', () => {
  beforeEach(() => {
    api.put.mockReset().mockResolvedValue({ data: { id: 'leave-1', status: 'APPROVED' } });
    broadcastTelemetry.mockReset().mockResolvedValue(undefined);
  });

  it('approves a tenant-scoped time-off request through the People domain endpoint', async () => {
    await approveTimeOff('leave-1', 'TENANT-PEOPLE-1');
    expect(api.put).toHaveBeenCalledWith('/hr/timeoff/leave-1/approve', {}, {
      headers: { 'X-Tenant-ID': 'TENANT-PEOPLE-1' },
    });
    expect(broadcastTelemetry).toHaveBeenCalled();
  });

  it('denies a tenant-scoped time-off request through the People domain endpoint', async () => {
    await denyTimeOff('leave-1', 'TENANT-PEOPLE-1');
    expect(api.put).toHaveBeenCalledWith('/hr/timeoff/leave-1/deny', {}, {
      headers: { 'X-Tenant-ID': 'TENANT-PEOPLE-1' },
    });
  });
});
