/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * TITLE: WILSY OS Conversation History Engine Durable Archive Certificate
 * VERSION: v5.6.1-PRINCIPAL-REHYDRATION-REFUSAL-CERT
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: Encrypted history transport, owner isolation and session fallback
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/wilsyAIConversationHistoryEngine.test.js
 * COLLABORATION / OWNERSHIP: EOS history router and current Dock history engine
 * CERTIFICATION / UPDATE DATE: 2026-11-25
 * CHANGELOG: v5.6.1-PRINCIPAL-REHYDRATION-REFUSAL-CERT tests
 *            same-tenant foreign-principal archive denial and non-elevation
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2
 * SECURITY / PRIVACY POSTURE: Synthetic scopes and prompts; no real secrets
 * TENANT BOUNDARY: Exact identity scope is checked; mocks grant no IAM
 * AUTHORITY BOUNDARY: Test-only evidence; Python EOS owns durable truth
 * FINANCIAL AUTHORITY BOUNDARY: No paid model or payment execution
 *
 * Wilsy OS — AI Conversation History Engine Session-Bound Certificate
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/tests/client/wilsyAIConversationHistoryEngine.test.js
 * Version:        v5.6.1-PRINCIPAL-REHYDRATION-REFUSAL-CERT
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Direct certificate for transient same-session conversation
 *                 history with EOS-encrypted remote archive and explicit
 *                 session-only fallback; no localStorage conversation data.
 * Classification: Production Test Artifact — Institutional Contract
 *
 * Change Log:
 *   2026-11-25 v5.6.1-PRINCIPAL-REHYDRATION-REFUSAL-CERT — Verifies the authenticated
 *     principal selector must match the EOS history response even when HTTP
 *     succeeds, without creating cross-identity cached conversations.
 *   2026-11-25 v5.6.0-EOS-DURABLE-HISTORY-ISOLATION-CERT — Tests approved Python EOS history transport,
 *     durable create/revision/reload, archive isolation and failed-write
 *     session fallback without treating saved text as live EOS evidence.
 *   2026-09-24 v5.4.2-SESSION-BOUND-LEGAL-HISTORY-CERT — Replaced retired backend-history assumptions with
 *     direct session-memory, cache-integrity, fail-closed, and no-network proofs.
 *   2026-08-05 v5.1.1-KENNEL-PHASE5 — Fixed async integrity checks.
 *   2026-08-05 v5.1.0-KENNEL-PHASE5 — Initial creation.
 *
 * Certification Seal: PRODUCTION_READY_v5.6.1-PRINCIPAL-REHYDRATION-REFUSAL-CERT
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { readFileSync } from 'node:fs';
import { vi } from 'vitest';

const { mockGet, mockPut, mockDelete } = vi.hoisted(() => ({
  mockGet: vi.fn(), mockPut: vi.fn(), mockDelete: vi.fn(),
}));
vi.mock('../../src/services/api.js', () => ({
  default: { get: mockGet, put: mockPut, delete: mockDelete },
}));
import {
  normalizeWilsyAIConversationText,
  resolveWilsyAIConversationWorkspace,
  resolveWilsyChatHistoryTitle,
  loadWilsyAIConversationThreads,
  createWilsyAIConversationThread,
  persistWilsyAIConversationTurn,
  clearWilsyAIConversationThreads,
  saveWilsyAIConversationThreads,
  getCachedThreads,
  syncThreads,
  verifyThreadIntegrity,
  deleteWilsyAIConversationThread,
  wilsyAIConversationHistoryPosture,
} from '../../src/components/intelligence/wilsyAIConversationHistoryEngine.js';

