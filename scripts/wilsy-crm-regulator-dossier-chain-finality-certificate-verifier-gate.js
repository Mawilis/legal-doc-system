/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY',
  'WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIER_VERSION',
  'verifyLeadSearchRegulatorDossierChainFinalityCertificate',
  'computeRegulatorDossierChainFinalityCertificateHash',
  'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED',
  'certificateHashVerified',
  'recomputedCertificateHash',
  'receiptHashVerified',
  'sourceLedgerRootVerified',
  'sourceContinuityVerified',
  'sourceLinksVerified',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R68S_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest',
  'R68S_SAFE_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIER_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R68S finality certificate verifier gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, finality verifier controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R68S gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R68S gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R68S gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R68S gate blocked ${label}`);
  }
};

/**
 * @function runR68SFinalityCertificateVerifierGate
 * @description Validates R68S regulator dossier chain finality certificate verifier contracts.
 * @collaboration CRM command routes, lead search engine service, regulator evidence proof chain.
 */
const runR68SFinalityCertificateVerifierGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR DOSSIER CHAIN FINALITY CERTIFICATE VERIFIER GATE');
  console.log(' - R68S finality verifier authority contract present');
  console.log(' - R68R finality source route anchored');
  console.log(' - certificate hash recomputation contract present');
  console.log(' - JSON response only verifier contract present');
  console.log(' - filesystem export behavior blocked');
};

runR68SFinalityCertificateVerifierGate();
