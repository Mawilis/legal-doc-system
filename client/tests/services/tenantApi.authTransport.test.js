/**
 * TITLE: Canonical Tenant Transport Certificate
 * VERSION: v1.0.0-R1D-B0F-B4-R3-CANONICAL-TRANSPORT-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves tenant operations share the AuthProvider-owned HTTP client,
 *          preserve its bearer, and fail closed on authentication responses.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/services/tenantApi.authTransport.test.js
 * COLLABORATION / OWNERSHIP: TenantApiClient and AuthProvider browser contract.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.0.0-R1D-B0F-B4-R3-CANONICAL-TRANSPORT-CERT — Initial focused
 *            canonical transport and retry-boundary certificate.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic bearer only; no live credentials.
 * TENANT BOUNDARY: Requests remain tenant-scoped by the canonical API client.
 * AUTHORITY BOUNDARY: Transport certificate only; server owns tenant authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api } = vi.hoisted(() => ({
  api: {
    defaults: { baseURL: '/api', headers: { common: {} } },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
  },
}));

vi.mock('../../src/services/api', () => ({ default: api }));
vi.mock('../../src/utils/telemetryHelper', () => ({ broadcastTelemetry: vi.fn() }));

import { TenantApiClient } from '../../src/services/api/tenantApi.js';

describe('canonical tenant authenticated transport', () => {
  beforeEach(() => {
    api.get.mockReset();
    api.defaults.headers.common = { Authorization: 'Bearer mfa-session-token' };
  });

  it('delegates tenant requests to the canonical client carrying the MFA bearer', async () => {
    api.get.mockResolvedValue({ status: 200, data: { tenantId: 'TENANT-A' } });
    const client = new TenantApiClient({ retryCount: 0 });

    await client.getTenant('TENANT-A');

    expect(client.client).toBe(api);
    expect(api.defaults.headers.common.Authorization).toBe('Bearer mfa-session-token');
    expect(api.get).toHaveBeenCalledWith('/tenants/TENANT-A');
  });

  it.each([401, 403])('does not retry a %s response', async (status) => {
    const error = { response: { status }, message: 'auth boundary failure' };
    api.get.mockRejectedValue(error);
    const client = new TenantApiClient({ retryCount: 3 });

    await expect(client.getTenant('TENANT-A')).rejects.toBe(error);
    expect(api.get).toHaveBeenCalledTimes(1);
  });

  it('retries one bounded transient 5xx response', async () => {
    vi.useFakeTimers();
    api.get
      .mockRejectedValueOnce({ response: { status: 503 }, message: 'temporarily unavailable' })
      .mockResolvedValueOnce({ status: 200, data: { tenantId: 'TENANT-A' } });
    const client = new TenantApiClient({ retryCount: 1 });
    const request = client.getTenant('TENANT-A');

    await vi.advanceTimersByTimeAsync(1000);
    await expect(request).resolves.toMatchObject({ data: { tenantId: 'TENANT-A' } });
    expect(api.get).toHaveBeenCalledTimes(2);
    vi.useRealTimers();
  });
});

/**
 * ARTIFACT: client/tests/services/tenantApi.authTransport.test.js
 * VERSION: v1.0.0-R1D-B0F-B4-R3-CANONICAL-TRANSPORT-CERT
 * AUTHORITY BOUNDARY: canonical transport behavior only
 * TENANT POSTURE: no cross-tenant authority is inferred by the adapter
 * FAIL-CLOSED POSTURE: 401/403 responses are terminal and never retried
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
