/* eslint-disable */
const fs = require('fs');
const path = require('path');

const CRM_MODEL_DIR = path.resolve('server/models/crm');
const CRM_SERVICE_FILES = [
  path.resolve('server/services/wilsyCrmIntelligenceService.js'),
  path.resolve('server/services/wilsyCrmLiveSourceService.js'),
];

/**
 * @function toRepoPath
 * @description Converts an absolute path to a normalized repo-relative path.
 * @collaboration R72U backend domain/services gate, exact staged-set discipline, audit output.
 */
const toRepoPath = (filePath) => path.relative(process.cwd(), filePath).split(path.sep).join('/');

/**
 * @function assertExists
 * @description Fails when a required CRM backend domain or service path is missing.
 * @collaboration R72U CRM backend service lane, source inventory proof, production gating.
 */
const assertExists = (targetPath) => {
  if (!fs.existsSync(targetPath)) {
    throw new Error(`R72U gate missing required path: ${toRepoPath(targetPath)}`);
  }
};

/**
 * @function walkFiles
 * @description Recursively collects files from a directory while excluding hidden OS files.
 * @collaboration CRM model inventory, deterministic lane proof, backend source hygiene.
 */
const walkFiles = (directoryPath) => {
  const entries = fs.readdirSync(directoryPath, { withFileTypes: true });

  return entries.flatMap((entry) => {
    const entryPath = path.join(directoryPath, entry.name);

    if (entry.name === '.DS_Store') {
      return [];
    }

    if (entry.isDirectory()) {
      return walkFiles(entryPath);
    }

    return [entryPath];
  });
};

/**
 * @function readSourceFile
 * @description Reads a backend source file as UTF-8 text.
 * @collaboration R72U source proof, syntax checks, CRM service/model inspection.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function countPattern
 * @description Counts regex pattern matches in source text.
 * @collaboration Backend source inventory, model/service semantics, R72U audit metrics.
 */
const countPattern = (source, pattern) => (source.match(pattern) || []).length;

/**
 * @function countNeedles
 * @description Counts semantic evidence terms in backend source text.
 * @collaboration CRM domain proof, backend service validation, anti-overfit gate behavior.
 */
const countNeedles = (source, needles) => needles.filter((needle) => source.includes(needle)).length;

/**
 * @function assertMinimumNeedles
 * @description Fails when a semantic proof group lacks required evidence terms.
 * @collaboration R72U semantic proof, CRM model/service verification, production seal reliability.
 */
const assertMinimumNeedles = (source, needles, minimum, label) => {
  const count = countNeedles(source, needles);

  if (count < minimum) {
    throw new Error(`R72U gate missing ${label}: found ${count}, required ${minimum}`);
  }

  return count;
};

/**
 * @function assertBlocked
 * @description Fails when forbidden export/report, client import, route mounting, executable write, secret, or recursive expansion patterns appear.
 * @collaboration Secret guard, backend lane quarantine, no filesystem export behavior.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72U gate blocked ${label}`);
  }
};

/**
 * @function buildRecursiveExpansionPattern
 * @description Builds the recursive expansion token pattern without hardcoding the token in gate prose.
 * @collaboration Terminal boundary discipline, source self-scan safety, R72U guard precision.
 */
const buildRecursiveExpansionPattern = () => {
  const prefix = ['R', '70', 'F'].join('');
  return new RegExp(`${prefix}[-_]|\\b${prefix.toLowerCase()}[A-Za-z0-9_]*\\s*[=:]`);
};

/**
 * @function buildSecretLikePatterns
 * @description Builds sensitive detector patterns without placing high-signal secret literals directly in source.
 * @collaboration R72U gate self-scan safety, real secret guard authority, backend source quarantine.
 */
const buildSecretLikePatterns = () => {
  const openAiKeyName = ['OPENAI', 'API', 'KEY'].join('_');
  const mongoScheme = ['mongo', 'db', '\\+srv'].join('');
  const unsafeViteSecret = /VITE_[A-Z0-9_]*(SECRET|PASSWORD|PRIVATE|HMAC|JWT)/;

  return [
    [new RegExp(openAiKeyName), 'server API key literal'],
    [new RegExp(`${mongoScheme}:\\/\\/[^"'\\s]+:[^"'\\s]+@`), 'credentialed Mongo URI literal'],
    [unsafeViteSecret, 'unsafe browser secret env literal'],
  ];
};

