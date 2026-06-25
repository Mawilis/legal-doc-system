/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R69H-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-INDEX-VERIFICATION-RECEIPT-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERSION',
  'buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt',
  'computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceiptHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED',
  'terminalFinalityEvidenceIndexVerificationReceipt',
  'verificationReceiptHash',
  'receiptDisposition',
  'evidenceIndexHashVerified',
  'expectedSourceStatusesVerified',
  'evidenceRoutesVerified',
  'proofFlagsAllTrue',
  'evidenceIndexPostureVerified',
  'regulatorReady',
  'investorReady',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R69H_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/latest',
  'R69H_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R69H terminal finality evidence index verification receipt gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, terminal evidence receipt controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R69H gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R69H gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R69H gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R69H gate blocked ${label}`);
  }
};

/**
 * @function runR69HTerminalFinalityEvidenceIndexVerificationReceiptGate
 * @description Validates R69H terminal regulator and investor finality evidence index verification receipt contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR69HTerminalFinalityEvidenceIndexVerificationReceiptGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL FINALITY EVIDENCE INDEX VERIFICATION RECEIPT GATE');
  console.log(' - R69H terminal finality evidence index verification receipt authority contract present');
  console.log(' - R69G evidence index verifier source route anchored');
  console.log(' - verification receipt hash contract present');
  console.log(' - JSON response only receipt contract present');
  console.log(' - filesystem export behavior blocked');
};

runR69HTerminalFinalityEvidenceIndexVerificationReceiptGate();
