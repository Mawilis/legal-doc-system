/**
 * ============================================================================
 * WILSY OS — PASSWORD RESET PORTAL
 * ============================================================================
 * TITLE: Browser password-reset completion surface
 * VERSION: v1.3.0-R10E14-RECOVERY-LINK-FRAGMENT-HANDOFF
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Presents the unauthenticated recovery completion form and delegates
 *           all reset authority to the certified Python-backed client method.
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/PasswordResetPortal.jsx
 * COLLABORATION / OWNERSHIP: R10D8 browser surface; api.js owns transport and
 * Python EOS owns recovery, policy, hashing, revision, and revocation truth.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   2026-09-22 v1.3.0-R10E14-RECOVERY-LINK-FRAGMENT-HANDOFF — Consumes
 *   tenant/recovery values from the governed URL fragment, seeds the existing
 *   reset lookup fields, immediately scrubs the secret fragment from browser
 *   history/address display, and replaces manual token entry with a bounded
 *   "recovery link loaded" state while preserving manual fallback.
 *   2026-09-22 v1.2.2-R10D9D-VISIBLE-BOTTOM-GUTTER — Makes the lower brand
 *   gutter visible in the initial desktop viewport by compacting vertical shell
 *   chrome and form rhythm only; workspace context, recovery authority, reset
 *   transport, secret handling, and responsive scrolling remain unchanged.
 *   2026-09-22 v1.2.1-R10D9D-AUTH-SHELL-BREATHING-ROOM — Adds a deliberate
 *   viewport-safe lower brand gutter so the recovery panel finishes with
 *   premium visual breathing room without changing workspace selection,
 *   recovery authority, transport, or responsive flow.
 *   2026-09-22 v1.2.0-R10D9C-AUTH-LAYOUT-CLOSURE — Uses a responsive
 *   evidence-and-form composition on wide screens, keeps one-column flow on
 *   narrow screens, and makes recovery verification hierarchy explicit
 *   without inventing a delivery channel or changing the reset payload.
 *   2026-09-22 v1.1.0-R10D9B-CONTEXTUAL-RESPONSIVE-PASSWORD-RESET-UI — Reuses
 *   the existing selected-workspace projection as a read-only lookup selector,
 *   preserves a manual direct-entry fallback, adds privacy-safe recovery and
 *   confirmation guidance, and keeps the form in a scrollable dynamic-viewport
 *   flow. Server reset authority and certified transport remain unchanged.
 *   2026-09-22 v1.0.0-R10D8-PASSWORD-RESET-UI — Added a bounded, accessible
 *   browser form with exact certified transport, local confirmation UX,
 *   pending protection, bodyless-204 success, and safe status messaging.
 * COMPLIANCE: POPIA §19, GDPR §32, SOC2 §CC7.2; client projection only.
 * SECURITY / PRIVACY POSTURE: Password and recovery capability values remain
 *   transient component state, are never logged or persisted, and are cleared
 *   on success; fragment-delivered capabilities are removed from the address
 *   bar immediately after initial hydration.
 * TENANT BOUNDARY: AuthContext's server-backed tenant projection is used only
 *                 as a reset lookup selector; the browser neither resolves nor
 *                 grants tenant authority.
 * AUTHORITY BOUNDARY: Presentation and certified transport invocation only;
 *   no principal, role, permission, MFA, credential-revision, or session truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * ============================================================================
 */

import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, ArrowLeft, CheckCircle2, Loader2, ShieldCheck } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/authContext.jsx';
import { resetPassword } from '../../services/api.js';
import TenantIdentityCard from './TenantIdentityCard.jsx';

/**
 * @description Maps bounded server transport outcomes to safe user-facing copy.
 * @param {number|undefined} status - HTTP status returned by the reset route.
 * @returns {string} Non-sensitive status message.
 * @institutional Prevents the browser from reconstructing recovery lifecycle or
 * exposing Axios configuration, identity, or capability material.
 */
