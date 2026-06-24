/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R68T-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-AUTHORITY',
  'WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERSION',
  'buildLeadSearchRegulatorDossierChainEvidenceBundleIndex',
  'computeRegulatorDossierChainEvidenceBundleIndexHash',
  'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED',
  'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY',
  'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY',
  'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY',
  'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY',
  'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY',
  'bundleIndexHash',
  'proofFlags',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R68T_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest',
  'R68T_SAFE_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R68T evidence bundle index gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, evidence bundle controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R68T gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R68T gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R68T gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R68T gate blocked ${label}`);
  }
};

/**
 * @function runR68TEvidenceBundleIndexGate
 * @description Validates R68T regulator dossier chain evidence bundle index contracts.
 * @collaboration CRM command routes, lead search engine service, regulator evidence proof chain.
 */
const runR68TEvidenceBundleIndexGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR DOSSIER CHAIN EVIDENCE BUNDLE INDEX GATE');
  console.log(' - R68T evidence bundle authority contract present');
  console.log(' - R68O through R68S contracts indexed');
  console.log(' - evidence bundle hash contract present');
  console.log(' - JSON response only index contract present');
  console.log(' - filesystem export behavior blocked');
};

runR68TEvidenceBundleIndexGate();
