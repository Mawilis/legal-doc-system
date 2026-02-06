/**
 * File: client/src/components/navigation/UserMenu.jsx
 * STATUS: PRODUCTION-READY | SUPER_ADMIN-FIRST | AUDITABLE
 * VERSION: 1.0.2
 *
 * PURPOSE
 * - Super Admin profile menu and immutable actor card.
 * - Shows owner logo for SUPER_ADMIN; initials fallback for others.
 * - Provides quick access to: Personal Profile, System Settings, View Audit Trail, Terminate Session.
 * - Emits best-effort audit events for each action (AuthUtils.AuditService.log).
 *
 * COLLABORATION & OWNERSHIP
 * - AUTHOR: Chief Architect (Wilson Khanyezi)
 * - FRONTEND: @frontend (integration into AppTopBar)
 * - SECURITY: @security (audit masking & retention)
 * - SRE: @sre (ingestion endpoint)
 * - QA: @qa (keyboard, focus, tenant switch, logout tests)
 *
 * NOTES
 * - UI gating only; backend must enforce RBAC.
 * - Audit calls are best-effort and must never throw to UI.
 * - This component is defensive: it tolerates missing store methods and missing user data.
 */

import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';
import AuthUtils from '../../features/auth/utils/authUtils';
import { ChevronDown, LogOut, Settings, User, Shield } from 'lucide-react';

/* -------------------------
   Styled primitives
   ------------------------- */

const Wrap = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Card = styled.button`
  display:flex;
  align-items:center;
  gap:10px;
  padding:6px 10px;
  border-radius:10px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.04);
  color: inherit;
  cursor: pointer;
  min-width: 220px;
  text-align: left;
  &:focus { outline: 2px solid rgba(59,130,246,0.25); }
`;

const Avatar = styled.div`
  width:40px;
  height:40px;
  border-radius:8px;
  overflow:hidden;
  display:flex;
  align-items:center;
  justify-content:center;
  background: linear-gradient(135deg,#0f172a,#1e293b);
  color:#fff;
  font-weight:800;
  img { width:100%; height:100%; object-fit:contain; display:block; }
`;

const Info = styled.div`
  flex:1;
  display:flex;
  flex-direction:column;
  align-items:flex-start;
  gap:2px;
  .name { font-weight:700; font-size:0.95rem; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .meta { font-size:0.72rem; color:#93c5fd; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; }
`;

const Menu = styled.div`
  position:absolute;
  right:12px;
  top:56px;
  width:260px;
  background: #07102a;
  border-radius:10px;
  box-shadow: 0 12px 40px rgba(2,6,23,0.6);
  border: 1px solid rgba(255,255,255,0.04);
  padding:8px;
  z-index:1200;
`;

const MenuItem = styled.button`
  display:flex;
  align-items:center;
  gap:10px;
  width:100%;
  padding:10px;
  border-radius:8px;
  background:transparent;
  border:none;
  color:#cbd5e1;
  cursor:pointer;
  text-align:left;
  &:hover { background: rgba(255,255,255,0.02); color:#fff; }
  &:focus { outline: 2px solid rgba(59,130,246,0.18); }
  svg { color:inherit; }
`;

const Divider = styled.hr`
  border: none;
  height:1px;
  background: rgba(255,255,255,0.03);
  margin:8px 0;
`;

/* -------------------------
   Audit helper (best-effort)
   ------------------------- */
async function recordAudit(payload = {}) {
    try {
        const svc = AuthUtils?.AuditService;
        if (svc && typeof svc.log === 'function') {
            await svc.log(payload.eventType || 'USER_MENU_EVENT', payload);
            return;
        }
        // Dev fallback
        // eslint-disable-next-line no-console
        console.info('[AUDIT] UserMenu:', payload);
    } catch (e) {
        // eslint-disable-next-line no-console
        console.warn('[AUDIT] UserMenu failed', e);
    }
}

/* -------------------------
   Component
   ------------------------- */

