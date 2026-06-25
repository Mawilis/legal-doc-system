/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R70E-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-CLOSURE-CERTIFICATE-VERIFIER-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_VERIFIER_VERSION',
  'verifyLeadSearchRegulatorInvestorEvidenceChainTerminalClosureCertificate',
  'computeRegulatorInvestorEvidenceChainTerminalClosureCertificateHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_VERIFIED',
  'terminalClosureCertificateVerifier',
  'terminalClosureCertificateHashVerified',
  'certificateHashR70DVerified',
  'recomputedCertificateHashR70D',
  'recursiveLoopFrozen',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R70E_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_VERIFIER_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/terminal-closure-certificate/verify/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/terminal-closure-certificate/verify/latest',
  'R70E_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_VERIFIER_ROUTE',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R70E terminal closure certificate verifier gate.
 * @collaboration CRM regulator evidence gates, route contracts, terminal closure verifier contracts.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R70E terminal closure certificate verifier contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R70E gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior appears.
 * @collaboration JSON-only terminal closure verifier posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R70E gate blocked ${label}`);
  }
};

/**
 * @function runR70ETerminalClosureCertificateVerifierGate
 * @description Validates R70E terminal closure certificate verifier service and route contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR70ETerminalClosureCertificateVerifierGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL CLOSURE CERTIFICATE VERIFIER GATE');
  console.log(' - R70E closure verifier authority contract present');
  console.log(' - R70D closure certificate source route anchored');
  console.log(' - R70E closure certificate hash recomputation contract present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export behavior blocked');
};

runR70ETerminalClosureCertificateVerifierGate();
