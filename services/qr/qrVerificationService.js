/**
 * ====================================================================
 *  WILSY OS – SOVEREIGN QR VERIFICATION SERVICE (PKI EDITION)
 *  Version: v2.0.0-PKI
 *  Authority: WILSY OS KENNEL EOS – TENANT ISOLATION & CRYPTOGRAPHIC VERIFICATION
 *  Epitome: Verifies QR payload signatures using dual HMAC‑SHA3‑512 (internal)
 *           and RSASSA‑PKCS1‑v1_5 (regulator PKI) signatures. Validates tenant,
 *           invoice existence, amount/currency/VAT/jurisdiction, and expiry
 *           with a grace period. Logs every attempt immutably with anomaly scores
 *           and PKI status. Provides health checks and telemetry hooks.
 *  Collaboration: Wilson (architect), AI (implementation) – 2026-08-10
 *  Institutional: POPIA §19, GDPR §32, SOC2 §CC7.2 – all verification steps are
 *                 non‑repudiable, cryptographically sealed, and regulator‑ready.
 * ====================================================================
 */

import crypto from 'crypto';
import { AuditLogger } from '../AuditLogger.js';
import { getInvoiceById } from '../../controllers/billingController.js';
import { tenantIsolation } from '../../middleware/tenantIsolation.js';

// ------------------------------------------------------------------
//  CONFIGURATION (loaded from environment; HSM/KMS recommended)
// ------------------------------------------------------------------
const QR_SECRET = process.env.QR_SIGNING_SECRET || 'default-secret-change-me';
const WILSY_PUBLIC_KEY = process.env.WILSY_PUBLIC_KEY || ''; // PEM format
const EXPIRY_GRACE_SECONDS = 300; // 5 minutes clock skew tolerance

// ------------------------------------------------------------------
//  PKI VERIFICATION FUNCTION
// ------------------------------------------------------------------

/**
 * verifyPKISignature – Verifies a payload against Wilsy OS public key.
 *
 * @collaboration  Wilson & AI – 2026-08-10
 * @epitome        Provides regulator‑grade authentication using asymmetric
 *                 cryptography, aligning with the ForensicProofBlock PKI badge.
 * @institutional  Required for POPIA §19 and GDPR §32 non‑repudiation.
 *
 * @param {string} payloadString - The JSON payload string.
 * @param {string} signatureHex - The hex‑encoded PKI signature.
 * @param {string|Buffer} publicKeyPem - The Wilsy OS public key (PEM format).
 * @returns {boolean} True if signature is valid, false otherwise.
 */
export function verifyPKISignature(payloadString, signatureHex, publicKeyPem) {
  try {
    const verifier = crypto.createVerify('RSA-SHA256');
    verifier.update(payloadString);
    verifier.end();

    const signatureBuffer = Buffer.from(signatureHex, 'hex');
    return verifier.verify(publicKeyPem, signatureBuffer);
  } catch (err) {
    // In production, this would alert monitoring via structured log.
    console.error('PKI verification error:', err);
    return false;
  }
}

// ------------------------------------------------------------------
//  CORE VERIFICATION FUNCTION
// ------------------------------------------------------------------

/**
 * verifyQRPayload – Verifies a QR payload against HMAC and optional PKI signatures.
 *
 * @collaboration  Wilson & AI – 2026-08-10
 * @epitome        Ensures both internal authenticity (HMAC) and regulator trust (PKI).
 *                 Validates tenant, invoice data, and expiry (with grace).
 * @institutional  Provides a cryptographically sealed proof that can be presented
 *                 to regulators and auditors.
 *
 * @param {string} payloadString - The JSON string that was originally signed.
 * @param {string} signature - The hex‑encoded HMAC signature provided with the QR.
 * @param {string} tenantId - The tenant context (must match the payload's tenantId).
 * @param {Object} [options] - Additional options.
 * @param {string} [options.secret] - Override the HMAC secret (defaults to env).
 * @param {string} [options.publicKey] - Override the PKI public key (defaults to env).
 * @param {boolean} [options.skipInvoiceCheck=false] - For testing, skip invoice lookup.
 * @returns {Promise<Object>} Verification proof:
 *          { valid: boolean, invoice?: Object, tenant?: string, merkleRoot?: string,
 *            sealHash?: string, error?: string, anomalyScore?: number, pkiVerified?: boolean }
 *
 * @throws {Error} If required parameters are missing or malformed.
 */
