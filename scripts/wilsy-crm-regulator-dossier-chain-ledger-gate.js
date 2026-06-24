/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM regulator dossier chain ledger authority gate.
 */
const fs = require('node:fs');
const path = require('node:path');
const parser = require('../client/node_modules/@babel/parser');

const ROOT = process.cwd();
const SEARCH_SERVICE = 'server/services/wilsyCrmLeadSearchEngineService.js';
const CRM_ROUTE = 'server/routes/crmCommandRoutes.js';

/**
 * @function readText
 * @description Reads a repository-relative source file.
 * @param {string} relativePath - Repository-relative file path.
 * @returns {string} Source text.
 * @collaboration Supplies source content for R68N ledger validation.
 */
function readText(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), 'utf8');
}

/**
 * @function assertCondition
 * @description Throws when a condition fails.
 * @param {boolean} condition - Assertion condition.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Blocks broken regulator dossier chain ledger contracts.
 */
function assertCondition(condition, message) {
  if (!condition) throw new Error(message);
}

/**
 * @function assertIncludes
 * @description Requires source text to include a contract.
 * @param {string} source - Source text.
 * @param {string} contract - Required contract.
 * @param {string} label - Source label.
 * @returns {void}
 * @collaboration Locks R68N ledger contracts.
 */
function assertIncludes(source, contract, label) {
  assertCondition(source.includes(contract), `${label} missing contract: ${contract}`);
}

/**
 * @function assertNotIncludes
 * @description Blocks forbidden source text.
 * @param {string} source - Source text.
 * @param {string} contract - Forbidden contract.
 * @param {string} label - Source label.
 * @returns {void}
 * @collaboration Prevents fake chain ledger data and filesystem exports.
 */
function assertNotIncludes(source, contract, label) {
  assertCondition(!source.includes(contract), `${label} contains forbidden contract: ${contract}`);
}

/**
 * @function parseModule
 * @description Parses ESM JavaScript source.
 * @param {string} source - Source text.
 * @param {string} label - Source label.
 * @returns {void}
 * @collaboration Catches syntax errors before runtime.
 */
function parseModule(source, label) {
  parser.parse(source, {
    sourceType: 'module',
    plugins: [
      'importMeta',
      'dynamicImport',
      'classProperties',
      'objectRestSpread',
      'optionalChaining',
      'nullishCoalescingOperator',
      'topLevelAwait'
    ]
  });
  console.log(` - Parsed ${label}`);
}

/**
 * @function runGate
 * @description Runs the R68N regulator dossier chain ledger gate.
 * @returns {void}
 * @collaboration Verifies JSON-only dossier chain ledger contracts.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);

  [
    'WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERSION',
    'R68N-REGULATOR-DOSSIER-CHAIN-LEDGER-AUTHORITY',
    'resolveRegulatorDossierLedgerVerification',
    'resolveRegulatorDossierLedgerDossier',
    'buildRegulatorDossierLedgerLinkHashInput',
    'buildRegulatorDossierLedgerLink',
    'computeRegulatorDossierLedgerRoot',
    'verifyRegulatorDossierLedgerContinuity',
    'buildRegulatorDossierChainLedgerHashInput',
    'buildLeadSearchRegulatorDossierChainLedger',
    'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED',
    'REGULATOR_DOSSIER_LEDGER_ROOT_VERIFIED',
    'REGULATOR_DOSSIER_CHAIN_CONTINUITY_VERIFIED',
    'CRM_LEAD_SEARCH_REGULATOR_DOSSIER_CHAIN_LEDGER',
    'JSON_RESPONSE_ONLY',
    'noFilesystemWrite'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'WILSY_R68N_REGULATOR_DOSSIER_CHAIN_LEDGER_ROUTE_CONTRACT',
    'R68N-REGULATOR-DOSSIER-CHAIN-LEDGER-AUTHORITY',
    "router.get('/search/regulator-evidence/dossier-chain/latest'",
    'buildLeadSearchRegulatorDossierChainLedger'
  ].forEach((contract) => assertIncludes(route, contract, CRM_ROUTE));

  [
    'sourcebasis',
    'traceablethrough',
    'throughimmutable',
    'sampleLead',
    'sampleCustomer',
    'faker',
    'mockLead',
    'mockCustomer',
    'server/exports',
    'reports/',
    'fs.writeFileSync('
  ].forEach((contract) => {
    assertNotIncludes(service, contract, SEARCH_SERVICE);
    assertNotIncludes(route, contract, CRM_ROUTE);
  });

  console.log('PASS: WILSY CRM REGULATOR DOSSIER CHAIN LEDGER GATE');
  console.log(' - verified dossier ledger contracts present');
  console.log(' - ledger root contracts present');
  console.log(' - continuity proof contracts present');
  console.log(' - JSON response only contracts present');
  console.log(' - fake rows and filesystem exports blocked');
}

runGate();
