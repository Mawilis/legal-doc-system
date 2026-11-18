/**
 * TITLE: WILSY Authenticated Company Transport and Refresh Contract
 * VERSION: v1.0.0
 * AUTHORITY: Client transport regression evidence only.
 * EPITOME: Exercise real Axios interceptors and AuthProvider with a bounded
 * adapter; prove credentials, rotation ownership and fail-closed scope handling.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/services/companyAuthenticationTransport.test.jsx
 * COLLABORATION / OWNERSHIP: AuthProvider, shared api.js and company source client.
 * CERTIFICATION / UPDATE DATE: 2026-11-14
 * CHANGELOG: v1.0.0 adds actual-interceptor request and provider-refresh regressions.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY: Synthetic opaque credentials only; no live network or data.
 * SECURITY / PRIVACY POSTURE: Tests authenticated transport isolation without exposing credentials, session tokens or sensitive identity evidence.
 * TENANT BOUNDARY: Exact synthetic scope; foreign refresh/evidence is rejected.
 * AUTHORITY BOUNDARY: Adapter fixtures never certify actual browser/IAM acceptance.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
 */
import React from 'react';
import axios, { AxiosError } from 'axios';
import { act, cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it } from 'vitest';

const scope = { tenantId: 'WILSYTENANT-TRANSPORT-TEST', principalId: 'transport-test-principal' };
const originalAdapter = axios.defaults.adapter;
let api;
let setActiveTenantTransportId;
let readFounderSessionEvidence;
let AuthProvider;
let useAuth;
let calls;
let route;
let owner;
const ok = (config, data) => ({ config, data, status: 200, statusText: 'OK', headers: {} });
const reject401 = (config) => { throw new AxiosError('Synthetic expiry', 'ERR_BAD_REQUEST', config, null,
  { config, data: { detail: 'Synthetic expiry' }, status: 401, headers: {} }); };
const workspace = (principalId = scope.principalId) => ({
  status: 'READY', user: { id: principalId, email: 'transport@example.test' },
  workspace: { tenantId: scope.tenantId, workspaceId: 'WILSY_HEADQUARTERS', businessRole: 'tenant_owner',
    workspaceContractVersion: 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION', membershipRevision: 0,
    businessRoleRevision: 0, branding: null,
    tenant: { tenantId: scope.tenantId, name: 'Test', legalName: 'Test', status: 'ACTIVE' } },
});
const evidence = () => ({ schema: 'WILSY-FOUNDER-SESSION-EVIDENCE/V1', state: 'AUTHENTICATED_SESSION_OBSERVED',
  principal_id: scope.principalId, tenant_id: scope.tenantId, principal_scope: 'GLOBAL', selected_capacity_claim: 'tenant_owner',
  capacity_authority_verified_by_this_endpoint: false, grant_issued: false, administrative_grantor_appointed: false });
const fresh = () => ({ status: 'REFRESHED', token_type: 'Bearer', access_token: 'test-renewed-access', refresh_token: 'test-renewed-refresh' });
const deferred = () => { let resolve; const promise = new Promise(done => { resolve = done; }); return { promise, resolve }; };
function Observer() {
  owner = useAuth();
  return <output data-testid="auth-state">{owner.isAuthenticated ? owner.user.id : 'SIGNED_OUT'}</output>;
}
async function mountOwner() {
  localStorage.setItem('wilsy_auth_token', 'test-old-access');
  localStorage.setItem('token', 'test-old-access');
  localStorage.setItem('wilsy_refresh_token', 'test-old-refresh');
  render(<AuthProvider><Observer /></AuthProvider>);
  await waitFor(() => expect(screen.getByTestId('auth-state').textContent).toBe(scope.principalId));
}

beforeAll(async () => {
  axios.defaults.adapter = async config => ok(config, {});
  ({ default: api, setActiveTenantTransportId } = await import('../../src/services/api.js'));
  ({ readFounderSessionEvidence } = await import('../../src/services/companyOperatingDocumentsClient.js'));
  ({ AuthProvider, useAuth } = await import('../../src/contexts/authContext.jsx'));
});
beforeEach(() => {
  calls = [];
  localStorage.clear(); sessionStorage.clear();
  delete api.defaults.headers.common.Authorization;
  setActiveTenantTransportId(null);
  route = async config => ok(config, {});
  api.defaults.adapter = async config => {
    // Capture request bytes before Axios reuses its mutable retry config.
    calls.push({ ...config, headers: new axios.AxiosHeaders(config.headers) });
    return route(config);
  };
});
afterEach(() => cleanup());
afterAll(() => { axios.defaults.adapter = originalAdapter; });

