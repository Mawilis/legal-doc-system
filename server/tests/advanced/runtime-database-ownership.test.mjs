import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { describe, it } from 'node:test';
import { resolveEosWorkspaceIdentity, resolveEosWorkspaceTenantScope } from '../../services/eosWorkspaceIdentity.js';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');

describe('EOS runtime database ownership inventory', () => {
  it('resolves PDF identity only through the authenticated EOS workspace projection', async () => {
    const calls = [];
    const result = await resolveEosWorkspaceIdentity({
      baseUrl: 'http://127.0.0.1:9095/',
      authorization: 'Bearer opaque-session-token',
      tenantId: 'WILSY-TENANT-1',
      fetchImpl: async (url, options) => {
        calls.push({ url, options });
        return {
          ok: true,
          status: 200,
          json: async () => ({
            status: 'READY',
            user: {
              id: 'WILSY-PRINCIPAL-1',
              email: 'person@example.test',
              firstName: 'Wilsy',
              lastName: 'Owner',
            },
            workspace: { tenantId: 'WILSY-TENANT-1' },
          }),
        };
      },
    });

    assert.equal(result.ok, true);
    assert.deepEqual(result.user, {
      id: 'WILSY-PRINCIPAL-1',
      email: 'person@example.test',
      firstName: 'Wilsy',
      lastName: 'Owner',
      displayName: 'Wilsy Owner',
    });
    assert.equal(calls.length, 1);
    assert.equal(calls[0].url, 'http://127.0.0.1:9095/api/auth/workspace-bootstrap');
    assert.equal(calls[0].options.headers.Authorization, 'Bearer opaque-session-token');
    assert.equal(calls[0].options.headers['X-Tenant-ID'], 'WILSY-TENANT-1');
  });

  it('rejects PDF body tenant substitution against the EOS-authorized workspace', () => {
    const workspace = { tenantId: 'WILSY-TENANT-A' };
    assert.deepEqual(
      resolveEosWorkspaceTenantScope({
        requestedTenantId: 'WILSY-TENANT-A',
        workspace,
        suppliedTenantIds: ['WILSY-TENANT-A'],
      }),
      { ok: true, tenantId: 'WILSY-TENANT-A' },
    );
    assert.deepEqual(
      resolveEosWorkspaceTenantScope({
        requestedTenantId: 'WILSY-TENANT-A',
        workspace,
        suppliedTenantIds: ['WILSY-TENANT-B'],
      }),
      { ok: false, status: 403, code: 'WORKSPACE_SCOPE_MISMATCH' },
    );
    assert.deepEqual(
      resolveEosWorkspaceTenantScope({
        requestedTenantId: 'WILSY-TENANT-B',
        workspace,
      }),
      { ok: false, status: 403, code: 'WORKSPACE_SCOPE_MISMATCH' },
    );
  });

  it('rejects missing bearer or tenant scope before contacting EOS', async () => {
    let calls = 0;
    const fetchImpl = async () => {
      calls += 1;
      throw new Error('must not call');
    };

    assert.deepEqual(
      await resolveEosWorkspaceIdentity({
        baseUrl: 'http://127.0.0.1:9095',
        authorization: '',
        tenantId: 'WILSY-TENANT-1',
        fetchImpl,
      }),
      { ok: false, status: 401, code: 'AUTHENTICATION_REQUIRED' },
    );
    assert.deepEqual(
      await resolveEosWorkspaceIdentity({
        baseUrl: 'http://127.0.0.1:9095',
        authorization: 'Bearer opaque-session-token',
        tenantId: '',
        fetchImpl,
      }),
      { ok: false, status: 400, code: 'TENANT_SCOPE_REQUIRED' },
    );
    assert.equal(calls, 0);
  });

  it('maps EOS authorization failures and malformed authority responses fail-closed', async () => {
    const failure = async (status) => resolveEosWorkspaceIdentity({
      baseUrl: 'http://127.0.0.1:9095',
      authorization: 'Bearer opaque-session-token',
      tenantId: 'WILSY-TENANT-1',
      fetchImpl: async () => ({ ok: false, status }),
    });

    assert.deepEqual(await failure(401), {
      ok: false, status: 401, code: 'AUTHENTICATION_REQUIRED',
    });
    assert.deepEqual(await failure(403), {
      ok: false, status: 403, code: 'WORKSPACE_ACCESS_DENIED',
    });
    assert.deepEqual(await failure(500), {
      ok: false, status: 503, code: 'AUTHORITY_UNAVAILABLE',
    });

    const malformed = await resolveEosWorkspaceIdentity({
      baseUrl: 'http://127.0.0.1:9095',
      authorization: 'Bearer opaque-session-token',
      tenantId: 'WILSY-TENANT-1',
      fetchImpl: async () => ({
        ok: true,
        status: 200,
        json: async () => ({ status: 'READY', user: { id: '', email: '' } }),
      }),
    });
    assert.deepEqual(malformed, {
      ok: false, status: 503, code: 'AUTHORITY_RESPONSE_INVALID',
    });
  });
  it('keeps the active Node BFF database-free and delegates PDF identity to EOS', async () => {
    const source = await readFile(resolve(ROOT, 'server/server.js'), 'utf8');
    assert.doesNotMatch(source, /mongoose/);
    assert.match(source, /database: 'NOT_CONNECTED_BY_BFF'/);
    assert.match(source, /databaseAuthority: 'PYTHON_EOS'/);
    assert.doesNotMatch(source, /MongoClient|MONGODB_URI|MONGO_URI/);

    const pdfController = await readFile(
      resolve(ROOT, 'server/controllers/businessArtifactPdfController.js'),
      'utf8',
    );
    assert.doesNotMatch(pdfController, /mongoose|findWilsyLiveUserProfileDocument/);
    assert.match(pdfController, /EOS_VERIFIED_WORKSPACE_BOOTSTRAP/);
    assert.match(source, /resolveEosWorkspaceIdentity/);
    assert.match(source, /requireEosWorkspaceIdentity, generateSovereignArtifactPdf/);

    const identityAdapter = await readFile(
      resolve(ROOT, 'server/services/eosWorkspaceIdentity.js'),
      'utf8',
    );
    assert.match(identityAdapter, /\/api\/auth\/workspace-bootstrap/);
    assert.match(identityAdapter, /resolveEosWorkspaceTenantScope/);
  });

  it('keeps PM2 and local development on the repository-defined EOS entrypoints', async () => {
    const pm2 = await readFile(resolve(ROOT, 'server/ecosystem.config.js'), 'utf8');
    assert.match(pm2, /script: '\.\/server\.js'/);
    assert.doesNotMatch(pm2, /app\.js|scheduler\.js/);

    const dev = await readFile(resolve(ROOT, 'scripts/start-dev-stack.sh'), 'utf8');
    assert.match(dev, /uvicorn tools\.eos\.api\.server:app/);
    assert.doesNotMatch(dev, /server\/app\.js|server\/jobs\/scheduler\.js/);

    const packageJson = JSON.parse(await readFile(resolve(ROOT, 'package.json'), 'utf8'));
    assert.equal(packageJson.scripts.dev, 'bash scripts/start-dev-stack.sh');
    assert.match(packageJson.scripts['dev:kernel'], /uvicorn tools\.eos\.api\.server:app/);
  });
});
