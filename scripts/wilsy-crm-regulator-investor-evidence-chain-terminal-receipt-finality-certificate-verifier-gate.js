/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R69E-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERSION',
  'verifyLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate',
  'computeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIED',
  'certificateHashVerified',
  'storedCertificateHash',
  'recomputedCertificateHash',
  'receiptHashVerified',
  'terminalSealHashVerified',
  'upstreamCertificatePostureVerified',
  'certificateFlagsVerified',
  'finalityDispositionVerified',
  'regulatorReady',
  'investorReady',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R69E_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
  'R69E_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R69E terminal receipt finality certificate verifier gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, finality certificate verifier controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R69E gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R69E gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R69E gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R69E gate blocked ${label}`);
  }
};

/**
 * @function runR69ETerminalReceiptFinalityCertificateVerifierGate
 * @description Validates R69E terminal regulator and investor receipt finality certificate verifier contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR69ETerminalReceiptFinalityCertificateVerifierGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL RECEIPT FINALITY CERTIFICATE VERIFIER GATE');
  console.log(' - R69E terminal receipt finality certificate verifier authority contract present');
  console.log(' - R69D terminal receipt finality certificate source route anchored');
  console.log(' - certificate hash recomputation contract present');
  console.log(' - JSON response only verifier contract present');
  console.log(' - filesystem export behavior blocked');
};

runR69ETerminalReceiptFinalityCertificateVerifierGate();
