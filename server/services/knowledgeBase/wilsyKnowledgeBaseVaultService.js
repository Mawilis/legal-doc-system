/* eslint-disable */

import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import fsSync from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const SERVICE_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(SERVICE_DIR, '../../..');
const MANIFEST_FILE = path.join(REPO_ROOT, 'client/src/data/wilsyKnowledgeBaseManifest.js');
const FULL_ACCESS_ROLES = new Set([
  'FOUNDER',
  'SOVEREIGN',
  'SUPER_ADMIN',
  'SUPERADMIN',
  'ADMIN',
  'OWNER',
]);
const VERIFIED_POSTURES = new Set([
  'KNOWLEDGE_BASE_VERIFIED',
  'LOCKED',
  'VERIFIED',
  'LOCKED_AFTER_VISUAL_PROOF_AND_MANIFEST_PROOF_CONTRACT',
  'JSON_VERIFIED',
  'COMPLETE_SET_VERIFIED',
]);

/**
 * @function textValue
 * @description Normalizes unknown values into safe display text for the Knowledge Base Vault.
 * @param {unknown} value Source value.
 * @param {string} fallback Fallback value.
 * @returns {string} Normalized text.
 * @collaboration FG108O3N2 Vault resolver, manifest integrity, and source-aware UI.
 */
function textValue(value, fallback = '') {
  if (typeof value === 'string') return value.trim() || fallback;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return fallback;
}

/**
 * @function safeRepoFile
 * @description Resolves manifest-declared repo files while blocking path traversal and external file reads.
 * @param {string} relativePath Manifest-declared relative path.
 * @returns {string} Absolute repo file path.
 * @collaboration FG108O3N2 Vault resolver, proof sidecar access, and saved PDF access.
 */
function safeRepoFile(relativePath = '') {
  const normalized = textValue(relativePath).replace(/^\/+/, '');

  if (!normalized) {
    const error = new Error('KNOWLEDGE_BASE_FILE_PATH_REQUIRED');
    error.statusCode = 422;
    throw error;
  }

  const absolutePath = path.resolve(REPO_ROOT, normalized);
  const boundary = `${REPO_ROOT}${path.sep}`;

  if (!absolutePath.startsWith(boundary)) {
    const error = new Error('KNOWLEDGE_BASE_FILE_PATH_FORBIDDEN');
    error.statusCode = 403;
    throw error;
  }

  return absolutePath;
}

/**
 * @function readJsonFile
 * @description Reads a JSON proof sidecar from a manifest-declared file path.
 * @param {string} absolutePath Absolute proof sidecar path.
 * @returns {Promise<object>} Parsed JSON.
 * @collaboration FG108O3N2 Vault resolver, SHA3 proof sidecars, and evidence JSON display.
 */
async function readJsonFile(absolutePath = '') {
  const raw = await fs.readFile(absolutePath, 'utf8');
  return JSON.parse(raw);
}

/**
 * @function fileExists
 * @description Checks saved artifact existence without creating or regenerating files.
 * @param {string} absolutePath Absolute artifact path.
 * @returns {boolean} Existence state.
 * @collaboration FG108O3N2 Vault resolver and fail-closed saved artifact reads.
 */
function fileExists(absolutePath = '') {
  return Boolean(absolutePath && fsSync.existsSync(absolutePath));
}

/**
 * @function digestPdfSha3
 * @description Computes a SHA3-512 hash for a saved PDF without mutating the artifact.
 * @param {string} absolutePath Absolute saved PDF path.
 * @returns {Promise<string>} SHA3-512 digest.
 * @collaboration FG108O3N2 Vault resolver, Knowledge Base guard, and proof sidecar verification.
 */
async function digestPdfSha3(absolutePath = '') {
  const buffer = await fs.readFile(absolutePath);
  return crypto.createHash('sha3-512').update(buffer).digest('hex');
}

/**
 * @function readKnowledgeBaseManifest
 * @description Imports the existing Knowledge Base manifest as the only Vault source of truth.
 * @returns {Promise<Array<object>>} Manifest entries.
 * @collaboration FG108O3N2 Vault resolver and manifest-backed artifact discovery.
 */