export default function UserMenu({ compact = false }) {
    const navigate = useNavigate();

    // IMPORTANT: call hook unconditionally to satisfy React rules of hooks.
    // Do not wrap this call in any conditional logic.
    const auth = useAuthStore();
    // Defensive destructure: provide safe defaults if store shape is incomplete.
    const {
        user = null,
        tenants = [],
        logout = async () => { },
        switchTenant = null,
        refreshUser = null
    } = auth || {};

    const [open, setOpen] = useState(false);
    const [selectedTenant, setSelectedTenant] = useState(user?.tenantId || '');
    const toggleRef = useRef(null);
    const menuRef = useRef(null);

    const isOwner = useMemo(() => (user?.role === 'SUPER_ADMIN'), [user]);

    const displayName = useMemo(() => {
        if (!user) return 'Chief Architect';
        const name = `${user.firstName || user.name || ''} ${user.lastName || ''}`.trim();
        return name || user.email || 'Chief Architect';
    }, [user]);

    const initials = useMemo(() => {
        if (!user) return '??';
        const f = (user.firstName || user.name || '').trim();
        const l = (user.lastName || '').trim();
        const chars = (f.charAt(0) || '') + (l ? l.charAt(0) : '');
        return (chars || '??').toUpperCase();
    }, [user]);

    /* Close handlers: outside click and Escape */
    useEffect(() => {
        if (!open) return undefined;

        function onDocumentClick(e) {
            const t = toggleRef.current;
            const m = menuRef.current;
            if (t && t.contains(e.target)) return; // click on toggle -> ignore
            if (m && !m.contains(e.target)) {
                setOpen(false);
            }
        }

        function onKey(e) {
            if (e.key === 'Escape') {
                setOpen(false);
            }
        }

        document.addEventListener('mousedown', onDocumentClick);
        document.addEventListener('touchstart', onDocumentClick);
        document.addEventListener('keydown', onKey);
        return () => {
            document.removeEventListener('mousedown', onDocumentClick);
            document.removeEventListener('touchstart', onDocumentClick);
            document.removeEventListener('keydown', onKey);
        };
    }, [open]);

    /* Focus first menu item when opened, restore focus to toggle when closed */
    useEffect(() => {
        if (open) {
            const m = menuRef.current;
            if (m) {
                const first = m.querySelector('button, [role="menuitem"], select, a');
                if (first && typeof first.focus === 'function') first.focus();
            }
        } else {
            const t = toggleRef.current;
            if (t && typeof t.focus === 'function') t.focus();
        }
    }, [open]);

    /* Keep selectedTenant in sync if user changes */
    useEffect(() => {
        setSelectedTenant(user?.tenantId || '');
    }, [user?.tenantId]);

    /* Toggle menu */
    const handleToggle = useCallback(() => {
        setOpen(s => {
            const next = !s;
            recordAudit({
                actor: user?.email || user?._id,
                eventType: 'USER_MENU_TOGGLE',
                summary: 'Toggled user menu',
                metadata: { open: next }
            });
            return next;
        });
    }, [user]);

    /* Navigation actions */
    const goToProfile = useCallback(async () => {
        setOpen(false);
        await recordAudit({ actor: user?.email, eventType: 'NAV_PROFILE', summary: 'Opened personal profile' });
        navigate('/profile');
    }, [navigate, user]);

    const goToSystemSettings = useCallback(async () => {
        setOpen(false);
        await recordAudit({ actor: user?.email, eventType: 'NAV_SYSTEM_SETTINGS', summary: 'Opened system settings' });
        navigate('/admin/health');
    }, [navigate, user]);

    const viewAuditTrail = useCallback(async () => {
        setOpen(false);
        await recordAudit({ actor: user?.email, eventType: 'NAV_AUDIT_TRAIL', summary: 'Opened audit trail' });
        navigate('/admin/audits');
    }, [navigate, user]);

    const handleTerminate = useCallback(async () => {
        setOpen(false);
        await recordAudit({ actor: user?.email, eventType: 'AUTH_LOGOUT', summary: 'User initiated logout via UserMenu' });
        try {
            if (typeof logout === 'function') await logout();
        } catch (e) {
            // eslint-disable-next-line no-console
            console.error('Logout failed', e);
        }
    }, [logout, user]);

    /* Tenant change */
    const handleTenantChange = useCallback(async (e) => {
        const tenantId = e.target.value;
        setSelectedTenant(tenantId);
        await recordAudit({ actor: user?.email, eventType: 'TENANT_SWITCH', summary: `Switched tenant to ${tenantId}`, metadata: { tenantId } });
        if (typeof switchTenant === 'function') {
            try {
                await switchTenant(tenantId);
                if (typeof refreshUser === 'function') await refreshUser();
            } catch (err) {
                // eslint-disable-next-line no-console
                console.error('Tenant switch failed', err);
            }
        }
    }, [switchTenant, refreshUser, user]);

    /* Image fallback handler */
    const handleImgError = useCallback((e) => {
        try {
            e.currentTarget.onerror = null;
            e.currentTarget.src = '/assets/wilsy_logo.png';
        } catch { /* ignore */ }
    }, []);

    return (
        <Wrap>
            <Card
                aria-haspopup="true"
                aria-expanded={open}
                onClick={handleToggle}
                title={displayName}
                ref={toggleRef}
                type="button"
            >
                <Avatar aria-hidden="true">
                    {isOwner && (user?.logoUrl || user?.tenant?.logoUrl) ? (
                        <img
                            src={user.logoUrl || user.tenant?.logoUrl}
                            alt="Owner logo"
                            onError={handleImgError}
                        />
                    ) : (
                        <span aria-hidden="true">{initials}</span>
                    )}
                </Avatar>

                {!compact && (
                    <Info>
                        <div className="name">{displayName}</div>
                        <div className="meta">{(user?.role || 'GUEST').toUpperCase()} • {user?.tenantName || 'No Tenant'}</div>
                    </Info>
                )}

                <ChevronDown size={16} aria-hidden="true" />
            </Card>

            {open && (
                <Menu role="menu" aria-label="User menu" ref={menuRef}>
                    {isOwner && Array.isArray(tenants) && tenants.length > 0 && (
                        <div style={{ padding: '8px 10px' }}>
                            <label htmlFor="um-tenant" style={{ display: 'block', color: '#94a3b8', fontSize: 12, marginBottom: 6 }}>Active Tenant</label>
                            <select
                                id="um-tenant"
                                value={selectedTenant}
                                onChange={handleTenantChange}
                                style={{
                                    width: '100%',
                                    padding: '8px',
                                    borderRadius: 8,
                                    background: 'transparent',
                                    color: '#fff',
                                    border: '1px solid rgba(255,255,255,0.04)'
                                }}
                            >
                                <option value="">Select tenant</option>
                                {tenants.map(t => <option key={t._id} value={t._id}>{t.name}</option>)}
                            </select>
                        </div>
                    )}

                    <MenuItem onClick={goToProfile} role="menuitem" type="button">
                        <User size={16} /> <span>Personal Profile</span>
                    </MenuItem>

                    {(user?.role === 'SUPER_ADMIN' || user?.role === 'TENANT_ADMIN') && (
                        <MenuItem onClick={goToSystemSettings} role="menuitem" type="button">
                            <Settings size={16} /> <span>System Settings</span>
                        </MenuItem>
                    )}

                    {(user?.role === 'SUPER_ADMIN' || user?.role === 'TENANT_ADMIN') && (
                        <MenuItem onClick={viewAuditTrail} role="menuitem" type="button">
                            <Shield size={16} /> <span>View Audit Trail</span>
                        </MenuItem>
                    )}

                    <Divider />

                    <MenuItem onClick={handleTerminate} role="menuitem" aria-label="Terminate session" type="button">
                        <LogOut size={16} /> <span>Terminate Session</span>
                    </MenuItem>
                </Menu>
            )}
        </Wrap>
    );
}

UserMenu.propTypes = {
    compact: PropTypes.bool
};
