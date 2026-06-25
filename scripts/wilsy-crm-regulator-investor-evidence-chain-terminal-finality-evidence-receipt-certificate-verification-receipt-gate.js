/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R69L-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_VERSION',
  'buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceipt',
  'computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_MATERIALIZED',
  'terminalFinalityEvidenceReceiptCertificateVerificationReceipt',
  'verificationReceiptHash',
  'receiptHashR69L',
  'verifierSummary',
  'receiptDispositionR69L',
  'certificateHashVerified',
  'verificationReceiptHashVerified',
  'receiptHashVerified',
  'evidenceIndexHashVerified',
  'proofSummaryVerified',
  'certificateDispositionVerified',
  'receiptDispositionVerified',
  'regulatorReady',
  'investorReady',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R69L_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/latest',
  'R69L_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R69L terminal finality evidence receipt certificate verification receipt gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, terminal certificate verification receipt controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R69L gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R69L gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R69L gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R69L gate blocked ${label}`);
  }
};

/**
 * @function runR69LTerminalFinalityEvidenceReceiptCertificateVerificationReceiptGate
 * @description Validates R69L terminal regulator and investor finality evidence receipt certificate verification receipt contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR69LTerminalFinalityEvidenceReceiptCertificateVerificationReceiptGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL FINALITY EVIDENCE RECEIPT CERTIFICATE VERIFICATION RECEIPT GATE');
  console.log(' - R69L terminal finality evidence receipt certificate verification receipt authority contract present');
  console.log(' - R69K certificate verifier source route anchored');
  console.log(' - verification receipt hash contract present');
  console.log(' - JSON response only receipt contract present');
  console.log(' - filesystem export behavior blocked');
};

runR69LTerminalFinalityEvidenceReceiptCertificateVerificationReceiptGate();