async function readKnowledgeBaseManifest() {
  const moduleUrl = pathToFileURL(MANIFEST_FILE).href;
  const manifestModule = await import(moduleUrl);
  const manifest = manifestModule.wilsyKnowledgeBaseManifest || manifestModule.default || [];

  if (!Array.isArray(manifest)) {
    const error = new Error('KNOWLEDGE_BASE_MANIFEST_INVALID');
    error.statusCode = 500;
    throw error;
  }

  return manifest;
}

/**
 * @function resolveVaultPermissionContext
 * @description Resolves Founder/admin full view and tenant read posture from authenticated request user context.
 * @param {object} user Authenticated user or admin context.
 * @returns {object} Permission context.
 * @collaboration FG108O3N2 Vault route, tenant posture, and Founder authority.
 */
function resolveVaultPermissionContext(user = {}) {
  const role = textValue(user.role || user.userRole || user.primaryRole, 'USER').toUpperCase();
  const permissions = Array.isArray(user.permissions) ? user.permissions : [];
  const scopes = Array.isArray(user.scopes) ? user.scopes : [];
  const fullAccess =
    FULL_ACCESS_ROLES.has(role) || permissions.includes('*') || scopes.includes('*');

  return {
    role,
    mode: fullAccess ? 'FOUNDER_ADMIN_FULL_VIEW' : 'TENANT_PERMISSIONED_READ_MODE',
    fullAccess,
  };
}

/**
 * @function isApprovedVaultEntry
 * @description Determines whether a manifest entry is safe for permissioned tenant read mode.
 * @param {object} entry Manifest entry.
 * @param {object} proof Proof sidecar.
 * @param {boolean} proofMatches Whether sidecar SHA3 matches saved PDF.
 * @returns {boolean} Approval state.
 * @collaboration FG108O3N2 Vault permissions and locked artifact posture.
 */
function isApprovedVaultEntry(entry = {}, proof = {}, proofMatches = false) {
  const sourcePosture = textValue(entry.sourcePosture || proof.sourcePosture).toUpperCase();
  const lockStatus = textValue(entry.lockStatus || proof.lockStatus).toUpperCase();

  return (
    proofMatches ||
    VERIFIED_POSTURES.has(sourcePosture) ||
    VERIFIED_POSTURES.has(lockStatus) ||
    lockStatus.includes('LOCKED') ||
    sourcePosture.includes('VERIFIED')
  );
}

/**
 * @function createVaultRoutes
 * @description Creates saved PDF and proof sidecar URLs for a Vault entry without using the PDF generation route.
 * @param {string} id Manifest artifact id.
 * @returns {object} Vault route map.
 * @collaboration FG108O3N2 Vault UI and saved artifact access.
 */
function createVaultRoutes(id = '') {
  const encodedId = encodeURIComponent(id);

  return {
    pdfOpenUrl: `/api/knowledge-base/vault/${encodedId}/pdf`,
    pdfDownloadUrl: `/api/knowledge-base/vault/${encodedId}/pdf?download=true`,
    jsonUrl: `/api/knowledge-base/vault/${encodedId}/json`,
    jsonDownloadUrl: `/api/knowledge-base/vault/${encodedId}/json?download=true`,
    proofUrl: `/api/knowledge-base/vault/${encodedId}/proof`,
  };
}

/**
 * @function normalizeVaultEntry
 * @description Converts a manifest entry and proof sidecar into a source-aware Vault row.
 * @param {object} entry Manifest entry.
 * @param {object} permission Permission context.
 * @returns {Promise<object|null>} Normalized Vault entry or null.
 * @collaboration FG108O3N2 Vault UI, proof ledger metadata, and saved PDF operations.
 */
