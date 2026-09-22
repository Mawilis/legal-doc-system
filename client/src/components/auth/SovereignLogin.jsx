/**
 * WILSY OS — AUTHENTICATED WORKSPACE SIGN-IN
 * VERSION: v3.9.0-R10E23-FORGOT-PASSWORD-REQUEST-ENTRYPOINT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Collects primary credentials and routes only on the server-issued
 *          MFA state; it never creates identity, tenant, role, or enrollment truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/SovereignLogin.jsx
 * COLLABORATION / OWNERSHIP: authContext transports credentials to Python EOS;
 *                            SovereignMfaPortal owns the challenge presentation.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v3.9.0-R10E23-FORGOT-PASSWORD-REQUEST-ENTRYPOINT — Routes the pre-authentication Forgot Password
 *            action to the enumeration-safe /forgot-password request journey,
 *            carrying only the current email field as ephemeral navigation state;
 *            tenant context remains the existing discovery projection and no
 *            recovery capability or account truth enters the browser route.
 *            v3.8.0-R10D9G-RESET-PARITY-LOGIN-ARCHITECTURE — Brings sign-in
 *            into the same institutional page grammar as password reset by
 *            promoting the page title above a balanced identity-and-credentials
 *            task grid, widening the tenant identity surface, and tightening
 *            the inter-column relationship without changing controls,
 *            authentication, MFA, recovery navigation, or tenant authority.
 *            v3.7.0-R10D9F-INSTITUTIONAL-LOGIN-COMPOSITION — Finalizes the
 *            institutional sign-in composition by removing the redundant
 *            workspace-identity eyebrow, top-aligning the tenant projection
 *            with the credential column, and anchoring tenant identity in a
 *            restrained presentation surface without changing authentication,
 *            recovery navigation, tenant authority, or control geometry.
 *            v3.6.2-R10D9D-VISIBLE-BOTTOM-GUTTER — Makes the lower brand
 *            gutter visible in the initial desktop viewport by compacting
 *            vertical shell chrome only; field sizing, recovery navigation,
 *            authentication, MFA, tenant authority, and responsive scrolling
 *            remain unchanged.
 *            v3.6.1-R10D9D-AUTH-SHELL-BREATHING-ROOM — Adds a deliberate
 *            viewport-safe lower brand gutter so the sign-in panel and trust
 *            boundary finish with clear visual breathing room without changing
 *            authentication, recovery navigation, or responsive flow.
 *            v3.6.0-R10D9C-AUTH-LAYOUT-CLOSURE — Places the pre-authentication
 *            recovery action beside the password label, preserves its
 *            keyboard/pointer target, and keeps the content-driven shell and
 *            footer in normal flow across short and narrow viewports.
 *            v3.5.1-R10D9A-FORGOT-PASSWORD-ENTRYPOINT — Adds one
 *            pre-authentication Forgot password? navigation action to the
 *            certified `/reset-password` route without sending form data or
 *            invoking reset authority.
 *            v3.5.0-FINAL-PIXEL-CLOSURE — Centers a bounded 1120px panel,
 *            balances the identity/form columns, and keeps the natural-flow
 *            auth surface visible on desktop, short, and mobile viewports.
 *            v3.4.0-VIEWPORT-SAFE-AUTH — Makes the page shell a natural-flow,
 *            `100dvh` scroll-safe container so short viewports never clip the
 *            panel or footer.
 *            v3.3.0-PUBLIC-IDENTITY-CONTRACT — Keeps public identity limited
 *            to legal/display name, alias, verified state, and governed mark;
 *            removes internal tenant identifiers from the login presentation.
 *            v3.2.0-INSTITUTIONAL-AUTH-BRAND — Recomposed sign-in as one
 *            responsive institutional panel with an integrated identity zone
 *            and the established WILSY brand asset.
 *            v3.1.0-PREMIUM-TENANT-IDENTITY — Added the permanent WILSY OS
 *            platform trust mark and bounded premium tenant identity card.
 *            v3.0.0-AUTHORITATIVE-MFA-ROUTING — Replaced founder/citadel
 *            presentation, fake telemetry, inline QR flow, and reload navigation
 *            with restrained institutional sign-in and explicit server state routing.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No password or provisioning secret is rendered in copy.
 * TENANT BOUNDARY: Organization context is displayed only from authoritative discovery.
 * AUTHORITY BOUNDARY: Credential transport and state projection only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
 */

