/**
 * WILSY OS P0-C4E1 SOVEREIGN BFF PROXY RUNTIME CONTRACT CERTIFICATE
 * VERSION: v2.0.0-P0-C4E1
 * AUTHORITY: Wilsy OS Core Governance; transport evidence only
 * EPITOME: Freezes server/server.js proxy behavior before adapter replacement.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/routes/wilsyAiAdvisoryProxy.test.js
 * COLLABORATION / OWNERSHIP: Node BFF fixed mounts, selective Legal routes, Python Kennel EOS.
 * CERTIFICATION / UPDATE DATE: 2026-10-03
 * CHANGELOG: v2.0.0-P0-C4E1 expands v1.1.0 into route, path, query, method,
 *            byte-stream, header, no-fabrication, timeout, and failure evidence.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic loopback evidence only; no external services or secrets.
 * TENANT BOUNDARY: Supplied tenant evidence is forwarded; no GLOBAL_ROOT is invented.
 * AUTHORITY BOUNDARY: Node transports only; Python EOS retains business/legal authority.
 * FINANCIAL AUTHORITY BOUNDARY: Proxy success is not execution or settlement; Kennel EOS is exclusive.
 */

import { strict as assert } from 'node:assert';
import { readFile } from 'node:fs/promises';
import { createServer, request as httpRequest } from 'node:http';
import request from 'supertest';

const SERVER_SOURCE_URL = new URL('../../server.js', import.meta.url);
const upstreamRequests = [];
let upstream;
let upstreamPort;
let bffServer;
let bffPort;
let app;
let releaseStream;
let streamBarrier;

function resetStreamBarrier() {
  streamBarrier = new Promise((resolve) => {
    releaseStream = resolve;
  });
}

function listen(server, port = 0) {
  return new Promise((resolve, reject) => {
    const failed = (error) => {
      server.off('listening', ready);
      reject(error);
    };
    const ready = () => {
      server.off('error', failed);
      resolve(server.address().port);
    };
    server.once('error', failed);
    server.once('listening', ready);
    server.listen(port, '127.0.0.1');
  });
}

function close(server) {
  if (!server?.listening) return Promise.resolve();
  return new Promise((resolve, reject) =>
    server.close((error) => (error ? reject(error) : resolve()))
  );
}

function rawRequest({ method = 'GET', path, headers = {}, chunks = [] }) {
  let firstChunkResolve;
  const firstChunk = new Promise((resolve) => {
    firstChunkResolve = resolve;
  });
  const completed = new Promise((resolve, reject) => {
    const outgoing = httpRequest(
      { host: '127.0.0.1', port: bffPort, method, path, headers },
      (response) => {
        const body = [];
        response.once('data', (chunk) => firstChunkResolve(Buffer.from(chunk)));
        response.on('data', (chunk) => body.push(Buffer.from(chunk)));
        response.once('end', () =>
          resolve({
            status: response.statusCode,
            headers: response.headers,
            body: Buffer.concat(body),
          })
        );
        response.once('error', reject);
      }
    );
    outgoing.once('error', reject);
    for (const chunk of chunks) outgoing.write(chunk);
    outgoing.end();
  });
  return { completed, firstChunk };
}

