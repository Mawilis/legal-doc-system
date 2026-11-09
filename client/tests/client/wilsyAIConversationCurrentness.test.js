/**
 * TITLE: WILSY OS Transient Intelligence Conversation Session Currentness
 * VERSION: v1.0.0-ASYNC-SESSION-REVOCATION-TEST
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Prevents in-flight transient AI history writes from resurfacing
 *          after logout or selected tenant/capacity changes.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/wilsyAIConversationCurrentness.test.js
 * COLLABORATION / OWNERSHIP: Conversation history engine, authenticated Dock.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.0-ASYNC-SESSION-REVOCATION-TEST certifies generation
 *            invalidation across thread creation, turn persistence and reset.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic prompts, transient memory only.
 * TENANT BOUNDARY: Conversation generation represents one session at a time.
 * AUTHORITY BOUNDARY: No browser cache confers EOS identity or advisory rights.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import { beforeEach, describe, expect, it } from 'vitest';
import {
  resetWilsyAIConversationSession,
  loadWilsyAIConversationThreads,
  createWilsyAIConversationThread,
  persistWilsyAIConversationTurn,
} from '../../src/components/intelligence/wilsyAIConversationHistoryEngine.js';

beforeEach(() => {
  resetWilsyAIConversationSession();
});

describe('session-only Intelligence Dock memory currentness', () => {
  it('clears old-thread data when the authenticated session is revoked', async () => {
    const thread = await createWilsyAIConversationThread({
      title: 'Synthetic case review',
      workspace: 'WILSY OS',
    });
    await persistWilsyAIConversationTurn({
      threadId: thread.id,
      message: { role: 'user', content: 'Synthetic confidential question' },
    });
    expect((await loadWilsyAIConversationThreads())[0].messages).toHaveLength(1);

    resetWilsyAIConversationSession();
    expect(await loadWilsyAIConversationThreads()).toEqual([]);
  });

  it('never adds a newly created thread after a session reset races its proof hash', async () => {
    const pending = createWilsyAIConversationThread({
      title: 'Obsolete session thread',
      workspace: 'WILSY OS',
    });
    resetWilsyAIConversationSession();

    await expect(pending).rejects.toThrow('WILSY_AI_CONVERSATION_SESSION_SUPERSEDED');
    expect(await loadWilsyAIConversationThreads()).toEqual([]);
  });

  it('never appends an old-session operator turn after a generation change', async () => {
    const thread = await createWilsyAIConversationThread({
      title: 'Obsolete turn target',
      workspace: 'WILSY OS',
    });
    const pending = persistWilsyAIConversationTurn({
      threadId: thread.id,
      message: { role: 'assistant', content: 'Synthetic stale response' },
    });
    resetWilsyAIConversationSession();

    await expect(pending).rejects.toThrow('WILSY_AI_CONVERSATION_SESSION_SUPERSEDED');
    expect(await loadWilsyAIConversationThreads()).toEqual([]);
  });
});

/*
 * ARTIFACT: wilsyAIConversationCurrentness.test.js
 * VERSION: v1.0.0-ASYNC-SESSION-REVOCATION-TEST
 * AUTHORITY BOUNDARY: Synthetic session-memory test; no durable AI truth.
 * TENANT POSTURE: Revocation clears old transient conversation state.
 * FAIL-CLOSED POSTURE: Old async turns cannot repopulate the active UI cache.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
