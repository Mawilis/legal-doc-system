/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN MFA PORTAL [V1.1.1-ENTERPRISE]                                                                                    ║
 * ║ [3FA ENROLLMENT | DUAL-FLOW VERIFICATION | HARD BRIDGE HANDSHAKE | BILLION DOLLAR SPEC]                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.1-ENTERPRISE | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                 ║
 * ║ EPITOME: NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY | MASTER NUCLEUS                                                                 ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/SovereignMfaPortal.jsx                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-error QR enrollment and backup code transparency.                               ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Obliterated React Context race condition via Hard Bridge to FounderDashboard.                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { broadcastTelemetry } from '../../utils/telemetryHelper.js';
import { ShieldCheck, Lock, Copy, RefreshCcw, CheckCircle2, AlertTriangle } from 'lucide-react';

const SovereignMfaPortal = ({ onVerificationSuccess }) => {
  const location = useLocation();
  const navigate = useNavigate();

  // 🛡️ RECTIFIED: Ingesting identity vector and tokens from the Login handover state
  const { email, qrCode, tempToken } = location.state || {};

  const [setupData, setSetupData] = useState({ qrCode: qrCode || null, secret: null });
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState('');

  // 🛡️ RECTIFIED: If a QR code is passed, we start at 'enroll'. If not, we go straight to 'verify'.
  const [step, setStep] = useState(qrCode ? 'enroll' : 'verify');

  useEffect(() => {
    // 🛡️ If the state is missing, the session is fractured. Redirect to login.
    if (!email) {
      console.warn("[MFA_PORTAL] 🚨 Missing identity vector. Redirecting to gateway.");
      navigate('/login');
      return;
    }

    /**
     * @function initiateMfaEnrollment
     * @desc Only called if we are in enrollment mode and missing setup data.
     */
    const initiateMfaEnrollment = async () => {
      if (qrCode) return; // Already have the data from Login

      setLoading(true);
      try {
        const { data } = await api.post('/auth/setup-mfa', { email });
        if (data.success) {
          setSetupData(data.data);
        } else {
          setError('FAILED_TO_PROVISION_MFA_SHARD');
        }
      } catch (err) {
        setError(err.response?.data?.message || 'GATEWAY_CONNECTION_ERROR');
      } finally {
        setLoading(false);
      }
    };

    if (step === 'enroll') initiateMfaEnrollment();
  }, [email, qrCode, step, navigate]);

  const handleVerify = async (e) => {
    e?.preventDefault();
    if (otp.length !== 6) return;

    setVerifying(true);
    setError('');

    broadcastTelemetry('GLOBAL_ROOT', 'AUTH_STRIKE', 'MFA_VERIFICATION_INIT', email, {});

    try {
      /**
       * 🏛️ RECTIFIED: Inclusion of tempToken for the V31.2.48 Handshake.
       * Matches backend: { email, otp, tempToken }
       */
      const { data } = await api.post('/auth/verify-3fa', { email, otp, tempToken });

      if (data.success) {
        // 🛡️ RECTIFIED: Storage aligned with api.js interceptor (wilsy_auth_token)
        localStorage.setItem('wilsy_auth_token', data.token);
        localStorage.setItem('wilsy_user', JSON.stringify(data.user));

        broadcastTelemetry('GLOBAL_ROOT', 'AUTH_STRIKE', 'MFA_VERIFICATION_SUCCESS', email, {});

        setStep('complete');

        // 🛡️ RECTIFIED: HARD BRIDGE. This obliterates the React Context race condition.
        // By forcing a window location shift, the global AuthContext is guaranteed
        // to mount, read the token from localStorage, and render the FounderDashboard.
        setTimeout(() => {
          if (onVerificationSuccess) {
            onVerificationSuccess(data.user);
          } else {
            window.location.href = '/dashboard';
          }
        }, 2000);
      } else {
        setError('INVALID_CHALLENGE_RESPONSE');
      }
    } catch (err) {
      broadcastTelemetry('GLOBAL_ROOT', 'AUTH_STRIKE', 'MFA_VERIFICATION_FAILURE', email, { error: err.message });
      setError(err.response?.data?.message || 'VERIFICATION_FAULT');
    } finally {
      setVerifying(false);
    }
  };

  if (loading) return <div style={portalContainer}><RefreshCcw className="animate-spin" color="#d4af37" /></div>;

  return (
    <div style={portalContainer}>
      <div style={mfaCard}>
        <div style={headerSection}>
          <ShieldCheck size={32} color="#d4af37" />
          <h2 style={titleStyle}>3FA SOVEREIGN ENROLLMENT</h2>
          <p style={subtitleStyle}>Identity: {email}</p>
        </div>

        {error && (
          <div style={errorBanner}>
            <AlertTriangle size={14} /> <span>{error}</span>
          </div>
        )}

        {step === 'enroll' && (
          <div style={stepContent}>
            <p style={instructionText}>Scan this barcode with Google Authenticator to anchor your identity.</p>

            <div style={qrContainer}>
              {setupData?.qrCode || qrCode ? (
                <img src={setupData.qrCode || qrCode} alt="MFA Barcode" style={qrImage} />
              ) : (
                <div style={qrPlaceholder}>QR_GEN_FAULT</div>
              )}
            </div>

            <div style={manualEntryBox}>
              <small style={labelStyle}>MANUAL KEY</small>
              <div style={keyRow}>
                <code>{setupData?.secret || 'CHECK_APP'}</code>
                <button
                  onClick={() => setupData?.secret && navigator.clipboard.writeText(setupData.secret)}
                  style={iconBtn}
                >
                  <Copy size={14} />
                </button>
              </div>
            </div>

            <button onClick={() => setStep('verify')} style={primaryBtn}>PROCEED TO VERIFICATION</button>
          </div>
        )}

        {step === 'verify' && (
          <form onSubmit={handleVerify} style={stepContent}>
            <p style={instructionText}>Enter the 6-digit code generated by your device.</p>

            <input
              type="text"
              autoFocus
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
              style={otpInput}
              placeholder="000 000"
            />

            <button type="submit" style={primaryBtn} disabled={verifying || otp.length < 6}>
              {verifying ? 'ANALYZING...' : 'FINALIZE ANCHOR'}
            </button>
            {qrCode && (
               <button onClick={() => setStep('enroll')} style={linkBtn}>VIEW BARCODE AGAIN</button>
            )}
          </form>
        )}

        {step === 'complete' && (
          <div style={stepContent}>
            <CheckCircle2 size={48} color="#10b981" style={{ marginBottom: '20px' }} />
            <h3 style={{ color: '#fff', letterSpacing: '2px' }}>IDENTITY ANCHORED</h3>
            <p style={instructionText}>Redirecting to the Sovereign Dashboard...</p>
          </div>
        )}
      </div>
    </div>
  );
};

