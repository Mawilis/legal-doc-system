/**
 * ============================================================================
 * WILSY OS — PASSWORD RESET API CERTIFICATE
 * ============================================================================
 * TITLE: Client password-reset transport contract certificate
 * VERSION: v1.0.0-R10D7-CLIENT-PASSWORD-RESET-API-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies the real resetPassword client method at the Axios seam
 * without contacting a network, changing browser authority, or duplicating
 * server-side recovery semantics.
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/passwordResetApi.test.js
 * COLLABORATION / OWNERSHIP: R10D7 client certification; production transport
 * remains owned by client/src/services/api.js and reset authority by Python EOS.
 * CERTIFICATION DATE: 2026-09-22
 * CHANGELOG:
 *   2026-09-22 v1.0.0-R10D7-CLIENT-PASSWORD-RESET-API-CERT — Certified exact
 *   unauthenticated reset transport, body preservation, 204 semantics, and
 *   fail-closed error behavior through the live client method.
 * COMPLIANCE: POPIA §19, GDPR §32, SOC2 §CC7.2; certificate-only scope.
 * SECURITY / PRIVACY POSTURE: Synthetic values only; no request is sent and no
 * secret is persisted, logged, refreshed, or returned by this certificate.
 * TENANT BOUNDARY: The caller's tenantId is forwarded as tenant_id only; the
 * client does not resolve, grant, or persist tenant authority.
 * AUTHORITY BOUNDARY: Transport only. Python EOS owns recovery, policy,
 * hashing, credential revision, session/refresh revocation, and responses.
 * FINANCIAL AUTHORITY BOUNDARY: No financial or Kennel EOS authority.
 * ============================================================================
 */

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import axios from 'axios';
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';

const {
  mockAxiosInstance,
  mockAxiosGet,
  mockGenerateTraceAnchor,
  mockBroadcastTelemetry,
  mockBridgeLog,
  localStorageMock,
  sessionStorageMock,
  requestInterceptorCapture,
  responseInterceptorCapture,
} = vi.hoisted(() => {
  const requestInterceptorCapture = { fulfilled: null, rejected: null };
  const responseInterceptorCapture = { fulfilled: null, rejected: null };

  const createStorage = () => {
    let values = {};
    return {
      getItem: vi.fn((key) => values[key] ?? null),
      setItem: vi.fn((key, value) => {
        values[key] = String(value);
      }),
      removeItem: vi.fn((key) => {
        delete values[key];
      }),
      clear: vi.fn(() => {
        values = {};
      }),
    };
  };

  const mockAxiosInstance = {
    defaults: { baseURL: '/api' },
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: {
        use: vi.fn((fulfilled, rejected) => {
          requestInterceptorCapture.fulfilled = fulfilled;
          requestInterceptorCapture.rejected = rejected;
        }),
      },
      response: {
        use: vi.fn((fulfilled, rejected) => {
          responseInterceptorCapture.fulfilled = fulfilled;
          responseInterceptorCapture.rejected = rejected;
        }),
      },
    },
  };

  return {
    mockAxiosInstance,
    mockAxiosGet: vi.fn().mockResolvedValue({ data: {}, headers: {} }),
    mockGenerateTraceAnchor: vi.fn(() => 'TRC-R10D7'),
    mockBroadcastTelemetry: vi.fn(),
    mockBridgeLog: vi.fn(),
    localStorageMock: createStorage(),
    sessionStorageMock: createStorage(),
    requestInterceptorCapture,
    responseInterceptorCapture,
  };
});

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance),
    get: mockAxiosGet,
  },
}));

vi.mock('../../utils/telemetryHelper.js', () => ({
  generateTraceAnchor: mockGenerateTraceAnchor,
  broadcastTelemetry: mockBroadcastTelemetry,
}));

vi.mock('../../utils/bridgeLog.js', () => ({
  bridgeLog: mockBridgeLog,
}));

vi.mock('js-sha3', () => ({
  sha3_512: vi.fn(() => 'synthetic-sha3-512'),
}));

Object.defineProperty(window, 'localStorage', {
  configurable: true,
  value: localStorageMock,
  writable: true,
});
Object.defineProperty(window, 'sessionStorage', {
  configurable: true,
  value: sessionStorageMock,
  writable: true,
});

import api, { resetPassword } from '../../services/api.js';

