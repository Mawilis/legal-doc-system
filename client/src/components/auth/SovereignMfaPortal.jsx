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

const pageStyle = {
  width: '100%',
  height: '100dvh',
  minHeight: '100dvh',
  boxSizing: 'border-box',
  overflowY: 'auto',
  overflowX: 'hidden',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 'clamp(10px, 1.8vh, 20px)',
  background: 'radial-gradient(circle at 50% 12%, rgba(213,176,79,.055), transparent 32%), #0a0c0d',
  color: '#f7f4ec',
  fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
};
const cardStyle = {
  width: 'min(100%, 520px)',
  maxHeight: 'calc(100dvh - 20px)',
  overflowY: 'auto',
  boxSizing: 'border-box',
  padding: 'clamp(20px, 2.8vh, 30px)',
  background: 'linear-gradient(145deg, rgba(25,28,29,.99), rgba(15,17,18,.995))',
  border: '1px solid rgba(213,176,79,.30)',
  borderRadius: '18px',
  boxShadow: '0 36px 100px rgba(0,0,0,.58), inset 0 0 0 1px rgba(255,255,255,.018)',
  scrollbarWidth: 'thin',
  scrollbarColor: 'rgba(213,176,79,.22) transparent'
};
const brandRow = {
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  paddingBottom: '14px',
  marginBottom: '16px',
  color: '#d5b04f',
  fontSize: '12px',
  letterSpacing: '.20em',
  fontWeight: 800,
  borderBottom: '1px solid rgba(255,255,255,.065)'
};
const titleStyle = {
  margin: '0 0 7px',
  color: '#fbf9f3',
  fontSize: 'clamp(27px, 4vh, 34px)',
  lineHeight: 1.04,
  letterSpacing: '-.035em',
  fontWeight: 720
};
const copyStyle = {
  margin: '0 0 10px',
  color: '#a5a7a2',
  fontSize: '12px',
  lineHeight: 1.55
};
const tenantStyle = {
  display: 'grid',
  gap: '3px',
  margin: '8px 0 6px',
  padding: '9px 12px',
  borderLeft: '3px solid #d5b04f',
  borderRadius: '0 8px 8px 0',
  background: 'rgba(255,255,255,.035)',
  color: '#f1eee6',
  fontSize: '12px',
  fontWeight: 650
};
const emailStyle = {
  margin: '7px 0 9px',
  color: '#aaa8a1',
  fontSize: '11px',
  overflowWrap: 'anywhere'
};
const qrWrap = {
  width: 'fit-content',
  maxWidth: '100%',
  boxSizing: 'border-box',
  display: 'grid',
  placeItems: 'center',
  padding: '8px',
  margin: '8px auto 10px',
  background: '#ffffff',
  border: '1px solid rgba(213,176,79,.30)',
  borderRadius: '10px',
  boxShadow: '0 15px 36px rgba(0,0,0,.30)'
};
const qrStyle = {
  width: 'min(178px, 21vh, 62vw)',
  height: 'auto',
  aspectRatio: '1 / 1',
  display: 'block'
};
const formStyle = {
  display: 'grid',
  gap: '7px',
  width: '100%',
  marginTop: '7px'
};
const labelStyle = {
  color: '#999b96',
  fontSize: '9px',
  fontWeight: 800,
  letterSpacing: '.16em',
  textTransform: 'uppercase'
};
const otpStyle = {
  width: '100%',
  height: '50px',
  boxSizing: 'border-box',
  padding: '8px 14px',
  borderRadius: '9px',
  border: '1px solid rgba(213,176,79,.27)',
  background: '#0d0f10',
  color: '#f5f2e9',
  fontSize: '21px',
  fontWeight: 650,
  fontFamily: '"JetBrains Mono", ui-monospace, monospace',
  letterSpacing: '.30em',
  textAlign: 'center',
  outlineColor: '#d5b04f'
};
const buttonStyle = {
  width: '100%',
  minHeight: '46px',
  marginTop: '2px',
  padding: '10px 15px',
  border: 0,
  borderRadius: '9px',
  display: 'inline-flex',
  justifyContent: 'center',
  alignItems: 'center',
  gap: '8px',
  background: 'linear-gradient(135deg, #dfba50 0%, #c59d36 100%)',
  color: '#121313',
  fontSize: '11px',
  fontWeight: 800,
  letterSpacing: '.04em',
  cursor: 'pointer',
  boxShadow: '0 11px 26px rgba(171,130,31,.15)'
};
const backButtonStyle = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '7px',
  marginTop: '10px',
  padding: '6px 0',
  border: 0,
  background: 'none',
  color: '#898b86',
  fontSize: '10px',
  cursor: 'pointer'
};
const errorStyle = {
  display: 'flex',
  alignItems: 'flex-start',
  gap: '8px',
  marginTop: '2px',
  padding: '8px 10px',
  borderRadius: '8px',
  border: '1px solid rgba(244,114,114,.25)',
  background: 'rgba(127,29,29,.10)',
  color: '#f5b4b4',
  fontSize: '10px',
  lineHeight: 1.4
};

/**
 * ARTIFACT: client/src/components/auth/SovereignMfaPortal.jsx
 * VERSION: v30.1.0-SESSION-OWNER-CLOSURE
 * AUTHORITY BOUNDARY: MFA presentation and transport only
 * TENANT POSTURE: no tenant or enrollment state is inferred locally
 * FAIL-CLOSED POSTURE: invalid challenge state redirects to sign-in
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
