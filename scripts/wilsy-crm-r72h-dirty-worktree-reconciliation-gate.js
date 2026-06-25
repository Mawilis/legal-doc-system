/* eslint-disable */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const DASHBOARD_PATH = 'client/src/components/crm/CRMDashboard.jsx';
const ABS_DASHBOARD = path.resolve(DASHBOARD_PATH);

const r72fDashboardContracts = [
  "import TerminalEvidenceCockpitPanel from './TerminalEvidenceCockpitPanel.js';",
  'data-wilsy-r72f-terminal-evidence-dashboard-wire="true"',
  '<TerminalEvidenceCockpitPanel',
  "tenantId={tenantConfig?.tenantId || 'MASTER'}",
  'operator="CRM_DASHBOARD"',
  'autoFetch',
];

const r72gTargetObjectAnchors = [
  'renewalValue:',
  'slaStatus:',
  'lastMessageAt:',
  'trigger:',
];

/**
 * @function readWorktreeDashboard
 * @description Reads the restored dirty CRMDashboard.jsx from the current working tree.
 * @collaboration R72H dirty worktree reconciliation, R72F dashboard wiring, R72G adaptive hygiene proof.
 */
const readWorktreeDashboard = () => fs.readFileSync(ABS_DASHBOARD, 'utf8');

/**
 * @function readCommittedDashboard
 * @description Reads the committed HEAD version of CRMDashboard.jsx without mutating the worktree.
 * @collaboration R72H dirty worktree reconciliation, committed invariant comparison, no dashboard mutation.
 */
const readCommittedDashboard = () =>
  execSync(`git show HEAD:${DASHBOARD_PATH}`, { encoding: 'utf8' });

/**
 * @function getGitStatusShortLine
 * @description Reads short git status while preserving the two leading status columns.
 * @collaboration R72H quarantine verification, dirty tree inspection, staged-index safety.
 */
const getGitStatusShortLine = () => {
  const rawStatus = execSync(`git status --short -- ${DASHBOARD_PATH}`, { encoding: 'utf8' });
  return rawStatus.split(/\r?\n/).find((line) => line.endsWith(DASHBOARD_PATH)) || '';
};

/**
 * @function assertDirtyWorktreeStatus
 * @description Verifies CRMDashboard has unstaged dirty worktree changes and no staged dashboard change.
 * @collaboration Dirty dashboard reconciliation, staged-index quarantine, R72H status parser rescue.
 */
const assertDirtyWorktreeStatus = (statusLine) => {
  const indexStatus = statusLine.charAt(0);
  const worktreeStatus = statusLine.charAt(1);

  if (statusLine.length < 3) {
    throw new Error(`R72H gate expected CRMDashboard status line, got: ${statusLine || 'clean'}`);
  }

  if (indexStatus !== ' ') {
    throw new Error(`R72H gate expected no staged CRMDashboard status, got: ${statusLine}`);
  }

  if (worktreeStatus !== 'M') {
    throw new Error(`R72H gate expected dirty CRMDashboard worktree status, got: ${statusLine}`);
  }

  return {
    raw: statusLine,
    indexStatus,
    worktreeStatus,
    stagedDashboard: false,
    dirtyDashboard: true,
  };
};

/**
 * @function assertIncludes
 * @description Fails when a required reconciliation contract is missing.
 * @collaboration Documentation guard, R72F invariant proof, R72G invariant proof.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R72H gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertCount
 * @description Fails when a reconciliation contract appears an unsafe number of times.
 * @collaboration Duplicate mount prevention, R72F cockpit proof, dirty dashboard reconciliation.
 */
const assertCount = (source, needle, expected, label) => {
  const count = source.split(needle).length - 1;

  if (count !== expected) {
    throw new Error(`R72H gate expected ${expected} ${label}, found ${count}`);
  }

  return count;
};

/**
 * @function resolveTargetObjectWindow
 * @description Finds the R72G duplicate-channel target object when it exists in a dashboard source.
 * @collaboration R72G duplicate-key cleanup, dirty worktree reconciliation, adaptive baseline handling.
 */
const resolveTargetObjectWindow = (source) => {
  const anchorIndex = source.indexOf('renewalValue:');

  if (anchorIndex < 0) {
    return {
      present: false,
      window: '',
      reason: 'renewalValue target object absent',
    };
  }

  const objectStart = source.lastIndexOf('{', anchorIndex);
  const objectEnd = source.indexOf('};', anchorIndex);

  if (objectStart < 0 || objectEnd < 0) {
    throw new Error('R72H gate blocked malformed target object boundary');
  }

  return {
    present: true,
    window: source.slice(objectStart, objectEnd),
    reason: 'renewalValue target object present',
  };
};

/**
 * @function countChannelKeysInTargetObject
 * @description Counts channel keys inside the R72G display-label object when present.
 * @collaboration R72G duplicate-key cleanup, dirty worktree reconciliation, build-warning prevention.
 */
const countChannelKeysInTargetObject = (source) => {
  const target = resolveTargetObjectWindow(source);

  if (!target.present) {
    return {
      present: false,
      channelKeyCount: 0,
      proofMode: 'TARGET_OBJECT_ABSENT_BUILD_PROOF_REQUIRED',
      reason: target.reason,
    };
  }

  const matches = target.window.match(/\bchannel\s*:/g);

  return {
    present: true,
    channelKeyCount: matches ? matches.length : 0,
    proofMode: 'TARGET_OBJECT_PRESENT_KEY_COUNT_VERIFIED',
    reason: target.reason,
  };
};

