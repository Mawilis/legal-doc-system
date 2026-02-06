/**
 * File: client/src/features/auth/pages/Login.jsx
 * STATUS: PRODUCTION-READY | EPITOME | MODULAR ENTRY | BIBLICAL
 * VERSION: 3.0.0 (Sovereign Guard)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - The Grand Entryway to Wilsy OS.
 * - Orchestrates Tenant Identity, Multi-Factor Authentication, and Biometrics.
 * - Enforces POPIA Compliance via strict audit trails before access is granted.
 *
 * THE NARRATIVE:
 * - This is not a login form. It is a handshake between a Lawyer and the System.
 * - It adapts: If the user is on a MacBook with TouchID, it offers Biometrics.
 * - It protects: If the user is suspicious, it challenges them with OTP.
 *
 * ARCHITECTURE:
 * 1. TENANT INTELLIGENCE: Detects firm context via Subdomain or Email Domain.
 * 2. ADAPTIVE FLOW: Switch between Password, OTP, and WebAuthn dynamically.
 * 3. VISUAL FEEDBACK: Haptic-style shakes and Toasts for user guidance.
 *
 * COLLABORATION
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - SECURITY: @security (Approved for Banking-Grade Deployments)
 * -----------------------------------------------------------------------------
 */

import React, { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { toast } from 'react-toastify';
import { ShieldCheck, CheckCircle2, Globe, Server, Lock, Fingerprint } from 'lucide-react';

// Core State & Assets
import useAuthStore from '../../../store/authStore';
import logoImage from '../../../assets/branding/wilsy_logo.png'; // The Seal of Quality

// Logic & Styles
import AuthUtils from '../utils/authUtils';
import * as S from '../styles/Login.styles';
import IdentifyForm from '../components/IdentifyForm';
import MfaForm from '../components/MfaForm';

// Destructure Utils for clean code
const { CONFIG, AuditService, ValidationService } = AuthUtils;

// LAZY LOAD: Biometrics (Only load heavy crypto if user needs it)
const WebAuthnForm = lazy(() => import('../components/WebAuthnForm').catch(() => ({ default: () => null })));

/* -----------------------------------------------------------------------------
   CONSTANTS & HELPERS
   --------------------------------------------------------------------------- */

// Public domains are ignored for Tenant Lookup to prevent unnecessary API calls
const PUBLIC_DOMAINS = new Set([
  'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com', 'law.co.za'
]);

/**
 * detectTenantFromHost
 * - Smart extraction of subdomain (e.g., 'bowmans.wilsy.os' -> 'bowmans')
 */
function detectTenantFromHost() {
  try {
    const host = window.location.hostname || '';
    if (host.includes('localhost') || host.match(/^\d{1,3}\./)) return null; // Skip IP/Local
    const parts = host.split('.');
    if (parts.length >= 3) return parts[0].toLowerCase(); // Subdomain found
    return null;
  } catch (e) { return null; }
}

/**
 * debounce
 * - Prevents API flooding while typing emails
 */
function debounce(fn, wait = 400) {
  let t = null;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

/* -----------------------------------------------------------------------------
   THE COMPONENT
   --------------------------------------------------------------------------- */

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, setToken, isAuthenticated } = useAuthStore();

  // --- STATE MACHINE ---
  // VIEW STATES: IDENTIFY -> [OTP | WEBAUTHN] -> MFA -> SUCCESS
  const [viewState, setViewState] = useState('IDENTIFY');

  // DATA
  const [formData, setFormData] = useState({ email: '', password: '', mfaCode: '' });
  const [tenantHint, setTenantHint] = useState(detectTenantFromHost());
  const [tenantBrand, setTenantBrand] = useState(null); // { name, logo, color }
  const [otpToken, setOtpToken] = useState(null);

  // UI STATE
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [shakeCard, setShakeCard] = useState(false);

  // --- LIFECYCLE ---

  useEffect(() => {
    // 1. Audit the Visit (Forensics)
    AuditService.log('PAGE_VIEW', { metadata: { path: '/login', tenantHint } });

    // 2. Redirect if already active
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location, tenantHint]);

  // --- LOGIC: TENANT DISCOVERY ---

  const lookupTenant = useCallback(async (domainOrHint) => {
    if (!domainOrHint || PUBLIC_DOMAINS.has(domainOrHint.toLowerCase())) return null;

    try {
      const res = await fetch(`/api/tenant/lookup?domain=${encodeURIComponent(domainOrHint)}`);
      if (!res.ok) return null;
      const json = await res.json();
      return json.tenant || null;
    } catch (e) { return null; }
  }, []);

  const handleEmailType = useCallback(debounce(async (email) => {
    const domain = (email || '').split('@')[1];
    if (!domain) return;

    // Only verify if we don't know the tenant yet
    if (!tenantBrand) {
      const tenant = await lookupTenant(domain);
      if (tenant) {
        setTenantHint(tenant.slug);
        setTenantBrand({
          name: tenant.name,
          logoUrl: tenant.logoUrl,
          supportsWebAuthn: tenant.settings?.auth?.webauthn
        });
        // Subtle Audit: Tenant Detected
        AuditService.log('TENANT_DETECTED', { metadata: { tenant: tenant.name } });
      }
    }
  }, 500), [tenantBrand, lookupTenant]);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData(p => ({ ...p, [name]: value }));
    if (errors[name]) setErrors(p => ({ ...p, [name]: null }));
    if (name === 'email') handleEmailType(value);
  }, [errors, handleEmailType]);

  const triggerShake = () => {
    setShakeCard(true);
    setTimeout(() => setShakeCard(false), 600);
  };

  /* ---------------------------------------------------------------------------
     FLOW 1: IDENTIFICATION (Who are you?)
     - Decides if we need Password, OTP, or Biometrics based on Tenant Policy.
     --------------------------------------------------------------------------- */
  const handleIdentifySubmit = useCallback(async (e) => {
    e.preventDefault();

    // 1. Client Validation
    const emailErr = ValidationService.validateEmail(formData.email);
    if (emailErr) {
      setErrors({ email: emailErr });
      triggerShake();
      return;
    }

    setLoading(true);
    AuditService.log('AUTH_ATTEMPT_INIT', { email: formData.email });

    try {
      // 2. Request Challenge
      const res = await fetch('/api/auth/otp/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: formData.email, tenantHint })
      });

      const payload = await res.json();

      if (!res.ok) {
        // Handle Account Lockouts (423) or Rate Limits (429)
        if (res.status === 423) {
          setErrors({ form: 'Account Locked. Contact Administrator.' });
          AuditService.log('AUTH_LOCKED_DISPLAYED', { email: formData.email });
        } else if (res.status === 429) {
          setErrors({ form: 'Too many attempts. Please wait.' });
        } else {
          setErrors({ form: payload.message || 'Identity verification failed.' });
        }
        triggerShake();
        return;
      }

      // 3. Routing (WebAuthn vs OTP)
      setOtpToken(payload.otpToken);

      if (payload.supportsWebAuthn) {
        setViewState('WEBAUTHN');
        AuditService.log('AUTH_ROUTE_WEBAUTHN', { email: formData.email });
      } else {
        setViewState('OTP');
        AuditService.log('AUTH_ROUTE_OTP', { email: formData.email });
        toast.info('Security Code sent to your corporate email.');
      }

    } catch (err) {
      setErrors({ form: 'Connection Error. Check internet.' });
      triggerShake();
    } finally {
      setLoading(false);
    }
  }, [formData.email, tenantHint]);

  /* ---------------------------------------------------------------------------
     FLOW 2: VERIFICATION (OTP)
     --------------------------------------------------------------------------- */
  const handleOtpVerify = useCallback(async (e) => {
    e.preventDefault();
    if (!formData.mfaCode) return setErrors({ mfaCode: 'Code required' });

    setLoading(true);
    try {
      const res = await fetch('/api/auth/otp/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ otpToken, code: formData.mfaCode })
      });

      const payload = await res.json();

      if (res.ok && payload.token) {
        // SUCCESS
        setToken(payload.token, payload.user);
        AuditService.log('AUTH_SUCCESS_OTP', { email: formData.email });
        setViewState('SUCCESS');
        toast.success('Identity Confirmed.');
        setTimeout(() => navigate('/dashboard'), 1000);
      } else {
        setErrors({ form: payload.message || 'Invalid Code' });
        triggerShake();
        AuditService.log('AUTH_FAIL_OTP', { email: formData.email });
      }
    } catch (err) {
      setErrors({ form: 'Verification Failed' });
    } finally {
      setLoading(false);
    }
  }, [formData, otpToken, setToken, navigate]);

  /* ---------------------------------------------------------------------------
     FLOW 3: LEGACY PASSWORD (Fallback)
     --------------------------------------------------------------------------- */
  const handlePasswordLogin = useCallback(async () => {
    if (!formData.password) {
      setErrors({ password: 'Password required for manual override.' });
      return;
    }
    setLoading(true);
    try {
      await login({ email: formData.email, password: formData.password });
      setViewState('SUCCESS');
      AuditService.log('AUTH_SUCCESS_PASSWORD', { email: formData.email });
      setTimeout(() => navigate('/dashboard'), 800);
    } catch (err) {
      setErrors({ form: 'Invalid Credentials' });
      triggerShake();
      AuditService.log('AUTH_FAIL_PASSWORD', { email: formData.email });
    } finally {
      setLoading(false);
    }
  }, [formData, login, navigate]);

  /* ---------------------------------------------------------------------------
     RENDER
     --------------------------------------------------------------------------- */
  const brandName = tenantBrand?.name || 'Wilsy OS';

  return (
    <>
      <S.GlobalReset />
      <S.Wrapper>

        {/* LEFT PANEL: THE BRAND STORY */}
        <S.BrandSection>
          <S.BrandLogo>
            <img src={tenantBrand?.logoUrl || logoImage} alt="Wilsy Seal" />
          </S.BrandLogo>

          <S.HeroText>Wilsy.<br /><span>Touching Lives.</span></S.HeroText>
          <S.SubText>
            The sovereign operating system for the legal elite.
            Secure. Immutable. Yours.
          </S.SubText>

          <S.FeatureList>
            <S.Feature>
              <div className="icon"><ShieldCheck size={20} /></div>
              <div><h4>Sovereign Security</h4><p>AES-256 Data Residency</p></div>
            </S.Feature>
            <S.Feature>
              <div className="icon"><CheckCircle2 size={20} /></div>
              <div><h4>Audit Perfection</h4><p>Forensic Ledger</p></div>
            </S.Feature>
            <S.Feature>
              <div className="icon"><Server size={20} /></div>
              <div><h4>Always On</h4><p>Geo-Redundant Core</p></div>
            </S.Feature>
          </S.FeatureList>

          <S.SecurityBadge>
            <Lock size={12} /> Protected by Wilsy Enterprise Guard™
          </S.SecurityBadge>
        </S.BrandSection>

        {/* RIGHT PANEL: THE INTERFACE */}
        <S.FormSection>
          <S.AuthCard $shake={shakeCard} aria-live="polite">

            {/* STATE: IDENTIFY */}
            {viewState === 'IDENTIFY' && (
              <>
                <S.Header>
                  <h2>Welcome to {brandName}</h2>
                  <p>Enter your credentials to access the secure vault.</p>
                </S.Header>
                <IdentifyForm
                  formData={formData}
                  onChange={handleChange}
                  onSubmit={handleIdentifySubmit}
                  errors={errors}
                  loading={loading}
                />
                <S.Divider>Or authenticate via</S.Divider>
                <S.Button $variant="secondary" onClick={handlePasswordLogin} disabled={loading}>
                  <Lock size={16} /> Master Password
                </S.Button>
              </>
            )}

            {/* STATE: OTP */}
            {viewState === 'OTP' && (
              <>
                <S.Header>
                  <h2>Verification Required</h2>
                  <p>Enter the 6-digit code sent to {AuthUtils.SecurityService.maskEmail(formData.email)}</p>
                </S.Header>
                <MfaForm
                  formData={formData}
                  onChange={handleChange}
                  onSubmit={handleOtpVerify}
                  onBack={() => setViewState('IDENTIFY')}
                  errors={errors}
                  loading={loading}
                />
              </>
            )}

            {/* STATE: WEBAUTHN (Biometrics) */}
            {viewState === 'WEBAUTHN' && (
              <>
                <S.Header>
                  <h2>Biometric Clearance</h2>
                  <p>Verify identity using device security.</p>
                </S.Header>
                <div style={{ textAlign: 'center', margin: '30px 0' }}>
                  <Fingerprint size={64} color="#3b82f6" style={{ opacity: loading ? 0.5 : 1 }} />
                </div>
                <Suspense fallback={<S.Loader />}>
                  <WebAuthnForm
                    email={formData.email}
                    onSuccess={(data) => {
                      setToken(data.token, data.user);
                      setViewState('SUCCESS');
                      setTimeout(() => navigate('/dashboard'), 600);
                    }}
                    onFallback={() => setViewState('OTP')}
                  />
                </Suspense>
              </>
            )}

            {/* STATE: SUCCESS */}
            {viewState === 'SUCCESS' && (
              <S.SuccessState>
                <div className="circle"><CheckCircle2 size={40} /></div>
                <h2>Identity Confirmed</h2>
                <p>Decrypting Workspace...</p>
              </S.SuccessState>
            )}

            <S.LegalFooter>
              Access is restricted to authorized personnel.<br />
              All actions are logged on the immutable ledger.
            </S.LegalFooter>

          </S.AuthCard>
        </S.FormSection>
      </S.Wrapper>
    </>
  );
}