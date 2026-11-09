/* eslint-disable */
// @vitest-environment node
/**
/**
 * TITLE: WILSY OS Sovereign Dashboard Controller Certification.
 * VERSION: v1.2.0-EXECUTIVE-ROUTING-RETIREMENT
 * AUTHORITY: Unit certification of authenticated EOS workspace presentation routing.
 * EPITOME: Verifies Headquarters is mounted only from the EOS-issued
 *          WILSY_HEADQUARTERS workspace identifier.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/SovereignDashboardController.test.js
 * COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
 * CERTIFICATION / UPDATE DATE: 2026-11-08.
 * CHANGELOG: v1.2.0-EXECUTIVE-ROUTING-RETIREMENT updates owner, Legal-boundary,
 *            system-fallback and historical-alias expectations after the
 *            legacy Executive Dashboard retirement.
 *            v1.1.0-WILSY-HEADQUARTERS-DASHBOARD-CERTIFICATION certifies the WILSY Headquarters dashboard mapping
 *            and mounted component without granting browser-side authority.
 * SECURITY / PRIVACY POSTURE: Client route selection is presentation only;
 *                             Python EOS remains the authority.
 * TENANT BOUNDARY: The server-issued workspace identifier is tenant-scoped.
 * AUTHORITY BOUNDARY: Test evidence only; no IAM or business permissions.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
/*
 * Dashboard selection consumes the validated EOS workspace identifier. The
 * sole exception is a durable Tenant Owner selecting a commercial-only Legal
 * shell; every commercial read remains server-authorized and practice access stays absent.
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import {
  DASHBOARD_KEYS,
  hasFounderReturnAuthority,
  hasTenantModuleManifestAdmission,
  resolveDashboardRequestSignal,
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
    })).toBe(DASHBOARD_KEYS.HEADQUARTERS);
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
    for (const request of ['CRM_DASHBOARD', 'BILLING_HUB', 'HR_DASHBOARD', 'OPERATIONS_DASHBOARD', 'INTELLIGENCE_DASHBOARD', 'POS_DASHBOARD', 'FOUNDER_DASHBOARD']) {
      expect(resolveDashboardKey({ user, manualDashboardKey: request }))
        .toBe(DASHBOARD_KEYS.HEADQUARTERS);
    }
  });

  it('does not allow non-owner roles to select Legal outside the EOS workspace projection', () => {
    for (const role of ['LEGAL_PARTNER', 'LEGAL_FINANCE', 'TENANT_ADMIN']) {
      expect(resolveDashboardKey({
        user: { id: `principal-${role}`, role, workspaceId: 'EXECUTIVE_COMMAND_CENTRE' },
        manualDashboardKey: 'LEGAL_DASHBOARD',
      })).toBe(DASHBOARD_KEYS.HEADQUARTERS);
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
      ['WILSY_HEADQUARTERS', DASHBOARD_KEYS.HEADQUARTERS],
      ['TENANT_ADMINISTRATION', DASHBOARD_KEYS.GENERAL],
      ['AUDIT_REPORTING', DASHBOARD_KEYS.GENERAL],
      ['TENANT_OPERATIONS', DASHBOARD_KEYS.GENERAL],
      ['LEGAL_PRACTICE', DASHBOARD_KEYS.LEGAL],
      ['LEGAL_FINANCE', DASHBOARD_KEYS.FINANCE],
      ['CLIENT_PORTAL', DASHBOARD_KEYS.LEGAL],
      ['PROCESS_SERVICE', DASHBOARD_KEYS.LEGAL],
      ['PEOPLE_OPERATIONS', DASHBOARD_KEYS.HR],
      ['POINT_OF_SALE', DASHBOARD_KEYS.POS],
      ['POS_DASHBOARD', DASHBOARD_KEYS.POS],
    ];
    for (const [workspaceId, dashboardKey] of cases) {
      expect(resolveDashboardKey({
        user: { id: workspaceId, role: 'UNTRUSTED_ROLE_LABEL', workspaceId },
      })).toBe(dashboardKey);
    }
  });

  it('mounts all seven tenant products on their real independent module destinations', () => {
    const source = readFileSync(CONTROLLER_SOURCE, 'utf8');
    const mounts = [
      ['DASHBOARD_KEYS.HEADQUARTERS', '<WilsyHeadquartersWorkspace'],
      ['DASHBOARD_KEYS.LEGAL', '<LegalDashboard'],
      ['DASHBOARD_KEYS.FINANCE', '<BillingHUD'],
      ['DASHBOARD_KEYS.CRM', '<CRMDashboard'],
      ['DASHBOARD_KEYS.HR', '<HRDashboard'],
      ['DASHBOARD_KEYS.OPERATIONS', '<OperationsDashboard'],
      ['DASHBOARD_KEYS.INTELLIGENCE', '<IntelligenceDashboard'],
      ['DASHBOARD_KEYS.POS', '<POSDashboard'],
    ];
    for (const [key, component] of mounts) {
      expect(source).toContain(`dashboardKey === ${key}`);
      expect(source).toContain(component);
    }
    expect(source).toContain("const WilsyHeadquartersWorkspace = React.lazy(() => import('../workspaces/WilsyHeadquartersWorkspace.jsx'))");
  });

  it('routes the new product workspace keys distinctly without changing the legacy Operations alias', () => {
    expect(resolveDashboardRequestSignal('OPERATIONS_DASHBOARD')).toBe(DASHBOARD_KEYS.OPERATIONS);
    expect(resolveDashboardRequestSignal('INTELLIGENCE_DASHBOARD')).toBe(DASHBOARD_KEYS.INTELLIGENCE);
    expect(resolveDashboardRequestSignal('OPERATIONS')).toBe(DASHBOARD_KEYS.COO);
  });

  it('mounts every non-Legal product only from exact server-issued module/product/workspace evidence', () => {
    const manifest = [
      { moduleId: 'BILLING', productId: 'BILLING', workspaceKey: 'BILLING_HUB' },
      { moduleId: 'CRM', productId: 'CRM', workspaceKey: 'CRM_DASHBOARD' },
      { moduleId: 'PEOPLE', productId: 'HR', workspaceKey: 'HR_DASHBOARD' },
      { moduleId: 'OPERATIONS', productId: 'OPERATIONS', workspaceKey: 'OPERATIONS_DASHBOARD' },
      { moduleId: 'INTELLIGENCE', productId: 'INTELLIGENCE', workspaceKey: 'INTELLIGENCE_DASHBOARD' },
      { moduleId: 'POS', productId: 'POS', workspaceKey: 'POS_DASHBOARD' },
    ];
    expect(hasTenantModuleManifestAdmission(manifest, DASHBOARD_KEYS.FINANCE)).toBe(true);
    expect(hasTenantModuleManifestAdmission(manifest, DASHBOARD_KEYS.CRM)).toBe(true);
    expect(hasTenantModuleManifestAdmission(manifest, DASHBOARD_KEYS.HR)).toBe(true);
    expect(hasTenantModuleManifestAdmission(manifest, DASHBOARD_KEYS.OPERATIONS)).toBe(true);
    expect(hasTenantModuleManifestAdmission(manifest, DASHBOARD_KEYS.INTELLIGENCE)).toBe(true);
    expect(hasTenantModuleManifestAdmission(manifest, DASHBOARD_KEYS.POS)).toBe(true);
    expect(hasTenantModuleManifestAdmission([], DASHBOARD_KEYS.FINANCE)).toBe(false);
    expect(hasTenantModuleManifestAdmission([], DASHBOARD_KEYS.CRM)).toBe(false);
    expect(hasTenantModuleManifestAdmission([], DASHBOARD_KEYS.HR)).toBe(false);
    expect(hasTenantModuleManifestAdmission([], DASHBOARD_KEYS.OPERATIONS)).toBe(false);
    expect(hasTenantModuleManifestAdmission([], DASHBOARD_KEYS.POS)).toBe(false);
    expect(hasTenantModuleManifestAdmission([
      { moduleId: 'OPERATIONS', productId: 'CRM', workspaceKey: 'OPERATIONS_DASHBOARD' },
    ], DASHBOARD_KEYS.OPERATIONS)).toBe(false);
    expect(hasTenantModuleManifestAdmission(manifest, DASHBOARD_KEYS.CRM)).toBe(true);
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
    })).toBe(DASHBOARD_KEYS.HEADQUARTERS);
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
      })).toBe(DASHBOARD_KEYS.HEADQUARTERS);
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
      })).toBe(DASHBOARD_KEYS.HEADQUARTERS);
  });

  it('keeps historical module aliases as labels, not workspace authority', () => {
    expect(mapDashboardAlias('CEO_DASHBOARD')).toBe(DASHBOARD_KEYS.HEADQUARTERS);
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

/* 
 * ARTIFACT: SovereignDashboardController.test.js
 * VERSION: v1.2.0-EXECUTIVE-ROUTING-RETIREMENT
 * AUTHORITY BOUNDARY: unit certification of client workspace presentation routing
 * TENANT POSTURE: workspace identity is supplied by EOS; tests distinguish Headquarters and customer workspaces
 * FAIL-CLOSED POSTURE: no browser role or preference creates workspace authority
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
