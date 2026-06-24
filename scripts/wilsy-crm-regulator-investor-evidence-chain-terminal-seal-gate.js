/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R68Z-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERSION',
  'buildLeadSearchRegulatorInvestorEvidenceChainTerminalSeal',
  'computeRegulatorInvestorEvidenceChainTerminalSealHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED',
  'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIED',
  'terminalSealHash',
  'terminalSeal',
  'requiredStatusesVerified',
  'proofFlagsAllTrue',
  'finalAttestationVerifierPassed',
  'TERMINALLY_SEALED',
  'REGULATOR',
  'INVESTOR',
  'R68Y',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R68Z_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
  'R68Z_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R68Z terminal evidence-chain seal gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, terminal seal controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R68Z gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R68Z gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R68Z gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R68Z gate blocked ${label}`);
  }
};

/**
 * @function runR68ZTerminalSealGate
 * @description Validates R68Z terminal regulator and investor evidence-chain seal contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR68ZTerminalSealGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => {
    assertIncludes(service, contract, 'service contract');
  });

  requiredRouteContracts.forEach((contract) => {
    assertIncludes(route, contract, 'route contract');
  });

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL SEAL GATE');
  console.log(' - R68Z terminal seal authority contract present');
  console.log(' - R68Y final attestation verifier source route anchored');
  console.log(' - terminal seal hash contract present');
  console.log(' - JSON response only terminal seal contract present');
  console.log(' - filesystem export behavior blocked');
};

runR68ZTerminalSealGate();
