/**
 * TITLE: BillingHUD Governed C2 Tenant Status Mutation Certificate
 * VERSION: v1.0.0-GOVERNED-C2-TENANT-STATUS-DENY-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves the legacy BillingHUD tenant-status binding rejects before
 *          transport, telemetry, or success evidence while C2 is ungoverned.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/billing/BillingHUD.liveBindings.governedC2.test.jsx
 * COLLABORATION / OWNERSHIP: BillingHUD live bindings, canonical API client,
 *                            and Python EOS tenant authority contract.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v1.0.0-GOVERNED-C2-TENANT-STATUS-DENY-CERT establishes the C2
 *            pre-transport denial regression certificate.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic tenant identifiers only; no credentials.
 * TENANT BOUNDARY: Exact authenticated workspace is supplied to the hook.
 * AUTHORITY BOUNDARY: No UI identity or legacy status endpoint grants C2 authority.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive for financial execution.
 */

import { renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api, useAuth, useTenants, useRealtimeMetrics, broadcastTelemetry } = vi.hoisted(() => ({
  api: { post: vi.fn(), patch: vi.fn(), get: vi.fn() },
  useAuth: vi.fn(),
  useTenants: vi.fn(),
  useRealtimeMetrics: vi.fn(),
  broadcastTelemetry: vi.fn(),
}));

vi.mock('../../../src/utils/sovereignClient', () => ({ default: api }));
vi.mock('../../../src/contexts/authContext', () => ({ useAuth }));
vi.mock('../../../src/contexts/tenantContext', () => ({ useTenants }));
vi.mock('../../../src/utils/telemetryHelper', () => ({ broadcastTelemetry }));
vi.mock('../../../src/components/billing/BillingHUD.metrics', () => ({ useRealtimeMetrics }));

import { useLiveBindings } from '../../../src/components/billing/BillingHUD.liveBindings.js';

describe('BillingHUD governed C2 tenant status boundary', () => {
  beforeEach(() => {
    api.post.mockReset();
    api.patch.mockReset();
    api.get.mockReset();
    broadcastTelemetry.mockReset();
    useAuth.mockReturnValue({ user: { tenantId: 'TENANT-A' } });
    useTenants.mockReturnValue({ activeTenant: { tenantId: 'TENANT-A' } });
    useRealtimeMetrics.mockReturnValue({
      tenantLifecycle: { created: 0, suspended: 0, verified: 0, activated: 0 },
      arrForecastData: [],
      treasuryReserves: {},
      riskBands: {},
      proofHashes: {},
    });
  });

  it('rejects status changes before transport, telemetry, and proof generation', async () => {
    const { result } = renderHook(() => useLiveBindings());

    await expect(result.current.updateTenantStatus('TENANT-B', 'SUSPENDED')).rejects.toMatchObject({
      code: 'GOVERNED_C2_CAPABILITY_REQUIRED',
      operation: 'tenant_lifecycle_status_update',
    });

    expect(api.post).not.toHaveBeenCalled();
    expect(api.patch).not.toHaveBeenCalled();
    expect(broadcastTelemetry).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: client/tests/components/billing/BillingHUD.liveBindings.governedC2.test.jsx
 * VERSION: v1.0.0-GOVERNED-C2-TENANT-STATUS-DENY-CERT
 * AUTHORITY BOUNDARY: UI mutation adapter only; Python EOS owns tenant authorization.
 * TENANT POSTURE: Synthetic current/target tenant values; no persistent state.
 * FAIL-CLOSED POSTURE: Status update rejects before any network or telemetry side effect.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
