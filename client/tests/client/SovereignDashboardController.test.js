/* eslint-disable */
import { describe, expect, it } from 'vitest';
import {
  DASHBOARD_KEYS,
  getExecutiveRoleLabel,
  hasFounderReturnAuthority,
  mapDashboardAlias,
  resolveDashboardKey
} from '../../src/components/sovereign/SovereignDashboardController.jsx';

describe('SovereignDashboardController resolver', () => {
  it('defaults founder authority to the Founder Dashboard when no explicit dashboard is requested', () => {
    const dashboardKey = resolveDashboardKey({
      user: {
        id: 'wilson-root',
        email: 'wilson@example.com',
        role: 'FOUNDER'
      }
    });

    expect(dashboardKey).toBe(DASHBOARD_KEYS.FOUNDER);
    expect(hasFounderReturnAuthority({ user: { role: 'FOUNDER', id: 'wilson-root' } })).toBe(true);
  });

  it('honors founder executive intent as a standalone dashboard with return authority', () => {
    const user = {
      id: 'wilson-root',
      email: 'wilson@example.com',
      role: 'OMEGA',
      defaultDashboard: 'EXECUTIVE_OVERSIGHT'
    };

    expect(resolveDashboardKey({ user })).toBe(DASHBOARD_KEYS.EXECUTIVE);
    expect(hasFounderReturnAuthority({ user })).toBe(true);
    expect(getExecutiveRoleLabel(user)).toBe('CEO');
  });

  it('routes executive and owner identities to the standalone executive surface', () => {
    expect(resolveDashboardKey({ user: { id: 'ceo-1', role: 'CEO' } })).toBe(DASHBOARD_KEYS.EXECUTIVE);
    expect(resolveDashboardKey({ user: { id: 'owner-1', role: 'TENANT_OWNER' } })).toBe(DASHBOARD_KEYS.EXECUTIVE);
  });

  it('routes specialist roles to their own dashboards before falling back to general', () => {
    expect(resolveDashboardKey({ user: { id: 'sales-1', role: 'SALES_REPRESENTATIVE' } })).toBe(DASHBOARD_KEYS.SALES);
    expect(resolveDashboardKey({ user: { id: 'finance-1', role: 'CFO' } })).toBe(DASHBOARD_KEYS.FINANCE);
    expect(resolveDashboardKey({ user: { id: 'tenant-1', role: 'TENANT_ADMIN' } })).toBe(DASHBOARD_KEYS.GENERAL);
  });

  it('keeps legacy Founder module names compatible with canonical dashboard keys', () => {
    expect(mapDashboardAlias('CEO_DASHBOARD')).toBe(DASHBOARD_KEYS.EXECUTIVE);
    expect(mapDashboardAlias('REVENUE_LEDGER')).toBe(DASHBOARD_KEYS.FINANCE);
    expect(mapDashboardAlias('SINGULARITY_MATRIX')).toBe(DASHBOARD_KEYS.FOUNDER);
  });
});
