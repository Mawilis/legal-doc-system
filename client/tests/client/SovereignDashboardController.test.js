/* eslint-disable */
// @vitest-environment node
/**
 * WILSY OS dashboard contract certificate.
 * Dashboard selection consumes the validated EOS workspace identifier. The
 * sole exception is a durable Tenant Owner selecting a commercial-only Legal
 * shell; every commercial read remains server-authorized and practice access stays absent.
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import {
  DASHBOARD_KEYS,
  getExecutiveRoleLabel,
  hasFounderReturnAuthority,
  mapDashboardAlias,
  resolveDashboardKey,
} from '../../src/components/sovereign/SovereignDashboardController.jsx';

const CONTROLLER_SOURCE = resolve(
  process.cwd(),
  'src/components/sovereign/SovereignDashboardController.jsx',
);

describe('SovereignDashboardController EOS workspace contract', () => {
  it('routes the tenant owner to Executive Command Centre from the EOS workspace contract', () => {
    expect(resolveDashboardKey({
      user: {
        id: 'owner-1',
        role: 'TENANT_OWNER',
        workspaceId: 'EXECUTIVE_COMMAND_CENTRE',
      },
      manualDashboardKey: 'CRM_DASHBOARD',
      dashboardIntent: 'LEGAL_DASHBOARD',
    })).toBe(DASHBOARD_KEYS.EXECUTIVE);
    expect(getExecutiveRoleLabel({ role: 'TENANT_OWNER' })).toBe('OWNER');
  });

  it('does not infer a dashboard from a role, founder permission or browser preference', () => {
    expect(resolveDashboardKey({
      user: {
        id: 'owner-2',
        role: 'OWNER',
        permissions: ['FOUNDER'],
        defaultDashboard: 'CRM_DASHBOARD',
      },
      manualDashboardKey: 'FOUNDER_DASHBOARD',
    })).toBe('');
    expect(resolveDashboardKey({
      user: { id: 'ceo-1', role: 'CEO' },
    })).toBe('');
    expect(resolveDashboardKey({
      user: { id: 'founder-1', role: 'FOUNDER' },
    })).toBe('');
  });

  it('allows Tenant Owner to open only the Legal commercial presentation, never practice or Founder dashboards', () => {
    const user = {
      id: 'owner-3',
      role: 'TENANT_OWNER',
      workspaceId: 'EXECUTIVE_COMMAND_CENTRE',
    };
    expect(resolveDashboardKey({ user, manualDashboardKey: 'LEGAL_DASHBOARD' }))
      .toBe(DASHBOARD_KEYS.LEGAL);
    for (const request of ['CRM_DASHBOARD', 'FOUNDER_DASHBOARD']) {
      expect(resolveDashboardKey({ user, manualDashboardKey: request }))
        .toBe(DASHBOARD_KEYS.EXECUTIVE);
    }
  });

  it('does not allow non-owner roles to select Legal outside the EOS workspace projection', () => {
    for (const role of ['LEGAL_PARTNER', 'LEGAL_FINANCE', 'TENANT_ADMIN']) {
      expect(resolveDashboardKey({
        user: { id: `principal-${role}`, role, workspaceId: 'EXECUTIVE_COMMAND_CENTRE' },
        manualDashboardKey: 'LEGAL_DASHBOARD',
      })).toBe(DASHBOARD_KEYS.EXECUTIVE);
    }
  });

  it('routes a Legal practice user only from the EOS Legal workspace identifier', () => {
    expect(resolveDashboardKey({
      user: {
        id: 'legal-partner-1',
        role: 'TENANT_LEGAL_PARTNER',
        workspaceId: 'LEGAL_PRACTICE',
      },
      manualDashboardKey: 'FOUNDER_DASHBOARD',
    })).toBe(DASHBOARD_KEYS.LEGAL);
  });

  it('maps every published workspace identifier to an existing presentation shard', () => {
    const cases = [
      ['TENANT_ADMINISTRATION', DASHBOARD_KEYS.GENERAL],
      ['AUDIT_REPORTING', DASHBOARD_KEYS.GENERAL],
      ['TENANT_OPERATIONS', DASHBOARD_KEYS.GENERAL],
      ['LEGAL_PRACTICE', DASHBOARD_KEYS.LEGAL],
      ['LEGAL_FINANCE', DASHBOARD_KEYS.FINANCE],
      ['CLIENT_PORTAL', DASHBOARD_KEYS.LEGAL],
      ['PROCESS_SERVICE', DASHBOARD_KEYS.LEGAL],
      ['PEOPLE_OPERATIONS', DASHBOARD_KEYS.HR],
    ];
    for (const [workspaceId, dashboardKey] of cases) {
      expect(resolveDashboardKey({
        user: { id: workspaceId, role: 'UNTRUSTED_ROLE_LABEL', workspaceId },
      })).toBe(dashboardKey);
    }
  });

  it('maps Operations and Intelligence product workspace keys to their own dashboard shards', () => {
    expect(resolveDashboardKey({
      user: { id: 'owner-ops', role: 'TENANT_OWNER', workspaceId: 'EXECUTIVE_COMMAND_CENTRE' },
      manualDashboardKey: 'OPERATIONS_DASHBOARD',
    })).toBe(DASHBOARD_KEYS.OPERATIONS);
    expect(resolveDashboardKey({
      user: { id: 'owner-intel', role: 'TENANT_OWNER', workspaceId: 'EXECUTIVE_COMMAND_CENTRE' },
      manualDashboardKey: 'INTELLIGENCE_DASHBOARD',
    })).toBe(DASHBOARD_KEYS.INTELLIGENCE);
    expect(resolveDashboardKey({
      user: { id: 'owner-legacy-ops', role: 'TENANT_OWNER', workspaceId: 'EXECUTIVE_COMMAND_CENTRE' },
      manualDashboardKey: 'OPERATIONS',
    })).toBe(DASHBOARD_KEYS.COO);
  });

  it('mounts System Services only from a READY EOS capability projection', () => {
    const workspace = {
      status: 'READY',
      authority: 'EOS_SYSTEM_SERVICES',
      principalId: 'platform-staff-1',
      scope: 'SYSTEM',
      capabilities: ['system_services:queue:read'],
    };
    expect(resolveDashboardKey({
      user: { id: 'platform-staff-1', role: 'SYSTEM_SERVICES', systemServicesWorkspace: workspace },
    })).toBe(DASHBOARD_KEYS.SYSTEM_SERVICES);
    expect(resolveDashboardKey({
      user: { id: 'platform-staff-1', role: 'SYSTEM_SERVICES', systemServicesWorkspace: workspace },
      manualDashboardKey: 'SYSTEM_SERVICES_DASHBOARD',
    })).toBe(DASHBOARD_KEYS.SYSTEM_SERVICES);
    expect(resolveDashboardKey({
      user: { id: 'staff-2', role: 'SYSTEM_ADMIN', workspaceId: 'EXECUTIVE_COMMAND_CENTRE' },
      manualDashboardKey: 'SYSTEM_SERVICES_DASHBOARD',
    })).toBe(DASHBOARD_KEYS.EXECUTIVE);
  });

  it('rejects a malformed or capability-free System Services workspace projection', () => {
    for (const systemServicesWorkspace of [
      { status: 'READY', authority: 'SYSTEM_ADMIN', principalId: 'staff-1', scope: 'SYSTEM', capabilities: ['system_services:queue:read'] },
      { status: 'PENDING', authority: 'EOS_SYSTEM_SERVICES', principalId: 'staff-1', scope: 'SYSTEM', capabilities: ['system_services:queue:read'] },
      { status: 'READY', authority: 'EOS_SYSTEM_SERVICES', principalId: 'staff-1', scope: 'SYSTEM', capabilities: [] },
      { status: 'READY', authority: 'EOS_SYSTEM_SERVICES', principalId: 'foreign-staff', scope: 'SYSTEM', capabilities: ['system_services:queue:read'] },
      { status: 'READY', authority: 'EOS_SYSTEM_SERVICES', principalId: 'staff-1', scope: 'TENANT', capabilities: ['system_services:queue:read'] },
    ]) {
      expect(resolveDashboardKey({
        user: { id: 'staff-1', role: 'SYSTEM_ADMIN', workspaceId: 'EXECUTIVE_COMMAND_CENTRE', systemServicesWorkspace },
        manualDashboardKey: 'SYSTEM_SERVICES_DASHBOARD',
      })).toBe(DASHBOARD_KEYS.EXECUTIVE);
    }
  });

  it('retains Founder-return predicate as a separate presentation helper only', () => {
    expect(hasFounderReturnAuthority({
      user: { role: 'FOUNDER', id: 'founder-2' },
    })).toBe(true);
    expect(resolveDashboardKey({
      user: {
        id: 'owner-4',
        role: 'TENANT_OWNER',
        permissions: ['FOUNDER'],
        workspaceId: 'EXECUTIVE_COMMAND_CENTRE',
      },
      manualDashboardKey: 'FOUNDER_DASHBOARD',
    })).toBe(DASHBOARD_KEYS.EXECUTIVE);
  });

  it('keeps historical module aliases as labels, not workspace authority', () => {
    expect(mapDashboardAlias('CEO_DASHBOARD')).toBe(DASHBOARD_KEYS.EXECUTIVE);
    expect(mapDashboardAlias('REVENUE_LEDGER')).toBe(DASHBOARD_KEYS.FINANCE);
    expect(mapDashboardAlias('SINGULARITY_MATRIX')).toBe(DASHBOARD_KEYS.FOUNDER);
    expect(mapDashboardAlias('LEGAL')).toBe(DASHBOARD_KEYS.LEGAL);
    expect(mapDashboardAlias('LEGAL_DASHBOARD')).toBe(DASHBOARD_KEYS.LEGAL);
    expect(mapDashboardAlias('LEGAL_OS')).toBe(DASHBOARD_KEYS.LEGAL);
  });

  it('keeps the Legal role as presentation metadata and not as dashboard authority', () => {
    const source = readFileSync(CONTROLLER_SOURCE, 'utf8');
    expect(source).toContain("const LegalDashboard = React.lazy(() => import('../industry/LegalDashboard'))");
    expect(source).toContain('dashboardKey === DASHBOARD_KEYS.LEGAL');
    expect(source).toContain('roleView={role}');
    expect(source).toContain('WORKSPACE_DASHBOARD_MAP[user.workspaceId]');
    expect(source).not.toContain('ROLE_DASHBOARD_MAP');
  });
});
