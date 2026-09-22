/**
 * ============================================================================
 * WILSY OS — PASSWORD RECOVERY REQUEST PORTAL
 * ============================================================================
 * TITLE: Browser Forgot Password initiation surface
 * VERSION: v1.0.0-R10E21-PASSWORD-RECOVERY-REQUEST-UI
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Accepts a workspace/email selector, invokes the enumeration-safe
 *           recovery-request transport, and projects only a generic acknowledgement.
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/PasswordRecoveryPortal.jsx
 * COLLABORATION / OWNERSHIP: requestPasswordReset owns browser transport only;
 * Python EOS owns principal admission, verified recovery contact authority,
 * capability issuance, cooldown, persistence, and delivery.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   2026-09-22 v1.0.0-R10E21-PASSWORD-RECOVERY-REQUEST-UI — Adds a bounded unauthenticated Forgot Password
 *   request experience with selected-workspace reuse, direct-entry fallback,
 *   generic 202 acknowledgement, duplicate-submit protection, and no recovery
 *   secret, account-existence, or delivery-outcome projection.
 * COMPLIANCE: POPIA §19, GDPR §32, SOC2 §CC7.2; client projection only.
 * SECURITY / PRIVACY POSTURE: Email remains component state and is never logged,
 *   persisted by this component, or projected after submission beyond masked copy.
 * TENANT BOUNDARY: Selected workspace is a lookup selector only; the browser
 *   never grants tenant, principal, recovery-contact, or credential authority.
 * AUTHORITY BOUNDARY: Presentation and certified transport invocation only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * ============================================================================
 */

import React, { useState } from 'react';
import { ArrowLeft, CheckCircle2, Loader2, Mail, ShieldCheck } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '../../contexts/authContext.jsx';
import { requestPasswordReset } from '../../services/api.js';
import TenantIdentityCard from './TenantIdentityCard.jsx';

const genericAcknowledgement =
  'If an eligible account with a verified recovery email exists for this workspace, WILSY OS has sent recovery instructions.';

const recoveryRequestFailureMessage = (status) => {
  if (status === 422) {
    return 'Check the workspace and email values, then try again.';
  }
  if (status === 503) {
    return 'Password recovery is temporarily unavailable. Please try again later.';
  }
  return 'We could not submit the recovery request. Please try again later.';
};

