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
  'wilsyAIDynamicSuggestionEngine.js',
);

/**
 * @function loadWilsyDynamicSuggestionEngineExports
 * @description Loads the browser ESM suggestion engine into a CommonJS VM for local proof harness execution.
 * @returns {Object} Engine exports.
 * @collaboration Wilsy AI dynamic suggestion engine, proof harness, source isolation, and Node validation.
 */
function loadWilsyDynamicSuggestionEngineExports() {
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
  WILSY_AI_SUGGESTION_MEMORY_KEY,
  buildWilsyDynamicSuggestions,
  recordWilsyAISuggestionUsage,
  resolveWilsyAIConversationTitle,
  resolveWilsySuggestionWorkspace,
  resolveWilsySuggestionMemory,
  saveWilsySuggestionMemory,
};`,
    sandbox,
    { filename: ENGINE_PATH },
  );

  return sandbox.module.exports;
}

/**
 * @function assertWilsyHarnessCondition
 * @description Throws a proof error when a dynamic suggestion engine condition fails.
 * @param {boolean} condition - Condition to assert.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Wilsy AI proof harness, dynamic suggestion validation, and controlled regression safety.
 */
function assertWilsyHarnessCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

/**
 * @function runWilsyAIDynamicSuggestionEngineProofHarness
 * @description Proves six suggestions, non-repetition, typeahead behavior, dynamic workspace naming, usage recording, and context titles.
 * @returns {void}
 * @collaboration Wilsy AI dynamic suggestion engine, Node proof harness, model growth governance, and operator UX validation.
 */
function runWilsyAIDynamicSuggestionEngineProofHarness() {
  const engine = loadWilsyDynamicSuggestionEngineExports();
  const storageMap = new Map();
  const storage = {
    getItem: (key) => storageMap.get(key) || null,
    setItem: (key, value) => storageMap.set(key, value),
  };
  const model = {
    workspace: 'CRM Setup',
    commandTokens: [
      { label: 'Trace authority route', route: '/crm/setup/authority' },
      { label: 'Bind evidence anchors', route: '/crm/setup/evidence' },
      { label: 'Judge release route', route: '/crm/setup/release' },
      { label: 'Inspect queue drift', route: '/crm/setup/queue' },
    ],
    sourceTrace: [{ label: 'Setup packet' }, { label: 'Approval ledger' }],
    evidenceAnchors: [{ label: 'Role proof' }, { label: 'Release receipt' }],
    telemetryPacks: [{ label: 'Queue hygiene' }],
  };

  const first = engine.buildWilsyDynamicSuggestions({
    model,
    context: { workspace: 'CRM Setup' },
    refreshKey: 101,
    storage,
  });
  const second = engine.buildWilsyDynamicSuggestions({
    model,
    context: { workspace: 'CRM Setup' },
    refreshKey: 202,
    storage,
  });
  const typed = engine.buildWilsyDynamicSuggestions({
    model,
    context: { workspace: 'CRM Setup' },
    promptText: 'authority approval blocker',
    refreshKey: 303,
    persistExposure: false,
    storage,
  });
  const otherWorkspace = engine.buildWilsyDynamicSuggestions({
    model: { workspace: 'Revenue Desk' },
    context: { workspace: 'Revenue Desk' },
    refreshKey: 404,
    persistExposure: false,
    storage,
  });
  const title = engine.resolveWilsyAIConversationTitle({
    workspace: 'CRM Setup',
    promptText: 'Walk me through the CRM Setup authority path',
  });

  engine.recordWilsyAISuggestionUsage(first[0], storage);
  const memory = engine.resolveWilsySuggestionMemory(storage);

  assertWilsyHarnessCondition(first.length === 6, 'first suggestion set must contain six suggestions');
  assertWilsyHarnessCondition(second.length === 6, 'second suggestion set must contain six suggestions');
  assertWilsyHarnessCondition(typed.length === 6, 'typed suggestion set must contain six suggestions');
  assertWilsyHarnessCondition(
    first.map((item) => item.label).join('|') !== second.map((item) => item.label).join('|'),
    'suggestions must not repeat same order after refresh',
  );
  assertWilsyHarnessCondition(
    typed.some((item) => /authority approval blocker|blocker|candidate/i.test(`${item.label} ${item.prompt}`)),
    'typed intent must influence suggestions',
  );
  assertWilsyHarnessCondition(
    otherWorkspace.some((item) => /Revenue Desk/i.test(`${item.label} ${item.prompt}`)),
    'workspace label must be dynamic',
  );
  assertWilsyHarnessCondition(
    /CRM Setup ·/.test(title) && !/Current workspace/i.test(title),
    'conversation title must come from prompt context',
  );
  assertWilsyHarnessCondition(
    Object.keys(memory.usage || {}).length >= 1,
    'usage memory must record selected suggestion',
  );

  console.log('[WILSY AI DYNAMIC SUGGESTION ENGINE PROOF PASS]', {
    first: first.map((item) => item.label),
    second: second.map((item) => item.label),
    typed: typed.slice(0, 3).map((item) => item.label),
    title,
    usageKeys: Object.keys(memory.usage || {}),
  });
}

runWilsyAIDynamicSuggestionEngineProofHarness();