export async function verifyQRPayload(payloadString, signature, tenantId, options = {}) {
  const secret = options.secret || QR_SECRET;
  const publicKey = options.publicKey || WILSY_PUBLIC_KEY;
  const skipInvoiceCheck = options.skipInvoiceCheck || false;

  // Validate inputs
  if (!payloadString || typeof payloadString !== 'string') {
    throw new Error('verifyQRPayload: payloadString must be a non‑empty string');
  }
  if (!signature || typeof signature !== 'string') {
    throw new Error('verifyQRPayload: signature must be a non‑empty string');
  }
  if (!tenantId || typeof tenantId !== 'string') {
    throw new Error('verifyQRPayload: tenantId is required and must be a string');
  }

  // Prepare proof object
  const proof = {
    valid: false,
    tenant: tenantId,
    anomalyScore: 0,
    error: null,
    invoice: null,
    merkleRoot: null,
    sealHash: null,
    pkiVerified: false,
  };

  try {
    // 1. HMAC Verification (internal)
    const hmac = crypto.createHmac('sha3-512', secret);
    hmac.update(payloadString);
    const expectedSignature = hmac.digest('hex');

    const sigBuffer = Buffer.from(signature, 'hex');
    const expectedBuffer = Buffer.from(expectedSignature, 'hex');
    if (sigBuffer.length !== expectedBuffer.length) {
      proof.error = 'Signature length mismatch';
      proof.anomalyScore = 0.8;
      await logVerificationAttempt(proof, payloadString, signature, tenantId);
      return proof;
    }
    const hmacValid = crypto.timingSafeEqual(sigBuffer, expectedBuffer);
    if (!hmacValid) {
      proof.error = 'Invalid HMAC signature';
      proof.anomalyScore = 0.9;
      await logVerificationAttempt(proof, payloadString, signature, tenantId);
      return proof;
    }

    // 2. Parse payload
    let payload;
    try {
      payload = JSON.parse(payloadString);
    } catch (e) {
      proof.error = 'Malformed payload JSON';
      proof.anomalyScore = 0.7;
      await logVerificationAttempt(proof, payloadString, signature, tenantId);
      return proof;
    }

    // 3. Tenant match
    if (payload.tenantId !== tenantId) {
      proof.error = `Tenant mismatch: payload tenant "${payload.tenantId}" vs request "${tenantId}"`;
      proof.anomalyScore = 0.85;
      await logVerificationAttempt(proof, payloadString, signature, tenantId);
      return proof;
    }

    // 4. Expiry with grace period
    const expiresAt = new Date(payload.expiresAt);
    const now = new Date();
    const graceMs = EXPIRY_GRACE_SECONDS * 1000;
    if (isNaN(expiresAt.getTime()) || expiresAt.getTime() < now.getTime() - graceMs) {
      proof.error = 'QR code expired';
      proof.anomalyScore = 0.5;
      await logVerificationAttempt(proof, payloadString, signature, tenantId);
      return proof;
    }

    // 5. Optional PKI verification (regulator mode)
    if (payload.pkiSignature) {
      if (!publicKey || publicKey === '') {
        proof.error = 'PKI public key not configured';
        proof.anomalyScore = 0.6;
        await logVerificationAttempt(proof, payloadString, signature, tenantId);
        return proof;
      }
      const pkiValid = verifyPKISignature(payloadString, payload.pkiSignature, publicKey);
      if (!pkiValid) {
        proof.error = 'Invalid PKI signature';
        proof.anomalyScore = 0.95;
        await logVerificationAttempt(proof, payloadString, signature, tenantId);
        return proof;
      }
      proof.pkiVerified = true;
    }

    // 6. Invoice lookup and validation
    if (!skipInvoiceCheck) {
      const invoice = await getInvoiceById(payload.invoiceId, tenantId);
      if (!invoice) {
        proof.error = 'Invoice not found';
        proof.anomalyScore = 0.6;
        await logVerificationAttempt(proof, payloadString, signature, tenantId);
        return proof;
      }

      // Validate amount, currency, VAT, jurisdiction against invoice data
      if (Math.abs(invoice.total - payload.amount) > 0.01) {
        proof.error = `Amount mismatch: invoice ${invoice.total} vs payload ${payload.amount}`;
        proof.anomalyScore = 0.7;
        await logVerificationAttempt(proof, payloadString, signature, tenantId);
        return proof;
      }
      if (invoice.currency !== payload.currency) {
        proof.error = `Currency mismatch: invoice ${invoice.currency} vs payload ${payload.currency}`;
        proof.anomalyScore = 0.7;
        await logVerificationAttempt(proof, payloadString, signature, tenantId);
        return proof;
      }
      // Additional checks: VAT rate, jurisdiction (if stored in invoice)
      if (invoice.vatRate !== undefined && invoice.vatRate !== payload.vatRate) {
        proof.error = `VAT rate mismatch: invoice ${invoice.vatRate} vs payload ${payload.vatRate}`;
        proof.anomalyScore = 0.7;
        await logVerificationAttempt(proof, payloadString, signature, tenantId);
        return proof;
      }
      // Jurisdiction: if invoice has jurisdiction field
      if (invoice.jurisdiction && invoice.jurisdiction !== payload.jurisdiction) {
        proof.error = `Jurisdiction mismatch: invoice ${invoice.jurisdiction} vs payload ${payload.jurisdiction}`;
        proof.anomalyScore = 0.7;
        await logVerificationAttempt(proof, payloadString, signature, tenantId);
        return proof;
      }

      // Store invoice details in proof
      proof.invoice = invoice;
      proof.merkleRoot = payload.merkleRoot || invoice.merkleRoot || null;
      proof.sealHash = payload.sealHash || invoice.sealHash || null;
    } else {
      proof.merkleRoot = payload.merkleRoot || null;
      proof.sealHash = payload.sealHash || null;
    }

    // 7. All checks passed
    proof.valid = true;
    proof.error = null;
    proof.anomalyScore = 0;

    // 8. Log successful verification
    await logVerificationAttempt(proof, payloadString, signature, tenantId);

    return proof;

  } catch (error) {
    proof.error = `Unexpected error: ${error.message}`;
    proof.anomalyScore = 0.9;
    await logVerificationAttempt(proof, payloadString, signature, tenantId);
    // In production, emit a structured alert to monitoring (e.g., Prometheus)
    console.error('QR Verification system error:', error);
    return proof;
  }
}

