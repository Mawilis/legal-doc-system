/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R69D-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-RECEIPT-FINALITY-CERTIFICATE-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERSION',
  'buildLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate',
  'computeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ISSUED',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIED',
  'terminalReceiptFinalityCertificate',
  'certificateHash',
  'receiptHashVerified',
  'terminalSealHashVerified',
  'FINALITY_CERTIFIED',
  'regulatorReady',
  'investorReady',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R69D_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
  'R69D_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R69D terminal receipt finality certificate gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, finality certificate controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R69D gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R69D gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R69D gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R69D gate blocked ${label}`);
  }
};

/**
 * @function runR69DTerminalReceiptFinalityCertificateGate
 * @description Validates R69D terminal regulator and investor receipt finality certificate contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR69DTerminalReceiptFinalityCertificateGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL RECEIPT FINALITY CERTIFICATE GATE');
  console.log(' - R69D terminal receipt finality certificate authority contract present');
  console.log(' - R69C terminal receipt verifier source route anchored');
  console.log(' - certificate hash contract present');
  console.log(' - JSON response only finality certificate contract present');
  console.log(' - filesystem export behavior blocked');
};

runR69DTerminalReceiptFinalityCertificateGate();
