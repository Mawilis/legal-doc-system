/**
 * WILSY OS — MFA CHALLENGE AND FIRST-TIME ENROLLMENT
 * VERSION: v30.1.0-SESSION-OWNER-CLOSURE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Presents the server-issued MFA state and submits one six-digit OTP
 *          without exposing existing secrets or using page reload navigation.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/SovereignMfaPortal.jsx
 * COLLABORATION / OWNERSHIP: authContext owns challenge/session state; Python
 *                            EOS auth_router validates and durably enrolls MFA.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v30.1.0-SESSION-OWNER-CLOSURE — Keeps AuthProvider as the sole
 *            session owner and removes internal tenant identifiers from the
 *            unauthenticated challenge projection.
 *            v30.0.0-AUTHORITATIVE-MFA-STATES — QR is rendered only for
 *            MFA_SETUP; reconciliation and enrolled challenges never disclose QR.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Existing TOTP provisioning material is never re-disclosed.
 * TENANT BOUNDARY: Organization identity is display-only server discovery evidence.
 * AUTHORITY BOUNDARY: Presentation and transport only; EOS owns MFA authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
 */

import React, { useEffect, useState } from 'react';
import QRCode from 'qrcode';
import { AlertCircle, ArrowLeft, CheckCircle2, Loader2, ShieldCheck } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AUTH_STATES, useAuth } from '../../contexts/authContext.jsx';

export default function SovereignMfaPortal({ onVerificationSuccess }) {
  const navigate = useNavigate();
  const location = useLocation();
  const {
    authStage,
    pendingEmail,
    qrCodeData,
    tenant,
    verifyOTP,
    loading,
    error: authError,
  } = useAuth();
  const [otp, setOtp] = useState('');
  const [qrImage, setQrImage] = useState('');
  const [error, setError] = useState('');
  const setup = authStage === AUTH_STATES.MFA_SETUP;
  const challenge = [AUTH_STATES.MFA_REQUIRED, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_VERIFYING].includes(authStage);

  useEffect(() => {
    if (!setup || !qrCodeData) {
      setQrImage('');
      return undefined;
    }
    let disposed = false;
    QRCode.toDataURL(qrCodeData, { errorCorrectionLevel: 'M', margin: 1, width: 280 })
      .then((value) => { if (!disposed) setQrImage(value); })
      .catch(() => { if (!disposed) setError('Unable to render first-time enrollment QR.'); });
    return () => { disposed = true; };
  }, [qrCodeData, setup]);

  useEffect(() => {
    if (!challenge && !setup) navigate('/login', { replace: true });
  }, [challenge, setup, navigate]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!/^\d{6}$/.test(otp) || loading) return;
    setError('');
    try {
      const result = await verifyOTP(pendingEmail, otp, null, null, setup);
      onVerificationSuccess?.(result.user);
      navigate(result.user?.hasSignedCovenant ? '/' : '/covenant', { replace: true });
    } catch (verificationError) {
      setError(verificationError?.response?.data?.detail || verificationError?.response?.data?.message || verificationError.message || 'Identity verification failed.');
    }
  };

  return (
    <main style={pageStyle}>
      <section style={cardStyle} aria-labelledby="mfa-title">
        <div style={brandRow}><ShieldCheck size={22} color="#d5b04f" /><span>WILSY OS</span></div>
        <h1 id="mfa-title" style={titleStyle}>{setup ? 'Set up authenticator' : 'Verify your identity'}</h1>
        <p style={copyStyle}>{setup ? 'Scan this code with your authenticator app, then enter the six-digit confirmation code.' : 'Enter the 6-digit code from your authenticator app.'}</p>
        {tenant && <div style={tenantStyle}><span>{tenant.name}</span></div>}
        <p style={emailStyle}>{pendingEmail || 'Identity challenge in progress'}</p>

        {setup && qrImage && <div style={qrWrap}><img src={qrImage} alt="Authenticator enrollment QR code" style={qrStyle} /></div>}

        {(challenge || setup) && (
          <form onSubmit={handleSubmit} style={formStyle}>
            <label htmlFor="mfa-code" style={labelStyle}>Six-digit code</label>
            <input id="mfa-code" value={otp} onChange={(event) => setOtp(event.target.value.replace(/\D/g, '').slice(0, 6))} inputMode="numeric" autoComplete="one-time-code" autoFocus maxLength="6" style={otpStyle} required />
            {(error || authError) && <div role="alert" style={errorStyle}><AlertCircle size={16} /><span>{error || authError}</span></div>}
            <button type="submit" disabled={loading || otp.length !== 6} style={buttonStyle}>{loading ? <Loader2 size={18} className="animate-spin" /> : <CheckCircle2 size={18} />}<span>{setup ? 'Confirm enrollment' : 'Verify identity'}</span></button>
          </form>
        )}
        <button type="button" onClick={() => navigate('/login', { replace: true })} style={backButtonStyle}><ArrowLeft size={16} /> Back to sign in</button>
      </section>
    </main>
  );
}

