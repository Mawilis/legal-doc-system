/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM compliance receipt verification gate.
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
 * @collaboration Supplies source content for compliance receipt verification validation.
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
 * @collaboration Blocks unsafe compliance verification regressions.
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
 * @collaboration Locks compliance receipt verification contracts.
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
 * @collaboration Prevents fake compliance receipt verification records.
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
 * @description Runs the R68E compliance receipt verification gate.
 * @returns {void}
 * @collaboration Validates compliance receipt lookup, list endpoint and integrity contracts.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);

  [
    'WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION',
    'R68E-COMPLIANCE-RECEIPT-VERIFICATION-AUTHORITY',
    'buildComplianceReceiptLookupFilter',
    'buildComplianceReceiptListFilter',
    'extractComplianceReceiptPayload',
    'computeComplianceReceiptPayloadHash',
    'buildComplianceReceiptIntegrityPacket',
    'normalizeSearchComplianceReceipt',
    'findComplianceReceiptByHashFallback',
    'verifyLeadSearchComplianceReceipt',
    'listLeadSearchComplianceReceipts',
    'COMPLIANCE_RECEIPT_HASH_VERIFIED',
    'COMPLIANCE_RECEIPT_FOUND',
    'COMPLIANCE_RECEIPTS_LISTED'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'WILSY_R68E_COMPLIANCE_RECEIPT_VERIFICATION_ROUTE_CONTRACT',
    'R68E-COMPLIANCE-RECEIPT-VERIFICATION-AUTHORITY',
    "router.get('/search/compliance-receipt/:receiptId'",
    "router.get('/search/compliance-receipts/latest'",
    'verifyLeadSearchComplianceReceipt',
    'listLeadSearchComplianceReceipts'
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

  console.log('PASS: WILSY CRM COMPLIANCE RECEIPT VERIFICATION GATE');
  console.log(' - compliance receipt lookup contracts present');
  console.log(' - compliance receipt ledger contracts present');
  console.log(' - compliance receipt hash integrity contracts present');
  console.log(' - fake rows blocked');
}

runGate();
