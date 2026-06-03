/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SECRET GUARD [V1.0.0-PRODUCTION-SECURITY]                                                                                 ║
 * ║ [SOURCE SECRET SCAN | CLIENT ENV SECRET WARNING | HARDCODED URI DETECTION | SAFE REPORTING]                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-SECURITY | PRODUCTION READY | CONFIGURATION DISCIPLINE AUDIT TOOL                                         ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/scripts/wilsy-secret-guard.js                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated no sensitive data inside code files and env-owned production configuration.              ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Added a secret/config guard that reports keys and files without printing secret values.      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const DEFAULT_SCAN_ROOTS = ['client/src', 'server', 'scripts'];
const SOURCE_EXTENSIONS = new Set(['.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx', '.sh']);
const SKIP_SEGMENTS = new Set(['node_modules', 'dist', 'build', 'coverage', '.git', '.next', '.cache', 'tests', '__tests__']);
const CLIENT_SECRET_KEY_PATTERN = /^VITE_.*(SECRET|TOKEN|PASSWORD|PRIVATE|HMAC|JWT)/i;
const SOURCE_SECRET_PATTERNS = [
  { label: 'MONGODB_URI_WITH_CREDENTIALS', pattern: /mongodb(?:\+srv)?:\/\/[^/\s"'`:@]+:[^@\s"'`]+@/i },
  { label: 'HARDCODED_PASSWORD_ASSIGNMENT', pattern: /\b(password|new_password|admin_password)\b\s*[:=]\s*["'`][^"'`\n]{8,}["'`]/i },
  { label: 'HARDCODED_SECRET_FALLBACK', pattern: /\b(jwt_secret|hmac_secret|seal_secret|api_secret|secretkey|secret_key)\b[^=\n]*=\s*[^;\n]*\|\|\s*["'`][^"'`\n]{8,}["'`]/i },
  { label: 'TWILIO_ACCOUNT_SID_LITERAL', pattern: /\bAC[0-9a-fA-F]{32}\b/ },
  { label: 'OPENAI_STYLE_KEY', pattern: /\bsk-[A-Za-z0-9_-]{20,}\b/ },
  { label: 'BEARER_TOKEN_LITERAL', pattern: /Bearer\s+[A-Za-z0-9._-]{24,}/i }
];

const BENIGN_LITERAL_PATTERN = /\[(?:REDACTED|REDACTED_FOR_COMPLIANCE|MASKED)[^\]]*\]|test|fixture|example|placeholder|dummy|mock/i;
const GENERATED_SECRET_LINE_PATTERN = /\$\{?[A-Z0-9_]+\}?|openssl rand|base64|crypto\.random/i;

/**
 * @function shouldSkipPath
 * @description Determines whether a filesystem path belongs to generated or dependency output.
 * @param {string} candidatePath - Candidate path.
 * @returns {boolean} True when the path should be skipped.
 * @collaboration Keeps the secret guard focused on Wilsy OS source rather than third-party bundles.
 */
const shouldSkipPath = (candidatePath = '') => (
  candidatePath.split(path.sep).some(segment => SKIP_SEGMENTS.has(segment))
);

/**
 * @function isGitIgnored
 * @description Checks whether Git already classifies a path as ignored.
 * @param {string} candidatePath - Candidate path.
 * @returns {boolean} True when Git ignore rules exclude the path.
 * @collaboration Keeps local env files, generated logs and recovery artifacts out of source secret gates.
 */
const isGitIgnored = (candidatePath = '') => {
  const relativePath = path.relative(process.cwd(), candidatePath);
  if (!relativePath || relativePath.startsWith('..')) return false;
  const result = spawnSync('git', ['check-ignore', '--quiet', relativePath], {
    cwd: process.cwd(),
    stdio: 'ignore'
  });
  return result.status === 0;
};

/**
 * @function isBenignSecretSignal
 * @description Determines whether a detected secret-shaped line is a redaction marker, generated credential or test fixture.
 * @param {string} label - Detection label.
 * @param {string} line - Source line containing the detection.
 * @returns {boolean} True when the line is safe to ignore.
 * @collaboration Reduces audit noise without allowing deployable credential literals into source control.
 */
const isBenignSecretSignal = (label = '', line = '') => {
  if (BENIGN_LITERAL_PATTERN.test(line)) return true;
  if (label === 'MONGODB_URI_WITH_CREDENTIALS' && GENERATED_SECRET_LINE_PATTERN.test(line)) return true;
  if (label === 'HARDCODED_PASSWORD_ASSIGNMENT' && /\b(PASSWORD|PIN|TOKEN|SECRET)\b\s*:/.test(line)) return true;
  if (label === 'HARDCODED_PASSWORD_ASSIGNMENT' && /\bpassword\b\s*:\s*['"][A-Z0-9_]+['"]/.test(line)) return true;
  return false;
};

/**
 * @function collectSourceFiles
 * @description Recursively collects source files for secret scanning.
 * @param {string} root - Scan root.
 * @returns {Array<string>} Source file paths.
 * @collaboration Gives security audits a deterministic source inventory without shelling out to grep.
 */
const collectSourceFiles = (root) => {
  if (!fs.existsSync(root) || shouldSkipPath(root) || isGitIgnored(root)) return [];
  const stat = fs.statSync(root);
  if (stat.isFile()) {
    return SOURCE_EXTENSIONS.has(path.extname(root)) ? [root] : [];
  }
  return fs.readdirSync(root).flatMap(entry => collectSourceFiles(path.join(root, entry)));
};

/**
 * @function readEnvKeys
 * @description Reads environment key names without exposing secret values.
 * @param {string} envPath - Environment file path.
 * @returns {Array<string>} Environment keys.
 * @collaboration Lets the guard detect browser-exposed secret key names while keeping values private.
 */
const readEnvKeys = (envPath) => {
  if (!fs.existsSync(envPath)) return [];
  return fs.readFileSync(envPath, 'utf8')
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(line => line && !line.startsWith('#') && line.includes('='))
    .map(line => line.split('=')[0]);
};

/**
 * @function auditClientEnvKeys
 * @description Detects Vite environment keys that would expose secrets to the browser.
 * @returns {Array<Object>} Client env violations.
 * @collaboration VITE keys are public at build time; secret-shaped names belong on the server side.
 */
const auditClientEnvKeys = () => readEnvKeys(path.resolve(process.cwd(), 'client/.env'))
  .filter(() => !isGitIgnored(path.resolve(process.cwd(), 'client/.env')))
  .filter(key => CLIENT_SECRET_KEY_PATTERN.test(key))
  .map(key => ({ filePath: 'client/.env', label: 'BROWSER_EXPOSED_SECRET_ENV_KEY', detail: key }));

/**
 * @function auditSourceFile
 * @description Checks one source file for high-confidence embedded secret patterns.
 * @param {string} filePath - Source file path.
 * @returns {Array<Object>} Source secret violations.
 * @collaboration Reports only pattern labels and line numbers so secrets are not echoed in audit output.
 */
const auditSourceFile = (filePath) => {
  const source = fs.readFileSync(filePath, 'utf8');
  return source.split(/\r?\n/).flatMap((lineText, index) => (
    SOURCE_SECRET_PATTERNS.flatMap(({ label, pattern }) => {
      if (!pattern.test(lineText)) return [];
      if (isBenignSecretSignal(label, lineText)) return [];
      return [{ filePath, label, detail: `line ${index + 1}` }];
    })
  ));
};

/**
 * @function runSecretGuard
 * @description Runs the Wilsy OS secret/config audit.
 * @param {Array<string>} args - Optional scan roots.
 * @returns {number} Exit code.
 * @collaboration Establishes a repeatable production gate for env-owned secrets and client-safe configuration.
 */
const runSecretGuard = (args = []) => {
  const roots = (args.length ? args : DEFAULT_SCAN_ROOTS)
    .map(root => path.resolve(process.cwd(), root))
    .filter(root => fs.existsSync(root));
  const files = [...new Set(roots.flatMap(collectSourceFiles))].sort();
  const violations = [
    ...auditClientEnvKeys(),
    ...files.flatMap(auditSourceFile)
  ];

  if (violations.length === 0) {
    console.log(`[WILSY-SECRET-GUARD] PASS ${files.length} source files inspected.`);
    return 0;
  }

  console.error(`[WILSY-SECRET-GUARD] FAIL ${violations.length} secret/config violations detected.`);
  violations.slice(0, 120).forEach(violation => {
    const fileLabel = path.isAbsolute(violation.filePath)
      ? path.relative(process.cwd(), violation.filePath)
      : violation.filePath;
    console.error(`- ${fileLabel} :: ${violation.label} :: ${violation.detail}`);
  });
  if (violations.length > 120) {
    console.error(`... ${violations.length - 120} additional violations omitted. Run with targeted roots to repair by module.`);
  }
  return 1;
};

process.exitCode = runSecretGuard(process.argv.slice(2));
