/**
 * WILSY OS — INTERNAL PASSWORD RECOVERY DELIVERY BRIDGE
 * VERSION: v1.0.0-R10E5-INTERNAL-RECOVERY-DELIVERY-BRIDGE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Authenticates one Python-EOS delivery instruction and delegates the
 *          already-issued recovery bearer to the strict Node SMTP transport.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/passwordRecoveryDelivery.js
 * COLLABORATION / OWNERSHIP: Python EOS owns recovery issuance/lifecycle;
 *                            passwordRecoveryEmailTransport owns SMTP delivery;
 *                            this route owns internal transport authentication only.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v1.0.0-R10E5-INTERNAL-RECOVERY-DELIVERY-BRIDGE — Establishes exact-body internal
 *            delivery ingress with SHA3-512 HMAC, timing-safe comparison,
 *            60-second timestamp freshness, generic failures, and 204-only success.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: No recipient or recovery bearer is logged,
 *                             persisted, returned, or placed in error messages.
 * TENANT BOUNDARY: No tenant identity is accepted; Python already admitted the
 *                  exact tenant/principal before invoking this transport bridge.
 * AUTHORITY BOUNDARY: Internal request authentication and SMTP delegation only;
 *                     no recovery, credential, login, MFA, session, role, or tenant authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import crypto from 'node:crypto';
import express from 'express';

import passwordRecoveryEmailTransport from '../services/passwordRecoveryEmailTransport.js';

export const INTERNAL_RECOVERY_DELIVERY_PATH = '/internal/auth/password-recovery-delivery';
export const RECOVERY_DELIVERY_TIMESTAMP_HEADER = 'x-wilsy-recovery-timestamp';
export const RECOVERY_DELIVERY_SIGNATURE_HEADER = 'x-wilsy-recovery-signature';
export const RECOVERY_DELIVERY_MAX_SKEW_SECONDS = 60;

function secretFromEnvironment(environment) {
  const value = String(environment.WILSY_RECOVERY_DELIVERY_SECRET || '');
  if (value.length < 32) return null;
  return value;
}

function exactDeliveryBody(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const keys = Object.keys(value).sort();
  const expected = ['expires_at', 'recipient_email', 'recovery_token'];
  if (keys.length !== expected.length || keys.some((key, index) => key !== expected[index])) return null;
  const recipientEmail = value.recipient_email;
  const recoveryToken = value.recovery_token;
  const expiresAt = value.expires_at;
  if (
    typeof recipientEmail !== 'string'
    || typeof recoveryToken !== 'string'
    || typeof expiresAt !== 'string'
    || !recipientEmail
    || !recoveryToken
    || !expiresAt
  ) return null;
  return { recipientEmail, recoveryToken, expiresAt };
}

export function recoveryDeliverySigningPayload(timestamp, body) {
  return [
    String(timestamp),
    body.recipient_email,
    body.recovery_token,
    body.expires_at,
  ].join('\n');
}

function validFreshTimestamp(rawTimestamp, nowMilliseconds) {
  if (typeof rawTimestamp !== 'string' || !/^[0-9]{10,13}$/u.test(rawTimestamp)) return false;
  const numeric = Number(rawTimestamp);
  if (!Number.isSafeInteger(numeric) || numeric < 0) return false;
  const timestampMilliseconds = rawTimestamp.length === 10 ? numeric * 1000 : numeric;
  const skew = Math.abs(nowMilliseconds - timestampMilliseconds);
  return skew <= RECOVERY_DELIVERY_MAX_SKEW_SECONDS * 1000;
}

function validSignature(rawSignature, timestamp, body, secret) {
  if (typeof rawSignature !== 'string' || !/^[0-9a-f]{128}$/u.test(rawSignature)) return false;
  const expected = crypto
    .createHmac('sha3-512', secret)
    .update(recoveryDeliverySigningPayload(timestamp, body), 'utf8')
    .digest('hex');
  const suppliedBuffer = Buffer.from(rawSignature, 'hex');
  const expectedBuffer = Buffer.from(expected, 'hex');
  return suppliedBuffer.length === expectedBuffer.length
    && crypto.timingSafeEqual(suppliedBuffer, expectedBuffer);
}

export function createPasswordRecoveryDeliveryRouter({
  transport = passwordRecoveryEmailTransport,
  clock = () => Date.now(),
  environment = process.env,
} = {}) {
  if (!transport || typeof transport.deliver !== 'function') {
    throw new TypeError('password recovery delivery transport is required');
  }
  if (typeof clock !== 'function') throw new TypeError('clock must be callable');
  const router = express.Router();

  router.post('/password-recovery-delivery', async (req, res) => {
    const secret = secretFromEnvironment(environment);
    const body = exactDeliveryBody(req.body);
    if (!secret) return res.status(503).json({ status: 'RECOVERY_DELIVERY_UNAVAILABLE' });
    if (!body) return res.status(400).json({ status: 'RECOVERY_DELIVERY_REQUEST_INVALID' });

    const timestamp = req.get(RECOVERY_DELIVERY_TIMESTAMP_HEADER);
    const signature = req.get(RECOVERY_DELIVERY_SIGNATURE_HEADER);
    const now = clock();
    if (
      !Number.isFinite(now)
      || !validFreshTimestamp(timestamp, now)
      || !validSignature(signature, timestamp, req.body, secret)
    ) {
      return res.status(401).json({ status: 'RECOVERY_DELIVERY_UNAUTHORIZED' });
    }

    try {
      await transport.deliver({
        recipientEmail: body.recipientEmail,
        recoveryToken: body.recoveryToken,
        expiresAt: body.expiresAt,
      });
      return res.status(204).end();
    } catch {
      return res.status(503).json({ status: 'RECOVERY_DELIVERY_FAILED' });
    }
  });

  return router;
}

export default createPasswordRecoveryDeliveryRouter();

/**
 * ARTIFACT: server/routes/passwordRecoveryDelivery.js
 * VERSION: v1.0.0-R10E5-INTERNAL-RECOVERY-DELIVERY-BRIDGE
 * AUTHORITY BOUNDARY: HMAC-authenticated internal delivery ingress and transport delegation only
 * TENANT POSTURE: no tenant input; upstream Python EOS retains tenant/principal recovery authority
 * FAIL-CLOSED POSTURE: missing secret, invalid body, stale/bad signature, and transport failure reject
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
