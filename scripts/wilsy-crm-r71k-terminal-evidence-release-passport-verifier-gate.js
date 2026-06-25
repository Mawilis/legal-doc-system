/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71K-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-RELEASE-PASSPORT-VERIFIER-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_VERIFIER_VERSION',
  'verifyLeadSearchRegulatorInvestorTerminalEvidenceReleasePassport',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_VERIFIED',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_VERIFIER',
  'verificationMatrix',
  'signerVerification',
  'channelVerification',
  'verificationSummary',
  'releaseSeal',
  'sourcePassportSummary',
  'passport_ready',
  'release_decision_go',
  'signoffs_go',
  'protected_boundaries_intact',
  'json_only_no_filesystem',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71K_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_VERIFIER_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-release-passport/verify/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-passport/verify/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-passport/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-readiness/latest',
  'R71K_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_VERIFIER_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71K terminal evidence release passport verifier gate.
 * @collaboration CRM regulator evidence gates, release passport API, release passport verifier API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71K terminal evidence release passport verifier contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71K gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence release passport verifier posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71K gate blocked ${label}`);
  }
};

/**
 * @function runR71KTerminalEvidenceReleasePassportVerifierGate
 * @description Validates R71K terminal regulator/investor evidence release passport verifier service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71J release passport.
 */
const runR71KTerminalEvidenceReleasePassportVerifierGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE RELEASE PASSPORT VERIFIER GATE');
  console.log(' - R71K release passport verifier authority present');
  console.log(' - R71J release passport and R71I release readiness source routes anchored');
  console.log(' - verification matrix/signers/channels/seal posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71KTerminalEvidenceReleasePassportVerifierGate();
