/**
 * ============================================================================
 * WILSY OS — RECOVERY CONTACT SECURITY PORTAL
 * ============================================================================
 * TITLE: Authenticated recovery-contact possession verification surface
 * VERSION: v1.0.0-R10E25-RECOVERY-CONTACT-SECURITY-UI
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Lets the current authenticated principal propose and verify one
 *           recovery email without browser-owned tenant/principal/VERIFIED truth.
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/RecoveryContactSecurityPortal.jsx
 * COLLABORATION / OWNERSHIP: Client API owns signed transport only; Python EOS
 * owns principal lifecycle, contact authority, verification challenge, and
 * PENDING-to-VERIFIED promotion; Node owns SMTP transport only.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   2026-09-22 v1.0.0-R10E25-RECOVERY-CONTACT-SECURITY-UI — Adds authenticated two-step recovery-contact
 *   verification with current-login-email convenience only, explicit editable
 *   address input, transient challenge state, bodyless 202/204 handling, and
 *   no browser tenant/principal/recovery-authority fields.
 * COMPLIANCE: POPIA §19, GDPR §32, SOC2 §CC7.2; client projection only.
 * SECURITY / PRIVACY POSTURE: Address and challenge values remain component
 * state only; challenge values are cleared after successful verification.
 * TENANT BOUNDARY: Protected ACCESS identity supplies tenant/principal binding.
 * AUTHORITY BOUNDARY: Presentation and signed transport invocation only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * ============================================================================
 */

