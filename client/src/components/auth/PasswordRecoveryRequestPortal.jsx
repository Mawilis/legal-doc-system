/**
 * ============================================================================
 * WILSY OS — PASSWORD RECOVERY REQUEST PORTAL
 * ============================================================================
 * TITLE: Browser password-recovery initiation surface
 * VERSION: v1.0.0-R10E10-PASSWORD-RECOVERY-REQUEST-UI
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Collects one workspace/email recovery request and delegates all
 *           contact verification, rate limiting, capability issuance, and
 *           delivery truth to the certified Python-backed client method.
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/PasswordRecoveryRequestPortal.jsx
 * COLLABORATION / OWNERSHIP: AuthContext supplies the server-backed selected
 *   workspace projection; api.js owns transport; Python EOS owns recovery
 *   contact, rate-limit, issuance, and delivery orchestration.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   2026-09-22 v1.0.0-R10E10-PASSWORD-RECOVERY-REQUEST-UI — Adds an
 *   unauthenticated, enumeration-safe recovery-request form with selected
 *   workspace reuse, direct-entry fallback, generic 202 acknowledgement,
 *   bounded 429 handling, duplicate-submit suppression, and no token input.
 * COMPLIANCE: POPIA §19, GDPR §32, SOC2 §CC7.2; client projection only.
 * SECURITY / PRIVACY POSTURE: Email remains component state and transport input;
 *   no recovery token, credential, session, storage, telemetry, or URL state.
 * TENANT BOUNDARY: Selected workspace supplies only the tenant lookup selector;
 *   direct entry remains available when no selected workspace exists.
 * AUTHORITY BOUNDARY: Presentation and certified transport invocation only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * ============================================================================
 */

import React, { useState } from 'react';
import { AlertCircle, ArrowLeft, CheckCircle2, Loader2, ShieldCheck } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/authContext.jsx';
import { requestPasswordRecovery } from '../../services/api.js';
import TenantIdentityCard from './TenantIdentityCard.jsx';

const failureMessage = (status) => {
  if (status === 429) {
    return 'Too many recovery requests. Please wait before trying again.';
  }
  if (status === 422) {
    return 'Check the workspace and work email, then try again.';
  }
  return 'Password recovery is temporarily unavailable. Please try again later.';
};

export default function PasswordRecoveryRequestPortal() {
  const navigate = useNavigate();
  const location = useLocation();
  const { tenant: selectedTenant } = useAuth();
  const contextTenantId = typeof selectedTenant?.tenantId === 'string'
    ? selectedTenant.tenantId.trim()
    : '';
  const initialEmail = typeof location.state?.email === 'string'
    ? location.state.email
    : '';
  const [manualTenantId, setManualTenantId] = useState('');
  const [email, setEmail] = useState(initialEmail);
  const [pending, setPending] = useState(false);
  const [accepted, setAccepted] = useState(false);
  const [error, setError] = useState('');

  const tenantId = contextTenantId || manualTenantId;
  const hasSelectedWorkspace = Boolean(contextTenantId);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (pending || accepted) return;

    setError('');
    const normalizedEmail = email.trim();
    if (!tenantId.trim() || !normalizedEmail) {
      setError('Enter your workspace and work email to continue.');
      return;
    }

    setPending(true);
    try {
      const response = await requestPasswordRecovery({
        tenantId,
        email: normalizedEmail,
      });
      if (response?.status !== 202) {
        setError(failureMessage(undefined));
        return;
      }
      setAccepted(true);
    } catch (requestError) {
      setError(failureMessage(requestError?.response?.status));
    } finally {
      setPending(false);
    }
  };

  return (
    <main style={pageStyle}>
      <section style={panelStyle} aria-labelledby="recovery-request-title" data-testid="password-recovery-request">
        <div style={brandRow}><ShieldCheck size={22} color="#d5b04f" /><span>WILSY OS</span></div>
        <h1 id="recovery-request-title" style={titleStyle}>Recover your account</h1>
        <p style={copyStyle}>
          Request secure password-reset instructions for your institutional workspace.
        </p>

        <div style={contentGridStyle}>
          <div style={evidenceColumnStyle}>
            {hasSelectedWorkspace ? (
              <section aria-label="Selected workspace" style={workspaceContextStyle}>
                <TenantIdentityCard tenant={selectedTenant} integrated />
                <p style={workspaceHelpStyle}>Using the workspace you selected during discovery.</p>
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
                  aria-describedby="recovery-tenant-help"
                  style={inputStyle}
                  required
                />
                <p id="recovery-tenant-help" style={helpStyle}>
                  Use the workspace ID shown during workspace discovery.
                </p>
                <button type="button" onClick={() => navigate('/discovery', { replace: true })} style={linkButtonStyle}>
                  Find your workspace
                </button>
              </section>
            )}

            <section aria-labelledby="recovery-security-title" style={securityBriefStyle}>
              <h2 id="recovery-security-title" style={sectionTitleStyle}>Private by design</h2>
              <p style={helpStyle}>
                WILSY OS does not reveal whether an account or recovery contact exists.
              </p>
            </section>
          </div>

          <div style={formColumnStyle}>
            {accepted ? (
              <div role="status" aria-live="polite" style={successStyle}>
                <CheckCircle2 size={22} aria-hidden="true" />
                <div>
                  <h2 style={successTitleStyle}>Check your recovery channel</h2>
                  <p style={successCopyStyle}>
                    If recovery is available for this account, secure instructions will be sent.
                  </p>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} aria-busy={pending} style={formStyle}>
                <label htmlFor="recovery-email" style={labelStyle}>Work email</label>
                <input
                  id="recovery-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  aria-describedby="recovery-email-help"
                  style={inputStyle}
                  required
                />
                <p id="recovery-email-help" style={helpStyle}>
                  Use the work email associated with this institutional workspace.
                </p>

                {error && (
                  <div role="alert" aria-live="assertive" style={errorStyle}>
                    <AlertCircle size={16} aria-hidden="true" />
                    <span>{error}</span>
                  </div>
                )}

                <button type="submit" disabled={pending} style={buttonStyle}>
                  {pending ? <Loader2 size={18} className="animate-spin" aria-hidden="true" /> : null}
                  <span>{pending ? 'Requesting recovery…' : 'Send recovery instructions'}</span>
                </button>
              </form>
            )}

            <button type="button" onClick={() => navigate('/login', { replace: true })} style={backButtonStyle}>
              <ArrowLeft size={16} aria-hidden="true" /> Back to sign in
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

