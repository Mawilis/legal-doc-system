/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN QR GENERATOR ENGINE [v1.2.0-STRICT-CONFIGURATION]                                                              ║
 * ║ [SIGNED VERIFICATION PAYLOADS | SHA3-512 PARITY | TENANT-BOUND INVOICES | SCANNABLE PNG]                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME: Produces the exact signed payload consumed by /api/qr/verify/:payload; a generated QR is a verifiable document reference.    ║
 * ║ BIBLICAL ANCHOR: Psalm 1:3 - "And he shall be like a tree planted by the rivers of water..."                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/qr/qrGenerator.js                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & OWNERSHIP: Wilson Khanyezi (Founder/Chief Architect) | AI Engineering (Codex) - unified generator and verifier.      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import QRCode from 'qrcode';

const QR_SECRET = process.env.QR_SIGNING_SECRET || process.env.QR_SECRET || '';
const QR_VERIFICATION_BASE_URL = process.env.QR_VERIFICATION_BASE_URL || '';
const QR_EXPIRY_MS = 30 * 24 * 60 * 60 * 1000;
const MAX_QR_EXPIRY_MS = 90 * 24 * 60 * 60 * 1000;

/**
 * @function getSigningConfiguration
 * @description Validates non-secret QR signing configuration before document issuance.
 * @param {string} [secret=QR_SECRET] - Signing secret supplied by the environment.
 * @param {string} [baseUrl=QR_VERIFICATION_BASE_URL] - HTTPS public verification endpoint.
 * @returns {{secret: string, baseUrl: string}} Validated configuration.
 * @throws {Error} When a production signing secret or HTTPS verifier origin is absent.
 * @collaboration Prevents a shipped default secret or untrusted QR destination from becoming a forensic control.
 */
export function getSigningConfiguration(secret = QR_SECRET, baseUrl = QR_VERIFICATION_BASE_URL) {
  if (typeof secret !== 'string' || secret.trim().length < 32) {
    throw new Error('QR_SIGNING_SECRET must be configured and contain at least 32 characters');
  }
  let parsedUrl;
  try {
    parsedUrl = new URL(baseUrl);
  } catch {
    throw new Error('QR_VERIFICATION_BASE_URL must be a valid HTTPS URL');
  }
  if (parsedUrl.protocol !== 'https:') {
    throw new Error('QR_VERIFICATION_BASE_URL must use HTTPS');
  }
  return { secret: secret.trim(), baseUrl: parsedUrl.toString().replace(/\/$/, '') };
}

/**
 * @function buildQRPayload
 * @description Builds the base64url payload and SHA3-512 signature accepted by the QR verification controller.
 * @param {object} invoiceData - Tenant-scoped invoice or statement metadata.
 * @param {string} invoiceData.invoiceId - Persisted invoice or statement number.
 * @param {string} invoiceData.tenantId - Tenant that owns the document.
 * @param {number} invoiceData.amount - Non-negative document total.
 * @param {string} invoiceData.currency - ISO 4217 currency code.
 * @param {string} invoiceData.traceId - Persisted forensic trace identifier.
 * @param {string} [invoiceData.merkleRoot] - Ledger Merkle root retained in the encoded proof.
 * @param {string} [invoiceData.sealHash] - Document seal.
 * @param {string} [invoiceData.documentType='INVOICE'] - INVOICE or STATEMENT.
 * @param {string|number} [invoiceData.expiresAt] - Expiry instant accepted by Date.
 * @param {string} [secret=QR_SECRET] - Shared verifier secret.
 * @param {string} [baseUrl=QR_VERIFICATION_BASE_URL] - Public origin and verification path.
 * @returns {{payload: object, signature: string, encodedPayload: string, verificationUrl: string, payloadString: string}}
 * @collaboration Keeps the producer contract byte-for-byte compatible with qrController.decodeQrPayload.
 */
