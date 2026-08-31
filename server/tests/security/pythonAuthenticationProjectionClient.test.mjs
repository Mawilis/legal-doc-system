/**
 * TITLE: WILSY OS Python Authentication Projection Client Certification
 * VERSION: v1.0.0-PYTHON-AUTHENTICATION-PROJECTION-CLIENT-CERT
 * AUTHORITY: Certification evidence only; grants no authentication, tenant, role, permission, or financial authority.
 * EPITOME: Proves exact Node → Python authentication transport, bounded projection, and fail-closed denial/outage semantics.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/security/pythonAuthenticationProjectionClient.test.mjs
 * COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
 * CERTIFICATION/UPDATE DATE: 2026-08-31
 * CHANGELOG:
 *   v1.0.0-PYTHON-AUTHENTICATION-PROJECTION-CLIENT-CERT — Initial transport/runtime certificate for the bounded authentication projection client.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Uses generated local credentials only; never contacts production services; response bodies containing hostile authority fields must be rejected.
 * TENANT BOUNDARY: Certifies that tenant/role/permission claims are neither accepted nor returned.
 * AUTHORITY BOUNDARY: Evidence only; Python get_current_identity remains the authentication authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial execution authority.
 */

import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import http from 'node:http';
import test from 'node:test';

import {
  PYTHON_AUTHENTICATION_ERROR_CODES,
  PythonAuthenticationProjectionError,
  parsePythonAuthenticationProjection,
  requireBearerAuthorization,
  resolvePythonAuthenticationBaseUrl,
  verifyPythonAuthenticationProjection,
} from '../../services/pythonAuthenticationProjectionClient.js';

async function withServer(handler, callback) {
  const server = http.createServer(handler);
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const address = server.address();
  assert(address && typeof address === 'object');
  try {
    return await callback(`http://127.0.0.1:${address.port}`);
  } finally {
    await new Promise((resolve, reject) =>
      server.close((error) => (error ? reject(error) : resolve()))
    );
  }
}

function json(res, statusCode, body) {
  const encoded = Buffer.from(JSON.stringify(body));
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Content-Length': encoded.length,
  });
  res.end(encoded);
}

test('base URL resolution uses the canonical Kennel origin and rejects ambiguous configuration', () => {
  assert.equal(resolvePythonAuthenticationBaseUrl({}), 'http://127.0.0.1:9095');
  assert.equal(
    resolvePythonAuthenticationBaseUrl({ KENNEL_URL: 'https://python.internal.example/' }),
    'https://python.internal.example'
  );
  for (const candidate of [
    'ftp://127.0.0.1:9095',
    'http://user:secret@127.0.0.1:9095',
    'http://127.0.0.1:9095/kernel',
    'http://127.0.0.1:9095/?x=1',
    'not a url',
  ]) {
    assert.throws(
      () => resolvePythonAuthenticationBaseUrl({ KENNEL_URL: candidate }),
      (error) =>
        error instanceof PythonAuthenticationProjectionError &&
        error.code === PYTHON_AUTHENTICATION_ERROR_CODES.CONFIGURATION
    );
  }
});

test('bearer syntax is transport-only and malformed credentials fail before any HTTP call', async () => {
  assert.equal(
    requireBearerAuthorization('Bearer opaque.generated.token'),
    'Bearer opaque.generated.token'
  );
  let calls = 0;
  for (const authorization of [undefined, '', 'opaque.generated.token', 'Basic abc', 'Bearer']) {
    await assert.rejects(
      verifyPythonAuthenticationProjection({
        authorization,
        fetchImpl: async () => {
          calls += 1;
          throw new Error('must not execute');
        },
      }),
      (error) =>
        error instanceof PythonAuthenticationProjectionError &&
        error.code === PYTHON_AUTHENTICATION_ERROR_CODES.INVALID_CREDENTIAL &&
        error.statusCode === 401
    );
  }
  assert.equal(calls, 0);
});

test('real Node HTTP transport calls only the canonical Python verify-token path and forwards no tenant or role authority', async () => {
  let observation;
  await withServer(
    (req, res) => {
      observation = {
        method: req.method,
        url: req.url,
        authorization: req.headers.authorization,
        accept: req.headers.accept,
        tenant: req.headers['x-tenant-id'],
        role: req.headers['x-role'],
      };
      json(res, 200, {
        success: true,
        status: 'VERIFIED',
        user: { id: 'principal-generated-1', email: 'principal1@example.invalid' },
      });
    },
    async (baseUrl) => {
      const projection = await verifyPythonAuthenticationProjection({
        authorization: 'Bearer generated.transport.credential',
        baseUrl,
      });
      assert.deepEqual(projection, {
        id: 'principal-generated-1',
        email: 'principal1@example.invalid',
      });
      assert(Object.isFrozen(projection));
    }
  );

  assert.deepEqual(observation, {
    method: 'GET',
    url: '/api/auth/verify-token',
    authorization: 'Bearer generated.transport.credential',
    accept: 'application/json',
    tenant: undefined,
    role: undefined,
  });
});

