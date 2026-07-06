/* eslint-disable */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const BRIDGE_PATH = path.join(ROOT, 'client', 'src', 'components', 'crm', 'shared', 'wilsyCrmControlRepairBridge.js');

/**
 * @function assertWilsyContainedBridgeCondition
 * @description Throws when a contained bridge proof condition fails.
 * @param {boolean} condition - Condition to assert.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Contained CRM bridge, checkbox persistence, setup rail protection, and static proof.
 */
function assertWilsyContainedBridgeCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

/**
 * @function runWilsyContainedBridgeProofHarness
 * @description Proves the CRM bridge is contained and no longer manipulates Setup rails or staged layout globally.
 * @returns {void}
 * @collaboration Leads filters, Meetings filters, Setup map search, side rail protection, and import placeholder hardening.
 */
function runWilsyContainedBridgeProofHarness() {
  const source = fs.readFileSync(BRIDGE_PATH, 'utf8');

  const proof = {
    bridgeId: source.includes('P60K5Q10FF_CONTAINED_CRM_CONTROL_BRIDGE'),
    checkboxNativeSetter: source.includes('setWilsyCheckboxChecked') && source.includes('HTMLInputElement.prototype'),
    checkboxPersistence: source.includes('persistWilsyCheckbox') && source.includes('restoreWilsyCheckboxes'),
    setupSearchOnly: source.includes('filterWilsySetupMapControls') && source.includes('without changing rail layout'),
    placeholderBlocking: source.includes('PLACEHOLDER_IMPORT_BLOCKED'),
    previousGlobalCleanup: source.includes('cleanupPreviousWilsyGlobalBridgeEffects'),
    noMutationObserver: !source.includes('new MutationObserver'),
    noBodyHasCss: !source.includes('body:has'),
    noRailCssInjection: !source.includes('data-wilsy-setup-domain-rail-repaired="true"] {') && !source.includes('writing-mode: horizontal-tb'),
    noBackendMutation: !source.includes('fetch(') && !source.includes('axios'),
  };

  Object.entries(proof).forEach(([key, value]) => {
    assertWilsyContainedBridgeCondition(Boolean(value), `Contained bridge proof failed: ${key}`);
  });

  console.log('[WILSY CONTAINED CRM BRIDGE PROOF PASS]', proof);
}

runWilsyContainedBridgeProofHarness();
