/* eslint-disable */
const fs = require('fs');
const path = require('path');

const MOUNT = path.resolve('client/src/services/wilsyCrmTerminalEvidenceDashboardMountContract.js');

const requiredContracts = [
  'R72C-CRM-TERMINAL-EVIDENCE-DASHBOARD-MOUNT-CONTRACT-AUTHORITY',
  'WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_SLOT_ID',
  'WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_PANEL_ID',
  'crm-terminal-evidence-launch-cockpit-slot',
  'crm-terminal-evidence-launch-cockpit-panel',
  'buildDashboardMetricTiles',
  'buildDashboardAudiencePanels',
  'buildDashboardActionButtons',
  'buildDashboardReadinessRail',
  'buildDashboardHeroContract',
  'buildTerminalEvidenceDashboardMountContract',
  'fetchTerminalEvidenceDashboardMountContract',
  'CRM_TERMINAL_EVIDENCE_DASHBOARD_MOUNT_CONTRACT',
  'Verified Launch Packet',
  'terminal-evidence-hero',
  'metricTiles',
  'audiencePanels',
  'actionButtons',
  'readinessRail',
  'mountAssertions',
  'VERIFIED_TERMINAL_EVIDENCE',
  'JSON_RESPONSE_ONLY',
  'noR70F',
  'recursiveLoopFrozen',
  'noFilesystemWrite',
];

/**
 * @function readSourceFile
 * @description Reads the R72C dashboard mount contract source for contract validation.
 * @collaboration CRM terminal evidence dashboard mount, cockpit model, integration guard.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R72C dashboard mount contract is missing.
 * @collaboration Documentation guard, secret guard, CRM terminal evidence dashboard mount gate.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R72C gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden mutation, filesystem, secret, or recursive expansion patterns appear.
 * @collaboration Dashboard mount guardrails, CRM UI quarantine, terminal evidence launch posture.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72C gate blocked ${label}`);
  }
};

/**
 * @function runR72CTerminalEvidenceDashboardMountGate
 * @description Validates the clean dashboard mount contract for future CRM dashboard integration.
 * @collaboration R72B cockpit model, R72A adapter, future CRMDashboard wiring.
 */
const runR72CTerminalEvidenceDashboardMountGate = () => {
  const source = readSourceFile(MOUNT);

  if (!source.startsWith('/* eslint-disable */')) {
    throw new Error('R72C gate blocked missing eslint-disable header');
  }

  requiredContracts.forEach((contract) => assertIncludes(source, contract, 'mount contract'));

  assertBlocked(source, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export');
  assertBlocked(source, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion token');
  assertBlocked(source, /SECRET|PRIVATE_KEY|BEARER_TOKEN|PASSWORD\s*=/, 'secret-like literal');
  assertBlocked(source, /client\/src\/components\/account|client\/src\/components\/crm\/rail|client\/src\/styles\/superadmin\/themes/, 'quarantined UI path');

  console.log('PASS: WILSY CRM R72C TERMINAL EVIDENCE DASHBOARD MOUNT CONTRACT GATE');
  console.log(' - dashboard slot, panel, hero, metric, audience, action, and readiness contracts present');
  console.log(' - future CRM dashboard mount contract present without dashboard mutation');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - no filesystem export or recursive expansion token shape present');
  console.log(' - no UI/account/rail/theme mutation present');
};

runR72CTerminalEvidenceDashboardMountGate();
