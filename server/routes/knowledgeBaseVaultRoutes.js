/* eslint-disable */

import express from 'express';
import { resolveKnowledgeBaseVaultSearch } from '../services/knowledgeBase/wilsyKnowledgeBaseRegistrySearchService.js';
import { createReadStream } from 'node:fs';
import { authenticateToken } from '../middleware/auth.js';
import {
  readKnowledgeBaseVaultProof,
  resolveKnowledgeBaseVaultEntries,
  resolveKnowledgeBaseVaultPdfFile,
} from '../services/knowledgeBase/wilsyKnowledgeBaseVaultService.js';

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
    const vault = await resolveKnowledgeBaseVaultEntries(readAuthenticatedVaultUser(req));

    return res.json({
      success: true,
      vault,
    });
  } catch (error) {
    return sendVaultError(res, error);
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

router.use(authenticateToken);

router.get('/', handleKnowledgeBaseVaultList);
router.post('/', handleKnowledgeBaseVaultList);
router.get('/:id/proof', handleKnowledgeBaseVaultProof);
router.post('/:id/proof', handleKnowledgeBaseVaultProof);
router.get('/:id/pdf', handleKnowledgeBaseVaultPdf);
router.post('/:id/pdf', handleKnowledgeBaseVaultPdf);

export default router;
