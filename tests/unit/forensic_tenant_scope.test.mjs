import test from 'node:test';
import assert from 'node:assert/strict';

import {
  requireForensicTenantScope,
  resolveForensicTenantScope,
} from '../../server/middleware/forensicTenantScope.js';

const TENANT = 'WILSYTENANT-4CD2FZ4O';

const authenticatedRequest = (overrides = {}) => ({
  user: { id: 'principal-1', tenantId: TENANT },
  tenantId: TENANT,
  params: {},
  query: {},
  body: {},
  headers: {},
  ...overrides,
});

test('forensic scope is derived from authenticated request context', () => {
  assert.equal(resolveForensicTenantScope(authenticatedRequest()), TENANT);
});

test('matching explicit tenant hints do not change authenticated scope', () => {
  const request = authenticatedRequest({
    params: { tenantId: TENANT },
    query: { tenantId: TENANT },
    body: { tenantId: TENANT },
    headers: { 'x-tenant-id': TENANT, 'x-wilsy-tenant-id': TENANT },
  });
  assert.equal(resolveForensicTenantScope(request), TENANT);
});

for (const [label, override] of [
  ['path parameter', { params: { tenantId: 'OTHER_TENANT' } }],
  ['query parameter', { query: { tenantId: 'OTHER_TENANT' } }],
  ['request body', { body: { tenantId: 'OTHER_TENANT' } }],
  ['tenant header', { headers: { 'x-tenant-id': 'OTHER_TENANT' } }],
  ['WILSY tenant header', { headers: { 'x-wilsy-tenant-id': 'OTHER_TENANT' } }],
  ['legacy root alias', { query: { tenantId: 'GLOBAL_ROOT' } }],
  ['legacy master alias', { body: { tenantId: 'MASTER' } }],
  ['multi-valued query', { query: { tenantId: [TENANT, 'OTHER_TENANT'] } }],
]) {
  test(`rejects caller-selected tenant scope in ${label}`, () => {
    assert.equal(resolveForensicTenantScope(authenticatedRequest(override)), null);
  });
}

test('does not accept a tenant supplied without authenticated request context', () => {
  assert.equal(
    resolveForensicTenantScope({ query: { tenantId: TENANT }, user: { id: 'principal-1' } }),
    null,
  );
});

test('rejects a principal and middleware tenant mismatch', () => {
  assert.equal(
    resolveForensicTenantScope(authenticatedRequest({
      user: { id: 'principal-1', tenantId: 'OTHER_TENANT' },
    })),
    null,
  );
});

test('middleware binds the resolved tenant and continues', () => {
  const request = authenticatedRequest();
  let continued = false;
  const response = {
    status() { throw new Error('unexpected denial'); },
    json() { throw new Error('unexpected denial'); },
  };
  requireForensicTenantScope(request, response, () => { continued = true; });
  assert.equal(continued, true);
  assert.equal(request.forensicTenantId, TENANT);
});

test('middleware rejects an invalid scope without continuing', () => {
  const request = authenticatedRequest({ query: { tenantId: 'OTHER_TENANT' } });
  let continued = false;
  let statusCode = null;
  let payload = null;
  const response = {
    status(code) { statusCode = code; return this; },
    json(value) { payload = value; return this; },
  };
  requireForensicTenantScope(request, response, () => { continued = true; });
  assert.equal(continued, false);
  assert.equal(statusCode, 403);
  assert.deepEqual(payload, {
    success: false,
    code: 'FORENSIC_TENANT_SCOPE_INVALID',
  });
});


test('canonicalizes case-insensitive authenticated tenant IDs before database use', () => {
  const request = authenticatedRequest({ tenantId: TENANT.toLowerCase() });
  assert.equal(resolveForensicTenantScope(request), TENANT);
});


test('rejects an authenticated principal without an explicit tenant membership', () => {
  const request = authenticatedRequest({ user: { id: 'principal-without-membership' } });
  assert.equal(resolveForensicTenantScope(request), null);
});