async function normalizeVaultEntry(entry = {}, permission = {}) {
  const id = textValue(entry.id || entry.artifactId || entry.slug);
  if (!id) return null;

  const pdfPath = textValue(entry.pdfPath);
  const proofPath = textValue(entry.proofPath);
  const jsonPath = textValue(entry.jsonPath);
  const publicPdfPath = textValue(entry.publicPdfPath);
  const publicJsonPath = textValue(entry.publicJsonPath);

  const pdfFile = safeRepoFile(pdfPath);
  const proofFile = safeRepoFile(proofPath);
  const jsonFile = jsonPath ? safeRepoFile(jsonPath) : '';
  const pdfPresent = fileExists(pdfFile);
  const proofPresent = fileExists(proofFile);
  const jsonPresent = jsonPath ? fileExists(jsonFile) : false;

  let proof = {};
  let computedPdfSha3 = '';
  let computedJsonSha3 = '';
  let proofMatches = false;

  if (proofPresent) {
    proof = await readJsonFile(proofFile);
  }

  if (pdfPresent) {
    computedPdfSha3 = await digestPdfSha3(pdfFile);
  }

  if (jsonPresent) {
    computedJsonSha3 = await digestPdfSha3(jsonFile);
  }

  const declaredPdfSha3 = textValue(proof.pdfSha3 || entry.pdfSha3);
  const declaredJsonSha3 = textValue(proof.jsonSha3 || entry.jsonSha3);
  proofMatches = Boolean(declaredPdfSha3 && computedPdfSha3 && declaredPdfSha3 === computedPdfSha3);

  const approved = isApprovedVaultEntry(entry, proof, proofMatches);

  if (!permission.fullAccess && !approved) {
    return null;
  }

  const title = textValue(proof.title || entry.title || entry.name, id);

  const artifactType = textValue(
    proof.artifactType || entry.artifactType || entry.type,
    'KNOWLEDGE_BASE_ARTIFACT'
  );

  return {
    id,
    title,
    artifactType,
    sourcePosture: textValue(proof.sourcePosture || entry.sourcePosture, 'SOURCE_POSTURE_PENDING'),
    generatedByDisplayName: textValue(
      proof.generatedByDisplayName || entry.generatedByDisplayName,
      'PROFILE_REQUIRED'
    ),
    sourceCommit: textValue(entry.sourceCommit || proof.sourceCommit),
    sourceTag: textValue(entry.sourceTag || proof.sourceTag),
    lockStatus: textValue(
      proof.lockStatus || entry.lockStatus,
      approved ? 'LOCKED_OR_VERIFIED' : 'PENDING'
    ),
    pdfPath,
    proofPath,
    jsonPath,
    publicPdfPath,
    publicJsonPath,
    pdfSha3: declaredPdfSha3,
    jsonSha3: declaredJsonSha3,
    computedPdfSha3,
    computedJsonSha3,
    proofStatus: proofMatches ? 'SHA3_PROOF_MATCH' : 'SHA3_PROOF_REVIEW_REQUIRED',
    pdfPresent,
    proofPresent,
    jsonPresent,
    jsonStatus: jsonPresent && declaredJsonSha3 && declaredJsonSha3 === computedJsonSha3
      ? 'JSON_SHA3_PROOF_MATCH'
      : jsonPresent
        ? 'JSON_AVAILABLE'
        : 'JSON_NOT_DECLARED',
    requiredPdfTextCount: Number(proof.requiredPdfTextCount || proof.requiredPdfText?.length || 0),
    forbiddenPdfTextCount: Number(
      proof.forbiddenPdfTextCount || proof.forbiddenPdfText?.length || 0
    ),
    canonicalSectionsCount: Number(
      proof.canonicalSectionsCount || proof.canonicalSections?.length || 0
    ),
    requiredTextPosture:
      Number(proof.requiredPdfTextCount || proof.requiredPdfText?.length || 0) > 0
        ? 'REQUIRED_TEXT_DECLARED'
        : 'REQUIRED_TEXT_PENDING',
    forbiddenTextPosture:
      Number(proof.forbiddenPdfTextCount || proof.forbiddenPdfText?.length || 0) > 0
        ? 'FORBIDDEN_TEXT_DECLARED'
        : 'FORBIDDEN_TEXT_PENDING',
    permissionMode: permission.mode,
    allowedActions: {
      open: pdfPresent,
      print: pdfPresent,
      download: pdfPresent,
      json: jsonPresent,
      proof: proofPresent,
    },
    routes: createVaultRoutes(id),
  };
}

/**
 * @function resolveKnowledgeBaseVaultEntries
 * @description Resolves all permissioned Knowledge Base Vault entries from the existing manifest only.
 * @param {object} user Authenticated user or admin context.
 * @returns {Promise<object>} Vault payload.
 * @collaboration FG108O3N2 global Knowledge Base Vault and manifest-backed artifact listing.
 */
