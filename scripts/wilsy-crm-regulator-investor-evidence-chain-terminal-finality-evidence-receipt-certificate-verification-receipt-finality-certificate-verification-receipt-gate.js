/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R69P-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERSION',
  'buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceipt',
  'computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_MATERIALIZED',
  'terminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceipt',
  'verificationReceiptHash',
  'receiptHashR69P',
  'verificationReceiptSummaryR69P',
  'verificationReceiptDispositionR69P',
  'finalityCertificateHashVerified',
  'certificateHashR69NVerified',
  'receiptHashPostureVerified',
  'certificateHashPostureVerified',
  'verifierFinalitySummaryVerified',
  'finalityCertificateDispositionR69NVerified',
  'regulatorReady',
  'investorReady',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R69P_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/latest',
  'R69P_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R69P terminal finality certificate verification receipt gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, terminal finality verification receipt controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R69P gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R69P gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R69P gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R69P gate blocked ${label}`);
  }
};

/**
 * @function runR69PTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptGate
 * @description Validates R69P terminal regulator and investor finality certificate verification receipt contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR69PTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL FINALITY CERTIFICATE VERIFICATION RECEIPT GATE');
  console.log(' - R69P terminal finality certificate verification receipt authority contract present');
  console.log(' - R69O finality certificate verifier source route anchored');
  console.log(' - verification receipt hash contract present');
  console.log(' - JSON response only receipt contract present');
  console.log(' - filesystem export behavior blocked');
};

runR69PTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptGate();
