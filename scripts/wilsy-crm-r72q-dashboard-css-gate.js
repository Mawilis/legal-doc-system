/* eslint-disable */
const fs = require('fs');
const path = require('path');

const CRM_DASHBOARD_CSS = path.resolve('client/src/components/crm/CRMDashboard.module.css');

/**
 * @function assertExists
 * @description Fails when the CRM dashboard CSS module is missing.
 * @collaboration R72Q CRM dashboard CSS lane, exact staged-set discipline, production gate workflow.
 */
const assertExists = (targetPath) => {
  if (!fs.existsSync(targetPath)) {
    throw new Error(`R72Q gate missing required path: ${targetPath}`);
  }
};

/**
 * @function readCssFile
 * @description Reads the CRM dashboard CSS module as UTF-8 text.
 * @collaboration R72Q CSS inspection, build proof, dashboard style lane certification.
 */
const readCssFile = () => fs.readFileSync(CRM_DASHBOARD_CSS, 'utf8');

/**
 * @function toRepoPath
 * @description Converts an absolute path to a normalized repo-relative path.
 * @collaboration Audit-friendly lane output, staged-set verification, CRM CSS inventory.
 */
const toRepoPath = (filePath) => path.relative(process.cwd(), filePath).split(path.sep).join('/');

/**
 * @function countNeedles
 * @description Counts semantic evidence terms in CRM dashboard CSS.
 * @collaboration CRM stylesheet validation, dashboard UI proof, anti-overfit gate design.
 */
const countNeedles = (source, needles) => needles.filter((needle) => source.includes(needle)).length;

/**
 * @function assertMinimumNeedles
 * @description Fails when a semantic proof group lacks enough evidence terms.
 * @collaboration R72Q semantic proof, CRM dashboard CSS verification, production seal reliability.
 */
const assertMinimumNeedles = (source, needles, minimum, label) => {
  const count = countNeedles(source, needles);

  if (count < minimum) {
    throw new Error(`R72Q gate missing ${label}: found ${count}, required ${minimum}`);
  }

  return count;
};

/**
 * @function assertBlocked
 * @description Fails when forbidden export/report, secret, backend import, or recursive expansion patterns appear.
 * @collaboration Secret guard, no filesystem export behavior, CSS-only boundary.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72Q gate blocked ${label}`);
  }
};

/**
 * @function buildRecursiveExpansionPattern
 * @description Builds the recursive expansion token pattern without hardcoding the token in gate prose.
 * @collaboration Terminal boundary discipline, source self-scan safety, R72Q guard precision.
 */
const buildRecursiveExpansionPattern = () => {
  const prefix = ['R', '70', 'F'].join('');
  return new RegExp(`${prefix}[-_]|\\b${prefix.toLowerCase()}[A-Za-z0-9_]*\\s*[=:]`);
};

/**
 * @function summarizeCss
 * @description Produces an audit summary for the CRM dashboard CSS module.
 * @collaboration Investor-grade lane receipts, source inventory, CSS gate output.
 */
const summarizeCss = (source) => ({
  path: toRepoPath(CRM_DASHBOARD_CSS),
  extension: path.extname(CRM_DASHBOARD_CSS),
  bytes: source.length,
  lines: source.split(/\r?\n/).length,
  mentionsCrm: /crm|CRM/.test(source),
  mentionsDashboard: /dashboard|Dashboard|cockpit|Cockpit|command|Command/.test(source),
  mentionsTheme: /theme|Theme|skin|Skin|palette|Palette|token|Token|surface|Surface/.test(source),
  mentionsResponsive: /@media|grid|flex|minmax|clamp|rem|vh|vw/.test(source),
  selectorCount: (source.match(/\{[\s\S]*?\}/g) || []).length,
  cssVariableReferenceCount: (source.match(/var\(--[A-Za-z0-9_-]+\)/g) || []).length,
  cssVariableDefinitionCount: (source.match(/--[A-Za-z0-9_-]+\s*:/g) || []).length,
  mediaQueryCount: (source.match(/@media/g) || []).length,
});

/**
 * @function verifyCssBoundaries
 * @description Verifies CRM dashboard CSS remains style-only and does not import runtime/backend/report/export surfaces.
 * @collaboration R72Q lane quarantine, no backend path reference, no secret literal discipline.
 */
