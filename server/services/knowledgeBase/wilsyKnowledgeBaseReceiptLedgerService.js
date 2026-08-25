/* eslint-disable */
import KnowledgeBaseVaultReceipt from '../../models/knowledgeBaseVaultReceiptModel.js';

/**
 * @function normalizeKnowledgeBaseReceiptText
 * @description Normalizes receipt ledger text values without leaking backend enum language into the frontend display layer.
 * @param {*} value Source value.
 * @param {string} fallback Fallback value.
 * @returns {string} Normalized receipt text.
 * @collaboration Knowledge Base Vault receipt ledger, institutional evidence, and saved PDF/proof actions.
 */
function normalizeKnowledgeBaseReceiptText(value, fallback = '') {
  if (typeof value === 'string') return value.trim() || fallback;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return fallback;
}

/**
 * @function resolveKnowledgeBaseReceiptActor
 * @description Resolves tenant and operator identity from authenticated request context and institutional headers.
 * @param {object} req Express request.
 * @returns {object} Receipt actor identity.
 * @collaboration Tenant context, authenticated operator context, Knowledge Base Vault receipts, and institutional headers.
 */
function resolveKnowledgeBaseReceiptActor(req = {}) {
  const headers = req.headers || {};
  const body = req.body || {};
  const query = req.query || {};
  const user = req.user || req.authUser || {};

  const tenantId = normalizeKnowledgeBaseReceiptText(
    headers['x-tenant-id'] ||
      headers['x-wilsy-tenant-id'] ||
      body.tenantId ||
      body.institutionalHeaders?.tenantId ||
      body.strikePayload?.institutionalHeaders?.tenantId ||
      query.tenantId ||
      user.tenantId ||
      user.tenant?._id ||
      user.tenant?.id,
    'MASTER'
  );

  const operatorId = normalizeKnowledgeBaseReceiptText(
    headers['x-operator-id'] ||
      headers['x-user-id'] ||
      headers['x-wilsy-operator-id'] ||
      body.operatorId ||
      body.userId ||
      body.institutionalHeaders?.operatorId ||
      body.institutionalHeaders?.userId ||
      body.strikePayload?.institutionalHeaders?.operatorId ||
      body.strikePayload?.institutionalHeaders?.userId ||
      user.operatorId ||
      user.userId ||
      user._id ||
      user.id,
    'SYSTEM_OPERATOR'
  );

  return {
    tenantId,
    operatorId,
    userId: operatorId,
  };
}

/**
 * @function buildKnowledgeBaseReceiptInstitutionalHeaders
 * @description Builds the institutional receipt headers required at top level and inside strike payload evidence.
 * @param {object} req Express request.
 * @param {string} commandSurface Receipt command surface.
 * @returns {object} Institutional receipt headers.
 * @collaboration Knowledge Base Vault receipt ledger, command evidence, tenant context, and strike payload contract.
 */
function buildKnowledgeBaseReceiptInstitutionalHeaders(req = {}, commandSurface = 'knowledge_base_vault_receipt') {
  const actor = resolveKnowledgeBaseReceiptActor(req);
  const generatedAt = new Date().toISOString();

  return {
    tenantId: actor.tenantId,
    operatorId: actor.operatorId,
    userId: actor.userId,
    route: normalizeKnowledgeBaseReceiptText(req.originalUrl || req.url, '/api/knowledge-base/vault/receipts'),
    commandSurface,
    generatedAt,
  };
}

/**
 * @function normalizeKnowledgeBaseReceiptPayload
 * @description Converts a receipt request into the server-persisted Knowledge Base receipt ledger contract.
 * @param {object} req Express request.
 * @returns {object} Normalized receipt payload.
 * @collaboration Knowledge Base Vault frontend actions, saved PDF/proof routes, institutional headers, and strike payload evidence.
 */
