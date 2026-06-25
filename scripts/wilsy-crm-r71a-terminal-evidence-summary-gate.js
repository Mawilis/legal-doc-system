/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71A-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-SUMMARY-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_SUMMARY_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceSummary',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_SUMMARY_READY',
  'JSON_RESPONSE_ONLY_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_CHAIN',
  'recursiveLoopFrozen',
  'noR70F',
  'competitivePosture',
  'crmEvidenceOperatingSystem',
  'auditReadyDecisionLayer',
  'regulatorInspectable',
  'investorInspectable',
  'sourceTerminalClosureProof',
  'terminalHashes',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71A_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_SUMMARY_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-summary/latest',
  '/api/crm/command/search/regulator-evidence/terminal-summary/latest',
  'R71A_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_SUMMARY_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71A terminal evidence summary gate.
 * @collaboration CRM regulator evidence gates, terminal closure proof, buyer-readable summary API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71A terminal evidence summary contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71A gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive R70F behavior appears.
 * @collaboration JSON-only terminal evidence summary posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71A gate blocked ${label}`);
  }
};

/**
 * @function runR71ATerminalEvidenceSummaryGate
 * @description Validates R71A terminal regulator/investor evidence summary service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R70E terminal closure verifier.
 */
const runR71ATerminalEvidenceSummaryGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE SUMMARY GATE');
  console.log(' - R71A summary authority contract present');
  console.log(' - R70E terminal closure verifier source route anchored');
  console.log(' - buyer/regulator/investor summary posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and R70F behavior blocked');
};

runR71ATerminalEvidenceSummaryGate();
