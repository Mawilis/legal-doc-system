/* eslint-disable */
/**
 * =============================================================================
 * Wilsy OS — Shared Profile Panel
 * =============================================================================
 * File:           client/src/components/shared/WilsyProfilePanel.jsx
 * Version:        v1.0.0-INSTITUTIONAL
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Reusable operator/employee profile surface for HR and OS chrome.
 *                 Hydrates display identity without inventing personal data.
 * Classification: Production Artifact
 *
 * Forensic Relationships:
 *   Upstream:   authContext, tenantContext, wilsyDashboardChromeConfig
 *   Downstream: HrDashboard, shared account surfaces
 * =============================================================================
 */

import React, { useMemo } from 'react';

/**
 * @function hydrateWilsyProfileRuntime
 * @description Builds a stable profile runtime object from live user/tenant props.
 * @param {object} [source={}] - User, employee, or operator payload.
 * @param {object} [options={}] - Optional tenant hints.
 * @returns {object} Profile runtime for panel rendering.
 * @collaboration HrDashboard profile drawer, OS identity plate, account command.
 */
export function hydrateWilsyProfileRuntime(source = {}, options = {}) {
    const raw = source && typeof source === 'object' ? source : {};
    const tenant = options.tenant && typeof options.tenant === 'object' ? options.tenant : {};

    const displayName =
        raw.displayName ||
        raw.fullName ||
        raw.name ||
        [raw.firstName, raw.lastName].filter(Boolean).join(' ') ||
        raw.email ||
        'Operator';

    const email = raw.email || raw.userEmail || raw.primaryEmail || '';
    const role = String(raw.roleLabel || raw.role || raw.title || options.role || 'MEMBER').replace(
        /_/g,
        ' '
    );
    const tenantId =
        raw.tenantId ||
        tenant.tenantId ||
        tenant.id ||
        options.tenantId ||
        'MASTER';
    const tenantName =
        tenant.name ||
        tenant.displayName ||
        tenant.companyName ||
        options.tenantName ||
        'Wilsy OS Root';

    const initials = String(displayName)
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part.charAt(0).toUpperCase())
        .join('') || 'WK';

    return {
        displayName: String(displayName).trim() || 'Operator',
        email: String(email).trim(),
        role: String(role).trim(),
        tenantId: String(tenantId).trim(),
        tenantName: String(tenantName).trim(),
        initials,
        avatarUrl: raw.avatarUrl || raw.photoUrl || raw.imageUrl || null,
        department: raw.department || raw.team || '',
        phone: raw.phone || raw.mobile || '',
        status: raw.status || raw.employmentStatus || 'ACTIVE',
        source: raw.source || 'LIVE_PROFILE'
    };
}

const panelShell = {
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
    padding: 16,
    borderRadius: 12,
    border: '1px solid rgba(212, 175, 55, 0.28)',
    background: 'rgba(8, 10, 14, 0.92)',
    color: '#E8E8E8',
    fontFamily: 'Inter, system-ui, sans-serif',
    minWidth: 240,
    maxWidth: 360
};

const rowStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: 12
};

const avatarStyle = {
    width: 44,
    height: 44,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #D4AF37, #8B7355)',
    color: '#0a0a0a',
    fontWeight: 800,
    fontSize: 14,
    flexShrink: 0,
    overflow: 'hidden'
};

const labelStyle = {
    fontSize: 11,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    color: '#A3A3A3',
    margin: 0
};

const valueStyle = {
    margin: '2px 0 0',
    fontSize: 14,
    fontWeight: 600,
    color: '#F5F5F5'
};

/**
 * @function WilsyProfilePanel
 * @description Renders a compact identity card for employees/operators.
 * @param {object} props - Component props.
 * @param {object} [props.user] - Live user or employee record.
 * @param {object} [props.profile] - Alternate profile payload.
 * @param {object} [props.tenant] - Active tenant.
 * @param {object} [props.runtime] - Pre-hydrated runtime (skips hydrate when provided).
 * @param {boolean} [props.compact=false] - Dense layout.
 * @param {function} [props.onClose] - Optional close handler.
 * @returns {JSX.Element}
 * @collaboration HrDashboard, shared account identity, OS chrome operator card.
 */
const WilsyProfilePanel = ({
    user = null,
    profile = null,
    tenant = null,
    runtime = null,
    compact = false,
    onClose = null,
    className = '',
    style = {}
}) => {
    const resolved = useMemo(() => {
        if (runtime && typeof runtime === 'object') return runtime;
        return hydrateWilsyProfileRuntime(profile || user || {}, { tenant: tenant || {} });
    }, [runtime, profile, user, tenant]);

    return (
        <aside
            className={className}
            style={{ ...panelShell, ...(compact ? { padding: 12, minWidth: 200 } : {}), ...style }}
            data-wilsy-profile-panel="true"
            aria-label="Profile"
        >
            <div style={rowStyle}>
                <div style={avatarStyle} aria-hidden>
                    {resolved.avatarUrl ? (
                        <img
                            src={resolved.avatarUrl}
                            alt=""
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                            onError={(event) => {
                                event.currentTarget.style.display = 'none';
                            }}
                        />
                    ) : (
                        resolved.initials
                    )}
                </div>
                <div style={{ minWidth: 0, flex: 1 }}>
                    <p style={labelStyle}>Profile</p>
                    <p style={{ ...valueStyle, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {resolved.displayName}
                    </p>
                    <p style={{ margin: 0, fontSize: 12, color: '#D4AF37' }}>{resolved.role}</p>
                </div>
                {typeof onClose === 'function' ? (
                    <button
                        type="button"
                        onClick={onClose}
                        aria-label="Close profile"
                        style={{
                            border: '1px solid rgba(212,175,55,0.3)',
                            background: 'transparent',
                            color: '#A3A3A3',
                            borderRadius: 8,
                            padding: '4px 8px',
                            cursor: 'pointer'
                        }}
                    >
                        Close
                    </button>
                ) : null}
            </div>

            {resolved.email ? (
                <div>
                    <p style={labelStyle}>Email</p>
                    <p style={{ ...valueStyle, fontSize: 13, fontWeight: 500 }}>{resolved.email}</p>
                </div>
            ) : null}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <div>
                    <p style={labelStyle}>Tenant</p>
                    <p style={{ ...valueStyle, fontSize: 13 }}>{resolved.tenantName}</p>
                </div>
                <div>
                    <p style={labelStyle}>Status</p>
                    <p style={{ ...valueStyle, fontSize: 13 }}>{resolved.status}</p>
                </div>
            </div>

            {resolved.department ? (
                <div>
                    <p style={labelStyle}>Department</p>
                    <p style={{ ...valueStyle, fontSize: 13 }}>{resolved.department}</p>
                </div>
            ) : null}

            {resolved.phone ? (
                <div>
                    <p style={labelStyle}>Phone</p>
                    <p style={{ ...valueStyle, fontSize: 13 }}>{resolved.phone}</p>
                </div>
            ) : null}
        </aside>
    );
};

export { WilsyProfilePanel };
export default WilsyProfilePanel;

/**
 * =============================================================================
 * INSTITUTIONAL CERTIFICATION SEAL — WilsyProfilePanel v1.0.0
 * =============================================================================
 */
