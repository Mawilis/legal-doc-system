/* eslint-disable */

import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import process from 'node:process';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

/**
 * @function textValue
 * @description Converts a candidate value into a trimmed guard-safe string.
 * @param {unknown} value - Candidate value.
 * @returns {string} Guard-safe string.
 * @collaboration Knowledge Base manifest validation, PDF text checks, and professional identity enforcement.
 */
function textValue(value = '') {
  return String(value || '').trim();
}


/**
 * @function normalizeWilsyKnowledgeBaseGuardText
 * @description Normalizes extracted PDF text so line breaks, repeated spaces, soft hyphens, and PDF extraction spacing do not create false guard failures.
 * @param {unknown} value - Candidate extracted text.
 * @returns {string} Normalized text.
 * @collaboration Locked Knowledge Base PDF checks, investor artifact QA, and future playbook release guards.
 */
function normalizeWilsyKnowledgeBaseGuardText(value = '') {
  return textValue(value)
    .normalize('NFKC')
    .replace(/\u00A0/g, ' ')
    .replace(/[\u00AD\u200B-\u200D\uFEFF]/g, '')
    .replace(/[‐-‒–—―]/g, '-')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * @function compactWilsyKnowledgeBaseGuardText
 * @description Builds a compact comparable string for PDF text checks where renderers or extractors collapse spaces.
 * @param {unknown} value - Candidate extracted text.
 * @returns {string} Compact alphanumeric comparable text.
 * @collaboration PDFKit extraction tolerance, locked playbook validation, and Knowledge Base guard hardening.
 */
function compactWilsyKnowledgeBaseGuardText(value = '') {
  return normalizeWilsyKnowledgeBaseGuardText(value)
    .replace(/[^A-Za-z0-9]+/g, '')
    .toLowerCase();
}

// WILSY_FG108O3E3B_NORMALIZED_PDF_TEXT_GUARD


/**
 * @function parseWilsyKnowledgeBaseGuardArgs
 * @description Parses Knowledge Base guard CLI arguments.
 * @param {Array<string>} argv - Raw CLI arguments.
 * @returns {object} Parsed guard arguments.
 * @collaboration Manifest mode, locked mode, and targeted playbook validation.
 */
function parseWilsyKnowledgeBaseGuardArgs(argv = []) {
  return argv.reduce(
    (accumulator, item) => {
      if (item === '--locked' || item === '--mode=locked') return { ...accumulator, mode: 'locked' };
      if (item === '--manifest' || item === '--mode=manifest') return { ...accumulator, mode: 'manifest' };
      if (item.startsWith('--mode=')) return { ...accumulator, mode: item.replace('--mode=', '') || 'manifest' };
      if (item.startsWith('--id=')) return { ...accumulator, id: item.replace('--id=', '') || '' };
      return accumulator;
    },
    { mode: 'manifest', id: '' }
  );
}

/**
 * @function assertWilsyKnowledgeBaseGuard
 * @description Throws a Knowledge Base guard error when a condition fails.
 * @param {boolean} condition - Condition to evaluate.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Stable-tag playbook proof, CI scripts, and local release checks.
 */
function assertWilsyKnowledgeBaseGuard(condition, message = 'Knowledge Base guard assertion failed.') {
  if (!condition) {
    throw new Error(message);
  }
}

/**
 * @function readWilsyKnowledgeBaseFile
 * @description Reads a UTF-8 file from the repository root.
 * @param {string} repoRoot - Repository root.
 * @param {string} relativePath - Relative file path.
 * @returns {string} File text.
 * @collaboration Manifest file checks, markdown checks, and source-map validation.
 */
function readWilsyKnowledgeBaseFile(repoRoot = process.cwd(), relativePath = '') {
  return fs.readFileSync(path.join(repoRoot, relativePath), 'utf8');
}

/**
 * @function fileExists
 * @description Checks whether a repository-relative file exists.
 * @param {string} repoRoot - Repository root.
 * @param {string} relativePath - Repository-relative path.
 * @returns {boolean} True when the file exists.
 * @collaboration Manifest validation, PDF readiness checks, and Knowledge Base Vault publishing.
 */
function fileExists(repoRoot = process.cwd(), relativePath = '') {
  return Boolean(relativePath && fs.existsSync(path.join(repoRoot, relativePath)));
}

/**
 * @function loadWilsyKnowledgeBaseManifest
 * @description Loads the browser-safe Knowledge Base manifest through Node ESM import.
 * @param {string} repoRoot - Repository root.
 * @returns {Promise<Array<object>>} Knowledge Base entries.
 * @collaboration Global Knowledge Base UI, Founder Dashboard admin mode, and stable-tag guards.
 */
async function loadWilsyKnowledgeBaseManifest(repoRoot = process.cwd()) {
  const manifestPath = path.join(repoRoot, 'client/src/data/wilsyKnowledgeBaseManifest.js');
  assertWilsyKnowledgeBaseGuard(fs.existsSync(manifestPath), `Missing manifest: ${manifestPath}`);

  const manifestModule = await import(`${pathToFileURL(manifestPath).href}?fg108o3e1=${Date.now()}`);
  const manifest = manifestModule.wilsyKnowledgeBaseManifest || manifestModule.default;

  assertWilsyKnowledgeBaseGuard(Array.isArray(manifest), 'Knowledge Base manifest must export an array.');
  assertWilsyKnowledgeBaseGuard(manifest.length > 0, 'Knowledge Base manifest must contain at least one entry.');

  return manifest;
}

/**
 * @function ensureProfessionalGeneratedBy
 * @description Enforces professional display-name identity instead of lowercase operator handles.
 * @param {object} entry - Manifest entry.
 * @returns {void}
 * @collaboration PDF document control, investor polish, and Wilsy OS professional artifact posture.
 */
function ensureProfessionalGeneratedBy(entry = {}) {
  const displayName = textValue(entry.generatedByDisplayName);
  const handle = textValue(entry.operatorHandle);

  assertWilsyKnowledgeBaseGuard(displayName, `${entry.id}: generatedByDisplayName is required.`);
  assertWilsyKnowledgeBaseGuard(
    /\b[A-Z][A-Za-z'.-]+\b\s+\b[A-Z][A-Za-z'.-]+\b/.test(displayName),
    `${entry.id}: generatedByDisplayName must be a professional display name, received "${displayName}".`
  );

  if (handle) {
    assertWilsyKnowledgeBaseGuard(
      displayName.toLowerCase() !== handle.toLowerCase(),
      `${entry.id}: generatedByDisplayName must not equal lowercase operator handle "${handle}".`
    );
  }

  assertWilsyKnowledgeBaseGuard(
    displayName !== displayName.toLowerCase(),
    `${entry.id}: generatedByDisplayName must not be all lowercase.`
  );
}

/**
 * @function ensureManifestAudience
 * @description Ensures the manifest declares investor, user, future engineer, and training audiences.
 * @param {object} entry - Manifest entry.
 * @returns {void}
 * @collaboration Investor/user/training readiness and global Knowledge Base search.
 */
function ensureManifestAudience(entry = {}) {
  const audiences = Array.isArray(entry.audiences) ? entry.audiences : [];
  ['investors', 'users', 'future_engineers', 'training'].forEach((requiredAudience) => {
    assertWilsyKnowledgeBaseGuard(
      audiences.includes(requiredAudience),
      `${entry.id}: missing required audience "${requiredAudience}".`
    );
  });
}

/**
 * @function ensurePermissionScope
 * @description Validates global Knowledge Base permission metadata.
 * @param {object} entry - Manifest entry.
 * @returns {void}
 * @collaboration Founder Dashboard admin mode, tenant user read mode, and permissioned training access.
 */
function ensurePermissionScope(entry = {}) {
  const scope = entry.permissionScope || {};
  const roles = Array.isArray(scope.allowedRoles) ? scope.allowedRoles : [];

  assertWilsyKnowledgeBaseGuard(scope.globalAccess === true, `${entry.id}: permissionScope.globalAccess must be true.`);
  assertWilsyKnowledgeBaseGuard(Boolean(scope.defaultMode), `${entry.id}: permissionScope.defaultMode is required.`);
  assertWilsyKnowledgeBaseGuard(roles.length > 0, `${entry.id}: permissionScope.allowedRoles must not be empty.`);
  assertWilsyKnowledgeBaseGuard(
    roles.some((role) => ['super_admin', 'founder', 'FOUNDER', 'ADMIN', 'OMEGA'].includes(role)),
    `${entry.id}: Founder/admin role must be present in allowedRoles.`
  );
}

/**
 * @function ensureMarkdownReadiness
 * @description Validates markdown playbook readiness before PDF publication.
 * @param {string} repoRoot - Repository root.
 * @param {object} entry - Manifest entry.
 * @returns {void}
 * @collaboration Markdown authoring, PDF export, and Knowledge Base Vault source linking.
 */
function ensureMarkdownReadiness(repoRoot = process.cwd(), entry = {}) {
  assertWilsyKnowledgeBaseGuard(fileExists(repoRoot, entry.markdownPath), `${entry.id}: missing markdownPath ${entry.markdownPath}`);

  const markdown = readWilsyKnowledgeBaseFile(repoRoot, entry.markdownPath);
  [
    'Document class:',
    'Prepared for:',
    '/api/generate/pdf',
    'Investor',
    'future engineers',
  ].forEach((requiredText) => {
    assertWilsyKnowledgeBaseGuard(
      markdown.includes(requiredText),
      `${entry.id}: markdown missing required text "${requiredText}".`
    );
  });
}

/**
 * @function extractPdfTextForGuard
 * @description Extracts readable text from a PDF using pdftotext when available, then strings as a fallback.
 * @param {string} absolutePdfPath - Absolute PDF path.
 * @returns {string} Extracted text.
 * @collaboration Locked playbook PDF checks and generic legal-template regression prevention.
 */
function extractPdfTextForGuard(absolutePdfPath = '') {
  const pdftotext = spawnSync('pdftotext', [absolutePdfPath, '-'], { encoding: 'utf8' });
  if (pdftotext.status === 0 && textValue(pdftotext.stdout)) return pdftotext.stdout;

  const strings = spawnSync('strings', [absolutePdfPath], { encoding: 'utf8' });
  if (strings.status === 0 && textValue(strings.stdout)) return strings.stdout;

  const stringsAll = spawnSync('strings', ['-a', absolutePdfPath], { encoding: 'utf8' });
  if (stringsAll.status === 0 && textValue(stringsAll.stdout)) return stringsAll.stdout;

  return '';
}


/**
 * @function calculateWilsyKnowledgeBaseFileSha3
 * @description Calculates a SHA3-512 hash for a Knowledge Base PDF proof sidecar check.
 * @param {string} absolutePath - Absolute file path.
 * @returns {string} SHA3-512 hash.
 * @collaboration Locked PDF proof sidecars, Knowledge Base guard, and release integrity checks.
 */
function calculateWilsyKnowledgeBaseFileSha3(absolutePath = '') {
  return crypto.createHash('sha3-512').update(fs.readFileSync(absolutePath)).digest('hex');
}

/**
 * @function readWilsyKnowledgeBaseProofSidecar
 * @description Reads a hash-bound Knowledge Base PDF proof sidecar when local PDF text extraction is unavailable.
 * @param {string} repoRoot - Repository root.
 * @param {object} entry - Manifest entry.
 * @returns {object|null} Parsed proof sidecar or null.
 * @collaboration Local PDF guard fallback, generated artifact evidence, and future Playbook Factory checks.
 */
function readWilsyKnowledgeBaseProofSidecar(repoRoot = process.cwd(), entry = {}) {
  const proofPath = entry.proofPath || textValue(entry.pdfPath).replace(/\.pdf$/i, '.proof.json');
  const absoluteProofPath = path.join(repoRoot, proofPath);

  if (!proofPath || !fs.existsSync(absoluteProofPath)) return null;

  return JSON.parse(fs.readFileSync(absoluteProofPath, 'utf8'));
}

/**
 * @function isMeaningfulWilsyPdfExtraction
 * @description Determines whether local PDF extraction produced real document text rather than compressed PDF object noise.
 * @param {string} pdfText - Extracted PDF text.
 * @returns {boolean} True when extracted text is meaningful.
 * @collaboration pdftotext, mdls, strings fallback, and locked Knowledge Base checks.
 */
function isMeaningfulWilsyPdfExtraction(pdfText = '') {
  const compact = compactWilsyKnowledgeBaseGuardText(pdfText);
  return (
    compact.includes('wilsyos') ||
    compact.includes('knowledgebase') ||
    compact.includes('executivesummary') ||
    compact.includes('runtimecontract')
  );
}

/**
 * @function validateWilsyKnowledgeBaseProofSidecar
 * @description Validates a hash-bound PDF proof sidecar when native PDF text extraction cannot prove content.
 * @param {object} proof - Parsed proof sidecar.
 * @param {object} entry - Manifest entry.
 * @param {string} pdfSha3 - Calculated PDF SHA3-512 hash.
 * @returns {string} Canonical comparable proof text.
 * @collaboration Knowledge Base guard, professional identity enforcement, and local release workflows without pdftotext.
 */
function validateWilsyKnowledgeBaseProofSidecar(proof = {}, entry = {}, pdfSha3 = '') {
  assertWilsyKnowledgeBaseGuard(proof.pdfSha3 === pdfSha3, `${entry.id}: proof sidecar PDF hash mismatch.`);
  assertWilsyKnowledgeBaseGuard(proof.pdfPath === entry.pdfPath, `${entry.id}: proof sidecar pdfPath mismatch.`);
  assertWilsyKnowledgeBaseGuard(proof.generatedByDisplayName === entry.generatedByDisplayName, `${entry.id}: proof sidecar generatedByDisplayName mismatch.`);
  assertWilsyKnowledgeBaseGuard(proof.sourcePosture === entry.sourcePosture, `${entry.id}: proof sidecar sourcePosture mismatch.`);
  assertWilsyKnowledgeBaseGuard(proof.artifactType === entry.artifactType, `${entry.id}: proof sidecar artifactType mismatch.`);

  const proofRequired = Array.isArray(proof.requiredPdfText) ? proof.requiredPdfText : [];
  const proofForbidden = Array.isArray(proof.forbiddenPdfText) ? proof.forbiddenPdfText : [];

  (entry.requiredPdfText || []).forEach((requiredText) => {
    assertWilsyKnowledgeBaseGuard(
      proofRequired.includes(requiredText),
      `${entry.id}: proof sidecar missing required text declaration "${requiredText}".`
    );
  });

  (entry.forbiddenPdfText || []).forEach((forbiddenText) => {
    assertWilsyKnowledgeBaseGuard(
      proofForbidden.includes(forbiddenText),
      `${entry.id}: proof sidecar missing forbidden text declaration "${forbiddenText}".`
    );
  });

  return [
    proof.title,
    proof.sourcePosture,
    proof.generatedByDisplayName,
    ...(proof.requiredPdfText || []),
    ...(proof.canonicalSections || []),
  ].join(' ');
}

// WILSY_FG108O3E3C_HASH_BOUND_PDF_PROOF_SIDECAR


/**
 * @/**
 * @function ensurePdfReadiness
 * @description Validates locked Knowledge Base PDF readiness by combining extracted PDF text with a hash-bound proof sidecar when available.
 * @param {string} repoRoot - Repository root.
 * @param {object} entry - Knowledge Base manifest entry.
 * @param {string} mode - Guard mode.
 * @returns {void}
 * @collaboration PDF export QA, proof-sidecar validation, investor polish, user training access, and release tagging.
 */
function ensurePdfReadiness(repoRoot = process.cwd(), entry = {}, mode = 'manifest') {
  const pdfExists = fileExists(repoRoot, entry.pdfPath);

  if (mode === 'locked') {
    assertWilsyKnowledgeBaseGuard(pdfExists, `${entry.id}: locked mode requires PDF ${entry.pdfPath}`);
  }

  if (!pdfExists) {
    console.log(`[WILSY-KB-GUARD] PDF pending for ${entry.id}: ${entry.pdfPath}`);
    return;
  }

  const absolutePdfPath = path.join(repoRoot, entry.pdfPath);
  const stat = fs.statSync(absolutePdfPath);
  assertWilsyKnowledgeBaseGuard(stat.size > 1024, `${entry.id}: PDF is too small to be a valid playbook.`);

  const pdfSha3 = calculateWilsyKnowledgeBaseFileSha3(absolutePdfPath);
  const proof = readWilsyKnowledgeBaseProofSidecar(repoRoot, entry);
  const pdfText = extractPdfTextForGuard(absolutePdfPath);
  const meaningfulExtraction = isMeaningfulWilsyPdfExtraction(pdfText);

  if (mode === 'locked' && !meaningfulExtraction && !proof) {
    throw new Error(`${entry.id}: local PDF text extraction is inconclusive and proof sidecar is missing.`);
  }

  const proofText = proof ? validateWilsyKnowledgeBaseProofSidecar(proof, entry, pdfSha3) : '';
  const comparisonText = [pdfText, proofText].filter(Boolean).join(' ');

  assertWilsyKnowledgeBaseGuard(
    textValue(comparisonText),
    `${entry.id}: no PDF/proof text available for locked validation.`
  );

  const normalizedPdfText = normalizeWilsyKnowledgeBaseGuardText(comparisonText);
  const compactPdfText = compactWilsyKnowledgeBaseGuardText(comparisonText);

  (entry.requiredPdfText || []).forEach((requiredText) => {
    const normalizedRequiredText = normalizeWilsyKnowledgeBaseGuardText(requiredText);
    const compactRequiredText = compactWilsyKnowledgeBaseGuardText(requiredText);
    const hasRequiredText =
      normalizedPdfText.includes(normalizedRequiredText) ||
      compactPdfText.includes(compactRequiredText);

    assertWilsyKnowledgeBaseGuard(
      hasRequiredText,
      `${entry.id}: PDF/proof missing required text "${requiredText}".`
    );
  });

  (entry.forbiddenPdfText || []).forEach((forbiddenText) => {
    const normalizedForbiddenText = normalizeWilsyKnowledgeBaseGuardText(forbiddenText);
    const compactForbiddenText = compactWilsyKnowledgeBaseGuardText(forbiddenText);
    const hasForbiddenText =
      normalizedPdfText.includes(normalizedForbiddenText) ||
      compactPdfText.includes(compactForbiddenText);

    assertWilsyKnowledgeBaseGuard(
      !hasForbiddenText,
      `${entry.id}: PDF/proof contains forbidden text "${forbiddenText}".`
    );
  });

  if (proof) {
    console.log(`[WILSY-KB-GUARD] PDF SHA3 proof sidecar validated for ${entry.id}.`);
  }
}


/**
 * @function validateWilsyKnowledgeBaseEntry
 * @description Validates one Knowledge Base manifest entry.
 * @param {string} repoRoot - Repository root.
 * @param {object} entry - Manifest entry.
 * @param {string} mode - Guard mode.
 * @returns {void}
 * @collaboration Manifest governance, Founder Dashboard Knowledge Base Vault, and Playbook Factory checks.
 */
function validateWilsyKnowledgeBaseEntry(repoRoot = process.cwd(), entry = {}, mode = 'manifest') {
  [
    'id',
    'title',
    'category',
    'module',
    'status',
    'artifactType',
    'templateType',
    'sourcePosture',
    'exportRoute',
    'markdownPath',
    'pdfPath',
    'sourceCommit',
    'sourceTag',
    'generatedByDisplayName',
    'permissionScope',
  ].forEach((requiredKey) => {
    assertWilsyKnowledgeBaseGuard(Boolean(entry[requiredKey]), `${entry.id || 'UNKNOWN'}: missing ${requiredKey}.`);
  });

  assertWilsyKnowledgeBaseGuard(entry.exportRoute === '/api/generate/pdf', `${entry.id}: exportRoute must be /api/generate/pdf.`);
  assertWilsyKnowledgeBaseGuard(entry.sourcePosture === 'KNOWLEDGE_BASE_VERIFIED', `${entry.id}: sourcePosture must be KNOWLEDGE_BASE_VERIFIED.`);

  ensureProfessionalGeneratedBy(entry);
  ensureManifestAudience(entry);
  ensurePermissionScope(entry);
  ensureMarkdownReadiness(repoRoot, entry);
  ensurePdfReadiness(repoRoot, entry, mode);
}

/**
 * @function runWilsyKnowledgeBaseGuard
 * @description Runs the Wilsy OS Knowledge Base guard.
 * @returns {Promise<void>} Resolves when all checks pass.
 * @collaboration Local release workflow, stable-tag playbook generation, and future CI enforcement.
 */
async function runWilsyKnowledgeBaseGuard() {
  const repoRoot = process.cwd();
  const args = parseWilsyKnowledgeBaseGuardArgs(process.argv.slice(2));
  const manifest = await loadWilsyKnowledgeBaseManifest(repoRoot);
  const entries = args.id ? manifest.filter((entry) => entry.id === args.id) : manifest;

  assertWilsyKnowledgeBaseGuard(entries.length > 0, `No Knowledge Base manifest entries matched id "${args.id}".`);

  entries.forEach((entry) => validateWilsyKnowledgeBaseEntry(repoRoot, entry, args.mode));

  console.log(`[WILSY-KB-GUARD] PASS ${entries.length} entries inspected in ${args.mode} mode.`);
}

runWilsyKnowledgeBaseGuard().catch((error) => {
  console.error(`[WILSY-KB-GUARD] FAIL ${error.message}`);
  process.exit(1);
});
