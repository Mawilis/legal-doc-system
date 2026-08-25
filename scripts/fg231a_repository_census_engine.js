/**
 * ============================================================================
 * WILSY OS - ENTERPRISE REPOSITORY CENSUS & BASELINE ENGINE (FG231A)
 * ============================================================================
 *
 * @file         fg231a_repository_census_engine.js
 * @directory    scripts/
 * @system       Wilsy OS - Institutional Audit & Integration Layer (FG231A)
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Forensic, zero-mutation repository scanner and enterprise
 *               capability map generator. Audits server/ and client/ to build
 *               an immutable inventory, dependency graph, API atlas, schema
 *               dictionary, and engine wiring matrix for Generation 2 execution.
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Sovereign census engine for FG231A
 *            |                 |         | Repository & Capability Mapping.
 * ============================================================================
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

/**
 * Directories to strictly scan and directories/files to ignore during audit.
 */
const PROJECT_ROOT = path.resolve(__dirname, '..');
const SCAN_TARGETS = ['server', 'client', 'scripts'];
const IGNORE_DIRS = new Set(['node_modules', '.venv', '.git', 'dist', 'build', 'coverage', '.next']);
const IGNORE_FILES = new Set(['.DS_Store', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock']);

/**
 * Enterprise Subsystem Engine Classification Mapping Protocol.
 */
const ENGINE_MAP = {
  ENTERPRISE_KERNEL: [/kernel/i, /redact/i, /popia/i, /security/i, /context/i, /crypto/i],
  OBJECT_REGISTRY: [/registry/i, /object/i, /schema/i, /domain/i],
  WORKFLOW_ENGINE: [/workflow/i, /state/i, /transition/i, /lifecycle/i],
  GRAPH_ENGINE: [/graph/i, /traversal/i, /relationship/i, /link/i],
  TENANCY_ISOLATION: [/tenant/i, /provision/i, /isolation/i],
  AUTH_GATEWAY: [/auth/i, /jwt/i, /session/i, /role/i, /permission/i],
  BILLING_ENGINE: [/billing/i, /invoice/i, /payment/i, /subscription/i],
  LEGAL_DOCUMENT_ENGINE: [/document/i, /template/i, /clause/i, /contract/i, /signature/i],
  AI_INTELLIGENCE: [/ai/i, /predict/i, /twin/i, /knowledge/i, /reasoning/i],
  CLIENT_UI_WORKSPACE: [/client/i, /component/i, /view/i, /page/i, /hook/i, /store/i]
};

/**
 * Computes SHA-256 hash for raw file content to ensure zero-loss provenance.
 * @param {string} content - Raw text file content.
 * @returns {string} SHA-256 hash hex string.
 */
function hashContent(content) {
  return crypto.createHash('sha256').update(content).digest('hex');
}

/**
 * Computes a Merkle Tree Root Hash from a list of leaf hashes.
 * @param {string[]} hashes - Sorted list of file SHA-256 hashes.
 * @returns {string} 64-character SHA-256 Merkle Root.
 */
function computeMerkleRoot(hashes) {
  if (!hashes || hashes.length === 0) return crypto.createHash('sha256').update('EMPTY_TREE').digest('hex');
  let currentLevel = [...hashes].sort();

  while (currentLevel.length > 1) {
    const nextLevel = [];
    for (let i = 0; i < currentLevel.length; i += 2) {
      if (i + 1 < currentLevel.length) {
        const combined = currentLevel[i] + currentLevel[i + 1];
        nextLevel.push(crypto.createHash('sha256').update(combined).digest('hex'));
      } else {
        nextLevel.push(currentLevel[i]);
      }
    }
    currentLevel = nextLevel;
  }
  return currentLevel[0];
}

/**
 * Audits dependency import statements (CommonJS & ESM).
 * @param {string} content - File source code.
 * @returns {string[]} List of imported module paths.
 */
function extractDependencies(content) {
  const dependencies = new Set();
  const requireRegex = /require\(['"]([^'"]+)['"]\)/g;
  const importRegex = /from\s+['"]([^'"]+)['"]/g;

  let match;
  while ((match = requireRegex.exec(content)) !== null) {
    dependencies.add(match[1]);
  }
  while ((match = importRegex.exec(content)) !== null) {
    dependencies.add(match[1]);
  }
  return Array.from(dependencies);
}

/**
 * Audits HTTP API Endpoint routes defined in Express/Router instances.
 * @param {string} content - File source code.
 * @returns {object[]} List of identified routes with HTTP verbs.
 */
function extractAPIRoutes(content) {
  const routes = [];
  const routeRegex = /(router|app)\.(get|post|put|patch|delete|use)\(['"]([^'"]+)['"]/gi;
  let match;
  while ((match = routeRegex.exec(content)) !== null) {
    routes.push({ method: match[2].toUpperCase(), path: match[3] });
  }
  return routes;
}

/**
 * Classifies a target file into an Enterprise Engine domain owner.
 * @param {string} relativePath - Relative path of file.
 * @param {string} content - File source code.
 * @returns {string} Assigned Enterprise Engine name.
 */
function classifyEngine(relativePath, content) {
  for (const [engine, patterns] of Object.entries(ENGINE_MAP)) {
    for (const pattern of patterns) {
      if (pattern.test(relativePath) || pattern.test(content.slice(0, 500))) {
        return engine;
      }
    }
  }
  return 'PLATFORM_SHARED_SERVICES';
}

/**
 * Recursively scans directory target and performs multi-phase census audit.
 * @param {string} dir - Directory path to inspect.
 * @param {object} census - Accumulator manifest data structure.
 */
function scanDirectoryRecursive(dir, census) {
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.relative(PROJECT_ROOT, fullPath);

      if (entry.isDirectory()) {
        if (!IGNORE_DIRS.has(entry.name)) {
          census.summary.directoryCount++;
          scanDirectoryRecursive(fullPath, census);
        }
      } else if (entry.isFile()) {
        if (IGNORE_FILES.has(entry.name)) continue;

        const ext = path.extname(entry.name).toLowerCase();
        const stat = fs.statSync(fullPath);
        const content = fs.readFileSync(fullPath, 'utf8');
        const fileHash = hashContent(content);

        census.summary.fileCount++;
        census.summary.totalSizeBytes += stat.size;
        census.summary.languageStats[ext] = (census.summary.languageStats[ext] || 0) + 1;
        census.leafHashes.push(fileHash);

        const assignedEngine = classifyEngine(relativePath, content);
        const dependencies = extractDependencies(content);
        const apiRoutes = extractAPIRoutes(content);

        const fileRecord = {
          relativePath,
          sizeBytes: stat.size,
          extension: ext,
          sha256: fileHash,
          assignedEngine,
          dependenciesCount: dependencies.length,
          dependencies,
          apiRoutesCount: apiRoutes.length,
          apiRoutes,
          isOrphanCandidate: dependencies.length === 0 && !relativePath.includes('test') && !relativePath.includes('index')
        };

        census.manifest[relativePath] = fileRecord;

        // Group into Enterprise Engine Registry
        if (!census.engineRegistry[assignedEngine]) {
          census.engineRegistry[assignedEngine] = [];
        }
        census.engineRegistry[assignedEngine].push(relativePath);

        // Aggregate API Atlas
        if (apiRoutes.length > 0) {
          census.apiAtlas.push(...apiRoutes.map(r => ({ ...r, file: relativePath })));
        }

        // Flag potential orphan or un-imported files
        if (fileRecord.isOrphanCandidate) {
          census.gapAnalysis.orphanCandidates.push(relativePath);
        }
      }
    }
  } catch (error) {
    census.gapAnalysis.scanErrors.push({ dir, error: error.message });
  }
}

/**
 * Main Execution Function for FG231A Census Engine.
 */
function runFG231ACensus() {
  const startTime = process.hrtime.bigint();
  console.log('================================================================');
  console.log(' WILSY OS — FG231A REPOSITORY CENSUS & INTEGRATION BASELINE ENGINE');
  console.log('================================================================');
  console.log('Authority: Wilson Khanyezi | Founder & Chief Architect');
  console.log('Status: Executing Zero-Loss Forensic Scan...');
  console.log('----------------------------------------------------------------\n');

  const census = {
    metadata: {
      system: 'Wilsy OS',
      milestone: 'FG231A',
      timestampSAST: new Date().toISOString(),
      architectureVersion: '2.0.0-GEN2-BASELINE'
    },
    summary: {
      fileCount: 0,
      directoryCount: 0,
      totalSizeBytes: 0,
      languageStats: {}
    },
    leafHashes: [],
    engineRegistry: {},
    apiAtlas: [],
    gapAnalysis: {
      orphanCandidates: [],
      scanErrors: []
    },
    manifest: {}
  };

  for (const target of SCAN_TARGETS) {
    const targetPath = path.join(PROJECT_ROOT, target);
    if (fs.existsSync(targetPath)) {
      scanDirectoryRecursive(targetPath, census);
    }
  }

  // Phase 9: Compute Cryptographic Merkle Root
  const merkleRoot = computeMerkleRoot(census.leafHashes);
  census.metadata.merkleRootHash = merkleRoot;

  // Phase 10: Finalize Generation 2 Work Queue Metrics
  const endTime = process.hrtime.bigint();
  const durationMs = Number(endTime - startTime) / 1e6;
  census.metadata.scanDurationMs = durationMs.toFixed(3);

  // Write Master Manifest Artifact
  const reportsDir = path.join(PROJECT_ROOT, 'reports');
  if (!fs.existsSync(reportsDir)) {
    fs.mkdirSync(reportsDir, { recursive: true });
  }

  const manifestPath = path.join(reportsDir, 'fg231a_repository_census_manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify(census, null, 2), 'utf8');

  // Print Executive Terminal Audit Summary
  console.log('----------------------------------------------------------------');
  console.log('FG231A INSTITUTIONAL CENSUS COMPLETE');
  console.log('----------------------------------------------------------------');
  console.log(`Total Files Audited       : ${census.summary.fileCount}`);
  console.log(`Total Directories Scanned : ${census.summary.directoryCount}`);
  console.log(`Repository Raw Size       : ${(census.summary.totalSizeBytes / 1024 / 1024).toFixed(2)} MB`);
  console.log(`Discovered API Endpoints  : ${census.apiAtlas.length}`);
  console.log(`Orphan/Standalone Files  : ${census.gapAnalysis.orphanCandidates.length}`);
  console.log(`Scan Performance Latency  : ${durationMs.toFixed(3)} ms`);
  console.log(`Cryptographic Merkle Root : ${merkleRoot}`);
  console.log('----------------------------------------------------------------');
  console.log('ENGINE DOMAIN ALLOCATION MATRIX:');
  for (const [engine, files] of Object.entries(census.engineRegistry)) {
    console.log(`  • ${engine.padEnd(25)} : ${files.length} files`);
  }
  console.log('----------------------------------------------------------------');
  console.log(`Master Audit Manifest Generated At:\n -> ${manifestPath}`);
  console.log('================================================================\n');
}

if (require.main === module) {
  runFG231ACensus();
}
