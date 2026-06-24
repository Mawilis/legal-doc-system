/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R68X-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-REGULATOR-INVESTOR-ATTESTATION-AUTHORITY',
  'WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_VERSION',
  'buildLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation',
  'computeRegulatorDossierChainFinalAttestationHash',
  'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_ISSUED',
  'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED',
  'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED',
  'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED',
  'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED',
  'attestationHash',
  'finalAttestation',
  'REGULATOR',
  'INVESTOR',
  'R68W',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R68X_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest',
  'R68X_SAFE_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_REGULATOR_INVESTOR_ATTESTATION_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R68X final attestation gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, final attestation controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R68X gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R68X gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R68X gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R68X gate blocked ${label}`);
  }
};

/**
 * @function runR68XFinalAttestationGate
 * @description Validates R68X final regulator and investor attestation contracts.
 * @collaboration CRM command routes, lead search engine service, regulator evidence proof chain.
 */
const runR68XFinalAttestationGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR DOSSIER CHAIN FINAL ATTESTATION GATE');
  console.log(' - R68X final regulator/investor attestation authority contract present');
  console.log(' - R68W receipt verifier source route anchored');
  console.log(' - attestation hash contract present');
  console.log(' - JSON response only attestation contract present');
  console.log(' - filesystem export behavior blocked');
};

runR68XFinalAttestationGate();