function createFakeUpstream() {
  return createServer((req, res) => {
    const chunks = [];
    req.on('data', (chunk) => chunks.push(Buffer.from(chunk)));
    req.on('end', () => {
      upstreamRequests.push({
        method: req.method,
        path: req.url,
        headers: { ...req.headers },
        body: Buffer.concat(chunks),
      });
      if (req.url === '/api/kernel/stream') {
        res.writeHead(206, {
          'content-type': 'application/octet-stream',
          'cache-control': 'no-store',
          'x-wilsy-upstream': 'stream-certificate',
        });
        res.write(Buffer.from([0, 1, 2, 3]));
        streamBarrier.then(() => res.end(Buffer.from([252, 253, 254, 255])));
        return;
      }
      if (req.url === '/api/kernel/failure') {
        res.writeHead(502, {
          'content-type': 'application/octet-stream',
          'cache-control': 'no-cache',
          'x-wilsy-upstream': 'failure-certificate',
        });
        res.end(Buffer.from('upstream-failure-byte-body'));
        return;
      }
      const token = req.headers.authorization;
      const legalStatus = {
        'Bearer status-401': 401,
        'Bearer status-403': 403,
        'Bearer status-409': 409,
      }[token];
      if (req.url.startsWith('/api/legal-acceptance/') && legalStatus) {
        res.writeHead(legalStatus, {
          'content-type': 'application/json',
          'cache-control': 'no-store',
        });
        res.end(JSON.stringify({ detail: `LEGAL_ACCEPTANCE_${legalStatus}` }));
        return;
      }
      if (req.url === '/api/wilsy-ai/legal-next-actions/conflict-id') {
        res.writeHead(409, { 'content-type': 'application/json' });
        res.end(JSON.stringify({ detail: 'C1E_SOURCE_SNAPSHOT_STALE' }));
        return;
      }
      res.writeHead(200, { 'content-type': 'application/json', 'x-wilsy-upstream': 'default' });
      res.end(JSON.stringify({ orchestration_id: 'c1c-root-1', advisory_id: 'c1e-advisory-1' }));
    });
  });
}

before(async () => {
  resetStreamBarrier();
  upstream = createFakeUpstream();
  upstreamPort = await listen(upstream);
  process.env.KENNEL_URL = `http://127.0.0.1:${upstreamPort}`;
  const { default: createApp } = await import('../../server.js');
  app = createApp();
  bffServer = createServer(app);
  bffPort = await listen(bffServer);
});

after(async () => {
  releaseStream?.();
  await Promise.all([close(bffServer), close(upstream)]);
});

beforeEach(() => {
  upstreamRequests.length = 0;
});

describe('fixed proxy route, path, query, and method contract', () => {
  it('maps every broad mount to its exact upstream prefix', async () => {
    const mappings = [
      ['/api/auth/session', '/api/auth/session'],
      ['/auth/session', '/api/auth/session'],
      ['/api/tenants/t1', '/api/tenants/t1'],
      ['/api/business/tenants/t1', '/api/tenants/t1'],
      ['/api/employees/e1', '/api/employees/e1'],
      ['/api/kernel/status', '/api/kernel/status'],
      ['/api/plans/p1', '/api/plans/p1'],
      ['/api/subscriptions/s1', '/api/subscriptions/s1'],
      ['/api/billing/invoices/i1', '/billing/invoices/i1'],
      ['/billing/invoices/i1', '/billing/invoices/i1'],
    ];
    for (const [source, target] of mappings) {
      upstreamRequests.length = 0;
      await request(app).get(source).expect(200);
      assert.equal(upstreamRequests.length, 1);
      assert.equal(upstreamRequests[0].path, target);
    }
  });

  it('freezes root and trailing-slash normalization', async () => {
    for (const [source, target] of [
      ['/api/kernel', '/api/kernel'],
      ['/api/kernel/', '/api/kernel'],
      ['/api/billing', '/billing'],
      ['/api/billing/', '/billing'],
      ['/billing', '/billing'],
      ['/billing/', '/billing'],
    ]) {
      upstreamRequests.length = 0;
      await request(app).get(source).expect(200);
      assert.equal(upstreamRequests[0].path, target);
    }
  });

  it('preserves ordered, repeated, and encoded query bytes', async () => {
    const query = 'tag=first&tag=second&encoded=a%2Fb%20c&empty=';
    await request(app).get(`/api/kernel/search?${query}`).expect(200);
    assert.equal(upstreamRequests[0].path, `/api/kernel/search?${query}`);
  });

  it('forwards broad methods while CORS answers OPTIONS locally', async () => {
    for (const method of ['get', 'post', 'put', 'patch', 'delete', 'head']) {
      upstreamRequests.length = 0;
      const exchange = request(app)[method]('/api/kernel/method');
      if (!['get', 'head'].includes(method)) exchange.type('application/octet-stream').send('x');
      await exchange.expect(200);
      assert.equal(upstreamRequests[0].method, method.toUpperCase());
    }
    upstreamRequests.length = 0;
    await request(app)
      .options('/api/kernel/method')
      .set('Origin', 'https://certificate.invalid')
      .set('Access-Control-Request-Method', 'POST')
      .expect(204);
    assert.equal(upstreamRequests.length, 0);
  });

  it('rejects sibling and unsupported selective namespaces without glob semantics', async () => {
    for (const path of [
      '/api/kernelish',
      '/api/billings',
      '/api/businesses/tenants',
      '/api/wilsy-ai/legal-services/extended',
      '/api/legal-acceptance/status/extended',
    ]) {
      upstreamRequests.length = 0;
      await request(app).get(path).expect(404);
      assert.equal(upstreamRequests.length, 0);
    }
  });
});

