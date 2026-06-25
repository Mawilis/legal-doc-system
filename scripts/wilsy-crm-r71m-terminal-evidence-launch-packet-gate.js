/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71M-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-LAUNCH-PACKET-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_LAUNCH_PACKET_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceLaunchPacket',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_LAUNCH_PACKET_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_LAUNCH_PACKET',
  'launchPacketIdentity',
  'launchArtifacts',
  'launchSequence',
  'competitivePositioning',
  'launchReadinessMatrix',
  'launchAssertions',
  'buyer_demo_packet',
  'board_approval_packet',
  'regulator_inspection_packet',
  'investor_diligence_packet',
  'audit_assurance_packet',
  'engineering_handoff_packet',
  'COMMERCIAL_EVIDENCE_LAUNCH',
  'sourceReleaseBriefSummary',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71M_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_LAUNCH_PACKET_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-launch-packet/latest',
  '/api/crm/command/search/regulator-evidence/terminal-launch-packet/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-brief/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-passport/verify/latest',
  'R71M_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_LAUNCH_PACKET_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71M terminal evidence launch packet gate.
 * @collaboration CRM regulator evidence gates, release brief API, launch packet API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71M terminal evidence launch packet contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71M gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence launch packet posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71M gate blocked ${label}`);
  }
};

/**
 * @function runR71MTerminalEvidenceLaunchPacketGate
 * @description Validates R71M terminal regulator/investor evidence launch packet service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71L release brief.
 */
const runR71MTerminalEvidenceLaunchPacketGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE LAUNCH PACKET GATE');
  console.log(' - R71M launch packet authority present');
  console.log(' - R71L release brief and R71K verifier source routes anchored');
  console.log(' - launch identity/artifacts/sequence/positioning/readiness posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71MTerminalEvidenceLaunchPacketGate();