const recoveryFragmentValues = (hash) => {
  if (typeof hash !== 'string' || !hash.startsWith('#')) {
    return { tenantId: '', recoveryToken: '' };
  }
  const params = new URLSearchParams(hash.slice(1));
  const tenantId = params.get('tenant') || '';
  const recoveryToken = params.get('recovery') || '';
  return {
    tenantId: tenantId.length <= 256 ? tenantId : '',
    recoveryToken: recoveryToken.length <= 4096 ? recoveryToken : '',
  };
};

const messageForResetFailure = (status) => {
  if (status === 400) {
    return 'We could not reset your password. Check the recovery information and password requirements, then try again.';
  }
  if (status === 422) {
    return 'The reset request could not be validated. Check the fields and try again.';
  }
  if (status === 503) {
    return 'Password reset is temporarily unavailable. Please try again later.';
  }
  return 'We could not confirm the password reset. Please try again later.';
};

/**
 * @description Browser-facing password-reset completion form.
 * @param {{initialTenantId?: string, initialRecoveryToken?: string}} props
 *   Optional values supplied by a future governed route adapter. They are
 *   treated as form values only and are never parsed for identity or authority.
 * @returns {JSX.Element} Accessible reset form, pending state, or success state.
 * @collaboration Consumes the certified resetPassword transport and navigates to
 *   the existing `/login` sign-in surface after explicit operator action.
 * @institutional Keeps recovery completion unauthenticated and fail-closed;
 *   Python EOS remains the sole recovery and credential authority. Existing
 *   server-backed workspace context is presentation-only and may be absent.
 * @tenantBoundary A selected AuthContext tenant supplies only the lookup value;
 *   direct entry remains available when no selected workspace exists.
 * @transactionOwnership No transaction, retry, session, or token lifecycle is
 *   owned by this component.
 * @secretHandling Password and recovery values are local state only and are not
 *   included in diagnostics, telemetry, URLs, or rendered error messages.
 * @financialBoundary This component has no financial authority.
 */