describe('raw request and response stream contract', () => {
  it('forwards raw JSON bytes without reconstruction', async () => {
    const body = Buffer.from('{\n  "b": 2,\n  "a": 1\n}\n');
    await rawRequest({
      method: 'POST',
      path: '/api/kernel/raw-json',
      headers: { 'content-type': 'application/json', 'content-length': String(body.length) },
      chunks: [body],
    }).completed;
    assert.deepEqual(upstreamRequests[0].body, body);
  });

  it('forwards chunked binary request bytes exactly', async () => {
    const chunks = [Buffer.from([0, 1, 127]), Buffer.from([128, 254, 255])];
    await rawRequest({
      method: 'PATCH',
      path: '/api/kernel/raw-binary',
      headers: { 'content-type': 'application/octet-stream' },
      chunks,
    }).completed;
    assert.deepEqual(upstreamRequests[0].body, Buffer.concat(chunks));
    assert.equal(upstreamRequests[0].headers['transfer-encoding'], 'chunked');
  });

  it('delivers a response chunk before the upstream response completes', async () => {
    resetStreamBarrier();
    const exchange = rawRequest({ path: '/api/kernel/stream' });
    assert.deepEqual(await exchange.firstChunk, Buffer.from([0, 1, 2, 3]));
    releaseStream();
    const response = await exchange.completed;
    assert.equal(response.status, 206);
    assert.deepEqual(response.body, Buffer.from([0, 1, 2, 3, 252, 253, 254, 255]));
    assert.equal(response.headers['cache-control'], 'no-store');
    assert.equal(response.headers['x-wilsy-upstream'], 'stream-certificate');
  });

  it('passes 5xx status, safe headers, and raw body without a success envelope', async () => {
    const response = await rawRequest({ path: '/api/kernel/failure' }).completed;
    assert.equal(response.status, 502);
    assert.equal(response.headers['content-type'], 'application/octet-stream');
    assert.equal(response.headers['cache-control'], 'no-cache');
    assert.equal(response.headers['x-wilsy-upstream'], 'failure-certificate');
    assert.deepEqual(response.body, Buffer.from('upstream-failure-byte-body'));
  });
});

