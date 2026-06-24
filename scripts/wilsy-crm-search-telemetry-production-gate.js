/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM search telemetry persistence production gate.
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
 * @collaboration Supplies source content for search telemetry validation.
 */
function readText(relativePath) {
  const absolutePath = path.join(ROOT, relativePath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`Missing required file: ${relativePath}`);
  }

  return fs.readFileSync(absolutePath, 'utf8');
}

/**
 * @function assertCondition
 * @description Throws when a gate condition fails.
 * @param {boolean} condition - Condition to assert.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Blocks unsafe CRM search telemetry regressions.
 */
function assertCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

/**
 * @function assertIncludes
 * @description Requires source text to include a contract string.
 * @param {string} source - Source text.
 * @param {string} contract - Required contract.
 * @param {string} label - Source label.
 * @returns {void}
 * @collaboration Locks search telemetry persistence contracts.
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
 * @collaboration Prevents fake search telemetry or placeholder records.
 */
function assertNotIncludes(source, contract, label) {
  assertCondition(!source.includes(contract), `${label} contains forbidden contract: ${contract}`);
}

/**
 * @function parseModule
 * @description Parses an ESM source file with Babel.
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
 * @function assertTelemetryDeclaredBeforeUse
 * @description Ensures telemetryPersistence is not referenced before declaration.
 * @param {string} source - Service source text.
 * @returns {void}
 * @collaboration Blocks temporal-dead-zone regressions in Lead search telemetry.
 */
function assertTelemetryDeclaredBeforeUse(source) {
  const functionStart = source.indexOf('export async function searchLeadOperatingRoom');
  const declaration = source.indexOf('const telemetryPersistence = await persistLeadSearchTelemetrySafely(telemetryParams);', functionStart);

  assertCondition(functionStart >= 0, 'searchLeadOperatingRoom function not found');
  assertCondition(declaration > functionStart, 'telemetryPersistence declaration not found');

  const beforeDeclaration = source.slice(functionStart, declaration);
  assertNotIncludes(beforeDeclaration, 'telemetryPersistence', SEARCH_SERVICE);
}

/**
 * @function runGate
 * @description Runs the canonical R68B.5 CRM search telemetry production gate.
 * @returns {void}
 * @collaboration Validates telemetry persistence, breaker isolation, canonical reset and no TDZ references.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);
  assertTelemetryDeclaredBeforeUse(service);

  [
    'WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION',
    'R68B-SEARCH-TELEMETRY-PERSISTENCE',
    'WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION',
    'R68B.1-SEARCH-TELEMETRY-BREAKER',
    'WILSY_CRM_SEARCH_FUNCTION_REWRITE_VERSION',
    'R68B.4-SEARCH-FUNCTION-REWRITE',
    'WILSY_CRM_SEARCH_CANONICAL_RESET_VERSION',
    'R68B.5-CANONICAL-SERVICE-RESET',
    'persistLeadSearchTelemetrySafely',
    'const telemetryParams = {',
    'const telemetryPersistence = await persistLeadSearchTelemetrySafely(telemetryParams);',
    'telemetryCanonicalResetVersion: WILSY_CRM_SEARCH_CANONICAL_RESET_VERSION',
    'telemetryPersisted: Boolean(telemetryPersistence?.persisted)',
    'telemetryReceiptHashShort: telemetryPersistence?.receiptHashShort || null'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION',
    'WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION',
    'WILSY_R68B1_SEARCH_TELEMETRY_BREAKER_ROUTE_CONTRACT',
    'telemetryRouteVersion',
    'telemetryRouteContract',
    'telemetryBreakerVersion',
    'telemetryBreakerContract'
  ].forEach((contract) => assertIncludes(route, contract, CRM_ROUTE));

  [
    'Institutional Finality Breach',
    'sampleLead',
    'sampleCustomer',
    'faker',
    'mockLead',
    'mockCustomer'
  ].forEach((contract) => {
    assertNotIncludes(service, contract, SEARCH_SERVICE);
    assertNotIncludes(route, contract, CRM_ROUTE);
  });

  console.log('PASS: WILSY CRM SEARCH TELEMETRY PRODUCTION GATE');
  console.log(' - canonical R68B.5 search service reset present');
  console.log(' - telemetryPersistence declared before use');
  console.log(' - telemetry breaker contracts present');
  console.log(' - fake rows blocked');
}

runGate();
