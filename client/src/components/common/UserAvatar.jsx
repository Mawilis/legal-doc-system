/**
 * File: client/src/components/common/UserAvatar.jsx
 * STATUS: PRODUCTION | ROLE-AWARE | ACCESSIBLE
 * VERSION: 2026-01-10 (patched)
 *
 * PURPOSE
 * - Role-aware avatar component used across the UI.
 * - Prioritizes the Wilsy owner logo for SUPER_ADMIN users.
 * - Falls back to user-provided avatar, initials, or a local brand asset.
 *
 * KEY IMPROVEMENTS (production hardening)
 * - SSR-safe guards around window/document usage.
 * - Defensive localStorage / origin checks removed from render path.
 * - Prefetch logic guarded to avoid errors in non-browser environments.
 * - Clear data-testid attributes for QA and E2E.
 * - All audit/PII concerns remain delegated to AuthUtils/AuditService.
 *
 * INTEGRATION CONTRACT
 * - Depends on `useAuthStore` at: client/src/store/authStore.js
 * - AuthUtils used only for optional masking; no PII is leaked by default.
 *
 * COLLABORATION NOTES
 * - @frontend: move inline colors to theme tokens in theme.js when ready.
 * - @security: review maskEmail behavior in AuthUtils.SecurityService.
 * - @qa: tests should assert SUPER_ADMIN logo priority, initials fallback, keyboard activation.
 */

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import useAuthStore from '../../store/authStore';
import AuthUtils from '../../features/auth/utils/authUtils'; // optional masking

/* -------------------------
   Styled primitives
   ------------------------- */

const Wrapper = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
  cursor: ${p => (p.$clickable ? 'pointer' : 'default')};
  color: inherit;
  text-decoration: none;
  vertical-align: middle;
  &:focus { outline: 2px solid rgba(37,99,235,0.18); border-radius: 8px; }
`;

const AvatarBox = styled.span`
  width: ${p => p.size}px;
  height: ${p => p.size}px;
  min-width: ${p => p.size}px;
  min-height: ${p => p.size}px;
  border-radius: ${p => Math.max(4, Math.floor(p.size * 0.18))}px;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: ${p => p.bg || '#0f172a'};
  color: ${p => p.fg || '#fff'};
  font-weight: 700;
  font-size: ${p => Math.max(10, Math.floor(p.size * 0.38))}px;
  box-shadow: 0 2px 6px rgba(2,6,23,0.12);
  border: 1px solid rgba(255,255,255,0.04);
`;

const Img = styled.img`
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
`;

/* Role badge for SUPER_ADMIN (small crown-like indicator) */
const RoleBadge = styled.span`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: ${p => Math.max(12, Math.floor(p.size * 0.36))}px;
  height: ${p => Math.max(12, Math.floor(p.size * 0.36))}px;
  border-radius: 50%;
  background: ${p => p.badgeBg || '#f59e0b'};
  color: ${p => p.badgeFg || '#07102a'};
  font-size: ${p => Math.max(8, Math.floor(p.size * 0.28))}px;
  font-weight: 800;
  position: relative;
  margin-left: -${p => Math.max(10, Math.floor(p.size * 0.28))}px;
  border: 2px solid rgba(0,0,0,0.06);
`;

/* Optional display name (used when showName=true) */
const NameWrap = styled.span`
  display: inline-block;
  max-width: ${p => (p.size * 6)}px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 700;
  color: ${p => p.color || '#ffffff'};
  font-size: ${p => Math.max(12, Math.floor(p.size * 0.36))}px;
