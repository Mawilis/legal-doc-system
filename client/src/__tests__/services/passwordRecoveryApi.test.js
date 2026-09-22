/**
 * WILSY OS — PASSWORD RECOVERY CLIENT API CERTIFICATE
 * VERSION: v1.0.0-R10E58-PASSWORD-RECOVERY-API-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies exact browser transport for recovery request, authenticated
 *          recovery-contact verification request, and public verification
 *          completion without duplicating Python recovery or contact authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/passwordRecoveryApi.test.js
 * COLLABORATION / OWNERSHIP: Exercises live methods in client/src/services/api.js
 *                            through a synthetic Axios instance; Python EOS owns
 *                            all recovery, contact, credential, and tenant truth.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v1.0.0-R10E58-PASSWORD-RECOVERY-API-CERT — Adds exact path/body/auth-mode evidence for all R10E
 *            recovery transports, including proof that authenticated contact
 *            verification sends an empty body and public capability consumers
 *            remain skipAuth.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic values only; no network, secret storage,
 *                             telemetry, or authority mutation occurs.
 * TENANT BOUNDARY: Tenant selectors are forwarded only where the public Python
 *                  contract requires them; authenticated contact verification
 *                  sends no browser tenant/email/principal authority.
 * AUTHORITY BOUNDARY: Client HTTP transport evidence only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
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
    mockGenerateTraceAnchor: vi.fn(() => 'TRC-R10E58'),
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

import api, {
  completeRecoveryContactVerification,
  requestPasswordRecovery,
  requestRecoveryContactVerification,
} from '../../services/api.js';

const REQUEST_INPUT = Object.freeze({
  tenantId: 'TENANT-R10E58',
  email: 'member@example.test',
});
const VERIFY_INPUT = Object.freeze({
  tenantId: 'TENANT-R10E58',
  verificationToken: 'verification-token-r10e58-synthetic',
});

const readApiSource = () => readFileSync(
  resolve(process.cwd(), 'src/services/api.js'),
  'utf8',
);

describe('R10E58 password recovery client API certificate', () => {
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

  it('sends the exact generic public password-recovery request', async () => {
    const response = { status: 202, data: { status: 'RECOVERY_REQUEST_ACCEPTED' } };
    mockAxiosInstance.post.mockResolvedValueOnce(response);

    await expect(requestPasswordRecovery(REQUEST_INPUT)).resolves.toBe(response);
    expect(mockAxiosInstance.post).toHaveBeenCalledWith(
      '/auth/request-password-reset',
      { tenant_id: REQUEST_INPUT.tenantId, email: REQUEST_INPUT.email },
      { skipAuth: true },
    );
    expect(mockAxiosInstance.post).toHaveBeenCalledTimes(1);
    expect(api.defaults.baseURL).toBe('/api');
  });

  it('requests authenticated recovery-contact verification with no browser identity body', async () => {
    const response = { status: 202, data: { status: 'VERIFICATION_SENT' } };
    mockAxiosInstance.post.mockResolvedValueOnce(response);

    await expect(requestRecoveryContactVerification()).resolves.toBe(response);
    expect(mockAxiosInstance.post).toHaveBeenCalledWith(
      '/auth/recovery-contact/request-verification',
      {},
    );
    expect(mockAxiosInstance.post.mock.calls[0]).toHaveLength(2);
  });

  it('submits only tenant selector and transient verification capability publicly', async () => {
    const response = { status: 204, data: undefined };
    mockAxiosInstance.post.mockResolvedValueOnce(response);

    await expect(completeRecoveryContactVerification(VERIFY_INPUT)).resolves.toBe(response);
    expect(mockAxiosInstance.post).toHaveBeenCalledWith(
      '/auth/recovery-contact/verify',
      {
        tenant_id: VERIFY_INPUT.tenantId,
        verification_token: VERIFY_INPUT.verificationToken,
      },
      { skipAuth: true },
    );
    expect(Object.keys(mockAxiosInstance.post.mock.calls[0][1]).sort()).toEqual([
      'tenant_id',
      'verification_token',
    ]);
  });

  it('keeps public recovery request and verification completion bearer-free at the interceptor', async () => {
    localStorageMock.setItem('wilsy_auth_token', 'synthetic-access-token');
    localStorageMock.setItem('wilsy_active_tenant', JSON.stringify({ tenantId: REQUEST_INPUT.tenantId }));

    for (const config of [
      {
        url: '/auth/request-password-reset',
        method: 'post',
        data: { tenant_id: REQUEST_INPUT.tenantId, email: REQUEST_INPUT.email },
        skipAuth: true,
        headers: {},
      },
      {
        url: '/auth/recovery-contact/verify',
        method: 'post',
        data: {
          tenant_id: VERIFY_INPUT.tenantId,
          verification_token: VERIFY_INPUT.verificationToken,
        },
        skipAuth: true,
        headers: {},
      },
    ]) {
      const sealed = await requestInterceptorCapture.fulfilled(config);
      expect(sealed.headers.Authorization).toBeUndefined();
      expect(sealed.skipAuth).toBe(true);
      expect(sealed.data).toEqual(config.data);
    }
  });

  it('preserves bearer authentication for current-email verification without adding a body identity claim', async () => {
    localStorageMock.setItem('wilsy_auth_token', 'synthetic-access-token');
    localStorageMock.setItem('wilsy_active_tenant', JSON.stringify({ tenantId: REQUEST_INPUT.tenantId }));

    const sealed = await requestInterceptorCapture.fulfilled({
      url: '/auth/recovery-contact/request-verification',
      method: 'post',
      data: {},
      headers: {},
    });

    expect(sealed.headers.Authorization).toBe('Bearer synthetic-access-token');
    expect(sealed.data).toEqual({});
    expect(sealed.data).not.toHaveProperty('email');
    expect(sealed.data).not.toHaveProperty('tenant_id');
    expect(sealed.data).not.toHaveProperty('principal_id');
    expect(sealed.data).not.toHaveProperty('verified');
  });

  it.each([
    ['requestPasswordRecovery', () => requestPasswordRecovery(REQUEST_INPUT), 429],
    ['completeRecoveryContactVerification', () => completeRecoveryContactVerification(VERIFY_INPUT), 400],
    ['requestRecoveryContactVerification', () => requestRecoveryContactVerification(), 503],
  ])('propagates %s HTTP failures without client retry or success conversion', async (_name, invoke, status) => {
    const error = { response: { status, data: { detail: 'synthetic failure' } } };
    mockAxiosInstance.post.mockRejectedValueOnce(error);

    await expect(invoke()).rejects.toBe(error);
    expect(mockAxiosInstance.post).toHaveBeenCalledTimes(1);
    expect(localStorageMock.setItem).not.toHaveBeenCalled();
    expect(sessionStorageMock.setItem).not.toHaveBeenCalled();
  });

  it('audits the production methods for exact authority boundaries', () => {
    const source = readApiSource();

    const requestStart = source.indexOf('const requestPasswordRecovery =');
    const contactStart = source.indexOf('const requestRecoveryContactVerification =');
    const verifyStart = source.indexOf('const completeRecoveryContactVerification =');
    const resetStart = source.indexOf('const resetPassword =');

    expect(requestStart).toBeGreaterThanOrEqual(0);
    expect(contactStart).toBeGreaterThan(requestStart);
    expect(verifyStart).toBeGreaterThan(contactStart);
    expect(resetStart).toBeGreaterThan(verifyStart);

    const requestSource = source.slice(requestStart, contactStart);
    const contactSource = source.slice(contactStart, verifyStart);
    const verifySource = source.slice(verifyStart, resetStart);

    expect(requestSource).toContain("'/auth/request-password-reset'");
    expect(requestSource).toContain('{ skipAuth: true }');
    expect(contactSource).toContain("'/auth/recovery-contact/request-verification'");
    expect(contactSource).toContain('{}');
    expect(contactSource).not.toMatch(/email|tenant_id|principal_id|verification_token/);
    expect(verifySource).toContain("'/auth/recovery-contact/verify'");
    expect(verifySource).toContain('tenant_id: tenantId');
    expect(verifySource).toContain('verification_token: verificationToken');
    expect(verifySource).toContain('{ skipAuth: true }');

    for (const methodSource of [requestSource, contactSource, verifySource]) {
      expect(methodSource).not.toMatch(/localStorage|sessionStorage|window\.location|hashPassword|bcrypt|mongo|role|permission|mfaRegistered/i);
    }
  });

  it('does not log, persist, or emit telemetry for the three recovery transport calls', async () => {
    mockAxiosInstance.post
      .mockResolvedValueOnce({ status: 202, data: { status: 'RECOVERY_REQUEST_ACCEPTED' } })
      .mockResolvedValueOnce({ status: 202, data: { status: 'VERIFICATION_SENT' } })
      .mockResolvedValueOnce({ status: 204, data: undefined });

    await requestPasswordRecovery(REQUEST_INPUT);
    await requestRecoveryContactVerification();
    await completeRecoveryContactVerification(VERIFY_INPUT);

    expect(consoleLogSpy).not.toHaveBeenCalled();
    expect(consoleWarnSpy).not.toHaveBeenCalled();
    expect(consoleErrorSpy).not.toHaveBeenCalled();
    expect(mockGenerateTraceAnchor).not.toHaveBeenCalled();
    expect(mockBroadcastTelemetry).not.toHaveBeenCalled();
    expect(mockBridgeLog).not.toHaveBeenCalled();
    expect(localStorageMock.setItem).not.toHaveBeenCalled();
    expect(sessionStorageMock.setItem).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: passwordRecoveryApi.test.js
 * VERSION: v1.0.0-R10E58-PASSWORD-RECOVERY-API-CERT
 * AUTHORITY BOUNDARY: deterministic Axios transport evidence only
 * TENANT POSTURE: public tenant selectors remain lookup-only; authenticated verification sends none
 * FAIL-CLOSED POSTURE: transport failures reject without local authority or retry
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