test('projection parser accepts exactly id/email and rejects role, tenant, permission, credential, and unknown fields', () => {
  const valid = {
    success: true,
    status: 'VERIFIED',
    user: { id: 'principal-generated-2', email: 'principal2@example.invalid' },
  };
  assert.deepEqual(parsePythonAuthenticationProjection(valid), {
    id: 'principal-generated-2',
    email: 'principal2@example.invalid',
  });

  for (const forbidden of ['role', 'tenantId', 'permissions', 'token', 'securityClearance']) {
    assert.throws(
      () =>
        parsePythonAuthenticationProjection({
          ...valid,
          user: { ...valid.user, [forbidden]: 'hostile' },
        }),
      (error) =>
        error instanceof PythonAuthenticationProjectionError &&
        error.code === PYTHON_AUTHENTICATION_ERROR_CODES.INVALID_PROJECTION
    );
  }

  assert.throws(() => parsePythonAuthenticationProjection({ ...valid, authority: 'hostile' }));
  assert.throws(() => parsePythonAuthenticationProjection({ ...valid, success: false }));
  assert.throws(() => parsePythonAuthenticationProjection({ ...valid, status: 'AUTHORIZED' }));
});

test('Python 401 is a bounded authentication denial and upstream body detail is never leaked', async () => {
  await withServer(
    (req, res) => {
      json(res, 401, { detail: 'secret-upstream-diagnostic' });
    },
    async (baseUrl) => {
      await assert.rejects(
        verifyPythonAuthenticationProjection({
          authorization: 'Bearer generated.denied.credential',
          baseUrl,
        }),
        (error) => {
          assert(error instanceof PythonAuthenticationProjectionError);
          assert.equal(error.code, PYTHON_AUTHENTICATION_ERROR_CODES.DENIED);
          assert.equal(error.statusCode, 401);
          assert.doesNotMatch(error.message, /secret-upstream-diagnostic/u);
          return true;
        }
      );
    }
  );
});

test('unexpected upstream status fails closed as authentication authority unavailable', async () => {
  await withServer(
    (req, res) => {
      json(res, 500, { detail: 'database topology and stack detail must remain private' });
    },
    async (baseUrl) => {
      await assert.rejects(
        verifyPythonAuthenticationProjection({
          authorization: 'Bearer generated.upstream.failure',
          baseUrl,
        }),
        (error) =>
          error instanceof PythonAuthenticationProjectionError &&
          error.code === PYTHON_AUTHENTICATION_ERROR_CODES.UNAVAILABLE &&
          error.statusCode === 503 &&
          !error.message.includes('database topology')
      );
    }
  );
});

test('malformed successful response fails closed and cannot synthesize an identity', async () => {
  const malformedPayloads = [
    { success: true, status: 'VERIFIED', user: { id: '', email: 'x@example.invalid' } },
    { success: true, status: 'VERIFIED', user: { id: 'p', email: '' } },
    { success: true, status: 'VERIFIED', user: null },
  ];
  for (const body of malformedPayloads) {
    await withServer(
      (req, res) => json(res, 200, body),
      async (baseUrl) => {
        await assert.rejects(
          verifyPythonAuthenticationProjection({
            authorization: 'Bearer generated.malformed.projection',
            baseUrl,
          }),
          (error) =>
            error instanceof PythonAuthenticationProjectionError &&
            error.code === PYTHON_AUTHENTICATION_ERROR_CODES.INVALID_PROJECTION
        );
      }
    );
  }
});

test('network failure and timeout fail closed as unavailable', async () => {
  await assert.rejects(
    verifyPythonAuthenticationProjection({
      authorization: 'Bearer generated.network.failure',
      baseUrl: 'http://127.0.0.1:1',
      timeoutMs: 100,
    }),
    (error) =>
      error instanceof PythonAuthenticationProjectionError &&
      error.code === PYTHON_AUTHENTICATION_ERROR_CODES.UNAVAILABLE
  );

  await withServer(
    (req, res) => {
      setTimeout(
        () =>
          json(res, 200, {
            success: true,
            status: 'VERIFIED',
            user: { id: 'late', email: 'late@example.invalid' },
          }),
        200
      );
    },
    async (baseUrl) => {
      await assert.rejects(
        verifyPythonAuthenticationProjection({
          authorization: 'Bearer generated.timeout.failure',
          baseUrl,
          timeoutMs: 50,
        }),
        (error) =>
          error instanceof PythonAuthenticationProjectionError &&
          error.code === PYTHON_AUTHENTICATION_ERROR_CODES.UNAVAILABLE
      );
    }
  );
});

test('client source contains no local JWT, user database, tenant, role, or bypass authority implementation', async () => {
  const source = await readFile('server/services/pythonAuthenticationProjectionClient.js', 'utf8');
  const executable = source.replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, '');
  assert.doesNotMatch(
    executable,
    /jsonwebtoken|jwt\.verify|User\.findById|canBypassTenant|requireRole|authorizeRoles/u
  );
  assert.doesNotMatch(executable, /X-Tenant-ID|X-Role|tenantId|securityClearance/u);
});

// ARTIFACT: pythonAuthenticationProjectionClient.test.mjs
// VERSION: v1.0.0-PYTHON-AUTHENTICATION-PROJECTION-CLIENT-CERT
// AUTHORITY BOUNDARY: certification evidence only; Python remains the authenticated identity authority.
// TENANT POSTURE: generated tests prove no tenant/role/permission authority crosses the client boundary.
// FAIL-CLOSED POSTURE: invalid credential, denial, outage, timeout, malformed projection, and unexpected status cannot synthesize identity.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
// END OF WILSY OS SOVEREIGN ARTIFACT
