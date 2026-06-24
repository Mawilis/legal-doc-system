/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM regulator export receipt verification gate.
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
 * @collaboration Supplies source content for R68K verification validation.
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
 * @collaboration Blocks broken regulator export receipt verification contracts.
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
 * @collaboration Locks R68K verification contracts.
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
 * @collaboration Prevents fake receipt verification data.
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
 * @description Runs the R68K regulator export receipt verification gate.
 * @returns {void}
 * @collaboration Verifies id/hash/exportHash lookup and regulator export integrity contracts.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);

  [
    'WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERIFICATION_VERSION',
    'R68K-REGULATOR-EXPORT-RECEIPT-VERIFICATION-AUTHORITY',
    'resolveRegulatorExportReceiptFieldValue',
    'extractRegulatorExportReceiptPayload',
    'computeRegulatorExportReceiptPayloadHash',
    'verifyRegulatorExportIntegrityFromReceiptPayload',
    'buildRegulatorExportReceiptLookupFilter',
    'normalizeLeadSearchRegulatorExportReceipt',
    'findRegulatorExportReceiptByHashFallback',
    'verifyLeadSearchRegulatorExportReceipt',
    'listLeadSearchRegulatorExportReceiptVerifications',
    'REGULATOR_EXPORT_RECEIPT_FOUND',
    'REGULATOR_EXPORT_RECEIPT_HASH_VERIFIED',
    'REGULATOR_EXPORT_HASH_VERIFIED',
    'REGULATOR_EXPORT_RECEIPT_VERIFICATIONS_LISTED'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'WILSY_R68K_REGULATOR_EXPORT_RECEIPT_VERIFICATION_ROUTE_CONTRACT',
    'R68K-REGULATOR-EXPORT-RECEIPT-VERIFICATION-AUTHORITY',
    "router.get('/search/regulator-evidence/receipt/:receiptId'",
    "router.get('/search/regulator-evidence/receipts/verified/latest'",
    'verifyLeadSearchRegulatorExportReceipt',
    'listLeadSearchRegulatorExportReceiptVerifications'
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

  console.log('PASS: WILSY CRM REGULATOR EXPORT RECEIPT VERIFICATION GATE');
}

runGate();