// ------------------------------------------------------------------
//  AUDIT LOGGING HELPER (with enhanced redaction)
// ------------------------------------------------------------------

/**
 * logVerificationAttempt – Internal helper to log every verification to the audit trail.
 *
 * @collaboration  Internal – used by verifyQRPayload.
 * @epitome        Records the SHA3‑512 digest of the signature (not the raw signature)
 *                 for regulator traceability without exposing sensitive material.
 * @institutional  Meets POPIA/GDPR data minimisation requirements.
 *
 * @param {Object} proof - The proof object (contains valid, error, anomalyScore, etc.).
 * @param {string} payloadString - The original payload string.
 * @param {string} signature - The provided HMAC signature.
 * @param {string} tenantId - The tenant context.
 * @returns {Promise<void>}
 */
async function logVerificationAttempt(proof, payloadString, signature, tenantId) {
  try {
    const logEntry = {
      action: 'QR_VERIFICATION',
      tenantId,
      timestamp: new Date().toISOString(),
      valid: proof.valid,
      error: proof.error,
      anomalyScore: proof.anomalyScore,
      payloadHash: crypto.createHash('sha3-512').update(payloadString).digest('hex'),
      signatureDigest: crypto.createHash('sha3-512').update(signature).digest('hex'), // redacted
      pkiVerified: proof.pkiVerified || false,
      invoiceId: proof.invoice?.invoiceId || null,
      merkleRoot: proof.merkleRoot,
      sealHash: proof.sealHash,
    };
    // Add compliance metadata if available
    if (proof.invoice) {
      logEntry.amount = proof.invoice.total;
      logEntry.currency = proof.invoice.currency;
      logEntry.jurisdiction = proof.invoice.jurisdiction || 'ZA';
    }
    await AuditLogger.log(logEntry);
  } catch (logError) {
    // Fail silently – but alert monitoring
    console.error('Failed to log verification attempt:', logError);
    // In production, increment a Prometheus counter
  }
}

// ------------------------------------------------------------------
//  TENANT‑AWARE WRAPPER
// ------------------------------------------------------------------

/**
 * verifyQRPayloadWithTenant – Enforces tenant isolation via request context.
 *
 * @collaboration  Wilson & AI – 2026-08-10
 * @epitome        Recommended entry point for API routes; ensures tenantId is
 *                 derived from the request context (middleware).
 * @institutional  Prevents cross‑tenant verification, ensuring data segregation.
 *
 * @param {string} payloadString - The QR payload string.
 * @param {string} signature - The HMAC signature.
 * @param {Object} req - Express request object (must have `tenant` property).
 * @param {Object} [options] - Additional options passed to verifyQRPayload.
 * @returns {Promise<Object>} Same as verifyQRPayload.
 *
 * @throws {Error} If tenant is missing in request.
 */
export async function verifyQRPayloadWithTenant(payloadString, signature, req, options = {}) {
  const tenantId = req.tenant?.id || req.headers['x-tenant-id'];
  if (!tenantId) {
    throw new Error('verifyQRPayloadWithTenant: tenant context not found in request');
  }
  return verifyQRPayload(payloadString, signature, tenantId, options);
}

// ------------------------------------------------------------------
//  HEALTH CHECK – Operational Seal
// ------------------------------------------------------------------

/**
 * healthCheck – Validates service configuration and readiness.
 *
 * @collaboration  Wilson & AI – 2026-08-10
 * @epitome        Provides a simple status endpoint for monitoring and CI/CD.
 * @institutional  Required for SOC2 §CC7.2 continuous monitoring.
 *
 * @returns {Object} { status: 'healthy', secretSet: boolean, pkiConfigured: boolean, version: string }
 */
export function healthCheck() {
  const secretSet = QR_SECRET !== 'default-secret-change-me';
  const pkiConfigured = Boolean(WILSY_PUBLIC_KEY && WILSY_PUBLIC_KEY.length > 0);
  return {
    status: 'healthy',
    secretSet,
    pkiConfigured,
    version: 'v2.0.0-PKI',
  };
}

// ------------------------------------------------------------------
//  EXPORT DEFAULTS
// ------------------------------------------------------------------
export default {
  verifyQRPayload,
  verifyQRPayloadWithTenant,
  verifyPKISignature,
  healthCheck,
};
