/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71J-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-RELEASE-PASSPORT-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceReleasePassport',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT',
  'passportIdentity',
  'signoffMatrix',
  'releasePassportSections',
  'consumptionMap',
  'finalAssertions',
  'sourceReleaseReadinessSummary',
  'TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT',
  'releaseDecision',
  'GO',
  'scorePerfect',
  'allSignoffsReady',
  'allConsumptionReady',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71J_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-release-passport/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-passport/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-readiness/latest',
  '/api/crm/command/search/regulator-evidence/terminal-api-surface-registry/latest',
  'R71J_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71J terminal evidence release passport gate.
 * @collaboration CRM regulator evidence gates, release readiness API, release passport API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71J terminal evidence release passport contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71J gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence release passport posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71J gate blocked ${label}`);
  }
};

/**
 * @function runR71JTerminalEvidenceReleasePassportGate
 * @description Validates R71J terminal regulator/investor evidence release passport service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71I release readiness.
 */
const runR71JTerminalEvidenceReleasePassportGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE RELEASE PASSPORT GATE');
  console.log(' - R71J release passport authority present');
  console.log(' - R71I release readiness and R71H API surface registry source routes anchored');
  console.log(' - identity/signoff/sections/consumption/assertion posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71JTerminalEvidenceReleasePassportGate();
