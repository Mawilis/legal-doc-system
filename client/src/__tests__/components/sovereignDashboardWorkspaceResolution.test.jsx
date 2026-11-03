import { describe, expect, it } from 'vitest';
import {
  DASHBOARD_KEYS,
  resolveDashboardKey,
} from '../../components/sovereign/SovereignDashboardController.jsx';

describe('EOS workspace-driven dashboard resolution', () => {
  it('routes the tenant owner to the executive command centre regardless of legacy role labels', () => {
    expect(resolveDashboardKey({
      user: { id: 'owner-1', role: 'OWNER', workspaceId: 'EXECUTIVE_COMMAND_CENTRE' },
    })).toBe(DASHBOARD_KEYS.EXECUTIVE);
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
    })).toBe(DASHBOARD_KEYS.EXECUTIVE);
  });
});
