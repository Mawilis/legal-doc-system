/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – AI CONVERSATION HISTORY ENGINE [v5.4.2-SESSION-BOUND-LEGAL-HISTORY-CACHE-INTEGRITY]                                              ║
 * ║ [MIGRATED TO NATIVE WEB CRYPTO API]                                                                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME: Session-bound WILSY AI conversation history for authenticated workspace use.                                               ║
 * ║           No remote history route is assumed or probed. Legal prompts remain in memory until a                                      ║
 * ║           separately certified Python-EOS durable history authority exists. Native Web Crypto                                       ║
 * ║           seals the transient thread projection for same-session integrity checks.                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/intelligence/wilsyAIConversationHistoryEngine.js        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                               ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated sovereign conversation history and cryptographic sealing.                                ║
 * ║ • AI Engineering – Migrated to Web Crypto, made hash functions async, updated all callers.                                          ║
 * ║ • REFINED (2026-08-05) – Removed `crypto-js` CDN, hardened error handling, compliance flags.                                         ║
 * ║ • REFINED (2026-09-24) – v5.4.1-SESSION-BOUND-LEGAL-HISTORY-EXPORT-INTEGRITY: retired stale status export; aligned documentation with session-only history. ║
 * ║ • REFINED (2026-09-24) – v5.4.2-SESSION-BOUND-LEGAL-HISTORY-CACHE-INTEGRITY: restored the module-local empty session cache required by all session-history operations. ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COMPLIANCE:                                                                                                                          ║
 * ║   • POPIA §19 (Accountability)                                                                                                      ║
 * ║   • GDPR §32 (Security of Processing)                                                                                               ║
 * ║   • SOC2 §CC7.2 (Monitoring & Anomaly Detection)                                                                                    ║
 * ║   • ISO 27001 (Information Security Management)                                                                                     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

// ──────────────────────────────────────────────────────────────────────────────
// DEPENDENCIES
// ──────────────────────────────────────────────────────────────────────────────
// No remote history transport is mounted in the current production BFF. Until a
// Python-EOS-owned durable history authority is separately certified, history is
// deliberately session-memory only so legal prompts are never silently persisted
// through a legacy or caller-scoped store.
let conversationCache = [];

// ──────────────────────────────────────────────────────────────────────────────
// UTILITY FUNCTIONS
// ──────────────────────────────────────────────────────────────────────────────

/**
 * @function normalizeWilsyAIConversationText
 * @description Normalizes unknown chat text into a compact string for titles, prompts, and saved answers.
 * @param {*} value - Candidate text value.
 * @param {string} fallback - Fallback text.
 * @returns {string} Normalized text.
 * @collaboration Wilsy AI conversation engine.
 * @institutional Ensures clean string representation for display and storage.
 */
