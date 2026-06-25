/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71L-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-RELEASE-BRIEF-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_BRIEF_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceReleaseBrief',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_BRIEF_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_BRIEF',
  'executiveReleaseBrief',
  'audienceBriefs',
  'proofHighlights',
  'releaseBriefActions',
  'finalBriefAssertions',
  'sourceVerifierSummary',
  'Buyer release brief',
  'Board release brief',
  'Regulator release brief',
  'Investor release brief',
  'Audit release brief',
  'Engineering release brief',
  'NO_RECURSIVE_EXPANSION_TERMINAL_BOUNDARY_VERIFIED',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71L_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_BRIEF_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-release-brief/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-brief/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-passport/verify/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-passport/latest',
  'R71L_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_BRIEF_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71L terminal evidence release brief gate.
 * @collaboration CRM regulator evidence gates, release passport verifier API, release brief API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71L terminal evidence release brief contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71L gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence release brief posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71L gate blocked ${label}`);
  }
};

/**
 * @function runR71LTerminalEvidenceReleaseBriefGate
 * @description Validates R71L terminal regulator/investor evidence release brief service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71K release passport verifier.
 */
const runR71LTerminalEvidenceReleaseBriefGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE RELEASE BRIEF GATE');
  console.log(' - R71L release brief authority present');
  console.log(' - R71K verifier and R71J release passport source routes anchored');
  console.log(' - executive/audience/proof/action/assertion brief posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71LTerminalEvidenceReleaseBriefGate();
