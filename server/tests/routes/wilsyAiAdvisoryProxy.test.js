/**
 * WILSY OS R1D-B0F-B4-R1 selective legal-acceptance BFF transport certificate.
 *
 * TITLE: Legal Acceptance Browser-to-Python Proxy Certificate
 * VERSION: v1.1.0-R1D-B0F-B4-R1
 * AUTHORITY: Wilsy OS Core Governance; transport evidence only
 * EPITOME: Proves exact legal-acceptance route, path, header, body, status, and fail-closed
 *          behavior without MongoDB, providers, models, or external networks.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/routes/wilsyAiAdvisoryProxy.test.js
 * COLLABORATION / OWNERSHIP: server/server.js selective proxy and Python EOS.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.1.0-R1D-B0F-B4-R1 certifies the bounded legal-acceptance transport seam.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Fake upstream captures only test headers/body.
 * TENANT BOUNDARY: X-Tenant-ID is forwarded unchanged; no tenant is invented.
 * AUTHORITY BOUNDARY: Node is transport-only; Python remains C1C/C1E authority.
 * FINANCIAL AUTHORITY BOUNDARY: No financial route or execution is exposed.
 */

import { strict as assert } from 'node:assert';
import { createServer } from 'node:http';
import request from 'supertest';

const upstreamRequests = [];
let upstream;
let createApp;
let app;

before(async () => {
  upstream = createServer((req, res) => {
    const chunks = [];
    req.on('data', (chunk) => chunks.push(chunk));
    req.on('end', () => {
      const body = Buffer.concat(chunks).toString('utf8');
      upstreamRequests.push({
        method: req.method,
        path: req.url,
        headers: req.headers,
        body,
      });

      if (
        req.url.startsWith('/api/legal-acceptance/') &&
        req.headers.authorization === 'Bearer status-401'
      ) {
        res.writeHead(401, { 'content-type': 'application/json', 'cache-control': 'no-store' });
        res.end(
          JSON.stringify({
            error_code: 'UNAUTHORIZED',
            detail: 'Missing authentication credentials.',
          })
        );
        return;
      }
      if (
        req.url.startsWith('/api/legal-acceptance/') &&
        req.headers.authorization === 'Bearer status-403'
      ) {
        res.writeHead(403, { 'content-type': 'application/json', 'cache-control': 'no-store' });
        res.end(JSON.stringify({ detail: 'LEGAL_ACCEPTANCE_FORBIDDEN' }));
        return;
      }
      if (
        req.url.startsWith('/api/legal-acceptance/') &&
        req.headers.authorization === 'Bearer status-409'
      ) {
        res.writeHead(409, { 'content-type': 'application/json', 'cache-control': 'no-store' });
        res.end(JSON.stringify({ detail: 'LEGAL_ACCEPTANCE_IDEMPOTENCY_CONFLICT' }));
        return;
      }

      if (req.url === '/api/wilsy-ai/legal-next-actions/conflict-id') {
        res.writeHead(409, { 'content-type': 'application/json' });
        res.end(JSON.stringify({ detail: 'C1E_SOURCE_SNAPSHOT_STALE' }));
        return;
      }
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ orchestration_id: 'c1c-root-1', advisory_id: 'c1e-advisory-1' }));
    });
  });
  await new Promise((resolve) => upstream.listen(0, '127.0.0.1', resolve));
  process.env.KENNEL_URL = `http://127.0.0.1:${upstream.address().port}`;
  ({ default: createApp } = await import('../../server.js'));
  app = createApp();
});

after(async () => {
  await new Promise((resolve, reject) =>
    upstream.close((error) => (error ? reject(error) : resolve()))
  );
});

beforeEach(() => {
  upstreamRequests.length = 0;
});

