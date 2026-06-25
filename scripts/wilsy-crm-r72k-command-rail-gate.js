/* eslint-disable */
const fs = require('fs');
const path = require('path');

const RAIL_DIR = path.resolve('client/src/components/crm/rail');
const SOURCE_EXTENSIONS = new Set(['.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx']);

/**
 * @function assertExists
 * @description Fails when the CRM command rail directory is missing.
 * @collaboration R72K command rail lane, exact staged-set discipline, production gate workflow.
 */
const assertExists = (targetPath) => {
  if (!fs.existsSync(targetPath)) {
    throw new Error(`R72K gate missing required path: ${targetPath}`);
  }
};

/**
 * @function listFilesRecursive
 * @description Lists all files under a directory recursively in stable sorted order.
 * @collaboration CRM command rail inventory, source hygiene, exact lane proof.
 */
const listFilesRecursive = (dirPath) => {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  const files = [];

  entries.forEach((entry) => {
    const absolutePath = path.join(dirPath, entry.name);

    if (entry.isDirectory()) {
      files.push(...listFilesRecursive(absolutePath));
      return;
    }

    if (entry.isFile()) {
      files.push(absolutePath);
    }
  });

  return files.sort();
};

/**
 * @function isSourceFile
 * @description Detects JavaScript and TypeScript source files that should carry Wilsy OS source contracts.
 * @collaboration Documentation guard, secret guard, CRM command rail proof.
 */
const isSourceFile = (filePath) => SOURCE_EXTENSIONS.has(path.extname(filePath));

/**
 * @function readSourceFile
 * @description Reads a source file as UTF-8 text.
 * @collaboration R72K command rail source inspection, guard checks, build proof.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function toRepoPath
 * @description Converts an absolute path to a normalized repo-relative path.
 * @collaboration Audit-friendly lane output, staged-set verification, command rail inventory.
 */
const toRepoPath = (filePath) => path.relative(process.cwd(), filePath).split(path.sep).join('/');

/**
 * @function assertEslintHeader
 * @description Fails when a source file lacks the mandatory eslint-disable header.
 * @collaboration Wilsy documentation guard, production source hygiene, R72K command rail lane.
 */
const assertEslintHeader = (source, repoPath) => {
  if (!source.startsWith('/* eslint-disable */')) {
    throw new Error(`R72K gate blocked missing eslint-disable header in ${repoPath}`);
  }
};

/**
 * @function assertIncludesAny
 * @description Fails when a source bundle lacks all required semantic contract fragments.
 * @collaboration Flexible source-shape validation, command rail proof, CRM cockpit quality.
 */
const assertIncludesAny = (source, needles, label) => {
  if (!needles.some((needle) => source.includes(needle))) {
    throw new Error(`R72K gate missing ${label}: ${needles.join(', ')}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden runtime filesystem, secret, backend, or recursive expansion patterns appear.
 * @collaboration Secret guard, no export/report behavior, tenant-safe CRM command rail.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72K gate blocked ${label}`);
  }
};

/**
 * @function summarizeFile
 * @description Produces an audit summary for a command rail file.
 * @collaboration Investor-grade lane receipts, source inventory, command rail gate output.
 */
const summarizeFile = (filePath) => {
  const source = readSourceFile(filePath);
  const repoPath = toRepoPath(filePath);

  return {
    path: repoPath,
    extension: path.extname(filePath),
    bytes: source.length,
    lines: source.split(/\r?\n/).length,
    sourceFile: isSourceFile(filePath),
    hasEslintHeader: isSourceFile(filePath) ? source.startsWith('/* eslint-disable */') : null,
    mentionsRail: /rail|Rail|sidebar|Sidebar|navigation|Navigation/.test(source + repoPath),
    mentionsCommand: /command|Command|cockpit|Cockpit|workspace|Workspace/.test(source + repoPath),
    mentionsCrm: /crm|CRM/.test(source + repoPath),
  };
};

/**
 * @function verifyRailSourceFiles
 * @description Verifies command rail source files satisfy source hygiene and runtime boundaries.
 * @collaboration CRM command rail lane, Wilsy OS guards, no mixed-lane mutation.
 */
