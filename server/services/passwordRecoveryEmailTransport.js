/**
 * WILSY OS — PASSWORD RECOVERY EMAIL TRANSPORT
 * VERSION: v1.0.0-R10E4-PASSWORD-RECOVERY-EMAIL-TRANSPORT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Delivers an already-issued one-time recovery bearer by SMTP without
 *          creating, validating, persisting, or interpreting recovery authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/passwordRecoveryEmailTransport.js
 * COLLABORATION / OWNERSHIP: Python EOS owns recovery issuance and lifecycle;
 *                            this Node service owns SMTP transport capability only.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v1.0.0-R10E4-PASSWORD-RECOVERY-EMAIL-TRANSPORT — Establishes strict SMTP-only
 *            password-recovery delivery with no development fake-success path,
 *            no recipient/token logging, bounded input validation, HTML escaping,
 *            and optional trusted reset-screen origin.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Recovery values exist only in the in-memory mail
 *                             payload and are never logged or persisted.
 * TENANT BOUNDARY: No tenant identity or membership is accepted or derived.
 * AUTHORITY BOUNDARY: Email transport only; no recovery, credential, auth, MFA,
 *                     session, role, membership, or tenant authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import nodemailer from 'nodemailer';

export class PasswordRecoveryEmailTransportError extends Error {
  constructor(code) {
    const safeCode = typeof code === 'string' && code ? code : 'PASSWORD_RECOVERY_EMAIL_TRANSPORT_FAILED';
    super(safeCode);
    this.name = 'PasswordRecoveryEmailTransportError';
    this.code = safeCode;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function normalizeEmail(value) {
  if (typeof value !== 'string') {
    throw new PasswordRecoveryEmailTransportError('RECOVERY_EMAIL_INVALID');
  }
  const email = value.trim().toLowerCase();
  const parts = email.split('@');
  if (
    !email
    || email.length > 320
    || parts.length !== 2
    || /\s/u.test(email)
    || !parts[0]
    || !parts[1]
    || !parts[1].includes('.')
  ) {
    throw new PasswordRecoveryEmailTransportError('RECOVERY_EMAIL_INVALID');
  }
  return email;
}

function normalizeRecoveryToken(value) {
  if (
    typeof value !== 'string'
    || value.length < 32
    || value.length > 4096
    || /\s/u.test(value)
  ) {
    throw new PasswordRecoveryEmailTransportError('RECOVERY_TOKEN_INVALID');
  }
  return value;
}

function normalizeExpiry(value) {
  const date = value instanceof Date ? new Date(value.getTime()) : new Date(value);
  if (Number.isNaN(date.getTime())) {
    throw new PasswordRecoveryEmailTransportError('RECOVERY_EXPIRY_INVALID');
  }
  return date;
}

function configuredOrigin() {
  const raw = String(process.env.WILSY_PUBLIC_APP_ORIGIN || '').trim();
  if (!raw) return null;
  try {
    const url = new URL(raw);
    if (
      !['https:', 'http:'].includes(url.protocol)
      || url.username
      || url.password
      || url.search
      || url.hash
      || url.pathname !== '/'
    ) {
      throw new Error('invalid origin');
    }
    return url.protocol + '//' + url.host;
  } catch {
    throw new PasswordRecoveryEmailTransportError('RECOVERY_PUBLIC_ORIGIN_INVALID');
  }
}

function smtpConfig() {
  const host = String(process.env.SMTP_HOST || '').trim();
  const user = String(process.env.SMTP_USER || '').trim();
  const pass = String(process.env.SMTP_PASS || '');
  const from = String(process.env.EMAIL_FROM || process.env.SMTP_FROM || '').trim();
  const port = Number(process.env.SMTP_PORT || 587);
  const secure = String(process.env.SMTP_SECURE || '').toLowerCase() === 'true';
  if (
    !host
    || !user
    || !pass
    || !from
    || !Number.isInteger(port)
    || port < 1
    || port > 65535
  ) {
    throw new PasswordRecoveryEmailTransportError('RECOVERY_SMTP_UNAVAILABLE');
  }
  return { host, port, secure, auth: { user, pass }, from };
}

export class PasswordRecoveryEmailTransport {
  constructor({ transporterFactory = nodemailer.createTransport } = {}) {
    if (typeof transporterFactory !== 'function') {
      throw new TypeError('transporterFactory must be callable');
    }
    this.transporterFactory = transporterFactory;
  }

  /**
   * Deliver one already-authorized recovery value by SMTP.
   * This method never stores the value, invents delivery success, or reports
   * recipient/token material in errors or logs.
   */
  async deliver({ recipientEmail, recoveryToken, expiresAt }) {
    const recipient = normalizeEmail(recipientEmail);
    const token = normalizeRecoveryToken(recoveryToken);
    const expiry = normalizeExpiry(expiresAt);
    const config = smtpConfig();
    const origin = configuredOrigin();
    const resetUrl = origin ? origin + '/reset-password' : null;
    const expiryIso = expiry.toISOString();
    const safeToken = escapeHtml(token);
    const safeExpiry = escapeHtml(expiryIso);
    const safeResetUrl = resetUrl ? escapeHtml(resetUrl) : null;

    const textLines = [
      'A password reset was requested for your WILSY OS account.',
      '',
      'One-time recovery value: ' + token,
      'Expires: ' + expiryIso,
      resetUrl ? 'Reset screen: ' + resetUrl : 'Return to WILSY OS and open the password reset screen.',
      '',
      'If you did not request this reset, you can ignore this message. Do not share the recovery value.',
    ];

    let html = '';
    html += '<div style="font-family:Inter,Arial,sans-serif;background:#0b0d0e;color:#f7f4ec;padding:32px;border:1px solid #d5b04f;border-radius:12px">';
    html += '<div style="color:#d5b04f;font-size:12px;font-weight:800;letter-spacing:.18em;text-transform:uppercase">WILSY OS</div>';
    html += '<h1 style="margin:18px 0 8px;font-size:24px">Password recovery</h1>';
    html += '<p style="color:#b8b6ae">A password reset was requested for your WILSY OS account.</p>';
    html += '<div style="margin:22px 0;padding:16px;background:#111315;border:1px solid #4d4f51;border-radius:8px">';
    html += '<div style="font-size:11px;color:#8f918d;text-transform:uppercase;letter-spacing:.12em">One-time recovery value</div>';
    html += '<div style="margin-top:8px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:18px;word-break:break-all;color:#f2d681">' + safeToken + '</div>';
    html += '</div>';
    html += '<p style="font-size:12px;color:#8f918d">Expires: ' + safeExpiry + '</p>';
    if (safeResetUrl) {
      html += '<p><a href="' + safeResetUrl + '" style="color:#d5b04f">Open the WILSY OS password reset screen</a></p>';
    }
    html += '<p style="margin-top:24px;color:#8f918d;font-size:12px">If you did not request this reset, ignore this message. Never share the recovery value.</p>';
    html += '</div>';

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
        subject: 'Reset your WILSY OS password',
        text: textLines.join('\n'),
        html,
        headers: {
          'X-Wilsy-Message-Type': 'PASSWORD_RECOVERY',
          'Auto-Submitted': 'auto-generated',
        },
      });
      if (!result || typeof result.messageId !== 'string' || !result.messageId) {
        throw new PasswordRecoveryEmailTransportError('RECOVERY_SMTP_DELIVERY_UNCONFIRMED');
      }
      return { status: 'DELIVERED' };
    } catch (error) {
      if (error instanceof PasswordRecoveryEmailTransportError) throw error;
      throw new PasswordRecoveryEmailTransportError('RECOVERY_SMTP_DELIVERY_FAILED');
    }
  }
}

export default new PasswordRecoveryEmailTransport();

/**
 * ARTIFACT: server/services/passwordRecoveryEmailTransport.js
 * VERSION: v1.0.0-R10E4-PASSWORD-RECOVERY-EMAIL-TRANSPORT
 * AUTHORITY BOUNDARY: SMTP transport of already-issued recovery bearer only
 * TENANT POSTURE: no tenant identity, membership, or authorization projection
 * FAIL-CLOSED POSTURE: missing configuration, invalid inputs, and unconfirmed SMTP delivery fail
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