describe('host and institutional evidence contract', () => {
  it('rewrites Host to the upstream authority', async () => {
    await request(app).get('/api/kernel/host').set('Host', 'public.invalid').expect(200);
    assert.equal(upstreamRequests[0].headers.host, `127.0.0.1:${upstreamPort}`);
  });

  it('preserves Authorization exactly and never fabricates it', async () => {
    await request(app).get('/api/kernel/auth').set('Authorization', 'Bearer exact').expect(200);
    assert.equal(upstreamRequests[0].headers.authorization, 'Bearer exact');
    upstreamRequests.length = 0;
    await request(app).get('/api/kernel/no-auth').expect(200);
    assert.equal(Object.hasOwn(upstreamRequests[0].headers, 'authorization'), false);
  });

  it('projects tenant aliases and never fabricates a default tenant', async () => {
    await request(app)
      .get('/api/kernel/tenant')
      .set('X-Wilsy-Tenant', 'tenant-evidence')
      .expect(200);
    assert.equal(upstreamRequests[0].headers['x-wilsy-tenant'], 'tenant-evidence');
    assert.equal(upstreamRequests[0].headers['x-tenant-id'], 'tenant-evidence');
    upstreamRequests.length = 0;
    await request(app).get('/api/kernel/no-tenant').expect(200);
    for (const name of ['x-tenant-id', 'x-tenant', 'x-wilsy-tenant', 'x-wilsy-tenant-id']) {
      assert.equal(Object.hasOwn(upstreamRequests[0].headers, name), false);
    }
  });

  it('projects idempotency aliases without invention', async () => {
    await request(app)
      .post('/api/billing/idem')
      .set('X-Wilsy-Idempotency-Key', 'idem-evidence')
      .send('x')
      .expect(200);
    for (const name of ['idempotency-key', 'x-idempotency-key', 'x-wilsy-idempotency-key']) {
      assert.equal(upstreamRequests[0].headers[name], 'idem-evidence');
    }
    upstreamRequests.length = 0;
    await request(app).get('/api/kernel/no-idem').expect(200);
    for (const name of ['idempotency-key', 'x-idempotency-key', 'x-wilsy-idempotency-key']) {
      assert.equal(Object.hasOwn(upstreamRequests[0].headers, name), false);
    }
  });

  it('preserves trace/request IDs and does not invent absent IDs', async () => {
    await request(app)
      .get('/api/kernel/ids')
      .set('X-Trace-ID', 'trace-evidence')
      .set('X-Request-ID', 'request-evidence')
      .expect(200);
    assert.equal(upstreamRequests[0].headers['x-trace-id'], 'trace-evidence');
    assert.equal(upstreamRequests[0].headers['x-request-id'], 'request-evidence');
    upstreamRequests.length = 0;
    await request(app).get('/api/kernel/no-ids').expect(200);
    assert.equal(Object.hasOwn(upstreamRequests[0].headers, 'x-trace-id'), false);
    assert.equal(Object.hasOwn(upstreamRequests[0].headers, 'x-request-id'), false);
  });
});

describe('preserved selective Legal transport certificate', () => {
  it('forwards C1C with exact path, raw body, and institutional headers', async () => {
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
    assert.equal(upstreamRequests[0].body.toString(), JSON.stringify(body));
    assert.equal(upstreamRequests[0].headers.authorization, 'Bearer test-token');
    assert.equal(upstreamRequests[0].headers['x-tenant-id'], 'tenant-r1a');
    assert.equal(upstreamRequests[0].headers['x-idempotency-key'], 'idem-r1a');
    assert.equal(upstreamRequests[0].headers['x-trace-id'], 'trace-r1a');
    assert.equal(upstreamRequests[0].headers['x-request-id'], 'request-r1a');
  });

  it('forwards C1E POST and exact advisory-id GET suffix', async () => {
    await request(app)
      .post('/api/wilsy-ai/legal-next-actions')
      .send({ orchestration_id: 'c1c-root-1' })
      .expect(200);
    await request(app).get('/api/wilsy-ai/legal-next-actions/advisory-123').expect(200);
    assert.equal(upstreamRequests[0].path, '/api/wilsy-ai/legal-next-actions');
    assert.equal(upstreamRequests[1].path, '/api/wilsy-ai/legal-next-actions/advisory-123');
  });

  it('passes Python non-2xx semantics through without false success', async () => {
    const response = await request(app)
      .get('/api/wilsy-ai/legal-next-actions/conflict-id')
      .expect(409);
    assert.deepEqual(response.body, { detail: 'C1E_SOURCE_SNAPSHOT_STALE' });
  });

  it('forwards legal status, document, and acceptance without interpreting authority', async () => {
    await request(app)
      .get('/api/legal-acceptance/status')
      .set('X-Tenant-ID', 'tenant-legal')
      .expect(200);
    await request(app).get('/api/legal-acceptance/documents/charter-v1').expect(200);
    const body = {
      document_id: 'charter-v1',
      document_version: '1.0.0',
      document_sha3_512: 'a'.repeat(128),
      acceptance_method: 'ACKNOWLEDGEMENT',
    };
    await request(app)
      .post('/api/legal-acceptance/accept')
      .set('Authorization', 'Bearer test-token')
      .set('Idempotency-Key', 'legal-idem-1')
      .send(body)
      .expect(200);
    assert.equal(upstreamRequests[0].path, '/api/legal-acceptance/status');
    assert.equal(upstreamRequests[1].path, '/api/legal-acceptance/documents/charter-v1');
    assert.equal(upstreamRequests[2].path, '/api/legal-acceptance/accept');
    assert.equal(upstreamRequests[2].headers.authorization, 'Bearer test-token');
    assert.equal(upstreamRequests[2].headers['x-idempotency-key'], 'legal-idem-1');
    assert.equal(upstreamRequests[2].body.toString(), JSON.stringify(body));
  });

  it('preserves legal 401, 403, and 409 response semantics and no-store', async () => {
    for (const status of [401, 403, 409]) {
      const response = await request(app)
        .get('/api/legal-acceptance/status')
        .set('Authorization', `Bearer status-${status}`)
        .expect(status);
      assert.equal(response.headers['cache-control'], 'no-store');
    }
  });

  it('leaves reasoning and legal-tools outside the selective boundary', async () => {
    const reasoning = await request(app)
      .post('/api/wilsy-ai/reasoning')
      .send({ prompt: 'x' })
      .expect(404);
    const tools = await request(app).get('/api/wilsy-ai/legal-tools').expect(404);
    assert.equal(reasoning.body.error, 'BFF_ROUTE_NOT_PROXIED');
    assert.equal(tools.body.error, 'BFF_ROUTE_NOT_PROXIED');
    assert.equal(upstreamRequests.length, 0);
  });
});