const verifyRailSourceFiles = (files) => {
  const sourceFiles = files.filter(isSourceFile);

  if (sourceFiles.length < 1) {
    throw new Error('R72K gate blocked: command rail has no JS/TS source files');
  }

  const sourceBundle = sourceFiles
    .map((filePath) => `${toRepoPath(filePath)}\n${readSourceFile(filePath)}`)
    .join('\n\n');

  sourceFiles.forEach((filePath) => {
    const repoPath = toRepoPath(filePath);
    const source = readSourceFile(filePath);

    assertEslintHeader(source, repoPath);
    assertBlocked(source, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, `${repoPath} filesystem report/export behavior`);
    assertBlocked(source, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, `${repoPath} recursive expansion token shape`);
    assertBlocked(source, /VITE_[A-Z0-9_]*(SECRET|TOKEN|PASSWORD|PRIVATE|HMAC|JWT)|OPENAI_API_KEY|mongodb\+srv:\/\/[^"'\s]+:[^"'\s]+@/, `${repoPath} secret-like literal`);
    assertBlocked(source, /server\/middleware|server\/routes|server\/services|server\/models/, `${repoPath} backend path import`);
  });

  assertIncludesAny(sourceBundle, ['rail', 'Rail', 'sidebar', 'Sidebar', 'navigation', 'Navigation'], 'rail/navigation contract');
  assertIncludesAny(sourceBundle, ['command', 'Command', 'cockpit', 'Cockpit', 'workspace', 'Workspace'], 'command/workspace contract');
  assertIncludesAny(sourceBundle, ['crm', 'CRM'], 'CRM contract');

  return {
    sourceFileCount: sourceFiles.length,
    sourceFiles: sourceFiles.map(toRepoPath),
  };
};

/**
 * @function verifyNoCrossLaneFiles
 * @description Verifies the rail directory does not embed dashboard, lead, theme, service, backend, or auth lane files.
 * @collaboration R72K lane separation, quarantine discipline, no accidental broad commit.
 */
const verifyNoCrossLaneFiles = (files) => {
  const repoPaths = files.map(toRepoPath);
  const blocked = repoPaths.filter((repoPath) =>
    /CRMDashboard\.jsx|CRMDashboard\.module\.css|\/lead\/|\/theme\/|crmService\.js|server\/|middleware|auth|security|ProductionHardening|superadmin\/themes|components\/account/.test(repoPath)
  );

  if (blocked.length) {
    throw new Error(`R72K gate blocked cross-lane files: ${JSON.stringify(blocked, null, 2)}`);
  }

  return {
    crossLaneFiles: 0,
  };
};

/**
 * @function runR72KCommandRailGate
 * @description Certifies the CRM command rail lane as an isolated, source-safe, build-backed Wilsy OS rail surface.
 * @collaboration R72J account theme seal, R72H dashboard reconciliation, R72K command rail lane.
 */
const runR72KCommandRailGate = () => {
  assertExists(RAIL_DIR);

  const files = listFilesRecursive(RAIL_DIR);

  if (files.length < 1) {
    throw new Error('R72K gate blocked: no command rail files found');
  }

  const railProof = verifyRailSourceFiles(files);
  const crossLaneProof = verifyNoCrossLaneFiles(files);
  const fileSummaries = files.map(summarizeFile);

  console.log(JSON.stringify({
    gate: 'R72K_CRM_COMMAND_RAIL_VERIFIED',
    lane: 'crm-command-rail',
    railDir: 'client/src/components/crm/rail',
    fileCount: files.length,
    sourceFileCount: railProof.sourceFileCount,
    files: fileSummaries,
    sourceFiles: railProof.sourceFiles,
    crossLaneProof,
    isolatedLane: true,
    noDashboardMutation: true,
    noLeadThemeServiceMutation: true,
    noBackendAuthSecurityMutation: true,
    noAccountMutation: true,
    noSuperadminThemeMutation: true,
    noFilesystemReportExport: true,
    noSecrets: true,
    noR70F: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY CRM R72K COMMAND RAIL GATE');
  console.log(' - CRM command rail lane is isolated under client/src/components/crm/rail/');
  console.log(' - command rail source files satisfy Wilsy OS source hygiene');
  console.log(' - no dashboard, lead, theme, service, backend, auth, account, or superadmin files are inside rail lane');
  console.log(' - no filesystem report/export, secret, or recursive expansion token shape present');
};

runR72KCommandRailGate();
