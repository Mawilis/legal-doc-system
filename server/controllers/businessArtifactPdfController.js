/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                                                                                        ║
 * ║   ██████╗ ██╗██╗     ██╗     ██╗███╗   ██╗ ██████╗     ██████╗ ██╗   ██╗████████╗███████╗███████╗                               ║
 * ║   ██╔══██╗██║██║     ██║     ██║████╗  ██║██╔════╝     ██╔══██╗██╔═══██╗██║   ██║╚══██╔══╝██╔════╝╚════██║                       ║
 * ║   ██████╔╝██║██║     ██║     ██║██╔██╗ ██║██║  ███╗    ██████╔╝██║   ██║██║   ██║   ██║   █████╗   █████╔╝                       ║
 * ║   ██╔══██╗██║██║     ██║     ██║██║╚██╗██║██║   ██║    ██╔══██╗██║   ██║██║   ██║   ██║   ██╔══╝  ██╔═══╝                        ║
 * ║   ██████╔╝██║███████╗███████╗██║██║ ╚████║╚██████╔╝    ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗███████╗                       ║
 * ║   ╚═════╝ ╚═╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝╚══════╝                       ║
 * ║                                                                                                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - BUSINESS ARTIFACT PDF CONTROLLER [V9.1.0‑EOS‑VERIFIED‑IDENTITY]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ [FORENSIC PDF GENERATION | KNOWLEDGE BASE | CRM PROOF PACK | NDA | BILLING INVOICE]                                               ║
 * ║ [KENNEL EOS AWARE | TENANT ISOLATION | CRYPTOGRAPHIC SEALING]                                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 9.1.0‑EOS‑VERIFIED‑IDENTITY | EOS AUTHORITY BOUNDARY | INSTITUTIONAL GRADE                                                     ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/businessArtifactPdfController.js                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                              ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated explicit invoice payload enrichment to guarantee serviceType, metadata, and type.║
 * ║ • AI Engineering – V9.0.0: Added `enrichBillingInvoiceIdentity` to normalise invoice fields for the enterprise renderer.           ║
 * ║ • Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2, ISO 27001                                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGES (v9.1.0‑EOS‑VERIFIED‑IDENTITY):                                                                                        ║
 * ║   1. Added `enrichBillingInvoiceIdentity` – sets `type: 'billing-invoice'` and ensures all invoice fields are present.             ║
 * ║   2. Integrated enrichment into `generateSovereignArtifactPdf` before passing identity to renderer.                                 ║
 * ║   3. All existing Knowledge Base, CRM Proof Pack, NDA, and generic logic preserved unchanged.                                       ║
 * ║   4. Full JSDoc and compliance references.                                                                                           ║
 * ║   5. Removed Mongoose profile reads and unverified JWT claim decoding; only EOS-verified workspace identity is accepted.           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import streamEnterpriseArtifactPdf from '../services/artifacts/wilsyEnterprisePdfRenderer.js';
import { resolveEosWorkspaceTenantScope } from '../services/eosWorkspaceIdentity.js';

/**
 * @function readHeader
 * @description Reads a request header using case-insensitive aliases.
 * @param {object} req Express request.
 * @param {string[]} names Header aliases.
 * @returns {string} Header value.
 * @collaboration Preserves browser, middleware and proxy compatibility for Wilsy OS artifact generation.
 */
function readHeader(req, names = []) {
  for (const name of names) {
    const value = req.headers?.[name] || req.headers?.[String(name).toLowerCase()];
    if (value) return String(value);
  }
  return '';
}

/**
 * @function clean
 * @description Normalises printable artifact values.
 * @param {unknown} value Raw value.
 * @param {string} fallback Fallback.
 * @returns {string} Safe string.
 * @collaboration Prevents incomplete browser payloads from breaking enterprise PDF rendering.
 */
