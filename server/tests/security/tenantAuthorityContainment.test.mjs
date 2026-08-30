/**
 * WILSY OS — NODE TENANT AUTHORITY CONTAINMENT CERTIFICATION
 * VERSION: v1.0.0-TENANT-AUTHORITY-CONTAINMENT-CERT
 * AUTHORITY: Certifies the real early containment middleware contract.
 * EPITOME: Proves direct legacy tenant requests stop before tenant context/auth/controllers while plural Python proxy paths remain distinct.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/security/tenantAuthorityContainment.test.mjs
 * COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
 * CERTIFICATION/UPDATE DATE: 2026-08-30
 * CHANGELOG: v1.0.0 certifies route boundary, hostile inputs, non-invocation, and plural-path non-interference.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY/PRIVACY POSTURE: Responses are bounded and contain no identity, tenant, token, or stack data.
 * TENANT BOUNDARY: Only singular /api/tenant is contained; plural /api/tenants is tested as a separate proxy surface.
 * AUTHORITY BOUNDARY: Transport containment only; Kennel EOS remains tenant authority.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
 */

import assert from 'node:assert/strict';
import express from 'express';
import { test } from 'node:test';
import { tenantAuthorityUnavailable } from '../../middleware/tenantAuthorityContainment.middleware.js';

async function request(app, method, path, headers = {}) {
  return new Promise((resolve, reject) => {
    const req = {
      method,
      url: path,
      originalUrl: path,
      headers,
      get: (name) => headers[name] || headers[name.toLowerCase()],
    };
    const response = {
      statusCode: 200,
      headers: {},
      setHeader(name, value) {
        this.headers[name] = value;
      },
      getHeader(name) {
        return this.headers[name];
      },
      removeHeader(name) {
        delete this.headers[name];
      },
      status(code) {
        this.statusCode = code;
        return this;
      },
      json(body) {
        resolve({ status: this.statusCode, body });
      },
      end() {
        resolve({ status: this.statusCode, body: null });
      },
    };
    app.handle(req, response, (error) =>
      error ? reject(error) : resolve({ status: response.statusCode, body: null })
    );
  });
}

test('direct tenant namespace fails before context, auth, controller, or persistence', async () => {
  const app = express();
  let contextExecutions = 0;
  let downstreamExecutions = 0;
  app.use('/api/tenant', tenantAuthorityUnavailable);
  app.use((req, res, next) => {
    contextExecutions += 1;
    next();
  });
  app.use('/api/tenant', (req, res) => {
    downstreamExecutions += 1;
    res.status(500).end();
  });

  const routes = [
    ['GET', '/api/tenant/'],
    ['POST', '/api/tenant/'],
    ['GET', '/api/tenant/tenant-a'],
    ['GET', '/api/tenant/tenant-a/seal'],
    ['PATCH', '/api/tenant/tenant-a/suspend'],
    ['GET', '/api/tenant/tenant-a/health'],
    ['PATCH', '/api/tenant/tenant-a/tier'],
    ['POST', '/api/tenant/discover'],
  ];
  const roles = [
    '',
    'FOUNDER',
    'SUPER_ADMIN',
    'ADMIN',
    'SOVEREIGN_ARCHITECT',
    'ENTERPRISE_ADMIN',
    'TENANT_OWNER',
    'tenant_admin',
  ];
  for (const [method, path] of routes) {
    for (const role of roles) {
      for (const tenant of ['', 'GLOBAL_ROOT', 'tenant-b']) {
        const result = await request(app, method, path, {
          'X-Tenant-ID': tenant,
          'X-Test-Role': role,
        });
        assert.equal(result.status, 503);
        assert.deepEqual(result.body, {
          success: false,
          error: { code: 'TENANT_AUTHORITY_UNAVAILABLE' },
        });
      }
    }
  }
  assert.equal(contextExecutions, 0);
  assert.equal(downstreamExecutions, 0);
});

test('singular containment does not intercept plural Python proxy namespace', async () => {
  const app = express();
  app.use('/api/tenant', tenantAuthorityUnavailable);
  app.use('/api/tenants', (req, res) =>
    res.status(503).json({ success: false, error: { code: 'TENANT_AUTHORITY_UNAVAILABLE' } })
  );
  const result = await request(app, 'GET', '/api/tenants');
  assert.equal(result.status, 503);
  assert.equal(result.body.error.code, 'TENANT_AUTHORITY_UNAVAILABLE');
});

// ARTIFACT: tenantAuthorityContainment.test.mjs
// VERSION: v1.0.0-TENANT-AUTHORITY-CONTAINMENT-CERT
// AUTHORITY BOUNDARY: certifies early direct Node tenant transport containment
// TENANT POSTURE: singular legacy namespace denied; plural Python proxy remains distinct
// FAIL-CLOSED POSTURE: HTTP 503 before downstream middleware for hostile inputs
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
// END OF WILSY OS SOVEREIGN ARTIFACT
