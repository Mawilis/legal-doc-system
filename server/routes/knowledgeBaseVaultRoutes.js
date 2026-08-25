/* eslint-disable */

import express from 'express';
import { resolveKnowledgeBaseVaultSearch } from '../services/knowledgeBase/wilsyKnowledgeBaseRegistrySearchService.js';
import { createReadStream } from 'node:fs';
import { authenticateToken } from '../middleware/auth.js';
import {
  readKnowledgeBaseVaultProof,
  resolveKnowledgeBaseVaultJsonFile,
  resolveKnowledgeBaseVaultPdfFile,
} from '../services/knowledgeBase/wilsyKnowledgeBaseVaultService.js';
import { createKnowledgeBaseVaultReceiptLedgerEntry, listKnowledgeBaseVaultReceiptLedgerEntries } from '../services/knowledgeBase/wilsyKnowledgeBaseReceiptLedgerService.js';

const router = express.Router();

/**
 * @function readAuthenticatedVaultUser
 * @description Reads authenticated user context from common Wilsy OS request locations.
 * @param {object} req Express request.
 * @returns {object} Authenticated user context.
 * @collaboration FG108O3N2 Vault permissions, Founder/admin full view, and tenant read mode.
 */
function readAuthenticatedVaultUser(req = {}) {
  return req.user || req.admin || req.authenticatedUser || {};
}

/**
 * @function sendVaultError
 * @description Sends redacted Knowledge Base Vault errors without leaking internal file paths.
 * @param {object} res Express response.
 * @param {Error} error Source error.
 * @returns {object} JSON response.
 * @collaboration FG108O3N2 Vault route safety and proof-ledger access.
 */
function sendVaultError(res, error = new Error('KNOWLEDGE_BASE_VAULT_ERROR')) {
  const statusCode = Number(error.statusCode || 500);

  return res.status(statusCode).json({
    success: false,
    error: error.message || 'KNOWLEDGE_BASE_VAULT_ERROR',
    sourceMode: 'KNOWLEDGE_BASE_VAULT_READ_ONLY',
  });
}

/**
 * @function resolveKnowledgeBaseVaultRouteFilters
 * @description Resolves backend search/category filters from query parameters and institutional POST body.
 * @param {object} req Express request.
 * @returns {object} Vault registry filters.
 * @collaboration Knowledge Base Vault live backend search, POST evidence body, and scalable registry filtering.
 */
function resolveKnowledgeBaseVaultRouteFilters(req = {}) {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const filters = body.filters && typeof body.filters === 'object' ? body.filters : {};

  return {
    query:
      req.query?.query ||
      req.query?.search ||
      body.query ||
      body.search ||
      filters.query ||
      filters.search ||
      '',
    category: req.query?.category || body.category || filters.category || 'all',
    lifecycle: req.query?.lifecycle || body.lifecycle || filters.lifecycle || 'all',
    module: req.query?.module || body.module || filters.module || 'all',
    playbookType: req.query?.playbookType || body.playbookType || filters.playbookType || 'all',
  };
}

/**
 * @function handleKnowledgeBaseVaultList
 * @description Lists permissioned saved Knowledge Base artifacts from the manifest only.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration FG108O3N2 global Vault UI and manifest-backed resolver.
 */
async function handleKnowledgeBaseVaultList(req, res) {
  try {
    const vault = await resolveKnowledgeBaseVaultSearch({
      ...readAuthenticatedVaultUser(req),
      filters: resolveKnowledgeBaseVaultRouteFilters(req),
    });

    return res.json({
      success: true,
      vault,
    });
  } catch (error) {
    return sendVaultError(res, error);
  }
}

/**
 * @function handleKnowledgeBaseVaultJson
 * @description Streams a saved machine-readable Knowledge Base JSON companion without calling the PDF generator.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<void>} JSON stream response.
 * @collaboration FG109 Knowledge Base JSON companion route, manifest jsonPath, and Vault UI JSON action.
 */
async function handleKnowledgeBaseVaultJson(req, res) {
  try {
    const json = await resolveKnowledgeBaseVaultJsonFile(
      req.params.id,
      readAuthenticatedVaultUser(req)
    );
    const dispositionType = req.query.download === 'true' ? 'attachment' : 'inline';

    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.setHeader('Content-Disposition', `${dispositionType}; filename="${json.filename}"`);
    res.setHeader('X-Wilsy-Knowledge-Base-Source-Mode', 'SAVED_JSON_ONLY');
    res.setHeader('X-Wilsy-Knowledge-Base-Json-Status', json.entry.jsonStatus);

    const stream = createReadStream(json.absolutePath);
    stream.on('error', () => sendVaultError(res, new Error('KNOWLEDGE_BASE_JSON_STREAM_FAILED')));
    stream.pipe(res);
  } catch (error) {
    sendVaultError(res, error);
  }
}

