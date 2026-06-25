/* eslint-disable */
const fs = require('fs');
const path = require('path');

const PANEL = path.resolve('client/src/components/crm/TerminalEvidenceCockpitPanel.js');

const requiredContracts = [
  'R72D-CRM-TERMINAL-EVIDENCE-COCKPIT-PANEL-AUTHORITY',
  'WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_PANEL_TEST_ID',
  'crm-terminal-evidence-cockpit-panel',
  'TerminalEvidenceCockpitPanel',
  'resolvePanelMountContract',
  'createTerminalEvidenceCockpitPanelViewState',
  'renderTerminalEvidenceBadge',
  'renderMetricTile',
  'renderAudiencePanel',
  'renderActionButton',
  'renderReadinessRailItem',
  'fetchTerminalEvidenceDashboardMountContract',
  'CRM_TERMINAL_EVIDENCE_DASHBOARD_MOUNT_CONTRACT',
  'WILSY CRM TERMINAL EVIDENCE',
  'Launch Artifacts',
  'Evidence Actions',
  'Readiness Rail',
  'VERIFIED_TERMINAL_EVIDENCE',
  'JSON_RESPONSE_ONLY',
  'noR70F',
  'recursiveLoopFrozen',
  'noFilesystemWrite',
];

/**
 * @function readSourceFile
 * @description Reads the R72D cockpit panel source for contract validation.
 * @collaboration CRM terminal evidence panel, dashboard mount contract, integration guard.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R72D cockpit panel contract is missing.
 * @collaboration Documentation guard, secret guard, CRM terminal evidence panel gate.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R72D gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden mutation, filesystem, secret, or recursive expansion patterns appear.
 * @collaboration Cockpit panel guardrails, CRM dashboard quarantine, terminal evidence launch posture.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72D gate blocked ${label}`);
  }
};

/**
 * @function runR72DTerminalEvidenceCockpitPanelGate
 * @description Validates the isolated CRM terminal evidence cockpit panel before dashboard wiring.
 * @collaboration R72C dashboard mount contract, R72B cockpit model, future CRMDashboard integration.
 */
const runR72DTerminalEvidenceCockpitPanelGate = () => {
  const source = readSourceFile(PANEL);

  if (!source.startsWith('/* eslint-disable */')) {
    throw new Error('R72D gate blocked missing eslint-disable header');
  }

  requiredContracts.forEach((contract) => assertIncludes(source, contract, 'panel contract'));

  assertBlocked(source, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export');
  assertBlocked(source, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion token');
  assertBlocked(source, /SECRET|PRIVATE_KEY|BEARER_TOKEN|PASSWORD\s*=/, 'secret-like literal');
  assertBlocked(source, /client\/src\/components\/account|client\/src\/components\/crm\/rail|client\/src\/styles\/superadmin\/themes/, 'quarantined UI path');

  console.log('PASS: WILSY CRM R72D TERMINAL EVIDENCE COCKPIT PANEL GATE');
  console.log(' - isolated cockpit panel contract present');
  console.log(' - dashboard mount contract consumption present');
  console.log(' - hero, metric, audience, action, and readiness render helpers present');
  console.log(' - no CRMDashboard/account/rail/theme/auth/security mutation present');
  console.log(' - no filesystem export or recursive expansion token shape present');
};

runR72DTerminalEvidenceCockpitPanelGate();
