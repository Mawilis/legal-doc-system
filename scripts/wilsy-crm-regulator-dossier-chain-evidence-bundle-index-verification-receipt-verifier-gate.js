/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R68W-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY',
  'WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIER_VERSION',
  'verifyLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt',
  'computeRegulatorDossierChainEvidenceBundleIndexVerificationReceiptHash',
  'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED',
  'receiptHashVerified',
  'recomputedReceiptHash',
  'sourceVerifierStatusVerified',
  'sourceBundleIndexStatusVerified',
  'bundleIndexHashEqualityVerified',
  'embeddedProofFlagsVerified',
  'evidenceRangeStillIndexed',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R68W_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest',
  'R68W_SAFE_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R68W verification receipt verifier gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, receipt verifier controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R68W gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R68W gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R68W gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R68W gate blocked ${label}`);
  }
};

/**
 * @function runR68WVerificationReceiptVerifierGate
 * @description Validates R68W regulator dossier chain evidence bundle index verification receipt verifier contracts.
 * @collaboration CRM command routes, lead search engine service, regulator evidence proof chain.
 */
const runR68WVerificationReceiptVerifierGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR DOSSIER CHAIN EVIDENCE BUNDLE INDEX VERIFICATION RECEIPT VERIFIER GATE');
  console.log(' - R68W verification receipt verifier authority contract present');
  console.log(' - R68V verification receipt source route anchored');
  console.log(' - receipt hash recomputation contract present');
  console.log(' - JSON response only verifier contract present');
  console.log(' - filesystem export behavior blocked');
};

runR68WVerificationReceiptVerifierGate();