export default function PasswordResetPortal({
  initialTenantId = '',
  initialRecoveryToken = '',
}) {
  const navigate = useNavigate();
  const location = useLocation();
  const { tenant: selectedTenant } = useAuth();
  const linkValues = useMemo(
    () => recoveryFragmentValues(location.hash),
    [location.hash],
  );
  const contextTenantId = typeof selectedTenant?.tenantId === 'string'
    ? selectedTenant.tenantId.trim()
    : '';
  const [manualTenantId, setManualTenantId] = useState(
    () => String(initialTenantId || linkValues.tenantId || ''),
  );
  const [recoveryToken, setRecoveryToken] = useState(
    () => String(initialRecoveryToken || linkValues.recoveryToken || ''),
  );
  const [newPassword, setNewPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [pending, setPending] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const tenantId = contextTenantId || manualTenantId;
  const hasSelectedWorkspace = Boolean(contextTenantId);
  const recoveryLinkLoaded = Boolean(linkValues.recoveryToken);

  useEffect(() => {
    if (!recoveryLinkLoaded) return;
    window.history.replaceState(
      window.history.state,
      '',
      `${location.pathname}${location.search}`,
    );
  }, [location.pathname, location.search, recoveryLinkLoaded]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (pending || success) return;

    setError('');
    if (!tenantId.trim() || !recoveryToken || !newPassword) {
      setError('Enter the workspace, recovery information, and new password to continue.');
      return;
    }
    if (newPassword !== confirmation) {
      setError('The password confirmation does not match.');
      return;
    }

    setPending(true);
    try {
      const response = await resetPassword({
        tenantId,
        recoveryToken,
        newPassword,
      });
      if (response?.status !== 204) {
        setError(messageForResetFailure(undefined));
        return;
      }
      setNewPassword('');
      setConfirmation('');
      setRecoveryToken('');
      setSuccess(true);
    } catch (resetError) {
      setError(messageForResetFailure(resetError?.response?.status));
    } finally {
      setPending(false);
    }
  };

  if (success) {
    return (
      <main style={pageStyle}>
        <section style={panelStyle} aria-labelledby="reset-success-title" data-testid="password-reset-success">
          <div style={brandRow}><ShieldCheck size={22} color="#d5b04f" /><span>WILSY OS</span></div>
          <div role="status" aria-live="polite" style={successPanelStyle}>
            <CheckCircle2 size={24} aria-hidden="true" />
            <div>
              <h1 id="reset-success-title" style={titleStyle}>Password reset complete</h1>
              <p style={copyStyle}>Your password has been reset. Sign in with your new password.</p>
            </div>
          </div>
          <button type="button" style={buttonStyle} onClick={() => navigate('/login', { replace: true })}>
            Continue to sign in
          </button>
        </section>
      </main>
    );
  }

  return (
    <main style={pageStyle}>
      <section style={panelStyle} aria-labelledby="reset-title" data-testid="password-reset-portal">
        <div style={brandRow}><ShieldCheck size={22} color="#d5b04f" /><span>WILSY OS</span></div>
        <h1 id="reset-title" style={titleStyle}>Reset your password</h1>
        <p style={copyStyle}>Complete the recovery step below. The server will confirm whether the reset can be recorded.</p>

        <div style={resetContentGridStyle}>
          <div style={resetEvidenceColumnStyle}>
            {hasSelectedWorkspace ? (
              <section aria-label="Selected workspace" style={workspaceContextStyle}>
                <TenantIdentityCard tenant={selectedTenant} integrated />
                <p style={workspaceContextHelpStyle}>Using the workspace you selected during discovery.</p>
              </section>
            ) : (
              <section aria-label="Workspace selection" style={workspaceFallbackStyle}>
                <label htmlFor="reset-tenant" style={labelStyle}>Workspace ID</label>
                <input
                  id="reset-tenant"
                  name="tenantId"
                  type="text"
                  autoComplete="organization"
                  value={manualTenantId}
                  onChange={(event) => setManualTenantId(event.target.value)}
                  aria-describedby="reset-tenant-help"
                  style={inputStyle}
                  required
                />
                <p id="reset-tenant-help" style={helpStyle}>Use the workspace ID shown during workspace discovery.</p>
                <button type="button" onClick={() => navigate('/discovery', { replace: true })} style={discoveryButtonStyle}>
                  Find your workspace
                </button>
              </section>
            )}
            <section aria-labelledby="recovery-verification-title" style={recoveryBriefStyle}>
              <h2 id="recovery-verification-title" style={sectionTitleStyle}>Recovery verification</h2>
              <p style={helpStyle}>
                {recoveryLinkLoaded
                  ? 'Secure recovery link loaded. The server will validate it when you submit.'
                  : 'Use the one-time recovery value issued for this reset. Keep it private.'}
              </p>
            </section>
          </div>

          <div style={resetFormColumnStyle}>
            <form onSubmit={handleSubmit} aria-busy={pending} style={formStyle}>
              {recoveryLinkLoaded ? (
                <div role="status" aria-live="polite" style={recoveryLinkStatusStyle}>
                  <ShieldCheck size={17} aria-hidden="true" />
                  <span>Secure recovery link loaded. The capability has been removed from the address bar.</span>
                </div>
              ) : (
                <>
                  <label htmlFor="reset-recovery-token" style={labelStyle}>Recovery information</label>
                  <input
                    id="reset-recovery-token"
                    name="recoveryToken"
                    type="password"
                    autoComplete="one-time-code"
                    value={recoveryToken}
                    onChange={(event) => setRecoveryToken(event.target.value)}
                    aria-describedby="reset-recovery-help"
                    style={inputStyle}
                    required
                  />
                  <p id="reset-recovery-help" style={helpStyle}>Enter the one-time recovery value. Keep it private; it is used once.</p>
                </>
              )}

              <label htmlFor="reset-new-password" style={labelStyle}>New password</label>
              <input
                id="reset-new-password"
                name="newPassword"
                type="password"
                autoComplete="new-password"
                value={newPassword}
                onChange={(event) => setNewPassword(event.target.value)}
                aria-describedby="reset-password-help"
                style={inputStyle}
                required
              />
              <p id="reset-password-help" style={helpStyle}>Choose a strong, unique password. Requirements are checked securely when you submit.</p>

              <label htmlFor="reset-confirm-password" style={labelStyle}>Confirm new password</label>
              <input
                id="reset-confirm-password"
                name="confirmation"
                type="password"
                autoComplete="new-password"
                value={confirmation}
                onChange={(event) => setConfirmation(event.target.value)}
                aria-describedby="reset-confirm-help"
                style={inputStyle}
                required
              />
              <p id="reset-confirm-help" style={helpStyle}>Re-enter your new password exactly. This confirmation is checked locally and is not sent to the server.</p>

              {error && <div role="alert" aria-live="assertive" style={errorStyle}><AlertCircle size={16} aria-hidden="true" /><span>{error}</span></div>}

              <button type="submit" disabled={pending} style={buttonStyle}>
                {pending ? <Loader2 size={18} className="animate-spin" aria-hidden="true" /> : null}
                <span>{pending ? 'Resetting password…' : 'Reset password'}</span>
              </button>
            </form>

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
  height: 'auto',
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

const workspaceContextStyle = {
  marginBottom: '22px',
  padding: '14px 16px',
  border: '1px solid rgba(213,176,79,.22)',
  borderRadius: '10px',
  background: 'rgba(37,38,38,.52)',
};

const workspaceContextHelpStyle = {
  margin: '14px 0 0',
  color: '#8f918d',
  fontSize: '11px',
  lineHeight: 1.45,
};

const resetContentGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 320px), 1fr))',
  alignItems: 'start',
  gap: 'clamp(28px, 5vw, 64px)',
};

