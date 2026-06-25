/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71D-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-INSPECTION-DESK-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_INSPECTION_DESK_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceInspectionDesk',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_INSPECTION_DESK_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_INSPECTION_DESK',
  'audienceCards',
  'actionRegistry',
  'endpointRegistry',
  'proofPassport',
  'boardBrief',
  'Executive command evidence card',
  'Regulator inspection evidence card',
  'Investor diligence evidence card',
  'Audit and assurance evidence card',
  'Engineering terminal proof card',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71D_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_INSPECTION_DESK_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-inspection-desk/latest',
  '/api/crm/command/search/regulator-evidence/terminal-inspection-desk/latest',
  '/api/crm/command/search/regulator-evidence/terminal-packet/latest',
  '/api/crm/command/search/regulator-evidence/terminal-manifest/latest',
  '/api/crm/command/search/regulator-evidence/terminal-summary/latest',
  'R71D_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_INSPECTION_DESK_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71D terminal evidence inspection desk gate.
 * @collaboration CRM regulator evidence gates, terminal packet API, buyer/regulator/investor inspection desk API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71D terminal evidence inspection desk contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71D gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence inspection desk posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71D gate blocked ${label}`);
  }
};

/**
 * @function runR71DTerminalEvidenceInspectionDeskGate
 * @description Validates R71D terminal regulator/investor evidence inspection desk service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71C terminal evidence packet.
 */
const runR71DTerminalEvidenceInspectionDeskGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE INSPECTION DESK GATE');
  console.log(' - R71D inspection desk authority contract present');
  console.log(' - R71C packet, R71B manifest, and R71A summary source routes anchored');
  console.log(' - audience card/action registry/proof passport posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71DTerminalEvidenceInspectionDeskGate();
