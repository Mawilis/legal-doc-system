/**
 * TITLE: WILSY OS canonical Headquarters routing certificate
 * VERSION: v1.1.0-HEADQUARTERS-EXECUTIVE-RETIREMENT
 * AUTHORITY: EOS workspace-driven client routing evidence
 * EPITOME: Proves legacy executive requests resolve to the canonical Headquarters
 *          workspace while Legal routing remains independently selected by EOS.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/sovereignDashboardWorkspaceResolution.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.1.0 updates owner landing expectations after Executive Dashboard retirement.
 * AUTHORITY BOUNDARY: Routing evidence only; browser keys do not grant permissions.
 */
import { describe, expect, it } from 'vitest';
import {
  DASHBOARD_KEYS,
  resolveDashboardKey,
} from '../../components/sovereign/SovereignDashboardController.jsx';

describe('EOS workspace-driven dashboard resolution', () => {
  it('routes the tenant owner to canonical Headquarters regardless of legacy role labels', () => {
    expect(resolveDashboardKey({
      user: { id: 'owner-1', role: 'OWNER', workspaceId: 'EXECUTIVE_COMMAND_CENTRE' },
    })).toBe(DASHBOARD_KEYS.HEADQUARTERS);
  });

  it('routes the Legal practice partner only from the EOS Legal workspace identifier', () => {
    expect(resolveDashboardKey({
      user: { id: 'legal-1', role: 'TENANT_LEGAL_PARTNER', workspaceId: 'LEGAL_PRACTICE' },
    })).toBe(DASHBOARD_KEYS.LEGAL);
  });

  it('does not infer a dashboard from a role when EOS omits the workspace contract', () => {
    expect(resolveDashboardKey({
      user: { id: 'owner-1', role: 'TENANT_OWNER' },
    })).toBe('');
  });

  it('does not allow a browser dashboard preference to override the EOS workspace', () => {
    expect(resolveDashboardKey({
      user: { id: 'owner-1', role: 'TENANT_OWNER', workspaceId: 'EXECUTIVE_COMMAND_CENTRE' },
      manualDashboardKey: DASHBOARD_KEYS.CRM,
    })).toBe(DASHBOARD_KEYS.HEADQUARTERS);
  });
});

/* ARTIFACT: WILSY OS canonical Headquarters routing certificate
 * VERSION: v1.1.0-HEADQUARTERS-EXECUTIVE-RETIREMENT
 * AUTHORITY BOUNDARY: Presentation routing evidence only.
 * TENANT POSTURE: EOS workspace identifiers remain the sole routing input.
 * FAIL-CLOSED POSTURE: Missing workspace contracts still resolve to no dashboard.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