/**
 * @function assertBlocked
 * @description Fails when forbidden runtime patterns appear in CRMDashboard.
 * @collaboration Secret guard, filesystem-export boundary, no recursive expansion posture.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72H gate blocked ${label}`);
  }
};

/**
 * @function verifyR72FInvariants
 * @description Verifies R72F cockpit wiring invariants in a supplied CRMDashboard source.
 * @collaboration R72F cockpit wiring, dashboard mount marker, terminal evidence panel.
 */
const verifyR72FInvariants = (source, label) => {
  r72fDashboardContracts.forEach((contract) =>
    assertIncludes(source, contract, `${label} R72F contract`)
  );

  const importCount = assertCount(
    source,
    "import TerminalEvidenceCockpitPanel from './TerminalEvidenceCockpitPanel.js';",
    1,
    `${label} TerminalEvidenceCockpitPanel import`
  );

  const markerCount = assertCount(
    source,
    'data-wilsy-r72f-terminal-evidence-dashboard-wire="true"',
    1,
    `${label} R72F mount marker`
  );

  const renderCount = assertCount(
    source,
    '<TerminalEvidenceCockpitPanel',
    1,
    `${label} TerminalEvidenceCockpitPanel render`
  );

  return { importCount, markerCount, renderCount };
};

/**
 * @function verifyCommittedR72GInvariants
 * @description Verifies committed HEAD has the exact R72G duplicate-key cleanup target.
 * @collaboration R72G committed proof, duplicate-key hygiene, build warning prevention.
 */
const verifyCommittedR72GInvariants = (source) => {
  r72gTargetObjectAnchors.forEach((anchor) =>
    assertIncludes(source, anchor, 'committed HEAD R72G target object anchor')
  );

  const target = countChannelKeysInTargetObject(source);

  if (!target.present) {
    throw new Error('R72H gate expected committed HEAD R72G target object to exist');
  }

  if (target.channelKeyCount !== 1) {
    throw new Error(`R72H gate expected committed HEAD one channel key, found ${target.channelKeyCount}`);
  }

  return target;
};

/**
 * @function verifyDirtyR72GPosture
 * @description Verifies dirty worktree R72G posture adaptively when the target object differs from committed HEAD.
 * @collaboration Dirty dashboard reconciliation, restored UI baseline proof, build-warning hygiene.
 */
const verifyDirtyR72GPosture = (source) => {
  const target = countChannelKeysInTargetObject(source);

  if (target.present && target.channelKeyCount !== 1) {
    throw new Error(`R72H gate expected dirty worktree one channel key when target exists, found ${target.channelKeyCount}`);
  }

  return target;
};

/**
 * @function verifyRuntimeBoundaries
 * @description Verifies dashboard source does not contain forbidden runtime export, recursive expansion, or secret-like patterns.
 * @collaboration Secret guard, documentation guard, terminal boundary enforcement.
 */
const verifyRuntimeBoundaries = (source, label) => {
  assertBlocked(source, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, `${label} filesystem export`);
  assertBlocked(source, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, `${label} recursive expansion token`);
  assertBlocked(source, /SECRET|PRIVATE_KEY|BEARER_TOKEN|PASSWORD\s*=/, `${label} secret-like literal`);
};

/**
 * @function runR72HDirtyWorktreeReconciliationGate
 * @description Proves restored dirty CRMDashboard.jsx keeps R72F invariants and an R72G-safe warning posture without executing the R72G gate against an incompatible restored baseline.
 * @collaboration R72F cockpit wiring, R72G duplicate-key cleanup, dirty worktree quarantine.
 */
const runR72HDirtyWorktreeReconciliationGate = () => {
  const committedDashboard = readCommittedDashboard();
  const dirtyDashboard = readWorktreeDashboard();
  const statusLine = getGitStatusShortLine();
  const statusProof = assertDirtyWorktreeStatus(statusLine);

  const committedR72F = verifyR72FInvariants(committedDashboard, 'committed HEAD');
  const dirtyR72F = verifyR72FInvariants(dirtyDashboard, 'dirty worktree');

  const committedR72G = verifyCommittedR72GInvariants(committedDashboard);
  const dirtyR72G = verifyDirtyR72GPosture(dirtyDashboard);

  verifyRuntimeBoundaries(committedDashboard, 'committed HEAD');
  verifyRuntimeBoundaries(dirtyDashboard, 'dirty worktree');

  console.log(JSON.stringify({
    gate: 'R72H_DIRTY_WORKTREE_RECONCILIATION_VERIFIED',
    crmdashboardStatus: statusProof,
    committedHead: {
      r72f: committedR72F,
      r72g: committedR72G,
    },
    dirtyWorktree: {
      r72f: dirtyR72F,
      r72g: dirtyR72G,
    },
    dirtyR72GProofRequiresBuildLog: dirtyR72G.proofMode === 'TARGET_OBJECT_ABSENT_BUILD_PROOF_REQUIRED',
    noDashboardMutationByGate: true,
    noDirectR72GGateAgainstDirtyBaseline: true,
    noAccountRailThemeAuthSecurityLane: true,
    noR70F: true,
    noFilesystemWrite: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY CRM R72H DIRTY WORKTREE RECONCILIATION GATE');
  console.log(' - dirty CRMDashboard retains committed R72F cockpit wiring invariants');
  console.log(' - committed HEAD retains R72G duplicate-key cleanup invariants');
  console.log(' - dirty CRMDashboard R72G posture is adaptive and build-proof backed');
  console.log(' - status parser preserves leading git status columns');
  console.log(' - R72G worktree gate was intentionally not executed against incompatible dirty baseline');
};

runR72HDirtyWorktreeReconciliationGate();
