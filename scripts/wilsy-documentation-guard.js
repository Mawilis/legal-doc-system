/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DOCUMENTATION GUARD [V1.0.0-GENERATIONAL-STANDARD]                                                                         ║
 * ║ [ESLINT HEADER ENFORCEMENT | JSDOC FUNCTION CHECK | COLLABORATION COMMENT CHECK | FUTURE MAINTAINER PROTECTION]                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-GENERATIONAL-STANDARD | PRODUCTION READY | REPO DOCUMENTATION AUDIT TOOL                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/scripts/wilsy-documentation-guard.js                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated every Wilsy OS file to start with eslint disable and carry generational documentation.    ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Added an audit guard that detects missing headers, JSDoc markers and collaboration notes.     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

const fs = require('node:fs');
const path = require('node:path');

const REQUIRED_FIRST_LINE = '/* eslint-disable */';
const DEFAULT_SCAN_ROOTS = ['client/src', 'server', 'scripts'];
const SKIP_SEGMENTS = new Set([
  'node_modules',
  'dist',
  'build',
  'coverage',
  '.git',
  '.next',
  '.cache'
]);
const JS_EXTENSIONS = new Set(['.js', '.jsx', '.mjs', '.cjs']);
const DOCUMENTABLE_FUNCTION_PATTERN = /\b(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(|\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)/g;

/**
 * @function resolveScanRoots
 * @description Resolves CLI-provided scan roots or falls back to Wilsy OS source roots.
 * @param {Array<string>} args - Command-line arguments.
 * @returns {Array<string>} Absolute scan roots.
 * @collaboration Lets future maintainers audit targeted shards or the default Wilsy OS source surface.
 */
const resolveScanRoots = (args = []) => {
  const roots = args.length ? args : DEFAULT_SCAN_ROOTS;
  return roots
    .map(root => path.resolve(process.cwd(), root))
    .filter(root => fs.existsSync(root));
};

/**
 * @function shouldSkipPath
 * @description Determines whether a path belongs to generated or dependency output that should not be audited.
 * @param {string} candidatePath - Candidate path.
 * @returns {boolean} True when the path should be skipped.
 * @collaboration Keeps the guard focused on Wilsy OS source code instead of third-party or generated files.
 */
const shouldSkipPath = (candidatePath = '') => (
  candidatePath
    .split(path.sep)
    .some(segment => SKIP_SEGMENTS.has(segment))
);

/**
 * @function collectSourceFiles
 * @description Recursively collects JavaScript source files under a scan root.
 * @param {string} root - Absolute scan root.
 * @returns {Array<string>} Source file paths.
 * @collaboration Gives the documentation standard a deterministic source inventory.
 */
const collectSourceFiles = (root) => {
  if (shouldSkipPath(root)) return [];
  if (!fs.existsSync(root)) return [];
  let stat;
  try {
    stat = fs.statSync(root);
  } catch {
    return [];
  }
  if (stat.isFile()) {
    return JS_EXTENSIONS.has(path.extname(root)) ? [root] : [];
  }
  try {
    return fs.readdirSync(root).flatMap(entry => collectSourceFiles(path.join(root, entry)));
  } catch {
    return [];
  }
};

/**
 * @function findDocumentableFunctions
 * @description Finds named functions, helpers, hooks and components that require adjacent JSDoc.
 * @param {string} source - File source text.
 * @returns {Array<{name:string,index:number}>} Documentable function records.
 * @collaboration Makes Wilson's documentation mandate enforceable at function level instead of accepting one file-level marker.
 */
const findDocumentableFunctions = (source = '') => {
  const functions = [];
  DOCUMENTABLE_FUNCTION_PATTERN.lastIndex = 0;
  let match = DOCUMENTABLE_FUNCTION_PATTERN.exec(source);
  while (match) {
    functions.push({
      name: match[1] || match[2],
      index: match.index
    });
    match = DOCUMENTABLE_FUNCTION_PATTERN.exec(source);
  }
  return functions;
};

/**
 * @function hasAdjacentJSDoc
 * @description Verifies that a named function has an immediately preceding JSDoc block with required Wilsy markers.
 * @param {string} source - File source text.
 * @param {number} functionIndex - Character index where the function declaration starts.
 * @returns {boolean} True when the adjacent JSDoc satisfies the standard.
 * @collaboration Prevents disconnected comments from satisfying documentation requirements for unrelated functions.
 */
const hasAdjacentJSDoc = (source = '', functionIndex = 0) => {
  const before = source.slice(Math.max(0, functionIndex - 1600), functionIndex).replace(/\bexport\s+(default\s+)?$/, '');
  const jsdocMatch = before.match(/\/\*\*[\s\S]*?\*\/\s*$/);
  if (!jsdocMatch) return false;
  const block = jsdocMatch[0];
  return block.includes('@function') && block.includes('@description') && block.includes('@collaboration');
};

/**
 * @function auditFile
 * @description Audits one file for the Wilsy OS documentation standard.
 * @param {string} filePath - Absolute file path.
 * @returns {{filePath:string,violations:Array<string>}} Audit result.
 * @collaboration Produces precise violations so future maintainers can repair files without guessing.
 */
const auditFile = (filePath) => {
  const source = fs.readFileSync(filePath, 'utf8');
  const firstLine = source.split(/\r?\n/)[0];
  const violations = [];

  if (firstLine !== REQUIRED_FIRST_LINE) {
    violations.push(`FIRST_LINE_REQUIRED: ${REQUIRED_FIRST_LINE}`);
  }

  const undocumentedFunctions = findDocumentableFunctions(source)
    .filter(fn => !hasAdjacentJSDoc(source, fn.index))
    .map(fn => fn.name);

  if (undocumentedFunctions.length > 0) {
    violations.push(`FUNCTION_JSDOC_REQUIRED: ${undocumentedFunctions.slice(0, 10).join('|')}`);
    if (undocumentedFunctions.length > 10) {
      violations.push(`FUNCTION_JSDOC_ADDITIONAL_COUNT: ${undocumentedFunctions.length - 10}`);
    }
  }

  return { filePath, violations };
};

/**
 * @function runDocumentationGuard
 * @description Runs the documentation audit and exits non-zero when violations are found.
 * @param {Array<string>} args - Command-line scan roots.
 * @returns {number} Exit code.
 * @collaboration This is the executable enforcement point for Wilson's generational documentation mandate.
 */
const runDocumentationGuard = (args = []) => {
  const roots = resolveScanRoots(args);
  const files = [...new Set(roots.flatMap(collectSourceFiles))].sort();
  const results = files
    .map(auditFile)
    .filter(result => result.violations.length > 0);

  if (results.length === 0) {
    console.log(`[WILSY-DOC-GUARD] PASS ${files.length} source files inspected.`);
    return 0;
  }

  console.error(`[WILSY-DOC-GUARD] FAIL ${results.length}/${files.length} files need documentation hardening.`);
  results.slice(0, 120).forEach(result => {
    console.error(`- ${path.relative(process.cwd(), result.filePath)} :: ${result.violations.join(', ')}`);
  });
  if (results.length > 120) {
    console.error(`... ${results.length - 120} additional files omitted. Run with targeted roots to repair by module.`);
  }
  return 1;
};

process.exitCode = runDocumentationGuard(process.argv.slice(2));