import React, { useState } from 'react';
import {
  ArrowLeft,
  CheckCircle2,
  Loader2,
  MailCheck,
  ShieldCheck,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../contexts/authContext.jsx';
import {
  completeRecoveryContactVerification,
  requestRecoveryContactVerification,
} from '../../services/api.js';
import TenantIdentityCard from './TenantIdentityCard.jsx';

const messageForFailure = (status) => {
  if (status === 400 || status === 422) {
    return 'The verification request is invalid or expired. Check the values and try again.';
  }
  if (status === 403) {
    return 'Recovery-contact verification is not available for this authenticated identity.';
  }
  if (status === 409) {
    return 'A verified recovery contact is already bound. Replacing it requires a separate security action.';
  }
  if (status === 503) {
    return 'Recovery-contact verification is temporarily unavailable. Please try again later.';
  }
  return 'We could not complete recovery-contact verification. Please try again later.';
};

export default function RecoveryContactSecurityPortal() {
  const navigate = useNavigate();
  const { user, tenant } = useAuth();

  const initialAddress = typeof user?.email === 'string' ? user.email.trim() : '';
  const [address, setAddress] = useState(initialAddress);
  const [verificationToken, setVerificationToken] = useState('');
  const [phase, setPhase] = useState('request');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');

  const requestChallenge = async (event) => {
    event.preventDefault();
    if (pending) return;

    setError('');
    const proposed = address.trim();
    if (!proposed) {
      setError('Enter the recovery email address you want to verify.');
      return;
    }

    setPending(true);
    try {
      const response = await requestRecoveryContactVerification({ address: proposed });
      if (response?.status !== 202) {
        setError(messageForFailure(undefined));
        return;
      }
      setPhase('verify');
    } catch (requestError) {
      setError(messageForFailure(requestError?.response?.status));
    } finally {
      setPending(false);
    }
  };

  const completeChallenge = async (event) => {
    event.preventDefault();
    if (pending) return;

    setError('');
    const token = verificationToken.trim();
    if (!token) {
      setError('Enter the one-time verification value from the recovery email.');
      return;
    }

    setPending(true);
    try {
      const response = await completeRecoveryContactVerification({
        verificationToken: token,
      });
      if (response?.status !== 204) {
        setError(messageForFailure(undefined));
        return;
      }
      setVerificationToken('');
      setPhase('complete');
    } catch (completionError) {
      setError(messageForFailure(completionError?.response?.status));
    } finally {
      setPending(false);
    }
  };

  return (
    <main style={pageStyle}>
      <section style={panelStyle} aria-labelledby="recovery-contact-title" data-testid="recovery-contact-security-portal">
        <div style={brandRow}>
          <ShieldCheck size={22} color="#d5b04f" aria-hidden="true" />
          <span>WILSY OS</span>
        </div>

        <h1 id="recovery-contact-title" style={titleStyle}>Recovery contact</h1>
        <p style={copyStyle}>
          Establish a verified email address for account recovery. This address is independent recovery authority and is never inferred from login metadata.
        </p>

        <div style={contentGridStyle}>
          <div style={evidenceColumnStyle}>
            {tenant ? (
              <section aria-label="Current workspace" style={workspaceContextStyle}>
                <TenantIdentityCard tenant={tenant} integrated />
                <p style={workspaceHelpStyle}>
                  Verification is bound by the server to your current authenticated workspace and principal.
                </p>
              </section>
            ) : null}

            <section style={securityBriefStyle} aria-labelledby="security-brief-title">
              <div style={briefHeadingStyle}>
                <MailCheck size={17} aria-hidden="true" />
                <h2 id="security-brief-title" style={sectionTitleStyle}>Email possession proof</h2>
              </div>
              <p style={helpStyle}>
                WILSY OS sends a one-time value to the proposed address. The address becomes recovery authority only after that value is consumed successfully.
              </p>
            </section>
          </div>

          <div style={formColumnStyle}>
            {phase === 'request' ? (
              <form onSubmit={requestChallenge} aria-busy={pending} style={formStyle}>
                <label htmlFor="recovery-contact-address" style={labelStyle}>Recovery email</label>
                <input
                  id="recovery-contact-address"
                  name="address"
                  type="email"
                  autoComplete="email"
                  value={address}
                  onChange={(event) => setAddress(event.target.value)}
                  style={inputStyle}
                  required
                />
                <p style={helpStyle}>
                  You may use your login email or a different address you control. Verification is always required.
                </p>

                {error && <div role="alert" aria-live="assertive" style={errorStyle}>{error}</div>}

                <button type="submit" disabled={pending} style={primaryButtonStyle}>
                  {pending ? <Loader2 size={18} className="animate-spin" aria-hidden="true" /> : null}
                  <span>{pending ? 'Sending verification…' : 'Verify recovery email'}</span>
                </button>
              </form>
            ) : null}

            {phase === 'verify' ? (
              <form onSubmit={completeChallenge} aria-busy={pending} style={formStyle}>
                <div style={statusRowStyle}>
                  <MailCheck size={18} aria-hidden="true" />
                  <span>If verification is required, check the proposed address for a one-time value.</span>
                </div>

                <label htmlFor="recovery-contact-token" style={labelStyle}>Verification value</label>
                <input
                  id="recovery-contact-token"
                  name="verificationToken"
                  type="password"
                  autoComplete="one-time-code"
                  value={verificationToken}
                  onChange={(event) => setVerificationToken(event.target.value)}
                  style={inputStyle}
                  required
                />
                <p style={helpStyle}>The verification value is used once and is never stored by this browser surface.</p>

                {error && <div role="alert" aria-live="assertive" style={errorStyle}>{error}</div>}

                <button type="submit" disabled={pending} style={primaryButtonStyle}>
                  {pending ? <Loader2 size={18} className="animate-spin" aria-hidden="true" /> : null}
                  <span>{pending ? 'Verifying…' : 'Confirm recovery email'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setVerificationToken('');
                    setError('');
                    setPhase('request');
                  }}
                  style={linkButtonStyle}
                >
                  Use a different address
                </button>
              </form>
            ) : null}

            {phase === 'complete' ? (
              <section role="status" aria-live="polite" style={successPanelStyle}>
                <CheckCircle2 size={22} aria-hidden="true" />
                <div>
                  <h2 style={successTitleStyle}>Recovery contact verified</h2>
                  <p style={successCopyStyle}>
                    Python EOS confirmed the possession challenge and promoted this recovery contact to VERIFIED authority.
                  </p>
                </div>
              </section>
            ) : null}

            <button
              type="button"
              onClick={() => navigate('/', { replace: true })}
              style={backButtonStyle}
            >
              <ArrowLeft size={16} aria-hidden="true" /> Back to workspace
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}

const pageStyle = {
  minHeight: '100dvh',
  width: '100%',
  boxSizing: 'border-box',
  display: 'grid',
  justifyItems: 'center',
  alignItems: 'start',
  padding: 'clamp(24px, 3.2vh, 32px) clamp(18px, 3vw, 48px) max(clamp(48px, 7vh, 80px), calc(env(safe-area-inset-bottom) + 28px))',
  overflowX: 'hidden',
  overflowY: 'auto',
  background: 'radial-gradient(circle at 50% 12%, rgba(213,176,79,.06), transparent 34%), #0a0c0d',
  color: '#f7f4ec',
  fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
};

const panelStyle = {
  width: 'min(100%, 1080px)',
  boxSizing: 'border-box',
  padding: 'clamp(24px, 3vh, 30px) clamp(24px, 4vh, 38px) 24px',
  background: 'linear-gradient(145deg, rgba(25,28,29,.99), rgba(15,17,18,.995))',
  border: '1px solid rgba(213,176,79,.30)',
  borderRadius: '18px',
  boxShadow: '0 36px 100px rgba(0,0,0,.58), inset 0 0 0 1px rgba(255,255,255,.018)',
};

const brandRow = {
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  paddingBottom: '12px',
  marginBottom: '18px',
  color: '#d5b04f',
  fontSize: '12px',
  letterSpacing: '.20em',
  fontWeight: 800,
  borderBottom: '1px solid rgba(255,255,255,.065)',
};

const titleStyle = {
  margin: '0 0 8px',
  fontSize: 'clamp(28px, 4vh, 36px)',
  lineHeight: 1.04,
  letterSpacing: '-.035em',
  fontWeight: 720,
};

const copyStyle = {
  margin: '0 0 18px',
  color: '#a5a7a2',
  fontSize: '13px',
  lineHeight: 1.55,
};

const contentGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 320px), 1fr))',
  alignItems: 'start',
  gap: 'clamp(28px, 5vw, 64px)',
};