function normalizeKnowledgeBaseReceiptPayload(req = {}) {
  const body = req.body || {};
  const receiptBody = body.receipt && typeof body.receipt === 'object' ? body.receipt : body;
  const actionType = normalizeKnowledgeBaseReceiptText(receiptBody.actionType || receiptBody.action || 'view', 'view').toLowerCase();
  const commandSurface = normalizeKnowledgeBaseReceiptText(
    receiptBody.commandSurface || body.commandSurface || `knowledge_base_vault_receipt_${actionType}`,
    `knowledge_base_vault_receipt_${actionType}`
  );
  const actor = resolveKnowledgeBaseReceiptActor(req);
  const institutionalHeaders = {
    ...buildKnowledgeBaseReceiptInstitutionalHeaders(req, commandSurface),
    ...(body.institutionalHeaders || {}),
    ...(receiptBody.institutionalHeaders || {}),
  };

  const strikePayload = {
    ...(body.strikePayload || {}),
    ...(receiptBody.strikePayload || {}),
    institutionalHeaders: {
      ...(body.strikePayload?.institutionalHeaders || {}),
      ...(receiptBody.strikePayload?.institutionalHeaders || {}),
      ...institutionalHeaders,
    },
  };

  return {
    tenantId: actor.tenantId,
    operatorId: actor.operatorId,
    userId: actor.userId,
    artifactId: normalizeKnowledgeBaseReceiptText(receiptBody.artifactId || receiptBody.entryId || receiptBody.id),
    artifactTitle: normalizeKnowledgeBaseReceiptText(receiptBody.artifactTitle || receiptBody.title),
    artifactCategory: normalizeKnowledgeBaseReceiptText(receiptBody.artifactCategory || receiptBody.category),
    actionType,
    actionLabel: normalizeKnowledgeBaseReceiptText(receiptBody.actionLabel || receiptBody.label || actionType),
    pdfSha3: normalizeKnowledgeBaseReceiptText(receiptBody.pdfSha3 || receiptBody.sha3 || receiptBody.digest),
    fingerprint: normalizeKnowledgeBaseReceiptText(receiptBody.fingerprint || receiptBody.pdfSha3 || receiptBody.sha3 || receiptBody.digest),
    pdfUrl: normalizeKnowledgeBaseReceiptText(receiptBody.pdfUrl || receiptBody.pdfOpenUrl || receiptBody.pdfDownloadUrl),
    proofUrl: normalizeKnowledgeBaseReceiptText(receiptBody.proofUrl || receiptBody.evidenceUrl),
    sourceTag: normalizeKnowledgeBaseReceiptText(receiptBody.sourceTag),
    sourceCommit: normalizeKnowledgeBaseReceiptText(receiptBody.sourceCommit),
    commandSurface,
    route: normalizeKnowledgeBaseReceiptText(institutionalHeaders.route, '/api/knowledge-base/vault/receipts'),
    generatedAt: receiptBody.generatedAt || institutionalHeaders.generatedAt,
    institutionalHeaders,
    strikePayload,
    metadata: {
      ...(receiptBody.metadata || {}),
      requestMethod: normalizeKnowledgeBaseReceiptText(req.method),
      requestIp: normalizeKnowledgeBaseReceiptText(req.ip || req.headers?.['x-forwarded-for']),
    },
  };
}

/**
 * @function createKnowledgeBaseVaultReceiptLedgerEntry
 * @description Persists a Knowledge Base receipt ledger entry with tenant/operator evidence and strike payload institutional headers.
 * @param {object} req Express request.
 * @returns {Promise<object>} Persisted receipt ledger entry.
 * @collaboration Knowledge Base Vault saved-document actions, Mongo receipt persistence, tenant evidence, and audit-ready proof.
 */
export async function createKnowledgeBaseVaultReceiptLedgerEntry(req = {}) {
  const payload = normalizeKnowledgeBaseReceiptPayload(req);
  const receipt = await KnowledgeBaseVaultReceipt.create(payload);

  return receipt.toObject();
}

/**
 * @function listKnowledgeBaseVaultReceiptLedgerEntries
 * @description Lists persisted Knowledge Base receipt ledger entries for the active tenant and optional artifact/action filters.
 * @param {object} req Express request.
 * @returns {Promise<object>} Receipt ledger list response.
 * @collaboration Knowledge Base Vault receipt cockpit, tenant-scoped ledger reads, saved PDF/proof history, and audit review.
 */
export async function listKnowledgeBaseVaultReceiptLedgerEntries(req = {}) {
  const actor = resolveKnowledgeBaseReceiptActor(req);
  const query = req.query || {};
  const filters = {
    tenantId: actor.tenantId,
  };

  const artifactId = normalizeKnowledgeBaseReceiptText(query.artifactId || query.entryId);
  const actionType = normalizeKnowledgeBaseReceiptText(query.actionType || query.action).toLowerCase();

  if (artifactId) filters.artifactId = artifactId;
  if (actionType && actionType !== 'all') filters.actionType = actionType;

  const limit = Math.min(Math.max(Number(query.limit || 24), 1), 100);
  const receipts = await KnowledgeBaseVaultReceipt
    .find(filters)
    .sort({ generatedAt: -1, createdAt: -1 })
    .limit(limit)
    .lean();

  return {
    receipts,
    count: receipts.length,
    filters: {
      tenantId: actor.tenantId,
      artifactId,
      actionType: actionType || 'all',
      limit,
    },
    institutionalHeaders: buildKnowledgeBaseReceiptInstitutionalHeaders(req, 'knowledge_base_vault_receipt_list'),
  };
}
