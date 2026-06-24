/* eslint-disable */
import fs from 'fs';
import path from 'path';

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY',
  'WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERSION',
  'buildLeadSearchRegulatorDossierChainLedgerVerificationReceipt',
  'computeRegulatorDossierLedgerVerificationReceiptHash',
  'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R68P_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/verification-receipt/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest',
  'R68P_SAFE_EXISTING_LEDGER_VERIFICATION_RECEIPT_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R68P gate contract validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, receipt verification controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R68P gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R68P gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R68P gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R68P gate blocked ${label}`);
  }
};

/**
 * @function runR68PVerificationReceiptGate
 * @description Validates R68P regulator dossier chain ledger verification receipt contracts.
 * @collaboration CRM command routes, lead search engine service, regulator evidence proof chain.
 */
const runR68PVerificationReceiptGate = () => {
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

  console.log('PASS: WILSY CRM REGULATOR DOSSIER CHAIN LEDGER VERIFICATION RECEIPT GATE');
  console.log(' - R68P receipt authority contract present');
  console.log(' - R68O verification source route anchored');
  console.log(' - JSON response only receipt contract present');
  console.log(' - filesystem export behavior blocked');
};

runR68PVerificationReceiptGate();
