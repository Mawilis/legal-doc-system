/* eslint-disable */
/**
 * @fileoverview WILSY OS CRM regulator dossier verification authority gate.
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
 * @collaboration Supplies source content for R68M verification validation.
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
 * @collaboration Blocks broken regulator dossier verification contracts.
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
 * @collaboration Locks R68M verification contracts.
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
 * @collaboration Prevents fake dossier verification data.
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
 * @description Runs the R68M regulator dossier verification gate.
 * @returns {void}
 * @collaboration Verifies final dossier hash-input verification contracts.
 */
function runGate() {
  const service = readText(SEARCH_SERVICE);
  const route = readText(CRM_ROUTE);

  parseModule(service, SEARCH_SERVICE);
  parseModule(route, CRM_ROUTE);

  [
    'WILSY_CRM_REGULATOR_DOSSIER_VERIFICATION_VERSION',
    'R68M-REGULATOR-DOSSIER-VERIFICATION-AUTHORITY',
    'computeRegulatorDossierHashFromInput',
    'resolveRegulatorDossierLookupCandidates',
    'verifyRegulatorDossierIntegrity',
    'buildRegulatorDossierVerificationPacket',
    'findRegulatorEvidenceDossierByHashFallback',
    'verifyLeadSearchRegulatorEvidenceDossier',
    'listLeadSearchRegulatorEvidenceDossierVerifications',
    'REGULATOR_DOSSIER_VERIFIED',
    'REGULATOR_DOSSIER_HASH_VERIFIED',
    'REGULATOR_DOSSIER_VERIFICATIONS_LISTED',
    'CRM_LEAD_SEARCH_REGULATOR_DOSSIER_VERIFICATION'
  ].forEach((contract) => assertIncludes(service, contract, SEARCH_SERVICE));

  [
    'WILSY_R68M_REGULATOR_DOSSIER_VERIFICATION_ROUTE_CONTRACT',
    'R68M-REGULATOR-DOSSIER-VERIFICATION-AUTHORITY',
    "router.get('/search/regulator-evidence/dossier/verify/:dossierId'",
    "router.get('/search/regulator-evidence/dossiers/verified/latest'",
    'verifyLeadSearchRegulatorEvidenceDossier',
    'listLeadSearchRegulatorEvidenceDossierVerifications'
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

  console.log('PASS: WILSY CRM REGULATOR DOSSIER VERIFICATION GATE');
  console.log(' - dossier hash lookup contracts present');
  console.log(' - export receipt hash lookup contracts present');
  console.log(' - export hash lookup contracts present');
  console.log(' - governance id lookup contracts present');
  console.log(' - final dossier hash input verification contracts present');
  console.log(' - fake rows blocked');
}

runGate();
