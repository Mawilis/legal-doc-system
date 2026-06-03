/* eslint-disable */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as superadminApi from '../../src/api/superadmin';
import api from '../../src/services/api';

// We spy on the underlying Axios instance ('api'), not the wrapper functions
vi.mock('../../src/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn(), handlers: [] },
      response: { use: vi.fn(), handlers: [] }
    }
  }
}));

describe('🏛️ SuperAdmin API Gateway (Wilsy OS Citadel)', () => {

  it('fetches global metrics and system valuation', async () => {
    const mockData = { success: true, data: { financials: { globalMRR: 199249 } } };
    api.get.mockResolvedValueOnce({ data: mockData });

    const result = await superadminApi.getGlobalStats();

    expect(api.get).toHaveBeenCalledWith('/superadmin/stats');
    expect(result.data.financials.globalMRR).toBe(199249);
  });

  it('retrieves tenants list for firm management', async () => {
    api.get.mockResolvedValueOnce({ data: { success: true, firms: [] } });

    await superadminApi.getFirms();
    expect(api.get).toHaveBeenCalledWith('/superadmin/firms');
  });
});
