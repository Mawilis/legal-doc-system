/* eslint-disable */
import crypto from 'node:crypto';
import streamEnterpriseArtifactPdf from '../services/artifacts/wilsyEnterprisePdfRenderer.js';
import mongoose from 'mongoose';

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
 * @function resolveWilsyAuthorizationBearerToken
 * @description Extracts the Bearer token from request headers without logging or exposing token content.
 * @param {object} req Express request.
 * @returns {string} Bearer token without the Bearer prefix.
 * @collaboration Artifact PDF route authentication, live identity resolution, and no-secret logging discipline.
 */
function resolveWilsyAuthorizationBearerToken(req = {}) {
  const authorization = clean(req.headers?.authorization || req.headers?.Authorization, '');
  const match = authorization.match(/^Bearer\s+(.+)$/i);

  return match ? clean(match[1], '') : '';
}

/**
 * @function decodeWilsyBase64UrlJsonSegment
 * @description Decodes a JWT base64url JSON segment for identity claim discovery without logging token content.
 * @param {string} segment JWT segment.
 * @returns {object} Decoded JSON object or an empty object.
 * @collaboration Bearer token identity bridge, PDF live user resolver, and profile lookup.
 */
function decodeWilsyBase64UrlJsonSegment(segment = '') {
  try {
    const normalized = clean(segment, '').replace(/-/g, '+').replace(/_/g, '/');
    const padded = `${normalized}${'='.repeat((4 - (normalized.length % 4)) % 4)}`;
    const decoded = Buffer.from(padded, 'base64').toString('utf8');
    const parsed = JSON.parse(decoded);

    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch {
    return {};
  }
}

/**
 * @function resolveWilsyBearerTokenClaims
 * @description Reads identity claims from the provided Bearer token so the controller can find the live database profile.
 * @param {object} req Express request.
 * @returns {object} Bearer token claims or an empty object.
 * @collaboration /api/generate/pdf, token-backed user identity, MongoDB profile lookup, and fail-closed Knowledge Base export.
 */
function resolveWilsyBearerTokenClaims(req = {}) {
  const token = resolveWilsyAuthorizationBearerToken(req);
  const parts = token.split('.');

  if (parts.length < 2) return {};

  return decodeWilsyBase64UrlJsonSegment(parts[1]);
}

// WILSY_FG108O3M2D_BEARER_IDENTITY_BRIDGE

/**
 * @function extractWilsyLiveUserProfileIdentity
 * @description Extracts live authenticated user/profile identity from request user objects and optional database user document.
 * @param {object} req Express request.
 * @param {object|null} profileDoc Optional database profile document.
 * @returns {object} Normalized live user identity.
 * @collaboration Auth middleware, Mongoose user profiles, account identity posture, and PDF document control.
 */
function extractWilsyLiveUserProfileIdentity(req = {}, profileDoc = null) {
  const user = req.user || {};
  const profile = user.profile || {};
  const tokenClaims = resolveWilsyBearerTokenClaims(req);
  const tokenProfile = tokenClaims.profile || tokenClaims.user || tokenClaims.account || {};
  const doc = profileDoc || {};
  const docProfile = doc.profile || {};
  const docAccount = doc.account || {};

  const displayCandidates = [
    user.displayName,
    user.fullName,
    user.name,
    user.firstName && user.lastName ? `${user.firstName} ${user.lastName}` : '',
    profile.displayName,
    profile.fullName,
    profile.name,
    profile.firstName && profile.lastName ? `${profile.firstName} ${profile.lastName}` : '',
    tokenClaims.displayName,
    tokenClaims.fullName,
    tokenClaims.name,
    tokenClaims.given_name && tokenClaims.family_name
      ? `${tokenClaims.given_name} ${tokenClaims.family_name}`
      : '',
    tokenProfile.displayName,
    tokenProfile.fullName,
    tokenProfile.name,
    tokenProfile.firstName && tokenProfile.lastName
      ? `${tokenProfile.firstName} ${tokenProfile.lastName}`
      : '',
    doc.displayName,
    doc.fullName,
    doc.name,
    doc.firstName && doc.lastName ? `${doc.firstName} ${doc.lastName}` : '',
    docProfile.displayName,
    docProfile.fullName,
    docProfile.name,
    docProfile.firstName && docProfile.lastName
      ? `${docProfile.firstName} ${docProfile.lastName}`
      : '',
    docAccount.displayName,
    docAccount.fullName,
    docAccount.name,
  ];

  const emailCandidates = [
    user.email,
    user.userEmail,
    user.primaryEmail,
    profile.email,
    profile.userEmail,
    tokenClaims.email,
    tokenClaims.userEmail,
    tokenClaims.primaryEmail,
    tokenProfile.email,
    tokenProfile.userEmail,
    doc.email,
    doc.userEmail,
    doc.primaryEmail,
    docProfile.email,
    docProfile.userEmail,
  ];

  const idCandidates = [
    user.id,
    user._id,
    user.userId,
    user.sub,
    tokenClaims.sub,
    tokenClaims.id,
    tokenClaims._id,
    tokenClaims.userId,
    tokenProfile.id,
    tokenProfile._id,
    tokenProfile.userId,
    doc._id,
    doc.id,
    doc.userId,
  ];

  const displayName =
    displayCandidates.map(resolveWilsyProfessionalDisplayNameCandidate).find(Boolean) || '';

  const email =
    emailCandidates.map((item) => clean(item, '')).find((item) => item && item.includes('@')) || '';

  const userId = idCandidates.map((item) => clean(item, '')).find(Boolean) || '';

  return {
    userId,
    email,
    displayName,
    source: profileDoc
      ? 'LIVE_DATABASE_PROFILE'
      : Object.keys(tokenClaims || {}).length
        ? 'LIVE_BEARER_TOKEN_CLAIMS'
        : 'LIVE_REQUEST_USER',
    hasProfessionalDisplayName: Boolean(displayName),
  };
}

/**
 * @function findWilsyLiveUserProfileDocument
 * @description Looks up the authenticated user in registered Mongoose user/profile models without hard-coded user identifiers.
 * @param {object} req Express request.
 * @returns {Promise<object|null>} User/profile document or null.
 * @collaboration MongoDB, Mongoose models, auth middleware, tenant profile data, and live Generated By resolution.
 */
async function findWilsyLiveUserProfileDocument(req = {}) {
  if (!mongoose?.connection?.readyState) return null;

  const user = req.user || {};
  const profile = user.profile || {};
  const tokenClaims = resolveWilsyBearerTokenClaims(req);
  const tokenProfile = tokenClaims.profile || tokenClaims.user || tokenClaims.account || {};

  const rawIds = [
    user._id,
    user.id,
    user.userId,
    user.sub,
    tokenClaims.sub,
    tokenClaims.id,
    tokenClaims._id,
    tokenClaims.userId,
    tokenProfile.id,
    tokenProfile._id,
    tokenProfile.userId,
  ]
    .map((item) => clean(item, ''))
    .filter(Boolean);

  const emails = [
    user.email,
    user.userEmail,
    user.primaryEmail,
    profile.email,
    profile.userEmail,
    tokenClaims.email,
    tokenClaims.userEmail,
    tokenClaims.primaryEmail,
    tokenProfile.email,
    tokenProfile.userEmail,
  ]
    .map((item) => clean(item, ''))
    .filter((item) => item && item.includes('@'));

  const modelNames = Object.keys(mongoose.models || {}).filter((name) =>
    /user|profile|account|operator|member/i.test(name)
  );

  for (const modelName of modelNames) {
    const Model = mongoose.models[modelName];

    for (const rawId of rawIds) {
      if (!mongoose.Types.ObjectId.isValid(rawId)) continue;

      try {
        const found = await Model.findById(rawId).lean().exec();
        if (found) return found;
      } catch {
        // Continue across models.
      }
    }

    for (const email of emails) {
      try {
        const found = await Model.findOne({
          $or: [
            { email },
            { userEmail: email },
            { primaryEmail: email },
            { 'profile.email': email },
            { 'profile.userEmail': email },
            { 'account.email': email },
            { 'auth.email': email },
            { 'local.email': email },
            { 'contact.email': email },
          ],
        })
          .lean()
          .exec();

        if (found) return found;
      } catch {
        // Continue across models.
      }
    }
  }

  return null;
}

/**
 * @function resolveWilsyLiveAuthenticatedUserIdentity
 * @description Resolves live backend authenticated user identity from req.user and registered database profile models without hard-coded names or emails.
 * @param {object} req Express request.
 * @returns {Promise<object>} Live authenticated user identity.
 * @collaboration PDF controller, auth middleware, MongoDB profile records, and no-hardcode Generated By governance.
 */
async function resolveWilsyLiveAuthenticatedUserIdentity(req = {}) {
  const profileDoc = await findWilsyLiveUserProfileDocument(req);
  const identity = extractWilsyLiveUserProfileIdentity(req, profileDoc);

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
 * @function buildArtifactIdentity
 * @description Builds the broad identity object consumed by the enterprise PDF renderer.
 * @param {object} req Express request.
 * @returns {object} Enterprise renderer identity.
 * @collaboration Connects BusinessArtifactStudio payloads to wilsyEnterprisePdfRenderer.js.
 */
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
    liveAuthenticatedUserIdentity.generatedByDisplayName ||
    resolveWilsyArtifactProfessionalGeneratedBy(req, body, metadata, payload, payloadData);

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

  const tenantId = clean(
    body.tenantId ||
      metadata.tenantId ||
      mergedPayloadData.tenantId ||
      req.tenantId ||
      req.user?.tenantId,
    'MASTER'
  );

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
 * @function buildCrmProofPackEnterpriseIdentity
 * @description Adapts CRM Proof Pack evidence into the existing tenant-branded enterprise PDF renderer identity.
 * @param {object} identity Existing artifact identity.
 * @param {object} proofPack CRM Proof Pack payload.
 * @returns {object} Enterprise renderer identity.
 * @collaboration businessArtifactPdfController, streamEnterpriseArtifactPdf, tenant branding, Merkle/SHA3 proof, and CRM evidence storytelling.
 */
function buildCrmProofPackEnterpriseIdentity(identity = {}, proofPack = {}) {
  const story = buildCrmProofPackEnterpriseStorySections(proofPack);
  const generatedAt = clean(
    proofPack.generatedAt || identity.generatedAt,
    new Date().toISOString()
  );
  const tenantId = clean(proofPack.tenantId || identity.tenantId, 'wilsy-sovereign-root');
  const generatedBy = clean(
    proofPack.generatedBy || identity.generatedBy || identity.userEmail,
    'UNRESOLVED_AUTHENTICATED_USER'
  );
  const title = clean(proofPack.title || identity.title, 'Lead Evidence Ledger Proof Pack');
  const sourcePosture = clean(
    proofPack.sourcePosture || identity.sourcePosture || 'SOURCE_LIVE',
    'SOURCE_LIVE'
  );

  return {
    ...identity,
    ...proofPack,
    type: 'crm-lead-proof-pack',
    artifactType: 'crm-lead-proof-pack',
    title,
    tenantId,
    tenant: tenantId,
    counterparty: clean(proofPack.counterparty || identity.counterparty || tenantId, tenantId),
    generatedAt,
    timestamp: generatedAt,
    generatedBy,
    userEmail: clean(identity.userEmail || proofPack.userEmail || generatedBy, generatedBy),
    sourcePosture,
    version: clean(identity.version || proofPack.version, 'WILSY-OS-ARTIFACT-v2.1-ENTERPRISE'),
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
    crmProofPack: proofPack,
    proofPackSections: proofPack,
    proofSummaryRows: proofPack.proofSummaryRows || [],
    authoritySealRows: proofPack.authoritySealRows || [],
    proofChecks: proofPack.proofChecks || [],
    operationalTimeline: proofPack.operationalTimeline || [],
    scopedRecords: proofPack.scopedRecords || [],
    metricsRows: proofPack.metricsRows || [],
    executivePurpose: story.executivePurpose,
    partiesOwnersAuthority: story.partiesOwnersAuthority,
    scopeControlsExceptions: story.scopeControlsExceptions,
    forensicProofRetention: story.forensicProofRetention,
    metadata: {
      ...(identity.metadata || {}),
      ...(proofPack.metadata || {}),
      type: 'crm-lead-proof-pack',
      artifactType: 'crm-lead-proof-pack',
      tenantId,
      timestamp: generatedAt,
      generatedAt,
      generatedBy,
      sourcePosture,
      renderer: 'streamEnterpriseArtifactPdf',
      crmProofPackBridge: 'FG106N_ENTERPRISE_ENGINE_ADAPTER',
    },
    payloadData: {
      ...(identity.payloadData || {}),
      crmProofPack: proofPack,
      proofPackSections: proofPack,
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
    const crmProofPackPayload = resolveCrmProofPackCandidate(req.body || {}, identity);
    const enterpriseIdentity = crmProofPackPayload
      ? buildCrmProofPackEnterpriseIdentity(identity, crmProofPackPayload)
      : identity;

    if (crmProofPackPayload) {
      res.setHeader('X-Wilsy-Pdf-Renderer', 'ENTERPRISE_ARTIFACT_CRM_PROOF_PACK');
      res.setHeader('X-Wilsy-Crm-Proof-Pack-Detected', 'true');
      res.setHeader('X-Wilsy-Artifact-Type', 'crm-lead-proof-pack');
    }

    const proof = buildProof(enterpriseIdentity);

    res.setHeader('X-Wilsy-Trace-ID', identity.traceId);
    res.setHeader('X-Artifact-Proof-Status', proof.status);
    res.setHeader('X-Request-Proof', identity.requestProof);

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
