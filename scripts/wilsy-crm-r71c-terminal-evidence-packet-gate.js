/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71C-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-PACKET-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_PACKET_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidencePacket',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_PACKET_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_PACKET',
  'executiveBrief',
  'regulatorPacket',
  'investorPacket',
  'engineeringPacket',
  'manifestSnapshot',
  'terminalSummarySnapshot',
  'commercialAssertions',
  'buyerDemoReady',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71C_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_PACKET_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-packet/latest',
  '/api/crm/command/search/regulator-evidence/terminal-packet/latest',
  '/api/crm/command/search/regulator-evidence/terminal-manifest/latest',
  '/api/crm/command/search/regulator-evidence/terminal-summary/latest',
  'R71C_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_PACKET_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71C terminal evidence packet gate.
 * @collaboration CRM regulator evidence gates, terminal manifest API, buyer/regulator/investor packet API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71C terminal evidence packet contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71C gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence packet posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71C gate blocked ${label}`);
  }
};

/**
 * @function runR71CTerminalEvidencePacketGate
 * @description Validates R71C terminal regulator/investor evidence packet service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71B terminal manifest.
 */
const runR71CTerminalEvidencePacketGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE PACKET GATE');
  console.log(' - R71C packet authority contract present');
  console.log(' - R71B manifest and R71A summary source routes anchored');
  console.log(' - executive/regulator/investor/engineering packet posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71CTerminalEvidencePacketGate();
