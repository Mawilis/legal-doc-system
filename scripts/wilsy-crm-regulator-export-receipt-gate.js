/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM regulator export receipt materialization gate.
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
 * @param {string} relativePath - Repository-relative path.
 * @returns {string} Source text.
 * @collaboration Supplies source content for export receipt validation.
 */
function readText(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), 'utf8');
}

/**
 * @function assertCondition
 * @description Throws when a gate condition fails.
 * @param {boolean} condition - Condition to assert.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Blocks unsafe export receipt regressions.
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
 * @collaboration Locks export receipt materialization contracts.
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
 * @collaboration Prevents fake export receipt records.
 */
function assertNotIncludes(source, contract, label) {
  assertCondition(!source.includes(contract), `${label} contains forbidden contract: ${contract}`);
}

/**
 * @function parseModule
 * @description Parses an ESM JavaScript source file.
 * @param {string} source - Source text.
 * @param {string} label - Source label.
 * @returns {void}
 * @collaboration Catches syntax errors before backend runtime.
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
 * @description Runs the R68J export receipt materialization gate.
 * @returns {void}
 * @collaboration Validates CrmRecord export receipt persistence and ledger contracts.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);

  [
    'WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION',
    'R68J-REGULATOR-EXPORT-RECEIPT-MATERIALIZATION',
    'resolveRegulatorExportRecordModel',
    'resolveRegulatorExportRecordRequiredPathDefault',
    'hydrateRequiredRegulatorExportRecordFields',
    'buildRegulatorExportReceiptPayload',
    'buildRegulatorExportReceiptDocument',
    'persistLeadSearchRegulatorExportReceipt',
    'materializeLeadSearchRegulatorExportReceipt',
    'listLeadSearchRegulatorExportReceipts',
    'REGULATOR_EXPORT_RECEIPT_PERSISTED',
    'REGULATOR_EXPORT_RECEIPT_MATERIALIZED',
    'REGULATOR_EXPORT_RECEIPTS_LISTED',
    'CRM_LEAD_SEARCH_REGULATOR_EXPORT_RECEIPT',
    'CrmRecord'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'WILSY_R68J_REGULATOR_EXPORT_RECEIPT_ROUTE_CONTRACT',
    'R68J-REGULATOR-EXPORT-RECEIPT-MATERIALIZATION',
    "router.post('/search/regulator-evidence/:governanceId/receipt'",
    "router.get('/search/regulator-evidence/receipts/latest'",
    'materializeLeadSearchRegulatorExportReceipt',
    'listLeadSearchRegulatorExportReceipts'
  ].forEach((contract) => assertIncludes(route, contract, CRM_ROUTE));

  [
    'sourcebasis',
    'traceablethrough',
    'throughimmutable',
    'sampleLead',
    'sampleCustomer',
    'faker',
    'mockLead',
    'mockCustomer'
  ].forEach((contract) => {
    assertNotIncludes(service, contract, SEARCH_SERVICE);
    assertNotIncludes(route, contract, CRM_ROUTE);
  });

  console.log('PASS: WILSY CRM REGULATOR EXPORT RECEIPT GATE');
  console.log(' - CrmRecord export receipt materialization contracts present');
  console.log(' - export receipt ledger contracts present');
  console.log(' - fake rows blocked');
}

runGate();
