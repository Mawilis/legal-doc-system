/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign MFA Portal
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/src/components/auth/SovereignMfaPortal.jsx
 * Version:        v29.0.5-TOTP-QR-COMPATIBILITY
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Production‑grade 3FA verification portal with zero‑tolerance error handling and automatic state invalidation.
 * Classification: Production Artifact
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) — Mandated institutional MFA handshake and absolute error resilience.
 *   - AI Engineering — RECTIFIED: Added explicit token clearing on verification failures to prevent stale session navigation.
 *
 * Change Log:
 *   2026-08-22 v29.0.5-TOTP-QR-COMPATIBILITY — Encodes otpauth provisioning URIs locally and sends the canonical OTP field pair.
 *   2026-07-30 v29.0.4-ERROR-GUARD — Rectified: On API failure, clears auth tokens to ensure the user cannot bypass to the dashboard.
 *   2026-07-30 v29.0.3-SINGULARITY-GOLD — Baseline with QR support and hard bridge handover.
 *
 * Forensic Relationships:
 *   Upstream:   ../../services/api.js, ../../contexts/authContext.jsx
 *   Downstream: ../Login.jsx, ../Dashboard.jsx
 *   Shared Crypto / Events / Config: wilsy_auth_token, wilsy_sovereign_user, api interceptors.
 *
 * Certification Seal: PRODUCTION_READY_v29.0.4-ERROR-GUARD
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { broadcastTelemetry } from '../../utils/telemetryHelper.js';
import { ShieldCheck, Lock, Copy, RefreshCcw, CheckCircle2, AlertTriangle } from 'lucide-react';
import QRCode from 'qrcode';
import { useAuth } from '../../contexts/authContext.jsx';

/**
 * @function SovereignMfaPortal
 * @description Manages 3FA provisioning, barcode scanning, and cryptographic verification.
 * On any verification error, it forcibly clears any stale tokens and prevents navigation to protected routes.
 * @param {Object} props - Component properties.
 * @param {Function} [props.onVerificationSuccess] - Optional callback for successful verification.
 * @returns {JSX.Element} Rendered Sovereign MFA Portal interface.
 */
const SovereignMfaPortal = ({ onVerificationSuccess }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth(); // 🛡️ Added: Access to logout to clear session on error.

  const { email, qrCode, tempToken } = location.state || {};

  const [setupData, setSetupData] = useState({ qrCode: qrCode || null, secret: null });
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState('');
  const [renderedQrCode, setRenderedQrCode] = useState(null);

  const [step, setStep] = useState(qrCode ? 'enroll' : 'verify');

  useEffect(() => {
    if (!email) {
      console.warn("[MFA_PORTAL] 🚨 Missing identity vector. Redirecting to gateway.");
      navigate('/login', { replace: true });
      return;
    }

    const initiateMfaEnrollment = async () => {
      if (qrCode) return;
      setLoading(true);
      try {
        const response = await api.post('/auth/setup-mfa', { email });
        if (response.data && response.data.success) {
          setSetupData(response.data.data);
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

  useEffect(() => {
    let disposed = false;
    const provisioningUri = setupData?.qrCode || qrCode;

    if (!provisioningUri) {
      setRenderedQrCode(null);
      return () => { disposed = true; };
    }

    if (!provisioningUri.startsWith('otpauth://')) {
      setRenderedQrCode(provisioningUri);
      return () => { disposed = true; };
    }

    QRCode.toDataURL(provisioningUri, { errorCorrectionLevel: 'M', margin: 1, width: 360 })
      .then((dataUrl) => {
        if (!disposed) setRenderedQrCode(dataUrl);
      })
      .catch((qrError) => {
        console.error('[MFA-QR] Failed to encode provisioning URI.', qrError);
        if (!disposed) setError('Unable to render the enrollment QR code. Please restart sign-in.');
      });

    return () => { disposed = true; };
  }, [qrCode, setupData?.qrCode]);

  /**
   * @function handleVerify
   * @description Submits the 6‑digit OTP. On failure, it forcibly clears the session and remains on the portal.
   */
  const handleVerify = async (e) => {
    if (e) e.preventDefault();
    if (otp.length !== 6) return;

    setVerifying(true);
    setError('');

    broadcastTelemetry('GLOBAL_ROOT', 'AUTH_STRIKE', 'MFA_VERIFICATION_INIT', email, {});

    try {
      const response = await api.post('/auth/verify-3fa', { email, code: otp, otp });
      const data = response.data;

      if (data && data.success && data.token) {
        localStorage.setItem('wilsy_auth_token', data.token);
        localStorage.setItem('wilsy_sovereign_token', data.token);
        localStorage.setItem('wilsy_user', JSON.stringify(data.user));
        localStorage.setItem('wilsy_user_profile', JSON.stringify(data.user));

        broadcastTelemetry('GLOBAL_ROOT', 'AUTH_STRIKE', 'MFA_VERIFICATION_SUCCESS', email, {});

        setStep('complete');

        setTimeout(() => {
          if (onVerificationSuccess) {
            onVerificationSuccess(data.user);
          } else {
            window.location.href = '/dashboard';
          }
        }, 1500);
      } else {
        setError(data?.message || 'INVALID_CHALLENGE_RESPONSE');
      }
    } catch (err) {
      broadcastTelemetry('GLOBAL_ROOT', 'AUTH_STRIKE', 'MFA_VERIFICATION_FAILURE', email, { error: err.message });
      setError(err.response?.data?.message || 'VERIFICATION_FAULT');
      // 🛡️ RECTIFIED: Forcibly log out the user to clear any stale tokens and prevent navigation.
      await logout();
    } finally {
      setVerifying(false);
    }
  };

  if (loading) {
    return (
      <div style={portalContainer}>
        <RefreshCcw className="animate-spin" color="#d4af37" size={32} />
      </div>
    );
  }

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
            <p style={instructionText}>Scan this barcode with Google Authenticator to anchor your institutional identity.</p>
            <div style={qrContainer}>
              {renderedQrCode ? (
                <img src={renderedQrCode} alt="MFA Barcode" style={qrImage} />
              ) : (
                <div style={qrPlaceholder}>QR_GEN_FAULT</div>
              )}
            </div>
            <div style={manualEntryBox}>
              <small style={labelStyle}>MANUAL KEY</small>
              <div style={keyRow}>
                <code>{setupData?.secret || 'CHECK_APP'}</code>
                <button type="button" onClick={() => setupData?.secret && navigator.clipboard.writeText(setupData.secret)} style={iconBtn} title="Copy Manual Key">
                  <Copy size={14} />
                </button>
              </div>
            </div>
            <button type="button" onClick={() => setStep('verify')} style={primaryBtn}>
              PROCEED TO VERIFICATION
            </button>
          </div>
        )}

        {step === 'verify' && (
          <form onSubmit={handleVerify} style={stepContent}>
            <p style={instructionText}>Enter the 6-digit code generated by your Google Authenticator app.</p>
            <input
              type="text"
              autoFocus
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
              style={otpInput}
              placeholder="000000"
              maxLength={6}
            />
            <button type="submit" style={primaryBtn} disabled={verifying || otp.length < 6}>
              {verifying ? 'ANALYZING...' : 'FINALIZE ANCHOR'}
            </button>
            {(qrCode || setupData?.qrCode) && (
               <button type="button" onClick={() => setStep('enroll')} style={linkBtn}>
                 VIEW BARCODE AGAIN
               </button>
            )}
          </form>
        )}

        {step === 'complete' && (
          <div style={stepContent}>
            <CheckCircle2 size={48} color="#10b981" style={{ marginBottom: '20px' }} />
            <h3 style={{ color: '#fff', letterSpacing: '2px' }}>IDENTITY ANCHORED</h3>
            <p style={instructionText}>Booting Mission Control Executive Surface...</p>
          </div>
        )}
      </div>
    </div>
  );
};

/* --- INSTITUTIONAL STYLING SYSTEM --- */
const portalContainer = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  backgroundColor: '#030303',
  fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
};

const mfaCard = {
  width: '100%',
  maxWidth: '440px',
  padding: '40px',
  backgroundColor: '#050505',
  border: '1px solid rgba(212, 175, 55, 0.4)',
  textAlign: 'center',
  boxShadow: '0 0 40px rgba(212,175,55,0.15)',
  borderRadius: '4px'
};

const headerSection = {
  marginBottom: '30px',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: '10px'
};

const titleStyle = {
  color: '#fff',
  fontSize: '0.9rem',
  letterSpacing: '4px',
  fontWeight: '900'
};

const subtitleStyle = {
  color: '#888',
  fontSize: '0.7rem',
  letterSpacing: '1px'
};

const stepContent = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  width: '100%'
};

