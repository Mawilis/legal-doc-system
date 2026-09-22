/**
 * ============================================================================
 * WILSY OS — RECOVERY CONTACT VERIFICATION PORTAL
 * ============================================================================
 * TITLE: Browser email-control verification completion surface
 * VERSION: v1.0.0-R10E24-RECOVERY-CONTACT-VERIFICATION-UI
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Hydrates one tenant/verification capability from the governed URL
 *           fragment, removes the secret from the address bar immediately, and
 *           requires explicit human confirmation before completing verification.
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/RecoveryContactVerificationPortal.jsx
 * COLLABORATION / OWNERSHIP: api.js owns transport; Python EOS owns verification
 *   lifecycle and verified recovery-contact authority.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   2026-09-22 v1.0.0-R10E24-RECOVERY-CONTACT-VERIFICATION-UI — Adds
 *   fragment-secret hydration/scrubbing, explicit confirmation to resist mail
 *   link scanners, bodyless-204 success, bounded failure copy, and no auto-login.
 * COMPLIANCE: POPIA §19, GDPR §32, SOC2 §CC7.2; client projection only.
 * SECURITY / PRIVACY POSTURE: Capability exists only in transient component
 *   state and is removed from the browser address bar before user interaction.
 * TENANT BOUNDARY: Tenant fragment value is a lookup selector only.
 * AUTHORITY BOUNDARY: Presentation and certified transport invocation only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * ============================================================================
 */

import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, ArrowLeft, CheckCircle2, Loader2, ShieldCheck } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { completeRecoveryContactVerification } from '../../services/api.js';

const fragmentValues = (hash) => {
  if (typeof hash !== 'string' || !hash.startsWith('#')) {
    return { tenantId: '', verificationToken: '' };
  }
  const params = new URLSearchParams(hash.slice(1));
  const tenantId = params.get('tenant') || '';
  const verificationToken = params.get('verification') || '';
  return {
    tenantId: tenantId.length <= 256 ? tenantId : '',
    verificationToken: verificationToken.length <= 4096 ? verificationToken : '',
  };
};

const messageForFailure = (status) => {
  if (status === 400) return 'This recovery-email verification link is invalid or expired.';
  if (status === 422) return 'The verification request could not be validated.';
  if (status === 503) return 'Recovery-email verification is temporarily unavailable.';
  return 'We could not complete recovery-email verification.';
};

