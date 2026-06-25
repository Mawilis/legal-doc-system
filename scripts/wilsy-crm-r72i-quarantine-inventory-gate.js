/* eslint-disable */
const { execSync } = require('child_process');

const SELF_PATH = 'scripts/wilsy-crm-r72i-quarantine-inventory-gate.js';

const expectedQuarantineStatusLines = [
  ' M .hintrc',
  ' M client/src/components/account/WilsyAccountCommandCenter.jsx',
  ' M client/src/components/account/wilsyAccountThemeTokens.js',
  ' M client/src/components/account/wilsyOperatingSkins.js',
  ' M client/src/components/crm/CRMDashboard.jsx',
  ' M client/src/components/crm/CRMDashboard.module.css',
  ' M client/src/index.css',
  ' M client/src/services/crmService.js',
  ' M server/app.js',
  ' M server/middleware/ProductionHardening.middleware.js',
  ' M server/middleware/auth.middleware.js',
  ' M server/middleware/security.js',
  '?? client/src/components/account/wilsyNebulaCommandSkin.js',
  '?? client/src/components/crm/lead/',
  '?? client/src/components/crm/rail/',
  '?? client/src/components/crm/theme/',
  '?? client/src/styles/superadmin/themes/wilsy-nebula-command.css',
  '?? scripts/wilsy-account-command-center-production-gate.js',
  '?? scripts/wilsy-crm-command-fabric-gate.js',
  '?? server/models/crm/',
  '?? server/routes/wilsyCrmIntelligenceRoutes.js',
  '?? server/routes/wilsyCrmLiveRoutes.js',
  '?? server/services/wilsyCrmIntelligenceService.js',
  '?? server/services/wilsyCrmLiveSourceService.js',
];

const laneRules = [
  {
    lane: 'config-local-hinting',
    match: (filePath) => filePath === '.hintrc',
    disposition: 'quarantine-config',
    nextAction: 'Review separately; do not blend with CRM/account/backend lanes.',
  },
  {
    lane: 'account-command-center-theme',
    match: (filePath) => filePath.startsWith('client/src/components/account/'),
    disposition: 'quarantine-account-theme',
    nextAction: 'Future account/theme lane only; not part of CRM dashboard evidence lane.',
  },
  {
    lane: 'crm-dashboard-core',
    match: (filePath) => filePath === 'client/src/components/crm/CRMDashboard.jsx',
    disposition: 'quarantine-dashboard-runtime',
    nextAction: 'Protected by R72H; only touch through a dedicated dashboard lane.',
  },
  {
    lane: 'crm-dashboard-css',
    match: (filePath) => filePath === 'client/src/components/crm/CRMDashboard.module.css',
    disposition: 'quarantine-dashboard-css',
    nextAction: 'CSS-only lane; do not mix with JSX/backend/auth lanes.',
  },
  {
    lane: 'client-global-style',
    match: (filePath) => filePath === 'client/src/index.css',
    disposition: 'quarantine-global-style',
    nextAction: 'Global style lane only; requires visual regression proof.',
  },
  {
    lane: 'crm-service-client',
    match: (filePath) => filePath === 'client/src/services/crmService.js',
    disposition: 'quarantine-client-service',
    nextAction: 'Client API/service lane; do not mix with UI chrome or auth middleware.',
  },
  {
    lane: 'crm-lead-operating-room',
    match: (filePath) => filePath.startsWith('client/src/components/crm/lead/'),
    disposition: 'quarantine-crm-lead',
    nextAction: 'Lead room lane; requires component guards and dashboard integration proof.',
  },
  {
    lane: 'crm-command-rail',
    match: (filePath) => filePath.startsWith('client/src/components/crm/rail/'),
    disposition: 'quarantine-crm-rail',
    nextAction: 'Rail lane; do not mix with dashboard CSS or auth/security.',
  },
  {
    lane: 'crm-theme-runtime',
    match: (filePath) => filePath.startsWith('client/src/components/crm/theme/'),
    disposition: 'quarantine-crm-theme',
    nextAction: 'CRM theme lane; requires account/theme compatibility proof.',
  },
  {
    lane: 'superadmin-theme-runtime',
    match: (filePath) => filePath.startsWith('client/src/styles/superadmin/themes/'),
    disposition: 'quarantine-superadmin-theme',
    nextAction: 'Superadmin theme lane; do not stage with CRM dashboard or account center.',
  },
  {
    lane: 'backend-app-shell',
    match: (filePath) => filePath === 'server/app.js',
    disposition: 'quarantine-backend-app',
    nextAction: 'Backend app lane; requires route smoke and middleware boundary proof.',
  },
  {
    lane: 'auth-security-hardening',
    match: (filePath) => filePath.startsWith('server/middleware/'),
    disposition: 'quarantine-auth-security',
    nextAction: 'Auth/security/hardening lane only; never blend with UI or CRM service lanes.',
  },
  {
    lane: 'crm-live-backend-models',
    match: (filePath) => filePath.startsWith('server/models/crm/'),
    disposition: 'quarantine-crm-backend-models',
    nextAction: 'CRM backend model lane; requires schema and tenant-isolation proof.',
  },
  {
    lane: 'crm-live-backend-routes',
    match: (filePath) => filePath.startsWith('server/routes/wilsyCrm'),
    disposition: 'quarantine-crm-backend-routes',
    nextAction: 'CRM live route lane; requires route smoke and auth boundary proof.',
  },
  {
    lane: 'crm-live-backend-services',
    match: (filePath) => filePath.startsWith('server/services/wilsyCrm'),
    disposition: 'quarantine-crm-backend-services',
    nextAction: 'CRM live service lane; requires tenant, connector, and no-secret proof.',
  },
  {
    lane: 'script-gates-command-fabric',
    match: (filePath) => filePath.startsWith('scripts/wilsy-account-command-center-production-gate.js') || filePath.startsWith('scripts/wilsy-crm-command-fabric-gate.js'),
    disposition: 'quarantine-script-gates',
    nextAction: 'Script gate lane; may be committed only with exact staged-set validation.',
  },
];