describe('actual shared Axios pipeline', () => {
  it('attaches the existing stored access bearer to Founder evidence and My Work', async () => {
    localStorage.setItem('wilsy_auth_token', 'test-access'); setActiveTenantTransportId(scope.tenantId);
    route = async config => ok(config, config.url.endsWith('founder-session-evidence') ? evidence() : {});
    const value = await readFounderSessionEvidence(scope, { token: 'test-access' });
    await api.get('/my-work');
    expect(value.principal_id).toBe(scope.principalId);
    expect(calls.map(config => config.headers.get('Authorization'))).toEqual(['Bearer test-access', 'Bearer test-access']);
    expect(calls.every(config => config.headers.get('X-Tenant-ID') === scope.tenantId)).toBe(true);
    expect(calls.every(config => !config.url.startsWith('/api/'))).toBe(true);
  });
  it('rejects missing company credentials before a network request', async () => {
    for (const path of ['/company-operating-documents/MISSION', '/company-operating-documents/STRATEGY', '/company-operating-documents/founder-session-evidence']) {
      await expect(api.get(path)).rejects.toMatchObject({ code: 'AUTHENTICATION_REQUIRED' });
    }
    expect(calls).toHaveLength(0);
  });
  it('preserves the exact reader-grant body through authenticated sealing', async () => {
    localStorage.setItem('wilsy_auth_token', 'test-access'); setActiveTenantTransportId(scope.tenantId);
    const body = { target_principal_id: scope.principalId, target_business_role: 'tenant_owner',
      expected_membership_revision: 0, expected_capacity_revision: 0, expected_assignment_revision: null,
      approval_reference: 'SYNTHETIC-DECISION', reason_reference: 'Synthetic read request', idempotency_key: 'test-only' };
    await api.post('/company-operating-documents/reader-grants', body);
    expect(JSON.parse(calls[0].data)).toEqual(body);
    expect(calls[0].headers.get('Authorization')).toBe('Bearer test-access');
  });
  it('rejects authenticated evidence for a different recipient', async () => {
    route = async config => ok(config, { ...evidence(), principal_id: 'another-principal' });
    await expect(readFounderSessionEvidence(scope, { token: 'test-access' })).rejects.toThrow('FOUNDER_SESSION_EVIDENCE_INVALID');
  });
});

