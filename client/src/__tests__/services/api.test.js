/**
 * TITLE: WILSY OS Institutional HTTP Transport Regression Certificate
 * VERSION: v1.5.0-NATIVE-FORMDATA-FILE-PROJECTION-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Existing HTTP contracts and critical post-MFA bootstrap requests
 *          cannot be misclassified as degraded dashboard source reads.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/api.test.js
 * COLLABORATION / OWNERSHIP: api.js transport, server-owned EOS session truth.
 * CERTIFICATION / UPDATE DATE: 2026-11-17
 * CHANGELOG: v1.5.0-NATIVE-FORMDATA-FILE-PROJECTION-CERT asserts multipart file bytes, MIME, size and name instead of File object identity (FormData may clone the File upon append), preserving the wire-level safety contract.
 * CHANGELOG: v1.4.0-NATIVE-FORMDATA-BOUNDARY-TRANSPORT-CERT verifies that native FormData clears the global application/json default using AxiosHeaders or ordinary header objects while preserving a single file part, bearer, tenant, idempotency and forensic headers. JSON-only commands retain canonical JSON handling.
 * CHANGELOG: v1.3.0-CRM-STATUS-CANCEL-JSON-CONTRACT verifies
 *            no extra timestamp fields in CRM status/cancel POSTs while
 *            cryptographic forensic headers remain intact.
 * CHANGELOG: v1.5.0-NATIVE-FORMDATA-FILE-PROJECTION-CERT verifies six exact
 *            company-document mutation paths retain caller fields and forensic headers.
 * CHANGELOG: v1.1.0 verifies post-MFA session bootstrap, SYSTEM bootstrap,
 *            covenant status, normal dashboard backoff and 403 separation.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic bearer only; no live secrets or users.
 * TENANT BOUNDARY: Test cannot establish or elevate tenant authority.
 * AUTHORITY BOUNDARY: Only EOS accepts or rejects session credentials.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * WILSY OS — SOVEREIGN API UNIT TESTS (HOISTED FINAL)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/api.test.js
 * Version:        v1.0.8-OTP-FIX
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Unit tests for api.js using vi.hoisted to resolve mock order.
 * Classification: Production Test Artifact — Institutional Contract
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) – Mandated test coverage.
 *   - AI Engineering – Hoisted mocks.
 *
 * Change Log:
 *   2026-08-07 v1.0.8-OTP-FIX — Used vi.hoisted for mock definitions.
 *
 * Certification Seal: PRODUCTION_READY_v1.0.8-OTP-FIX
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

// ──────────────────────────────────────────────────────────────────────────────
// HOISTED MOCKS (must be before vi.mock)
// ──────────────────────────────────────────────────────────────────────────────

const {
  mockAxiosInstance,
  localStorageMock,
  requestInterceptorCapture,
  responseInterceptorCapture,
} = vi.hoisted(() => {
  const requestInterceptorCapture = {
    fulfilled: null,
    rejected: null,
  };
  const responseInterceptorCapture = { fulfilled: null, rejected: null };

  const mockAxiosInstance = {
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: {
        use: vi.fn((fulfilled, rejected) => {
          requestInterceptorCapture.fulfilled = fulfilled;
          requestInterceptorCapture.rejected = rejected;
        }),
      },
      response: { use: vi.fn((fulfilled, rejected) => {
        responseInterceptorCapture.fulfilled = fulfilled;
        responseInterceptorCapture.rejected = rejected;
      }) },
    },
  };

  const localStorageMock = (() => {
    let store = {};
    return {
      getItem: vi.fn((key) => store[key] || null),
      setItem: vi.fn((key, val) => { store[key] = val; }),
      removeItem: vi.fn((key) => { delete store[key]; }),
      clear: vi.fn(() => { store = {}; }),
    };
  })();

  return {
    mockAxiosInstance,
    localStorageMock,
    requestInterceptorCapture,
    responseInterceptorCapture,
  };
});

// ──────────────────────────────────────────────────────────────────────────────
// MOCKS
// ──────────────────────────────────────────────────────────────────────────────

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance),
  },
}));

vi.mock('../../utils/telemetryHelper.js', () => ({
  generateTraceAnchor: vi.fn(() => 'TRC-TEST'),
  broadcastTelemetry: vi.fn(),
}));

vi.mock('../../utils/bridgeLog.js', () => ({
  bridgeLog: vi.fn(),
}));

vi.mock('js-sha3', () => ({
  sha3_512: vi.fn(() => 'mocked-sha3-512-hash'),
}));

// ──────────────────────────────────────────────────────────────────────────────
// SETUP GLOBALS
// ──────────────────────────────────────────────────────────────────────────────

Object.defineProperty(window, 'localStorage', { value: localStorageMock, writable: true });

// ──────────────────────────────────────────────────────────────────────────────
// IMPORT API AFTER MOCKS ARE SETUP
// ──────────────────────────────────────────────────────────────────────────────

import api, {
  getStatements,
  generateStatement,
  sealStatement,
  exportStatement,
  exportStatementPdf,
  verifyStatementSeal,
  setActiveTenantTransportId,
} from '../../services/api.js';

// ──────────────────────────────────────────────────────────────────────────────
// TESTS
// ──────────────────────────────────────────────────────────────────────────────

describe('api.js – Sovereign HTTP Client', () => {
  let consoleErrorSpy;

  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.clear();
    setActiveTenantTransportId(null);
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  // ──────────────────────────────────────────────────────────────────────────
  // Strict legal-acceptance transport contract
  // ──────────────────────────────────────────────────────────────────────────

  describe('Legal acceptance transport contract', () => {
    const tenantId = 'WILSYTENANT-4CD2FZ4O';

    const bindAuthenticatedTransport = () => {
      localStorageMock.setItem('wilsy_auth_token', 'bounded-test-token');
      setActiveTenantTransportId(tenantId);
    };

    it('preserves the exact five-field legal-acceptance body while retaining forensic headers', async () => {
      expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));

      bindAuthenticatedTransport();

      const originalBody = {
        document_id: 'terms-v1',
        document_version: '1.1.0-APPROVED',
        document_sha3_512: 'a'.repeat(128),
        acceptance_method: 'ACCEPTANCE',
        locale: 'en-ZA',
      };

      const config = {
        url: '/legal-acceptance/accept',
        method: 'post',
        data: { ...originalBody },
        headers: {
          'Idempotency-Key': 'legal-acceptance-test-1',
        },
      };

      const sealed = await requestInterceptorCapture.fulfilled(config);

      expect(sealed.data).toEqual(originalBody);
      expect(Object.keys(sealed.data).sort()).toEqual(
        Object.keys(originalBody).sort(),
      );
      expect(sealed.data).not.toHaveProperty('timestamp');

      expect(sealed.headers['Idempotency-Key']).toBe(
        'legal-acceptance-test-1',
      );
      expect(sealed.headers.Authorization).toBe(
        'Bearer bounded-test-token',
      );
      expect(sealed.headers['X-Tenant-ID']).toBe(tenantId);

      expect(sealed.headers['x-trace-id']).toEqual(expect.any(String));
      expect(sealed.headers['x-forensic-timestamp']).toEqual(
        expect.any(String),
      );
      expect(sealed.headers['x-cryptographic-nonce']).toEqual(
        expect.any(String),
      );
      expect(sealed.headers['x-request-seal']).toEqual(
        expect.any(String),
      );
    });

    it('preserves both classifications and all three strict company-document commands', async () => {
      bindAuthenticatedTransport();
      for (const classification of ['MISSION', 'STRATEGY']) {
        for (const action of ['drafts', 'submit', 'publish']) {
          const payload = { expected_revision: 1, synthetic_field: 'transport preservation only' };
          const sealed = await requestInterceptorCapture.fulfilled({
            url: '/company-operating-documents/' + classification + '/' + action,
            method: 'post', data: { ...payload }, headers: { 'Idempotency-Key': 'synthetic-key' },
          });
          expect(sealed.data).toEqual(payload);
          expect(sealed.data).not.toHaveProperty('timestamp');
          expect(sealed.headers['x-forensic-timestamp']).toEqual(expect.any(String));
          expect(sealed.headers['x-request-seal']).toEqual(expect.any(String));
          expect(sealed.headers['Idempotency-Key']).toBe('synthetic-key');
        }
      }
    });

    it('preserves exact EOS responder decision bodies while retaining forensic headers', async () => {
      expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));
      bindAuthenticatedTransport();

      for (const action of ['accept', 'decline']) {
        const originalBody = { expected_revision: 1 };
        const sealed = await requestInterceptorCapture.fulfilled({
          url: '/system-services/security-incident-assignments/assignment-1/' + action,
          method: 'post',
          data: { ...originalBody },
          headers: { 'Idempotency-Key': 'system-responder-test-1' },
        });

        expect(sealed.data).toEqual(originalBody);
        expect(sealed.data).not.toHaveProperty('timestamp');
        expect(sealed.headers['Idempotency-Key']).toBe('system-responder-test-1');
        expect(sealed.headers['x-forensic-timestamp']).toEqual(expect.any(String));
        expect(sealed.headers['x-request-seal']).toEqual(expect.any(String));
      }
    });

    it('preserves exact CRM, Operations and Intelligence work command bodies', async () => {
      expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));
      bindAuthenticatedTransport();

      const commands = [
        {
          url: '/crm/owner-workspace/work-items',
          data: {
            title: 'CRM follow-up', description: '', kind: 'TASK', priority: 'NORMAL',
            due_at: null, source_type: null, source_id: null,
          },
        },
        {
          url: '/crm/owner-workspace/work-items/work-1/complete',
          data: { completion_note: 'Completed by the assigned owner.' },
        },
        {
          url: '/crm/owner-workspace/work-items/work-1/status',
          data: { status: 'DRAFT', expected_updated_at: '2026-11-17T10:13:00Z' },
        },
        {
          url: '/crm/owner-workspace/work-items/work-1/cancel',
          data: { reason: 'Withdrawn by owner', expected_updated_at: '2026-11-17T10:13:00Z' },
        },
        ...['operations', 'intelligence'].flatMap(module => [
          {
            url: `/tenant-modules/${module}/workspace/work-items`,
            data: { title: `${module} task`, description: '', kind: 'TASK', priority: 'NORMAL', due_at: null },
          },
          {
            url: `/tenant-modules/${module}/workspace/work-items/work-1/complete`,
            data: { completion_note: 'Completed in the module workspace.' },
          },
        ]),
      ];

      for (const command of commands) {
        const originalBody = { ...command.data };
        const sealed = await requestInterceptorCapture.fulfilled({
          url: command.url,
          method: 'post',
          data: { ...command.data },
          headers: {},
        });
        expect(sealed.data).toEqual(originalBody);
        expect(sealed.data).not.toHaveProperty('timestamp');
        expect(sealed.headers['x-forensic-timestamp']).toEqual(expect.any(String));
        expect(sealed.headers['x-cryptographic-nonce']).toEqual(expect.any(String));
        expect(sealed.headers['x-request-seal']).toEqual(expect.any(String));
      }
    });

    it('does not promote discovery storage into authenticated tenant transport context', async () => {
      expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));

      localStorageMock.setItem('discoveredTenant', JSON.stringify({
        tenantId: 'TENANT-ACME-01',
        alias: 'acme-law',
      }));

      const sealed = await requestInterceptorCapture.fulfilled({
        url: '/legal-operations/commercial-context',
        method: 'get',
        headers: {},
      });

      expect(sealed.headers['X-Tenant-ID']).toBeUndefined();
    });

    it('does not invent a tenant header before successful discovery', async () => {
      expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));

      localStorageMock.setItem('wilsy_active_tenant', JSON.stringify({
        tenantId: 'STALE-TENANT',
      }));
      localStorageMock.setItem('discoveredTenant', 'GLOBAL_ROOT');

      const sealed = await requestInterceptorCapture.fulfilled({
        url: '/legal-operations/commercial-context',
        method: 'get',
        headers: { 'X-Tenant-ID': 'STALE-DEFAULT' },
      });

      expect(sealed.headers['X-Tenant-ID']).toBeUndefined();
      expect(sealed.headers['x-tenant-id']).toBeUndefined();
    });

    it('preserves an explicitly supplied MFA candidate bearer over stale browser storage', async () => {
      expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));

      localStorageMock.setItem('wilsy_auth_token', 'stale-stored-token');
      localStorageMock.setItem(
        'wilsy_active_tenant',
        JSON.stringify({ tenantId: 'TENANT-BOOTSTRAP-TEST' }),
      );

      const sealed = await requestInterceptorCapture.fulfilled({
        url: '/auth/workspace-bootstrap',
        method: 'get',
        headers: {
          Authorization: 'Bearer freshly-verified-candidate-token',
        },
      });

      expect(sealed.headers.Authorization).toBe(
        'Bearer freshly-verified-candidate-token',
      );
      expect(sealed.headers['X-Tenant-ID']).toBeUndefined();
    });

    it('rejects empty or malformed explicit bearer headers and uses the valid stored session', async () => {
      expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));
      localStorageMock.setItem('wilsy_auth_token', 'active-session-token');

      const emptyBearer = await requestInterceptorCapture.fulfilled({
        url: '/legal-operations/commercial-context',
        method: 'get',
        headers: { Authorization: 'Bearer ' },
      });
      expect(emptyBearer.headers.Authorization).toBe('Bearer active-session-token');

      const malformedScheme = await requestInterceptorCapture.fulfilled({
        url: '/legal-operations/commercial-context',
        method: 'get',
        headers: { Authorization: 'Basic not-a-bearer' },
      });
      expect(malformedScheme.headers.Authorization).toBe('Bearer active-session-token');
    });

    it('never forwards undefined or null stored tokens as bearer credentials', async () => {
      expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));

      for (const invalidToken of ['undefined', 'null', '   ']) {
        localStorageMock.clear();
        localStorageMock.setItem('wilsy_auth_token', invalidToken);
        const sealed = await requestInterceptorCapture.fulfilled({
          url: '/legal-operations/commercial-context',
          method: 'get',
          headers: { Authorization: 'Bearer ' },
        });
        expect(sealed.headers.Authorization).toBeUndefined();
      }
    });

    it('allows the browser to generate the multipart boundary and preserves the exact file part', async () => {
      bindAuthenticatedTransport();
      const file = new File(['%PDF-1.4\\nsynthetic'], 'design.pdf', { type: 'application/pdf' });
      const form = new FormData();
      form.append('file', file, file.name);
      const headers = {
        'Content-Type': 'application/json',
        'Idempotency-Key': 'existing-upload-command',
        'X-Tenant-ID': tenantId,
      };
      const sealed = await requestInterceptorCapture.fulfilled({
        url: '/projects/prj-' + 'a'.repeat(48) + '/my-project/tasks/ptk-'
          + 'b'.repeat(48) + '/attachments',
        method: 'post', data: form, headers,
      });
      expect(sealed.data).toBe(form);
      expect(Array.from(sealed.data.keys())).toEqual(['file']);
      expect(sealed.data.get('file').name).toBe(file.name);
      expect(sealed.data.get('file').type).toBe(file.type);
      expect(sealed.data.get('file').size).toBe(file.size);
      expect(await sealed.data.get('file').text()).toBe(await file.text());
      expect(sealed.headers).not.toHaveProperty('Content-Type');
      expect(sealed.headers).not.toHaveProperty('content-type');
      expect(sealed.headers['Idempotency-Key']).toBe('existing-upload-command');
      expect(sealed.headers['X-Tenant-ID']).toBe(tenantId);
      expect(sealed.headers.Authorization).toEqual(expect.stringMatching(/^Bearer /));
      expect(sealed.headers['x-request-seal']).toBeTruthy();
      expect(sealed.headers['x-forensic-timestamp']).toBeTruthy();
      expect(sealed.data.get('timestamp')).toBeNull();
    });

    it('clears an AxiosHeaders-style JSON default before native multipart serialization', async () => {
      bindAuthenticatedTransport();
      const form = new FormData();
      form.append('file', new File(['%PDF-1.4'], 'report.pdf', { type: 'application/pdf' }));
      const headers = {
        currentType: 'application/json',
        setContentType: vi.fn(function (value) { this.currentType = value; }),
        getContentType: vi.fn(function () { return this.currentType; }),
      };
      const sealed = await requestInterceptorCapture.fulfilled({
        url: '/projects/prj-' + 'a'.repeat(48) + '/my-project/tasks/ptk-'
          + 'b'.repeat(48) + '/attachments',
        method: 'post', data: form, headers,
      });
      expect(headers.setContentType).toHaveBeenCalledWith(undefined);
      expect(headers.getContentType()).toBeUndefined();
      expect(sealed.data).toBe(form);
      expect(sealed.data.get('file').name).toBe('report.pdf');
    });

    it('preserves historical timestamp body injection for unrelated mutation routes', async () => {
      expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));

      bindAuthenticatedTransport();

      const sealed = await requestInterceptorCapture.fulfilled({
        url: '/statements/generate',
        method: 'post',
        data: {
          clientId: 'client-1',
          period: '2026-09',
        },
        headers: {},
      });

      expect(sealed.data.clientId).toBe('client-1');
      expect(sealed.data.period).toBe('2026-09');
      expect(sealed.data.timestamp).toEqual(expect.any(String));

      expect(sealed.headers['x-forensic-timestamp']).toEqual(
        expect.any(String),
      );
      expect(sealed.headers['x-request-seal']).toEqual(
        expect.any(String),
      );
    });
  });

  // ──────────────────────────────────────────────────────────────────────────
  // Statement API functions
  // ──────────────────────────────────────────────────────────────────────────

  describe('Statement API', () => {
    it('getStatements calls api.get with params', async () => {
      mockAxiosInstance.get.mockResolvedValueOnce({ data: [] });
      await getStatements({ tenantId: 'test' });
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/statements', { params: { tenantId: 'test' } });
    });

    it('generateStatement calls api.post', async () => {
      mockAxiosInstance.post.mockResolvedValueOnce({ data: {} });
      await generateStatement({ clientId: 'c1', period: '2026-01' });
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/statements/generate', { clientId: 'c1', period: '2026-01' });
    });

    it('sealStatement calls api.post with statementId', async () => {
      mockAxiosInstance.post.mockResolvedValueOnce({ data: {} });
      await sealStatement('stmt1', { jurisdiction: 'ZA' });
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/statements/stmt1/seal', { jurisdiction: 'ZA' });
    });

    it('exportStatement calls api.get with format', async () => {
      mockAxiosInstance.get.mockResolvedValueOnce({ data: {} });
      await exportStatement('stmt1', 'xml');
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/statements/stmt1/export', { params: { format: 'xml' } });
    });

    it('exportStatementPdf calls api.get with responseType blob', async () => {
      mockAxiosInstance.get.mockResolvedValueOnce({ data: new Blob() });
      await exportStatementPdf('stmt1');
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/statements/stmt1/export-pdf', { responseType: 'blob' });
    });

    it('verifyStatementSeal calls api.post', async () => {
      mockAxiosInstance.post.mockResolvedValueOnce({ data: { valid: true } });
      await verifyStatementSeal('stmt1');
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/statements/stmt1/verify');
    });
  });

  describe('identity continuity excludes local 503 backoff', () => {
    const seedServer503 = async (path) => {
      const failed = {
        config: { url: path, method: 'get', headers: {} },
        response: { status: 503, data: { detail: 'SERVICE_UNAVAILABLE' } },
        message: 'Real EOS server unavailable',
      };
      await expect(responseInterceptorCapture.rejected(failed)).rejects.toBe(failed);
    };

    it.each([
      '/auth/workspace-bootstrap',
      '/auth/global/session',
      '/system-services/workspace-bootstrap',
      '/legal-acceptance/status',
      '/api/auth/workspace-bootstrap',
    ])('always sends %s for fresh EOS verification even after 503', async (path) => {
      expect(responseInterceptorCapture.rejected).toEqual(expect.any(Function));
      await seedServer503(path);

      const config = {
        url: path, method: 'get',
        headers: { Authorization: 'Bearer candidate-mfa-token' },
      };
      const result = await requestInterceptorCapture.fulfilled(config);
      expect(result).toMatchObject({
        url: path.replace(/^\/?api\//, '/'),
        headers: { Authorization: 'Bearer candidate-mfa-token' },
      });
    });

    it('retains protective backoff for degraded, ordinary dashboard GETs', async () => {
      const path = '/metrics/test-auth-backoff-20261109';
      await seedServer503(path);
      await expect(requestInterceptorCapture.fulfilled({
        url: path, method: 'get', headers: {},
      })).rejects.toMatchObject({
        isSourceBackoff: true,
        response: { status: 503, data: { code: 'SOURCE_BACKOFF_ACTIVE' } },
      });
    });

    it('respects deliberate forceNetworkRetry for diagnostic dashboard reads', async () => {
      const path = '/metrics/test-auth-force-20261109';
      await seedServer503(path);
      const result = await requestInterceptorCapture.fulfilled({
        url: path, method: 'get', headers: {}, forceNetworkRetry: true,
      });
      expect(result.url).toBe(path);
    });

    it('never treats a 403 permission denial as source degradation', async () => {
      const path = '/billing/dunning/state';
      const denied = {
        config: { url: path, method: 'get', headers: {} },
        response: { status: 403 }, message: 'Forbidden',
      };
      await expect(responseInterceptorCapture.rejected(denied)).rejects.toBe(denied);
      const result = await requestInterceptorCapture.fulfilled({
        url: path, method: 'get', headers: {},
      });
      expect(result.url).toBe(path);
    });
  });
});

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — API UNIT TESTS v1.0.8-OTP-FIX
 * ═══════════════════════════════════════════════════════════════════════════════
 * Coverage: Statement API functions.
 * The sovereign bridge is now verified by CI.
 * Phase 5 next: integration tests and performance benchmarks.
 * ═══════════════════════════════════════════════════════════════════════════════
 */

/*
 * ARTIFACT: client/src/__tests__/services/api.test.js
 * VERSION: v1.5.0-NATIVE-FORMDATA-FILE-PROJECTION-CERT
 * AUTHORITY BOUNDARY: Tests only, never creates browser authorization.
 * TENANT POSTURE: Synthetic credentials and endpoint identities.
 * FAIL-CLOSED POSTURE: Actual EOS errors remain errors; no invented success.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