/**
 * @function readGitStatusLines
 * @description Reads git status lines while excluding this R72I gate itself.
 * @collaboration R72I quarantine inventory, dirty tree audit, staged-index safety.
 */
const readGitStatusLines = () => {
  const raw = execSync('git status --short', { encoding: 'utf8' });

  return raw
    .split(/\r?\n/)
    .filter(Boolean)
    .filter((line) => !line.endsWith(SELF_PATH));
};

/**
 * @function parseStatusLine
 * @description Parses porcelain short-status lines into status columns and file path.
 * @collaboration Git quarantine inventory, lane classification, dirty tree freeze.
 */
const parseStatusLine = (line) => {
  const indexStatus = line.slice(0, 1);
  const worktreeStatus = line.slice(1, 2);
  const filePath = line.slice(3);

  return {
    raw: line,
    indexStatus,
    worktreeStatus,
    filePath,
    staged: indexStatus !== ' ' && indexStatus !== '?',
    dirty: worktreeStatus !== ' ' || indexStatus === '?',
    untracked: indexStatus === '?' && worktreeStatus === '?',
  };
};

/**
 * @function normalizeForCompare
 * @description Sorts status lines for stable exact inventory comparison.
 * @collaboration R72I frozen inventory, drift detection, audit reproducibility.
 */
const normalizeForCompare = (lines) => [...lines].sort();

/**
 * @function assertExactStatusInventory
 * @description Fails when the current dirty tree drifts from the frozen R72I inventory.
 * @collaboration Quarantine discipline, staged-set safety, production audit trail.
 */
const assertExactStatusInventory = (actualLines) => {
  const expected = normalizeForCompare(expectedQuarantineStatusLines);
  const actual = normalizeForCompare(actualLines);

  const missing = expected.filter((line) => !actual.includes(line));
  const unexpected = actual.filter((line) => !expected.includes(line));

  if (missing.length || unexpected.length) {
    throw new Error(`R72I inventory drift detected\nmissing=${JSON.stringify(missing, null, 2)}\nunexpected=${JSON.stringify(unexpected, null, 2)}`);
  }

  return {
    expectedCount: expected.length,
    actualCount: actual.length,
    missing,
    unexpected,
  };
};

/**
 * @function classifyLane
 * @description Classifies a dirty file into exactly one quarantine lane.
 * @collaboration Lane map audit, remediation planning, no mixed-scope mutation.
 */
const classifyLane = (entry) => {
  const rule = laneRules.find((candidate) => candidate.match(entry.filePath));

  if (!rule) {
    throw new Error(`R72I inventory has no lane rule for ${entry.raw}`);
  }

  return {
    ...entry,
    lane: rule.lane,
    disposition: rule.disposition,
    nextAction: rule.nextAction,
  };
};

