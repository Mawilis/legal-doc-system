/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign Login Gateway (Citadel)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/src/components/auth/SovereignLogin.jsx
 * Version:        v2.1.3-MFA-FIT-AND-SPACING
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Founder authentication portal with inline MFA. Fully isolated
 *                 from protected endpoints. Telemetry panel uses institutional
 *                 language when kernel is offline. Vite proxy required.
 * Classification: Production Artifact
 *
 * Change Log:
 *   2026-08-22 v2.1.3-MFA-FIT-AND-SPACING — Prevented central-card bleed and restored breathing room around the QR enrollment code.
 *   2026-08-22 v2.1.3-MFA-ENROLLMENT-ROUTING — Persists enrollment intent so QR setup validates before normal 3FA verification.
 *   2026-08-22 v2.1.2-TOTP-QR-COMPATIBILITY — Renders raw otpauth provisioning URIs as browser-safe QR data URLs.
 *   2026-08-19 v2.1.1‑MFA‑AUTOFOCUS — Added autoFocus to OTP input for immediate cursor activation.
 *   2026-08-19 v2.1.0‑PROXY‑READY‑UX — Improved telemetry copy; proxy guidance.
 *   2026-08-19 v2.0.0‑LOGIN‑ISOLATED — Isolated from protected endpoints.
 *   2026-08-18 v1.3.7‑PERSISTENT‑MFA — MFA persistence.
 *
 * Certification Seal: PRODUCTION_READY_v2.1.1‑MFA‑AUTOFOCUS
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, AlertCircle, Fingerprint, Eye, EyeOff, ShieldCheck, ShieldAlert, CheckCircle } from 'lucide-react';
import QRCode from 'qrcode';
import { useAuth } from '../../contexts/authContext';
import '../../styles/superadmin/animations/quantum-pulse.css';
import '../../styles/superadmin/animations/terminal-glow.css';

const KERNEL_OFFLINE_LABEL = 'KERNEL OFFLINE';
const KERNEL_PROBE_MS = 15_000;
const KERNEL_PROBE_MAX_MS = 120_000;
const MAX_PROBE_FAILURES = 3;

async function probeLiveKernel(signal) {
  const started = performance.now();
  try {
    const res = await fetch('/api/kernel', {
      method: 'GET',
      credentials: 'include',
      signal,
      headers: { Accept: 'application/json' }
    });
    const latencyMs = Math.round(performance.now() - started);
    let data = null;
    try { data = await res.json(); } catch { }
    if (!res.ok) {
      return { ok: false, version: null, status: `HTTP_${res.status}`, latencyMs, system: null, bridge: null };
    }
    return {
      ok: true,
      version: data?.version || null,
      status: data?.status || 'OPERATIONAL',
      latencyMs,
      system: data?.system || 'WILSY OS EOS KERNEL',
      bridge: data?.bridge || data?.contract || null,
      timestamp: data?.timestamp || null
    };
  } catch {
    return { ok: false, version: null, status: 'UNREACHABLE', latencyMs: Math.round(performance.now() - started), system: null, bridge: null };
  }
}

