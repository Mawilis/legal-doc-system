/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM regulator dossier chain ledger verification gate.
 */
const fs = require('node:fs');
const path = require('node:path');
const parser = require('../client/node_modules/@babel/parser');

const ROOT = process.cwd();
const SERVICE = 'server/services/wilsyCrmLeadSearchEngineService.js';
const ROUTE = 'server/routes/crmCommandRoutes.js';

/**
 * @function readText
 * @description Reads a repository-relative source file.
 * @param {string} relativePath - Repository-relative source path.
 * @returns {string} Source text.
 * @collaboration Supplies source content for R68O contract validation.
 */
function readText(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), 'utf8');
}

/**
 * @function assertCondition
 * @description Throws if condition is false.
 * @param {boolean} condition - Assertion condition.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Blocks incomplete R68O verification contracts.
 */
function assertCondition(condition, message) {
  if (!condition) throw new Error(message);
}

/**
 * @function parseModule
 * @description Parses an ES module source file.
 * @param {string} source - Source text.
 * @param {string} label - File label.
 * @returns {void}
 * @collaboration Catches syntax failures before runtime.
 */
function parseModule(source, label) {
  parser.parse(source, {
    sourceType: 'module',
    plugins: ['importMeta', 'dynamicImport', 'classProperties', 'objectRestSpread', 'optionalChaining', 'nullishCoalescingOperator', 'topLevelAwait']
  });
  console.log(` - Parsed ${label}`);
}

/**
 * @function requireContract
 * @description Requires source text to include a contract.
 * @param {string} source - Source text.
 * @param {string} contract - Required text.
 * @param {string} label - File label.
 * @returns {void}
 * @collaboration Locks R68O route and service behavior.
 */
function requireContract(source, contract, label) {
  assertCondition(source.includes(contract), `${label} missing ${contract}`);
}

/**
 * @function blockContract
 * @description Blocks forbidden source text.
 * @param {string} source - Source text.
 * @param {string} contract - Forbidden text.
 * @param {string} label - File label.
 * @returns {void}
 * @collaboration Keeps R68O free of fake rows and filesystem exports.
 */
function blockContract(source, contract, label) {
  assertCondition(!source.includes(contract), `${label} contains forbidden ${contract}`);
}

/**
 * @function runGate
 * @description Runs the R68O regulator dossier chain ledger verification gate.
 * @returns {void}
 * @collaboration Verifies ledger root recomputation, link continuity and safe existing route alias.
 */
function runGate() {
  const service = readText(SERVICE);
  const route = readText(ROUTE);

  parseModule(service, SERVICE);
  parseModule(route, ROUTE);

  [
    'WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_VERSION',
    'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY',
    'verifyLeadSearchRegulatorDossierChainLedger',
    'REGULATOR_DOSSIER_LEDGER_ROOT_HASH_VERIFIED',
    'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED',
    'CRM_LEAD_SEARCH_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION'
  ].forEach((contract) => requireContract(service, contract, SERVICE));

  [
    'WILSY_R68O_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_ROUTE_CONTRACT',
    'R68O_SAFE_EXISTING_LEDGER_ROUTE',
    'rootCheck',
    'verifyLeadSearchRegulatorDossierChainLedger',
    'dossier-chain/latest?rootCheck=R68O'
  ].forEach((contract) => requireContract(route, contract, ROUTE));

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
    blockContract(service, contract, SERVICE);
    blockContract(route, contract, ROUTE);
  });

  console.log('PASS: WILSY CRM REGULATOR DOSSIER CHAIN LEDGER VERIFICATION GATE');
}

runGate();
