/* eslint-disable */
/**
 * TITLE: WILSY OS Sovereign Dashboard Controller Legal Role Routing Certificate
 * VERSION: v1.1.0-L8-7D10-LEGAL-ROLE-CONVERGENCE-CERT
 * AUTHORITY: Client routing/resolver certification only.
 * EPITOME: Certifies SovereignDashboardController resolves every published Legal
 *          business role to the single canonical Legal OS shard, preserves
 *          existing non-Legal dashboard mappings, accepts canonical Legal OS
 *          aliases, and forwards normalized authenticated role only as
 *          presentation roleView.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/SovereignDashboardController.test.js
 * COLLABORATION / OWNERSHIP: Controller owns client routing; Python EOS owns IAM
 *                            and Legal Operations authority.
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v1.1.0-L8-7D10-LEGAL-ROLE-CONVERGENCE-CERT adds exact routing coverage for
 *            LEGAL_PARTNER, LEGAL_ATTORNEY, LEGAL_PARALEGAL, LEGAL_SECRETARY,
 *            LEGAL_FINANCE, LEGAL_CLIENT and TENANT_* aliases while retaining
 *            SHERIFF/DEPUTY and all existing non-Legal mappings.
 *            2026-09-23 v1.0.0-L8-6C-LEGAL-ROLE-ROUTING-CERT establishes L8-6C Legal OS role-routing coverage.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic identities only; no credentials or PII.
 * TENANT BOUNDARY: Tests routing only and create no tenant authority.
 * AUTHORITY BOUNDARY: Resolver/wiring evidence only; role routing is not IAM.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import {
  DASHBOARD_KEYS,
  getExecutiveRoleLabel,
  hasFounderReturnAuthority,
  mapDashboardAlias,
  resolveDashboardKey
} from '../../src/components/sovereign/SovereignDashboardController.jsx';

const CONTROLLER_SOURCE = resolve(
  process.cwd(),
  'src/components/sovereign/SovereignDashboardController.jsx',
);

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

  it('routes every published Legal business role to the canonical Legal OS shard', () => {
    const roles = [
      'LEGAL_PARTNER',
      'TENANT_LEGAL_PARTNER',
      'LEGAL_ATTORNEY',
      'TENANT_LEGAL_ATTORNEY',
      'LEGAL_PARALEGAL',
      'TENANT_LEGAL_PARALEGAL',
      'LEGAL_SECRETARY',
      'TENANT_LEGAL_SECRETARY',
      'LEGAL_FINANCE',
      'TENANT_LEGAL_FINANCE',
      'LEGAL_CLIENT',
      'TENANT_LEGAL_CLIENT',
      'SHERIFF',
      'TENANT_SHERIFF',
      'DEPUTY',
      'TENANT_DEPUTY',
    ];

    for (const role of roles) {
      expect(resolveDashboardKey({ user: { id: `legal-${role}`, role } })).toBe(
        DASHBOARD_KEYS.LEGAL,
      );
    }
  });

  it('keeps legacy Founder module names compatible with canonical dashboard keys', () => {
    expect(mapDashboardAlias('CEO_DASHBOARD')).toBe(DASHBOARD_KEYS.EXECUTIVE);
    expect(mapDashboardAlias('REVENUE_LEDGER')).toBe(DASHBOARD_KEYS.FINANCE);
    expect(mapDashboardAlias('SINGULARITY_MATRIX')).toBe(DASHBOARD_KEYS.FOUNDER);
  });

  it('recognizes Legal OS aliases without inventing authorization', () => {
    expect(mapDashboardAlias('LEGAL')).toBe(DASHBOARD_KEYS.LEGAL);
    expect(mapDashboardAlias('LEGAL_DASHBOARD')).toBe(DASHBOARD_KEYS.LEGAL);
    expect(mapDashboardAlias('LEGAL_OS')).toBe(DASHBOARD_KEYS.LEGAL);
  });

  it('forwards normalized authenticated role as presentation roleView', () => {
    const source = readFileSync(CONTROLLER_SOURCE, 'utf8');
    expect(source).toContain("const LegalDashboard = React.lazy(() => import('../industry/LegalDashboard'))");
    expect(source).toContain('dashboardKey === DASHBOARD_KEYS.LEGAL');
    expect(source).toContain('roleView={role}');
    expect(source).not.toContain('roleView="DEPUTY"');
    expect(source).not.toContain('roleView="SHERIFF"');
  });
});

/**
 * ARTIFACT: SovereignDashboardController.test.js
 * VERSION: v1.1.0-L8-7D10-LEGAL-ROLE-CONVERGENCE-CERT
 * AUTHORITY BOUNDARY: client resolver and Legal OS routing certification only
 * TENANT POSTURE: routing evidence does not create or widen tenant authority
 * FAIL-CLOSED POSTURE: role routing never substitutes browser authority for Python EOS IAM
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
