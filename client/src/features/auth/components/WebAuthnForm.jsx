/**
 * File: client/src/features/auth/components/WebAuthnForm.jsx
 * PATH: client/src/features/auth/components/WebAuthnForm.jsx
 * STATUS: EPITOME | PRODUCTION-READY | BIOMETRIC AUTH (feature-flagged)
 * VERSION: 1.0.0
 * -----------------------------------------------------------------------------
 * PURPOSE
 * - A production-ready, accessible, and extensible WebAuthn UI component.
 * - Acts as a safe placeholder when WebAuthn is disabled by policy or unsupported.
 * - Provides a clear integration surface for real WebAuthn flows (registration & login).
 *
 * KEY FEATURES
 * - Feature-flag driven: enable via env or runtime config (REACT_APP_WEBAUTHN_ENABLED).
 * - Capability detection: gracefully degrades when browser/platform doesn't support WebAuthn.
 * - Accessibility: ARIA roles, keyboard focus, and clear status messages.
 * - Pluggable handlers: `onAuthenticate` and `onRegister` callbacks for wiring to services.
 * - Secure UX: never stores credentials client-side; delegates to server endpoints.
 * - Testable: small pure helpers separated for unit testing.
 *
 * COLLABORATION & OWNERSHIP
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend (component maintenance)
 * - SECURITY: @security (WebAuthn flow review, origin checks)
 * - BACKEND: @backend-team (server endpoints: /webauthn/register, /webauthn/authenticate)
 * - QA: @qa (unit + E2E tests)
 * - PRODUCT: @product (UX acceptance)
 *
 * REVIEW & DEPLOYMENT GATES
 * - Security review required before enabling in production.
 * - Backend must implement and document WebAuthn endpoints and challenge lifecycle.
 * - Add integration tests that exercise registration and authentication flows in staging.
 *
 * INTEGRATION CONTRACT (server)
 * - Registration flow:
 *   1. Client requests POST /webauthn/register/begin { userId }
 *   2. Server returns PublicKeyCredentialCreationOptions (challenge, rp, user, pubKeyCredParams, etc.)
 *   3. Client calls navigator.credentials.create(options) and POSTs result to /webauthn/register/complete
 * - Authentication flow:
 *   1. Client requests POST /webauthn/authenticate/begin { userId }
 *   2. Server returns PublicKeyCredentialRequestOptions (challenge, allowCredentials, etc.)
 *   3. Client calls navigator.credentials.get(options) and POSTs result to /webauthn/authenticate/complete
 *
 * TESTS
 * - Unit tests: tests/features/auth/WebAuthnForm.unit.test.jsx
 *   * Capability detection, UI states, callback invocation, fallback messaging.
 * - Integration/E2E: tests/e2e/auth/webauthn.spec.js (run in browsers that support WebAuthn)
 *
 * SECURITY NOTES
 * - Ensure origin and RP ID are correctly configured on the server.
 * - Use HTTPS in production; WebAuthn requires secure contexts.
 * - Do not expose raw challenges in logs.
 * - Prefer relying on server-side session or short-lived tokens to complete flows.
 *
 * USAGE
 * - Import and place in login or account security pages:
 *     <WebAuthnForm
 *       userId={userId}
 *       onAuthenticate={handleAuthenticate}
 *       onRegister={handleRegister}
 *       enabled={process.env.REACT_APP_WEBAUTHN_ENABLED === 'true'}
 *     />
 *
 * -----------------------------------------------------------------------------
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { FiShield, FiCheckCircle, FiXCircle, FiInfo } from 'react-icons/fi';

/* -------------------------
   Styled components
   ------------------------- */

const Container = styled.div`
  padding: 1rem;
  text-align: left;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  color: #0f172a;
  margin-top: 1rem;
  background: #ffffff;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
`;

const Title = styled.h4`
  margin: 0;
  font-size: 1rem;
  color: #0f172a;
`;

const Body = styled.div`
  font-size: 0.9rem;
  color: #475569;
`;

const Actions = styled.div`
  margin-top: 0.75rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
`;

