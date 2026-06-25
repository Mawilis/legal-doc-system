/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R70B-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERSION',
  'buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerificationReceipt',
  'computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerificationReceiptHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_MATERIALIZED',
  'terminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerificationReceipt',
  'receiptHashR70B',
  'verificationReceiptHash',
  'verificationReceiptSummaryR70B',
  'verificationReceiptDispositionR70B',
  'certificateHashR69ZVerified',
  'finalityCertificateHashVerified',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R70B_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/latest',
  'R70B_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R70B finality certificate verification receipt gate.
 * @collaboration CRM regulator evidence gates, route contracts, service receipt contracts.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R70B verification receipt contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R70B gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior appears.
 * @collaboration JSON-only verification receipt posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R70B gate blocked ${label}`);
  }
};

/**
 * @function runR70BFinalityCertificateVerificationReceiptGate
 * @description Validates R70B terminal finality certificate verification receipt service and route contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR70BFinalityCertificateVerificationReceiptGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL FINALITY CERTIFICATE VERIFICATION RECEIPT GATE');
  console.log(' - R70B authority contract present');
  console.log(' - R70A finality certificate verifier source route anchored');
  console.log(' - R70B verification receipt hash contract present');
  console.log(' - JSON-only verification receipt posture present');
  console.log(' - filesystem export behavior blocked');
};

runR70BFinalityCertificateVerificationReceiptGate();
