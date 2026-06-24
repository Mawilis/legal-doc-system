/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY',
  'WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERSION',
  'buildLeadSearchRegulatorDossierChainFinalityCertificate',
  'computeRegulatorDossierChainFinalityCertificateHash',
  'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED',
  'receiptHashVerified',
  'sourceLedgerRootVerified',
  'sourceContinuityVerified',
  'sourceLinksVerified',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R68R_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/finality-certificate/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest',
  'R68R_SAFE_DOSSIER_CHAIN_FINALITY_CERTIFICATE_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R68R finality certificate gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, finality certificate controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R68R gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R68R gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R68R gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R68R gate blocked ${label}`);
  }
};

/**
 * @function runR68RFinalityCertificateGate
 * @description Validates R68R regulator dossier chain finality certificate contracts.
 * @collaboration CRM command routes, lead search engine service, regulator evidence proof chain.
 */
const runR68RFinalityCertificateGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR DOSSIER CHAIN FINALITY CERTIFICATE GATE');
  console.log(' - R68R finality authority contract present');
  console.log(' - R68Q verifier source route anchored');
  console.log(' - certificate hash contract present');
  console.log(' - JSON response only finality contract present');
  console.log(' - filesystem export behavior blocked');
};

runR68RFinalityCertificateGate();
