/* eslint-disable */
const fs = require('fs');
const path = require('path');

const ADAPTER = path.resolve('client/src/services/wilsyCrmTerminalEvidenceLaunchService.js');

const requiredContracts = [
  'R72A-CRM-TERMINAL-EVIDENCE-LAUNCH-CLIENT-ADAPTER-AUTHORITY',
  'WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS',
  'fetchTerminalEvidenceLaunchPacket',
  'fetchTerminalEvidenceReleaseBrief',
  'fetchTerminalEvidenceCockpitContract',
  'fetchTerminalEvidenceApiSurfaceRegistry',
  'buildTerminalEvidenceLaunchSnapshot',
  '/api/crm/command/search/regulator-evidence/terminal-launch-packet/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-brief/latest',
  '/api/crm/command/search/regulator-evidence/terminal-cockpit-contract/latest',
  '/api/crm/command/search/regulator-evidence/terminal-api-surface-registry/latest',
  'X-Tenant-Id',
  'X-Wilsy-Operator',
  'VERIFIED_TERMINAL_EVIDENCE',
  'JSON_RESPONSE_ONLY',
  'noR70F',
  'recursiveLoopFrozen',
  'noFilesystemWrite',
];

/**
 * @function readSourceFile
 * @description Reads the R72A client adapter source for contract validation.
 * @collaboration CRM terminal evidence adapter, launch packet API, client integration guard.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R72A client adapter contract is missing.
 * @collaboration Documentation guard, secret guard, CRM terminal evidence adapter gate.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R72A gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden mutation, filesystem, secret, or recursive expansion patterns appear.
 * @collaboration Client adapter guardrails, CRM UI quarantine, terminal evidence launch posture.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72A gate blocked ${label}`);
  }
};

/**
 * @function runR72ATerminalEvidenceClientAdapterGate
 * @description Validates the clean client adapter for CRM terminal evidence launch packet consumption.
 * @collaboration R71M launch packet API, CRM cockpit integration lane, client services.
 */
const runR72ATerminalEvidenceClientAdapterGate = () => {
  const source = readSourceFile(ADAPTER);

  if (!source.startsWith('/* eslint-disable */')) {
    throw new Error('R72A gate blocked missing eslint-disable header');
  }

  requiredContracts.forEach((contract) => assertIncludes(source, contract, 'adapter contract'));

  assertBlocked(source, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export');
  assertBlocked(source, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion token');
  assertBlocked(source, /SECRET|PRIVATE_KEY|BEARER_TOKEN|PASSWORD\s*=/, 'secret-like literal');
  assertBlocked(source, /client\/src\/components\/account|client\/src\/components\/crm\/rail|client\/src\/styles\/superadmin\/themes/, 'quarantined UI path');

  console.log('PASS: WILSY CRM R72A TERMINAL EVIDENCE CLIENT ADAPTER GATE');
  console.log(' - launch packet, release brief, cockpit contract, and API registry endpoints anchored');
  console.log(' - tenant/operator header contract present');
  console.log(' - cockpit snapshot contract present');
  console.log(' - no filesystem export or recursive expansion token shape present');
  console.log(' - no UI/account/rail/theme mutation present');
};

runR72ATerminalEvidenceClientAdapterGate();
