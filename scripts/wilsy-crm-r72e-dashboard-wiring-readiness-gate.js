/* eslint-disable */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const DASHBOARD = path.resolve('client/src/components/crm/CRMDashboard.jsx');
const PANEL = path.resolve('client/src/components/crm/TerminalEvidenceCockpitPanel.js');
const MOUNT = path.resolve('client/src/services/wilsyCrmTerminalEvidenceDashboardMountContract.js');
const MODEL = path.resolve('client/src/services/wilsyCrmTerminalEvidenceCockpitModel.js');
const ADAPTER = path.resolve('client/src/services/wilsyCrmTerminalEvidenceLaunchService.js');

const requiredDashboardContracts = [
  '/* eslint-disable */',
  'CRMDashboard',
  'return',
];

const requiredPanelContracts = [
  'R72D-CRM-TERMINAL-EVIDENCE-COCKPIT-PANEL-AUTHORITY',
  'TerminalEvidenceCockpitPanel',
  'crm-terminal-evidence-cockpit-panel',
  'fetchTerminalEvidenceDashboardMountContract',
];

const requiredMountContracts = [
  'R72C-CRM-TERMINAL-EVIDENCE-DASHBOARD-MOUNT-CONTRACT-AUTHORITY',
  'CRM_TERMINAL_EVIDENCE_DASHBOARD_MOUNT_CONTRACT',
  'crm-terminal-evidence-launch-cockpit-slot',
];

const requiredModelContracts = [
  'R72B-CRM-TERMINAL-EVIDENCE-COCKPIT-MODEL-AUTHORITY',
  'CRM_TERMINAL_EVIDENCE_LAUNCH_COCKPIT_MODEL',
];

const requiredAdapterContracts = [
  'R72A-CRM-TERMINAL-EVIDENCE-LAUNCH-CLIENT-ADAPTER-AUTHORITY',
  '/api/crm/command/search/regulator-evidence/terminal-launch-packet/latest',
];

/**
 * @function readSourceFile
 * @description Reads a source file for the R72E dashboard wiring readiness gate.
 * @collaboration CRM dashboard wiring readiness, terminal evidence cockpit panel, guarded integration lane.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function getGitStatus
 * @description Reads short git status for a path without mutating the working tree.
 * @collaboration CRM dashboard quarantine, exact staged-set guard, R72E readiness gate.
 */
const getGitStatus = (relativePath) => {
  try {
    return execSync(`git status --short -- ${JSON.stringify(relativePath)}`, {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    }).trim();
  } catch (error) {
    throw new Error(`R72E gate failed to read git status for ${relativePath}: ${error.message}`);
  }
};

/**
 * @function assertIncludes
 * @description Fails when a required dashboard wiring readiness contract is missing.
 * @collaboration Documentation guard, secret guard, CRM dashboard wiring gate.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R72E gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem, secret, recursive, or quarantined path patterns appear.
 * @collaboration Dashboard wiring readiness, no recursive expansion posture, dirty-tree quarantine.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72E gate blocked ${label}`);
  }
};

/**
 * @function findDashboardAnchors
 * @description Finds safe candidate anchors for a future CRMDashboard mount insertion without editing the file.
 * @collaboration R72D cockpit panel, CRMDashboard future wiring, controlled UI integration.
 */