/* --- INSTITUTIONAL STYLING --- */
const portalContainer = { display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', background: 'transparent' };
const mfaCard = { width: '100%', maxWidth: '400px', padding: '40px', background: '#050505', border: '1px solid #d4af37', textAlign: 'center' };
const headerSection = { marginBottom: '30px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' };
const titleStyle = { color: '#fff', fontSize: '0.9rem', letterSpacing: '4px', fontWeight: '900' };
const subtitleStyle = { color: '#444', fontSize: '0.65rem', letterSpacing: '1px' };
const stepContent = { display: 'flex', flexDirection: 'column', alignItems: 'center' };
const instructionText = { color: '#888', fontSize: '0.75rem', lineHeight: '1.6', marginBottom: '25px' };
const qrContainer = { background: '#fff', padding: '15px', borderRadius: '4px', marginBottom: '25px', display: 'inline-block' };
const qrImage = { width: '180px', height: '180px', display: 'block' };
const qrPlaceholder = { width: '180px', height: '180px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000', fontWeight: 'bold' };
const manualEntryBox = { width: '100%', background: '#0a0a0a', border: '1px solid #111', padding: '15px', marginBottom: '30px', textAlign: 'left' };
const labelStyle = { color: '#333', fontSize: '0.6rem', fontWeight: 'bold', display: 'block', marginBottom: '8px' };
const keyRow = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#d4af37', fontFamily: 'monospace' };
const iconBtn = { background: 'none', border: 'none', color: '#444', cursor: 'pointer' };
const primaryBtn = { width: '100%', padding: '15px', background: '#d4af37', color: '#000', border: 'none', fontWeight: '900', letterSpacing: '2px', cursor: 'pointer' };
const linkBtn = { background: 'none', border: 'none', color: '#444', fontSize: '0.6rem', marginTop: '20px', cursor: 'pointer', textDecoration: 'underline' };
const otpInput = { width: '100%', background: '#000', border: '1px solid #111', padding: '20px', color: '#d4af37', fontSize: '2rem', textAlign: 'center', letterSpacing: '12px', outline: 'none', marginBottom: '30px' };
const errorBanner = { background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#ef4444', padding: '12px', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', width: '100%' };

export default SovereignMfaPortal;
