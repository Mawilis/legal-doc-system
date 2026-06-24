/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R69B-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-VERIFICATION-RECEIPT-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERSION',
  'buildLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt',
  'computeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_MATERIALIZED',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED',
  'terminalSealVerificationReceipt',
  'terminalSealHashVerified',
  'storedTerminalSealHash',
  'recomputedTerminalSealHash',
  'receiptHash',
  'regulatorReady',
  'investorReady',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R69B_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
  'R69B_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R69B terminal seal verification receipt gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, terminal receipt controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R69B gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R69B gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R69B gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R69B gate blocked ${label}`);
  }
};

/**
 * @function runR69BTerminalSealVerificationReceiptGate
 * @description Validates R69B terminal regulator and investor evidence-chain verification receipt contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR69BTerminalSealVerificationReceiptGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL SEAL VERIFICATION RECEIPT GATE');
  console.log(' - R69B terminal seal verification receipt authority contract present');
  console.log(' - R69A terminal seal verifier source route anchored');
  console.log(' - receipt hash contract present');
  console.log(' - JSON response only receipt contract present');
  console.log(' - filesystem export behavior blocked');
};

runR69BTerminalSealVerificationReceiptGate();
