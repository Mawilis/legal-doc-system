/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM regulator evidence export authority gate.
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
 * @collaboration Supplies source content for regulator export validation.
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
 * @collaboration Blocks unsafe regulator export regressions.
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
 * @collaboration Locks regulator evidence export contracts.
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
 * @collaboration Prevents fake regulator evidence exports.
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
 * @description Runs the R68I regulator evidence export gate.
 * @returns {void}
 * @collaboration Validates regulator bundle export, ledger and hash contracts.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);

  [
    'WILSY_CRM_REGULATOR_EVIDENCE_EXPORT_VERSION',
    'R68I-REGULATOR-EVIDENCE-EXPORT-AUTHORITY',
    'buildRegulatorEvidenceHashInput',
    'buildRegulatorEvidenceBundleCore',
    'sealRegulatorEvidenceBundle',
    'exportLeadSearchRegulatorEvidenceBundle',
    'listLeadSearchRegulatorEvidenceBundles',
    'REGULATOR_EVIDENCE_BUNDLE_READY',
    'REGULATOR_EVIDENCE_EXPORT_VERIFIED',
    'REGULATOR_EVIDENCE_BUNDLES_LISTED',
    'CRM_LEAD_SEARCH_REGULATOR_EVIDENCE_BUNDLE',
    'persistenceMode',
    'JSON_RESPONSE_ONLY'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'WILSY_R68I_REGULATOR_EVIDENCE_EXPORT_ROUTE_CONTRACT',
    'R68I-REGULATOR-EVIDENCE-EXPORT-AUTHORITY',
    "router.get('/search/regulator-evidence/:governanceId'",
    "router.get('/search/regulator-evidence/latest'",
    'exportLeadSearchRegulatorEvidenceBundle',
    'listLeadSearchRegulatorEvidenceBundles'
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

  console.log('PASS: WILSY CRM REGULATOR EVIDENCE EXPORT GATE');
  console.log(' - regulator bundle export contracts present');
  console.log(' - regulator bundle ledger contracts present');
  console.log(' - export hash contracts present');
  console.log(' - JSON response only, no file exports required');
  console.log(' - fake rows blocked');
}

runGate();
