/**
 * TITLE: Protected Dashboard Logout Propagation Certificate
 * VERSION: v1.0.0-ALL-PROTECTED-ROUTES-LOGOUT-PROPAGATION-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves both protected dashboard entry routes receive the AuthProvider
 *          logout command so role-aware dashboard shards can expose Sign out.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/App.logoutPropagation.test.jsx
 * COLLABORATION / OWNERSHIP: App.jsx, SovereignDashboardController, AuthProvider.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG:
 *   v1.0.0-ALL-PROTECTED-ROUTES-LOGOUT-PROPAGATION-CERT — Initial direct
 *     route-contract certificate for "/" and "/dashboard" logout propagation.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Static route composition only; no credential,
 *                             token, tenant, legal, or financial state is used.
 * TENANT BOUNDARY: Logout propagation grants no tenant authority.
 * AUTHORITY BOUNDARY: Browser command wiring only; AuthProvider owns logout and
 *                     Python EOS remains authentication authority.
 * FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
 */

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

const source = readFileSync('src/App.jsx', 'utf8');

describe('protected dashboard logout propagation', () => {
  it('passes AuthProvider logout to both canonical dashboard entry routes', () => {
    expect(source).toMatch(
      /<Route path="\/" element=\{isAuthenticated && user \? <ErrorBoundary><SovereignDashboardController user=\{user\} onLogout=\{logout\} \/><\/ErrorBoundary>/,
    );
    expect(source).toMatch(
      /<Route path="\/dashboard" element=\{[\s\S]*?<SovereignDashboardController user=\{user\} onLogout=\{logout\} \/>/,
    );

    const propagated = source.match(
      /<SovereignDashboardController user=\{user\} onLogout=\{logout\} \/>/g,
    ) || [];
    expect(propagated).toHaveLength(2);
  });

  it('does not replace logout authority with browser-local token deletion', () => {
    const routerStart = source.indexOf('const SovereignRouter = () =>');
    const routerEnd = source.indexOf('/**\n * @function App', routerStart);
    const routerSource = source.slice(routerStart, routerEnd);

    expect(routerSource).toContain('logout,');
    expect(routerSource).not.toContain("localStorage.removeItem('wilsy_auth_token')");
    expect(routerSource).not.toContain("localStorage.removeItem('token')");
  });
});

/**
 * ARTIFACT: client/tests/client/App.logoutPropagation.test.jsx
 * VERSION: v1.0.0-ALL-PROTECTED-ROUTES-LOGOUT-PROPAGATION-CERT
 * AUTHORITY BOUNDARY: deterministic browser route-wiring certificate only
 * TENANT POSTURE: no tenant authority is created by route composition
 * FAIL-CLOSED POSTURE: logout remains delegated to AuthProvider
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
