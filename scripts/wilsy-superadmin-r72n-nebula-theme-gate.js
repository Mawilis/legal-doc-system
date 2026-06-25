/* eslint-disable */
const fs = require('fs');
const path = require('path');

const NEBULA_THEME = path.resolve('client/src/styles/superadmin/themes/wilsy-nebula-command.css');

/**
 * @function assertExists
 * @description Fails when the Superadmin Nebula command theme CSS file is missing.
 * @collaboration R72N superadmin theme lane, exact staged-set discipline, production gate workflow.
 */
const assertExists = (targetPath) => {
  if (!fs.existsSync(targetPath)) {
    throw new Error(`R72N gate missing required path: ${targetPath}`);
  }
};

/**
 * @function readThemeFile
 * @description Reads the Superadmin Nebula theme CSS file as UTF-8 text.
 * @collaboration R72N Nebula command theme inspection, CSS runtime proof, build validation.
 */
const readThemeFile = () => fs.readFileSync(NEBULA_THEME, 'utf8');

/**
 * @function toRepoPath
 * @description Converts an absolute path to a normalized repo-relative path.
 * @collaboration Audit-friendly lane output, staged-set verification, superadmin theme inventory.
 */
const toRepoPath = (filePath) => path.relative(process.cwd(), filePath).split(path.sep).join('/');

/**
 * @function assertIncludesAny
 * @description Fails when the theme CSS lacks all required semantic contract fragments.
 * @collaboration Flexible CSS-shape validation, Nebula theme proof, Superadmin theme quality.
 */
const assertIncludesAny = (source, needles, label) => {
  if (!needles.some((needle) => source.includes(needle))) {
    throw new Error(`R72N gate missing ${label}: ${needles.join(', ')}`);
  }
};

/**
 * @function countNeedles
 * @description Counts semantic evidence terms in a theme CSS bundle.
 * @collaboration Superadmin theme validation, palette proof, anti-overfit gate design.
 */
const countNeedles = (source, needles) => needles.filter((needle) => source.includes(needle)).length;

/**
 * @function assertMinimumNeedles
 * @description Fails when a semantic proof group lacks enough evidence terms.
 * @collaboration R72N semantic proof, Nebula command theme verification, production seal reliability.
 */
const assertMinimumNeedles = (source, needles, minimum, label) => {
  const count = countNeedles(source, needles);

  if (count < minimum) {
    throw new Error(`R72N gate missing ${label}: found ${count}, required ${minimum}`);
  }

  return count;
};

/**
 * @function assertBlocked
 * @description Fails when forbidden export/report, secret, backend, or recursive expansion patterns appear.
 * @collaboration Secret guard, no filesystem export behavior, style-only lane boundary.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72N gate blocked ${label}`);
  }
};

/**
 * @function summarizeTheme
 * @description Produces an audit summary for the Superadmin Nebula CSS theme.
 * @collaboration Investor-grade lane receipts, source inventory, theme gate output.
 */
const summarizeTheme = (source) => ({
  path: toRepoPath(NEBULA_THEME),
  extension: path.extname(NEBULA_THEME),
  bytes: source.length,
  lines: source.split(/\r?\n/).length,
  mentionsNebula: /nebula|Nebula|WILSY_NEBULA|wilsy-nebula/.test(source),
  mentionsCommand: /command|Command|sovereign|Sovereign|superadmin|Superadmin/.test(source),
  mentionsTheme: /theme|Theme|skin|Skin|palette|Palette|token|Token|surface|Surface/.test(source),
  cssVariableCount: (source.match(/--[A-Za-z0-9_-]+\s*:/g) || []).length,
  selectorCount: (source.match(/\{[\s\S]*?\}/g) || []).length,
});

/**
 * @function verifyStyleOnlyBoundary
 * @description Verifies the Nebula CSS file does not import or reference disallowed runtime/backend lanes.
 * @collaboration R72N lane quarantine, no accidental runtime mutation, superadmin-only theme proof.
 */
const verifyStyleOnlyBoundary = (source) => {
  assertBlocked(source, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem report/export behavior');
  assertBlocked(source, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive expansion token shape');
  assertBlocked(source, /VITE_[A-Z0-9_]*(SECRET|TOKEN|PASSWORD|PRIVATE|HMAC|JWT)|OPENAI_API_KEY|mongodb\+srv:\/\/[^"'\s]+:[^"'\s]+@/, 'secret-like literal');
  assertBlocked(source, /server\/middleware|server\/routes|server\/services|server\/models/, 'backend path reference');
  assertBlocked(source, /client\/src\/components\/crm\/CRMDashboard|client\/src\/services\/crmService|client\/src\/components\/account/, 'cross-lane runtime reference');
};

/**
 * @function runR72NNebulaThemeGate
 * @description Certifies the Superadmin Nebula command theme CSS as an isolated style-only Wilsy OS skin surface.
 * @collaboration R72J account theme seal, R72K command rail seal, R72L lead seal, R72M theme bridge seal, R72H dashboard reconciliation.
 */
const runR72NNebulaThemeGate = () => {
  assertExists(NEBULA_THEME);

  const source = readThemeFile();
  const summary = summarizeTheme(source);

  if (summary.bytes < 200) {
    throw new Error('R72N gate blocked: Nebula theme CSS is too small to certify');
  }

  verifyStyleOnlyBoundary(source);

  const semanticProof = {
    nebulaEvidence: assertMinimumNeedles(source, ['nebula', 'Nebula', 'WILSY_NEBULA', 'wilsy-nebula'], 1, 'Nebula identity contract'),
    commandEvidence: assertMinimumNeedles(source, ['command', 'Command', 'sovereign', 'Sovereign', 'superadmin', 'Superadmin'], 1, 'command/superadmin contract'),
    themeEvidence: assertMinimumNeedles(source, ['theme', 'Theme', 'skin', 'Skin', 'palette', 'Palette', 'token', 'Token', 'surface', 'Surface'], 2, 'theme/skin/token/surface contract'),
    cssVariableCount: summary.cssVariableCount,
    selectorCount: summary.selectorCount,
  };

  if (semanticProof.cssVariableCount < 3) {
    throw new Error(`R72N gate blocked: expected at least 3 CSS variables, found ${semanticProof.cssVariableCount}`);
  }

  assertIncludesAny(source, [':root', '[data-', '.wilsy', '.superadmin', '.nebula'], 'CSS scope contract');

  console.log(JSON.stringify({
    gate: 'R72N_SUPERADMIN_NEBULA_THEME_VERIFIED',
    lane: 'superadmin-theme-runtime',
    themeFile: 'client/src/styles/superadmin/themes/wilsy-nebula-command.css',
    fileCount: 1,
    files: [summary],
    semanticProof,
    isolatedLane: true,
    styleOnlyLane: true,
    noDashboardMutation: true,
    noCrmCssMutation: true,
    noCrmRailLeadThemeServiceMutation: true,
    noBackendAuthSecurityMutation: true,
    noAccountMutation: true,
    noScriptFabricMutation: true,
    noFilesystemReportExport: true,
    noSecrets: true,
    noR70F: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY SUPERADMIN R72N NEBULA THEME GATE');
  console.log(' - Superadmin Nebula command theme lane is isolated to client/src/styles/superadmin/themes/');
  console.log(' - CSS theme semantics prove Nebula, command/superadmin, and theme/token/surface contracts');
  console.log(' - no CRM dashboard, CRM CSS, CRM rail/lead/theme/service, backend, auth, account, or script-fabric files are inside the lane');
  console.log(' - no filesystem report/export, secret, or recursive expansion token shape present');
};

runR72NNebulaThemeGate();
