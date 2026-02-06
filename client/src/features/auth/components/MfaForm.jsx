/**
 * File: client/src/features/auth/components/MfaForm.jsx
 * STATUS: PRODUCTION-READY | EPITOME | TENANT-FACING
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Multi-Factor Authentication (OTP) step component used in the Wilsy OS login flow.
 * - Focused on accessibility, UX clarity, and audit telemetry (client-side).
 *
 * COLLABORATION COMMENTS:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @security, @frontend, @accessibility, @product
 * - OPERATIONS: This component is presentation + lightweight orchestration only.
 *   Network calls and token handling remain the responsibility of the parent container.
 *
 * CODE EXPLANATION:
 * - Validates the 6-digit code client-side using ValidationService before delegating
 *   to the parent onSubmit handler to perform server verification.
 * - Emits non-blocking client-side audit events via AuditService for telemetry.
 * - Uses THEME tokens from Login.styles for consistent branding and accessible colors.
 * - Provides clear ARIA attributes and role semantics for screen readers.
 * -----------------------------------------------------------------------------
 */

import React, { useCallback } from 'react';
import PropTypes from 'prop-types';
import { Fingerprint, Key, AlertCircle } from 'lucide-react';

import {
    InputGroup,
    Label,
    InputWrapper,
    Input,
    ErrorMsg,
    Button,
    THEME
} from '../styles/Login.styles';

import AuthUtils from '../utils/authUtils'; // SecurityService, AuditService, ValidationService

const { AuditService, ValidationService, SecurityService } = AuthUtils;

export default function MfaForm({
    formData,
    onChange,
    onSubmit,
    onBack,
    errors,
    loading,
    tenantHint
}) {
    /**
     * handleSubmit
     * - Performs client-side validation for the MFA code.
     * - Emits a lightweight audit event and calls parent onSubmit for server verification.
     */
    const handleSubmit = useCallback(
        async (e) => {
            e.preventDefault();

            // Client-side validation
            const mfaErr = ValidationService.validateMfaCode(formData.mfaCode);
            if (mfaErr) {
                // Emit client-side validation failure for telemetry (non-blocking)
                AuditService.log('AUTH_MFA_CLIENT_VALIDATION_FAILURE', {
                    email: formData.email,
                    metadata: { mfaErr, tenantHint }
                });
                // Let parent show the error via errors prop; also return early
                return;
            }

            // Emit attempt audit (client-side telemetry)
            AuditService.log('AUTH_MFA_ATTEMPT', {
                email: formData.email,
                metadata: { tenantHint }
            });

            // Delegate to parent to perform server verification and further auditing
            try {
                await onSubmit(e);
            } catch (err) {
                // Emit client-side failure telemetry
                AuditService.log('AUTH_MFA_FAILURE', {
                    email: formData.email,
                    metadata: { message: err?.message || 'MFA verification failed', tenantHint }
                });
                // Rethrow so parent can handle UI state if needed
                throw err;
            }
        },
        [formData, onSubmit, tenantHint]
    );

    return (
        <form onSubmit={handleSubmit} noValidate aria-live="polite">
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
                <div
                    style={{
                        width: 64,
                        height: 64,
                        background: '#EFF6FF',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 16px'
                    }}
                    aria-hidden="true"
                >
                    <Fingerprint size={32} color={THEME.colors.accent} />
                </div>

                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: THEME.colors.text, margin: 0 }}>
                    Two-Factor Authentication
                </h3>

                <p style={{ fontSize: '0.9rem', color: THEME.colors.muted, marginTop: 8 }}>
                    Enter the 6-digit code sent to your device ending in <strong>****89</strong>.
                </p>
            </div>

            <InputGroup>
                <Label htmlFor="mfaCode" style={{ justifyContent: 'center' }}>
                    Security Code
                </Label>

                <InputWrapper>
                    <Key size={18} aria-hidden="true" />
                    <Input
                        id="mfaCode"
                        name="mfaCode"
                        inputMode="numeric"
                        pattern="\d{6}"
                        placeholder="000000"
                        value={formData.mfaCode}
                        onChange={onChange}
                        $error={!!errors.mfaCode}
                        aria-invalid={!!errors.mfaCode}
                        aria-describedby={errors.mfaCode ? 'mfa-error' : undefined}
                        style={{ textAlign: 'center', letterSpacing: '4px', fontSize: '1.2rem', fontWeight: 700 }}
                        maxLength={6}
                        autoFocus
                    />
                </InputWrapper>

                {errors.mfaCode && (
                    <ErrorMsg id="mfa-error" role="alert" style={{ justifyContent: 'center' }}>
                        <AlertCircle size={12} /> {errors.mfaCode}
                    </ErrorMsg>
                )}
            </InputGroup>

            <Button
                type="submit"
                disabled={loading}
                aria-disabled={loading}
                aria-label="Verify and access"
            >
                {loading ? <div className="loader" aria-hidden="true" /> : 'Verify & Access'}
            </Button>

            <Button
                type="button"
                $variant="secondary"
                onClick={() => {
                    // Emit a client-side audit for the back action
                    AuditService.log('AUTH_MFA_BACK_TO_LOGIN', {
                        email: formData.email,
                        metadata: { tenantHint }
                    });
                    onBack();
                }}
                style={{ marginTop: 12 }}
                aria-label="Back to login"
            >
                Back to Login
            </Button>
        </form>
    );
}

MfaForm.propTypes = {
    formData: PropTypes.shape({
        email: PropTypes.string,
        mfaCode: PropTypes.string
    }).isRequired,
    onChange: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired,
    onBack: PropTypes.func.isRequired,
    errors: PropTypes.object,
    loading: PropTypes.bool,
    tenantHint: PropTypes.string
};

MfaForm.defaultProps = {
    errors: {},
    loading: false,
    tenantHint: null
};
