/* eslint-disable */
const fs = require('fs');
const path = require('path');

const DASHBOARD = path.resolve('client/src/components/crm/CRMDashboard.jsx');

const targetObjectAnchors = [
  'renewalValue:',
  'slaStatus:',
  'lastMessageAt:',
  'trigger:',
];

/**
 * @function readSourceFile
 * @description Reads CRMDashboard source for the R72G duplicate channel key cleanup gate.
 * @collaboration CRM dashboard build hygiene, Vite warning cleanup, controlled quarantine lane.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R72G duplicate-key cleanup anchor is missing.
 * @collaboration Documentation guard, controlled CRM hygiene gate, build-warning cleanup.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R72G gate missing ${label}: ${needle}`);
  }
};

/**
 * @function countChannelKeysInTargetObject
 * @description Counts channel keys inside the target CRM display-label object that previously caused the Vite duplicate-key warning.
 * @collaboration CRMDashboard hygiene, exact duplicate-key cleanup, build warning prevention.
 */
const countChannelKeysInTargetObject = (source) => {
  const anchorIndex = source.indexOf('renewalValue:');

  if (anchorIndex < 0) {
    throw new Error('R72G gate blocked missing renewalValue anchor');
  }

  const objectStart = source.lastIndexOf('{', anchorIndex);
  const objectEnd = source.indexOf('};', anchorIndex);

  if (objectStart < 0 || objectEnd < 0) {
    throw new Error('R72G gate blocked missing target object boundary');
  }

  const window = source.slice(objectStart, objectEnd);
  const matches = window.match(/\bchannel\s*:/g);

  return matches ? matches.length : 0;
};

/**
 * @function assertBlocked
 * @description Fails when forbidden runtime filesystem or recursive expansion patterns appear in CRMDashboard.
 * @collaboration CRM dashboard hygiene, no recursive expansion posture, secret guard support.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72G gate blocked ${label}`);
  }
};

/**
 * @function runR72GDuplicateChannelKeyGate
 * @description Validates that CRMDashboard no longer has the duplicate channel key warning target.
 * @collaboration R72F dashboard cockpit wiring, Vite build hygiene, CRM dashboard production seal.
 */
const runR72GDuplicateChannelKeyGate = () => {
  const dashboard = readSourceFile(DASHBOARD);

  targetObjectAnchors.forEach((anchor) =>
    assertIncludes(dashboard, anchor, 'target object anchor')
  );

  const channelKeyCount = countChannelKeysInTargetObject(dashboard);

  if (channelKeyCount !== 1) {
    throw new Error(`R72G gate expected one channel key in target object, found ${channelKeyCount}`);
  }

  assertIncludes(
    dashboard,
    'data-wilsy-r72f-terminal-evidence-dashboard-wire="true"',
    'R72F cockpit mount marker'
  );

  assertIncludes(
    dashboard,
    "import TerminalEvidenceCockpitPanel from './TerminalEvidenceCockpitPanel.js';",
    'R72F cockpit panel import'
  );

  assertBlocked(dashboard, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export');
  assertBlocked(dashboard, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive expansion token');
  assertBlocked(dashboard, /SECRET|PRIVATE_KEY|BEARER_TOKEN|PASSWORD\s*=/, 'secret-like literal');

  console.log('PASS: WILSY CRM R72G DUPLICATE CHANNEL KEY CLEANUP GATE');
  console.log(' - target display-label object has exactly one channel key');
  console.log(' - R72F cockpit wiring remains present');
  console.log(' - no filesystem export or recursive expansion token shape present');
};

runR72GDuplicateChannelKeyGate();
