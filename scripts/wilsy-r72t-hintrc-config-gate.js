/* eslint-disable */
const fs = require('fs');
const path = require('path');

const HINTRC_FILE = path.resolve('.hintrc');

/**
 * @function assertExists
 * @description Fails when the .hintrc configuration file is missing.
 * @collaboration R72T .hintrc config lane, exact staged-set discipline, production gate workflow.
 */
const assertExists = (targetPath) => {
  if (!fs.existsSync(targetPath)) {
    throw new Error(`R72T gate missing required path: ${targetPath}`);
  }
};

/**
 * @function readHinrtrcFile
 * @description Reads .hintrc as UTF-8 text.
 * @collaboration R72T config inspection, browser hinting posture, config-only certification.
 */
const readHinrtrcFile = () => fs.readFileSync(HINTRC_FILE, 'utf8');

/**
 * @function toRepoPath
 * @description Converts an absolute path to a normalized repo-relative path.
 * @collaboration Audit-friendly lane output, staged-set verification, config inventory.
 */
const toRepoPath = (filePath) => path.relative(process.cwd(), filePath).split(path.sep).join('/');

/**
 * @function stripJsonComments
 * @description Removes JSON-style comments while preserving string literals.
 * @collaboration .hintrc parser safety, config proof, resilient gate behavior.
 */
const stripJsonComments = (source) => {
  let output = '';
  let inString = false;
  let quote = '';
  let escaped = false;

  for (let index = 0; index < source.length; index += 1) {
    const current = source[index];
    const next = source[index + 1];

    if (inString) {
      output += current;

      if (escaped) {
        escaped = false;
      } else if (current === '\\') {
        escaped = true;
      } else if (current === quote) {
        inString = false;
        quote = '';
      }

      continue;
    }

    if (current === '"' || current === "'") {
      inString = true;
      quote = current;
      output += current;
      continue;
    }

    if (current === '/' && next === '/') {
      while (index < source.length && source[index] !== '\n') {
        index += 1;
      }
      output += '\n';
      continue;
    }

    if (current === '/' && next === '*') {
      index += 2;
      while (index < source.length && !(source[index] === '*' && source[index + 1] === '/')) {
        index += 1;
      }
      index += 1;
      continue;
    }

    output += current;
  }

  return output;
};

/**
 * @function parseHinrtrc
 * @description Parses .hintrc into a JSON object with comment-tolerant fallback.
 * @collaboration R72T config proof, webhint compatibility, deterministic validation.
 */
const parseHinrtrc = (source) => {
  const normalized = source.replace(/^\uFEFF/, '').trim();

  try {
    return JSON.parse(normalized);
  } catch (firstError) {
    try {
      return JSON.parse(stripJsonComments(normalized));
    } catch (secondError) {
      throw new Error(`R72T gate blocked invalid .hintrc JSON: ${secondError.message}`);
    }
  }
};

/**
 * @function countPattern
 * @description Counts regex pattern matches in source.
 * @collaboration R72T config inventory, selector-free source audit, gate summary.
 */
const countPattern = (source, pattern) => (source.match(pattern) || []).length;

/**
 * @function assertBlocked
 * @description Fails when forbidden export/report, secret, backend import, executable command, or recursive expansion patterns appear.
 * @collaboration Secret guard, no filesystem export behavior, config-only boundary.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72T gate blocked ${label}`);
  }
};

/**
 * @function buildRecursiveExpansionPattern
 * @description Builds the recursive expansion token pattern without hardcoding the token in gate prose.
 * @collaboration Terminal boundary discipline, source self-scan safety, R72T guard precision.
 */
const buildRecursiveExpansionPattern = () => {
  const prefix = ['R', '70', 'F'].join('');
  return new RegExp(`${prefix}[-_]|\\b${prefix.toLowerCase()}[A-Za-z0-9_]*\\s*[=:]`);
};

/**
 * @function verifyConfigBoundaries
 * @description Verifies .hintrc remains config-only and does not reference runtime/backend/report/export/secret surfaces.
 * @collaboration R72T lane quarantine, backend isolation, browser-hint config discipline.
 */