import React, { useState } from 'react';
import { AlertCircle, ArrowLeft, Loader2 } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AUTH_STATES, useAuth } from '../../contexts/authContext.jsx';
import TenantIdentityCard from './TenantIdentityCard.jsx';
import wilsyBrandAsset from '../../assets/logo/wilsy.jpeg';

export default function SovereignLogin({ onLoginSuccess }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, loading, error: authError, tenant } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const resolvedTenant = location.state?.tenant || tenant;

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    try {
      const result = await login(email.trim(), password);
      if ([AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED].includes(result.status)) {
        navigate('/mfa', { replace: true, state: { tenant: resolvedTenant } });
        return;
      }
      if (result.status === 'AUTHENTICATED') {
        onLoginSuccess?.(result.user);
        navigate('/', { replace: true });
      }
    } catch (loginError) {
      setError(loginError?.response?.data?.detail || loginError?.response?.data?.message || loginError.message || 'Authentication service unavailable.');
    }
  };

  return (
    <main style={pageStyle}>
      <section style={panelStyle} aria-labelledby="login-title" data-testid="login-panel">
        <header style={brandRow}>
          <img src={wilsyBrandAsset} alt="WILSY OS platform mark" style={platformMarkStyle} />
          <div style={brandCopyStyle}><strong>WILSY OS</strong><span>Institutional access</span></div>
        </header>
        <div style={headingStyle} data-testid="login-page-heading">
          <h1 id="login-title" style={titleStyle}>Sign in</h1>
          <p style={subtitleStyle}>Continue securely into your institution's workspace.</p>
        </div>
        <div style={contentGridStyle} data-testid="login-content-grid">
          <div style={identityZoneStyle}>
            <TenantIdentityCard tenant={resolvedTenant} integrated />
          </div>
          <div style={authZoneStyle}>
            <form onSubmit={handleSubmit} style={formStyle}>
              <label htmlFor="work-email" style={labelStyle}>Work email</label>
              <input id="work-email" type="email" autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} style={inputStyle} required />
              <div style={passwordLabelRowStyle}>
                <label htmlFor="work-password" style={passwordLabelStyle}>Password</label>
                <button
                  type="button"
                  onClick={() => navigate('/forgot-password', { state: { email: email.trim() } })}
                  style={forgotPasswordButtonStyle}
                >
                  Forgot password?
                </button>
              </div>
              <input id="work-password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} style={inputStyle} required />
              {(error || authError) && <div role="alert" style={errorStyle}><AlertCircle size={16} /><span>{error || authError}</span></div>}
              <button type="submit" disabled={loading || !email.trim() || !password} style={buttonStyle}>
                {loading ? <Loader2 size={18} className="animate-spin" /> : null}<span>Continue securely</span>
              </button>
            </form>
            <button type="button" onClick={() => navigate('/discovery', { replace: true })} style={backButtonStyle}><ArrowLeft size={16} /> Back to workspace discovery</button>
          </div>
        </div>
        <footer style={footerStyle}><span>Private workspace access</span><span>WILSY OS trust boundary</span></footer>
      </section>
    </main>
  );
}

