/**
 * WILSY OS — P8-R1 LEGAL WORK COMPLETION BROWSER TRANSPORT CERT
 * VERSION: v1.0.0-P8-R1-LEGAL-WORK-COMPLETION-CLIENT-RED
 * AUTHORITY: Browser transport contract only; Python EOS owns IAM,
 * completion authorization, evidence persistence and currentness.
 * EPITOME: Prove the browser adapter emits only opaque completion intent to
 * the canonical EOS command and rejects caller-owned authority fields.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/legalOperationsWorkCompletion.test.js
 * COLLABORATION / OWNERSHIP: Python EOS owns completion authority and durable
 * truth; this certificate owns browser-transport boundary evidence only.
 * CERTIFICATION / UPDATE DATE: 2026-10-19
 * CHANGELOG: v1.0.0 establishes strict completion-command transport,
 * canonical endpoint, opaque evidence, and authority-field rejection proof.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 controls.
 * SECURITY / PRIVACY POSTURE: Synthetic identifiers only; no credentials,
 * legal content, tenant authority, or production evidence is persisted.
 * TENANT BOUNDARY: No browser-owned tenant/principal/role selectors.
 * AUTHORITY BOUNDARY: Test evidence only; creates no IAM, assignment,
 * completion, workflow, billing, payment, or settlement authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED POSTURE: Extra, missing, malformed, or authority-bearing input
 * rejects before transport; response scope drift rejects after transport.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

const { mockPost } = vi.hoisted(() => ({
  mockPost: vi.fn(),
}));

vi.mock('../../services/api.js', () => ({
  default: { get: vi.fn(), post: mockPost },
}));

vi.mock('../../utils/sovereignClient.js', () => ({
  default: { post: mockPost },
}));

import * as legalOperations from '../../services/legalOperationsService.js';

const fingerprint = 'a'.repeat(128);

describe('P8 authenticated work-completion transport', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('exposes the governed completion command adapter', () => {
    expect(typeof legalOperations.completeLegalWorkItem).toBe(
      'function',
    );
  });

  it('sends only opaque evidence to the canonical server command', async () => {
    const complete = legalOperations.completeLegalWorkItem;
    expect(typeof complete).toBe('function');

    mockPost.mockResolvedValue({
      data: {
        data: {
          work_item_id: 'work-1',
        },
      },
    });

    await complete({
      workItemId: 'work-1',
      completionEvidenceReference: 'evidence:work-1',
      completionEvidenceFingerprint: fingerprint,
    });

    expect(mockPost).toHaveBeenCalledTimes(1);
    expect(mockPost).toHaveBeenCalledWith(
      '/legal-operations/work-items/work-1/completion',
      {
        completion_evidence_reference: 'evidence:work-1',
        completion_evidence_fingerprint: fingerprint,
      },
    );
  });

  it('rejects caller-owned authority fields before transport', async () => {
    const complete = legalOperations.completeLegalWorkItem;
    expect(typeof complete).toBe('function');

    await expect(complete({
      workItemId: 'work-1',
      completionEvidenceReference: 'evidence:work-1',
      completionEvidenceFingerprint: fingerprint,
      tenantId: 'forged-tenant',
    })).rejects.toThrow();

    expect(mockPost).not.toHaveBeenCalled();
  });
});

// ARTIFACT: legalOperationsWorkCompletion.test.js
// VERSION: v1.0.0-P8-R1-LEGAL-WORK-COMPLETION-CLIENT-RED
// AUTHORITY BOUNDARY: browser-transport certificate only
// TENANT POSTURE: no browser-owned tenant, principal, or role selector
// FAIL-CLOSED POSTURE: malformed or authority-bearing intent rejects
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