const evidenceColumnStyle = {
  display: 'grid',
  alignContent: 'start',
  gap: '22px',
  minWidth: 0,
};

const formColumnStyle = { minWidth: 0 };

const workspaceContextStyle = {
  padding: '18px 20px',
  border: '1px solid rgba(213,176,79,.22)',
  borderRadius: '10px',
  background: 'rgba(37,38,38,.52)',
};

const workspaceHelpStyle = {
  margin: '14px 0 0',
  color: '#8f918d',
  fontSize: '11px',
  lineHeight: 1.45,
};

const securityBriefStyle = {
  paddingTop: '18px',
  borderTop: '1px solid rgba(255,255,255,.08)',
};

const briefHeadingStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  marginBottom: '8px',
  color: '#d5b04f',
};

const sectionTitleStyle = {
  margin: 0,
  color: '#d8d4c9',
  fontSize: '14px',
  fontWeight: 700,
};

const formStyle = {
  display: 'grid',
  gap: '8px',
  width: '100%',
};

const labelStyle = {
  marginTop: '6px',
  color: '#d8d4c9',
  fontSize: '12px',
  fontWeight: 650,
};

const inputStyle = {
  width: '100%',
  boxSizing: 'border-box',
  padding: '12px 14px',
  borderRadius: '8px',
  border: '1px solid #4d4f51',
  background: '#0f1011',
  color: '#fff',
  fontSize: '16px',
  outlineColor: '#d5b04f',
};

const helpStyle = {
  margin: '-2px 0 0',
  color: '#777a76',
  fontSize: '11px',
  lineHeight: 1.45,
};

const primaryButtonStyle = {
  display: 'inline-flex',
  justifyContent: 'center',
  alignItems: 'center',
  gap: '9px',
  minHeight: '46px',
  marginTop: '10px',
  padding: '12px 18px',
  border: 0,
  borderRadius: '8px',
  background: '#d5b04f',
  color: '#141414',
  fontWeight: 750,
  fontSize: '14px',
  cursor: 'pointer',
};

const linkButtonStyle = {
  justifySelf: 'start',
  marginTop: '6px',
  padding: '2px 0',
  border: 0,
  background: 'none',
  color: '#d5b04f',
  fontSize: '12px',
  fontWeight: 650,
  textDecoration: 'underline',
  textUnderlineOffset: '3px',
  cursor: 'pointer',
};

const backButtonStyle = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '7px',
  marginTop: '16px',
  padding: 0,
  border: 0,
  background: 'none',
  color: '#bbb8ae',
  cursor: 'pointer',
};

const errorStyle = {
  marginTop: '8px',
  padding: '10px 12px',
  border: '1px solid rgba(255,181,181,.24)',
  borderRadius: '8px',
  color: '#ffb5b5',
  fontSize: '13px',
  lineHeight: 1.45,
};

const statusRowStyle = {
  display: 'flex',
  gap: '8px',
  alignItems: 'flex-start',
  marginBottom: '8px',
  color: '#c9e7d5',
  fontSize: '12px',
  lineHeight: 1.45,
};

const successPanelStyle = {
  display: 'flex',
  gap: '12px',
  alignItems: 'flex-start',
  padding: '18px',
  border: '1px solid rgba(185,233,199,.18)',
  borderRadius: '10px',
  background: 'rgba(30,52,38,.18)',
  color: '#b9e9c7',
};

const successTitleStyle = {
  margin: '0 0 8px',
  color: '#f7f4ec',
  fontSize: '18px',
};

const successCopyStyle = {
  margin: 0,
  color: '#a9b8ad',
  fontSize: '13px',
  lineHeight: 1.55,
};

/**
 * ============================================================================
 * SOVEREIGN ARTIFACT SEAL
 * ============================================================================
 * ARTIFACT: Authenticated recovery-contact possession verification surface
 * VERSION: v1.0.0-R10E25-RECOVERY-CONTACT-SECURITY-UI
 * AUTHORITY BOUNDARY: Presentation and signed verification transport only
 * TENANT POSTURE: Tenant/principal identity derives only from authenticated server state
 * FAIL-CLOSED POSTURE: Only server-confirmed HTTP 204 projects VERIFIED success
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ============================================================================
 */