const Button = styled.button`
  background: ${(p) => (p.primary ? '#0ea5a4' : 'transparent')};
  color: ${(p) => (p.primary ? '#fff' : '#0f172a')};
  border: 1px solid #cbd5e1;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

/* -------------------------
   Small helpers (pure, testable)
   ------------------------- */

/**
 * isWebAuthnSupported
 * - Returns true if the current environment supports WebAuthn APIs.
 */
export function isWebAuthnSupported() {
  return typeof window !== 'undefined' && !!(window.PublicKeyCredential && typeof window.PublicKeyCredential === 'function');
}

/* -------------------------
   Component
   ------------------------- */

export default function WebAuthnForm({
  userId,
  enabled,
  onAuthenticate,
  onRegister,
  className,
  ariaLabel
}) {
  const supported = useMemo(() => isWebAuthnSupported(), []);
  const active = Boolean(enabled) && supported;

  const [status, setStatus] = useState({ state: 'idle', message: null }); // idle | pending | success | error
  const [lastError, setLastError] = useState(null);

  useEffect(() => {
    // Reset transient state when enabled/support changes
    setStatus({ state: 'idle', message: null });
    setLastError(null);
  }, [active, userId]);

  const handleRegister = useCallback(async () => {
    if (!active) return;
    setStatus({ state: 'pending', message: 'Starting registration...' });
    setLastError(null);

    try {
      // Delegate to caller: they should implement server roundtrip and navigator.credentials.create
      // onRegister should return a promise that resolves with { success: true } or rejects with error
      if (typeof onRegister !== 'function') {
        throw new Error('onRegister handler not provided');
      }
      const result = await onRegister({ userId });
      if (result && result.success) {
        setStatus({ state: 'success', message: 'Biometric credential registered' });
      } else {
        setStatus({ state: 'error', message: result && result.message ? result.message : 'Registration failed' });
      }
    } catch (err) {
      setLastError(err);
      setStatus({ state: 'error', message: err && err.message ? err.message : 'Registration error' });
    }
  }, [active, onRegister, userId]);

  const handleAuthenticate = useCallback(async () => {
    if (!active) return;
    setStatus({ state: 'pending', message: 'Starting authentication...' });
    setLastError(null);

    try {
      if (typeof onAuthenticate !== 'function') {
        throw new Error('onAuthenticate handler not provided');
      }
      const result = await onAuthenticate({ userId });
      if (result && result.success) {
        setStatus({ state: 'success', message: 'Authentication successful' });
      } else {
        setStatus({ state: 'error', message: result && result.message ? result.message : 'Authentication failed' });
      }
    } catch (err) {
      setLastError(err);
      setStatus({ state: 'error', message: err && err.message ? err.message : 'Authentication error' });
    }
  }, [active, onAuthenticate, userId]);

  // UI states
  const isPending = status.state === 'pending';
  const isSuccess = status.state === 'success';
  const isError = status.state === 'error';

  return (
    <Container className={className} role="region" aria-label={ariaLabel || 'Biometric authentication'}>
      <Header>
        <FiShield size={20} aria-hidden="true" />
        <Title>Biometric Login (WebAuthn)</Title>
      </Header>

      <Body>
        {!enabled && (
          <div aria-live="polite">
            <FiInfo style={{ verticalAlign: 'middle', marginRight: 6 }} />
            <strong>Disabled by policy.</strong>
            <div style={{ marginTop: 6 }}>
              This organization has disabled biometric login. Contact your administrator to enable.
            </div>
          </div>
        )}

        {enabled && !supported && (
          <div aria-live="polite">
            <FiInfo style={{ verticalAlign: 'middle', marginRight: 6 }} />
            <strong>Not supported in this browser.</strong>
            <div style={{ marginTop: 6 }}>
              Your browser or device does not support WebAuthn. Use a modern browser or a device with platform authenticators.
            </div>
          </div>
        )}

        {enabled && supported && (
          <>
            <div aria-live="polite" style={{ marginBottom: 8 }}>
              Use a hardware key or platform authenticator (FaceID/TouchID) to register or sign in.
            </div>

            {isSuccess && (
              <div role="status" aria-live="polite" style={{ color: '#059669', display: 'flex', alignItems: 'center', gap: 8 }}>
                <FiCheckCircle /> {status.message}
              </div>
            )}

            {isError && (
              <div role="alert" aria-live="assertive" style={{ color: '#dc2626', display: 'flex', alignItems: 'center', gap: 8 }}>
                <FiXCircle /> {status.message}
              </div>
            )}

            {isPending && (
              <div role="status" aria-live="polite" style={{ color: '#0ea5a4' }}>
                {status.message}
              </div>
            )}

            <Actions>
              <Button
                type="button"
                onClick={handleRegister}
                disabled={isPending}
                aria-disabled={isPending}
                title="Register a new biometric credential"
              >
                Register credential
              </Button>

              <Button
                type="button"
                onClick={handleAuthenticate}
                disabled={isPending}
                aria-disabled={isPending}
                primary
                title="Authenticate using a registered credential"
              >
                Sign in with biometrics
              </Button>
            </Actions>

            {/* Developer debug info (hidden in production) */}
            {process.env.NODE_ENV !== 'production' && lastError && (
              <pre style={{ marginTop: 8, fontSize: 12, color: '#ef4444' }}>
                {String(lastError && lastError.stack ? lastError.stack : lastError)}
              </pre>
            )}
          </>
        )}
      </Body>
    </Container>
  );
}

/* -------------------------
   PropTypes & defaults
   ------------------------- */

WebAuthnForm.propTypes = {
  userId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  enabled: PropTypes.bool, // feature flag: enable WebAuthn UI
  onAuthenticate: PropTypes.func, // async handler: ({ userId }) => Promise<{ success, message }>
  onRegister: PropTypes.func, // async handler: ({ userId }) => Promise<{ success, message }>
  className: PropTypes.string,
  ariaLabel: PropTypes.string
};

WebAuthnForm.defaultProps = {
  userId: null,
  enabled: process.env.REACT_APP_WEBAUTHN_ENABLED === 'true',
  onAuthenticate: null,
  onRegister: null,
  className: '',
  ariaLabel: null
};