export default function PasswordRecoveryPortal() {
  const navigate = useNavigate();
  const location = useLocation();
  const { tenant: selectedTenant } = useAuth();

  const contextTenantId = typeof selectedTenant?.tenantId === 'string'
    ? selectedTenant.tenantId.trim()
    : '';
  const initialEmail = typeof location.state?.email === 'string'
    ? location.state.email.trim()
    : '';

  const [manualTenantId, setManualTenantId] = useState('');
  const [email, setEmail] = useState(initialEmail);
  const [pending, setPending] = useState(false);
  const [accepted, setAccepted] = useState(false);
  const [error, setError] = useState('');

  const tenantId = contextTenantId || manualTenantId.trim();
  const hasSelectedWorkspace = Boolean(contextTenantId);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (pending || accepted) return;

    setError('');
    const normalizedEmail = email.trim();
    if (!tenantId || !normalizedEmail) {
      setError('Enter the workspace and work email to continue.');
      return;
    }

    setPending(true);
    try {
      const response = await requestPasswordReset({
        tenantId,
        email: normalizedEmail,
      });
      if (response?.status !== 202) {
        setError(recoveryRequestFailureMessage(undefined));
        return;
      }
      setAccepted(true);
    } catch (requestError) {
      setError(recoveryRequestFailureMessage(requestError?.response?.status));
    } finally {
      setPending(false);
    }
  };

  return (
    <main style={pageStyle}>
      <section style={panelStyle} aria-labelledby="recovery-title" data-testid="password-recovery-portal">
        <div style={brandRow}>
          <ShieldCheck size={22} color="#d5b04f" aria-hidden="true" />
          <span>WILSY OS</span>
        </div>

        <h1 id="recovery-title" style={titleStyle}>Recover access</h1>
        <p style={copyStyle}>
          Request password recovery for your institutional workspace.
        </p>

        <div style={contentGridStyle}>
          <div style={evidenceColumnStyle}>
            {hasSelectedWorkspace ? (
              <section aria-label="Selected workspace" style={workspaceContextStyle}>
                <TenantIdentityCard tenant={selectedTenant} integrated />
                <p style={workspaceHelpStyle}>
                  Recovery will be requested only for the workspace selected during discovery.
                </p>
              </section>
            ) : (
              <section aria-label="Workspace selection" style={workspaceFallbackStyle}>
                <label htmlFor="recovery-tenant" style={labelStyle}>Workspace ID</label>
                <input
                  id="recovery-tenant"
                  name="tenantId"
                  type="text"
                  autoComplete="organization"
                  value={manualTenantId}
                  onChange={(event) => setManualTenantId(event.target.value)}
                  style={inputStyle}
                  required
                />
                <p style={helpStyle}>Use the workspace ID from workspace discovery.</p>
                <button
                  type="button"
                  onClick={() => navigate('/discovery', { replace: true })}
                  style={linkButtonStyle}
                >
                  Find your workspace
                </button>
              </section>
            )}

            <section style={privacyBriefStyle} aria-labelledby="privacy-title">
              <div style={briefHeadingStyle}>
                <Mail size={17} aria-hidden="true" />
                <h2 id="privacy-title" style={sectionTitleStyle}>Private recovery</h2>
              </div>
              <p style={helpStyle}>
                For security, WILSY OS does not reveal whether an account exists or whether recovery instructions were delivered.
              </p>
            </section>
          </div>

          <div style={formColumnStyle}>
            {accepted ? (
              <section role="status" aria-live="polite" style={successPanelStyle}>
                <CheckCircle2 size={22} aria-hidden="true" />
                <div>
                  <h2 style={successTitleStyle}>Check your recovery email</h2>
                  <p style={successCopyStyle}>{genericAcknowledgement}</p>
                  <div style={successActionsStyle}>
                    <button
                      type="button"
                      onClick={() => navigate('/login', { replace: true })}
                      style={secondaryButtonStyle}
                    >
                      <ArrowLeft size={16} aria-hidden="true" /> Back to sign in
                    </button>
                    <button
                      type="button"
                      onClick={() => navigate('/reset-password')}
                      style={linkButtonStyle}
                    >
                      I already have recovery information
                    </button>
                  </div>
                </div>
              </section>
            ) : (
              <>
                <form onSubmit={handleSubmit} aria-busy={pending} style={formStyle}>
                  <label htmlFor="recovery-email" style={labelStyle}>Work email</label>
                  <input
                    id="recovery-email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    style={inputStyle}
                    required
                  />
                  <p style={helpStyle}>
                    Use the email associated with your access to this workspace.
                  </p>

                  {error && (
                    <div role="alert" aria-live="assertive" style={errorStyle}>
                      {error}
                    </div>
                  )}

                  <button type="submit" disabled={pending} style={primaryButtonStyle}>
                    {pending ? <Loader2 size={18} className="animate-spin" aria-hidden="true" /> : null}
                    <span>{pending ? 'Requesting recovery…' : 'Send recovery instructions'}</span>
                  </button>
                </form>

                <button
                  type="button"
                  onClick={() => navigate('/login', { replace: true })}
                  style={secondaryButtonStyle}
                >
                  <ArrowLeft size={16} aria-hidden="true" /> Back to sign in
                </button>
              </>
            )}
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
  color: '#fbf9f3',
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

const workspaceFallbackStyle = {
  display: 'grid',
  gap: '8px',
};

const privacyBriefStyle = {
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

const secondaryButtonStyle = {
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

const linkButtonStyle = {
  justifySelf: 'start',
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

const errorStyle = {
  marginTop: '8px',
  padding: '10px 12px',
  border: '1px solid rgba(255,181,181,.24)',
  borderRadius: '8px',
  color: '#ffb5b5',
  fontSize: '13px',
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
  lineHeight: 1.2,
};

const successCopyStyle = {
  margin: 0,
  color: '#a9b8ad',
  fontSize: '13px',
  lineHeight: 1.55,
};

const successActionsStyle = {
  display: 'grid',
  justifyItems: 'start',
  gap: '8px',
  marginTop: '8px',
};

/**
 * ============================================================================
 * SOVEREIGN ARTIFACT SEAL
 * ============================================================================
 * ARTIFACT: Browser Forgot Password initiation surface
 * VERSION: v1.0.0-R10E21-PASSWORD-RECOVERY-REQUEST-UI
 * AUTHORITY BOUNDARY: Presentation and public recovery-request transport only
 * TENANT POSTURE: Workspace value is forwarded as a lookup selector, never granted
 * FAIL-CLOSED POSTURE: No account existence or delivery outcome is projected
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ============================================================================
 */