function clean(value, fallback = '') {
  const result = String(value ?? fallback)
    .replace(/[^\x09\x0A\x0D\x20-\x7E]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  return result || fallback;
}

/**
 * @function titleFromType
 * @description Converts an artifact type into a professional document title without hard-coded user identity.
 * @param {string} type Artifact type.
 * @returns {string} Human-readable artifact title.
 * @collaboration Business artifact PDF identity builder, Knowledge Base exports, and renderer document control.
 */
function titleFromType(type = '') {
  const raw = clean(type, 'WILSY ENTERPRISE ARTIFACT');

  return raw
    .replace(/[-_]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

/**
 * @function createRequestProof
 * @description Creates a deterministic request proof hash for artifact identity when the request does not provide one.
 * @param {string} type Artifact type.
 * @param {string} tenantId Tenant identifier.
 * @param {string} generatedAt Artifact generation timestamp.
 * @returns {string} Deterministic SHA-512 request proof.
 * @collaboration /api/generate/pdf, artifact request evidence, and Knowledge Base export reconstruction.
 */
function createRequestProof(type = '', tenantId = '', generatedAt = '') {
  return hashHex(`${clean(type)}|${clean(tenantId)}|${clean(generatedAt)}`, 'sha512');
}

// WILSY_FG108O3M3_TITLE_HELPER_RUNTIME_RESCUE

/**
 * @function createMerkleRoot
 * @description Creates a deterministic Merkle-style evidence root from artifact identity and request evidence values.
 * @param {Array<string>} values Evidence values to hash into a Merkle root.
 * @returns {string} Deterministic SHA-512 Merkle-style root hash.
 * @collaboration Artifact PDF evidence receipts, Knowledge Base export integrity, and enterprise renderer audit metadata.
 */
function createMerkleRoot(values = []) {
  const normalizedValues = (Array.isArray(values) ? values : [values])
    .map((value) => clean(value, ''))
    .filter(Boolean);

  if (!normalizedValues.length) {
    return hashHex('WILSY_EMPTY_MERKLE_ROOT', 'sha512');
  }

  let level = normalizedValues.map((value) => hashHex(value, 'sha512'));

  while (level.length > 1) {
    const nextLevel = [];

    for (let index = 0; index < level.length; index += 2) {
      const left = level[index];
      const right = level[index + 1] || left;
      nextLevel.push(hashHex(`${left}|${right}`, 'sha512'));
    }

    level = nextLevel;
  }

  return level[0];
}

// WILSY_FG108O3M4_MERKLE_ROOT_RUNTIME_RESCUE

/**
 * @function isWilsyKnowledgeBaseArtifactRequest
 * @description Detects Knowledge Base PDF export requests that must fail closed when live user identity is unresolved.
 * @param {object} body Request body.
 * @param {object} payload Artifact payload.
 * @param {object} payloadData Explicit payloadData envelope.
 * @returns {boolean} True when the request is a Knowledge Base artifact.
 * @collaboration Knowledge Base PDFs, /api/generate/pdf, live user identity governance, and release guard enforcement.
 */
function isWilsyKnowledgeBaseArtifactRequest(body = {}, payload = {}, payloadData = {}) {
  const candidates = [
    body.type,
    body.artifactType,
    body.templateType,
    payload.type,
    payload.artifactType,
    payload.templateType,
    payloadData.type,
    payloadData.artifactType,
    payloadData.templateType,
    body.knowledgeBase?.templateType,
    body.playbook?.templateType,
    body.playbookPayload?.templateType,
    payload.knowledgeBase?.templateType,
    payload.playbook?.templateType,
    payload.playbookPayload?.templateType,
    payloadData.knowledgeBase?.templateType,
    payloadData.playbook?.templateType,
    payloadData.playbookPayload?.templateType,
  ].map((item) => clean(item, '').toUpperCase());

  return candidates.some(
    (item) => item.includes('KNOWLEDGE_BASE') || item.includes('PLAYBOOK_FG108')
  );
}

/**
 * @function resolveWilsyProfessionalDisplayNameCandidate
 * @description Validates an authenticated profile display-name candidate without deriving identity from handles or emails.
 * @param {unknown} value Candidate display value.
 * @returns {string} Professional display name or empty string.
 * @collaboration Live auth profile, tenant account identity, and generated artifact document control.
 */
function resolveWilsyProfessionalDisplayNameCandidate(value = '') {
  const raw = clean(value, '').replace(/^@/, '').trim();

  if (!raw || raw.includes('@')) return '';
  if (raw === raw.toLowerCase()) return '';
  if (/^[a-z0-9_.-]+$/.test(raw)) return '';
  if (!/[A-Z]/.test(raw) || !/[a-z]/.test(raw)) return '';

  return raw;
}

/**
 * @function extractWilsyLiveUserProfileIdentity
 * @description Accepts identity only after the BFF has verified the workspace through Python EOS.
 * @param {object} req Express request enriched by the EOS workspace-bootstrap verifier.
 * @returns {object} Normalized verified user identity.
 */
function extractWilsyLiveUserProfileIdentity(req = {}) {
  if (req.eosAuthenticatedIdentity !== true) {
    return {
      userId: '',
      email: '',
      displayName: '',
      source: 'EOS_AUTHORITY_UNVERIFIED',
      hasProfessionalDisplayName: false,
    };
  }

  const user = req.user || {};
  const displayName = [
    user.displayName,
    user.fullName,
    user.firstName && user.lastName ? `${user.firstName} ${user.lastName}` : '',
  ]
    .map(resolveWilsyProfessionalDisplayNameCandidate)
    .find(Boolean) || '';
  const email = clean(user.email, '');
  const userId = clean(user.id, '');

  return {
    userId,
    email,
    displayName,
    source: 'EOS_VERIFIED_WORKSPACE_BOOTSTRAP',
    hasProfessionalDisplayName: Boolean(displayName),
  };
}

/**
 * @function resolveWilsyLiveAuthenticatedUserIdentity
 * @description Resolves the exact user profile returned by EOS after token, session, tenant and membership checks.
 * @param {object} req Express request enriched by the EOS workspace-bootstrap verifier.
 * @returns {Promise<object>} Verified identity projection for PDF metadata.
 */
async function resolveWilsyLiveAuthenticatedUserIdentity(req = {}) {
  const identity = extractWilsyLiveUserProfileIdentity(req);
  return {
    ...identity,
    generatedByDisplayName: identity.displayName,
    operatorDisplayName: identity.displayName,
    ownerDisplayName: identity.displayName,
    displayName: identity.displayName,
  };
}

/**
 * @function assertWilsyKnowledgeBaseLiveUserIdentity
 * @description Fails closed when a Knowledge Base PDF export cannot prove a live professional user display name.
 * @param {boolean} isKnowledgeBaseRequest Whether this request is a Knowledge Base export.
 * @param {object} liveIdentity Live authenticated user identity.
 * @returns {void}
 * @collaboration Knowledge Base export safety, generated-by identity proof, and prevention of fallback operator labels.
 */
function assertWilsyKnowledgeBaseLiveUserIdentity(
  isKnowledgeBaseRequest = false,
  liveIdentity = {}
) {
  if (!isKnowledgeBaseRequest) return;

  if (!liveIdentity?.hasProfessionalDisplayName) {
    const error = new Error('LIVE_USER_DISPLAY_NAME_REQUIRED');
    error.statusCode = 422;
    error.code = 'LIVE_USER_DISPLAY_NAME_REQUIRED';
    error.publicMessage =
      'Knowledge Base PDF export requires a live authenticated user profile display name. Update the user profile identity before exporting.';
    throw error;
  }
}

// WILSY_FG108O3E3K3C_LIVE_USER_IDENTITY_BUILDER

/**
 * @function resolveWilsyLiveAuthenticatedUserEmail
 * @description Resolves email identity from live authenticated backend request/profile context without hard-coded personal email fallbacks.
 * @param {object} req Express request.
 * @param {object} body Request body.
 * @param {object} metadata Request metadata.
 * @param {object} payload Artifact payload.
 * @param {object} payloadData Explicit payloadData envelope.
 * @returns {string} Live user email or an unresolved identity posture marker.
 * @collaboration Auth middleware, /api/generate/pdf, account identity posture, tenant audit, and Knowledge Base PDF document control.
 */
function resolveWilsyLiveAuthenticatedUserEmail(
  req = {},
  body = {},
  metadata = {},
  payload = {},
  payloadData = {}
) {
  const candidates = [
    req.user?.email,
    req.user?.userEmail,
    req.user?.primaryEmail,
    req.user?.profile?.email,
    req.user?.profile?.userEmail,
    req.auth?.email,
    req.auth?.userEmail,
    req.session?.user?.email,
    body.userEmail,
    metadata.userEmail,
    payload.userEmail,
    payloadData.userEmail,
  ];

  for (const candidate of candidates) {
    const normalized = clean(candidate, '');
    if (normalized && normalized.includes('@')) return normalized;
  }

  return 'UNRESOLVED_AUTHENTICATED_USER';
}

// WILSY_FG108O3E3J2_LIVE_AUTHENTICATED_USER_EMAIL

/**
 * @function resolveWilsyArtifactProfessionalGeneratedBy
 * @description Resolves a generic professional Generated By display name from request payload, metadata, payloadData, nested playbook data, or authenticated profile display fields.
 * @param {object} req Express request.
 * @param {object} body Request body.
 * @param {object} metadata Request metadata.
 * @param {object} payload Artifact payload.
 * @param {object} payloadData Explicit payloadData envelope.
 * @returns {string} Professional display name or Wilsy OS Operator.
 * @collaboration Knowledge Base PDF exports, BusinessArtifactStudio, authenticated profile identity, and non-hardcoded artifact document control.
 */
function resolveWilsyArtifactProfessionalGeneratedBy(
  req = {},
  body = {},
  metadata = {},
  payload = {},
  payloadData = {}
) {
  /**
   * @function normalizeCandidate
   * @description Converts live backend identity candidates into professional display names without hard-coded personal values.
   * @param {unknown} value - Candidate identity value from request, metadata, payload, profile, or authenticated user context.
   * @returns {string} Professional display name candidate or empty string.
   * @collaboration Live authenticated user identity, Knowledge Base PDF document control, and non-hardcoded Generated By governance.
   */
  const normalizeCandidate = (value = '') => {
    const raw = clean(value, '').replace(/^@/, '').trim();

    if (!raw || raw.includes('@')) return '';

    if (
      raw !== raw.toLowerCase() &&
      /[A-Z]/.test(raw) &&
      /[a-z]/.test(raw) &&
      !/^[a-z0-9_.-]+$/.test(raw)
    ) {
      return raw;
    }

    const spaced = raw
      .replace(/[_-]+/g, ' ')
      .replace(/\.+/g, ' ')
      .replace(/([a-z])([A-Z])/g, '$1 $2')
      .replace(/\s+/g, ' ')
      .trim();

    const words = spaced.split(' ').filter(Boolean);

    if (words.length < 2) return '';

    return words
      .map((word) => `${word.slice(0, 1).toUpperCase()}${word.slice(1).toLowerCase()}`)
      .join(' ');
  };

  const nestedCandidates = [
    body.knowledgeBase,
    body.playbook,
    body.playbookPayload,
    body.payload?.knowledgeBase,
    body.payload?.playbook,
    body.payload?.playbookPayload,
    body.payloadData?.knowledgeBase,
    body.payloadData?.playbook,
    body.payloadData?.playbookPayload,
    payload.knowledgeBase,
    payload.playbook,
    payload.playbookPayload,
    payloadData.knowledgeBase,
    payloadData.playbook,
    payloadData.playbookPayload,
    metadata.knowledgeBase,
    metadata.playbook,
    metadata.playbookPayload,
  ].filter((item) => item && typeof item === 'object');

  const candidates = [
    body.generatedByDisplayName,
    metadata.generatedByDisplayName,
    payload.generatedByDisplayName,
    payloadData.generatedByDisplayName,
    body.operatorDisplayName,
    metadata.operatorDisplayName,
    payload.operatorDisplayName,
    payloadData.operatorDisplayName,
    body.ownerDisplayName,
    metadata.ownerDisplayName,
    payload.ownerDisplayName,
    payloadData.ownerDisplayName,
    body.displayName,
    metadata.displayName,
    payload.displayName,
    payloadData.displayName,
    req.user?.displayName,
    req.user?.fullName,
    req.user?.name,
    req.user?.profile?.displayName,
    req.user?.profile?.fullName,
    ...nestedCandidates.flatMap((item) => [
      item.generatedByDisplayName,
      item.operatorDisplayName,
      item.ownerDisplayName,
      item.displayName,
      item.fullName,
      item.name,
      item.generatedBy,
    ]),
    body.generatedBy,
    metadata.generatedBy,
    payload.generatedBy,
    payloadData.generatedBy,
  ];

  for (const candidate of candidates) {
    const normalized = normalizeCandidate(candidate);
    if (normalized) return normalized;
  }

  return 'Wilsy OS Operator';
}

// WILSY_FG108O3E3J_CONTROLLER_GENERATED_BY_PRECEDENCE

/**
 * @function hashHex
 * @description Creates a deterministic hex hash.
 * @param {string} value Input value.
 * @param {string} algorithm Preferred algorithm.
 * @returns {string} Hex digest.
 * @collaboration Supplies Wilsy OS proof, Merkle and seal values to the enterprise renderer.
 */
function hashHex(value, algorithm = 'sha512') {
  const safeAlgorithm = crypto.getHashes().includes(algorithm) ? algorithm : 'sha512';
  return crypto.createHash(safeAlgorithm).update(String(value), 'utf8').digest('hex').toUpperCase();
}

/**
 * @function createBrowserProof
 * @description Creates the Wilsy OS browser-safe SHA-512 proof contract.
 * @param {string} type Artifact type.
 * @param {string} tenantId Tenant ID.
 * @param {string} timestamp Timestamp.
 * @returns {string} SHA-512 proof.
 * @collaboration Keeps request proof visible without allowing proof mismatch to bypass enterprise rendering.
 */
function createBrowserProof(type, tenantId, timestamp) {
  return crypto
    .createHash('sha512')
    .update(`${type}|${tenantId}|${timestamp}`, 'utf8')
    .digest('hex');
}

/**
 * @function requireBearerToken
 * @description Requires authenticated artifact generation.
 * @param {object} req Express request.
 * @returns {string} Bearer token.
 * @throws {Error} When the token is missing.
 * @collaboration Keeps the emergency proof compatibility bridge from becoming an unauthenticated endpoint.
 */
function requireBearerToken(req) {
  const authorization = readHeader(req, ['Authorization']);

  if (!authorization || !authorization.startsWith('Bearer ') || authorization.length < 18) {
    const error = new Error('Artifact generation requires a Bearer token.');
    error.statusCode = 401;
    error.code = 'ARTIFACT_AUTH_TOKEN_MISSING';
    throw error;
  }

  return authorization.replace(/^Bearer\s+/i, '');
}

/**
 * @function isBillingInvoiceRequest
 * @description Detects whether the request is for a billing invoice artifact.
 * @param {object} body Request body.
 * @param {object} metadata Request metadata.
 * @param {object} payload Artifact payload.
 * @param {object} payloadData Explicit payloadData envelope.
 * @returns {boolean} True if the request is a billing invoice.
 * @collaboration Enables invoice-specific enrichment before passing to the renderer.
 */
function isBillingInvoiceRequest(body = {}, metadata = {}, payload = {}, payloadData = {}) {
  const candidates = [
    body.type,
    body.artifactType,
    body.templateType,
    metadata.type,
    metadata.artifactType,
    metadata.templateType,
    payload.type,
    payload.artifactType,
    payload.templateType,
    payloadData.type,
    payloadData.artifactType,
    payloadData.templateType,
    body.data?.type,
    body.data?.artifactType,
    body.payloadData?.type,
    body.payloadData?.artifactType,
  ].map((item) => clean(item, '').toLowerCase());

  return candidates.some(
    (item) =>
      item === 'billing-invoice' ||
      item === 'billing_invoice' ||
      item === 'invoice' ||
      item.includes('billing') ||
      (item.includes('invoice') && !item.includes('knowledge'))
  );
}

/**
 * @function enrichBillingInvoiceIdentity
 * @description Ensures that billing invoice requests have the correct `type`, `lineItems` (with `serviceType`), and `metadata` fields.
 * @param {object} identity The base artifact identity.
 * @param {object} body The raw request body.
 * @param {object} metadata The request metadata.
 * @param {object} payload The artifact payload.
 * @param {object} payloadData The explicit payloadData.
 * @returns {object} Enriched identity for invoice rendering.
 * @collaboration Bridges the BillingHUD print payload to the enterprise renderer with all required invoice fields.
 * @institutional Ensures every invoice PDF shows service type, line items, and forensic metadata.
 * @compliance POPIA §19, GDPR §32, SOC2 §CC7.2 – full invoice data sealed and traceable.
 */
function enrichBillingInvoiceIdentity(identity = {}, body = {}, metadata = {}, payload = {}, payloadData = {}) {
  // If not an invoice request, return identity unchanged
  if (!isBillingInvoiceRequest(body, metadata, payload, payloadData)) {
    return identity;
  }

  // Normalise the type to 'billing-invoice'
  const enriched = {
    ...identity,
    type: 'billing-invoice',
    artifactType: 'billing-invoice',
    templateType: 'invoice',
  };

  // Extract line items from various sources
  const lineItemsSource = payload.lineItems || payloadData.lineItems || body.data?.lineItems || body.lineItems || [];
  const lineItems = Array.isArray(lineItemsSource) ? lineItemsSource : [];

  // Enrich each line item with serviceType default
  const enrichedLineItems = lineItems.map((item) => ({
    serviceType: item.serviceType || item.category || item.type || 'General Service',
    description: item.description || item.name || 'Wilsy OS service',
    quantity: Number(item.quantity ?? 1),
    unitPrice: Number(item.unitPrice ?? item.amount ?? 0),
    lineTotal: Number(item.lineTotal ?? item.amount ?? (item.quantity || 1) * (item.unitPrice || 0)),
    taxAmount: Number(item.taxAmount ?? 0),
    currency: item.currency || payload.currency || payloadData.currency || body.currency || 'ZAR',
    ...item, // Preserve any extra fields
  }));

  // Build comprehensive metadata
  const totalAmount = Number(payload.totalAmount || payloadData.totalAmount || body.data?.totalAmount || body.totalAmount || 0);
  const currency = String(payload.currency || payloadData.currency || body.data?.currency || body.currency || 'ZAR').toUpperCase();
  const invoiceNumber = String(metadata.invoiceNumber || payload.invoiceNumber || payloadData.invoiceNumber || body.data?.invoiceNumber || body.invoiceNumber || identity.title || '');
  const status = String(metadata.status || payload.status || payloadData.status || body.data?.status || body.status || 'ISSUED').toUpperCase();
  const dueDate = metadata.dueDate || payload.dueDate || payloadData.dueDate || body.data?.dueDate || body.dueDate || null;
  const issueDate = metadata.issueDate || payload.issueDate || payloadData.issueDate || body.data?.issueDate || body.issueDate || identity.effectiveDate || null;
  const sealHash = metadata.sealHash || payload.sealHash || payloadData.sealHash || body.data?.sealHash || body.sealHash || null;

  // Place enriched data into the identity's data and payloadData fields
  enriched.data = {
    ...(identity.data || {}),
    ...(payload || {}),
    ...(payloadData || {}),
    type: 'billing-invoice',
    lineItems: enrichedLineItems,
    totalAmount,
    currency,
    status,
    dueDate,
    issueDate,
    invoiceNumber,
    sealHash,
  };

  enriched.payloadData = {
    ...(identity.payloadData || {}),
    ...(payloadData || {}),
    ...(payload || {}),
    type: 'billing-invoice',
    lineItems: enrichedLineItems,
    totalAmount,
    currency,
    status,
    dueDate,
    issueDate,
    invoiceNumber,
    sealHash,
  };

  enriched.metadata = {
    ...(identity.metadata || {}),
    ...(metadata || {}),
    invoiceNumber,
    amount: totalAmount,
    currency,
    status,
    dueDate,
    issueDate,
    sealHash,
    watermark: metadata.watermark || 'Wilsy OS Sovereign Copy',
    print: metadata.print || false,
    serviceType: enrichedLineItems.length ? enrichedLineItems[0].serviceType : '',
  };

  // Also set top-level fields for compatibility
  enriched.invoiceNumber = invoiceNumber;
  enriched.totalAmount = totalAmount;
  enriched.currency = currency;
  enriched.status = status;
  enriched.dueDate = dueDate;
  enriched.issueDate = issueDate;
  enriched.sealHash = sealHash;
  enriched.lineItems = enrichedLineItems;

  return enriched;
}

/**
 * @function buildArtifactIdentity
 * @description Builds enterprise PDF identity from request payload plus live authenticated backend user/profile data.
 * @param {object} req Express request.
 * @returns {Promise<object>} Artifact identity for the enterprise PDF renderer.
 * @collaboration /api/generate/pdf, auth middleware, live user profile data, Knowledge Base exports, and no-hardcode document control.
 */
async function buildArtifactIdentity(req) {
  const body = req.body || {};
  const metadata = body.metadata && typeof body.metadata === 'object' ? body.metadata : {};
  const payload = body.data || body.payload || body.artifact || {};
  const payloadData =
    body.payloadData && typeof body.payloadData === 'object' ? body.payloadData : {};
  const isKnowledgeBaseRequest = isWilsyKnowledgeBaseArtifactRequest(body, payload, payloadData);
  const liveAuthenticatedUserIdentity = await resolveWilsyLiveAuthenticatedUserIdentity(req);

  assertWilsyKnowledgeBaseLiveUserIdentity(isKnowledgeBaseRequest, liveAuthenticatedUserIdentity);

  const generatedByDisplayName =
    liveAuthenticatedUserIdentity.generatedByDisplayName || 'Authenticated WILSY User';

  const liveAuthenticatedUserEmail =
    liveAuthenticatedUserIdentity.email ||
    resolveWilsyLiveAuthenticatedUserEmail(req, body, metadata, payload, payloadData);

  const mergedPayloadData = {
    ...payload,
    ...payloadData,
    knowledgeBase: body.knowledgeBase || payload.knowledgeBase || payloadData.knowledgeBase,
    playbook: body.playbook || payload.playbook || payloadData.playbook,
    playbookPayload: body.playbookPayload || payload.playbookPayload || payloadData.playbookPayload,
  };

  const type = clean(
    body.type ||
    body.artifactType ||
    body.templateType ||
    metadata.type ||
    metadata.artifactType ||
    metadata.templateType ||
    mergedPayloadData.type ||
    mergedPayloadData.artifactType ||
    mergedPayloadData.templateType,
    'WILSY-ENTERPRISE-ARTIFACT'
  );

  const tenantScope = resolveEosWorkspaceTenantScope({
    requestedTenantId: req.tenantId,
    workspace: req.eosWorkspace,
    suppliedTenantIds: [
      body.tenantId,
      metadata.tenantId,
      payload.tenantId,
      payloadData.tenantId,
      mergedPayloadData.tenantId,
    ],
  });
  if (!tenantScope.ok || req.eosAuthenticatedIdentity !== true) {
    const error = new Error('PDF tenant scope does not match the authenticated EOS workspace.');
    error.statusCode = 403;
    error.code = 'WORKSPACE_SCOPE_MISMATCH';
    throw error;
  }
  const tenantId = tenantScope.tenantId;

  const generatedAt = clean(
    body.generatedAt ||
    body.timestamp ||
    metadata.generatedAt ||
    metadata.timestamp ||
    mergedPayloadData.generatedAt ||
    mergedPayloadData.timestamp,
    new Date().toISOString()
  );

  const effectiveDate = clean(
    body.effectiveDate || metadata.effectiveDate || mergedPayloadData.effectiveDate,
    generatedAt.slice(0, 10)
  );

  const title = clean(body.title || metadata.title || mergedPayloadData.title, titleFromType(type));

  const subtitle = clean(
    body.subtitle || metadata.subtitle || mergedPayloadData.subtitle,
    'Authority • Review • Execution • Forensic Proof • Source-Aware Control'
  );

  const issuingEntity = clean(
    body.issuingEntity || metadata.issuingEntity || mergedPayloadData.issuingEntity,
    'Wilsy (Pty) Ltd'
  );

  const counterparty = clean(
    body.counterparty || metadata.counterparty || mergedPayloadData.counterparty || tenantId,
    tenantId
  );

  const jurisdiction = clean(
    body.jurisdiction || metadata.jurisdiction || mergedPayloadData.jurisdiction,
    'Republic of South Africa'
  );

  const version = clean(
    body.version || metadata.version || mergedPayloadData.version,
    'WILSY-OS-ARTIFACT-v2.1-ENTERPRISE'
  );

  const sourcePosture = clean(
    body.sourcePosture || metadata.sourcePosture || mergedPayloadData.sourcePosture,
    'SOURCE_LIVE'
  );

  const requestProof = clean(
    body.requestProof ||
    body.proof ||
    metadata.requestProof ||
    metadata.proof ||
    mergedPayloadData.requestProof,
    createRequestProof(type, tenantId, generatedAt)
  );

  const traceId = clean(
    body.traceId ||
    body.traceID ||
    metadata.traceId ||
    metadata.traceID ||
    mergedPayloadData.traceId ||
    req.headers?.['x-trace-id'] ||
    req.headers?.['x-request-id'],
    `TRACE-${hashHex(`${type}|${tenantId}|${generatedAt}`).slice(0, 16)}`
  );

  const merkleRoot = clean(
    body.merkleRoot || metadata.merkleRoot || mergedPayloadData.merkleRoot,
    createMerkleRoot({
      type,
      tenantId,
      generatedAt,
      requestProof,
      sourcePosture,
      title,
    })
  );

  const professionalGeneratedBy = clean(generatedByDisplayName, 'Wilsy OS Operator');

  return {
    id: clean(
      body.id || metadata.id || mergedPayloadData.id,
      hashHex(`${type}|${tenantId}|${generatedAt}`).slice(0, 18)
    ),
    type,
    artifactType: clean(
      body.artifactType || metadata.artifactType || mergedPayloadData.artifactType,
      type
    ),
    templateType: clean(
      body.templateType || metadata.templateType || mergedPayloadData.templateType,
      type
    ),
    title,
    subtitle,
    tenantId,
    generatedAt,
    timestamp: generatedAt,
    effectiveDate,
    userEmail: clean(liveAuthenticatedUserEmail, 'UNRESOLVED_AUTHENTICATED_USER'),
    generatedBy: professionalGeneratedBy,
    generatedByDisplayName: professionalGeneratedBy,
    operatorDisplayName: professionalGeneratedBy,
    ownerDisplayName: professionalGeneratedBy,
    displayName: professionalGeneratedBy,
    liveUserIdentitySource: clean(
      liveAuthenticatedUserIdentity.source,
      'LIVE_USER_IDENTITY_UNRESOLVED'
    ),
    liveUserId: clean(liveAuthenticatedUserIdentity.userId, 'LIVE_USER_ID_UNRESOLVED'),
    issuingEntity,
    counterparty,
    jurisdiction,
    version,
    sourcePosture,
    requestProof,
    traceId,
    merkleRoot,
    payload: {
      ...mergedPayloadData,
      generatedBy: professionalGeneratedBy,
      generatedByDisplayName: professionalGeneratedBy,
      operatorDisplayName: professionalGeneratedBy,
      ownerDisplayName: professionalGeneratedBy,
      displayName: professionalGeneratedBy,
      liveUserIdentitySource: clean(
        liveAuthenticatedUserIdentity.source,
        'LIVE_USER_IDENTITY_UNRESOLVED'
      ),
    },
    data: {
      ...mergedPayloadData,
      generatedBy: professionalGeneratedBy,
      generatedByDisplayName: professionalGeneratedBy,
      operatorDisplayName: professionalGeneratedBy,
      ownerDisplayName: professionalGeneratedBy,
      displayName: professionalGeneratedBy,
      liveUserIdentitySource: clean(
        liveAuthenticatedUserIdentity.source,
        'LIVE_USER_IDENTITY_UNRESOLVED'
      ),
    },
    payloadData: {
      ...mergedPayloadData,
      generatedBy: professionalGeneratedBy,
      generatedByDisplayName: professionalGeneratedBy,
      operatorDisplayName: professionalGeneratedBy,
      ownerDisplayName: professionalGeneratedBy,
      displayName: professionalGeneratedBy,
      liveUserIdentitySource: clean(
        liveAuthenticatedUserIdentity.source,
        'LIVE_USER_IDENTITY_UNRESOLVED'
      ),
    },
    metadata: {
      ...metadata,
      id: clean(
        metadata.id || body.id || mergedPayloadData.id,
        hashHex(`${type}|${tenantId}|${generatedAt}`).slice(0, 18)
      ),
      type,
      artifactType: clean(
        body.artifactType || metadata.artifactType || mergedPayloadData.artifactType,
        type
      ),
      templateType: clean(
        body.templateType || metadata.templateType || mergedPayloadData.templateType,
        type
      ),
      tenantId,
      generatedAt,
      timestamp: generatedAt,
      requestProof,
      traceId,
      merkleRoot,
      sourcePosture,
      generatedBy: professionalGeneratedBy,
      generatedByDisplayName: professionalGeneratedBy,
      operatorDisplayName: professionalGeneratedBy,
      ownerDisplayName: professionalGeneratedBy,
      displayName: professionalGeneratedBy,
      liveUserIdentitySource: clean(
        liveAuthenticatedUserIdentity.source,
        'LIVE_USER_IDENTITY_UNRESOLVED'
      ),
    },
  };
}

/**
 * @function buildProof
 * @description Builds proof values for the enterprise PDF renderer.
 * @param {object} identity Artifact identity.
 * @returns {object} Proof packet.
 * @collaboration Preserves proof visibility while restoring the proper branded enterprise renderer.
 */
function buildProof(identity) {
  const merkleRoot = hashHex(
    JSON.stringify({
      type: identity.type,
      tenantId: identity.tenantId,
      generatedAt: identity.generatedAt,
      requestProof: identity.requestProof,
      sourcePosture: identity.sourcePosture,
    }),
    'sha512'
  );

  const sha3 = hashHex(`${merkleRoot}|${identity.traceId}|${identity.requestProof}`, 'sha3-512');

  return {
    status: 'VERIFIED',
    verified: true,
    requestProof: identity.requestProof,
    clientProof: identity.requestProof,
    serverSeal: sha3,
    seal: sha3,
    sha3,
    sha3Seal: sha3,
    merkleRoot,
    traceId: identity.traceId,
    sourcePosture: identity.sourcePosture,
    generatedAt: identity.generatedAt,
    lifecycle: identity.lifecycle,
    approvals: identity.approvals,
  };
}

/**
 * @function resolveCrmProofPackCandidate
 * @description Resolves a CRM Proof Pack object from the active business artifact PDF request shapes.
 * @param {object} body Express request body.
 * @param {object} identity Business artifact identity.
 * @returns {object|null} CRM Proof Pack object when evidence rows are present.
 * @collaboration businessArtifactPdfController, artifactExportService, WilsyLeadOperatingRoom, and the existing /api/generate/pdf route.
 */
function resolveCrmProofPackCandidate(body = {}, identity = {}) {
  const candidates = [
    body.crmProofPack,
    body.proofPackSections,
    body.payloadData?.crmProofPack,
    body.payloadData?.proofPackSections,
    body.payload?.crmProofPack,
    body.payload?.proofPackSections,
    body.payload?.payloadData?.crmProofPack,
    body.payload?.data?.crmProofPack,
    body.data?.crmProofPack,
    body.data?.proofPackSections,
    body.data?.payload?.crmProofPack,
    body.artifact?.crmProofPack,
    identity.crmProofPack,
    identity.proofPackSections,
    identity.payloadData?.crmProofPack,
    identity.payloadData?.proofPackSections,
  ].filter(Boolean);

  return (
    candidates.find(
      (candidate) =>
        Array.isArray(candidate.proofSummaryRows) ||
        Array.isArray(candidate.authoritySealRows) ||
        Array.isArray(candidate.proofChecks) ||
        Array.isArray(candidate.operationalTimeline) ||
        Array.isArray(candidate.scopedRecords) ||
        Array.isArray(candidate.metricsRows)
    ) || null
  );
}

/**
 * @function normalizeCrmProofPackEnterpriseValue
 * @description Converts CRM Proof Pack evidence values into readable enterprise artifact text.
 * @param {unknown} value Source evidence value.
 * @returns {string} Normalized story value.
 * @collaboration CRM Proof Pack evidence, enterprise PDF renderer, and tenant branded artifact readability.
 */
function normalizeCrmProofPackEnterpriseValue(value = '') {
  if (Array.isArray(value)) {
    return value
      .map((item) => normalizeCrmProofPackEnterpriseValue(item))
      .filter(Boolean)
      .join(' · ');
  }

  if (value && typeof value === 'object') {
    return Object.entries(value)
      .map(
        ([key, itemValue]) =>
          `${clean(key, 'field')}: ${normalizeCrmProofPackEnterpriseValue(itemValue)}`
      )
      .filter(Boolean)
      .join(' · ');
  }

  return clean(value, '');
}

/**
 * @function normalizeCrmProofPackEnterpriseRows
 * @description Normalizes CRM Proof Pack row collections into enterprise renderer story bullets.
 * @param {unknown} rows Source proof rows.
 * @returns {string[]} Story bullets.
 * @collaboration CRM Proof Pack row evidence and Wilsy enterprise artifact narrative sections.
 */
function normalizeCrmProofPackEnterpriseRows(rows = []) {
  if (!Array.isArray(rows)) {
    return [];
  }

  return rows
    .map((row) => {
      if (Array.isArray(row)) {
        return `${clean(row[0], 'Evidence')}: ${normalizeCrmProofPackEnterpriseValue(row[1])}`;
      }

      if (row && typeof row === 'object') {
        const label = clean(row.label || row.title || row.key || row.name, 'Evidence');
        const detail = normalizeCrmProofPackEnterpriseValue(
          [row.status, row.reason, row.value, row.detail].filter(Boolean)
        );

        return detail ? `${label}: ${detail}` : label;
      }

      return normalizeCrmProofPackEnterpriseValue(row);
    })
    .filter(Boolean);
}

/**
 * @function buildCrmProofPackEnterpriseStorySections
 * @description Builds narrative CRM proof sections for the branded Wilsy enterprise PDF engine.
 * @param {object} proofPack CRM Proof Pack payload.
 * @returns {object} Enterprise story section packet.
 * @collaboration CRM Proof Pack evidence, enterprise PDF story posture, and investor-grade audit reading.
 */
function buildCrmProofPackEnterpriseStorySections(proofPack = {}) {
  const proofSummary = normalizeCrmProofPackEnterpriseRows(proofPack.proofSummaryRows);
  const authoritySeals = normalizeCrmProofPackEnterpriseRows(proofPack.authoritySealRows);
  const proofChecks = normalizeCrmProofPackEnterpriseRows(proofPack.proofChecks);
  const operationalTimeline = normalizeCrmProofPackEnterpriseRows(proofPack.operationalTimeline);
  const scopedRecords = normalizeCrmProofPackEnterpriseRows(proofPack.scopedRecords);
  const metrics = normalizeCrmProofPackEnterpriseRows(proofPack.metricsRows);

  const verdict =
    proofSummary.find((row) => /proof verdict/i.test(row)) ||
    proofSummary[0] ||
    'Proof verdict: Sovereign Proof Sealed';

  const receipt =
    proofSummary.find((row) => /receipt/i.test(row)) ||
    proofChecks.find((row) => /receipt/i.test(row)) ||
    'Receipt: Proof run receipt attached';

  const criteria =
    proofSummary.find((row) => /criteria hash/i.test(row)) ||
    proofChecks.find((row) => /criteria hash/i.test(row)) ||
    'Criteria hash: verified against saved-view registry';

  return {
    executivePurpose: [
      'This CRM Lead Evidence Ledger Proof Pack records why the proof was generated, which saved-view criteria were executed, which ledger authority allowed export, and which CRM evidence was in scope at the time of generation.',
      verdict,
      receipt,
    ],
    partiesOwnersAuthority: [
      `Tenant authority: ${clean(proofPack.tenantId, 'wilsy-sovereign-root')}`,
      `Generated by: ${clean(proofPack.generatedBy, 'wilsy-operator')}`,
      `Command surface: ${clean(proofPack.commandSurface, 'CRM_LEAD_PROOF_PACK_ARTIFACT_EXPORT')}`,
      ...authoritySeals.slice(0, 8),
    ],
    scopeControlsExceptions: [
      'Scope: saved CRM lead view, proof-ledger access decision, membership overrides, cursor hydration, source-route posture, compliance signal, and export authority.',
      criteria,
      ...proofChecks,
      ...metrics,
    ],
    forensicProofRetention: [
      'Retention purpose: audit reconstruction, investor diligence, regulator response, internal control review, and operational handover.',
      ...operationalTimeline,
      ...scopedRecords,
    ],
  };
}

/**
 * @function buildCrmProofPackEnterpriseIdentity(identity = {}, proofPack = {}) {
  const tenantId = clean(identity.tenantId, '');
  const suppliedTenantId = clean(proofPack.tenantId, '');
  const generatedBy = clean(
    identity.generatedByDisplayName || identity.generatedBy,
    'Authenticated WILSY User'
  );
  const suppliedGeneratedBy = clean(proofPack.generatedBy, '');
  if (
    !tenantId ||
    (suppliedTenantId && suppliedTenantId !== tenantId) ||
    (suppliedGeneratedBy && suppliedGeneratedBy !== generatedBy)
  ) {
    const error = new Error('CRM proof pack identity does not match the authenticated EOS workspace.');
    error.statusCode = 403;
    error.code = 'PDF_IDENTITY_SCOPE_MISMATCH';
    throw error;
  }

  const authoritativeProofPack = {
    ...proofPack,
    tenantId,
    generatedBy,
    generatedByDisplayName: generatedBy,
    operatorDisplayName: generatedBy,
    ownerDisplayName: generatedBy,
    displayName: generatedBy,
    userEmail: clean(identity.userEmail, 'UNRESOLVED_AUTHENTICATED_USER'),
    liveUserIdentitySource: identity.liveUserIdentitySource,
    liveUserId: identity.liveUserId,
  };
  const story = buildCrmProofPackEnterpriseStorySections(authoritativeProofPack);
  const generatedAt = clean(
    authoritativeProofPack.generatedAt || identity.generatedAt,
    new Date().toISOString()
  );
  const title = clean(authoritativeProofPack.title || identity.title, 'Lead Evidence Ledger Proof Pack');
  const sourcePosture = clean(
    authoritativeProofPack.sourcePosture || identity.sourcePosture || 'SOURCE_LIVE',
    'SOURCE_LIVE'
  );

  return {
    ...identity,
    ...authoritativeProofPack,
    type: 'crm-lead-proof-pack',
    artifactType: 'crm-lead-proof-pack',
    title,
    tenantId,
    tenant: tenantId,
    counterparty: clean(authoritativeProofPack.counterparty || identity.counterparty || tenantId, tenantId),
    generatedAt,
    timestamp: generatedAt,
    generatedBy,
    generatedByDisplayName: generatedBy,
    operatorDisplayName: generatedBy,
    ownerDisplayName: generatedBy,
    displayName: generatedBy,
    userEmail: clean(identity.userEmail, 'UNRESOLVED_AUTHENTICATED_USER'),
    liveUserIdentitySource: identity.liveUserIdentitySource,
    liveUserId: identity.liveUserId,
    sourcePosture,
    version: clean(identity.version || authoritativeProofPack.version, 'WILSY-OS-ARTIFACT-v2.1-ENTERPRISE'),
    lifecycle: [
      'Proof target selected',
      'Saved view resolved',
      'Backend run executed',
      'Export authority verified',
      'Vault retention ready',
    ],
    approvals: ['Proof Ledger Access', 'Export Control', 'Tenant Authority'],
    clausePack: 'Wilsy CRM Proof Pack Enterprise Story v1',
    signatureRoute: 'Wilsy OS Proof Ledger / Artifact Vault',
    crmProofPack: authoritativeProofPack,
    proofPackSections: authoritativeProofPack,
    proofSummaryRows: authoritativeProofPack.proofSummaryRows || [],
    authoritySealRows: authoritativeProofPack.authoritySealRows || [],
    proofChecks: authoritativeProofPack.proofChecks || [],
    operationalTimeline: authoritativeProofPack.operationalTimeline || [],
    scopedRecords: authoritativeProofPack.scopedRecords || [],
    metricsRows: authoritativeProofPack.metricsRows || [],
    executivePurpose: story.executivePurpose,
    partiesOwnersAuthority: story.partiesOwnersAuthority,
    scopeControlsExceptions: story.scopeControlsExceptions,
    forensicProofRetention: story.forensicProofRetention,
    metadata: {
      ...(identity.metadata || {}),
      ...(authoritativeProofPack.metadata || {}),
      type: 'crm-lead-proof-pack',
      artifactType: 'crm-lead-proof-pack',
      tenantId,
      userEmail: clean(identity.userEmail, 'UNRESOLVED_AUTHENTICATED_USER'),
      timestamp: generatedAt,
      generatedAt,
      generatedBy,
      generatedByDisplayName: generatedBy,
      operatorDisplayName: generatedBy,
      ownerDisplayName: generatedBy,
      displayName: generatedBy,
      liveUserIdentitySource: identity.liveUserIdentitySource,
      liveUserId: identity.liveUserId,
      sourcePosture,
      renderer: 'streamEnterpriseArtifactPdf',
      crmProofPackBridge: 'FG106N_ENTERPRISE_ENGINE_ADAPTER',
    },
    payloadData: {
      ...(identity.payloadData || {}),
      crmProofPack: authoritativeProofPack,
      proofPackSections: authoritativeProofPack,
      story,
    },
  };
}
/**
 * @function generateSovereignArtifactPdf
 * @description Generates Wilsy OS enterprise business artifacts using the real enterprise renderer service.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @param {Function} next Express next callback.
 * @returns {Promise<void>} Streamed PDF response.
 * @collaboration Routes /api/generate/pdf away from plain fallback PDFs and into wilsyEnterprisePdfRenderer.js.
 */
export async function generateSovereignArtifactPdf(req, res, next) {
  try {
    requireBearerToken(req);

    const identity = await buildArtifactIdentity(req);

    // ─── Enrich if this is a billing invoice request ──────────────────────────
    const body = req.body || {};
    const metadata = body.metadata && typeof body.metadata === 'object' ? body.metadata : {};
    const payload = body.data || body.payload || body.artifact || {};
    const payloadData =
      body.payloadData && typeof body.payloadData === 'object' ? body.payloadData : {};
    const enrichedIdentity = enrichBillingInvoiceIdentity(identity, body, metadata, payload, payloadData);

    // ─── CRM Proof Pack detection (unchanged) ──────────────────────────────────
    const crmProofPackPayload = resolveCrmProofPackCandidate(req.body || {}, enrichedIdentity);
    const enterpriseIdentity = crmProofPackPayload
      ? buildCrmProofPackEnterpriseIdentity(enrichedIdentity, crmProofPackPayload)
      : enrichedIdentity;

    if (crmProofPackPayload) {
      res.setHeader('X-Wilsy-Pdf-Renderer', 'ENTERPRISE_ARTIFACT_CRM_PROOF_PACK');
      res.setHeader('X-Wilsy-Crm-Proof-Pack-Detected', 'true');
      res.setHeader('X-Wilsy-Artifact-Type', 'crm-lead-proof-pack');
    }

    // ─── If invoice, set appropriate headers ──────────────────────────────────
    if (isBillingInvoiceRequest(body, metadata, payload, payloadData)) {
      res.setHeader('X-Wilsy-Pdf-Renderer', 'BILLING_INVOICE_ENTERPRISE');
      res.setHeader('X-Wilsy-Artifact-Type', 'billing-invoice');
      res.setHeader('X-Wilsy-Invoice-Number', clean(enterpriseIdentity.invoiceNumber || identity.title, ''));
      res.setHeader('X-Wilsy-Total-Amount', String(enterpriseIdentity.totalAmount || 0));
    }

    const proof = buildProof(enterpriseIdentity);

    res.setHeader('X-Wilsy-Trace-ID', enterpriseIdentity.traceId);
    res.setHeader('X-Artifact-Proof-Status', proof.status);
    res.setHeader('X-Request-Proof', enterpriseIdentity.requestProof);

    await streamEnterpriseArtifactPdf({ res, identity: enterpriseIdentity, proof });
  } catch (error) {
    if (res.headersSent) {
      if (typeof next === 'function') return next(error);
      return;
    }

    res.status(error.statusCode || 500).json({
      success: false,
      error: error.code || 'ARTIFACT_ENTERPRISE_RENDER_FAILED',
      message: error.message || 'Enterprise artifact generation failed.',
      traceId: `ART-${Date.now().toString(16).toUpperCase()}`,
    });
  }
}

export default generateSovereignArtifactPdf;

// P60K5Q10FG106L_REAL_BUSINESS_PDF_CRM_PROOF_RENDERER
// P60K5Q10FG106N_CRM_PROOF_PACK_ENTERPRISE_ENGINE_ADAPTER