export function buildQRPayload(invoiceData = {}, secret = QR_SECRET, baseUrl = QR_VERIFICATION_BASE_URL) {
  const configuration = getSigningConfiguration(secret, baseUrl);
  const requiredFields = ['invoiceId', 'tenantId', 'amount', 'currency', 'traceId'];
  for (const field of requiredFields) {
    if (invoiceData[field] === undefined || invoiceData[field] === null || invoiceData[field] === '') {
      throw new Error(`buildQRPayload: missing required field "${field}"`);
    }
  }

  const amount = Number(invoiceData.amount);
  if (!Number.isFinite(amount) || amount < 0) {
    throw new Error('buildQRPayload: amount must be a non-negative finite number');
  }

  const issuedAt = Date.now();
  const expiresAt = invoiceData.expiresAt ? new Date(invoiceData.expiresAt).getTime() : issuedAt + QR_EXPIRY_MS;
  if (!Number.isFinite(expiresAt) || expiresAt <= issuedAt || expiresAt > issuedAt + MAX_QR_EXPIRY_MS) {
    throw new Error('buildQRPayload: expiresAt must be after issuance and within 90 days');
  }

  const payload = {
    documentId: String(invoiceData.invoiceId),
    tenantId: String(invoiceData.tenantId),
    amount,
    currency: String(invoiceData.currency).toUpperCase(),
    traceId: String(invoiceData.traceId),
    sealHash: String(invoiceData.sealHash || ''),
    merkleRoot: String(invoiceData.merkleRoot || ''),
    documentType: String(invoiceData.documentType || 'INVOICE').toUpperCase(),
    expiresAt,
    issuedAt,
  };
  const payloadString = JSON.stringify(payload);
  const signature = crypto.createHash('sha3-512').update(`${payloadString}|${configuration.secret}`).digest('hex').toUpperCase();
  const encodedPayload = `${Buffer.from(payloadString, 'utf8').toString('base64url')}.${signature}`;
  const verificationUrl = `${configuration.baseUrl}/${encodeURIComponent(encodedPayload)}`;

  return { payload, signature, encodedPayload, verificationUrl, payloadString };
}

/**
 * @function generateQRCode
 * @description Renders a verification URL into a PNG buffer for an invoice or statement artifact.
 * @param {string} payloadString - Non-empty URL or signed payload to encode.
 * @param {object} [options={}] - qrcode renderer options.
 * @returns {Promise<Buffer>} PNG buffer.
 * @collaboration Uses the documented qrcode server-side buffer API with an explicit, scanner-safe configuration.
 */
export async function generateQRCode(payloadString, options = {}) {
  if (!payloadString || typeof payloadString !== 'string') {
    throw new Error('generateQRCode: payloadString must be a non-empty string');
  }

  const { width = 300, margin = 4, errorCorrectionLevel = 'M', color = { dark: '#020403', light: '#FFFFFF' } } = options;
  if (!Number.isInteger(width) || width < 128 || width > 2048 || !Number.isInteger(margin) || margin < 0 || margin > 16) {
    throw new Error('generateQRCode: width must be 128-2048 and margin must be 0-16');
  }
  try {
    return await QRCode.toBuffer(payloadString, { type: 'png', width, margin, errorCorrectionLevel, color });
  } catch (error) {
    throw new Error(`QR generation failed: ${error.message}`);
  }
}

/**
 * @function healthCheck
 * @description Reports whether the generator uses an explicitly configured signing secret.
 * @returns {{status: string, secretSet: boolean, version: string}} Generator readiness state.
 * @collaboration Exposes non-sensitive readiness evidence without leaking the signing secret.
 */
export function healthCheck() {
  try {
    getSigningConfiguration();
    return { status: 'healthy', secretSet: true, verifierConfigured: true, version: 'v1.2.0-STRICT-CONFIGURATION' };
  } catch (error) {
    return { status: 'misconfigured', secretSet: Boolean(QR_SECRET), verifierConfigured: Boolean(QR_VERIFICATION_BASE_URL), version: 'v1.2.0-STRICT-CONFIGURATION', code: error.message };
  }
}

export default { buildQRPayload, generateQRCode, getSigningConfiguration, healthCheck };