/**
 * @function handleKnowledgeBaseVaultProof
 * @description Opens a saved proof sidecar JSON for a permissioned Knowledge Base artifact.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration FG108O3N2 evidence sidecar action and source-aware Vault UI.
 */
async function handleKnowledgeBaseVaultProof(req, res) {
  try {
    const proofPayload = await readKnowledgeBaseVaultProof(
      req.params.id,
      readAuthenticatedVaultUser(req)
    );

    return res.json({
      success: true,
      ...proofPayload,
    });
  } catch (error) {
    return sendVaultError(res, error);
  }
}

/**
 * @function handleKnowledgeBaseVaultPdf
 * @description Streams a saved PDF for open, print, or download without calling the PDF generator.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<void>} PDF stream response.
 * @collaboration FG108O3N2 saved PDF action route and no-regeneration contract.
 */
async function handleKnowledgeBaseVaultPdf(req, res) {
  try {
    const pdf = await resolveKnowledgeBaseVaultPdfFile(
      req.params.id,
      readAuthenticatedVaultUser(req)
    );
    const dispositionType = req.query.download === 'true' ? 'attachment' : 'inline';

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `${dispositionType}; filename="${pdf.filename}"`);
    res.setHeader('X-Wilsy-Knowledge-Base-Source-Mode', 'SAVED_PDF_ONLY');
    res.setHeader('X-Wilsy-Knowledge-Base-Proof-Status', pdf.entry.proofStatus);

    const stream = createReadStream(pdf.absolutePath);
    stream.on('error', () => sendVaultError(res, new Error('KNOWLEDGE_BASE_PDF_STREAM_FAILED')));
    stream.pipe(res);
  } catch (error) {
    sendVaultError(res, error);
  }
}


// FG108O5B_RECEIPT_LEDGER_HANDLERS_START
/**
 * @function handleKnowledgeBaseVaultReceiptList
 * @description Lists tenant-scoped persisted Knowledge Base Vault receipt ledger entries.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<void>} Sends receipt ledger list response.
 * @collaboration Knowledge Base Vault route, receipt ledger service, tenant evidence, and saved PDF/proof actions.
 */
async function handleKnowledgeBaseVaultReceiptList(req, res) {
  try {
    const ledger = await listKnowledgeBaseVaultReceiptLedgerEntries(req);

    res.status(200).json({
      ok: true,
      mode: 'KNOWLEDGE_BASE_VAULT_RECEIPT_LEDGER',
      ...ledger,
    });
  } catch (error) {
    res.status(500).json({
      ok: false,
      code: 'KNOWLEDGE_BASE_RECEIPT_LEDGER_LIST_FAILED',
      message: error?.message || 'Unable to list Knowledge Base receipt ledger entries.',
    });
  }
}

/**
 * @function handleKnowledgeBaseVaultReceiptCreate
 * @description Persists one tenant/operator-scoped Knowledge Base Vault action receipt with strike payload evidence.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<void>} Sends persisted receipt ledger response.
 * @collaboration Knowledge Base Vault route, receipt ledger service, institutional headers, and action evidence.
 */
async function handleKnowledgeBaseVaultReceiptCreate(req, res) {
  try {
    const receipt = await createKnowledgeBaseVaultReceiptLedgerEntry(req);

    res.status(201).json({
      ok: true,
      mode: 'KNOWLEDGE_BASE_VAULT_RECEIPT_LEDGER',
      receipt,
    });
  } catch (error) {
    res.status(500).json({
      ok: false,
      code: 'KNOWLEDGE_BASE_RECEIPT_LEDGER_CREATE_FAILED',
      message: error?.message || 'Unable to persist Knowledge Base receipt ledger entry.',
    });
  }
}
// FG108O5B_RECEIPT_LEDGER_HANDLERS_END

router.use(authenticateToken);

router.get('/', handleKnowledgeBaseVaultList);
router.post('/', handleKnowledgeBaseVaultList);


// FG108O5B_RECEIPT_LEDGER_ROUTES_START
router.get('/receipts', handleKnowledgeBaseVaultReceiptList);
router.post('/receipts', handleKnowledgeBaseVaultReceiptCreate);
// FG108O5B_RECEIPT_LEDGER_ROUTES_END

router.get('/:id/proof', handleKnowledgeBaseVaultProof);
router.post('/:id/proof', handleKnowledgeBaseVaultProof);
router.get('/:id/json', handleKnowledgeBaseVaultJson);
router.post('/:id/json', handleKnowledgeBaseVaultJson);
router.get('/:id/pdf', handleKnowledgeBaseVaultPdf);
router.post('/:id/pdf', handleKnowledgeBaseVaultPdf);

export default router;
