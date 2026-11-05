import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { resolveEosWorkspaceIdentity } from '../../services/eosWorkspaceIdentity.js';

const INPUT = {
  baseUrl: 'http://127.0.0.1:9095/',
  authorization: 'Bearer signed-access-token',
  tenantId: 'WILSYTENANT-CERT',
};

describe('EOS workspace identity resolver for local PDF rendering', () => {
  it('uses EOS workspace-bootstrap and returns only its verified user projection', async () => {
    let observedUrl;
    let observedOptions;
    const result = await resolveEosWorkspaceIdentity({
      ...INPUT,
      fetchImpl: async (url, options) => {
        observedUrl = url;
        observedOptions = options;
        return {
          ok: true,
          status: 200,
          json: async () => ({
            status: 'READY',
            user: {
              id: 'principal-certified',
              email: 'person@example.test',
              firstName: 'Ada',
              lastName: 'Example',
            },
            workspace: { tenantId: INPUT.tenantId, workspaceId: 'LEGAL_WORKSPACE' },
          }),
        };
      },
    });

    assert.equal(observedUrl, 'http://127.0.0.1:9095/api/auth/workspace-bootstrap');
    assert.equal(observedOptions.method, 'GET');
    assert.equal(observedOptions.headers.Authorization, INPUT.authorization);
    assert.equal(observedOptions.headers['X-Tenant-ID'], INPUT.tenantId);
    assert.equal(result.ok, true);
    assert.deepEqual(result.user, {
      id: 'principal-certified',
      email: 'person@example.test',
      firstName: 'Ada',
      lastName: 'Example',
      displayName: 'Ada Example',
    });
    assert.equal(result.workspace.workspaceId, 'LEGAL_WORKSPACE');
  });

  it('rejects missing bearer authority without contacting EOS', async () => {
    let called = false;
    const result = await resolveEosWorkspaceIdentity({
      ...INPUT,
      authorization: '',
      fetchImpl: async () => { called = true; },
    });
    assert.deepEqual(result, {
      ok: false,
      status: 401,
      code: 'AUTHENTICATION_REQUIRED',
    });
    assert.equal(called, false);
  });

  it('requires an explicit tenant scope before contacting EOS', async () => {
    let called = false;
    const result = await resolveEosWorkspaceIdentity({
      ...INPUT,
      tenantId: '',
      fetchImpl: async () => { called = true; },
    });
    assert.deepEqual(result, {
      ok: false,
      status: 400,
      code: 'TENANT_SCOPE_REQUIRED',
    });
    assert.equal(called, false);
  });

  it('preserves authentication and workspace denial while bounding upstream failures', async () => {
    for (const [upstreamStatus, expectedStatus, expectedCode] of [
      [401, 401, 'AUTHENTICATION_REQUIRED'],
      [403, 403, 'WORKSPACE_ACCESS_DENIED'],
      [500, 503, 'AUTHORITY_UNAVAILABLE'],
    ]) {
      const result = await resolveEosWorkspaceIdentity({
        ...INPUT,
        fetchImpl: async () => ({ ok: false, status: upstreamStatus }),
      });
      assert.deepEqual(result, {
        ok: false,
        status: expectedStatus,
        code: expectedCode,
      });
    }
  });

  it('fails closed on malformed EOS projections and network errors', async () => {
    const malformed = await resolveEosWorkspaceIdentity({
      ...INPUT,
      fetchImpl: async () => ({
        ok: true,
        status: 200,
        json: async () => ({ status: 'READY', user: { id: 'principal-only' } }),
      }),
    });
    assert.deepEqual(malformed, {
      ok: false,
      status: 503,
      code: 'AUTHORITY_RESPONSE_INVALID',
    });

    const unavailable = await resolveEosWorkspaceIdentity({
      ...INPUT,
      fetchImpl: async () => { throw new Error('private transport detail'); },
    });
    assert.deepEqual(unavailable, {
      ok: false,
      status: 503,
      code: 'AUTHORITY_UNAVAILABLE',
    });
  });
});
