/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM search receipt verification production gate.
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
 * @collaboration Supplies source content for receipt verification validation.
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
 * @collaboration Blocks unsafe receipt verification regressions.
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
 * @collaboration Locks receipt verification contracts.
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
 * @collaboration Prevents fake receipt verification records.
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
 * @description Runs the R68C.1 receipt verification gate.
 * @returns {void}
 * @collaboration Validates search receipt lookup, list endpoint and hash integrity contracts.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);

  [
    'WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION',
    'R68C.1-SEARCH-RECEIPT-VERIFICATION-SAFE',
    'buildTelemetryReceiptFilter',
    'buildTelemetryReceiptListFilter',
    'extractTelemetryPayload',
    'computeTelemetryPayloadHash',
    'buildReceiptIntegrityPacket',
    'findReceiptByHashFallback',
    'normalizeLeadSearchReceipt',
    'verifyLeadSearchTelemetryReceipt',
    'listLeadSearchTelemetryReceipts',
    'RECEIPT_HASH_VERIFIED',
    'RECEIPT_HASH_RECOMPUTED',
    'SEARCH_RECEIPT_FOUND',
    'SEARCH_RECEIPTS_LISTED',
    'through immutable operational telemetry'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'WILSY_R68C_SEARCH_RECEIPT_VERIFICATION_ROUTE_CONTRACT',
    'R68C.1-SEARCH-RECEIPT-VERIFICATION-SAFE',
    "router.get('/search/receipt/:receiptId'",
    "router.get('/search/receipts/latest'",
    'verifyLeadSearchTelemetryReceipt',
    'listLeadSearchTelemetryReceipts'
  ].forEach((contract) => assertIncludes(route, contract, CRM_ROUTE));

  [
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

  console.log('PASS: WILSY CRM SEARCH RECEIPT VERIFICATION GATE');
  console.log(' - receipt lookup contracts present');
  console.log(' - recent receipt ledger contracts present');
  console.log(' - hash fallback verification contracts present');
  console.log(' - fake rows blocked');
}

runGate();