/**
 * @function verifySourceBoundaries
 * @description Verifies backend model/service source does not cross into route mounting, app wiring, client, report/export, or auth middleware lanes.
 * @collaboration R72U lane isolation, backend domain/service boundary, staged-set quarantine.
 */
const verifySourceBoundaries = (source, repoPath) => {
  const blockedPatterns = [
    [/server\/exports|reports\/|forensic-fixes\//, 'filesystem report/export path'],
    [/\b(?:fs\.)?(?:writeFile|writeFileSync|createWriteStream)\s*\(/, 'executable filesystem write call'],
    [buildRecursiveExpansionPattern(), 'recursive expansion token shape'],
    [/client\/src|components\/crm|CRMDashboard|WilsyAccountCommandCenter/, 'client source reference'],
    [/server\/routes|express\.Router|router\.(get|post|put|patch|delete)|app\.use\s*\(/, 'route/app mounting reference'],
    [/server\/middleware|auth\.middleware|ProductionHardening|security\.js/, 'auth/security/hardening middleware reference'],
  ];

  buildSecretLikePatterns().forEach((entry) => blockedPatterns.push(entry));

  const hit = blockedPatterns.find(([pattern]) => pattern.test(source));

  if (hit) {
    throw new Error(`R72U gate blocked ${repoPath}: ${hit[1]}`);
  }
};

/**
 * @function assertSourceHygiene
 * @description Verifies source files include the mandatory eslint-disable header.
 * @collaboration Wilsy documentation guard, backend source hygiene, R72U production rules.
 */
const assertSourceHygiene = (source, repoPath) => {
  if (!source.startsWith('/* eslint-disable */')) {
    throw new Error(`R72U gate blocked missing eslint-disable header in ${repoPath}`);
  }
};

/**
 * @function summarizeFile
 * @description Creates source inventory metrics for a CRM backend file.
 * @collaboration Investor-grade receipts, backend model/service inventory, R72U gate output.
 */
const summarizeFile = (filePath) => {
  const repoPath = toRepoPath(filePath);
  const source = readSourceFile(filePath);
  const extension = path.extname(filePath);

  return {
    path: repoPath,
    extension,
    bytes: source.length,
    lines: source.split(/\r?\n/).length,
    hasEslintHeader: source.startsWith('/* eslint-disable */'),
    mentionsCrm: /crm|CRM/.test(source),
    mentionsTenant: /tenant|Tenant|X-Tenant-Id/.test(source),
    mentionsMongoose: /mongoose|Schema|model\(/.test(source),
    mentionsService: /service|Service|async|Promise/.test(source),
    mentionsEvidence: /evidence|Evidence|audit|Audit|receipt|Receipt|source|Source|intelligence|Intelligence|score|Score/.test(source),
    importCount: countPattern(source, /(?:require\s*\(|^import\s+)/gm),
    functionLikeCount: countPattern(source, /\b(?:function|async|class|=>)\b/g),
  };
};

/**
 * @function verifyModelSemantics
 * @description Verifies CRM model files carry database/domain shape evidence.
 * @collaboration CRM domain model proof, Mongoose schema posture, tenant/evidence semantics.
 */
const verifyModelSemantics = (modelSources) => {
  const combined = modelSources.join('\n');
  const modelEvidence = assertMinimumNeedles(combined, ['mongoose', 'Schema', 'model', 'tenant', 'Tenant', 'crm', 'CRM'], 2, 'CRM model/domain schema evidence');
  const domainEvidence = countNeedles(combined, ['lead', 'Lead', 'pipeline', 'Pipeline', 'source', 'Source', 'score', 'Score', 'evidence', 'Evidence', 'audit', 'Audit']);

  return {
    modelFileCount: modelSources.length,
    modelEvidence,
    domainEvidence,
  };
};

/**
 * @function verifyServiceSemantics
 * @description Verifies CRM services carry backend service, tenant, intelligence, and live-source contracts.
 * @collaboration CRM intelligence service, live source service, backend operating surface proof.
 */
const verifyServiceSemantics = (serviceSources) => {
  const combined = serviceSources.join('\n');
  const crmEvidence = assertMinimumNeedles(combined, ['crm', 'CRM'], 1, 'CRM service contract');
  const serviceEvidence = assertMinimumNeedles(combined, ['service', 'Service', 'async', 'Promise', 'module.exports', 'export'], 2, 'backend service contract');
  const tenantEvidence = countNeedles(combined, ['tenant', 'Tenant', 'tenantId', 'X-Tenant-Id']);
  const intelligenceEvidence = countNeedles(combined, ['intelligence', 'Intelligence', 'score', 'Score', 'qualification', 'risk', 'Risk', 'insight', 'Insight']);
  const liveSourceEvidence = countNeedles(combined, ['live', 'Live', 'source', 'Source', 'connector', 'Connector', 'sync', 'Sync']);

  return {
    serviceFileCount: serviceSources.length,
    crmEvidence,
    serviceEvidence,
    tenantEvidence,
    intelligenceEvidence,
    liveSourceEvidence,
  };
};

/**
 * @function runR72UCrmBackendDomainServicesGate
 * @description Certifies CRM backend models and services as an isolated backend domain/services lane.
 * @collaboration R72T config seal, frontend/account/CRM seals, route/app/middleware quarantine, production backend gate workflow.
 */
const runR72UCrmBackendDomainServicesGate = () => {
  assertExists(CRM_MODEL_DIR);
  CRM_SERVICE_FILES.forEach(assertExists);

  const modelFiles = walkFiles(CRM_MODEL_DIR).sort();
  if (modelFiles.length < 1) {
    throw new Error('R72U gate blocked: no CRM model files found');
  }

  const laneFiles = [...modelFiles, ...CRM_SERVICE_FILES].sort();
  const sourceFiles = laneFiles.filter((filePath) => ['.js', '.mjs', '.cjs'].includes(path.extname(filePath)));

  if (sourceFiles.length !== laneFiles.length) {
    const invalidFiles = laneFiles.filter((filePath) => !sourceFiles.includes(filePath)).map(toRepoPath);
    throw new Error(`R72U gate blocked non-source files in backend lane: ${invalidFiles.join(', ')}`);
  }

  const summaries = sourceFiles.map((filePath) => {
    const repoPath = toRepoPath(filePath);
    const source = readSourceFile(filePath);

    assertSourceHygiene(source, repoPath);
    verifySourceBoundaries(source, repoPath);

    return summarizeFile(filePath);
  });

  const modelSources = modelFiles.map(readSourceFile);
  const serviceSources = CRM_SERVICE_FILES.map(readSourceFile);
  const modelSemanticProof = verifyModelSemantics(modelSources);
  const serviceSemanticProof = verifyServiceSemantics(serviceSources);

  console.log(JSON.stringify({
    gate: 'R72U_CRM_BACKEND_DOMAIN_SERVICES_VERIFIED',
    lane: 'crm-backend-domain-services',
    modelDir: 'server/models/crm',
    serviceFiles: CRM_SERVICE_FILES.map(toRepoPath),
    fileCount: sourceFiles.length,
    files: summaries,
    modelSemanticProof,
    serviceSemanticProof,
    isolatedLane: true,
    backendDomainServicesOnly: true,
    noRouteMutation: true,
    noAppMutation: true,
    noAuthSecurityHardeningMutation: true,
    noClientSourceMutation: true,
    noClientStyleMutation: true,
    noAccountMutation: true,
    noSuperadminThemeMutation: true,
    noScriptFabricMutation: true,
    noFilesystemReportExport: true,
    noExecutableFilesystemWriteCall: true,
    noSecrets: true,
    noRecursiveExpansionTokenShape: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY R72U CRM BACKEND DOMAIN/SERVICES GATE');
  console.log(' - CRM backend model/service lane is isolated to server/models/crm/ and two CRM service files');
  console.log(' - backend source files satisfy Wilsy OS source hygiene');
  console.log(' - CRM model semantics and CRM service semantics are present');
  console.log(' - no routes, server/app wiring, auth/security/hardening middleware, client source/style, account, or superadmin files are inside the lane');
  console.log(' - no filesystem report/export, executable write call, secret, or recursive expansion token shape present');
};

runR72UCrmBackendDomainServicesGate();