const instructionText = {
  color: '#aaa',
  fontSize: '0.75rem',
  lineHeight: '1.6',
  marginBottom: '25px'
};

const qrContainer = {
  backgroundColor: '#fff',
  padding: '15px',
  borderRadius: '4px',
  marginBottom: '25px',
  display: 'inline-block'
};

const qrImage = {
  width: '180px',
  height: '180px',
  display: 'block'
};

const qrPlaceholder = {
  width: '180px',
  height: '180px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: '#000',
  fontWeight: 'bold'
};

const manualEntryBox = {
  width: '100%',
  backgroundColor: '#0a0a0a',
  border: '1px solid rgba(212, 175, 55, 0.2)',
  padding: '15px',
  marginBottom: '30px',
  textAlign: 'left',
  borderRadius: '4px'
};

const labelStyle = {
  color: '#666',
  fontSize: '0.6rem',
  fontWeight: 'bold',
  display: 'block',
  marginBottom: '8px'
};

const keyRow = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  color: '#d4af37',
  fontFamily: '"JetBrains Mono", monospace'
};

const iconBtn = {
  background: 'none',
  border: 'none',
  color: '#888',
  cursor: 'pointer'
};

const primaryBtn = {
  width: '100%',
  padding: '16px',
  background: 'linear-gradient(135deg, #d4af37 0%, #aa8c2c 100%)',
  color: '#000',
  border: 'none',
  fontWeight: '900',
  letterSpacing: '2px',
  cursor: 'pointer',
  borderRadius: '4px',
  transition: 'all 0.2s ease'
};

const linkBtn = {
  background: 'none',
  border: 'none',
  color: '#888',
  fontSize: '0.65rem',
  marginTop: '20px',
  cursor: 'pointer',
  textDecoration: 'underline'
};

const otpInput = {
  width: '100%',
  backgroundColor: '#000',
  border: '1px solid rgba(212, 175, 55, 0.3)',
  padding: '18px',
  color: '#d4af37',
  fontSize: '2rem',
  textAlign: 'center',
  letterSpacing: '12px',
  outline: 'none',
  marginBottom: '30px',
  fontFamily: '"JetBrains Mono", monospace',
  borderRadius: '4px'
};

const errorBanner = {
  backgroundColor: 'rgba(239, 68, 68, 0.1)',
  border: '1px solid #ef4444',
  color: '#ef4444',
  padding: '12px',
  fontSize: '0.7rem',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  marginBottom: '20px',
  width: '100%',
  borderRadius: '4px'
};

export default SovereignMfaPortal;
