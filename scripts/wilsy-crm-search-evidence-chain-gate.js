/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM search evidence chain verification gate.
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
 * @collaboration Supplies source content for evidence chain validation.
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
 * @collaboration Blocks unsafe evidence chain regressions.
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
 * @collaboration Locks evidence chain contracts.
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
 * @collaboration Prevents fake evidence chain records.
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
 * @description Runs the R68F evidence chain gate.
 * @returns {void}
 * @collaboration Validates telemetry/compliance chain verification contracts.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);

  [
    'WILSY_CRM_SEARCH_EVIDENCE_CHAIN_VERSION',
    'R68F-SEARCH-EVIDENCE-CHAIN-AUTHORITY',
    'resolveReceiptIntegrityStatus',
    'buildReceiptChainLink',
    'verifyLeadSearchEvidenceChain',
    'listLeadSearchEvidenceChains',
    'SEARCH_EVIDENCE_CHAIN_VERIFIED',
    'SEARCH_EVIDENCE_CHAIN_PARTIAL',
    'SEARCH_EVIDENCE_CHAINS_LISTED',
    'CRM_LEAD_SEARCH_EVIDENCE_CHAIN',
    'rootHashLinked',
    'telemetryEventLinked',
    'telemetryHashLinked'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'WILSY_R68F_SEARCH_EVIDENCE_CHAIN_ROUTE_CONTRACT',
    'R68F-SEARCH-EVIDENCE-CHAIN-AUTHORITY',
    "router.get('/search/evidence-chain/:receiptId'",
    "router.get('/search/evidence-chains/latest'",
    'verifyLeadSearchEvidenceChain',
    'listLeadSearchEvidenceChains'
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

  console.log('PASS: WILSY CRM SEARCH EVIDENCE CHAIN GATE');
  console.log(' - telemetry/compliance link contracts present');
  console.log(' - evidence chain endpoint contracts present');
  console.log(' - root hash linkage contracts present');
  console.log(' - fake rows blocked');
}

runGate();