describe('timeout, failure, and capability boundaries', () => {
  it('freezes route-level timeout selection without sleeping', async () => {
    const source = await readFile(SERVER_SOURCE_URL, 'utf8');
    assert.match(
      source,
      /DEFAULT_PROXY_TIMEOUT_MS\s*=\s*Number\(process\.env\.KENNEL_PROXY_TIMEOUT_MS\s*\|\|\s*30000\)/
    );
    assert.match(
      source,
      /BILLING_PROXY_TIMEOUT_MS\s*=\s*Number\(process\.env\.KENNEL_BILLING_TIMEOUT_MS\s*\|\|\s*60000\)/
    );
    assert.match(
      source,
      /mountPrefix:\s*['"]\/api\/billing['"][\s\S]*?timeoutMs:\s*BILLING_PROXY_TIMEOUT_MS/
    );
    assert.match(
      source,
      /mountPrefix:\s*['"]\/billing['"][\s\S]*?timeoutMs:\s*BILLING_PROXY_TIMEOUT_MS/
    );
  });

  it('returns bounded 503 evidence without leaking the refused upstream endpoint', async () => {
    await close(upstream);
    try {
      const response = await request(app).get('/api/kernel/refused').expect(503);
      assert.equal(response.body.success, false);
      assert.equal(response.body.error, 'Kennel service unavailable');
      assert.equal(typeof response.body.timestamp, 'string');
      assert.doesNotMatch(
        String(response.body.message || ''),
        /(ECONNREFUSED|127\.0\.0\.1|localhost|:\d{2,5})/i,
        'connection errors must not expose internal endpoint or socket details'
      );
    } finally {
      upstreamPort = await listen(upstream, upstreamPort);
    }
  });

  it('freezes absence of WebSocket proxy authority', async () => {
    const source = await readFile(SERVER_SOURCE_URL, 'utf8');
    assert.doesNotMatch(source, /\bws\s*:\s*true\b/);
    assert.doesNotMatch(source, /\.on\(\s*['"]upgrade['"]/);
  });
});

// CONNECT_TIMEOUT_RUNTIME_CERTIFIED=NO
// POST_HEADER_FAILURE_CERTIFIED=NO
// CLIENT_ABORT_CERTIFIED=NO
// UPSTREAM_ABORT_CERTIFIED=NO
// TLS_FAILURE_CERTIFIED=NO
// QUANTITATIVE_BACKPRESSURE_CERTIFIED=NO
// WEBSOCKET_PROXY_AUTHORITY=ABSENT
// ARTIFACT: wilsyAiAdvisoryProxy.test.js
// VERSION: v2.0.0-P0-C4E1
// AUTHORITY BOUNDARY: deterministic transport certificate only
// TENANT POSTURE: supplied tenant evidence is forwarded; none is fabricated
// FAIL-CLOSED POSTURE: route, authority, failure, and migration boundaries are explicit
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