export default function RecoveryContactVerificationPortal() {
  const navigate = useNavigate();
  const location = useLocation();
  const values = useMemo(() => fragmentValues(location.hash), [location.hash]);
  const [tenantId] = useState(() => values.tenantId);
  const [verificationToken, setVerificationToken] = useState(() => values.verificationToken);
  const [pending, setPending] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const linkLoaded = Boolean(tenantId && verificationToken);

  useEffect(() => {
    if (!linkLoaded) return;
    window.history.replaceState(
      window.history.state,
      '',
      `${location.pathname}${location.search}`,
    );
  }, [linkLoaded, location.pathname, location.search]);

  const handleVerify = async () => {
    if (!linkLoaded || pending || success) return;
    setError('');
    setPending(true);
    try {
      const response = await completeRecoveryContactVerification({
        tenantId,
        verificationToken,
      });
      if (response?.status !== 204) {
        setError(messageForFailure(undefined));
        return;
      }
      setVerificationToken('');
      setSuccess(true);
    } catch (verificationError) {
      setError(messageForFailure(verificationError?.response?.status));
    } finally {
      setPending(false);
    }
  };

  return (
    <main style={pageStyle}>
      <section style={panelStyle} aria-labelledby="verify-recovery-title" data-testid="recovery-contact-verification">
        <div style={brandRow}><ShieldCheck size={22} color="#d5b04f" /><span>WILSY OS</span></div>

        {success ? (
          <div role="status" aria-live="polite" style={successStyle}>
            <CheckCircle2 size={24} aria-hidden="true" />
            <div>
              <h1 id="verify-recovery-title" style={titleStyle}>Recovery email verified</h1>
              <p style={copyStyle}>
                This address can now receive secure WILSY OS password-recovery instructions.
              </p>
            </div>
          </div>
        ) : (
          <>
            <h1 id="verify-recovery-title" style={titleStyle}>Verify recovery email</h1>
            <p style={copyStyle}>
              Confirm control of this email before WILSY OS enables it for password recovery.
            </p>

            {linkLoaded ? (
              <div style={verificationCardStyle}>
                <ShieldCheck size={24} aria-hidden="true" />
                <div>
                  <strong style={verificationTitleStyle}>Secure verification link loaded</strong>
                  <p style={verificationCopyStyle}>
                    The capability has been removed from the address bar. Continue only if you requested this verification.
                  </p>
                </div>
              </div>
            ) : (
              <div role="alert" style={errorStyle}>
                <AlertCircle size={18} aria-hidden="true" />
                <span>This verification link is incomplete. Request a new recovery-email verification after signing in.</span>
              </div>
            )}

            {error && (
              <div role="alert" aria-live="assertive" style={errorStyle}>
                <AlertCircle size={18} aria-hidden="true" />
                <span>{error}</span>
              </div>
            )}

            <button type="button" disabled={!linkLoaded || pending} onClick={handleVerify} style={buttonStyle}>
              {pending ? <Loader2 size={18} className="animate-spin" aria-hidden="true" /> : null}
              <span>{pending ? 'Verifying…' : 'Verify recovery email'}</span>
            </button>
          </>
        )}

        <button type="button" onClick={() => navigate('/login', { replace: true })} style={backButtonStyle}>
          <ArrowLeft size={16} aria-hidden="true" /> Back to sign in
        </button>
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
  padding: 'clamp(24px, 4vh, 42px) clamp(18px, 3vw, 48px) max(clamp(48px, 7vh, 80px), calc(env(safe-area-inset-bottom) + 28px))',
  overflowX: 'hidden',
  overflowY: 'auto',
  background: 'radial-gradient(circle at 50% 12%, rgba(213,176,79,.06), transparent 34%), #0a0c0d',
  color: '#f7f4ec',
  fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
};

const panelStyle = {
  width: 'min(100%, 680px)',
  boxSizing: 'border-box',
  padding: 'clamp(24px, 4vh, 38px)',
  background: 'linear-gradient(145deg, rgba(25,28,29,.99), rgba(15,17,18,.995))',
  border: '1px solid rgba(213,176,79,.30)',
  borderRadius: '18px',
  boxShadow: '0 36px 100px rgba(0,0,0,.58), inset 0 0 0 1px rgba(255,255,255,.018)',
};

const brandRow = {
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  paddingBottom: '14px',
  marginBottom: '24px',
  color: '#d5b04f',
  fontSize: '12px',
  letterSpacing: '.20em',
  fontWeight: 800,
  borderBottom: '1px solid rgba(255,255,255,.065)',
};

const titleStyle = { margin: '0 0 8px', fontSize: 'clamp(28px, 4vh, 36px)', lineHeight: 1.04, letterSpacing: '-.035em', fontWeight: 720 };
const copyStyle = { margin: '0 0 24px', color: '#a5a7a2', fontSize: '13px', lineHeight: 1.55 };
const verificationCardStyle = { display: 'flex', gap: '12px', alignItems: 'flex-start', padding: '18px', border: '1px solid rgba(185,233,199,.20)', borderRadius: '10px', color: '#b9e9c7', background: 'rgba(28,49,36,.20)' };
const verificationTitleStyle = { display: 'block', color: '#e6f4ea', fontSize: '15px', lineHeight: 1.3 };
const verificationCopyStyle = { margin: '6px 0 0', color: '#aeb8b1', fontSize: '12px', lineHeight: 1.55 };
const errorStyle = { display: 'flex', gap: '9px', alignItems: 'flex-start', marginTop: '12px', padding: '12px', border: '1px solid rgba(255,181,181,.24)', borderRadius: '8px', color: '#ffb5b5', fontSize: '13px', lineHeight: 1.45 };
const successStyle = { display: 'flex', gap: '12px', alignItems: 'flex-start', color: '#b9e9c7' };
const buttonStyle = { display: 'inline-flex', width: '100%', justifyContent: 'center', alignItems: 'center', gap: '9px', minHeight: '46px', marginTop: '20px', padding: '12px 18px', border: 0, borderRadius: '8px', background: '#d5b04f', color: '#141414', fontWeight: 750, fontSize: '14px', cursor: 'pointer' };
const backButtonStyle = { display: 'inline-flex', alignItems: 'center', gap: '7px', marginTop: '20px', padding: 0, border: 0, background: 'none', color: '#bbb8ae', cursor: 'pointer' };

/**
 * ============================================================================
 * SOVEREIGN ARTIFACT SEAL
 * ============================================================================
 * ARTIFACT: RecoveryContactVerificationPortal.jsx
 * VERSION: v1.0.0-R10E24-RECOVERY-CONTACT-VERIFICATION-UI
 * AUTHORITY BOUNDARY: client presentation and verification transport only
 * TENANT POSTURE: fragment tenant is lookup selector only
 * FAIL-CLOSED POSTURE: missing/invalid capability cannot create verified contact
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ============================================================================
 */