export async function resolveKnowledgeBaseVaultEntries(user = {}) {
  const permission = resolveVaultPermissionContext(user);
  const manifest = await readKnowledgeBaseManifest();
  const entries = [];

  for (const entry of manifest) {
    const normalized = await normalizeVaultEntry(entry, permission);
    if (normalized) entries.push(normalized);
  }

  return {
    generatedAt: new Date().toISOString(),
    manifestSource: 'client/src/data/wilsyKnowledgeBaseManifest.js',
    sourceMode: 'MANIFEST_BACKED_SAVED_ARTIFACTS_ONLY',
    permission,
    entries,
  };
}

/**
 * @function resolveKnowledgeBaseVaultEntryById
 * @description Resolves one permissioned Vault entry by manifest id.
 * @param {string} id Artifact id.
 * @param {object} user Authenticated user or admin context.
 * @returns {Promise<object>} Vault entry.
 * @collaboration FG108O3N2 Vault file route, proof route, and permission enforcement.
 */
export async function resolveKnowledgeBaseVaultEntryById(id = '', user = {}) {
  const vault = await resolveKnowledgeBaseVaultEntries(user);
  const entry = vault.entries.find((candidate) => candidate.id === id);

  if (!entry) {
    const error = new Error('KNOWLEDGE_BASE_VAULT_ENTRY_NOT_FOUND');
    error.statusCode = 404;
    throw error;
  }

  return entry;
}

/**
 * @function readKnowledgeBaseVaultProof
 * @description Reads one permissioned proof sidecar JSON for the Vault UI.
 * @param {string} id Artifact id.
 * @param {object} user Authenticated user or admin context.
 * @returns {Promise<object>} Proof sidecar payload.
 * @collaboration FG108O3N2 proof sidecar route and evidence JSON action.
 */
export async function readKnowledgeBaseVaultProof(id = '', user = {}) {
  const entry = await resolveKnowledgeBaseVaultEntryById(id, user);
  const proofFile = safeRepoFile(entry.proofPath);
  const proof = await readJsonFile(proofFile);

  return {
    generatedAt: new Date().toISOString(),
    sourceMode: 'PROOF_SIDECAR_READ_ONLY',
    entry,
    proof,
  };
}

/**
 * @function resolveKnowledgeBaseVaultPdfFile
 * @description Resolves one saved PDF file path for open, print, or download actions without regeneration.
 * @param {string} id Artifact id.
 * @param {object} user Authenticated user or admin context.
 * @returns {Promise<object>} Saved PDF file payload.
 * @collaboration FG108O3N2 saved PDF route and no-regeneration Vault contract.
 */
export async function resolveKnowledgeBaseVaultPdfFile(id = '', user = {}) {
  const entry = await resolveKnowledgeBaseVaultEntryById(id, user);
  const pdfFile = safeRepoFile(entry.pdfPath);

  if (!fileExists(pdfFile)) {
    const error = new Error('KNOWLEDGE_BASE_PDF_NOT_FOUND');
    error.statusCode = 404;
    throw error;
  }

  return {
    entry,
    absolutePath: pdfFile,
    filename: `${entry.id}.pdf`,
  };
}

/**
 * @function resolveKnowledgeBaseVaultJsonFile
 * @description Resolves one saved machine-readable Knowledge Base JSON companion without regenerating artifacts.
 * @param {string} id Artifact id.
 * @param {object} user Authenticated user or admin context.
 * @returns {Promise<object>} Saved JSON file payload.
 * @collaboration Knowledge Base Vault JSON action, manifest jsonPath, proof sidecar JSON SHA3, and future AI retrieval.
 */
export async function resolveKnowledgeBaseVaultJsonFile(id = '', user = {}) {
  const entry = await resolveKnowledgeBaseVaultEntryById(id, user);

  if (!entry.jsonPath) {
    const error = new Error('KNOWLEDGE_BASE_JSON_NOT_FOUND');
    error.statusCode = 404;
    throw error;
  }

  const jsonFile = safeRepoFile(entry.jsonPath);

  if (!fileExists(jsonFile)) {
    const error = new Error('KNOWLEDGE_BASE_JSON_NOT_FOUND');
    error.statusCode = 404;
    throw error;
  }

  return {
    entry,
    absolutePath: jsonFile,
    filename: `${entry.id}.json`,
  };
}
