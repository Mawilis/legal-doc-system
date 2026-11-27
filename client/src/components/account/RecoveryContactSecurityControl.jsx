/**
 * ============================================================================
 * WILSY OS — RECOVERY CONTACT SECURITY CONTROL
 * ============================================================================
 * TITLE: Authenticated recovery-email verification control
 * VERSION: v1.3.1-SOVEREIGN-HEADER-CONFORMANCE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Lets an authenticated user request verification of the current
 *           durable recovery email without letting the browser nominate an
 *           address, tenant, principal, token, or verified state.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/account/RecoveryContactSecurityControl.jsx
 * COLLABORATION / OWNERSHIP: api.js owns authenticated transport; Python EOS
 *   re-reads durable principal/email and owns verification/contact authority.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   2026-11-27 v1.3.1-SOVEREIGN-HEADER-CONFORMANCE corrects the canonical path header declaration required by repository integrity; recovery contact runtime semantics remain unchanged.
 *   2026-11-27 v1.3.0 names an EOS-confirmed recovery contact Verified recovery email; all unknown, required and unavailable states retain neutral Recovery email.
 *   2026-11-27 v1.2.0 distinguishes absent EOS routes, authentication and bounded source stages and permits a read-only retry without sending email.
 *   2026-11-27 v1.1.0 reads authenticated status before enabling email issuance, suppresses redundant verification and preserves source-unavailable as a separate state.
 *   2026-09-22 v1.3.0-VERIFIED-RECOVERY-PLAIN-LANGUAGE — Adds
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

import React, { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, MailCheck, ShieldCheck } from 'lucide-react';
import { getRecoveryContactStatus, requestRecoveryContactVerification } from '../../services/api.js';

const messageForFailure = (status) => {
  if (status === 429) return 'Verification requests are temporarily rate-limited.';
  if (status === 401 || status === 403) return 'Sign in again before managing recovery security.';
  return 'Recovery-email verification is temporarily unavailable.';
};

export default function RecoveryContactSecurityControl({ email = '', compact = false }) {
  const [pending, setPending] = useState(false);
  const [state, setState] = useState('loading');
  const [error, setError] = useState('');
  const [readRevision, setReadRevision] = useState(0);
  const [statusIssue, setStatusIssue] = useState('');

  // Reading existing verified contact is idempotent: never issues SMTP tokens.
  useEffect(() => {
    let current = true;
    setState('loading');
    setStatusIssue('');
    getRecoveryContactStatus().then((response) => {
      if (!current) return;
      const status = response?.data?.status;
      setState(status === 'VERIFIED' ? 'verified'
        : status === 'VERIFICATION_REQUIRED' ? 'required' : 'unavailable');
      if (!['VERIFIED', 'VERIFICATION_REQUIRED'].includes(status)) {
        setStatusIssue('Unexpected EOS status response.');
      }
    }).catch((failure) => {
      if (!current) return;
      const status = failure?.response?.status;
      const stage = failure?.response?.headers?.['x-wilsy-recovery-status-stage'];
      if (status === 404 || status === 405) {
        setStatusIssue('The current EOS process does not expose the recovery status route. Restart Python EOS with the updated code.');
      } else if (status === 401 || status === 403) {
        setStatusIssue('EOS could not authenticate this request. Reauthenticate through the current Global Principal session.');
      } else if (status === 503 && ['PRINCIPAL_SOURCE', 'CONTACT_SOURCE', 'DURABLE_EMAIL', 'SOURCE_UNAVAILABLE'].includes(stage)) {
        setStatusIssue('EOS readback failed at: ' + stage.replaceAll('_', ' ').toLowerCase() + '.');
      } else if (status === 503) {
        setStatusIssue('EOS reported a source failure without a diagnostic stage.');
      } else {
        setStatusIssue('EOS status read could not be completed.');
      }
      setState('unavailable');
    });
    return () => { current = false; };
  }, [readRevision]);


  const requestVerification = async () => {
    if (pending || state !== 'required') return;
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
          <strong style={titleStyle}>{state === 'verified' ? 'Verified recovery email' : 'Recovery email'}</strong>
        </div>
      </div>

      {resolvedEmail ? (
        <p style={emailStyle}>{resolvedEmail}</p>
      ) : (
        <p style={copyStyle}>Your current account email will be verified by the server.</p>
      )}

      {state === 'loading' && <p role="status" style={copyStyle}>Checking recovery email status with EOS…</p>}
      {state === 'unavailable' && <>
        <p role="alert" style={errorStyle}>Recovery email status unavailable. {statusIssue} Existing verification evidence has not been changed.</p>
        <button type="button" style={buttonStyle} onClick={() => setReadRevision((value) => value + 1)}>Retry status read</button>
      </>}
      {state === 'required' && <p role="status" style={copyStyle}>No matching verified recovery contact for the current EOS email.</p>}
      {state === 'verified' && (
        <div role="status" style={statusStyle}>
          <ShieldCheck size={16} aria-hidden="true" />
          <span>Email ownership confirmed by EOS.</span>
        </div>
      )}

      {state === 'sent' && (
        <div role="status" style={statusStyle}>
          <CheckCircle2 size={16} aria-hidden="true" />
          <span>Verification sent. Open the secure email link to finish.</span>
        </div>
      )}

      {error && <p role="alert" style={errorStyle}>{error}</p>}

      {state === 'required' && <button
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
      </button>}
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
 * VERSION: v1.3.1-SOVEREIGN-HEADER-CONFORMANCE
 * AUTHORITY BOUNDARY: authenticated client transport/presentation only
 * TENANT POSTURE: no browser tenant/email authority submitted
 * FAIL-CLOSED POSTURE: only bounded server status updates presentation
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ============================================================================
 */