const pageStyle = { minHeight: '100vh', display: 'grid', placeItems: 'center', padding: '24px', background: '#101112', color: '#f5f1e8', fontFamily: 'Inter, system-ui, sans-serif' };
const cardStyle = { width: 'min(100%, 480px)', padding: '44px', background: '#17191b', border: '1px solid rgba(213,176,79,.28)', borderRadius: '12px', boxShadow: '0 24px 70px rgba(0,0,0,.35)' };
const brandRow = { display: 'flex', alignItems: 'center', gap: '10px', color: '#d5b04f', fontSize: '13px', letterSpacing: '.2em', fontWeight: 700 };
const titleStyle = { margin: '22px 0 10px', fontSize: '34px', lineHeight: 1.1, fontWeight: 650 };
const copyStyle = { color: '#b8b6ae', lineHeight: 1.55 };
const tenantStyle = { display: 'grid', gap: '4px', margin: '20px 0 10px', padding: '12px 14px', borderLeft: '3px solid #d5b04f', background: '#202224' };
const emailStyle = { color: '#d6d1c5', fontSize: '14px', margin: '20px 0' };
const qrWrap = { display: 'grid', placeItems: 'center', padding: '16px', margin: '18px auto 24px', width: 'fit-content', background: '#fff', borderRadius: '8px' };
const qrStyle = { width: '280px', height: '280px', display: 'block' };
const formStyle = { display: 'grid', gap: '10px' };
const labelStyle = { color: '#d8d4c9', fontSize: '14px', fontWeight: 600 };
const otpStyle = { width: '100%', boxSizing: 'border-box', padding: '14px', borderRadius: '7px', border: '1px solid #4d4f51', background: '#0f1011', color: '#fff', fontSize: '28px', letterSpacing: '.42em', textAlign: 'center', outlineColor: '#d5b04f' };
const buttonStyle = { display: 'inline-flex', justifyContent: 'center', alignItems: 'center', gap: '9px', marginTop: '12px', padding: '14px 18px', border: 0, borderRadius: '7px', background: '#d5b04f', color: '#141414', fontWeight: 700, fontSize: '15px', cursor: 'pointer' };
const backButtonStyle = { display: 'inline-flex', alignItems: 'center', gap: '7px', marginTop: '24px', padding: 0, border: 0, background: 'none', color: '#bbb8ae', cursor: 'pointer' };
const errorStyle = { display: 'flex', gap: '8px', color: '#ffb5b5', fontSize: '14px' };

/**
 * ARTIFACT: client/src/components/auth/SovereignMfaPortal.jsx
 * VERSION: v30.1.0-SESSION-OWNER-CLOSURE
 * AUTHORITY BOUNDARY: MFA presentation and transport only
 * TENANT POSTURE: no tenant or enrollment state is inferred locally
 * FAIL-CLOSED POSTURE: invalid challenge state redirects to sign-in
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