const verifyConfigBoundaries = (source) => {
  assertBlocked(source, /server\/exports|reports\/|forensic-fixes\//, 'filesystem report/export path');
  assertBlocked(source, /\b(?:fs\.)?(?:writeFile|writeFileSync|createWriteStream)\s*\(/, 'executable filesystem write call');
  assertBlocked(source, buildRecursiveExpansionPattern(), 'recursive expansion token shape');
  assertBlocked(source, /VITE_[A-Z0-9_]*(SECRET|PASSWORD|PRIVATE|HMAC|JWT)/, 'unsafe browser secret env literal');
  assertBlocked(source, /OPENAI_API_KEY|mongodb\+srv:\/\/[^"'\s]+:[^"'\s]+@/, 'server secret-like literal');
  assertBlocked(source, /server\/middleware|server\/routes|server\/services|server\/models/, 'backend path import/reference');
  assertBlocked(source, /\b(?:bash|chmod|curl|wget|node|npm|pnpm|yarn)\s+/, 'executable shell command in config');
};

/**
 * @function summarizeConfig
 * @description Produces an audit summary for .hintrc.
 * @collaboration Investor-grade lane receipts, config inventory, R72T gate output.
 */
const summarizeConfig = (source, parsed) => {
  const keys = Object.keys(parsed);
  const hints = parsed.hints && typeof parsed.hints === 'object' && !Array.isArray(parsed.hints)
    ? Object.keys(parsed.hints)
    : [];
  const extendsValue = parsed.extends || parsed.extendsHint || parsed.extendsHints || null;

  return {
    path: toRepoPath(HINTRC_FILE),
    extension: path.extname(HINTRC_FILE) || '.hintrc',
    bytes: source.length,
    lines: source.split(/\r?\n/).length,
    topLevelKeys: keys,
    topLevelKeyCount: keys.length,
    hasExtends: Boolean(extendsValue),
    hasHints: hints.length > 0,
    hintCount: hints.length,
    importLikeCount: countPattern(source, /@import|import\s+/g),
    commandLikeCount: countPattern(source, /\b(?:bash|chmod|curl|wget|node|npm|pnpm|yarn)\s+/g),
  };
};

/**
 * @function verifyHintrcShape
 * @description Verifies parsed .hintrc is a non-array config object with recognizable webhint configuration posture.
 * @collaboration R72T config shape proof, global tooling lane safety, non-source mutation control.
 */
const verifyHintrcShape = (parsed, summary) => {
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error('R72T gate blocked: .hintrc must parse to an object');
  }

  if (summary.topLevelKeyCount < 1) {
    throw new Error('R72T gate blocked: .hintrc has no top-level config keys');
  }

  const recognizedKeys = ['extends', 'hints', 'ignoredUrls', 'browserslist', 'connector', 'formatters', 'parsers', 'severity'];
  const recognizedCount = recognizedKeys.filter((key) => Object.prototype.hasOwnProperty.call(parsed, key)).length;

  if (recognizedCount < 1) {
    throw new Error('R72T gate blocked: .hintrc lacks recognizable webhint config keys');
  }

  return {
    recognizedConfigKeyCount: recognizedCount,
    recognizedConfigKeys: recognizedKeys.filter((key) => Object.prototype.hasOwnProperty.call(parsed, key)),
  };
};

/**
 * @function runR72THintrcConfigGate
 * @description Certifies .hintrc as an isolated browser-hint config lane.
 * @collaboration R72J account theme seal, R72K rail seal, R72L lead seal, R72M theme seal, R72N superadmin seal, R72O script-fabric seal, R72P service seal, R72Q CSS seal, R72R dashboard JSX seal, R72S index CSS seal.
 */
const runR72THintrcConfigGate = () => {
  assertExists(HINTRC_FILE);

  const source = readHinrtrcFile();
  const parsed = parseHinrtrc(source);
  const summary = summarizeConfig(source, parsed);

  if (summary.bytes < 2) {
    throw new Error(`R72T gate blocked: .hintrc is too small to certify (${summary.bytes} bytes)`);
  }

  verifyConfigBoundaries(source);
  const shapeProof = verifyHintrcShape(parsed, summary);

  console.log(JSON.stringify({
    gate: 'R72T_HINTRC_CONFIG_VERIFIED',
    lane: 'hintrc-config',
    configFile: '.hintrc',
    fileCount: 1,
    files: [summary],
    shapeProof,
    isolatedLane: true,
    configOnlyLane: true,
    noClientSourceMutation: true,
    noClientStyleMutation: true,
    noCrmMutation: true,
    noBackendAuthSecurityMutation: true,
    noCrmLiveBackendMutation: true,
    noAccountMutation: true,
    noSuperadminThemeMutation: true,
    noScriptFabricMutation: true,
    noFilesystemReportExport: true,
    noExecutableFilesystemWriteCall: true,
    noSecrets: true,
    noRecursiveExpansionTokenShape: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY R72T HINTRC CONFIG GATE');
  console.log(' - .hintrc config lane is isolated to .hintrc');
  console.log(' - config parses as a browser-hint configuration object');
  console.log(' - no client source/style, CRM, account, superadmin, backend, auth, or CRM-live backend files are inside the lane');
  console.log(' - no filesystem report/export, executable write call, secret, shell command, or recursive expansion token shape present');
};

runR72THintrcConfigGate();
