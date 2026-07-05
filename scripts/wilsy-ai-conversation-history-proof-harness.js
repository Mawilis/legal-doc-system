/* eslint-disable */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ENGINE_PATH = path.join(
  __dirname,
  '..',
  'client',
  'src',
  'components',
  'intelligence',
  'wilsyAIConversationHistoryEngine.js',
);

/**
 * @function loadWilsyAIConversationHistoryEngineExports
 * @description Loads the browser ESM conversation history engine into a CommonJS VM proof harness.
 * @returns {Object} Engine exports.
 * @collaboration Wilsy AI conversation history engine, Node proof harness, local storage adapter, and regression safety.
 */
function loadWilsyAIConversationHistoryEngineExports() {
  const source = fs
    .readFileSync(ENGINE_PATH, 'utf8')
    .replace(/export const /g, 'const ')
    .replace(/export function /g, 'function ');

  const sandbox = {
    console,
    Date,
    JSON,
    Math,
    Object,
    RegExp,
    String,
    Array,
    Number,
    module: { exports: {} },
    exports: {},
    window: undefined,
  };

  vm.runInNewContext(
    `${source}
module.exports = {
  WILSY_AI_CONVERSATION_HISTORY_KEY,
  createWilsyAIConversationThread,
  persistWilsyAIConversationTurn,
  loadWilsyAIConversationThreads,
  saveWilsyAIConversationThreads,
  clearWilsyAIConversationThreads,
  resolveWilsyChatHistoryTitle,
  resolveWilsyAIConversationWorkspace,
};`,
    sandbox,
    { filename: ENGINE_PATH },
  );

  return sandbox.module.exports;
}

/**
 * @function assertWilsyConversationHarnessCondition
 * @description Throws a proof error when a conversation history contract fails.
 * @param {boolean} condition - Condition to assert.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Wilsy AI conversation history proof, contextual title validation, selection safety, and clear-history verification.
 */
function assertWilsyConversationHarnessCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

/**
 * @function runWilsyAIConversationHistoryProofHarness
 * @description Proves chat naming, previous history loading, active-thread updates, and clear-history behavior.
 * @returns {void}
 * @collaboration Wilsy AI named chat history, operator continuity, context-aware titles, and local privacy controls.
 */
function runWilsyAIConversationHistoryProofHarness() {
  const engine = loadWilsyAIConversationHistoryEngineExports();
  const storageMap = new Map();
  const storage = {
    getItem: (key) => storageMap.get(key) || null,
    setItem: (key, value) => storageMap.set(key, value),
    removeItem: (key) => storageMap.delete(key),
  };

  const first = engine.persistWilsyAIConversationTurn({
    workspace: 'CRM Setup',
    promptText: 'Walk me through the CRM Setup authority path',
    answerText: 'Authority requires separate reviewer, approver, release owner, and mutation owner.',
    intent: 'authority_graph',
    storage,
  });

  const second = engine.persistWilsyAIConversationTurn({
    activeThreadId: first.activeThreadId,
    threads: first.threads,
    workspace: 'CRM Setup',
    promptText: 'Show the evidence gaps before setup moves',
    answerText: 'Role proof and release receipt are still missing.',
    intent: 'evidence_checklist',
    storage,
  });

  const third = engine.persistWilsyAIConversationTurn({
    workspace: 'Revenue Desk',
    promptText: 'Prepare the revenue handover brief',
    answerText: 'Revenue Desk handover requires owner, risk, and proof gap.',
    intent: 'handover_brief',
    storage,
  });

  const loaded = engine.loadWilsyAIConversationThreads(storage);
  const cleared = engine.clearWilsyAIConversationThreads(storage);
  const afterClear = engine.loadWilsyAIConversationThreads(storage);

  assertWilsyConversationHarnessCondition(first.threads.length === 1, 'first turn must create one thread');
  assertWilsyConversationHarnessCondition(second.threads.length === 1, 'second turn must update active thread, not create duplicate');
  assertWilsyConversationHarnessCondition(third.threads.length === 2, 'third workspace must create a second named thread');
  assertWilsyConversationHarnessCondition(/CRM Setup ·/.test(first.thread.title), 'first title must include CRM Setup context');
  assertWilsyConversationHarnessCondition(/authority path/i.test(first.thread.title), 'first title must include prompt context');
  assertWilsyConversationHarnessCondition(/Revenue Desk ·/.test(third.thread.title), 'third title must include Revenue Desk context');
  assertWilsyConversationHarnessCondition(loaded.length === 2, 'loaded history must show two named chats');
  assertWilsyConversationHarnessCondition(cleared.length === 0 && afterClear.length === 0, 'clear history must remove all local chats');

  console.log('[WILSY AI CONVERSATION HISTORY PROOF PASS]', {
    titles: loaded.map((thread) => thread.title),
    activeThreadId: second.activeThreadId,
    cleared: afterClear.length,
  });
}

runWilsyAIConversationHistoryProofHarness();