const RESET_INPUT = Object.freeze({
  tenantId: 'tenant-r10d7-synthetic',
  recoveryToken: 'recovery-token-r10d7-synthetic',
  newPassword: 'synthetic reset password with spaces 123',
});

const resetTransport = () => ({
  tenant_id: RESET_INPUT.tenantId,
  recovery_token: RESET_INPUT.recoveryToken,
  new_password: RESET_INPUT.newPassword,
});

const readApiSource = () => readFileSync(
  resolve(process.cwd(), 'src/services/api.js'),
  'utf8',
);

describe('R10D7 client password-reset API certificate', () => {
  let consoleLogSpy;
  let consoleWarnSpy;
  let consoleErrorSpy;

  beforeEach(() => {
    vi.clearAllMocks();
    mockAxiosGet.mockResolvedValue({ data: {}, headers: {} });
    localStorageMock.clear();
    sessionStorageMock.clear();
    mockAxiosInstance.defaults.baseURL = '/api';
    consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleLogSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  it('uses the live resetPassword method with the exact POST path, options, and three-field body', async () => {
    const response = { status: 204, data: undefined, headers: {} };
    mockAxiosInstance.post.mockResolvedValueOnce(response);

    const result = await resetPassword(RESET_INPUT);

    expect(result).toBe(response);
    expect(mockAxiosInstance.post).toHaveBeenCalledTimes(1);
    expect(mockAxiosInstance.get).not.toHaveBeenCalled();
    expect(mockAxiosInstance.post).toHaveBeenCalledWith(
      '/auth/reset-password',
      resetTransport(),
      { skipAuth: true },
    );
    const [path, body, options] = mockAxiosInstance.post.mock.calls[0];
    expect(path).toBe('/auth/reset-password');
    expect(Object.keys(body).sort()).toEqual([
      'new_password',
      'recovery_token',
      'tenant_id',
    ]);
    expect(body).toEqual(resetTransport());
    expect(options).toEqual({ skipAuth: true });
    expect(api.defaults.baseURL).toBe('/api');
    expect(RESET_INPUT).toEqual({
      tenantId: 'tenant-r10d7-synthetic',
      recoveryToken: 'recovery-token-r10d7-synthetic',
      newPassword: 'synthetic reset password with spaces 123',
    });
  });

  it('proves the request interceptor preserves the payload and resolves /api plus the reset endpoint without a bearer or seal mutation', async () => {
    expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));
    localStorageMock.setItem('wilsy_auth_token', 'synthetic-access-token');
    localStorageMock.setItem('wilsy_refresh_token', 'synthetic-refresh-token');
    localStorageMock.setItem('wilsy_active_tenant', JSON.stringify({
      tenantId: RESET_INPUT.tenantId,
      alias: 'synthetic-tenant',
    }));

    const body = resetTransport();
    const sealed = await requestInterceptorCapture.fulfilled({
      url: '/auth/reset-password',
      method: 'post',
      data: body,
      skipAuth: true,
      headers: {},
    });

    expect(sealed.url).toBe('/auth/reset-password');
    expect(sealed.skipAuth).toBe(true);
    expect(sealed.data).toEqual(body);
    expect(Object.keys(sealed.data).sort()).toEqual(Object.keys(body).sort());
    expect(sealed.data).not.toHaveProperty('timestamp');
    expect(sealed.headers.Authorization).toBeUndefined();
    expect(sealed.headers['X-Tenant-ID']).toBe(RESET_INPUT.tenantId);
    expect(sealed.headers['x-request-seal']).toBeUndefined();
    expect(sealed.headers['x-forensic-timestamp']).toBeUndefined();
    expect(sealed.headers['x-cryptographic-nonce']).toBeUndefined();
    expect(localStorageMock.getItem('wilsy_auth_token')).toBe('synthetic-access-token');
    expect(localStorageMock.getItem('wilsy_refresh_token')).toBe('synthetic-refresh-token');
    expect(mockBridgeLog).not.toHaveBeenCalled();
    expect(mockGenerateTraceAnchor).not.toHaveBeenCalled();
    expect(mockBroadcastTelemetry).not.toHaveBeenCalled();
  });

  it('accepts a bodyless 204 response without inventing response data or client authority', async () => {
    mockAxiosInstance.post.mockResolvedValueOnce({
      status: 204,
      data: undefined,
      headers: {},
    });

    const result = await resetPassword(RESET_INPUT);
    const intercepted = await responseInterceptorCapture.fulfilled(result);

    expect(result.status).toBe(204);
    expect(result.data).toBeUndefined();
    expect(intercepted).toBe(result);
    expect(localStorageMock.setItem).not.toHaveBeenCalled();
    expect(localStorageMock.removeItem).not.toHaveBeenCalled();
    expect(sessionStorageMock.setItem).not.toHaveBeenCalled();
    expect(sessionStorageMock.removeItem).not.toHaveBeenCalled();
  });

  it.each([400, 422, 503])(
    'rejects HTTP %s without retry, refresh, success conversion, or storage mutation',
    async (status) => {
      const error = {
        response: { status, data: { detail: 'synthetic failure' } },
        config: { url: '/auth/reset-password', method: 'post', skipAuth: true },
      };
      mockAxiosInstance.post.mockRejectedValueOnce(error);
      localStorageMock.setItem('wilsy_auth_token', 'synthetic-access-token');
      localStorageMock.setItem('wilsy_refresh_token', 'synthetic-refresh-token');
      localStorageMock.setItem('wilsy_active_tenant', RESET_INPUT.tenantId);
      localStorageMock.setItem.mockClear();
      localStorageMock.removeItem.mockClear();

      await expect(resetPassword(RESET_INPUT)).rejects.toBe(error);
      expect(mockAxiosInstance.post).toHaveBeenCalledTimes(1);
      expect(mockAxiosInstance.post.mock.calls[0][0]).toBe('/auth/reset-password');
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
      expect(localStorageMock.removeItem).not.toHaveBeenCalled();
      expect(responseInterceptorCapture.rejected).toEqual(expect.any(Function));
      await expect(responseInterceptorCapture.rejected(error)).rejects.toBe(error);
      expect(mockAxiosInstance.post).toHaveBeenCalledTimes(1);
    },
  );

  it('preserves caller values, does not navigate or log, and remains transport-only', async () => {
    const original = { ...RESET_INPUT };
    mockAxiosInstance.post.mockResolvedValueOnce({ status: 204, data: undefined, headers: {} });
    await resetPassword(RESET_INPUT);

    expect(RESET_INPUT).toEqual(original);
    expect(consoleLogSpy).not.toHaveBeenCalled();
    expect(consoleWarnSpy).not.toHaveBeenCalled();
    expect(consoleErrorSpy).not.toHaveBeenCalled();
    expect(mockGenerateTraceAnchor).not.toHaveBeenCalled();
    expect(mockBroadcastTelemetry).not.toHaveBeenCalled();
    expect(mockBridgeLog).not.toHaveBeenCalled();
    expect(window.location.pathname).not.toBe('/login');
    expect(mockAxiosInstance.post.mock.calls).toHaveLength(1);
  });

  it('audits the production method boundary for forbidden client-owned authority and duplicate API paths', () => {
    const source = readApiSource();
    const methodStart = source.indexOf('const resetPassword =');
    const methodEnd = source.indexOf('\n\n/**', methodStart);
    expect(methodStart).toBeGreaterThanOrEqual(0);
    expect(methodEnd).toBeGreaterThan(methodStart);
    const methodSource = source.slice(methodStart, methodEnd);

    expect(methodSource).toContain("'/auth/reset-password'");
    expect(methodSource).toContain('tenant_id: tenantId');
    expect(methodSource).toContain('recovery_token: recoveryToken');
    expect(methodSource).toContain('new_password: newPassword');
    expect(methodSource).toContain('{ skipAuth: true }');
    expect(methodSource).not.toContain("'/api/");
    expect(methodSource).not.toMatch(/localStorage|sessionStorage|window\.location|refresh/i);
    expect(methodSource).not.toMatch(/jwt|role|permission|mfa|credentialRevision|hashPassword|bcrypt|mongo|axios\.get|fetch|XMLHttpRequest|WebSocket|EventSource/i);
    expect(source).toContain("/^\\/auth\\/reset-password$/i.test(config.url)");
  });
});

/**
 * ============================================================================
 * SOVEREIGN ARTIFACT SEAL
 * ============================================================================
 * ARTIFACT: Client password-reset API certificate
 * VERSION: v1.0.0-R10D7-CLIENT-PASSWORD-RESET-API-CERT
 * AUTHORITY BOUNDARY: Synthetic Axios seam only; no server or browser authority
 * TENANT POSTURE: Exact caller tenant projection is asserted, never granted
 * FAIL-CLOSED POSTURE: Non-204 HTTP failures reject and are never retried
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; untouched
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ============================================================================
 */
