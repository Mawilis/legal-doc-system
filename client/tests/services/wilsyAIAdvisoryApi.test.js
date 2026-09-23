/**
 * WILSY OS — C1C/C1E CLIENT TRANSPORT CERTIFICATE
 *
 * TITLE: Dedicated legal-advisory adapter certificate
 * VERSION: v1.0.0-C1E-R1B
 * AUTHORITY: Wilsy OS Core Governance; transport evidence only
 * EPITOME: Certifies exact endpoint, payload, replay-header, response, and
 *          fail-closed behavior over the existing sovereign api.js client.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/services/wilsyAIAdvisoryApi.test.js
 * COLLABORATION / OWNERSHIP: wilsyAIAdvisoryApi.js and client/src/services/api.js.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.0.0-C1E-R1B — Added focused adapter contract coverage.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Only the sovereign api.js module is mocked.
 * TENANT BOUNDARY: Adapter payloads never carry or derive tenant identity.
 * AUTHORITY BOUNDARY: Tests prove transport only; Python EOS remains sovereign.
 * FINANCIAL AUTHORITY BOUNDARY: No billing, payment, settlement, or execution surface.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const { mockApi } = vi.hoisted(() => ({
  mockApi: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

vi.mock('../../src/services/api.js', () => ({ default: mockApi }));

import {
  executeWilsyAILegalServices,
  generateWilsyAILegalNextActions,
  readWilsyAILegalNextAction,
} from '../../src/services/wilsyAIAdvisoryApi.js';

describe('wilsyAIAdvisoryApi — C1C/C1E transport contract', () => {
  let storageSpies;

  beforeEach(() => {
    vi.clearAllMocks();
    const storageSentinel = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    };
    Object.defineProperty(window, 'localStorage', { configurable: true, value: storageSentinel });
    Object.defineProperty(window, 'sessionStorage', { configurable: true, value: storageSentinel });
    storageSpies = Object.values(storageSentinel);
  });

  afterEach(() => {
    storageSpies.forEach((spy) => spy.mockRestore());
  });

  it('uses the exact C1C endpoint and prompt-only body', async () => {
    mockApi.post.mockResolvedValueOnce({ status: 201, data: { orchestration_id: 'orch-1' } });

    await executeWilsyAILegalServices('recorded matter prompt', 'replay-key-1');

    expect(mockApi.post).toHaveBeenCalledWith(
      '/wilsy-ai/legal-services',
      { prompt: 'recorded matter prompt' },
      { headers: { 'Idempotency-Key': 'replay-key-1' } },
    );
    expect(mockApi.post.mock.calls[0][1]).toEqual({ prompt: 'recorded matter prompt' });
    expect(Object.keys(mockApi.post.mock.calls[0][1])).toEqual(['prompt']);
  });

  it('forwards the caller idempotency key exactly without generating one', async () => {
    const suppliedKey = '  caller-key/ß  ';
    mockApi.post.mockResolvedValueOnce({ status: 201, data: {} });

    await executeWilsyAILegalServices('prompt', suppliedKey);

    expect(mockApi.post.mock.calls[0][2].headers['Idempotency-Key']).toBe(suppliedKey);
    expect(mockApi.post).toHaveBeenCalledTimes(1);
  });

  it('uses the exact C1E generation endpoint and orchestration body', async () => {
    mockApi.post.mockResolvedValueOnce({ status: 201, data: { advisory_id: 'adv-1' } });

    await generateWilsyAILegalNextActions('orch-1');

    expect(mockApi.post).toHaveBeenCalledWith(
      '/wilsy-ai/legal-next-actions',
      { orchestration_id: 'orch-1' },
    );
  });

  it('uses a path-safe encoded advisory identity for C1E reads', async () => {
    mockApi.get.mockResolvedValueOnce({ status: 200, data: { advisory_id: 'a/b?c' } });

    await readWilsyAILegalNextAction('a/b?c');

    expect(mockApi.get).toHaveBeenCalledWith('/wilsy-ai/legal-next-actions/a%2Fb%3Fc');
  });

  it('preserves a 201 creation status', async () => {
    mockApi.post.mockResolvedValueOnce({ status: 201, data: { advisory_id: 'new-1' } });

    const result = await generateWilsyAILegalNextActions('orch-201');

    expect(result.status).toBe(201);
  });

  it('preserves a 200 exact-replay status', async () => {
    mockApi.post.mockResolvedValueOnce({ status: 200, data: { advisory_id: 'replay-1' } });

    const result = await generateWilsyAILegalNextActions('orch-replay');

    expect(result.status).toBe(200);
  });

  it('preserves CURRENT payload identity without transformation', async () => {
    const currentPayload = {
      advisory_id: 'current-1',
      status: 'CURRENT',
      risk_level: 'LOW',
      confidence_basis: { source_snapshot: 'snap-1' },
    };
    mockApi.get.mockResolvedValueOnce({ status: 200, data: currentPayload });

    const result = await readWilsyAILegalNextAction('current-1');

    expect(result.data).toBe(currentPayload);
  });

  it('preserves STALE payload and successor identity unchanged', async () => {
    const stalePayload = {
      advisory_id: 'stale-1',
      status: 'STALE',
      successor_advisory_id: 'successor-1',
      source_snapshot: 'snap-old',
    };
    mockApi.get.mockResolvedValueOnce({ status: 409, data: stalePayload });

    const result = await readWilsyAILegalNextAction('stale-1');

    expect(result.status).toBe(409);
    expect(result.data).toBe(stalePayload);
  });

  it.each([403, 404, 409, 422, 503])('propagates a %s server rejection unchanged', async (status) => {
    const error = { response: { status, data: { code: `C1E_${status}` } } };
    mockApi.get.mockRejectedValueOnce(error);

    await expect(readWilsyAILegalNextAction(`advisory-${status}`)).rejects.toBe(error);
  });

  it('does not turn an error into a fake advisory', async () => {
    const error = { response: { status: 503, data: { code: 'UPSTREAM_UNAVAILABLE' } } };
    mockApi.post.mockRejectedValueOnce(error);

    await expect(executeWilsyAILegalServices('prompt', 'key')).rejects.toBe(error);
    expect(mockApi.post).toHaveBeenCalledTimes(1);
  });

  it('never calls a generic operator path', async () => {
    mockApi.post
      .mockResolvedValueOnce({ status: 201, data: {} })
      .mockResolvedValueOnce({ status: 201, data: {} });
    mockApi.get.mockResolvedValueOnce({ status: 200, data: {} });

    await executeWilsyAILegalServices('prompt', 'key');
    await generateWilsyAILegalNextActions('orch');
    await readWilsyAILegalNextAction('advisory');

    const paths = [
      ...mockApi.post.mock.calls.map(([path]) => path),
      ...mockApi.get.mock.calls.map(([path]) => path),
    ];
    expect(paths.some((path) => path === '/api/ai/operator' || path === '/ai/operator')).toBe(false);
  });

  it('does not touch browser storage', async () => {
    mockApi.post.mockResolvedValueOnce({ status: 201, data: {} });
    mockApi.get.mockResolvedValueOnce({ status: 200, data: {} });

    await executeWilsyAILegalServices('prompt', 'key');
    await readWilsyAILegalNextAction('advisory');

    storageSpies.forEach((spy) => expect(spy).not.toHaveBeenCalled());
  });

  it('does not automatically chain C1C into C1E', async () => {
    mockApi.post.mockResolvedValueOnce({ status: 201, data: { orchestration_id: 'orch-only' } });

    await executeWilsyAILegalServices('prompt', 'key');

    expect(mockApi.post).toHaveBeenCalledTimes(1);
    expect(mockApi.post.mock.calls[0][0]).toBe('/wilsy-ai/legal-services');
  });

  it('does not automatically chain C1E generation into C1C or GET', async () => {
    mockApi.post.mockResolvedValueOnce({ status: 201, data: { advisory_id: 'adv-only' } });

    await generateWilsyAILegalNextActions('orch-only');

    expect(mockApi.post).toHaveBeenCalledTimes(1);
    expect(mockApi.get).not.toHaveBeenCalled();
    expect(mockApi.post.mock.calls[0][0]).toBe('/wilsy-ai/legal-next-actions');
  });

  it.each([
    ['prompt', executeWilsyAILegalServices, ['', 'key']],
    ['prompt', executeWilsyAILegalServices, [null, 'key']],
    ['idempotencyKey', executeWilsyAILegalServices, ['prompt', '']],
    ['idempotencyKey', executeWilsyAILegalServices, ['prompt', undefined]],
    ['orchestrationId', generateWilsyAILegalNextActions, ['']],
    ['orchestrationId', generateWilsyAILegalNextActions, [undefined]],
    ['advisoryId', readWilsyAILegalNextAction, ['']],
    ['advisoryId', readWilsyAILegalNextAction, [42]],
  ])('rejects structurally absent %s input before dispatch', async (_name, operation, args) => {
    await expect(operation(...args)).rejects.toBeInstanceOf(TypeError);
    expect(mockApi.post).not.toHaveBeenCalled();
    expect(mockApi.get).not.toHaveBeenCalled();
  });
});

// ARTIFACT: wilsyAIAdvisoryApi.test.js
// VERSION: v1.0.0-C1E-R1B
// AUTHORITY BOUNDARY: deterministic browser transport certificate only
// TENANT POSTURE: api.js remains the sole authenticated tenant-header owner
// FAIL-CLOSED POSTURE: server failures reject; no advisory fallback is accepted
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
