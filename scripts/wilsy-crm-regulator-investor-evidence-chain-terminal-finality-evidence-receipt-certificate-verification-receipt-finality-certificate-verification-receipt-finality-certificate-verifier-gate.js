/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R69S-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERSION',
  'verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificate',
  'computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIED',
  'finalityCertificateHashVerified',
  'certificateHashR69RVerified',
  'storedFinalityCertificateHash',
  'recomputedFinalityCertificateHash',
  'verificationReceiptHashVerified',
  'receiptHashR69PVerified',
  'sourceFinalityCertificateHashVerified',
  'certificateHashR69NVerified',
  'finalityCertificateSummaryR69RVerified',
  'finalityCertificateDispositionR69RVerified',
  'receiptHashPostureVerified',
  'certificateHashPostureVerified',
  'regulatorReady',
  'investorReady',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R69S_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/latest',
  'R69S_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads source files for the R69S terminal finality certificate verifier gate.
 * @collaboration CRM regulator evidence gates, route contracts, service verifier contracts.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R69S contract is absent.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R69S gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior appears.
 * @collaboration JSON-only runtime posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R69S gate blocked ${label}`);
  }
};

/**
 * @function runR69STerminalFinalityCertificateVerifierGate
 * @description Validates R69S terminal finality certificate verifier service and route contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR69STerminalFinalityCertificateVerifierGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL FINALITY CERTIFICATE VERIFIER GATE');
  console.log(' - R69S authority contract present');
  console.log(' - R69R finality certificate source route anchored');
  console.log(' - R69S hash recomputation contract present');
  console.log(' - JSON-only verifier posture present');
  console.log(' - filesystem export behavior blocked');
};

runR69STerminalFinalityCertificateVerifierGate();