const findDashboardAnchors = (dashboardSource) => {
  const anchors = {
    hasReactImport:
      /import\s+React\b|from\s+['"]react['"]/.test(dashboardSource),
    hasDefaultExport:
      /export\s+default\s+(function\s+)?CRMDashboard|export\s+\{\s*CRMDashboard\s+as\s+default\s*\}/.test(dashboardSource) ||
      /export\s+default\s+.*CRMDashboard/.test(dashboardSource),
    hasFunction:
      /function\s+CRMDashboard\b|const\s+CRMDashboard\s*=/.test(dashboardSource),
    hasReturn:
      /\breturn\s*\(/.test(dashboardSource),
    hasPanelImport:
      /TerminalEvidenceCockpitPanel/.test(dashboardSource),
    hasPanelSlot:
      /crm-terminal-evidence-launch-cockpit-slot|crm-terminal-evidence-cockpit-panel|terminal-evidence-cockpit-panel/.test(dashboardSource),
  };

  return {
    ...anchors,
    readyForFirstWire:
      anchors.hasReactImport &&
      anchors.hasFunction &&
      anchors.hasReturn &&
      !anchors.hasPanelImport &&
      !anchors.hasPanelSlot,
    alreadyMounted:
      anchors.hasPanelImport || anchors.hasPanelSlot,
  };
};

/**
 * @function buildDashboardWiringSnippet
 * @description Returns the exact future import/render snippets that should be added only in the controlled R72F wiring step.
 * @collaboration R72D cockpit panel, R72E readiness gate, future CRMDashboard mutation pass.
 */
const buildDashboardWiringSnippet = () => ({
  importSnippet:
    "import TerminalEvidenceCockpitPanel from './TerminalEvidenceCockpitPanel.js';",
  renderSnippet:
    "<TerminalEvidenceCockpitPanel tenantId={tenantConfig?.tenantId || 'MASTER'} operator=\"CRM_DASHBOARD\" autoFetch />",
  slotId:
    'crm-terminal-evidence-launch-cockpit-slot',
  panelTestId:
    'crm-terminal-evidence-cockpit-panel',
});

/**
 * @function runR72EDashboardWiringReadinessGate
 * @description Validates readiness for future CRMDashboard wiring without mutating or staging the dashboard.
 * @collaboration R72A adapter, R72B model, R72C mount contract, R72D panel, CRMDashboard future wiring.
 */
const runR72EDashboardWiringReadinessGate = () => {
  const dashboard = readSourceFile(DASHBOARD);
  const panel = readSourceFile(PANEL);
  const mount = readSourceFile(MOUNT);
  const model = readSourceFile(MODEL);
  const adapter = readSourceFile(ADAPTER);

  requiredDashboardContracts.forEach((contract) =>
    assertIncludes(dashboard, contract, 'dashboard readiness contract')
  );
  requiredPanelContracts.forEach((contract) =>
    assertIncludes(panel, contract, 'panel contract')
  );
  requiredMountContracts.forEach((contract) =>
    assertIncludes(mount, contract, 'mount contract')
  );
  requiredModelContracts.forEach((contract) =>
    assertIncludes(model, contract, 'model contract')
  );
  requiredAdapterContracts.forEach((contract) =>
    assertIncludes(adapter, contract, 'adapter contract')
  );

  [dashboard, panel, mount, model, adapter].forEach((source) => {
    assertBlocked(source, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export');
    assertBlocked(source, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion token');
    assertBlocked(source, /SECRET|PRIVATE_KEY|BEARER_TOKEN|PASSWORD\s*=/, 'secret-like literal');
  });

  assertBlocked(panel, /client\/src\/components\/account|client\/src\/components\/crm\/rail|client\/src\/styles\/superadmin\/themes/, 'quarantined UI path in panel chain');

  const dashboardStatus = getGitStatus('client/src/components/crm/CRMDashboard.jsx');
  const anchors = findDashboardAnchors(dashboard);
  const snippet = buildDashboardWiringSnippet();

  if (!anchors.readyForFirstWire && !anchors.alreadyMounted) {
    throw new Error(
      `R72E gate blocked dashboard wiring readiness: ${JSON.stringify(anchors)}`
    );
  }

  console.log('PASS: WILSY CRM R72E DASHBOARD WIRING READINESS GATE');
  console.log(' - CRMDashboard source inspected without mutation');
  console.log(' - R72A/R72B/R72C/R72D chain verified');
  console.log(` - dashboard git status: ${dashboardStatus || 'clean'}`);
  console.log(` - readyForFirstWire: ${anchors.readyForFirstWire}`);
  console.log(` - alreadyMounted: ${anchors.alreadyMounted}`);
  console.log(` - importSnippet: ${snippet.importSnippet}`);
  console.log(` - renderSnippet: ${snippet.renderSnippet}`);
  console.log(' - no filesystem export or recursive expansion token shape present');
  console.log(' - dashboard remained unmodified by this gate');
};

runR72EDashboardWiringReadinessGate();