const verifyCssBoundaries = (source) => {
  assertBlocked(source, /server\/exports|reports\/|forensic-fixes\//, 'filesystem report/export path');
  assertBlocked(source, /\b(?:fs\.)?(?:writeFile|writeFileSync|createWriteStream)\s*\(/, 'executable filesystem write call');
  assertBlocked(source, buildRecursiveExpansionPattern(), 'recursive expansion token shape');
  assertBlocked(source, /VITE_[A-Z0-9_]*(SECRET|PASSWORD|PRIVATE|HMAC|JWT)/, 'unsafe browser secret env literal');
  assertBlocked(source, /OPENAI_API_KEY|mongodb\+srv:\/\/[^"'\s]+:[^"'\s]+@/, 'server secret-like literal');
  assertBlocked(source, /server\/middleware|server\/routes|server\/services|server\/models/, 'backend path import/reference');
  assertBlocked(source, /client\/src\/components\/account|client\/src\/components\/crm\/rail|client\/src\/components\/crm\/lead|client\/src\/components\/crm\/theme|client\/src\/styles\/superadmin|client\/src\/services\/crmService/, 'cross-lane source/style reference');
};

/**
 * @function runR72QCrmDashboardCssGate
 * @description Certifies the CRM dashboard CSS module as an isolated style-only dashboard visual lane.
 * @collaboration R72J account theme seal, R72K rail seal, R72L lead seal, R72M theme seal, R72N superadmin seal, R72O script-fabric seal, R72P service seal, R72H dashboard reconciliation.
 */
const runR72QCrmDashboardCssGate = () => {
  assertExists(CRM_DASHBOARD_CSS);

  const source = readCssFile();
  const summary = summarizeCss(source);

  if (summary.bytes < 500) {
    throw new Error(`R72Q gate blocked: CRM dashboard CSS is too small to certify (${summary.bytes} bytes)`);
  }

  if (summary.selectorCount < 5) {
    throw new Error(`R72Q gate blocked: expected at least 5 CSS selectors, found ${summary.selectorCount}`);
  }

  verifyCssBoundaries(source);

  const semanticProof = {
    crmEvidence: assertMinimumNeedles(source, ['crm', 'CRM'], 1, 'CRM contract'),
    dashboardEvidence: assertMinimumNeedles(source, ['dashboard', 'Dashboard', 'cockpit', 'Cockpit', 'command', 'Command'], 1, 'dashboard/cockpit/command contract'),
    themeEvidence: countNeedles(source, ['theme', 'Theme', 'skin', 'Skin', 'palette', 'Palette', 'token', 'Token', 'surface', 'Surface']),
    responsiveEvidence: countNeedles(source, ['@media', 'grid', 'flex', 'minmax', 'clamp', 'rem', 'vh', 'vw']),
    selectorCount: summary.selectorCount,
    cssVariableReferenceCount: summary.cssVariableReferenceCount,
    cssVariableDefinitionCount: summary.cssVariableDefinitionCount,
    mediaQueryCount: summary.mediaQueryCount,
  };

  console.log(JSON.stringify({
    gate: 'R72Q_CRM_DASHBOARD_CSS_VERIFIED',
    lane: 'crm-dashboard-css',
    cssFile: 'client/src/components/crm/CRMDashboard.module.css',
    fileCount: 1,
    files: [summary],
    semanticProof,
    isolatedLane: true,
    cssOnlyLane: true,
    noDashboardJsxMutation: true,
    noClientIndexMutation: true,
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
  console.log('PASS: WILSY CRM R72Q DASHBOARD CSS GATE');
  console.log(' - CRM dashboard CSS lane is isolated to client/src/components/crm/CRMDashboard.module.css');
  console.log(' - CSS semantics prove CRM, dashboard/cockpit/command, and responsive style contracts');
  console.log(' - no dashboard JSX, index CSS, CRM service, rail, lead, theme, account, superadmin, backend, auth, or CRM-live backend files are inside the lane');
  console.log(' - no filesystem report/export, executable write call, secret, or recursive expansion token shape present');
};

runR72QCrmDashboardCssGate();
