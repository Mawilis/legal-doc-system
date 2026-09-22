/**
 * ============================================================================
 * WILSY OS — RECOVERY CONTACT SECURITY CONTROL
 * ============================================================================
 * TITLE: Authenticated recovery-email verification control
 * VERSION: v1.0.0-R10E26-RECOVERY-CONTACT-SECURITY-CONTROL
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Lets an authenticated user request verification of the current
 *           durable recovery email without letting the browser nominate an
 *           address, tenant, principal, token, or verified state.
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/account/RecoveryContactSecurityControl.jsx
 * COLLABORATION / OWNERSHIP: api.js owns authenticated transport; Python EOS
 *   re-reads durable principal/email and owns verification/contact authority.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   2026-09-22 v1.0.0-R10E26-RECOVERY-CONTACT-SECURITY-CONTROL — Adds
 *   pending suppression, verification-sent/already-verified states, bounded
 *   429/503 copy, and display-only current-email context.
 * COMPLIANCE: POPIA §19, GDPR §32, SOC2 §CC7.2.
 * SECURITY / PRIVACY POSTURE: The displayed email is never sent by this
 *   component; the authenticated Python endpoint derives durable email truth.
 * TENANT BOUNDARY: Browser sends no tenant selector for verification request.
 * AUTHORITY BOUNDARY: Presentation and authenticated transport invocation only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * ============================================================================
 */

import React, { useState } from 'react';
import { CheckCircle2, Loader2, MailCheck, ShieldCheck } from 'lucide-react';
import { requestRecoveryContactVerification } from '../../services/api.js';

const messageForFailure = (status) => {
  if (status === 429) return 'Verification requests are temporarily rate-limited.';
  if (status === 401 || status === 403) return 'Sign in again before managing recovery security.';
  return 'Recovery-email verification is temporarily unavailable.';
};

export default function RecoveryContactSecurityControl({ email = '', compact = false }) {
  const [pending, setPending] = useState(false);
  const [state, setState] = useState('idle');
  const [error, setError] = useState('');

  const requestVerification = async () => {
    if (pending) return;
    setError('');
    setPending(true);
    try {
      const response = await requestRecoveryContactVerification();
      const status = response?.data?.status;
      if (response?.status !== 202) {
        setError(messageForFailure(undefined));
        return;
      }
      if (status === 'VERIFICATION_NOT_REQUIRED') {
        setState('verified');
        return;
      }
      if (status === 'VERIFICATION_SENT') {
        setState('sent');
        return;
      }
      setError(messageForFailure(undefined));
    } catch (requestError) {
      setError(messageForFailure(requestError?.response?.status));
    } finally {
      setPending(false);
    }
  };

  const resolvedEmail = typeof email === 'string' ? email.trim() : '';

  return (
    <section
      style={compact ? compactShellStyle : shellStyle}
      aria-label="Password recovery security"
      data-testid="recovery-contact-security-control"
    >
      <div style={headingStyle}>
        <MailCheck size={compact ? 18 : 22} aria-hidden="true" />
        <div>
          <small style={eyebrowStyle}>Password recovery</small>
          <strong style={titleStyle}>Recovery email</strong>
        </div>
      </div>

      {resolvedEmail ? (
        <p style={emailStyle}>{resolvedEmail}</p>
      ) : (
        <p style={copyStyle}>Your current account email will be verified by the server.</p>
      )}

      {state === 'verified' && (
        <div role="status" style={statusStyle}>
          <ShieldCheck size={16} aria-hidden="true" />
          <span>Current recovery email is already verified.</span>
        </div>
      )}

      {state === 'sent' && (
        <div role="status" style={statusStyle}>
          <CheckCircle2 size={16} aria-hidden="true" />
          <span>Verification sent. Open the secure email link to finish.</span>
        </div>
      )}

      {error && <p role="alert" style={errorStyle}>{error}</p>}

      <button
        type="button"
        onClick={requestVerification}
        disabled={pending}
        style={buttonStyle}
      >
        {pending ? <Loader2 size={16} className="animate-spin" aria-hidden="true" /> : null}
        <span>
          {pending
            ? 'Sending verification…'
            : state === 'verified'
              ? 'Recheck recovery email'
              : 'Verify recovery email'}
        </span>
      </button>
    </section>
  );
}

const shellStyle = {
  display: 'grid',
  gap: '10px',
  minHeight: '160px',
  padding: '16px',
  border: '1px solid rgba(213,176,79,.24)',
  borderRadius: '16px',
  background: 'linear-gradient(145deg, rgba(30,35,38,.72), rgba(15,18,20,.76))',
};

const compactShellStyle = {
  ...shellStyle,
  minHeight: 0,
  padding: '14px',
  borderRadius: '12px',
};

const headingStyle = { display: 'flex', alignItems: 'center', gap: '10px', color: '#d5b04f' };
const eyebrowStyle = { display: 'block', color: '#9e9f9a', fontSize: '9px', letterSpacing: '.14em', textTransform: 'uppercase' };
const titleStyle = { display: 'block', marginTop: '2px', color: '#f7f4ec', fontSize: '14px' };
const emailStyle = { margin: 0, color: '#c9c5ba', fontSize: '12px', overflowWrap: 'anywhere' };
const copyStyle = { margin: 0, color: '#969892', fontSize: '11px', lineHeight: 1.45 };
const statusStyle = { display: 'flex', alignItems: 'center', gap: '7px', color: '#b9e9c7', fontSize: '11px', lineHeight: 1.4 };
const errorStyle = { margin: 0, color: '#ffb5b5', fontSize: '11px', lineHeight: 1.4 };
const buttonStyle = {
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: '7px',
  minHeight: '38px',
  padding: '9px 12px',
  border: '1px solid rgba(213,176,79,.45)',
  borderRadius: '9px',
  background: 'rgba(213,176,79,.12)',
  color: '#f0d57d',
  fontWeight: 750,
  fontSize: '11px',
  cursor: 'pointer',
};

/**
 * ============================================================================
 * SOVEREIGN ARTIFACT SEAL
 * ============================================================================
 * ARTIFACT: RecoveryContactSecurityControl.jsx
 * VERSION: v1.0.0-R10E26-RECOVERY-CONTACT-SECURITY-CONTROL
 * AUTHORITY BOUNDARY: authenticated client transport/presentation only
 * TENANT POSTURE: no browser tenant/email authority submitted
 * FAIL-CLOSED POSTURE: only bounded server status updates presentation
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ============================================================================
 */
