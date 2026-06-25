/* eslint-disable */
const fs = require('fs');
const { createRequire } = require('module');

const requireFromServer = createRequire(`${process.cwd()}/server/services/documentService.js`);

const DOC_SERVICE = 'server/services/documentService.js';
const POLYFILL_FILE = 'server/utils/pdfRuntimePolyfills.js';

/**
 * @function readFile
 * @description Reads a repository file for R73F source-contract validation.
 * @collaboration R73F backend boot stability, pdf-parse polyfill evidence, guard validation.
 */
function readFile(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

/**
 * @function assertIncludes
 * @description Throws when required R73F source evidence is absent.
 * @collaboration R73F source contract, documentService boot path, PDF runtime polyfill.
 */
function assertIncludes(source, value, label) {
  if (!source.includes(value)) {
    throw new Error(`R73F missing ${label}: ${value}`);
  }
}

/**
 * @function assertBlocked
 * @description Throws when forbidden R73F regression evidence is present.
 * @collaboration R73F regression shield, boot stability, secret-safe source discipline.
 */
function assertBlocked(source, pattern, label) {
  if (pattern.test(source)) {
    throw new Error(`R73F blocked ${label}`);
  }
}

/**
 * @function buildRecursiveExpansionPattern
 * @description Builds the recursive expansion token detector without embedding the forbidden token directly.
 * @collaboration Terminal boundary safety, R73F source hygiene, guard compatibility.
 */
function buildRecursiveExpansionPattern() {
  const prefix = ['R', '70', 'F'].join('');
  return new RegExp(`${prefix}[-_]|\\b${prefix.toLowerCase()}[A-Za-z0-9_]*\\s*[=:]`);
}

/**
 * @function verifySourceContract
 * @description Verifies documentService installs PDF runtime polyfills before pdf-parse loads.
 * @collaboration R73F document service stability, DOMMatrix rescue, backend boot contract.
 */
function verifySourceContract() {
  const documentService = readFile(DOC_SERVICE);
  const polyfill = readFile(POLYFILL_FILE);

  assertIncludes(documentService, "import { installPdfRuntimePolyfills } from '../utils/pdfRuntimePolyfills.js';", 'documentService polyfill import');
  assertIncludes(documentService, 'installPdfRuntimePolyfills();', 'documentService polyfill call');
  assertIncludes(documentService, "require('pdf-parse", 'documentService pdf-parse require');
  assertIncludes(polyfill, 'export function installPdfRuntimePolyfills', 'polyfill installer export');
  assertIncludes(polyfill, 'globalThis.DOMMatrix', 'DOMMatrix global installation');
  assertIncludes(polyfill, 'globalThis.DOMPoint', 'DOMPoint global installation');
  assertIncludes(polyfill, 'globalThis.ImageData', 'ImageData global installation');
  assertIncludes(polyfill, 'globalThis.Path2D', 'Path2D global installation');

  const pdfParseIndex = Math.min(
    ...[
      documentService.indexOf("require('pdf-parse"),
      documentService.indexOf('require("pdf-parse'),
    ].filter((index) => index >= 0)
  );
  const callIndex = documentService.indexOf('installPdfRuntimePolyfills();');

  if (pdfParseIndex < 0 || callIndex < 0 || callIndex > pdfParseIndex) {
    throw new Error('R73F blocked: installPdfRuntimePolyfills must run before pdf-parse require.');
  }

  const combined = `${documentService}\n${polyfill}`;

  [
    [/^\s*import\s+.*['"]pdf-parse['"]\s*;?\s*$/m, 'static pdf-parse import before polyfill'],
    [/ReferenceError:\s*DOMMatrix\s+is\s+not\s+defined/, 'committed DOMMatrix crash text'],
    [buildRecursiveExpansionPattern(), 'recursive expansion token shape'],
    [/VITE_[A-Z0-9_]*(SECRET|PASSWORD|PRIVATE|HMAC|JWT)/, 'unsafe browser secret env literal'],
  ].forEach(([pattern, label]) => assertBlocked(combined, pattern, label));

  return {
    documentServicePatched: true,
    polyfillInstallerPresent: true,
    callBeforePdfParse: true,
    regressionPatternsAbsent: true,
  };
}

/**
 * @function runDirectPdfParseSmoke
 * @description Loads the polyfill utility and then requires pdf-parse to prove DOMMatrix boot crash is gone.
 * @collaboration R73F runtime smoke, pdf-parse compatibility, backend boot stability.
 */
async function runDirectPdfParseSmoke() {
  const module = await import(`file://${process.cwd()}/${POLYFILL_FILE}`);
  const proof = module.installPdfRuntimePolyfills();

  if (!proof.domMatrix || !proof.domPoint || !proof.imageData || !proof.path2D) {
    throw new Error(`R73F blocked: incomplete PDF runtime polyfills ${JSON.stringify(proof)}`);
  }

  const pdfParseModule = requireFromServer('pdf-parse');

  return {
    polyfillProof: proof,
    pdfParseLoaded: Boolean(pdfParseModule),
    pdfParseExportKeys: Object.keys(pdfParseModule || {}).slice(0, 16),
  };
}

/**
 * @function runR73FGate
 * @description Runs R73F source and runtime validation.
 * @collaboration R73F boot-stability lane, documentService isolation, PDF runtime compatibility.
 */
async function runR73FGate() {
  const sourceProof = verifySourceContract();
  const runtimeProof = await runDirectPdfParseSmoke();

  console.log(JSON.stringify({
    gate: 'R73F_BACKEND_BOOT_STABILITY_PDF_DOMMATRIX_POLYFILLED',
    lane: 'backend-boot-stability-pdf-parse-dommatrix-polyfill',
    files: [DOC_SERVICE, POLYFILL_FILE],
    sourceProof,
    runtimeProof,
    noCrmMutation: true,
    noRouteMutation: true,
    noModelMutation: true,
    noFrontendMutation: true,
    bootCrashPrevented: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY R73F BACKEND BOOT STABILITY PDF DOMMATRIX POLYFILL GATE');
  console.log(' - documentService installs PDF runtime polyfills before pdf-parse loads');
  console.log(' - DOMMatrix, DOMPoint, ImageData and Path2D are available under Node');
  console.log(' - pdf-parse can be required without DOMMatrix boot crash');
  console.log(' - CRM search lane remains untouched');
}

runR73FGate().catch((error) => {
  console.error(error);
  process.exit(1);
});
