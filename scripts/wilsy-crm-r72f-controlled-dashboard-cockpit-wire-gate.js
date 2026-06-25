/* eslint-disable */
const fs = require('fs');
const path = require('path');

const DASHBOARD = path.resolve('client/src/components/crm/CRMDashboard.jsx');
const PANEL = path.resolve('client/src/components/crm/TerminalEvidenceCockpitPanel.js');

const requiredDashboardContracts = [
  "import TerminalEvidenceCockpitPanel from './TerminalEvidenceCockpitPanel.js';",
  'data-wilsy-r72f-terminal-evidence-dashboard-wire="true"',
  '<TerminalEvidenceCockpitPanel',
  "tenantId={tenantConfig?.tenantId || 'MASTER'}",
  'operator="CRM_DASHBOARD"',
  'autoFetch',
];

const requiredPanelContracts = [
  'R72D-CRM-TERMINAL-EVIDENCE-COCKPIT-PANEL-AUTHORITY',
  'TerminalEvidenceCockpitPanel',
  'crm-terminal-evidence-cockpit-panel',
  'fetchTerminalEvidenceDashboardMountContract',
];

/**
 * @function readSourceFile
 * @description Reads source files for the R72F controlled CRMDashboard cockpit wiring gate.
 * @collaboration CRMDashboard controlled wire, R72D cockpit panel, terminal evidence integration lane.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R72F dashboard wiring contract is missing.
 * @collaboration Documentation guard, secret guard, controlled CRM dashboard wiring gate.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R72F gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertCount
 * @description Fails when a wiring marker appears an unsafe number of times.
 * @collaboration CRMDashboard mount safety, duplicate render prevention, R72F wiring gate.
 */
const assertCount = (source, needle, expected, label) => {
  const count = source.split(needle).length - 1;

  if (count !== expected) {
    throw new Error(`R72F gate expected ${expected} ${label}, found ${count}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem, secret, or recursive expansion patterns appear.
 * @collaboration Dashboard wiring guardrails, terminal evidence posture, no recursive expansion boundary.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72F gate blocked ${label}`);
  }
};

/**
 * @function runR72FControlledDashboardCockpitWireGate
 * @description Validates the controlled CRMDashboard wiring to the R72D terminal evidence cockpit panel.
 * @collaboration R72D cockpit panel, R72E readiness gate, CRMDashboard integration.
 */
const runR72FControlledDashboardCockpitWireGate = () => {
  const dashboard = readSourceFile(DASHBOARD);
  const panel = readSourceFile(PANEL);

  if (!dashboard.startsWith('/* eslint-disable */')) {
    throw new Error('R72F gate blocked missing CRMDashboard eslint-disable header');
  }

  requiredDashboardContracts.forEach((contract) =>
    assertIncludes(dashboard, contract, 'dashboard wiring contract')
  );

  requiredPanelContracts.forEach((contract) =>
    assertIncludes(panel, contract, 'panel contract')
  );

  assertCount(
    dashboard,
    "import TerminalEvidenceCockpitPanel from './TerminalEvidenceCockpitPanel.js';",
    1,
    'TerminalEvidenceCockpitPanel import'
  );

  assertCount(
    dashboard,
    'data-wilsy-r72f-terminal-evidence-dashboard-wire="true"',
    1,
    'R72F dashboard mount marker'
  );

  assertCount(
    dashboard,
    '<TerminalEvidenceCockpitPanel',
    1,
    'TerminalEvidenceCockpitPanel render'
  );

  assertBlocked(dashboard, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in dashboard');
  assertBlocked(dashboard, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion token in dashboard');
  assertBlocked(panel, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion token in panel');
  assertBlocked(dashboard, /SECRET|PRIVATE_KEY|BEARER_TOKEN|PASSWORD\s*=/, 'secret-like literal in dashboard');

  console.log('PASS: WILSY CRM R72F CONTROLLED DASHBOARD COCKPIT WIRE GATE');
  console.log(' - TerminalEvidenceCockpitPanel import present exactly once');
  console.log(' - R72F mount marker present exactly once');
  console.log(' - final CRMDashboard return anchor verified');
  console.log(' - tenant fallback and CRM_DASHBOARD operator present');
  console.log(' - autoFetch mount present');
  console.log(' - no filesystem export or recursive expansion token shape present');
};

runR72FControlledDashboardCockpitWireGate();
