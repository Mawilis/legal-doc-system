/**
 * ============================================================================
 * WILSY OS — RECOVERY CONTACT VERIFICATION API CERTIFICATE
 * ============================================================================
 * TITLE: Authenticated recovery-contact verification client transport certificate
 * VERSION: v1.0.0-R10E24-RECOVERY-CONTACT-VERIFICATION-API-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies exact protected initiation/completion bodies while retaining
 * bearer authentication and SHA3 request-seal headers without client-owned
 * verification, tenant, principal, or persistence authority.
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/recoveryContactVerificationApi.test.js
 * CERTIFICATION DATE: 2026-09-22
 * COMPLIANCE: POPIA §19, GDPR §32, SOC2 §CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic address and bearer values only.
 * TENANT BOUNDARY: X-Tenant-ID remains transport context; Python ACCESS identity
 *                  supplies canonical tenant/principal binding.
 * AUTHORITY BOUNDARY: Axios transport only; Python EOS owns verification truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * ============================================================================
 */

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
    mockGenerateTraceAnchor: vi.fn(() => 'TRC-R10E24'),
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
  sha3_512: vi.fn(() => 'synthetic-r10e24-sha3-512'),
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

import {
  completeRecoveryContactVerification,
  requestRecoveryContactVerification,
} from '../../services/api.js';

const ADDRESS = 'recovery-r10e24@example.com';
const TOKEN = 'R10E24-' + 'x'.repeat(40);
const TENANT = 'TENANT-R10E24';
const ACCESS = 'synthetic-access-r10e24';

const sealedConfig = async (url, data) => {
  localStorageMock.setItem('wilsy_auth_token', ACCESS);
  localStorageMock.setItem('wilsy_active_tenant', JSON.stringify({ tenantId: TENANT }));
  return requestInterceptorCapture.fulfilled({
    url,
    method: 'post',
    data,
    headers: {},
  });
};

describe('R10E24 recovery-contact verification API certificate', () => {
  let consoleLogSpy;
  let consoleWarnSpy;
  let consoleErrorSpy;

  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.clear();
    sessionStorageMock.clear();
    mockAxiosGet.mockResolvedValue({ data: {}, headers: {} });
    consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleLogSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  it('serializes exact authenticated initiation and completion bodies', async () => {
    mockAxiosInstance.post
      .mockResolvedValueOnce({ status: 202, data: undefined, headers: {} })
      .mockResolvedValueOnce({ status: 204, data: undefined, headers: {} });

    await requestRecoveryContactVerification({ address: ADDRESS });
    await completeRecoveryContactVerification({ verificationToken: TOKEN });

    expect(mockAxiosInstance.post).toHaveBeenNthCalledWith(
      1,
      '/auth/recovery-contact/verification',
      { address: ADDRESS },
    );
    expect(mockAxiosInstance.post).toHaveBeenNthCalledWith(
      2,
      '/auth/recovery-contact/verification/complete',
      { verification_token: TOKEN },
    );
  });

  it('keeps strict initiation body unchanged while retaining bearer and request seal', async () => {
    const config = await sealedConfig(
      '/auth/recovery-contact/verification',
      { address: ADDRESS },
    );

    expect(config.data).toEqual({ address: ADDRESS });
    expect(config.data).not.toHaveProperty('timestamp');
    expect(config.headers.Authorization).toBe(`Bearer ${ACCESS}`);
    expect(config.headers['X-Tenant-ID']).toBe(TENANT);
    expect(config.headers['x-trace-id']).toBe('TRC-R10E24');
    expect(config.headers['x-forensic-timestamp']).toBeDefined();
    expect(config.headers['x-cryptographic-nonce']).toBeDefined();
    expect(config.headers['x-request-seal']).toBe('synthetic-r10e24-sha3-512');
    expect(mockGenerateTraceAnchor).toHaveBeenCalledTimes(1);
  });

  it('keeps strict completion body unchanged while retaining bearer and request seal', async () => {
    const config = await sealedConfig(
      '/auth/recovery-contact/verification/complete',
      { verification_token: TOKEN },
    );

    expect(config.data).toEqual({ verification_token: TOKEN });
    expect(config.data).not.toHaveProperty('timestamp');
    expect(config.headers.Authorization).toBe(`Bearer ${ACCESS}`);
    expect(config.headers['X-Tenant-ID']).toBe(TENANT);
    expect(config.headers['x-request-seal']).toBe('synthetic-r10e24-sha3-512');
  });

  it('accepts bodyless 202 and 204 without storage mutation', async () => {
    const initiation = { status: 202, data: undefined, headers: {} };
    const completion = { status: 204, data: undefined, headers: {} };

    expect(await responseInterceptorCapture.fulfilled(initiation)).toBe(initiation);
    expect(await responseInterceptorCapture.fulfilled(completion)).toBe(completion);
    expect(localStorageMock.setItem).not.toHaveBeenCalled();
    expect(localStorageMock.removeItem).not.toHaveBeenCalled();
    expect(sessionStorageMock.setItem).not.toHaveBeenCalled();
    expect(sessionStorageMock.removeItem).not.toHaveBeenCalled();
  });

  it.each([400, 403, 409, 422, 503])(
    'preserves HTTP %s failure without retry or authority mutation',
    async (status) => {
      const error = {
        response: { status, data: { detail: 'synthetic failure' } },
        config: { url: '/auth/recovery-contact/verification', method: 'post' },
      };
      mockAxiosInstance.post.mockRejectedValueOnce(error);

      await expect(
        requestRecoveryContactVerification({ address: ADDRESS }),
      ).rejects.toBe(error);
      expect(mockAxiosInstance.post).toHaveBeenCalledTimes(1);
      await expect(responseInterceptorCapture.rejected(error)).rejects.toBe(error);
      expect(mockAxiosInstance.post).toHaveBeenCalledTimes(1);
      expect(localStorageMock.removeItem).not.toHaveBeenCalled();
    },
  );

  it('does not mark protected verification endpoints as public', async () => {
    expect(requestInterceptorCapture.fulfilled).toEqual(expect.any(Function));
    const config = await sealedConfig(
      '/auth/recovery-contact/verification',
      { address: ADDRESS },
    );
    expect(config.headers.Authorization).toBe(`Bearer ${ACCESS}`);
    expect(config.headers['x-request-seal']).toBeDefined();
    expect(mockBridgeLog).toHaveBeenCalledWith(
      'POST',
      '/auth/recovery-contact/verification',
    );
  });
});

/**
 * ============================================================================
 * SOVEREIGN ARTIFACT SEAL
 * ============================================================================
 * ARTIFACT: Authenticated recovery-contact verification client API certificate
 * VERSION: v1.0.0-R10E24-RECOVERY-CONTACT-VERIFICATION-API-CERT
 * AUTHORITY BOUNDARY: Synthetic signed Axios transport only
 * TENANT POSTURE: Protected ACCESS identity remains server authority
 * FAIL-CLOSED POSTURE: Strict bodies are preserved; failures never become success
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ============================================================================
 */
