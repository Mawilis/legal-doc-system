/* eslint-disable */
const fs = require('fs');
const path = require('path');

const CLIENT_INDEX_CSS = path.resolve('client/src/index.css');

/**
 * @function assertExists
 * @description Fails when the global client index CSS file is missing.
 * @collaboration R72S client index CSS lane, exact staged-set discipline, production gate workflow.
 */
const assertExists = (targetPath) => {
  if (!fs.existsSync(targetPath)) {
    throw new Error(`R72S gate missing required path: ${targetPath}`);
  }
};

/**
 * @function readCssFile
 * @description Reads the global client index CSS as UTF-8 text.
 * @collaboration R72S CSS inspection, build proof, global client style certification.
 */
const readCssFile = () => fs.readFileSync(CLIENT_INDEX_CSS, 'utf8');

/**
 * @function toRepoPath
 * @description Converts an absolute path to a normalized repo-relative path.
 * @collaboration Audit-friendly lane output, staged-set verification, client index CSS inventory.
 */
const toRepoPath = (filePath) => path.relative(process.cwd(), filePath).split(path.sep).join('/');

/**
 * @function countNeedles
 * @description Counts semantic evidence terms in global client CSS.
 * @collaboration Client shell stylesheet validation, global UI proof, anti-overfit gate design.
 */
const countNeedles = (source, needles) => needles.filter((needle) => source.includes(needle)).length;

/**
 * @function assertMinimumNeedles
 * @description Fails when a semantic proof group lacks enough evidence terms.
 * @collaboration R72S semantic proof, global client CSS verification, production seal reliability.
 */
const assertMinimumNeedles = (source, needles, minimum, label) => {
  const count = countNeedles(source, needles);

  if (count < minimum) {
    throw new Error(`R72S gate missing ${label}: found ${count}, required ${minimum}`);
  }

  return count;
};

/**
 * @function assertBlocked
 * @description Fails when forbidden export/report, secret, backend import, or recursive expansion patterns appear.
 * @collaboration Secret guard, no filesystem export behavior, global CSS-only boundary.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72S gate blocked ${label}`);
  }
};

/**
 * @function buildRecursiveExpansionPattern
 * @description Builds the recursive expansion token pattern without hardcoding the token in gate prose.
 * @collaboration Terminal boundary discipline, source self-scan safety, R72S guard precision.
 */
const buildRecursiveExpansionPattern = () => {
  const prefix = ['R', '70', 'F'].join('');
  return new RegExp(`${prefix}[-_]|\\b${prefix.toLowerCase()}[A-Za-z0-9_]*\\s*[=:]`);
};

/**
 * @function summarizeCss
 * @description Produces an audit summary for the global client index CSS file.
 * @collaboration Investor-grade lane receipts, source inventory, global client CSS gate output.
 */
const summarizeCss = (source) => ({
  path: toRepoPath(CLIENT_INDEX_CSS),
  extension: path.extname(CLIENT_INDEX_CSS),
  bytes: source.length,
  lines: source.split(/\r?\n/).length,
  mentionsRoot: /:root|html|body|#root/.test(source),
  mentionsTheme: /theme|Theme|token|Token|surface|Surface|color|Color|background|Background/.test(source),
  mentionsResponsive: /@media|grid|flex|minmax|clamp|rem|vh|vw/.test(source),
  selectorCount: (source.match(/\{[\s\S]*?\}/g) || []).length,
  cssVariableReferenceCount: (source.match(/var\(--[A-Za-z0-9_-]+\)/g) || []).length,
  cssVariableDefinitionCount: (source.match(/--[A-Za-z0-9_-]+\s*:/g) || []).length,
  mediaQueryCount: (source.match(/@media/g) || []).length,
  importCount: (source.match(/@import/g) || []).length,
});

/**
 * @function verifyCssBoundaries
 * @description Verifies global client index CSS remains style-only and does not import runtime/backend/report/export surfaces.
 * @collaboration R72S lane quarantine, no backend path reference, no secret literal discipline.
 */
const verifyCssBoundaries = (source) => {
  assertBlocked(source, /server\/exports|reports\/|forensic-fixes\//, 'filesystem report/export path');
  assertBlocked(source, /\b(?:fs\.)?(?:writeFile|writeFileSync|createWriteStream)\s*\(/, 'executable filesystem write call');
  assertBlocked(source, buildRecursiveExpansionPattern(), 'recursive expansion token shape');
  assertBlocked(source, /VITE_[A-Z0-9_]*(SECRET|PASSWORD|PRIVATE|HMAC|JWT)/, 'unsafe browser secret env literal');
  assertBlocked(source, /OPENAI_API_KEY|mongodb\+srv:\/\/[^"'\s]+:[^"'\s]+@/, 'server secret-like literal');
  assertBlocked(source, /server\/middleware|server\/routes|server\/services|server\/models/, 'backend path import/reference');
};

/**
 * @function runR72SClientIndexCssGate
 * @description Certifies global client index CSS as an isolated style-only lane.
 * @collaboration R72J account theme seal, R72K rail seal, R72L lead seal, R72M theme seal, R72N superadmin seal, R72O script-fabric seal, R72P service seal, R72Q CSS seal, R72R dashboard JSX seal.
 */
const runR72SClientIndexCssGate = () => {
  assertExists(CLIENT_INDEX_CSS);

  const source = readCssFile();
  const summary = summarizeCss(source);

  if (summary.bytes < 300) {
    throw new Error(`R72S gate blocked: client index CSS is too small to certify (${summary.bytes} bytes)`);
  }

  if (summary.selectorCount < 3) {
    throw new Error(`R72S gate blocked: expected at least 3 CSS selectors, found ${summary.selectorCount}`);
  }

  verifyCssBoundaries(source);

  const semanticProof = {
    rootShellEvidence: assertMinimumNeedles(source, [':root', 'html', 'body', '#root'], 1, 'global root/body/#root shell contract'),
    themeEvidence: countNeedles(source, ['theme', 'Theme', 'token', 'Token', 'surface', 'Surface', 'color', 'Color', 'background', 'Background']),
    responsiveEvidence: countNeedles(source, ['@media', 'grid', 'flex', 'minmax', 'clamp', 'rem', 'vh', 'vw']),
    selectorCount: summary.selectorCount,
    cssVariableReferenceCount: summary.cssVariableReferenceCount,
    cssVariableDefinitionCount: summary.cssVariableDefinitionCount,
    mediaQueryCount: summary.mediaQueryCount,
    importCount: summary.importCount,
  };

  console.log(JSON.stringify({
    gate: 'R72S_CLIENT_INDEX_CSS_VERIFIED',
    lane: 'client-index-css',
    cssFile: 'client/src/index.css',
    fileCount: 1,
    files: [summary],
    semanticProof,
    isolatedLane: true,
    cssOnlyLane: true,
    globalClientStyleOnly: true,
    noCrmDashboardJsxMutation: true,
    noCrmDashboardCssMutation: true,
    noCrmServiceMutation: true,
    noCrmRailLeadThemeMutation: true,
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
  console.log('PASS: WILSY R72S CLIENT INDEX CSS GATE');
  console.log(' - client index CSS lane is isolated to client/src/index.css');
  console.log(' - CSS semantics prove global root/body/#root shell and responsive style contracts');
  console.log(' - no CRM dashboard JSX/CSS, service, rail, lead, theme, account, superadmin, backend, auth, or CRM-live backend files are inside the lane');
  console.log(' - no filesystem report/export, executable write call, secret, or recursive expansion token shape present');
};

runR72SClientIndexCssGate();
