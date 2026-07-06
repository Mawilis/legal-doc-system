/* eslint-disable */

/**
 * @constant WILSY_AI_CONVERSATION_HISTORY_KEY
 * @description Local non-sensitive storage key for Wilsy AI named chat history.
 */
export const WILSY_AI_CONVERSATION_HISTORY_KEY = 'wilsy.ai.conversationHistory.v1';

/**
 * @function normalizeWilsyAIConversationText
 * @description Normalizes unknown chat text into a compact string for titles, prompts, and saved answers.
 * @param {*} value - Candidate text value.
 * @param {string} fallback - Fallback text.
 * @returns {string} Normalized text.
 * @collaboration Wilsy AI chat history, contextual title generation, local operator memory, and safe UI display.
 */
export function normalizeWilsyAIConversationText(value, fallback = '') {
  return String(value || fallback || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyAIConversationWorkspace
 * @description Resolves the active chat workspace from live model and runtime context without fixed CRM-only defaults.
 * @param {Object} payload - Workspace payload.
 * @returns {string} Workspace label.
 * @collaboration Wilsy AI chat history, CRM workspace context, live operator model, and tenant-aware conversation naming.
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
 * @collaboration Wilsy AI named chat history, previous conversation recovery, contextual prompts, and operator continuity.
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
 * @function resolveWilsyConversationRuntimeStorage
 * @description Resolves browser localStorage or a harness storage adapter.
 * @param {Storage|null} storage - Optional storage adapter.
 * @returns {Storage|null} Runtime storage.
 * @collaboration Wilsy AI chat history, local persistence, browser runtime, and Node proof harnesses.
 */
export function resolveWilsyConversationRuntimeStorage(storage = null) {
  return storage || (typeof window !== 'undefined' && window.localStorage ? window.localStorage : null);
}

/**
 * @function loadWilsyAIConversationThreads
 * @description Loads bounded Wilsy AI conversation history from local non-sensitive storage.
 * @param {Storage|null} storage - Optional storage adapter.
 * @returns {Array} Conversation thread list.
 * @collaboration Wilsy AI previous chat history, named conversations, local operator continuity, and safe runtime memory.
 */
export function loadWilsyAIConversationThreads(storage = null) {
  const runtimeStorage = resolveWilsyConversationRuntimeStorage(storage);

  if (!runtimeStorage) {
    return [];
  }

  try {
    const parsed = JSON.parse(runtimeStorage.getItem(WILSY_AI_CONVERSATION_HISTORY_KEY) || '[]');
    return Array.isArray(parsed) ? parsed.filter(Boolean).slice(0, 60) : [];
  } catch (error) {
    return [];
  }
}

/**
 * @function createWilsyAIConversationThread
 * @description Creates a new named Wilsy AI conversation thread for the current workspace context.
 * @param {Object} payload - Thread creation payload.
 * @returns {Object} New thread.
 * @collaboration Wilsy AI new chat action, contextual workspace naming, previous chat list, and operator continuity.
 */
export function createWilsyAIConversationThread(payload = {}) {
  const workspace = resolveWilsyAIConversationWorkspace(payload);
  const now = new Date().toISOString();
  const id = `wilsy-chat-${workspace}-${Date.now()}-${Math.floor(Math.random() * 100000)}`
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, '-')
    .replace(/^-+|-+$/g, '');

  return {
    id,
    title: resolveWilsyChatHistoryTitle({ ...payload, workspace }),
    workspace,
    createdAt: now,
    updatedAt: now,
    turns: [],
  };
}

/**
 * @function persistWilsyAIConversationTurn
 * @description Persists a prompt and answer into the active contextual chat thread, creating one when needed.
 * @param {Object} payload - Conversation turn payload.
 * @returns {Object} Updated active thread payload.
 * @collaboration Wilsy AI typed answers, contextual chat history, named previous conversations, and operator session recovery.
 */
export function persistWilsyAIConversationTurn(payload = {}) {
  const storage = payload.storage || null;
  const existingThreads = Array.isArray(payload.threads)
    ? payload.threads.filter(Boolean)
    : loadWilsyAIConversationThreads(storage);
  const activeThreadId = normalizeWilsyAIConversationText(payload.activeThreadId, '');
  const workspace = resolveWilsyAIConversationWorkspace(payload);
  const promptText = normalizeWilsyAIConversationText(payload.promptText || payload.prompt || payload.question, '');
  const answerText = normalizeWilsyAIConversationText(payload.answerText || payload.answer || payload.response, '');

  if (!promptText && !answerText) {
    const emptyThread = activeThreadId ? existingThreads.find((thread) => thread?.id === activeThreadId) : null;
    return {
      thread: emptyThread || null,
      threads: existingThreads,
      activeThreadId: emptyThread?.id || '',
    };
  }

  const now = new Date().toISOString();
  const threadIndex = existingThreads.findIndex((thread) => thread?.id === activeThreadId);
  const baseThread =
    threadIndex >= 0
      ? existingThreads[threadIndex]
      : createWilsyAIConversationThread({ ...payload, workspace, promptText, answerText });

  const nextThread = {
    ...baseThread,
    title: resolveWilsyChatHistoryTitle({
      ...payload,
      workspace,
      promptText,
      answerText,
      thread: baseThread,
    }),
    workspace,
    updatedAt: now,
    turns: [
      ...(Array.isArray(baseThread.turns) ? baseThread.turns : []),
      {
        promptText,
        answerText,
        intent: normalizeWilsyAIConversationText(payload.intent, ''),
        createdAt: now,
      },
    ].slice(-40),
  };

  const nextThreads =
    threadIndex >= 0
      ? [nextThread, ...existingThreads.filter((_, index) => index !== threadIndex)]
      : [nextThread, ...existingThreads];

  return {
    thread: nextThread,
    threads: saveWilsyAIConversationThreads(nextThreads, storage),
    activeThreadId: nextThread.id,
  };
}

/**
 * @function clearWilsyAIConversationThreads
 * @description Clears local Wilsy AI chat history without touching model knowledge or backend records.
 * @param {Storage|null} storage - Optional storage adapter.
 * @returns {Array} Empty history list.
 * @collaboration Wilsy AI clear history action, local operator memory, privacy cleanup, and safe browser persistence.
 */
export function clearWilsyAIConversationThreads(storage = null) {
  const runtimeStorage = resolveWilsyConversationRuntimeStorage(storage);

  if (runtimeStorage) {
    try {
      runtimeStorage.removeItem(WILSY_AI_CONVERSATION_HISTORY_KEY);
    } catch (error) {
      return [];
    }
  }

  return [];
}

/**
 * @function saveWilsyAIConversationThreads
 * @description Persists the Wilsy AI conversation thread list using the same storage posture as the history loader.
 * @param {Array} threads - Conversation thread list to persist.
 * @returns {Array} Persisted thread list.
 * @collaboration Wilsy AI conversation history, global Lead create routing, and CRM Leads draft review history.
 */
export function saveWilsyAIConversationThreads(threads = []) {
  /* P60K5Q10FG87C_CONVERSATION_HISTORY_SAVER_SINGLETON */
  const safeThreads = Array.isArray(threads) ? threads : [];

  if (typeof window === 'undefined') {
    return safeThreads;
  }

  try {
    const storageKey =
      typeof WILSY_AI_CONVERSATION_HISTORY_KEY !== 'undefined'
        ? WILSY_AI_CONVERSATION_HISTORY_KEY
        : 'wilsy.ai.conversation.threads';

    window.localStorage?.setItem?.(storageKey, JSON.stringify(safeThreads));
  } catch {
    // Conversation persistence must not block the production workspace.
  }

  return safeThreads;
}
