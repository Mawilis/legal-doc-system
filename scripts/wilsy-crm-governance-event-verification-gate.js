/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM governance event verification gate.
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
 * @collaboration Supplies source content for governance verification validation.
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
 * @collaboration Blocks unsafe governance verification regressions.
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
 * @collaboration Locks governance verification contracts.
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
 * @collaboration Prevents fake governance verification records.
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
 * @description Runs the R68H governance event verification gate.
 * @returns {void}
 * @collaboration Validates governance event lookup, list endpoint and hash integrity contracts.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);

  [
    'WILSY_CRM_GOVERNANCE_EVENT_VERIFICATION_VERSION',
    'R68H-GOVERNANCE-EVENT-VERIFICATION-AUTHORITY',
    'buildGovernanceEventLookupFilter',
    'buildGovernanceEventListFilter',
    'extractGovernanceEventPayload',
    'computeGovernanceEventPayloadHash',
    'buildGovernanceEventIntegrityPacket',
    'normalizeLeadSearchGovernanceEvent',
    'findGovernanceEventByHashFallback',
    'verifyLeadSearchGovernanceEvent',
    'listLeadSearchGovernanceEvents',
    'GOVERNANCE_EVENT_HASH_VERIFIED',
    'GOVERNANCE_EVENT_FOUND',
    'GOVERNANCE_EVENTS_LISTED'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'WILSY_R68H_GOVERNANCE_EVENT_VERIFICATION_ROUTE_CONTRACT',
    'R68H-GOVERNANCE-EVENT-VERIFICATION-AUTHORITY',
    "router.get('/search/governance-event/:governanceId'",
    "router.get('/search/governance-events/latest'",
    'verifyLeadSearchGovernanceEvent',
    'listLeadSearchGovernanceEvents'
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

  console.log('PASS: WILSY CRM GOVERNANCE EVENT VERIFICATION GATE');
  console.log(' - governance event lookup contracts present');
  console.log(' - governance event ledger contracts present');
  console.log(' - governance hash integrity contracts present');
  console.log(' - fake rows blocked');
}

runGate();
