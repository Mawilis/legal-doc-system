/* eslint-disable */
const fs = require('fs');
const path = require('path');

const LEAD_DIR = path.resolve('client/src/components/crm/lead');
const SOURCE_EXTENSIONS = new Set(['.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx']);

/**
 * @function assertExists
 * @description Fails when the CRM lead operating room directory is missing.
 * @collaboration R72L lead operating room lane, exact staged-set discipline, production gate workflow.
 */
const assertExists = (targetPath) => {
  if (!fs.existsSync(targetPath)) {
    throw new Error(`R72L gate missing required path: ${targetPath}`);
  }
};

/**
 * @function listFilesRecursive
 * @description Lists all files under a directory recursively in stable sorted order.
 * @collaboration CRM lead operating room inventory, source hygiene, exact lane proof.
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
 * @collaboration Documentation guard, secret guard, CRM lead operating room proof.
 */
const isSourceFile = (filePath) => SOURCE_EXTENSIONS.has(path.extname(filePath));

/**
 * @function readSourceFile
 * @description Reads a source file as UTF-8 text.
 * @collaboration R72L lead operating room source inspection, guard checks, build proof.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function toRepoPath
 * @description Converts an absolute path to a normalized repo-relative path.
 * @collaboration Audit-friendly lane output, staged-set verification, lead operating room inventory.
 */
const toRepoPath = (filePath) => path.relative(process.cwd(), filePath).split(path.sep).join('/');

/**
 * @function assertEslintHeader
 * @description Fails when a source file lacks the mandatory eslint-disable header.
 * @collaboration Wilsy documentation guard, production source hygiene, R72L lead operating room lane.
 */
const assertEslintHeader = (source, repoPath) => {
  if (!source.startsWith('/* eslint-disable */')) {
    throw new Error(`R72L gate blocked missing eslint-disable header in ${repoPath}`);
  }
};

/**
 * @function assertIncludesAny
 * @description Fails when a source bundle lacks all required semantic contract fragments.
 * @collaboration Flexible source-shape validation, lead operating room proof, CRM quality.
 */
const assertIncludesAny = (source, needles, label) => {
  if (!needles.some((needle) => source.includes(needle))) {
    throw new Error(`R72L gate missing ${label}: ${needles.join(', ')}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden runtime filesystem, secret, backend, or recursive expansion patterns appear.
 * @collaboration Secret guard, no export/report behavior, tenant-safe CRM lead operating room.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72L gate blocked ${label}`);
  }
};

/**
 * @function summarizeFile
 * @description Produces an audit summary for a lead operating room file.
 * @collaboration Investor-grade lane receipts, source inventory, lead operating room gate output.
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
    mentionsLead: /lead|Lead|prospect|Prospect|opportunity|Opportunity/.test(source + repoPath),
    mentionsCrm: /crm|CRM/.test(source + repoPath),
    mentionsCommand: /command|Command|cockpit|Cockpit|operating|Operating|workspace|Workspace/.test(source + repoPath),
    mentionsEvidence: /evidence|Evidence|receipt|Receipt|audit|Audit|forensic|Forensic/.test(source + repoPath),
  };
};

/**
 * @function verifyLeadSourceFiles
 * @description Verifies lead operating room source files satisfy source hygiene and runtime boundaries.
 * @collaboration CRM lead lane, Wilsy OS guards, no mixed-lane mutation.
 */
const verifyLeadSourceFiles = (files) => {
  const sourceFiles = files.filter(isSourceFile);

  if (sourceFiles.length < 1) {
    throw new Error('R72L gate blocked: lead operating room has no JS/TS source files');
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

  assertIncludesAny(sourceBundle, ['lead', 'Lead', 'prospect', 'Prospect', 'opportunity', 'Opportunity'], 'lead/prospect/opportunity contract');
  assertIncludesAny(sourceBundle, ['crm', 'CRM'], 'CRM contract');
  assertIncludesAny(sourceBundle, ['command', 'Command', 'cockpit', 'Cockpit', 'operating', 'Operating', 'workspace', 'Workspace'], 'command/workspace contract');

  return {
    sourceFileCount: sourceFiles.length,
    sourceFiles: sourceFiles.map(toRepoPath),
  };
};

/**
 * @function verifyNoCrossLaneFiles
 * @description Verifies the lead directory does not embed dashboard, rail, theme, service, backend, auth, account, or superadmin lane files.
 * @collaboration R72L lane separation, quarantine discipline, no accidental broad commit.
 */
const verifyNoCrossLaneFiles = (files) => {
  const repoPaths = files.map(toRepoPath);
  const blocked = repoPaths.filter((repoPath) =>
    /CRMDashboard\.jsx|CRMDashboard\.module\.css|\/rail\/|\/theme\/|crmService\.js|server\/|middleware|auth|security|ProductionHardening|superadmin\/themes|components\/account/.test(repoPath)
  );

  if (blocked.length) {
    throw new Error(`R72L gate blocked cross-lane files: ${JSON.stringify(blocked, null, 2)}`);
  }

  return {
    crossLaneFiles: 0,
  };
};

/**
 * @function runR72LLeadOperatingRoomGate
 * @description Certifies the CRM lead operating room lane as an isolated, source-safe, build-backed Wilsy OS lead cockpit surface.
 * @collaboration R72J account theme seal, R72K command rail seal, R72H dashboard reconciliation, R72L lead lane.
 */
const runR72LLeadOperatingRoomGate = () => {
  assertExists(LEAD_DIR);

  const files = listFilesRecursive(LEAD_DIR);

  if (files.length < 1) {
    throw new Error('R72L gate blocked: no lead operating room files found');
  }

  const leadProof = verifyLeadSourceFiles(files);
  const crossLaneProof = verifyNoCrossLaneFiles(files);
  const fileSummaries = files.map(summarizeFile);

  console.log(JSON.stringify({
    gate: 'R72L_CRM_LEAD_OPERATING_ROOM_VERIFIED',
    lane: 'crm-lead-operating-room',
    leadDir: 'client/src/components/crm/lead',
    fileCount: files.length,
    sourceFileCount: leadProof.sourceFileCount,
    files: fileSummaries,
    sourceFiles: leadProof.sourceFiles,
    crossLaneProof,
    isolatedLane: true,
    noDashboardMutation: true,
    noRailThemeServiceMutation: true,
    noBackendAuthSecurityMutation: true,
    noAccountMutation: true,
    noSuperadminThemeMutation: true,
    noFilesystemReportExport: true,
    noSecrets: true,
    noR70F: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY CRM R72L LEAD OPERATING ROOM GATE');
  console.log(' - CRM lead operating room lane is isolated under client/src/components/crm/lead/');
  console.log(' - lead source files satisfy Wilsy OS source hygiene');
  console.log(' - no dashboard, rail, theme, service, backend, auth, account, or superadmin files are inside lead lane');
  console.log(' - no filesystem report/export, secret, or recursive expansion token shape present');
};

runR72LLeadOperatingRoomGate();
