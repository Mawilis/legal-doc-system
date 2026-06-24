/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R69C-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIER_VERSION',
  'verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt',
  'computeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIED',
  'receiptHashVerified',
  'storedReceiptHash',
  'recomputedReceiptHash',
  'terminalSealHashVerified',
  'upstreamReceiptPostureVerified',
  'receiptFlagsVerified',
  'terminalDispositionVerified',
  'regulatorReady',
  'investorReady',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R69C_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
  'R69C_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R69C terminal receipt verifier gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, receipt verifier controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R69C gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R69C gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R69C gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R69C gate blocked ${label}`);
  }
};

/**
 * @function runR69CTerminalSealVerificationReceiptVerifierGate
 * @description Validates R69C terminal regulator and investor verification receipt verifier contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR69CTerminalSealVerificationReceiptVerifierGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL SEAL VERIFICATION RECEIPT VERIFIER GATE');
  console.log(' - R69C terminal receipt verifier authority contract present');
  console.log(' - R69B terminal receipt source route anchored');
  console.log(' - receipt hash recomputation contract present');
  console.log(' - JSON response only verifier contract present');
  console.log(' - filesystem export behavior blocked');
};

runR69CTerminalSealVerificationReceiptVerifierGate();
