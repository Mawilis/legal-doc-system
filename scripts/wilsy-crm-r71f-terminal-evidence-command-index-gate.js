/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71F-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-COMMAND-INDEX-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COMMAND_INDEX_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceCommandIndex',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COMMAND_INDEX_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COMMAND_INDEX',
  'commandIndex',
  'readinessIndex',
  'aiCommandPrompts',
  'cockpitWiringHints',
  'open_terminal_diligence_room',
  'open_terminal_packet',
  'open_terminal_manifest',
  'open_terminal_summary',
  'inspect_terminal_closure_verifier',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71F_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COMMAND_INDEX_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-command-index/latest',
  '/api/crm/command/search/regulator-evidence/terminal-command-index/latest',
  '/api/crm/command/search/regulator-evidence/terminal-diligence-room/latest',
  '/api/crm/command/search/regulator-evidence/terminal-inspection-desk/latest',
  '/api/crm/command/search/regulator-evidence/terminal-packet/latest',
  'R71F_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COMMAND_INDEX_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71F terminal evidence command index gate.
 * @collaboration CRM regulator evidence gates, terminal diligence room API, command index API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71F terminal evidence command index contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71F gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence command index posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71F gate blocked ${label}`);
  }
};

/**
 * @function runR71FTerminalEvidenceCommandIndexGate
 * @description Validates R71F terminal regulator/investor evidence command index service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71E diligence room.
 */
const runR71FTerminalEvidenceCommandIndexGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE COMMAND INDEX GATE');
  console.log(' - R71F command index authority contract present');
  console.log(' - R71E diligence room source route anchored');
  console.log(' - command/readiness/AI/cockpit wiring posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71FTerminalEvidenceCommandIndexGate();
