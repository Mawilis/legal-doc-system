/* eslint-disable */
const fs = require('fs');
const path = require('path');

const MODEL = path.resolve('client/src/services/wilsyCrmTerminalEvidenceCockpitModel.js');

const requiredContracts = [
  'R72B-CRM-TERMINAL-EVIDENCE-COCKPIT-MODEL-AUTHORITY',
  'WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_AUDIENCES',
  'buildTerminalEvidenceCockpitKpis',
  'buildTerminalEvidenceAudienceCards',
  'buildTerminalEvidenceCockpitActions',
  'buildTerminalEvidenceReadinessRail',
  'buildTerminalEvidenceCockpitModel',
  'fetchTerminalEvidenceCockpitModel',
  'CRM_TERMINAL_EVIDENCE_LAUNCH_COCKPIT_MODEL',
  'buyer_demo_packet',
  'board_approval_packet',
  'regulator_inspection_packet',
  'investor_diligence_packet',
  'audit_assurance_packet',
  'engineering_handoff_packet',
  'open_launch_packet',
  'open_release_brief',
  'verify_release_passport',
  'open_api_surface_registry',
  'open_cockpit_contract',
  'VERIFIED_TERMINAL_EVIDENCE',
  'JSON_RESPONSE_ONLY',
  'noR70F',
  'recursiveLoopFrozen',
  'noFilesystemWrite',
];

/**
 * @function readSourceFile
 * @description Reads the R72B cockpit model source for contract validation.
 * @collaboration CRM terminal evidence cockpit model, client adapter, integration guard.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R72B cockpit model contract is missing.
 * @collaboration Documentation guard, secret guard, CRM terminal evidence cockpit model gate.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R72B gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden mutation, filesystem, secret, or recursive expansion patterns appear.
 * @collaboration Client cockpit model guardrails, CRM UI quarantine, terminal evidence launch posture.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72B gate blocked ${label}`);
  }
};

/**
 * @function runR72BTerminalEvidenceCockpitModelGate
 * @description Validates the clean cockpit model for terminal evidence launch packet consumption.
 * @collaboration R72A client adapter, R71M launch packet API, future CRM dashboard wiring.
 */
const runR72BTerminalEvidenceCockpitModelGate = () => {
  const source = readSourceFile(MODEL);

  if (!source.startsWith('/* eslint-disable */')) {
    throw new Error('R72B gate blocked missing eslint-disable header');
  }

  requiredContracts.forEach((contract) => assertIncludes(source, contract, 'model contract'));

  assertBlocked(source, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export');
  assertBlocked(source, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion token');
  assertBlocked(source, /SECRET|PRIVATE_KEY|BEARER_TOKEN|PASSWORD\s*=/, 'secret-like literal');
  assertBlocked(source, /client\/src\/components\/account|client\/src\/components\/crm\/rail|client\/src\/styles\/superadmin\/themes/, 'quarantined UI path');

  console.log('PASS: WILSY CRM R72B TERMINAL EVIDENCE COCKPIT MODEL GATE');
  console.log(' - cockpit KPI, audience card, action, and readiness rail contracts present');
  console.log(' - launch packet artifact contracts anchored');
  console.log(' - future CRM dashboard consumption model present without dashboard mutation');
  console.log(' - no filesystem export or recursive expansion token shape present');
  console.log(' - no UI/account/rail/theme mutation present');
};

runR72BTerminalEvidenceCockpitModelGate();
