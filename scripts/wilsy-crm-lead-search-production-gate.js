/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM Lead Search backend production gate.
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
 * @collaboration Supplies the Lead search production gate with source content.
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
 * @description Throws when a production gate condition fails.
 * @param {boolean} condition - Condition to assert.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Blocks unsafe Lead search backend regressions.
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
 * @param {string} contract - Required contract string.
 * @param {string} label - Source label.
 * @returns {void}
 * @collaboration Locks backend search authority contracts.
 */
function assertIncludes(source, contract, label) {
  assertCondition(source.includes(contract), `${label} missing contract: ${contract}`);
}

/**
 * @function assertNotIncludes
 * @description Blocks forbidden source text.
 * @param {string} source - Source text.
 * @param {string} contract - Forbidden contract string.
 * @param {string} label - Source label.
 * @returns {void}
 * @collaboration Prevents fake-data and unsafe route regressions.
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
 * @collaboration Catches syntax failures before server runtime.
 */
function parseModule(source, label) {
  parser.parse(source, {
    sourceType: 'module',
    plugins: ['importMeta', 'dynamicImport', 'classProperties', 'objectRestSpread', 'optionalChaining', 'nullishCoalescingOperator', 'topLevelAwait']
  });

  console.log(` - Parsed ${label}`);
}

/**
 * @function runGate
 * @description Runs the R68A backend Lead search production gate.
 * @returns {void}
 * @collaboration Validates tenant-scoped search, source registry telemetry, compliance bindings and provenance root hash.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);

  [
    'WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION',
    'R68A-BACKEND-LEAD-SEARCH-AUTHORITY',
    'SOURCE_REGISTRY',
    'COMPLIANCE_BINDINGS',
    'escapeRegex',
    'createHashDigest',
    'buildTenantFilter',
    'buildSearchFilter',
    'buildModelFilter',
    'safeCountDocuments',
    'safeFindDocuments',
    'normalizeLeadSearchRow',
    'buildSearchRootHash',
    'searchLeadOperatingRoom',
    'LEAD_OPERATING_ROOM_BACKEND_AUTHORITY',
    'rootHashShort',
    'complianceBindings'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    "router.get('/search'",
    'WILSY_R68A_BACKEND_LEAD_SEARCH_ROUTE_CONTRACT',
    'searchLeadOperatingRoom',
    'routeVersion: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION',
    'routeContract: WILSY_R68A_BACKEND_LEAD_SEARCH_ROUTE_CONTRACT'
  ].forEach((contract) => assertIncludes(route, contract, CRM_ROUTE));

  [
    'sampleLead',
    'sampleCustomer',
    'faker',
    'mockLead',
    'mockCustomer'
  ].forEach((contract) => {
    assertNotIncludes(service, contract, SEARCH_SERVICE);
    assertNotIncludes(route, contract, CRM_ROUTE);
  });

  console.log('PASS: WILSY CRM LEAD SEARCH PRODUCTION GATE');
  console.log(' - /api/crm/command/search upgraded');
  console.log(' - tenant-scoped backend search contracts present');
  console.log(' - source telemetry contracts present');
  console.log(' - provenance root hash contracts present');
  console.log(' - compliance binding contracts present');
  console.log(' - fake rows blocked');
}

runGate();
/**
 * @function runR68BSearchTelemetryExtensionGate
 * @description Validates R68B telemetry persistence contracts from the R68A search gate.
 * @returns {void}
 * @collaboration Keeps the search gate aware that every search is now auditable.
 */
function runR68BSearchTelemetryExtensionGate() {
  const service = fs.readFileSync(path.join(ROOT, 'server/services/wilsyCrmLeadSearchEngineService.js'), 'utf8');
  const route = fs.readFileSync(path.join(ROOT, 'server/routes/crmCommandRoutes.js'), 'utf8');

  [
    'WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION',
    'R68B-SEARCH-TELEMETRY-PERSISTENCE',
    'persistLeadSearchTelemetry',
    'telemetryPersistence',
    'telemetryPersisted',
    'telemetryReceiptHashShort'
  ].forEach((contract) => assertIncludes(service, contract, 'server/services/wilsyCrmLeadSearchEngineService.js'));

  [
    'WILSY_R68B_SEARCH_TELEMETRY_ROUTE_CONTRACT',
    'telemetryRouteVersion',
    'telemetryRouteContract'
  ].forEach((contract) => assertIncludes(route, contract, 'server/routes/crmCommandRoutes.js'));

  console.log(' - R68B search telemetry persistence extension valid');
}

runR68BSearchTelemetryExtensionGate();
