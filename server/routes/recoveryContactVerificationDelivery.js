/**
 * WILSY OS — INTERNAL RECOVERY CONTACT VERIFICATION DELIVERY BRIDGE
 * VERSION: v1.0.0-R10E16-INTERNAL-RECOVERY-CONTACT-VERIFICATION-DELIVERY
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Authenticates one Python-EOS verification-delivery instruction and
 *          delegates the already-issued bearer to strict SMTP transport.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/recoveryContactVerificationDelivery.js
 * COLLABORATION / OWNERSHIP: Python EOS owns challenge/contact authority;
 *                            recoveryContactVerificationEmailTransport owns SMTP;
 *                            this route owns internal request authentication only.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   v1.0.0-R10E16-INTERNAL-RECOVERY-CONTACT-VERIFICATION-DELIVERY — Establishes
 *   exact-body ingress, dedicated SHA3-512 HMAC secret, timing-safe signature
 *   comparison, 60-second freshness, generic failures, and 204-only success.
 * COMPLIANCE: POPIA §19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Recipient and verification bearer are never logged.
 * TENANT BOUNDARY: No tenant identity is accepted; Python already authenticates
 *                  exact tenant/principal before invoking this transport bridge.
 * AUTHORITY BOUNDARY: Internal request authentication and SMTP delegation only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import crypto from 'node:crypto';
import express from 'express';

import recoveryContactVerificationEmailTransport from '../services/recoveryContactVerificationEmailTransport.js';

export const INTERNAL_RECOVERY_CONTACT_VERIFICATION_DELIVERY_PATH =
  '/internal/auth/recovery-contact-verification-delivery';
export const RECOVERY_CONTACT_VERIFICATION_TIMESTAMP_HEADER =
  'x-wilsy-recovery-contact-verification-timestamp';
export const RECOVERY_CONTACT_VERIFICATION_SIGNATURE_HEADER =
  'x-wilsy-recovery-contact-verification-signature';
export const RECOVERY_CONTACT_VERIFICATION_MAX_SKEW_SECONDS = 60;

function secretFromEnvironment(environment) {
  const value = String(
    environment.WILSY_RECOVERY_CONTACT_VERIFICATION_DELIVERY_SECRET || '',
  );
  return value.length >= 32 ? value : null;
}

function exactDeliveryBody(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const expected = ['expires_at', 'recipient_email', 'verification_token'];
  if (Object.keys(value).sort().join('|') !== expected.join('|')) return null;
  const { recipient_email: recipientEmail, verification_token: verificationToken, expires_at: expiresAt } = value;
  if (
    typeof recipientEmail !== 'string'
    || typeof verificationToken !== 'string'
    || typeof expiresAt !== 'string'
    || !recipientEmail
    || !verificationToken
    || !expiresAt
  ) return null;
  return { recipientEmail, verificationToken, expiresAt };
}

export function recoveryContactVerificationSigningPayload(timestamp, body) {
  return [
    timestamp,
    body.recipient_email,
    body.verification_token,
    body.expires_at,
  ].join('\n');
}

function validFreshTimestamp(rawTimestamp, nowMilliseconds) {
  if (typeof rawTimestamp !== 'string' || !/^[0-9]{10,13}$/u.test(rawTimestamp)) return false;
  const numeric = Number(rawTimestamp);
  if (!Number.isSafeInteger(numeric)) return false;
  const timestampMilliseconds = rawTimestamp.length === 10 ? numeric * 1000 : numeric;
  const skew = Math.abs(nowMilliseconds - timestampMilliseconds);
  return skew <= RECOVERY_CONTACT_VERIFICATION_MAX_SKEW_SECONDS * 1000;
}

function validSignature(rawSignature, timestamp, body, secret) {
  if (typeof rawSignature !== 'string' || !/^[0-9a-f]{128}$/u.test(rawSignature)) return false;
  const expected = crypto
    .createHmac('sha3-512', secret)
    .update(recoveryContactVerificationSigningPayload(timestamp, body), 'utf8')
    .digest('hex');
  const suppliedBuffer = Buffer.from(rawSignature, 'hex');
  const expectedBuffer = Buffer.from(expected, 'hex');
  return (
    suppliedBuffer.length === expectedBuffer.length
    && crypto.timingSafeEqual(suppliedBuffer, expectedBuffer)
  );
}

export function createRecoveryContactVerificationDeliveryRouter({
  transport = recoveryContactVerificationEmailTransport,
  environment = process.env,
  clock = () => Date.now(),
} = {}) {
  if (!transport || typeof transport.deliver !== 'function') {
    throw new TypeError('recovery contact verification delivery transport is required');
  }
  if (typeof clock !== 'function') {
    throw new TypeError('clock must be callable');
  }

  const router = express.Router();

  router.post('/recovery-contact-verification-delivery', async (req, res) => {
    const secret = secretFromEnvironment(environment);
    const body = exactDeliveryBody(req.body);
    if (!secret) {
      return res.status(503).json({ status: 'RECOVERY_CONTACT_VERIFICATION_DELIVERY_UNAVAILABLE' });
    }
    if (!body) {
      return res.status(400).json({ status: 'RECOVERY_CONTACT_VERIFICATION_DELIVERY_REQUEST_INVALID' });
    }

    const timestamp = req.get(RECOVERY_CONTACT_VERIFICATION_TIMESTAMP_HEADER);
    const signature = req.get(RECOVERY_CONTACT_VERIFICATION_SIGNATURE_HEADER);
    if (
      !validFreshTimestamp(timestamp, clock())
      || !validSignature(signature, timestamp, req.body, secret)
    ) {
      return res.status(401).json({ status: 'RECOVERY_CONTACT_VERIFICATION_DELIVERY_UNAUTHORIZED' });
    }

    try {
      await transport.deliver({
        recipientEmail: body.recipientEmail,
        verificationToken: body.verificationToken,
        expiresAt: body.expiresAt,
      });
      return res.status(204).end();
    } catch (_error) {
      return res.status(503).json({ status: 'RECOVERY_CONTACT_VERIFICATION_DELIVERY_FAILED' });
    }
  });

  return router;
}

export default createRecoveryContactVerificationDeliveryRouter();

/**
 * ARTIFACT: server/routes/recoveryContactVerificationDelivery.js
 * VERSION: v1.0.0-R10E16-INTERNAL-RECOVERY-CONTACT-VERIFICATION-DELIVERY
 * AUTHORITY BOUNDARY: dedicated HMAC-authenticated internal verification delivery ingress only
 * TENANT POSTURE: no tenant input; Python retains authenticated tenant/principal authority
 * FAIL-CLOSED POSTURE: missing secret, invalid body, stale/bad signature, and transport failure reject
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
