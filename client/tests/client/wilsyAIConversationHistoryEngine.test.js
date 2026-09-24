/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — AI Conversation History Engine Session-Bound Certificate
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/tests/client/wilsyAIConversationHistoryEngine.test.js
 * Version:        v5.4.2-SESSION-BOUND-LEGAL-HISTORY-CERT
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Direct certificate for transient same-session conversation
 *                 history. No remote history route, durable persistence, legal
 *                 authority, tenant authority, or financial authority is implied.
 * Classification: Production Test Artifact — Institutional Contract
 *
 * Change Log:
 *   2026-09-24 v5.4.2-SESSION-BOUND-LEGAL-HISTORY-CERT — Replaced retired backend-history assumptions with
 *     direct session-memory, cache-integrity, fail-closed, and no-network proofs.
 *   2026-08-05 v5.1.1-KENNEL-PHASE5 — Fixed async integrity checks.
 *   2026-08-05 v5.1.0-KENNEL-PHASE5 — Initial creation.
 *
 * Certification Seal: PRODUCTION_READY_v5.4.2-SESSION-BOUND-LEGAL-HISTORY-CERT
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { readFileSync } from 'node:fs';
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
} from '../../src/components/intelligence/wilsyAIConversationHistoryEngine.js';

describe('Wilsy AI Conversation History Engine — session-bound authority', () => {
  beforeEach(async () => {
    window.__WILSY_ACTIVE_TENANT__ = { tenantId: 'TEST_TENANT' };
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

  describe('session-only transport boundary', () => {
    it('contains no retired remote conversation route or api transport dependency', () => {
      const source = readFileSync(
        `${process.cwd()}/src/components/intelligence/wilsyAIConversationHistoryEngine.js`,
        'utf8',
      );
      expect(source).not.toContain('/api/ai/conversations');
      expect(source).not.toMatch(/import\s+api\s+from/);
      expect(source).not.toMatch(/\bapi\.(?:get|post|put|delete|patch)\s*\(/);
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
 * INSTITUTIONAL CERTIFICATION SEAL — Conversation History v5.4.2-SESSION-BOUND-LEGAL-HISTORY-CERT
 * ═══════════════════════════════════════════════════════════════════════════════
 * ARTIFACT: client/tests/client/wilsyAIConversationHistoryEngine.test.js
 * VERSION: v5.4.2-SESSION-BOUND-LEGAL-HISTORY-CERT
 * AUTHORITY BOUNDARY: test certificate only; transient browser session memory
 * TENANT POSTURE: tenant identifiers partition presentation context but grant no access
 * DURABLE HISTORY AUTHORITY: none; no remote history route is assumed or probed
 * LEGAL AUTHORITY: none
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * FAIL-CLOSED POSTURE: unknown thread identities reject; integrity tampering rejects
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ═══════════════════════════════════════════════════════════════════════════════
 */