const pageStyle = { minHeight: '100dvh', width: '100%', boxSizing: 'border-box', display: 'grid', justifyItems: 'center', alignItems: 'start', padding: 'clamp(24px, 3.2vh, 32px) clamp(20px, 3vw, 48px) max(clamp(48px, 7vh, 80px), calc(env(safe-area-inset-bottom) + 28px))', overflowX: 'hidden', overflowY: 'auto', background: '#101112', color: '#f5f1e8', fontFamily: 'Inter, system-ui, sans-serif' };
const panelStyle = { width: 'min(1080px, 100%)', minHeight: 0, height: 'auto', boxSizing: 'border-box', padding: 'clamp(24px, 3vh, 30px) clamp(24px, 4vh, 38px) 24px', background: 'linear-gradient(145deg, #1c1e20, #141617)', border: '1px solid rgba(213,176,79,.3)', borderRadius: '16px', boxShadow: '0 30px 90px rgba(0,0,0,.42)' };
const brandRow = { display: 'flex', alignItems: 'center', gap: '14px', paddingBottom: '14px', borderBottom: '1px solid rgba(245,241,232,.1)', color: '#d5b04f' };
const platformMarkStyle = { width: '46px', height: '46px', objectFit: 'cover', objectPosition: '50% 13%', borderRadius: '8px', background: '#fff' };
const brandCopyStyle = { display: 'grid', gap: '3px' };
const contentGridStyle = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 320px), 1fr))', alignItems: 'start', columnGap: 'clamp(36px, 5vw, 64px)', rowGap: 'clamp(28px, 5vw, 48px)', padding: '22px 0 20px' };
const identityZoneStyle = { display: 'grid', alignContent: 'start', width: '100%', boxSizing: 'border-box', padding: '22px 24px 20px', border: '1px solid rgba(213,176,79,.18)', borderRadius: '12px', background: 'linear-gradient(145deg, rgba(37,38,38,.34), rgba(19,21,22,.18))', alignSelf: 'start' };
const authZoneStyle = { minWidth: 0, width: '100%' };
const headingStyle = { paddingTop: '22px' };
const titleStyle = { margin: '0 0 8px', fontSize: 'clamp(28px, 4vh, 36px)', lineHeight: 1.04, fontWeight: 720, letterSpacing: '-.035em' };
const subtitleStyle = { margin: 0, color: '#a5a7a2', lineHeight: 1.55, fontSize: '13px' };
const formStyle = { display: 'grid', gap: '10px' };
const labelStyle = { marginTop: '7px', color: '#d8d4c9', fontSize: '14px', fontWeight: 600 };
const passwordLabelRowStyle = { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '14px', minHeight: '44px' };
const passwordLabelStyle = { ...labelStyle, marginTop: 0 };
const inputStyle = { width: '100%', boxSizing: 'border-box', padding: '14px 15px', borderRadius: '7px', border: '1px solid #4d4f51', background: '#0f1011', color: '#fff', fontSize: '16px', outlineColor: '#d5b04f' };
const buttonStyle = { display: 'inline-flex', justifyContent: 'center', alignItems: 'center', gap: '9px', marginTop: '14px', padding: '14px 18px', border: 0, borderRadius: '7px', background: '#d5b04f', color: '#141414', fontWeight: 700, fontSize: '15px', cursor: 'pointer' };
const forgotPasswordButtonStyle = { display: 'inline-flex', alignItems: 'center', justifyContent: 'center', minHeight: '44px', margin: 0, padding: '10px 0', border: 0, background: 'none', color: '#d5b04f', fontSize: '13px', fontWeight: 650, textDecoration: 'underline', textUnderlineOffset: '3px', cursor: 'pointer' };
const backButtonStyle = { display: 'inline-flex', alignItems: 'center', gap: '7px', marginTop: '18px', padding: 0, border: 0, background: 'none', color: '#bbb8ae', cursor: 'pointer' };
const errorStyle = { display: 'flex', gap: '8px', alignItems: 'flex-start', marginTop: '8px', color: '#ffb5b5', fontSize: '14px' };
const footerStyle = { display: 'flex', justifyContent: 'space-between', gap: '16px', paddingTop: '14px', borderTop: '1px solid rgba(245,241,232,.1)', color: '#777873', fontSize: '10px', letterSpacing: '.1em', textTransform: 'uppercase' };

/**
 * ARTIFACT: client/src/components/auth/SovereignLogin.jsx
 * VERSION: v3.9.0-R10E23-FORGOT-PASSWORD-REQUEST-ENTRYPOINT
 * AUTHORITY BOUNDARY: credential transport and server-state routing only
 * TENANT POSTURE: no client tenant, role, or Founder fallback
 * FAIL-CLOSED POSTURE: incomplete auth responses remain unauthenticated
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