describe('C1C/C1E selective BFF transport', () => {
  it('forwards C1C legal-services with exact path, raw body, and institutional headers', async () => {
    const body = { prompt: 'review the recorded matter' };
    const response = await request(app)
      .post('/api/wilsy-ai/legal-services')
      .set('Authorization', 'Bearer test-token')
      .set('X-Tenant-ID', 'tenant-r1a')
      .set('Idempotency-Key', 'idem-r1a')
      .set('X-Trace-ID', 'trace-r1a')
      .set('X-Request-ID', 'request-r1a')
      .send(body)
      .expect(200);

    assert.deepEqual(response.body, {
      orchestration_id: 'c1c-root-1',
      advisory_id: 'c1e-advisory-1',
    });
    assert.equal(upstreamRequests[0].method, 'POST');
    assert.equal(upstreamRequests[0].path, '/api/wilsy-ai/legal-services');
    assert.equal(upstreamRequests[0].body, JSON.stringify(body));
    assert.equal(upstreamRequests[0].headers.authorization, 'Bearer test-token');
    assert.equal(upstreamRequests[0].headers['x-tenant-id'], 'tenant-r1a');
    assert.equal(upstreamRequests[0].headers['x-idempotency-key'], 'idem-r1a');
    assert.equal(upstreamRequests[0].headers['x-trace-id'], 'trace-r1a');
    assert.equal(upstreamRequests[0].headers['x-request-id'], 'request-r1a');
  });

  it('forwards C1E generation and preserves advisory-id GET suffix exactly', async () => {
    await request(app)
      .post('/api/wilsy-ai/legal-next-actions')
      .send({ orchestration_id: 'c1c-root-1' })
      .expect(200);
    await request(app)
      .get('/api/wilsy-ai/legal-next-actions/advisory-123')
      .set('Authorization', 'Bearer test-token')
      .set('X-Tenant-ID', 'tenant-r1a')
      .expect(200);

    assert.equal(upstreamRequests[0].path, '/api/wilsy-ai/legal-next-actions');
    assert.equal(upstreamRequests[1].path, '/api/wilsy-ai/legal-next-actions/advisory-123');
  });

  it('passes Python non-2xx semantics through without false success', async () => {
    const response = await request(app)
      .get('/api/wilsy-ai/legal-next-actions/conflict-id')
      .set('X-Tenant-ID', 'tenant-r1a')
      .expect(409);
    assert.deepEqual(response.body, { detail: 'C1E_SOURCE_SNAPSHOT_STALE' });
  });

  it('forwards legal-acceptance status, document, and acceptance without interpreting authority', async () => {
    const statusResponse = await request(app)
      .get('/api/legal-acceptance/status')
      .set('Authorization', 'Bearer test-token')
      .set('X-Tenant-ID', 'tenant-legal')
      .expect(200);
    assert.deepEqual(statusResponse.body, {
      orchestration_id: 'c1c-root-1',
      advisory_id: 'c1e-advisory-1',
    });

    await request(app)
      .get('/api/legal-acceptance/documents/charter-v1')
      .set('Authorization', 'Bearer test-token')
      .set('X-Tenant-ID', 'tenant-legal')
      .expect(200);

    const body = {
      document_id: 'charter-v1',
      document_version: '1.0.0',
      document_sha3_512: 'a'.repeat(128),
      acceptance_method: 'ACKNOWLEDGEMENT',
    };
    await request(app)
      .post('/api/legal-acceptance/accept')
      .set('Authorization', 'Bearer test-token')
      .set('X-Tenant-ID', 'tenant-legal')
      .set('Idempotency-Key', 'legal-idem-1')
      .send(body)
      .expect(200);

    assert.equal(upstreamRequests[0].path, '/api/legal-acceptance/status');
    assert.equal(upstreamRequests[1].path, '/api/legal-acceptance/documents/charter-v1');
    assert.equal(upstreamRequests[2].path, '/api/legal-acceptance/accept');
    assert.equal(upstreamRequests[2].headers.authorization, 'Bearer test-token');
    assert.equal(upstreamRequests[2].headers['idempotency-key'], 'legal-idem-1');
    assert.equal(upstreamRequests[2].headers['x-idempotency-key'], 'legal-idem-1');
    assert.equal(upstreamRequests[2].body, JSON.stringify(body));
  });

  it('preserves legal-acceptance 401, 403, and 409 response semantics and no-store', async () => {
    for (const [token, expectedStatus] of [
      ['status-401', 401],
      ['status-403', 403],
      ['status-409', 409],
    ]) {
      const response = await request(app)
        .get('/api/legal-acceptance/status')
        .set('Authorization', `Bearer ${token}`)
        .expect(expectedStatus);
      assert.equal(response.headers['cache-control'], 'no-store');
    }
  });

  it('leaves reasoning and legal-tools outside the selective proxy boundary', async () => {
    const reasoning = await request(app)
      .post('/api/wilsy-ai/reasoning')
      .send({ prompt: 'not proxied' })
      .expect(404);
    const legalTools = await request(app).get('/api/wilsy-ai/legal-tools').expect(404);
    assert.equal(reasoning.body.error, 'BFF_ROUTE_NOT_PROXIED');
    assert.equal(legalTools.body.error, 'BFF_ROUTE_NOT_PROXIED');
    assert.equal(upstreamRequests.length, 0);
  });
});

// ARTIFACT: wilsyAiAdvisoryProxy.test.js
// VERSION: v1.1.0-R1D-B0F-B4-R1
// AUTHORITY BOUNDARY: deterministic transport certificate only
// TENANT POSTURE: verifies unchanged institutional tenant forwarding
// FAIL-CLOSED POSTURE: non-2xx and unapproved namespaces never become success
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
