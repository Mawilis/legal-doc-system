/* eslint-disable */
import { existsSync, readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(import.meta.url);
const parser = require('../client/node_modules/@babel/parser');

const ROOT = process.cwd();
const ACCOUNT = 'client/src/components/account/WilsyAccountCommandCenter.jsx';
const INDEX_CSS = 'client/src/index.css';
const RENDERER = 'server/services/artifacts/wilsyEnterprisePdfRenderer.js';

/**
 * @function readText
 * @description Reads a repository-relative file as UTF-8 text.
 * @param {string} relativePath - Repository-relative file path.
 * @returns {string} File contents.
 * @collaboration Supplies source text to the Wilsy Account production gate without mutating files.
 */
function readText(relativePath) {
  const absolutePath = path.join(ROOT, relativePath);

  if (!existsSync(absolutePath)) {
    throw new Error(`Missing required file: ${relativePath}`);
  }

  return readFileSync(absolutePath, 'utf8');
}

/**
 * @function assertCondition
 * @description Throws when a production-readiness condition fails.
 * @param {boolean} condition - Condition result.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Provides hard-stop release protection for the Account export lane.
 */
function assertCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

/**
 * @function assertIncludes
 * @description Requires source text to include a production contract.
 * @param {string} source - Source text.
 * @param {string} needle - Required contract string.
 * @param {string} label - File label.
 * @returns {void}
 * @collaboration Locks critical Account Command Center export and proof contracts.
 */
function assertIncludes(source, needle, label) {
  assertCondition(source.includes(needle), `${label} missing required contract: ${needle}`);
}

/**
 * @function assertNotIncludes
 * @description Blocks known regression signatures from source text.
 * @param {string} source - Source text.
 * @param {string} needle - Forbidden regression string.
 * @param {string} label - File label.
 * @returns {void}
 * @collaboration Prevents repeat breakages such as duplicate exports, CORS headers and stuck button states.
 */
function assertNotIncludes(source, needle, label) {
  assertCondition(!source.includes(needle), `${label} contains forbidden regression: ${needle}`);
}

/**
 * @function parseAccountComponent
 * @description Parses the Account Command Center JSX with Babel.
 * @param {string} accountSource - Account component source.
 * @returns {void}
 * @collaboration Stops malformed JSX before Vite can load the dashboard.
 */
function parseAccountComponent(accountSource) {
  parser.parse(accountSource, {
    sourceType: 'module',
    plugins: [
      'jsx',
      'importMeta',
      'dynamicImport',
      'classProperties',
      'objectRestSpread',
      'optionalChaining',
      'nullishCoalescingOperator',
      'topLevelAwait'
    ]
  });
}

/**
 * @function assertCssImportOrder
 * @description Verifies CSS imports appear before body statements.
 * @param {string} cssSource - CSS source text.
 * @returns {void}
 * @collaboration Prevents the Vite CSS import-order regression from returning.
 */
function assertCssImportOrder(cssSource) {
  let seenBodyStatement = false;

  cssSource.split('\n').forEach((line, index) => {
    const stripped = line.trim();

    if (!stripped) return;
    if (stripped.startsWith('@charset')) return;

    if (stripped.startsWith('@import')) {
      assertCondition(!seenBodyStatement, `CSS @import appears after body statement at line ${index + 1}`);
      return;
    }

    seenBodyStatement = true;
  });
}

/**
 * @function assertAccountExportContracts
 * @description Verifies Account export, refresh, seal and proof-room contracts.
 * @param {string} accountSource - Account component source.
 * @returns {void}
 * @collaboration Freezes the current working Account Compliance export lane.
 */
function assertAccountExportContracts(accountSource) {
  [
    'export export',
    '/* eslint-disable */\\n',
    '\\nimport React',
    'disabled={forensicLoading || forensicExportLoading}',
    "'X-Artifact-Proof': requestProof",
    '"X-Artifact-Proof": requestProof',
    "'X-Request-Proof': requestProof",
    '"X-Request-Proof": requestProof',
    "'X-Request-Seal': requestProof",
    '"X-Request-Seal": requestProof'
  ].forEach((needle) => assertNotIncludes(accountSource, needle, ACCOUNT));

  [
    'downloadRegulatorPack',
    'refreshForensicProof',
    'requestBackendSeal',
    '/api/generate/pdf',
    'BRANDED_PDF_DOWNLOADED',
    'setForensicExportLoading(false);',
    '/wilsy-lab/forensic-merkle'
  ].forEach((needle) => assertIncludes(accountSource, needle, ACCOUNT));
}

/**
 * @function assertRendererSourceSafety
 * @description Verifies the renderer source is present and exposes the PDF stream contract without demanding generated PDF prose.
 * @param {string} rendererSource - Renderer source text.
 * @returns {void}
 * @collaboration Separates source architecture checks from runtime PDF evidence-output checks.
 */
function assertRendererSourceSafety(rendererSource) {
  [
    'streamEnterpriseArtifactPdf',
    'PDFDocument',
    'doc.end'
  ].forEach((needle) => assertIncludes(rendererSource, needle, RENDERER));
}

/**
 * @function runGate
 * @description Runs the Wilsy Account Command Center production gate.
 * @returns {void}
 * @collaboration Gives future Account/PDF changes a repeatable safety gate before release.
 */
function runGate() {
  const accountSource = readText(ACCOUNT);
  const cssSource = readText(INDEX_CSS);
  const rendererSource = readText(RENDERER);

  parseAccountComponent(accountSource);
  assertCssImportOrder(cssSource);
  assertAccountExportContracts(accountSource);
  assertRendererSourceSafety(rendererSource);

  console.log('PASS: WILSY ACCOUNT COMMAND CENTER PRODUCTION GATE');
  console.log(' - Account JSX parse valid');
  console.log(' - CSS import order valid');
  console.log(' - Refresh/Seal/Export regression signatures blocked');
  console.log(' - Browser proof custom headers blocked');
  console.log(' - PDF endpoint/proof-room contracts present');
  console.log(' - Renderer stream contract present');
}

runGate();