const resetEvidenceColumnStyle = {
  display: 'grid',
  alignContent: 'start',
  gap: '22px',
  minWidth: 0,
};

const resetFormColumnStyle = {
  minWidth: 0,
};

const recoveryBriefStyle = {
  padding: '18px 0 0',
  borderTop: '1px solid rgba(255,255,255,.08)',
};

const sectionTitleStyle = {
  margin: '0 0 8px',
  color: '#d8d4c9',
  fontSize: '14px',
  lineHeight: 1.3,
  fontWeight: 700,
};

const workspaceFallbackStyle = {
  display: 'grid',
  gap: '8px',
  marginBottom: '22px',
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
  padding: '11px 14px',
  borderRadius: '8px',
  border: '1px solid #4d4f51',
  background: '#0f1011',
  color: '#fff',
  fontSize: '16px',
  outlineColor: '#d5b04f',
};

const recoveryLinkStatusStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  margin: '6px 0 4px',
  padding: '11px 12px',
  border: '1px solid rgba(185,233,199,.20)',
  borderRadius: '8px',
  color: '#b9e9c7',
  background: 'rgba(28,49,36,.18)',
  fontSize: '12px',
  lineHeight: 1.45,
};

const helpStyle = {
  margin: '-2px 0 0',
  color: '#777a76',
  fontSize: '11px',
  lineHeight: 1.45,
};

const buttonStyle = {
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

const discoveryButtonStyle = {
  justifySelf: 'start',
  marginTop: '4px',
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
  display: 'flex',
  gap: '8px',
  alignItems: 'flex-start',
  marginTop: '10px',
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
  marginBottom: '22px',
  color: '#b9e9c7',
};

/**
 * ============================================================================
 * SOVEREIGN ARTIFACT SEAL
 * ============================================================================
 * ARTIFACT: Browser password-reset completion surface
 * VERSION: v1.3.0-R10E14-RECOVERY-LINK-FRAGMENT-HANDOFF
 * AUTHORITY BOUNDARY: Client presentation and certified transport invocation
 * TENANT POSTURE: Caller-supplied tenant value is forwarded, never granted
 * FAIL-CLOSED POSTURE: Only server-confirmed HTTP 204 produces success
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ============================================================================
 */