describe('provider-owned EOS rotation', () => {
  it('refreshes once, revalidates the same workspace, then retries actual transport', async () => {
    route = async config => {
      if (config.url === '/auth/workspace-bootstrap') return ok(config, workspace());
      if (config.url === '/auth/global/refresh') return ok(config, fresh());
      if (config.headers.get('Authorization') === 'Bearer test-old-access') return reject401(config);
      return ok(config, evidence());
    };
    await mountOwner();
    let value;
    await act(async () => { value = await readFounderSessionEvidence(scope, { token: owner.token }); });
    expect(value.principal_id).toBe(scope.principalId);
    expect(calls.filter(config => config.url === '/auth/global/refresh')).toHaveLength(1);
    expect(calls.filter(config => config.url.endsWith('founder-session-evidence')).map(config => config.headers.get('Authorization')))
      .toEqual(['Bearer test-old-access', 'Bearer test-renewed-access']);
    expect(calls.find(config => config.url === '/auth/global/refresh').headers.get('Authorization')).toBeUndefined();
    expect(localStorage.getItem('wilsy_auth_token')).toBe('test-renewed-access');
    expect(owner.token).toBe('test-renewed-access');
  });
  it('coalesces concurrent failed reads into one exact-session refresh', async () => {
    const rotated = deferred();
    route = async config => {
      if (config.url === '/auth/workspace-bootstrap') return ok(config, workspace());
      if (config.url === '/auth/global/refresh') { await rotated.promise; return ok(config, fresh()); }
      if (config.headers.get('Authorization') === 'Bearer test-old-access') return reject401(config);
      return ok(config, {});
    };
    await mountOwner();
    const first = api.get('/my-work'); const second = api.get('/company-operating-documents/MISSION');
    await waitFor(() => expect(calls.filter(config => config.url === '/auth/global/refresh')).toHaveLength(1));
    await act(async () => { rotated.resolve(); await Promise.all([first, second]); });
    expect(calls.filter(config => config.url === '/auth/global/refresh')).toHaveLength(1);
  });
  it('invalidates the current session when EOS rejects refresh', async () => {
    route = async config => config.url === '/auth/workspace-bootstrap' ? ok(config, workspace()) : reject401(config);
    await mountOwner();
    await act(async () => { await expect(api.get('/my-work')).rejects.toMatchObject({ response: { status: 401 } }); });
    expect(localStorage.getItem('wilsy_auth_token')).toBeNull();
    expect(owner.isAuthenticated).toBe(false);
    expect(calls.filter(config => config.url === '/auth/global/refresh')).toHaveLength(1);
  });
  it('requires normal sign-in when the current session has no refresh credential', async () => {
    route = async config => config.url === '/auth/workspace-bootstrap' ? ok(config, workspace()) : reject401(config);
    await mountOwner(); localStorage.removeItem('wilsy_refresh_token');
    await act(async () => { await expect(api.get('/my-work')).rejects.toMatchObject({ response: { status: 401 } }); });
    expect(owner.isAuthenticated).toBe(false);
    expect(calls.some(config => config.url === '/auth/global/refresh')).toBe(false);
  });
  it('does not loop when EOS rejects the retried access credential', async () => {
    route = async config => {
      if (config.url === '/auth/workspace-bootstrap') return ok(config, workspace());
      if (config.url === '/auth/global/refresh') return ok(config, fresh());
      return reject401(config);
    };
    await mountOwner();
    await act(async () => { await expect(api.get('/my-work')).rejects.toMatchObject({ response: { status: 401 } }); });
    expect(owner.isAuthenticated).toBe(false);
    expect(calls.filter(config => config.url === '/auth/global/refresh')).toHaveLength(1);
    expect(calls.filter(config => config.url === '/my-work')).toHaveLength(2);
  });
  it('does not promote a refreshed credential bound to another principal', async () => {
    route = async config => {
      if (config.url === '/auth/workspace-bootstrap') return ok(config, workspace(config.headers.get('Authorization') === 'Bearer test-old-access' ? scope.principalId : 'foreign-principal'));
      if (config.url === '/auth/global/refresh') return ok(config, fresh());
      return reject401(config);
    };
    await mountOwner();
    await act(async () => { await expect(api.get('/my-work')).rejects.toMatchObject({ response: { status: 401 } }); });
    expect(localStorage.getItem('wilsy_auth_token')).toBeNull();
    expect(owner.isAuthenticated).toBe(false);
  });
  it('never retries or restores a session after logout overtakes rotation', async () => {
    const rotated = deferred();
    route = async config => {
      if (config.url === '/auth/workspace-bootstrap') return ok(config, workspace());
      if (config.url === '/auth/global/refresh') { await rotated.promise; return ok(config, fresh()); }
      if (config.url === '/auth/logout') return ok(config, {});
      return reject401(config);
    };
    await mountOwner();
    const result = api.get('/my-work').catch(error => error);
    await waitFor(() => expect(calls.some(config => config.url === '/auth/global/refresh')).toBe(true));
    await act(async () => { await owner.logout(); rotated.resolve(); await result; });
    expect(owner.isAuthenticated).toBe(false);
    expect(localStorage.getItem('wilsy_auth_token')).toBeNull();
    expect(calls.filter(config => config.url === '/my-work')).toHaveLength(1);
  });
});
// ARTIFACT: companyAuthenticationTransport.test.jsx
// VERSION: v1.0.0
// AUTHORITY BOUNDARY: Synthetic adapter regression only; no live acceptance claim.
// TENANT POSTURE: Exact synthetic scope; cross-principal refresh rejected.
// FAIL-CLOSED POSTURE: Failed/superseded refresh cannot preserve authentication.
// FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
