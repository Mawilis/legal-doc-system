/* eslint-disable */
/**
 * WILSY OS - BUSINESS ARTIFACT INGRESS [V1.1.0-SECURE-BROWSER-ADMISSION]
 * Absolute Path: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/businessArtifactIngress.js
 */

import crypto from 'node:crypto';

const MAX_ARTIFACT_CLOCK_SKEW_MS = 5 * 60 * 1000;

/**
 * @function createArtifactBrowserProof
 * @description Recreates the browser-safe artifact proof.
 * @param {string} type - Artifact type.
 * @param {string} tenantId - Tenant id.
 * @param {string} timestamp - Forensic timestamp.
 * @returns {string} SHA-512 browser proof.
 * @collaboration Keeps browser-origin artifact requests secure without exposing server HMAC secrets.
 */
const createArtifactBrowserProof = (type = '', tenantId = '', timestamp = '') =>
  crypto.createHash('sha512').update(`${type}|${tenantId}|${timestamp}`).digest('hex');

/**
 * @function readHeader
 * @description Reads a request header case-insensitively.
 * @param {import('express').Request} req - Express request.
 * @param {string[]} names - Header names.
 * @returns {string} Header value.
 * @collaboration Normalizes browser, curl and Express lowercase header behavior.
 */
const readHeader = (req, names = []) => {
  for (const name of names) {
    const value = req.get?.(name) || req.headers?.[name] || req.headers?.[name.toLowerCase()];
    if (value !== undefined && value !== null && value !== '') return String(value);
  }

  return '';
};

/**
 * @function verifyBusinessArtifactIngress
 * @description Verifies browser-origin business artifact requests before PDF generation.
 * @param {import('express').Request} req - Express request.
 * @param {import('express').Response} res - Express response.
 * @param {import('express').NextFunction} next - Express next handler.
 * @returns {void}
 * @collaboration Admits secure browser artifact generation while keeping server-side HMAC sealing inside artifactController.
 */
export const verifyBusinessArtifactIngress = (req, res, next) => {
  req.body = req.body && typeof req.body === 'object' ? req.body : {};

  const metadata =
    req.body.metadata && typeof req.body.metadata === 'object' ? req.body.metadata : {};

  const type = String(
    readHeader(req, ['X-Artifact-Type', 'X-Wilsy-Artifact-Type']) ||
      req.body.type ||
      metadata.type ||
      req.query?.type ||
      ''
  ).trim();

  const tenantId = String(
    readHeader(req, ['X-Tenant-ID', 'X-Wilsy-Tenant-ID']) ||
      req.body.tenantId ||
      metadata.tenantId ||
      'MASTER'
  ).trim();

  const timestamp = String(
    readHeader(req, ['X-Forensic-Timestamp']) || req.body.timestamp || metadata.timestamp || ''
  ).trim();

  const nonce = String(
    readHeader(req, ['X-Cryptographic-Nonce']) || req.body.nonce || metadata.nonce || ''
  ).trim();

  const requestProof = String(
    readHeader(req, ['X-Request-Proof']) || req.body.requestProof || metadata.requestProof || ''
  ).trim();

  if (!type || !tenantId || !timestamp || !nonce || !requestProof) {
    return res.status(403).json({
      success: false,
      error: 'BUSINESS_ARTIFACT_INGRESS_REJECTED',
      message: 'Missing artifact type, tenant, timestamp, nonce or request proof.',
      diagnostics: {
        hasType: Boolean(type),
        hasTenantId: Boolean(tenantId),
        hasTimestamp: Boolean(timestamp),
        hasNonce: Boolean(nonce),
        hasRequestProof: Boolean(requestProof),
        bodyKeys: Object.keys(req.body || {}),
        metadataKeys: Object.keys(metadata || {}),
      },
    });
  }

  const parsedTimestamp = Date.parse(timestamp);
  const clockSkew = Math.abs(Date.now() - parsedTimestamp);

  if (!Number.isFinite(parsedTimestamp) || clockSkew > MAX_ARTIFACT_CLOCK_SKEW_MS) {
    return res.status(403).json({
      success: false,
      error: 'BUSINESS_ARTIFACT_TIMESTAMP_REJECTED',
      message: 'Artifact timestamp is invalid or outside the accepted freshness window.',
    });
  }

  const expectedProof = createArtifactBrowserProof(type, tenantId, timestamp);

  if (expectedProof !== requestProof) {
    return res.status(401).json({
      success: false,
      error: 'BUSINESS_ARTIFACT_PROOF_REJECTED',
      message: 'Artifact request proof does not match the browser-safe SHA-512 contract.',
    });
  }

  req.body.type = type;
  req.body.tenantId = tenantId;
  req.body.timestamp = timestamp;
  req.body.requestProof = requestProof;
  req.body.nonce = nonce;
  req.body.metadata = {
    ...metadata,
    type,
    tenantId,
    timestamp,
    requestProof,
    nonce,
    proofVersion: metadata.proofVersion || 'WILSY_BROWSER_SHA512_V1',
  };

  req.headers['x-artifact-type'] = type;
  req.headers['x-request-proof'] = requestProof;
  req.headers['x-tenant-id'] = tenantId;
  req.headers['x-forensic-timestamp'] = timestamp;
  req.headers['x-cryptographic-nonce'] = nonce;

  req.wilsyBusinessArtifactIngress = {
    type,
    tenantId,
    timestamp,
    nonce,
    proofVerified: true,
    verifiedAt: new Date().toISOString(),
  };

  return next();
};