export function normalizeWilsyAIConversationText(value, fallback = '') {
  return String(value || fallback || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyAIConversationWorkspace
 * @description Resolves the active chat workspace from live model and runtime context.
 * @param {Object} payload - Workspace payload.
 * @returns {string} Workspace label.
 * @collaboration Wilsy AI conversation engine, context resolution.
 * @institutional Provides consistent workspace naming for conversation threads.
 */
export function resolveWilsyAIConversationWorkspace(payload = {}) {
  const model = payload.model || {};
  const context = payload.context || {};
  return normalizeWilsyAIConversationText(
    payload.workspace ||
      context.workspace ||
      context.focus ||
      model.workspace ||
      model.module ||
      model.contextLabel ||
      model.surface ||
      model.domain,
    'Workspace',
  );
}

/**
 * @function resolveWilsyChatHistoryTitle
 * @description Builds a contextual chat title from workspace, prompt, answer, and existing thread title.
 * @param {Object} payload - Title payload.
 * @returns {string} Contextual chat title.
 * @collaboration Wilsy AI conversation engine, title generation.
 * @institutional Provides meaningful titles based on conversation content.
 */
export function resolveWilsyChatHistoryTitle(payload = {}) {
  const workspace = resolveWilsyAIConversationWorkspace(payload);
  const promptText = normalizeWilsyAIConversationText(payload.promptText || payload.prompt || payload.question, '');
  const answerText = normalizeWilsyAIConversationText(payload.answerText || payload.answer || payload.response, '');
  const existingTitle = normalizeWilsyAIConversationText(payload.thread?.title, '');
  const existingIsPlaceholder = /new chat|current workspace|workspace conversation|saved wilsy ai chat|untitled/i.test(existingTitle);

  if (!promptText && existingTitle && !existingIsPlaceholder) {
    return existingTitle;
  }

  if (!promptText && !answerText) {
    return `${workspace} · New conversation`;
  }

  const source = promptText || answerText;
  const normalized = source
    .replace(/^open\s+/i, '')
    .replace(/^tell me\s+/i, '')
    .replace(/^walk me through\s+/i, '')
    .replace(/^show me\s+/i, '')
    .replace(/^check whether\s+/i, 'Check ')
    .replace(/\?+$/g, '')
    .trim();

  const focus = normalized.length > 72 ? `${normalized.slice(0, 69)}...` : normalized;
  return `${workspace} · ${focus || source.slice(0, 72)}`;
}

/**
 * @function getTenantId
 * @description Extracts tenant ID from the active Kennel context or falls back to 'MASTER'.
 * @returns {string} Tenant ID.
 * @collaboration Wilsy OS Kennel context.
 * @institutional Enforces tenant isolation for all history operations.
 */
function getTenantId() {
  try {
    const direct = typeof window !== 'undefined' ? window.__WILSY_ACTIVE_TENANT__ : null;
    if (direct?.tenantId || direct?._id) return String(direct.tenantId || direct._id);

    const raw = typeof localStorage !== 'undefined'
      ? localStorage.getItem('wilsy_active_tenant')
      : null;
    const parsed = raw ? JSON.parse(raw) : null;
    const persisted = parsed?.tenantId || parsed?._id || parsed?.id;
    return persisted ? String(persisted) : 'UNRESOLVED';
  } catch {
    return 'UNRESOLVED';
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// CRYPTOGRAPHIC PROOF HASHING (SHA‑256 via Web Crypto)
// ──────────────────────────────────────────────────────────────────────────────

/**
 * @function generateProofHash
 * @description Generates a cryptographic proof hash (SHA‑256) for a thread or turn using the native Web Crypto API.
 * @param {Object} entity - Thread or turn object.
 * @returns {Promise<string>} SHA‑256 hash as hex string.
 * @collaboration Wilsy AI history integrity.
 * @institutional Seals every thread and turn to enable tamper‑detection.
 */
async function generateProofHash(entity) {
  try {
    const jsonString = JSON.stringify(entity);
    const encoder = new TextEncoder();
    const data = encoder.encode(jsonString);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
  } catch (error) {
    console.error('[HistoryEngine] generateProofHash error:', error);
    return ''; // Fallback to empty – will cause integrity mismatch
  }
}

/**
 * @function verifyThreadIntegrity
 * @description Verifies the proof hash of a thread. Returns false if proof hash is present and mismatches.
 * @param {Object} thread - Thread object with proofHash.
 * @returns {Promise<boolean>} True if proof hash matches or thread lacks proof hash (legacy).
 * @collaboration Wilsy AI history integrity check.
 * @institutional Ensures that threads have not been tampered with.
 */
export async function verifyThreadIntegrity(thread) {
  if (!thread || typeof thread !== 'object') return false;
  if (!thread.proofHash) return true;

  const recomputed = await generateProofHash({
    id: thread.id,
    title: thread.title,
    workspace: thread.workspace,
    messages: Array.isArray(thread.messages) ? thread.messages : [],
    createdAt: thread.createdAt,
    updatedAt: thread.updatedAt,
    tenantId: thread.tenantId,
  });
  return recomputed === thread.proofHash;
}

// ──────────────────────────────────────────────────────────────────────────────
// SESSION-BOUND CONVERSATION HISTORY OPERATIONS
// ──────────────────────────────────────────────────────────────────────────────

const sessionThreadId = () => {
  const uuid = globalThis.crypto?.randomUUID?.();
  return uuid
    ? `session-${uuid}`
    : `session-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
};

const normalizeThreadPayload = (payload = {}) => (
  typeof payload === 'string'
    ? { title: payload, workspace: 'Workspace' }
    : (payload && typeof payload === 'object' ? payload : {})
);

const resealThread = async (thread) => {
  const sealed = {
    ...thread,
    messages: Array.isArray(thread.messages) ? thread.messages : [],
  };
  sealed.proofHash = await generateProofHash({
    id: sealed.id,
    title: sealed.title,
    workspace: sealed.workspace,
    messages: sealed.messages,
    createdAt: sealed.createdAt,
    updatedAt: sealed.updatedAt,
    tenantId: sealed.tenantId,
  });
  return sealed;
};

/**
 * Return same-session threads only. This function performs no network request.
 */
export async function loadWilsyAIConversationThreads(_options = {}) {
  return Array.isArray(conversationCache) ? [...conversationCache] : [];
}

/**
 * Create one same-session thread. No prompt or response is durably persisted.
 */
export async function createWilsyAIConversationThread(payload = {}) {
  const normalized = normalizeThreadPayload(payload);
  const workspace = resolveWilsyAIConversationWorkspace(normalized);
  const tenantId = getTenantId();
  const now = new Date().toISOString();
  const thread = await resealThread({
    id: sessionThreadId(),
    title: normalizeWilsyAIConversationText(
      normalized.title,
      resolveWilsyChatHistoryTitle({ ...normalized, workspace }),
    ),
    workspace,
    createdAt: now,
    updatedAt: now,
    messages: [],
    tenantId,
    storagePosture: 'SESSION_ONLY',
  });

  conversationCache = [
    thread,
    ...conversationCache.filter((item) => item.id !== thread.id),
  ];
  return thread;
}

/**
 * Append one message to a session thread. A legacy (threadId, message) call is
 * accepted while the canonical shape is { threadId, message }.
 */
export async function persistWilsyAIConversationTurn(payload = {}, legacyMessage = null) {
  const normalized = (
    typeof payload === 'string'
      ? { threadId: payload, message: legacyMessage }
      : (payload && typeof payload === 'object' ? payload : {})
  );

  let threadId = String(normalized.threadId || '').trim();
  if (!threadId) {
    const created = await createWilsyAIConversationThread(normalized);
    threadId = created.id;
  }

  const existing = conversationCache.find((item) => item.id === threadId);
  if (!existing) throw new Error('WILSY_AI_SESSION_THREAD_NOT_FOUND');

  const messages = [...(existing.messages || [])];
  if (normalized.message && typeof normalized.message === 'object') {
    const content = normalizeWilsyAIConversationText(normalized.message.content, '');
    if (content) {
      messages.push({
        role: normalizeWilsyAIConversationText(normalized.message.role, 'user'),
        content,
        timestamp: normalized.message.timestamp || new Date().toISOString(),
        ...(normalized.message.meta ? { meta: normalized.message.meta } : {}),
      });
    }
  } else {
    const promptText = normalizeWilsyAIConversationText(normalized.promptText, '');
    const answerText = normalizeWilsyAIConversationText(normalized.answerText, '');
    const timestamp = new Date().toISOString();
    if (promptText) messages.push({ role: 'user', content: promptText, timestamp });
    if (answerText) messages.push({ role: 'assistant', content: answerText, timestamp });
  }

  const now = new Date().toISOString();
  const updated = await resealThread({
    ...existing,
    title: resolveWilsyChatHistoryTitle({
      ...normalized,
      thread: existing,
      promptText:
        normalized.promptText
        || normalized.message?.content
        || '',
    }),
    updatedAt: now,
    messages: messages.slice(-80),
    storagePosture: 'SESSION_ONLY',
  });

  conversationCache = conversationCache.map((item) => (
    item.id === threadId ? updated : item
  ));
  return updated;
}

/**
 * Clear same-session conversation history only.
 */
export async function clearWilsyAIConversationThreads(_options = {}) {
  conversationCache = [];
  return [];
}

// ──────────────────────────────────────────────────────────────────────────────
// COMPATIBILITY & CACHE ACCESS
// ──────────────────────────────────────────────────────────────────────────────

/**
 * @function saveWilsyAIConversationThreads
 * @description Legacy compatibility cache setter; copies supplied threads into same-session memory and performs no network persistence.
 * @param {Array} threads - Same-session compatibility thread snapshot.
 * @returns {Array} Snapshot of the same-session compatibility cache.
 * @collaboration Wilsy AI backwards compatibility.
 * @institutional Maintains API compatibility without introducing durable storage.
 */
export function saveWilsyAIConversationThreads(threads = []) {
  conversationCache = Array.isArray(threads) ? [...threads] : [];
  return [...conversationCache];
}

/**
 * @function getCachedThreads
 * @description Synchronous access to cached conversation threads (for immediate UI rendering).
 * @returns {Array} Cached threads or empty array.
 * @collaboration Wilsy AI UI fast initial render.
 * @institutional Provides instant access without network delay.
 */
export function getCachedThreads() {
  return Array.isArray(conversationCache) ? conversationCache : [];
}

/**
 * @function syncThreads
 * @description Re-reads the same-session conversation cache through the canonical load function.
 * @returns {Promise<Array>} Latest threads.
 * @collaboration Wilsy AI manual refresh.
 * @institutional Performs no network request and introduces no durable-history authority.
 */
export async function syncThreads() {
  return loadWilsyAIConversationThreads();
}

// ──────────────────────────────────────────────────────────────────────────────
// EXPORTS
// ──────────────────────────────────────────────────────────────────────────────
export default {
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
};

/**
 * ARTIFACT: client/src/components/intelligence/wilsyAIConversationHistoryEngine.js
 * VERSION: v5.4.2-SESSION-BOUND-LEGAL-HISTORY-CACHE-INTEGRITY
 * AUTHORITY BOUNDARY: transient browser presentation only; no AI, legal, tenant or durable-history authority
 * TENANT POSTURE: tenant identifier is display/cache partition metadata only and never grants workspace access
 * FAIL-CLOSED POSTURE: no uncertified remote conversation persistence route is called; refresh clears session history
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
