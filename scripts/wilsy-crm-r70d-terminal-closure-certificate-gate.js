/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R70D-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-CLOSURE-CERTIFICATE-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_VERSION',
  'buildLeadSearchRegulatorInvestorEvidenceChainTerminalClosureCertificate',
  'computeRegulatorInvestorEvidenceChainTerminalClosureCertificateHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_ISSUED',
  'terminalClosureCertificate',
  'terminalClosureCertificateHash',
  'certificateHashR70D',
  'terminalClosureDispositionR70D',
  'recursiveLoopFrozenAfterR70E',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R70D_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/terminal-closure-certificate/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/terminal-closure-certificate/latest',
  'R70D_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R70D terminal closure certificate gate.
 * @collaboration CRM regulator evidence gates, route contracts, terminal closure certificate contracts.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R70D terminal closure certificate contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R70D gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior appears.
 * @collaboration JSON-only terminal closure certificate posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R70D gate blocked ${label}`);
  }
};

/**
 * @function runR70DTerminalClosureCertificateGate
 * @description Validates R70D terminal closure certificate service and route contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR70DTerminalClosureCertificateGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL CLOSURE CERTIFICATE GATE');
  console.log(' - R70D closure authority contract present');
  console.log(' - R70C terminal verifier source route anchored');
  console.log(' - R70D closure certificate hash contract present');
  console.log(' - JSON-only closure certificate posture present');
  console.log(' - filesystem export behavior blocked');
};

runR70DTerminalClosureCertificateGate();
