/**
 * WILSY OS — RECOVERY CONTACT VERIFICATION EMAIL TRANSPORT
 * VERSION: v1.0.0-R10E15-RECOVERY-CONTACT-VERIFICATION-EMAIL-TRANSPORT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Delivers an already-issued recovery-contact possession challenge by
 *          SMTP without creating, validating, persisting, or interpreting
 *          recovery-contact or password-recovery authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/recoveryContactVerificationEmailTransport.js
 * COLLABORATION / OWNERSHIP: Python EOS owns challenge issuance and contact
 *                            verification lifecycle; this Node service owns SMTP
 *                            transport capability only.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   v1.0.0-R10E15-RECOVERY-CONTACT-VERIFICATION-EMAIL-TRANSPORT — Establishes
 *   strict SMTP-only recovery-contact verification delivery, bounded inputs,
 *   no fake-success provider, no recipient/token logging, HTML escaping, and
 *   explicit provider confirmation.
 * COMPLIANCE: POPIA §19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Recipient and verification bearer exist only in
 *   the in-memory mail dispatch path and are never logged or persisted here.
 * TENANT BOUNDARY: No tenant identity, membership, or authorization is accepted.
 * AUTHORITY BOUNDARY: SMTP transport only; no recovery-contact, recovery,
 *   credential, login, MFA, session, role, membership, or tenant authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import nodemailer from 'nodemailer';

export class RecoveryContactVerificationEmailTransportError extends Error {
  constructor(code) {
    const safeCode = typeof code === 'string' && code
      ? code
      : 'RECOVERY_CONTACT_VERIFICATION_EMAIL_TRANSPORT_FAILED';
    super(safeCode);
    this.name = 'RecoveryContactVerificationEmailTransportError';
    this.code = safeCode;
  }
}

function normalizeEmail(value) {
  if (typeof value !== 'string') {
    throw new RecoveryContactVerificationEmailTransportError(
      'RECOVERY_CONTACT_VERIFICATION_EMAIL_INVALID',
    );
  }
  const email = value.trim().toLowerCase();
  const parts = email.split('@');
  if (
    !email
    || email.length > 320
    || parts.length !== 2
    || !parts[0]
    || !parts[1]
    || /\s/u.test(email)
  ) {
    throw new RecoveryContactVerificationEmailTransportError(
      'RECOVERY_CONTACT_VERIFICATION_EMAIL_INVALID',
    );
  }
  return email;
}

function normalizeVerificationToken(value) {
  if (
    typeof value !== 'string'
    || value.length < 32
    || value.length > 4096
    || /[\u0000-\u001f\u007f]/u.test(value)
  ) {
    throw new RecoveryContactVerificationEmailTransportError(
      'RECOVERY_CONTACT_VERIFICATION_TOKEN_INVALID',
    );
  }
  return value;
}

function normalizeExpiry(value) {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) {
    throw new RecoveryContactVerificationEmailTransportError(
      'RECOVERY_CONTACT_VERIFICATION_EXPIRY_INVALID',
    );
  }
  return date;
}

function smtpConfig(environment = process.env) {
  const host = String(environment.SMTP_HOST || '').trim();
  const user = String(environment.SMTP_USER || '').trim();
  const pass = String(environment.SMTP_PASS || '');
  const from = String(environment.EMAIL_FROM || environment.SMTP_FROM || '').trim();
  const port = Number(environment.SMTP_PORT || 587);
  const secure = String(environment.SMTP_SECURE || '').toLowerCase() === 'true';

  if (
    !host
    || !user
    || !pass
    || !from
    || !Number.isInteger(port)
    || port < 1
    || port > 65535
  ) {
    throw new RecoveryContactVerificationEmailTransportError(
      'RECOVERY_CONTACT_VERIFICATION_SMTP_UNAVAILABLE',
    );
  }
  return {
    host,
    port,
    secure,
    auth: { user, pass },
    from,
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export class RecoveryContactVerificationEmailTransport {
  constructor({
    transporterFactory = nodemailer.createTransport,
    environment = process.env,
  } = {}) {
    if (typeof transporterFactory !== 'function') {
      throw new TypeError('transporterFactory must be callable');
    }
    this.transporterFactory = transporterFactory;
    this.environment = environment;
  }

  /**
   * Deliver one already-issued email-possession verification challenge.
   *
   * @param {object} options - Transport-only delivery inputs.
   * @param {string} options.recipientEmail - Explicit proposed recovery address.
   * @param {string} options.verificationToken - Transient bearer issued by Python EOS.
   * @param {Date|string} options.expiresAt - Server-owned challenge expiry.
   * @returns {Promise<{status: 'DELIVERED'}>} Provider-confirmed transport receipt only.
   * @throws {RecoveryContactVerificationEmailTransportError} Code-only transport failure.
   * @authority This method grants no recovery-contact or credential authority.
   */
  async deliver({ recipientEmail, verificationToken, expiresAt }) {
    const recipient = normalizeEmail(recipientEmail);
    const token = normalizeVerificationToken(verificationToken);
    const expiry = normalizeExpiry(expiresAt);
    const config = smtpConfig(this.environment);
    const safeToken = escapeHtml(token);
    const safeExpiry = escapeHtml(expiry.toISOString());

    const text = [
      'Verify your WILSY OS recovery email address.',
      '',
      'Verification value: ' + token,
      'Expires: ' + expiry.toISOString(),
      '',
      'Enter this value only in the authenticated WILSY OS recovery-contact verification screen.',
      'If you did not request this change, do not share the value and contact your administrator.',
    ].join('\n');

    const html = [
      '<div style="font-family:Inter,Arial,sans-serif;background:#0a0c0d;color:#f7f4ec;padding:28px">',
      '<div style="color:#d5b04f;font-size:12px;font-weight:800;letter-spacing:.18em">WILSY OS</div>',
      '<h1 style="margin:18px 0 8px;font-size:24px">Verify recovery email</h1>',
      '<p style="color:#b8b6ae">Confirm possession of this address before it can receive password-recovery instructions.</p>',
      '<div style="margin-top:20px;font-size:11px;color:#8f918d;text-transform:uppercase;letter-spacing:.12em">Verification value</div>',
      '<div style="margin-top:8px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:18px;word-break:break-all;color:#f2d681">' + safeToken + '</div>',
      '<p style="margin-top:18px;color:#8f918d;font-size:12px">Expires: ' + safeExpiry + '</p>',
      '<p style="margin-top:24px;color:#8f918d;font-size:12px">Enter this value only in the authenticated WILSY OS recovery-contact verification screen. Never share it.</p>',
      '</div>',
    ].join('');

    try {
      const transporter = this.transporterFactory({
        host: config.host,
        port: config.port,
        secure: config.secure,
        auth: config.auth,
      });
      const result = await transporter.sendMail({
        from: config.from,
        to: recipient,
        subject: 'Verify your WILSY OS recovery email',
        text,
        html,
        headers: {
          'X-Wilsy-Message-Type': 'RECOVERY_CONTACT_VERIFICATION',
          'Auto-Submitted': 'auto-generated',
        },
      });
      if (!result || typeof result.messageId !== 'string' || !result.messageId.trim()) {
        throw new RecoveryContactVerificationEmailTransportError(
          'RECOVERY_CONTACT_VERIFICATION_SMTP_DELIVERY_UNCONFIRMED',
        );
      }
      return { status: 'DELIVERED' };
    } catch (error) {
      if (error instanceof RecoveryContactVerificationEmailTransportError) {
        throw error;
      }
      throw new RecoveryContactVerificationEmailTransportError(
        'RECOVERY_CONTACT_VERIFICATION_SMTP_DELIVERY_FAILED',
      );
    }
  }
}

export default new RecoveryContactVerificationEmailTransport();

/**
 * ARTIFACT: server/services/recoveryContactVerificationEmailTransport.js
 * VERSION: v1.0.0-R10E15-RECOVERY-CONTACT-VERIFICATION-EMAIL-TRANSPORT
 * AUTHORITY BOUNDARY: SMTP transport of already-issued recovery-contact verification bearer only
 * TENANT POSTURE: no tenant identity, membership, or authorization projection
 * FAIL-CLOSED POSTURE: missing configuration, invalid inputs, and unconfirmed SMTP delivery fail
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
