/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM search compliance receipt materialization gate.
 */
const fs = require('node:fs');
const path = require('node:path');
const parser = require('../client/node_modules/@babel/parser');

const ROOT = process.cwd();
const SEARCH_SERVICE = 'server/services/wilsyCrmLeadSearchEngineService.js';

/**
 * @function readText
 * @description Reads a repository-relative source file.
 * @param {string} relativePath - Repository-relative path.
 * @returns {string} Source text.
 * @collaboration Supplies source content for compliance receipt validation.
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
 * @collaboration Blocks unsafe compliance receipt regressions.
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
 * @collaboration Locks search compliance receipt contracts.
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
 * @collaboration Prevents wording, fake-data and placeholder regressions.
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
 * @description Runs the R68D search compliance receipt materialization gate.
 * @returns {void}
 * @collaboration Validates CRMComplianceReceipt materialization contracts.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);

  parseModule(service, SEARCH_SERVICE);

  [
    'WILSY_CRM_SEARCH_COMPLIANCE_RECEIPT_VERSION',
    'R68D-SEARCH-COMPLIANCE-RECEIPT-MATERIALIZATION',
    'resolveComplianceReceiptModel',
    'resolveComplianceRequiredPathDefault',
    'hydrateRequiredComplianceReceiptFields',
    'buildLeadSearchComplianceReceiptPayload',
    'buildComplianceReceiptDocument',
    'persistLeadSearchComplianceReceipt',
    'persistLeadSearchComplianceReceiptSafely',
    'COMPLIANCE_RECEIPT_PERSISTED',
    'COMPLIANCE_RECEIPT_WRITE_FAILED',
    'CRMComplianceReceipt',
    'SEARCH_SOURCE_BASIS_RECEIPT_CREATED',
    'SEARCH_LAWFUL_BASIS_RECEIPT_CREATED',
    'SEARCH_AUDIT_CHAIN_RECEIPT_CREATED',
    'SEARCH_RECEIPT_READY_FOR_REGULATOR_REVIEW',
    'const complianceReceiptPersistence = await persistLeadSearchComplianceReceiptSafely',
    'complianceReceiptPersisted',
    'complianceReceiptHashShort',
    'source basis',
    'traceable through'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'sourcebasis',
    'traceablethrough',
    'throughimmutable',
    'sampleLead',
    'sampleCustomer',
    'faker',
    'mockLead',
    'mockCustomer'
  ].forEach((contract) => assertNotIncludes(service, contract, SEARCH_SERVICE));

  console.log('PASS: WILSY CRM SEARCH COMPLIANCE RECEIPT GATE');
  console.log(' - CRMComplianceReceipt materialization contracts present');
  console.log(' - response exposes complianceReceiptPersistence');
  console.log(' - future compliance wording clean');
  console.log(' - fake rows blocked');
}

runGate();
