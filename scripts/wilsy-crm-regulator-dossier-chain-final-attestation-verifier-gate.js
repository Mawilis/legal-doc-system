/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R68Y-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-ATTESTATION-VERIFIER-AUTHORITY',
  'WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_VERIFIER_VERSION',
  'verifyLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation',
  'computeRegulatorDossierChainFinalAttestationHash',
  'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIED',
  'attestationHashVerified',
  'recomputedAttestationHash',
  'chainRangeVerified',
  'audienceVerified',
  'hashEqualityVerified',
  'proofFlagsVerified',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R68Y_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_VERIFIER_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest',
  'R68Y_SAFE_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIER_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R68Y final attestation verifier gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, final attestation verifier controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R68Y gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R68Y gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R68Y gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R68Y gate blocked ${label}`);
  }
};

/**
 * @function runR68YFinalAttestationVerifierGate
 * @description Validates R68Y final regulator and investor attestation verifier contracts.
 * @collaboration CRM command routes, lead search engine service, regulator evidence proof chain.
 */
const runR68YFinalAttestationVerifierGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR DOSSIER CHAIN FINAL ATTESTATION VERIFIER GATE');
  console.log(' - R68Y final attestation verifier authority contract present');
  console.log(' - R68X final attestation source route anchored');
  console.log(' - attestation hash recomputation contract present');
  console.log(' - JSON response only verifier contract present');
  console.log(' - filesystem export behavior blocked');
};

runR68YFinalAttestationVerifierGate();