describe('Wilsy AI Conversation History Engine — session-bound authority', () => {
  beforeEach(async () => {
    window.__WILSY_ACTIVE_TENANT__ = { tenantId: 'TEST_TENANT' };
    mockGet.mockReset().mockRejectedValue(new Error('EOS history not configured'));
    mockPut.mockReset().mockRejectedValue(new Error('EOS history not configured'));
    mockDelete.mockReset().mockRejectedValue(new Error('EOS history not configured'));
    await clearWilsyAIConversationThreads();
  });

  describe('normalization helpers', () => {
    it('trims and collapses conversation text', () => {
      expect(normalizeWilsyAIConversationText('  hello   world  ')).toBe('hello world');
    });

    it('returns the supplied fallback for empty text', () => {
      expect(normalizeWilsyAIConversationText('', 'fallback')).toBe('fallback');
    });

    it('resolves workspace from payload, context, then fallback', () => {
      expect(resolveWilsyAIConversationWorkspace({ workspace: 'Billing' })).toBe('Billing');
      expect(resolveWilsyAIConversationWorkspace({ context: { workspace: 'CRM' } })).toBe('CRM');
      expect(resolveWilsyAIConversationWorkspace({})).toBe('Workspace');
    });

    it('creates a contextual title and preserves a non-placeholder existing title', () => {
      const generated = resolveWilsyChatHistoryTitle({
        workspace: 'Billing',
        promptText: 'Check invoices',
      });
      expect(generated).toContain('Billing');
      expect(generated).toContain('Check invoices');

      expect(resolveWilsyChatHistoryTitle({
        workspace: 'Billing',
        thread: { title: 'Existing Title' },
      })).toBe('Existing Title');
    });
  });

  describe('canonical EOS history transport boundary', () => {
    it('uses only Python EOS history, never a retired BFF or localStorage for transcripts', () => {
      const source = readFileSync(
        `${process.cwd()}/src/components/intelligence/wilsyAIConversationHistoryEngine.js`,
        'utf8',
      );
      expect(source).not.toContain('/api/ai/conversations');
      expect(source).toContain("'/wilsy-ai/history'");
      expect(source).toContain("'/wilsy-ai/history/'");
      expect(source).not.toMatch(/localStorage\.setItem\(/);
    });

    it('starts empty after an explicit same-session clear', async () => {
      expect(await loadWilsyAIConversationThreads()).toEqual([]);
      expect(getCachedThreads()).toEqual([]);
    });

    it('loads only the explicitly seeded same-session cache', async () => {
      const seeded = [{
        id: 'seed-1',
        title: 'Seeded',
        workspace: 'Legal',
        messages: [],
        tenantId: 'TEST_TENANT',
        storagePosture: 'SESSION_ONLY',
      }];
      saveWilsyAIConversationThreads(seeded);

      const loaded = await loadWilsyAIConversationThreads();
      expect(loaded).toEqual(seeded);
      expect(loaded).not.toBe(seeded);
    });
  });

  describe('session thread creation', () => {
    it('creates a sealed session thread without durable persistence authority', async () => {
      const thread = await createWilsyAIConversationThread({
        workspace: 'Legal',
        title: 'Matter review',
      });

      expect(thread.id).toMatch(/^session-/);
      expect(thread.title).toBe('Matter review');
      expect(thread.workspace).toBe('Legal');
      expect(thread.tenantId).toBe('TEST_TENANT');
      expect(thread.storagePosture).toBe('SESSION_ONLY');
      expect(thread.messages).toEqual([]);
      expect(thread.proofHash).toMatch(/^[a-f0-9]{64}$/);
      expect(getCachedThreads()).toHaveLength(1);
      expect(getCachedThreads()[0].id).toBe(thread.id);
    });

    it('creates distinct session identities without offline/backend fallback semantics', async () => {
      const first = await createWilsyAIConversationThread({ title: 'First' });
      const second = await createWilsyAIConversationThread({ title: 'Second' });

      expect(first.id).toMatch(/^session-/);
      expect(second.id).toMatch(/^session-/);
      expect(second.id).not.toBe(first.id);
      expect(getCachedThreads()).toHaveLength(2);
    });
  });

  describe('session turn persistence', () => {
    it('appends the canonical {threadId, message} shape and reseals the thread', async () => {
      const thread = await createWilsyAIConversationThread({
        workspace: 'Legal',
        title: 'Matter review',
      });
      const originalProof = thread.proofHash;

      const updated = await persistWilsyAIConversationTurn({
        threadId: thread.id,
        message: {
          role: 'user',
          content: '  Check   service address  ',
          timestamp: '2026-09-24T18:00:00.000Z',
          meta: { source: 'TEST' },
        },
      });

      expect(updated.messages).toHaveLength(1);
      expect(updated.messages[0]).toEqual({
        role: 'user',
        content: 'Check service address',
        timestamp: '2026-09-24T18:00:00.000Z',
        meta: { source: 'TEST' },
      });
      expect(updated.storagePosture).toBe('SESSION_ONLY');
      expect(updated.proofHash).toMatch(/^[a-f0-9]{64}$/);
      expect(updated.proofHash).not.toBe(originalProof);
      expect(await verifyThreadIntegrity(updated)).toBe(true);
    });

    it('preserves the legacy (threadId, message) caller shape only as session compatibility', async () => {
      const thread = await createWilsyAIConversationThread({ title: 'Compatibility' });
      const updated = await persistWilsyAIConversationTurn(thread.id, {
        role: 'assistant',
        content: 'Session-only reply',
        timestamp: '2026-09-24T18:01:00.000Z',
      });

      expect(updated.messages).toHaveLength(1);
      expect(updated.messages[0].role).toBe('assistant');
      expect(updated.messages[0].content).toBe('Session-only reply');
      expect(updated.storagePosture).toBe('SESSION_ONLY');
    });

    it('creates a new session thread when no threadId is supplied', async () => {
      const updated = await persistWilsyAIConversationTurn({
        workspace: 'Legal',
        promptText: 'Hello',
        answerText: 'Hi',
      });

      expect(updated.id).toMatch(/^session-/);
      expect(updated.messages).toHaveLength(2);
      expect(updated.messages.map((message) => message.role)).toEqual(['user', 'assistant']);
      expect(updated.storagePosture).toBe('SESSION_ONLY');
    });

    it('fails closed when a caller names an unknown session thread', async () => {
      await expect(
        persistWilsyAIConversationTurn({
          threadId: 'missing-thread',
          message: { role: 'user', content: 'Should fail' },
        }),
      ).rejects.toThrow('WILSY_AI_SESSION_THREAD_NOT_FOUND');
    });
  });


  describe('encrypted EOS history persistence and currentness', () => {
    it('persists a thread, revises its transcript and recovers it after browser-memory reset', async () => {
      const records = new Map();
      mockPut.mockImplementation(async (path, body) => {
        const id = path.split('/').pop();
        const previous = records.get(id);
        if (body.expected_revision !== (previous?.revision || 0)) {
          throw Object.assign(new Error('conflict'), { response: { status: 409 } });
        }
        const revision = body.expected_revision + 1;
        records.set(id, {
          id, revision, title: body.title, workspace: body.workspace,
          updatedAt: '2026-11-25T14:55:00Z', messages: body.messages,
          storagePosture: 'EOS_ENCRYPTED_HISTORY',
          authority: 'RECORDED_TRANSCRIPT_NOT_CURRENT_SOURCE',
        });
        return { data: {
          schema: 'WILSY-AI-HISTORY-THREAD/V1', id, revision,
          storagePosture: 'EOS_ENCRYPTED_HISTORY',
        } };
      });
      mockGet.mockImplementation(async () => ({
        data: { schema: 'WILSY-AI-HISTORY/V1', tenant_id: 'TEST_TENANT',
          principal_id: 'test-principal', threads: [...records.values()] },
      }));
      const created = await createWilsyAIConversationThread({
        title: 'Foundation review', workspace: 'Projects',
      });
      expect(created.storagePosture).toBe('EOS_ENCRYPTED_HISTORY');
      expect(created.revision).toBe(1);
      const saved = await persistWilsyAIConversationTurn({
        threadId: created.id,
        message: { role: 'assistant', content: 'EOS task source was inspected',
          timestamp: '2026-11-25T14:55:00Z',
          meta: { source: 'PYTHON_EOS', phase: 'SOURCE_VERIFIED_READ_ONLY' } },
      });
      expect(saved.storagePosture).toBe('EOS_ENCRYPTED_HISTORY');
      expect(saved.revision).toBe(2);
      expect(wilsyAIConversationHistoryPosture()).toBe('READY');
      await clearWilsyAIConversationThreads();
      const recovered = await loadWilsyAIConversationThreads();
      expect(recovered).toHaveLength(1);
      expect(recovered[0].title).toBe('Foundation review');
      expect(recovered[0].revision).toBe(2);
      expect(recovered[0].messages[0].meta).toEqual({
        source: 'EOS_SAVED_TRANSCRIPT', phase: 'HISTORICAL_NOT_LIVE_EVIDENCE',
      });
      expect(await verifyThreadIntegrity(recovered[0])).toBe(true);
      mockDelete.mockResolvedValue({ data: {
        schema: 'WILSY-AI-HISTORY-DELETED/V1', id: created.id, deleted: true,
      } });
      await deleteWilsyAIConversationThread(created.id);
      expect(mockDelete).toHaveBeenCalledWith(
        '/wilsy-ai/history/' + encodeURIComponent(created.id),
        expect.objectContaining({ params: { expected_revision: 2 } }),
      );
      expect(getCachedThreads()).toHaveLength(0);
    });

    it('refuses foreign-scope archive even when EOS HTTP returns 200', async () => {
      mockGet.mockResolvedValue({ data: {
        schema: 'WILSY-AI-HISTORY/V1', tenant_id: 'FOREIGN_TENANT',
        principal_id: 'foreign', threads: [],
      } });
      expect(await loadWilsyAIConversationThreads()).toEqual([]);
      expect(wilsyAIConversationHistoryPosture()).toBe('UNAVAILABLE');
    });

    it('refuses same-tenant history for a different authenticated principal', async () => {
      mockGet.mockResolvedValue({ data: {
        schema: 'WILSY-AI-HISTORY/V1', tenant_id: 'TEST_TENANT',
        principal_id: 'principal-B', threads: [],
      } });
      const recovered = await loadWilsyAIConversationThreads({
        tenantId: 'TEST_TENANT', principalId: 'principal-A',
      });
      expect(recovered).toEqual([]);
      expect(wilsyAIConversationHistoryPosture()).toBe('UNAVAILABLE');
    });

    it('does not erase a saved thread on an unverified EOS deletion', async () => {
      mockPut.mockImplementation(async (path, body) => ({
        data: { schema: 'WILSY-AI-HISTORY-THREAD/V1',
          id: path.split('/').pop(), revision: body.expected_revision + 1,
          storagePosture: 'EOS_ENCRYPTED_HISTORY' },
      }));
      const thread = await createWilsyAIConversationThread({
        title: 'Retention', workspace: 'Projects',
      });
      expect(thread.storagePosture).toBe('EOS_ENCRYPTED_HISTORY');
      await expect(deleteWilsyAIConversationThread(thread.id)).rejects.toThrow();
      expect(getCachedThreads()).toHaveLength(1);
    });
  });

  describe('cache lifecycle and integrity', () => {
    it('clears only the same-session cache', async () => {
      await createWilsyAIConversationThread({ title: 'Temporary' });
      expect(getCachedThreads()).toHaveLength(1);

      const result = await clearWilsyAIConversationThreads();
      expect(result).toEqual([]);
      expect(getCachedThreads()).toEqual([]);
      expect(await loadWilsyAIConversationThreads()).toEqual([]);
    });

    it('sync re-reads the same-session cache without creating durable history', async () => {
      const thread = await createWilsyAIConversationThread({ title: 'Sync me' });
      const synced = await syncThreads();

      expect(synced).toHaveLength(1);
      expect(synced[0].id).toBe(thread.id);
      expect(synced[0].storagePosture).toBe('SESSION_ONLY');
    });

    it('accepts a freshly sealed thread and rejects cryptographic tampering', async () => {
      const thread = await createWilsyAIConversationThread({ title: 'Integrity' });
      expect(await verifyThreadIntegrity(thread)).toBe(true);

      const tampered = { ...thread, title: 'Tampered title' };
      expect(await verifyThreadIntegrity(tampered)).toBe(false);
    });

    it('keeps compatibility for unsealed legacy session records without elevating authority', async () => {
      expect(await verifyThreadIntegrity({ id: 'legacy', title: 'Legacy' })).toBe(true);
    });
  });
});

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — Conversation History v5.6.1-PRINCIPAL-REHYDRATION-REFUSAL-CERT
 * ═══════════════════════════════════════════════════════════════════════════════
 * ARTIFACT: client/tests/client/wilsyAIConversationHistoryEngine.test.js
 * VERSION: v5.6.1-PRINCIPAL-REHYDRATION-REFUSAL-CERT
 * AUTHORITY BOUNDARY: synthetic tests only; EOS source and IAM are independent
 * TENANT POSTURE: tenant identifiers partition presentation context but grant no access
 * DURABLE HISTORY AUTHORITY: Python EOS authenticated encrypted history; tests use mock transport only
 * LEGAL AUTHORITY: none
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * FAIL-CLOSED POSTURE: unknown thread identities reject; integrity tampering rejects
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