const titleStyle = { margin: '0 0 8px', fontSize: 'clamp(28px, 4vh, 36px)', lineHeight: 1.04, letterSpacing: '-.035em', fontWeight: 720 };
const copyStyle = { margin: '0 0 18px', color: '#a5a7a2', fontSize: '13px', lineHeight: 1.55 };
const contentGridStyle = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 320px), 1fr))', alignItems: 'start', gap: 'clamp(36px, 5vw, 64px)' };
const evidenceColumnStyle = { display: 'grid', alignContent: 'start', gap: '22px', minWidth: 0 };
const formColumnStyle = { minWidth: 0 };
const workspaceContextStyle = { padding: '20px', border: '1px solid rgba(213,176,79,.22)', borderRadius: '12px', background: 'rgba(37,38,38,.52)' };
const workspaceHelpStyle = { margin: '14px 0 0', color: '#8f918d', fontSize: '11px', lineHeight: 1.45 };
const workspaceFallbackStyle = { display: 'grid', gap: '8px', padding: '20px', border: '1px solid rgba(213,176,79,.22)', borderRadius: '12px', background: 'rgba(37,38,38,.52)' };
const securityBriefStyle = { padding: '18px 0 0', borderTop: '1px solid rgba(255,255,255,.08)' };
const sectionTitleStyle = { margin: '0 0 8px', color: '#d8d4c9', fontSize: '14px', lineHeight: 1.3, fontWeight: 700 };
const formStyle = { display: 'grid', gap: '8px', width: '100%' };
const labelStyle = { marginTop: '6px', color: '#d8d4c9', fontSize: '12px', fontWeight: 650 };
const inputStyle = { width: '100%', boxSizing: 'border-box', padding: '12px 14px', borderRadius: '8px', border: '1px solid #4d4f51', background: '#0f1011', color: '#fff', fontSize: '16px', outlineColor: '#d5b04f' };
const helpStyle = { margin: '-2px 0 0', color: '#777a76', fontSize: '11px', lineHeight: 1.45 };
const buttonStyle = { display: 'inline-flex', justifyContent: 'center', alignItems: 'center', gap: '9px', minHeight: '46px', marginTop: '10px', padding: '12px 18px', border: 0, borderRadius: '8px', background: '#d5b04f', color: '#141414', fontWeight: 750, fontSize: '14px', cursor: 'pointer' };
const linkButtonStyle = { justifySelf: 'start', marginTop: '4px', padding: '2px 0', border: 0, background: 'none', color: '#d5b04f', fontSize: '12px', fontWeight: 650, textDecoration: 'underline', textUnderlineOffset: '3px', cursor: 'pointer' };
const backButtonStyle = { display: 'inline-flex', alignItems: 'center', gap: '7px', marginTop: '16px', padding: 0, border: 0, background: 'none', color: '#bbb8ae', cursor: 'pointer' };
const errorStyle = { display: 'flex', gap: '8px', alignItems: 'flex-start', marginTop: '10px', padding: '10px 12px', border: '1px solid rgba(255,181,181,.24)', borderRadius: '8px', color: '#ffb5b5', fontSize: '13px', lineHeight: 1.45 };
const successStyle = { display: 'flex', gap: '12px', alignItems: 'flex-start', padding: '18px', border: '1px solid rgba(185,233,199,.20)', borderRadius: '10px', color: '#b9e9c7', background: 'rgba(28,49,36,.20)' };
const successTitleStyle = { margin: '0 0 6px', color: '#e6f4ea', fontSize: '16px', lineHeight: 1.3 };
const successCopyStyle = { margin: 0, color: '#aeb8b1', fontSize: '12px', lineHeight: 1.55 };

/**
 * ============================================================================
 * SOVEREIGN ARTIFACT SEAL
 * ============================================================================
 * ARTIFACT: PasswordRecoveryRequestPortal.jsx
 * VERSION: v1.0.0-R10E10-PASSWORD-RECOVERY-REQUEST-UI
 * AUTHORITY BOUNDARY: client presentation and certified transport invocation
 * TENANT POSTURE: selected workspace is lookup context only; no authority grant
 * FAIL-CLOSED POSTURE: only HTTP 202 produces generic accepted state
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ============================================================================
 */
