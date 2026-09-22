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
} = vi.hoisted(() => {
  const requestInterceptorCapture = {
    fulfilled: null,
    rejected: null,
  };

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
      response: { use: vi.fn() },
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
} from '../../services/api.js';

// ──────────────────────────────────────────────────────────────────────────────
// TESTS
// ──────────────────────────────────────────────────────────────────────────────

describe('api.js – Sovereign HTTP Client', () => {
  let consoleErrorSpy;

  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.clear();
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

      // Current authenticated projection is authoritative where supported.
      localStorageMock.setItem(
        'wilsy_active_tenant',
        JSON.stringify({
          tenantId,
          alias: 'wilsy',
        }),
      );

      // Preserve compatibility with discovery-backed installations.
      localStorageMock.setItem(
        'discoveredTenant',
        JSON.stringify({
          tenantId,
          alias: 'wilsy',
        }),
      );
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
