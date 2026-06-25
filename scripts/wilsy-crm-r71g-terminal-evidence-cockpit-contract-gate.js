/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71G-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-COCKPIT-CONTRACT-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COCKPIT_CONTRACT_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceCockpitContract',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COCKPIT_CONTRACT_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COCKPIT_CONTRACT',
  'cockpitKpis',
  'cockpitTabs',
  'primaryActions',
  'evidenceHud',
  'aiSurfaceContract',
  'sourceCommandIndexSummary',
  'open_terminal_diligence_room',
  'VERIFIED_TERMINAL_EVIDENCE',
  'No recursive proof expansion required.',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71G_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COCKPIT_CONTRACT_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-cockpit-contract/latest',
  '/api/crm/command/search/regulator-evidence/terminal-cockpit-contract/latest',
  '/api/crm/command/search/regulator-evidence/terminal-command-index/latest',
  '/api/crm/command/search/regulator-evidence/terminal-diligence-room/latest',
  'R71G_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COCKPIT_CONTRACT_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71G terminal evidence cockpit contract gate.
 * @collaboration CRM regulator evidence gates, command index API, cockpit contract API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71G terminal evidence cockpit contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71G gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence cockpit contract posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71G gate blocked ${label}`);
  }
};

/**
 * @function runR71GTerminalEvidenceCockpitContractGate
 * @description Validates R71G terminal regulator/investor evidence cockpit contract service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71F command index.
 */
const runR71GTerminalEvidenceCockpitContractGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE COCKPIT CONTRACT GATE');
  console.log(' - R71G cockpit contract authority present');
  console.log(' - R71F command index source route anchored');
  console.log(' - KPI/tab/action/HUD/AI surface posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71GTerminalEvidenceCockpitContractGate();
