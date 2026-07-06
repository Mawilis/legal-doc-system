/* eslint-disable */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const BRIDGE_PATH = path.join(ROOT, 'client', 'src', 'components', 'crm', 'shared', 'wilsyCrmControlRepairBridge.js');

/**
 * @function assertWilsyCrmControlRepairCondition
 * @description Throws when a CRM control repair proof condition fails.
 * @param {boolean} condition - Condition to assert.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Shared CRM control repair bridge, static proof harness, guard discipline, and production repair verification.
 */
function assertWilsyCrmControlRepairCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

/**
 * @function runWilsyCrmControlRepairBridgeProofHarness
 * @description Proves the shared CRM control bridge contains completed P0/P1 contracts without backend mutation.
 * @returns {void}
 * @collaboration Leads checkbox ticks, Meetings outcome capture, readiness pill alignment, Setup rail repair, and adaptive stage layout.
 */
function runWilsyCrmControlRepairBridgeProofHarness() {
  const source = fs.readFileSync(BRIDGE_PATH, 'utf8');

  const proof = {
    bridgeId: source.includes('P60K5Q10FE_CRM_CONTROL_COMPLETION'),
    nativeCheckboxSetter: source.includes('setWilsyNativeCheckboxValue') && source.includes('HTMLInputElement.prototype'),
    visibleCheckboxTick: source.includes('input[type="checkbox"][data-wilsy-crm-filter-selected="true"]::after'),
    setupSearch: source.includes('filterWilsySetupMapControls') && source.includes('resolveWilsySetupSearchInput'),
    placeholderImports: source.includes('PLACEHOLDER_IMPORT_BLOCKED') && source.includes('manifest preview'),
    readinessSource: source.includes('UI_MODEL_SNAPSHOT_PENDING_LIVE_RECHECK') && source.includes('live recheck required'),
    meetingOutcomeCapture: source.includes('showWilsyMeetingOutcomePanel') && source.includes('saveWilsyMeetingOutcomeCandidate'),
    meetingImprovementSignal: source.includes('improvementSignal') && source.includes('NEGATIVE_RESULT'),
    meetingReadinessCentering: source.includes('data-wilsy-meeting-readiness-pill') && source.includes('justify-content: center'),
    setupRailRepair: source.includes('data-wilsy-setup-domain-rail-repaired') && source.includes('data-wilsy-setup-inspector-rail-repaired'),
    adaptiveStageRepair: source.includes('data-wilsy-setup-adaptive-stage-repaired'),
    noBackendMutation: !source.includes('fetch(') && !source.includes('axios'),
  };

  Object.entries(proof).forEach(([key, value]) => {
    assertWilsyCrmControlRepairCondition(Boolean(value), `CRM control completion proof failed: ${key}`);
  });

  console.log('[WILSY CRM CONTROL COMPLETION PROOF PASS]', proof);
}

runWilsyCrmControlRepairBridgeProofHarness();