/**
 * @function buildLaneMap
 * @description Builds an auditable map of dirty files grouped by remediation lane.
 * @collaboration Investor-grade audit posture, controlled CRM/account/backend lane selection, quarantine proof.
 */
const buildLaneMap = (entries) => {
  const laneMap = {};

  entries.forEach((entry) => {
    const classified = classifyLane(entry);

    if (!laneMap[classified.lane]) {
      laneMap[classified.lane] = {
        lane: classified.lane,
        disposition: classified.disposition,
        nextAction: classified.nextAction,
        files: [],
      };
    }

    laneMap[classified.lane].files.push({
      path: classified.filePath,
      status: `${classified.indexStatus}${classified.worktreeStatus}`,
      staged: classified.staged,
      dirty: classified.dirty,
      untracked: classified.untracked,
    });
  });

  return laneMap;
};

/**
 * @function assertNoStagedQuarantineFiles
 * @description Fails if any dirty inventory file is staged before R72I commit.
 * @collaboration Staged-index safety, gate-only commit scope, quarantine discipline.
 */
const assertNoStagedQuarantineFiles = (entries) => {
  const staged = entries.filter((entry) => entry.staged);

  if (staged.length) {
    throw new Error(`R72I blocked staged quarantine files: ${JSON.stringify(staged.map((entry) => entry.raw), null, 2)}`);
  }

  return staged.length;
};

/**
 * @function assertRuntimeBoundary
 * @description Fails if inventory contains forbidden generated artifacts or recursive expansion token shapes.
 * @collaboration No export reports, no forbidden artifacts, no recursive expansion posture.
 */
const assertRuntimeBoundary = (lines) => {
  const blocked = lines.filter((line) =>
    /(\.bak|\.baseline|\.backup|\.orig|\.rej|\.broken|\.checkpoint|^\.local-mongo|^server\/exports|^reports|^forensic-fixes|^WILSY_)/.test(line)
  );

  if (blocked.length) {
    throw new Error(`R72I blocked bad quarantine artifacts: ${JSON.stringify(blocked, null, 2)}`);
  }

  const joined = lines.join('\n');

  if (/R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/.test(joined)) {
    throw new Error('R72I blocked recursive expansion token shape');
  }

  return {
    badArtifacts: 0,
    noR70F: true,
  };
};

/**
 * @function runR72IQuarantineInventoryGate
 * @description Freezes the current dirty worktree into an auditable lane map before choosing account/theme, CRM rail/lead/theme, backend live, or auth/security remediation lanes.
 * @collaboration R72H reconciliation seal, dirty tree quarantine, controlled Wilsy OS remediation planning.
 */
const runR72IQuarantineInventoryGate = () => {
  const statusLines = readGitStatusLines();
  const exactProof = assertExactStatusInventory(statusLines);
  const boundaryProof = assertRuntimeBoundary(statusLines);
  const parsedEntries = statusLines.map(parseStatusLine);
  const stagedCount = assertNoStagedQuarantineFiles(parsedEntries);
  const laneMap = buildLaneMap(parsedEntries);

  const orderedLanes = Object.values(laneMap)
    .map((lane) => ({
      ...lane,
      fileCount: lane.files.length,
      files: lane.files.sort((a, b) => a.path.localeCompare(b.path)),
    }))
    .sort((a, b) => a.lane.localeCompare(b.lane));

  const priorityRecommendation = [
    'account-command-center-theme',
    'crm-command-rail',
    'crm-lead-operating-room',
    'crm-live-backend-routes',
    'auth-security-hardening',
  ];

  console.log(JSON.stringify({
    gate: 'R72I_QUARANTINE_INVENTORY_VERIFIED',
    exactInventory: exactProof,
    stagedQuarantineFiles: stagedCount,
    boundary: boundaryProof,
    laneCount: orderedLanes.length,
    dirtyFileCount: parsedEntries.length,
    lanes: orderedLanes,
    priorityRecommendation,
    noMutationByGate: true,
    noFilesystemReportExport: true,
    noAccountRailThemeAuthSecurityMutation: true,
    noR70F: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY CRM R72I QUARANTINE INVENTORY GATE');
  console.log(' - current dirty tree exactly matches frozen quarantine inventory');
  console.log(' - every dirty path is mapped to one remediation lane');
  console.log(' - no quarantine file is staged');
  console.log(' - no generated report/export/bad artifact path is present');
  console.log(' - gate is terminal-output only; no filesystem report export');
};

runR72IQuarantineInventoryGate();