`;

/* -------------------------
   Helpers
   ------------------------- */

/**
 * safeDisplayName
 * - Returns a safe, concise display string for the avatar title/alt.
 * - Uses AuthUtils.SecurityService.maskEmail when available to avoid exposing full local-part.
 */
function safeDisplayName(user) {
    if (!user) return 'User';
    const name = user.firstName || user.name || '';
    const last = user.lastName || '';
    const full = `${name} ${last}`.trim();
    if (full) return full;
    if (user.email) {
        try {
            return AuthUtils?.SecurityService?.maskEmail?.(user.email) || user.email;
        } catch {
            return user.email;
        }
    }
    return 'User';
}

/**
 * computeInitials
 * - Derives 1-2 character initials from available name/email.
 */
function computeInitials(user) {
    if (!user) return 'U';
    const name = user.firstName || user.name || user.email || '';
    const parts = String(name).trim().split(/\s+/).filter(Boolean);
    if (parts.length === 0) return 'U';
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return (parts[0][0] + parts[1][0]).toUpperCase();
}

/* -------------------------
   Component
   ------------------------- */

export default function UserAvatar({
    size = 36,
    showName = false,
    onClick = null,
    className = '',
    ariaLabel = null,
    fallbackLocal = '/assets/branding/wilsy_logo.png',
    testId = 'user-avatar'
}) {
    const { user } = useAuthStore();
    const [imgError, setImgError] = useState(false);
    const [prefetched, setPrefetched] = useState(false);

    // Role detection
    const isSuperAdmin = useMemo(() => (user?.role || '').toUpperCase() === 'SUPER_ADMIN', [user]);

    /**
     * Candidate image selection (priority)
     * - SUPER_ADMIN: user.logoUrl -> fallbackLocal
     * - Others: user.avatarUrl -> user.logoUrl -> fallbackLocal
     *
     * Note: we avoid referencing window during render to remain SSR-safe.
     */
    const candidateSrc = useMemo(() => {
        if (!user) return fallbackLocal;
        if (isSuperAdmin) return user.logoUrl || fallbackLocal;
        return user.avatarUrl || user.logoUrl || fallbackLocal;
    }, [user, isSuperAdmin, fallbackLocal]);

    // Accessible label (masked where possible)
    const label = ariaLabel || `${safeDisplayName(user)} (${(user?.role || 'GUEST').toUpperCase()})`;

    // initials computed once
    const initials = useMemo(() => computeInitials(user), [user]);

    /**
     * Prefetch image (browser-only)
     * - Guarded: only runs in browser environment.
     * - Avoids prefetch for local assets (starting with '/').
     */
    useEffect(() => {
        if (typeof window === 'undefined') return undefined;
        if (!candidateSrc) return undefined;

        // If candidateSrc is a local path (starts with '/'), treat as already available
        const isLocal = String(candidateSrc).startsWith('/');
        if (isLocal) {
            setPrefetched(true);
            return undefined;
        }

        let mounted = true;
        const img = new Image();
        img.src = candidateSrc;
        img.onload = () => { if (mounted) setPrefetched(true); };
        img.onerror = () => { if (mounted) setImgError(true); };
        return () => { mounted = false; };
    }, [candidateSrc]);

    // Reset imgError when candidateSrc changes
    useEffect(() => {
        setImgError(false);
    }, [candidateSrc]);

    const handleImgError = useCallback((e) => {
        setImgError(true);
        // prevent infinite loop if fallback also fails
        try { e.currentTarget.onerror = null; } catch { }
    }, []);

    // Render avatar content (image or initials)
    const avatarContent = useMemo(() => {
        if (candidateSrc && !imgError) {
            return (
                <Img
                    src={candidateSrc}
                    alt={safeDisplayName(user)}
                    loading="lazy"
                    onError={handleImgError}
                    data-testid={`${testId}-img`}
                />
            );
        }
        return <span aria-hidden="true" data-testid={`${testId}-initials`}>{initials}</span>;
    }, [candidateSrc, imgError, initials, handleImgError, user, testId]);

    return (
        <Wrapper
            $clickable={!!onClick}
            onClick={onClick || undefined}
            className={className}
            aria-label={label}
            title={safeDisplayName(user)}
            data-testid={testId}
            tabIndex={onClick ? 0 : -1}
            onKeyDown={(e) => {
                if (!onClick) return;
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onClick(e);
                }
            }}
        >
            <AvatarBox size={size} bg={isSuperAdmin ? '#07102a' : undefined} fg="#fff" data-testid={`${testId}-box`}>
                {avatarContent}
            </AvatarBox>

            {/* Role badge for SUPER_ADMIN */}
            {isSuperAdmin && (
                <RoleBadge size={size} aria-hidden="true" data-testid={`${testId}-badge`}>
                    ★
                </RoleBadge>
            )}

            {showName && (
                <NameWrap size={size} color="#ffffff" data-testid={`${testId}-name`}>
                    {safeDisplayName(user)}
                </NameWrap>
            )}
        </Wrapper>
    );
}

/* -------------------------
   PropTypes
   ------------------------- */

UserAvatar.propTypes = {
    /** Pixel size of avatar square (width & height) */
    size: PropTypes.number,
    /** Whether to show the display name next to the avatar */
    showName: PropTypes.bool,
    /** Optional click handler (makes the component keyboard-focusable) */
    onClick: PropTypes.func,
    /** Additional className for styling */
    className: PropTypes.string,
    /** ARIA label override */
    ariaLabel: PropTypes.string,
    /** Local fallback asset path (relative to public/) */
    fallbackLocal: PropTypes.string,
    /** Test id for reliable selectors in tests */
    testId: PropTypes.string
};