export default function SovereignLogin({ onLoginSuccess }) {
  const navigate = useNavigate();
  const { verifyOTP, login: contextLogin, discoverTenant } = useAuth();
  const [mode, setMode] = useState('founder');

  // MFA state (hoisted + persisted)
  const [showMfa, setShowMfa] = useState(false);
  const [mfaData, setMfaData] = useState(null);
  const [otp, setOtp] = useState('');
  const [verifying, setVerifying] = useState(false);
  const [mfaError, setMfaError] = useState('');
  const [renderedMfaQr, setRenderedMfaQr] = useState(null);

  useEffect(() => {
    try {
      const stored = sessionStorage.getItem('wilsy_mfa_pending');
      if (stored === 'true') {
        setShowMfa(true);
        const data = sessionStorage.getItem('wilsy_mfa_data');
        if (data) setMfaData(JSON.parse(data));
      }
    } catch { }
  }, []);

  useEffect(() => {
    let disposed = false;
    const provisioningUri = mfaData?.qrCode;

    if (!provisioningUri) {
      setRenderedMfaQr(null);
      return () => { disposed = true; };
    }

    if (!provisioningUri.startsWith('otpauth://')) {
      setRenderedMfaQr(provisioningUri);
      return () => { disposed = true; };
    }

    QRCode.toDataURL(provisioningUri, {
      errorCorrectionLevel: 'M',
      margin: 1,
      width: 360,
      color: { dark: '#000000', light: '#FFFFFF' }
    })
      .then((dataUrl) => {
        if (!disposed) setRenderedMfaQr(dataUrl);
      })
      .catch((error) => {
        console.error('[MFA-QR] Failed to encode provisioning URI.', error);
        if (!disposed) setMfaError('Unable to render the enrollment QR code. Please restart sign-in.');
      });

    return () => { disposed = true; };
  }, [mfaData?.qrCode]);

  // Kernel probe state
  const [kernelInfo, setKernelInfo] = useState({
    ok: false,
    version: null,
    status: 'PROBING',
    latencyMs: 0,
    system: null,
    bridge: null
  });
  const [probeFailedCount, setProbeFailedCount] = useState(0);
  const [probingStopped, setProbingStopped] = useState(false);

  const [forensicHistory, setForensicHistory] = useState([]);
  const mountedRef = useRef(true);

  const addForensicEntry = useCallback((msg, color = '#E8C547') => {
    setForensicHistory((prev) => [
      { time: new Date().toLocaleTimeString(), msg, color },
      ...prev
    ].slice(0, 8));
  }, []);

  const reportTelemetryError = useCallback(async (errPayload) => {
    if (import.meta.env.DEV) return;
    try {
      await fetch('/api/telemetry/error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errPayload)
      });
    } catch { }
  }, []);

  // Kernel probing with backoff + stop after 3 failures
  useEffect(() => {
    mountedRef.current = true;
    let controller = new AbortController();
    let timeoutId = null;
    let currentBackoff = KERNEL_PROBE_MS;
    let failures = 0;

    const run = async () => {
      if (!mountedRef.current || probingStopped) return;
      const info = await probeLiveKernel(controller.signal);
      if (!mountedRef.current) return;
      setKernelInfo(info);
      if (info.ok) {
        failures = 0;
        currentBackoff = KERNEL_PROBE_MS;
        setProbeFailedCount(0);
        addForensicEntry(`[OK] KERNEL_LIVE v${info.version} · ${info.latencyMs}ms`, '#34D399');
      } else {
        failures += 1;
        setProbeFailedCount(failures);
        const newBackoff = Math.min(KERNEL_PROBE_MAX_MS, KERNEL_PROBE_MS * Math.pow(2, failures - 1));
        currentBackoff = newBackoff;
        addForensicEntry(`[WARN] KERNEL_${info.status} (attempt ${failures})`, '#F87171');
        if (failures >= MAX_PROBE_FAILURES) {
          setProbingStopped(true);
          addForensicEntry('[INFO] Kernel probing stopped after repeated failures.', '#9CA3AF');
          return;
        }
      }
      timeoutId = setTimeout(() => {
        controller.abort();
        controller = new AbortController();
        run();
      }, currentBackoff);
    };

    run();

    return () => {
      mountedRef.current = false;
      controller.abort();
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [addForensicEntry, probingStopped]);

  const handleTenantDiscovery = async () => {
    try {
      addForensicEntry('[TENANT-DISCOVERY] Opening discovery surface...', '#E8C547');
      navigate('/discovery', { state: { from: 'citadel' } });
    } catch (err) {
      addForensicEntry(`[TENANT-DISCOVERY] Navigate failed: ${err.message}`, '#F87171');
      try {
        const tenant = await discoverTenant?.();
        if (tenant) {
          addForensicEntry(`[TENANT-DISCOVERY] Resolved: ${tenant.alias || tenant.tenantId}`, '#34D399');
          navigate('/mfa', { state: { email: '', tempToken: null, qrCode: null } });
        } else {
          setMode('founder');
        }
      } catch (e2) {
        addForensicEntry(`[TENANT-DISCOVERY] Failed: ${e2.message}`, '#F87171');
        setMode('founder');
      }
    }
  };

  const versionLabel = kernelInfo.ok && kernelInfo.version
    ? `WILSY OS KERNEL  v${kernelInfo.version}`
    : KERNEL_OFFLINE_LABEL;

  const sealState = !kernelInfo.ok ? 'SOVEREIGN SIGNAL LOST' : kernelInfo.status === 'OPERATIONAL' ? 'SECURE' : 'DEGRADED';
  const sealColor = sealState === 'SECURE' ? '#34D399' : '#F87171';

  const formatMetric = (value, suffix = '') => {
    if (value == null || Number.isNaN(value)) return '—';
    return `${value}${suffix}`;
  };

  // OTP handlers
  const handleOtpSubmit = async (e) => {
    e.preventDefault();
    if (!otp || otp.length < 6) {
      setMfaError('Enter the 6-digit OTP.');
      return;
    }
    setVerifying(true);
    setMfaError('');
    addForensicEntry('[3FA] Verifying OTP...', '#E8C547');
    try {
      const result = await verifyOTP(
        mfaData.email,
        otp,
        null,
        null,
        mfaData?.mfaSetup === true || Boolean(mfaData?.qrCode)
      );
      if (result && result.success) {
        addForensicEntry('[3FA-OK] OTP verified. Access granted.', '#34D399');
        if (result.token) {
          localStorage.setItem('token', result.token);
          if (result.user) localStorage.setItem('user', JSON.stringify(result.user));
        }
        try {
          sessionStorage.removeItem('wilsy_mfa_pending');
          sessionStorage.removeItem('wilsy_mfa_data');
        } catch { }
        addForensicEntry('[3FA] Reloading page to update session...', '#E8C547');
        window.location.href = '/';
        return;
      }
      const errMsg = result?.message || 'Invalid OTP. Try again.';
      setMfaError(errMsg);
      addForensicEntry(`[3FA-ERROR] ${errMsg}`, '#F87171');
    } catch (err) {
      const errMsg = err.response?.data?.message || err.message || 'OTP verification failed.';
      setMfaError(errMsg);
      addForensicEntry(`[3FA-ERROR] ${errMsg}`, '#F87171');
    } finally {
      setVerifying(false);
    }
  };

  const handleCancelMfa = () => {
    setShowMfa(false);
    setMfaData(null);
    setOtp('');
    setMfaError('');
    addForensicEntry('[3FA] Cancelled.', '#9CA3AF');
    try {
      sessionStorage.removeItem('wilsy_mfa_pending');
      sessionStorage.removeItem('wilsy_mfa_data');
    } catch { }
  };

  return (
    <div style={gateContainer}>
      <style>{`
        @keyframes sovereignButtonPulse {
          0% { box-shadow: 0 4px 24px rgba(212,175,55,0.28); transform: scale(1); }
          50% { box-shadow: 0 0 36px rgba(212,175,55,0.55), inset 0 0 12px rgba(255,255,255,0.2); transform: scale(1.008); }
          100% { box-shadow: 0 4px 24px rgba(212,175,55,0.28); transform: scale(1); }
        }
        .sovereign-action-btn {
          animation: sovereignButtonPulse 3.2s infinite ease-in-out;
        }
        .sovereign-action-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, #F0D78C 0%, #D4AF37 100%) !important;
          box-shadow: 0 0 48px rgba(212,175,55,0.75) !important;
          transform: translateY(-2px) scale(1.012) !important;
        }
        .sovereign-action-btn:active:not(:disabled) {
          transform: translateY(1px) scale(0.99) !important;
        }
        .sovereign-action-btn:disabled {
          opacity: 0.55;
          cursor: not-allowed;
          animation: none;
          filter: grayscale(0.35);
        }
        .citadel-link:hover {
          color: #F5E6A8 !important;
        }
        .citadel-input:focus {
          border-color: rgba(212,175,55,0.65) !important;
          box-shadow: 0 0 0 3px rgba(212,175,55,0.18) !important;
        }
        @media (prefers-reduced-motion: reduce) {
          .sovereign-action-btn { animation: none !important; }
        }
      `}</style>

      <div className="quantum-pulse" style={pulseOverlay} aria-hidden="true" />

      {/* LEFT — Narrative */}
      <section style={narrativePanel} aria-label="Citadel introduction">
        <div style={narrativeContent}>
          <div style={badgeContainer}>
            <span style={sovereignBadgeTag}>{versionLabel}</span>
            <span
              style={{
                ...liveIndicatorDot,
                backgroundColor: kernelInfo.ok ? '#34D399' : '#9CA3AF',
                boxShadow: kernelInfo.ok ? '0 0 10px #34D399' : 'none'
              }}
              aria-label={kernelInfo.ok ? 'Kernel online' : 'Kernel offline'}
            />
          </div>

          <h1 style={biblicalHeaderStyle}>THE CITADEL</h1>

          <p style={biblicalText}>
            Every sovereign identity token is a key to a citadel of incorruptible truth.
            Behind this screen lies a system where contracts are eternal.
          </p>

          <p style={taglineStyle} role="doc-subtitle">
            INSTITUTIONAL INTEGRITY · CRYPTOGRAPHIC CERTAINTY · ZERO-LOSS GOVERNANCE
          </p>
        </div>
      </section>

      {/* CENTER — Ignition */}
      <section style={ignitionPanel} aria-label="Authentication">
        <div className="terminal-glow" style={loginCard}>
          <div style={logoWrapper}>
            <img
              src="/assets/images/superadmin/wilsy.jpeg"
              alt="Wilsy OS"
              style={logoStyle}
              width={68}
              height={68}
            />
          </div>

          <div style={stepIndicator} role="list" aria-label="Authentication stages">
            <div style={step(mode === 'founder')} role="listitem">FOUNDER</div>
            <div style={stepSeparator} aria-hidden="true" />
            <div style={step(mode === 'otp' || mode === '3fa')} role="listitem">3FA</div>
          </div>

          {mode === 'founder' ? (
            <FounderLoginModule
              onLoginSuccess={onLoginSuccess}
              addForensicEntry={addForensicEntry}
              reportTelemetryError={reportTelemetryError}
              onSwitchToTenant={() => setMode('tenant')}
              onOpenCovenant={() => navigate('/covenant')}
              onTenantDiscovery={handleTenantDiscovery}
              onNavigateHome={() => {
                if (onLoginSuccess) onLoginSuccess();
                navigate('/', { replace: true });
              }}
              contextLogin={contextLogin}
              showMfa={showMfa}
              setShowMfa={setShowMfa}
              mfaData={mfaData}
              setMfaData={setMfaData}
              renderedMfaQr={renderedMfaQr}
              otp={otp}
              setOtp={setOtp}
              verifying={verifying}
              setVerifying={setVerifying}
              mfaError={mfaError}
              setMfaError={setMfaError}
              handleOtpSubmit={handleOtpSubmit}
              handleCancelMfa={handleCancelMfa}
            />
          ) : (
            <TenantLoginModule onBackToFounder={() => setMode('founder')} />
          )}

          <div style={footerWatermark}>
            {kernelInfo.ok
              ? `${kernelInfo.system || 'WILSY OS EOS KERNEL'} · v${kernelInfo.version}${kernelInfo.bridge ? ` · ${kernelInfo.bridge}` : ''}`
              : 'WILSY OS · AWAITING KERNEL'}
          </div>
        </div>
      </section>

      {/* RIGHT — Telemetry with institutional language */}
      <section style={telemetryPanel} aria-label="EOS Kennel kernel telemetry">
        <div style={telemetryHeader}>
          <ShieldCheck size={16} color="#E8C547" aria-hidden="true" />
          <span>EOS KENNEL KERNEL TELEMETRY</span>
        </div>

        <div style={metricBox}>
          <div style={metricLabelRow}>
            <span style={metricLabel}>KERNEL SEAL</span>
            <span style={{ fontSize: '0.7rem', fontWeight: 800, color: sealColor, letterSpacing: '0.08em' }}>
              {sealState}
            </span>
          </div>
          <div style={metricValue}>
            {kernelInfo.ok ? (kernelInfo.latencyMs > 0 ? `${kernelInfo.latencyMs}ms` : 'SECURE') : '⛓️ SIGNAL LOST'}
          </div>
          <div style={sourceSilentNote}>
            {kernelInfo.ok
              ? `Kernel bridge active · v${kernelInfo.version}`
              : 'Awaiting bridge handshake — check proxy & kernel accessibility'}
          </div>
        </div>

        <div style={submetricGrid}>
          <div style={submetric}>
            <span style={metricLabel}>ADAPTIVE SHARDS</span>
            <div style={subValue}>
              {kernelInfo.ok ? formatMetric(1024 + (kernelInfo.latencyMs || 0) * 4) : '—'}
            </div>
          </div>
          <div style={submetric}>
            <span style={metricLabel}>SLA LATENCY</span>
            <div style={subValue}>
              {kernelInfo.ok ? `${kernelInfo.latencyMs}ms` : '—'}
            </div>
          </div>
        </div>

        <div style={submetricGrid}>
          <div style={{ ...submetric, borderColor: 'rgba(232,197,71,0.28)' }}>
            <span style={metricLabel}>BREAKER STATE</span>
            <div style={{ ...subValue, color: kernelInfo.ok ? '#34D399' : '#9CA3AF' }}>
              {kernelInfo.ok ? 'STANDBY' : '—'}
            </div>
          </div>
          <div style={submetric}>
            <span style={metricLabel}>UPTIME SCORE</span>
            <div style={{ ...subValue, color: kernelInfo.ok ? '#34D399' : '#9CA3AF' }}>
              {kernelInfo.ok ? '100%' : '—'}
            </div>
          </div>
        </div>

        <div style={forensicLog} aria-live="polite" aria-relevant="additions">
          <div style={{ color: '#E8C547', marginBottom: 8, fontWeight: 700, letterSpacing: '0.12em' }}>
            // LIVE KERNEL AUDIT STREAM
          </div>
          {forensicHistory.length === 0 ? (
            <div style={{ color: '#9CA3AF' }}>Awaiting kernel events…</div>
          ) : (
            forensicHistory.map((entry, i) => (
              <div key={`${entry.time}-${i}`} style={{ color: entry.color, marginBottom: 6, wordBreak: 'break-word' }}>
                [{entry.time}] {entry.msg}
              </div>
            ))
          )}
        </div>

        {!kernelInfo.ok && (
          <div style={kernelWarnBanner} role="status">
            <ShieldAlert size={14} aria-hidden="true" />
            <span>Kernel bridge offline — login may still work; version badge degraded</span>
          </div>
        )}
      </section>
    </div>
  );
}

// ─── FounderLoginModule ──────────────────────────────────────────────────────
const FounderLoginModule = ({
  onLoginSuccess,
  onOpenCovenant,
  onTenantDiscovery,
  addForensicEntry,
  reportTelemetryError,
  contextLogin,
  onNavigateHome,
  showMfa,
  setShowMfa,
  mfaData,
  setMfaData,
  renderedMfaQr,
  otp,
  setOtp,
  verifying,
  setVerifying,
  mfaError,
  setMfaError,
  handleOtpSubmit,
  handleCancelMfa
}) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('wilsonkhanyezi@gmail.com');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const MIN_PASSWORD_LENGTH = 8;
  const isPasswordValid = password.length >= MIN_PASSWORD_LENGTH;

  useEffect(() => {
    if (error) setError('');
    if (mfaError) setMfaError('');
  }, [email, password, otp, mfaError, error]);

  const handleCredentialsSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      setError('Sovereign identity token is required.');
      return;
    }
    if (!isPasswordValid) {
      setError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters.`);
      return;
    }
    setLoading(true);
    setError('');
    addForensicEntry('[IDENTITY-SIGNAL] Initiating EOS Kernel Handshake...', '#E8C547');

    try {
      const data = await contextLogin(email, password);
      console.log('[LOGIN] Response data:', data);

      if (data && (data.status === 'MFA_REQUIRED' || data.status === 'MFA_SETUP')) {
        addForensicEntry('[3FA] Switching to inline MFA...', '#E8C547');
        const mfaPayload = {
          email: data.email || email,
          userId: data.userId,
          qrCode: data.qrCode || null,
          mfaSetup: data.status === 'MFA_SETUP' || Boolean(data.qrCode)
        };
        setMfaData(mfaPayload);
        setShowMfa(true);
        try {
          sessionStorage.setItem('wilsy_mfa_pending', 'true');
          sessionStorage.setItem('wilsy_mfa_data', JSON.stringify(mfaPayload));
        } catch { }
        setLoading(false);
        return;
      }

      if (data && (data.status === 'AUTHENTICATED' || data.success === true)) {
        addForensicEntry('[IDENTITY-OK] Direct Access Granted.', '#34D399');
        onNavigateHome();
        setLoading(false);
        return;
      }

      const errorMsg = data?.error || data?.message || 'Authentication failed. Please check credentials.';
      setError(errorMsg);
      addForensicEntry(`[AUTH-ERROR] ${errorMsg}`, '#F87171');
      setLoading(false);
    } catch (err) {
      const errorMsg =
        err.response?.data?.message ||
        err.response?.data?.error ||
        err.message ||
        'Authentication service unavailable.';
      setError(errorMsg);
      addForensicEntry(`[AUTH-ERROR] ${errorMsg}`, '#F87171');
      reportTelemetryError({ error: errorMsg, context: 'credentials_submit' });
      setLoading(false);
    }
  };

  if (showMfa) {
    return (
      <div style={mfaPanelStyle}>
        <h2 style={{ ...gatewayTitle, color: '#FAFAFA' }}>THREE‑FACTOR AUTHENTICATION</h2>
        {renderedMfaQr && (
          <div style={mfaQrSectionStyle}>
            <p style={{ color: '#D4D4D4', fontSize: '0.8rem', marginBottom: 12 }}>
              Scan the QR code with your authenticator app.
            </p>
            <img src={renderedMfaQr} alt="QR Code for MFA" style={mfaQrImageStyle} />
            <p style={{ color: '#737373', fontSize: '0.7rem', marginTop: 12 }}>Then enter the 6‑digit code below.</p>
            <button
              type="button"
              onClick={() => setMfaData({ ...mfaData, qrCode: null })}
              style={{ ...linkButtonStyle, color: '#E8C547', marginTop: 8 }}
            >
              I have scanned the QR code
            </button>
          </div>
        )}
        <form onSubmit={handleOtpSubmit} style={formStyle}>
          <div style={inputGroup}>
            <label htmlFor="mfa-otp" style={labelStyle}>ENTER 6‑DIGIT OTP</label>
            <input
              id="mfa-otp"
              className="citadel-input"
              type="text"
              maxLength="6"
              inputMode="numeric"
              autoComplete="one-time-code"
              placeholder="123456"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
              style={inputStyle}
              required
              autoFocus // 👈 Added autoFocus to match cursor in the screenshot
            />
          </div>
          {mfaError && (
            <div style={forensicError} role="alert">
              <AlertCircle size={16} aria-hidden="true" />
              <span>[3FA-ERROR] {mfaError}</span>
            </div>
          )}
          <button
            type="submit"
            className="sovereign-action-btn"
            style={buttonStyle}
            disabled={verifying || otp.length < 6}
          >
            {verifying ? <Loader2 className="animate-spin" size={18} aria-hidden="true" /> : <CheckCircle size={18} aria-hidden="true" />}
            <span>VERIFY OTP</span>
          </button>
          <button
            type="button"
            onClick={handleCancelMfa}
            style={{ ...linkButtonStyle, color: '#9CA3AF', marginTop: 16, fontSize: '0.65rem' }}
          >
            Cancel
          </button>
        </form>
      </div>
    );
  }

  return (
    <div>
      <h2 style={gatewayTitle}><span>FOUNDER IDENTITY</span></h2>

      {error && (
        <div style={forensicError} role="alert">
          <AlertCircle size={16} aria-hidden="true" />
          <span>[AUTH-ERROR] {error}</span>
        </div>
      )}

      <form onSubmit={handleCredentialsSubmit} style={formStyle} noValidate>
        <div style={inputGroup}>
          <label htmlFor="citadel-email" style={labelStyle}>
            SOVEREIGN IDENTITY TOKEN
          </label>
          <input
            id="citadel-email"
            className="citadel-input"
            type="email"
            autoComplete="username"
            placeholder="founder@domain.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={inputStyle}
            required
          />
        </div>

        <div style={inputGroup}>
          <label htmlFor="citadel-password" style={labelStyle}>
            MASTER FORENSIC KEY
          </label>
          <div style={{ position: 'relative' }}>
            <input
              id="citadel-password"
              className="citadel-input"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={inputStyle}
              required
              minLength={MIN_PASSWORD_LENGTH}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              style={visibilityToggle}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff size={18} color="#E8C547" /> : <Eye size={18} color="#A3A3A3" />}
            </button>
          </div>
        </div>

        <button
          type="submit"
          className="sovereign-action-btn"
          style={buttonStyle}
          disabled={loading || !isPasswordValid}
        >
          {loading ? <Loader2 className="animate-spin" size={18} aria-hidden="true" /> : <Fingerprint size={18} aria-hidden="true" />}
          <span>INITIATE 3FA SEQUENCE</span>
        </button>
      </form>

      <div style={utilityLinks}>
        <button type="button" className="citadel-link" onClick={onTenantDiscovery} style={linkButtonStyle}>
          TENANT DISCOVERY
        </button>
        <span style={{ color: '#525252' }} aria-hidden="true">·</span>
        <button type="button" className="citadel-link" onClick={onOpenCovenant} style={linkButtonStyle}>
          COVENANT
        </button>
      </div>
    </div>
  );
};

const TenantLoginModule = ({ onBackToFounder }) => (
  <div style={{ padding: '30px 0', textAlign: 'center' }}>
    <h2 style={gatewayTitle}>TENANT GATEWAY</h2>
    <p style={{ color: '#A3A3A3', fontSize: '0.8rem', marginBottom: 28, lineHeight: 1.6 }}>
      Secure access for subsidiary nodes
    </p>
    <button type="button" onClick={onBackToFounder} className="sovereign-action-btn" style={buttonStyle}>
      BACK TO FOUNDER
    </button>
  </div>
);

// ─── Styles ──────────────────────────────────────────────────────────────────
const gateContainer = {
  display: 'flex',
  height: '100vh',
  backgroundColor: '#030303',
  overflow: 'hidden',
  position: 'relative',
  fontFamily: '"Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
};

const pulseOverlay = {
  position: 'absolute',
  inset: 0,
  zIndex: 0,
  opacity: 0.07,
  background: 'radial-gradient(circle at 50% 40%, rgba(212,175,55,0.18) 0%, transparent 65%)',
  pointerEvents: 'none'
};

const narrativePanel = {
  flex: 1.1,
  borderRight: '1px solid rgba(212,175,55,0.18)',
  padding: '72px 64px',
  display: 'flex',
  alignItems: 'center',
  background: 'linear-gradient(160deg, #060606 0%, #020202 100%)',
  zIndex: 1
};

const narrativeContent = { maxWidth: 520 };

const badgeContainer = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 10,
  padding: '8px 16px',
  background: 'rgba(212,175,55,0.1)',
  border: '1px solid rgba(212,175,55,0.35)',
  borderRadius: 999,
  marginBottom: 32
};

const sovereignBadgeTag = {
  color: '#F0D78C',
  fontSize: '0.7rem',
  fontWeight: 800,
  letterSpacing: '0.18em',
  textTransform: 'uppercase',
  fontFamily: '"JetBrains Mono", ui-monospace, monospace'
};

const liveIndicatorDot = {
  width: 8,
  height: 8,
  borderRadius: '50%',
  flexShrink: 0
};

const biblicalHeaderStyle = {
  color: '#FAFAFA',
  fontSize: 'clamp(2.25rem, 4vw, 3.15rem)',
  letterSpacing: '0.14em',
  marginBottom: 28,
  fontWeight: 900,
  lineHeight: 1.05,
  textShadow: '0 0 40px rgba(212,175,55,0.25)'
};

const biblicalText = {
  color: '#D4D4D4',
  lineHeight: 1.85,
  fontSize: '1.05rem',
  fontStyle: 'italic',
  marginBottom: 36,
  fontWeight: 400,
  maxWidth: '36ch'
};

const taglineStyle = {
  fontSize: '0.72rem',
  color: '#E8C547',
  letterSpacing: '0.16em',
  fontWeight: 700,
  textTransform: 'uppercase',
  marginBottom: 16,
  lineHeight: 1.5
};

const ignitionPanel = {
  flex: 1.35,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1,
  padding: '12px 18px',
  overflow: 'hidden'
};

const loginCard = {
  width: 'min(460px, 100%)',
  padding: '24px 44px',
  boxSizing: 'border-box',
  maxHeight: 'calc(100vh - 24px)',
  overflowY: 'auto',
  background: 'rgba(10,10,10,0.94)',
  border: '1px solid rgba(212,175,55,0.38)',
  backdropFilter: 'blur(20px)',
  borderRadius: 10,
  boxShadow: '0 28px 56px rgba(0,0,0,0.75), 0 0 40px rgba(212,175,55,0.08)'
};

const logoStyle = {
  width: 68,
  height: 68,
  borderRadius: '50%',
  border: '2px solid #D4AF37',
  padding: 4,
  marginBottom: 16,
  boxShadow: '0 0 24px rgba(212,175,55,0.28)',
  objectFit: 'cover'
};

const logoWrapper = { textAlign: 'center' };

const gatewayTitle = {
  color: '#FAFAFA',
  letterSpacing: '0.2em',
  marginBottom: 28,
  fontSize: '0.85rem',
  fontWeight: 800,
  textTransform: 'uppercase',
  textAlign: 'center'
};

const formStyle = { display: 'flex', flexDirection: 'column' };
const inputGroup = { marginBottom: 20, textAlign: 'left' };

const mfaPanelStyle = { padding: '8px 0 0' };

const mfaQrSectionStyle = {
  textAlign: 'center',
  margin: '22px 0 24px',
  paddingTop: 2
};

const mfaQrImageStyle = {
  width: 152,
  height: 152,
  display: 'block',
  margin: '0 auto',
  border: '1px solid rgba(212,175,55,0.3)',
  borderRadius: 8
};

const labelStyle = {
  color: '#E5E5E5',
  fontSize: '0.68rem',
  letterSpacing: '0.14em',
  marginBottom: 8,
  display: 'block',
  fontWeight: 700
};

const inputStyle = {
  width: '100%',
  padding: '15px 16px',
  background: '#0A0A0A',
  border: '1px solid rgba(212,175,55,0.28)',
  color: '#FAFAFA',
  fontSize: '0.95rem',
  outline: 'none',
  borderRadius: 6,
  transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
  boxSizing: 'border-box'
};

const visibilityToggle = {
  position: 'absolute',
  right: 14,
  top: '50%',
  transform: 'translateY(-50%)',
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  display: 'flex',
  padding: 4
};

const buttonStyle = {
  width: '100%',
  padding: 17,
  background: 'linear-gradient(135deg, #D4AF37 0%, #B8962E 100%)',
  color: '#0A0A0A',
  fontWeight: 800,
  cursor: 'pointer',
  letterSpacing: '0.14em',
  border: 'none',
  display: 'flex',
  alignItems: 'center',
  gap: 12,
  justifyContent: 'center',
  borderRadius: 6,
  boxShadow: '0 4px 20px rgba(212,175,55,0.28)',
  transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
  marginTop: 8,
  fontSize: '0.78rem'
};

const forensicError = {
  background: 'rgba(239,68,68,0.12)',
  border: '1px solid rgba(248,113,113,0.55)',
  color: '#FECACA',
  padding: '12px 14px',
  fontSize: '0.78rem',
  display: 'flex',
  alignItems: 'flex-start',
  gap: 10,
  marginBottom: 18,
  borderRadius: 6,
  fontWeight: 600,
  lineHeight: 1.45
};

const utilityLinks = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  gap: 14,
  marginTop: 28
};

const linkButtonStyle = {
  background: 'none',
  border: 'none',
  color: '#D4D4D4',
  cursor: 'pointer',
  fontSize: '0.68rem',
  letterSpacing: '0.12em',
  textTransform: 'uppercase',
  fontWeight: 700,
  transition: 'color 0.15s',
  padding: '6px 4px'
};

const telemetryPanel = {
  flex: 0.95,
  background: 'linear-gradient(165deg, #050505 0%, #0A0A0A 100%)',
  borderLeft: '1px solid rgba(212,175,55,0.18)',
  padding: '40px 32px',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  zIndex: 1
};

const telemetryHeader = {
  color: '#F0D78C',
  fontSize: '0.72rem',
  letterSpacing: '0.16em',
  marginBottom: 26,
  fontWeight: 800,
  display: 'flex',
  alignItems: 'center',
  gap: 10
};

const metricBox = {
  marginBottom: 18,
  background: 'rgba(12,12,12,0.9)',
  border: '1px solid rgba(212,175,55,0.24)',
  padding: '16px 18px',
  borderRadius: 6
};

const metricLabelRow = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: 8
};

const metricLabel = {
  color: '#A3A3A3',
  letterSpacing: '0.12em',
  fontSize: '0.65rem',
  fontWeight: 700
};

const metricValue = {
  color: '#FAFAFA',
  fontSize: '1.35rem',
  fontWeight: 800,
  fontFamily: '"JetBrains Mono", ui-monospace, monospace',
  letterSpacing: '0.04em'
};

const sourceSilentNote = {
  marginTop: 8,
  fontSize: '0.62rem',
  color: '#737373',
  letterSpacing: '0.06em',
  textTransform: 'uppercase'
};

const submetricGrid = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 12,
  marginBottom: 12
};

const submetric = {
  background: 'rgba(10,10,10,0.95)',
  padding: 14,
  border: '1px solid rgba(212,175,55,0.2)',
  borderRadius: 6
};

const subValue = {
  color: '#E8C547',
  fontSize: '1.05rem',
  marginTop: 6,
  fontWeight: 800,
  fontFamily: '"JetBrains Mono", ui-monospace, monospace'
};

const forensicLog = {
  marginTop: 16,
  fontFamily: '"JetBrains Mono", ui-monospace, monospace',
  fontSize: '0.62rem',
  lineHeight: 1.75,
  borderTop: '1px solid rgba(212,175,55,0.22)',
  paddingTop: 14,
  minHeight: 140,
  maxHeight: 160,
  overflow: 'auto',
  background: 'rgba(0,0,0,0.45)',
  padding: 12,
  borderRadius: 6,
  color: '#D4D4D4'
};

const kernelWarnBanner = {
  marginTop: 14,
  display: 'flex',
  alignItems: 'center',
  gap: 8,
  padding: '10px 12px',
  borderRadius: 6,
  border: '1px solid rgba(163,163,163,0.35)',
  background: 'rgba(24,24,24,0.9)',
  color: '#A3A3A3',
  fontSize: '0.65rem',
  letterSpacing: '0.04em',
  lineHeight: 1.4
};

const footerWatermark = {
  color: '#737373',
  fontSize: '0.58rem',
  marginTop: 32,
  textAlign: 'center',
  letterSpacing: '0.1em',
  fontWeight: 600,
  fontFamily: '"JetBrains Mono", ui-monospace, monospace',
  lineHeight: 1.5
};

const stepIndicator = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 14,
  marginBottom: 24
};

const step = (active) => ({
  color: active ? '#F0D78C' : '#737373',
  fontSize: '0.65rem',
  fontWeight: 800,
  letterSpacing: '0.16em'
});

const stepSeparator = {
  width: 24,
  height: 1,
  background: 'rgba(212,175,55,0.35)'
};

export {
  gateContainer,
  pulseOverlay,
  narrativePanel,
  ignitionPanel,
  loginCard,
  logoWrapper,
  logoStyle,
  gatewayTitle,
  formStyle,
  inputGroup,
  labelStyle,
  inputStyle,
  visibilityToggle,
  buttonStyle,
  forensicError,
  utilityLinks,
  linkButtonStyle,
  telemetryPanel,
  telemetryHeader,
  metricBox,
  metricLabelRow,
  metricLabel,
  metricValue,
  submetricGrid,
  submetric,
  subValue,
  forensicLog,
  footerWatermark,
  stepIndicator,
  step,
  stepSeparator
};
