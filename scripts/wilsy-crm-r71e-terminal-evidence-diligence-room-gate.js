/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71E-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-DILIGENCE-ROOM-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_DILIGENCE_ROOM_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceDiligenceRoom',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_DILIGENCE_ROOM_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_DILIGENCE_ROOM',
  'roomPassport',
  'stakeholderRooms',
  'diligenceChecklist',
  'objectionMatrix',
  'demoScript',
  'routeMap',
  'Buyer proof room',
  'Board command room',
  'Regulator evidence room',
  'Investor diligence room',
  'Audit assurance room',
  'Engineering control room',
  'sourceInspectionDeskSummary',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71E_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_DILIGENCE_ROOM_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-diligence-room/latest',
  '/api/crm/command/search/regulator-evidence/terminal-diligence-room/latest',
  '/api/crm/command/search/regulator-evidence/terminal-inspection-desk/latest',
  '/api/crm/command/search/regulator-evidence/terminal-packet/latest',
  '/api/crm/command/search/regulator-evidence/terminal-manifest/latest',
  '/api/crm/command/search/regulator-evidence/terminal-summary/latest',
  'R71E_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_DILIGENCE_ROOM_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71E terminal evidence diligence room gate.
 * @collaboration CRM regulator evidence gates, terminal inspection desk API, due diligence room API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71E terminal evidence diligence room contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71E gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence diligence room posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71E gate blocked ${label}`);
  }
};

/**
 * @function runR71ETerminalEvidenceDiligenceRoomGate
 * @description Validates R71E terminal regulator/investor evidence diligence room service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71D inspection desk.
 */
const runR71ETerminalEvidenceDiligenceRoomGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE DILIGENCE ROOM GATE');
  console.log(' - R71E diligence room authority contract present');
  console.log(' - R71D inspection desk, R71C packet, R71B manifest, and R71A summary source routes anchored');
  console.log(' - stakeholder room/checklist/objection/demo posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71ETerminalEvidenceDiligenceRoomGate();
