/**
 * TITLE: WILSY OS Tenant Branding Management Panel
 * VERSION: v1.0.0-L10-P2C6-D21B-BRANDING-COMMAND-CENTER
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Presents fresh server-certified tenant-branding entitlement and
 *          profile truth in the shared Account Command Center and invokes only
 *          authenticated server-owned mutations.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/account/TenantBrandingManagementPanel.jsx
 * COLLABORATION / OWNERSHIP: Python EOS owns tenant authority and immutable
 *                            branding truth; D21B12 owns authenticated asset
 *                            delivery; this panel owns presentation state only.
 * CERTIFICATION / UPDATE DATE: 2026-09-29
 * CHANGELOG: v1.0.0-L10-P2C6-D21B-BRANDING-COMMAND-CENTER adds read, bounded
 *            profile-create and selection controls; safe-media upload remains
 *            deferred until its governed multipart dependency is certified.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No tenant selector, durable browser branding,
 *                             raw asset bytes, or local authority is created.
 * TENANT BOUNDARY: All scope is server-derived from the authenticated session.
 * AUTHORITY BOUNDARY: Presentation and transport invocation only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import useAuthenticatedTenantBrandingAsset from '../../hooks/useAuthenticatedTenantBrandingAsset.js';
import {
  createTenantBrandingProfile,
  fetchTenantBrandingManagement,
  selectTenantBrandingProfile,
} from '../../services/tenantBrandingManagementClient.js';

const EMPTY_FORM = Object.freeze({
  profileLabel: '',
  primaryColor: '',
  secondaryColor: '',
  accentColor: '',
  emailDisplayName: '',
});
const noop = () => {};

const panelStyle = {
  display: 'grid',
  gap: 16,
  padding: 18,
  borderRadius: 24,
  border: '1px solid rgba(255,255,255,.16)',
  background: 'linear-gradient(145deg, rgba(13,26,45,.96), rgba(7,12,22,.96))',
  color: '#fff',
};

const fieldStyle = { display: 'grid', gap: 6 };
const inputStyle = { minHeight: 40, borderRadius: 12, border: '1px solid rgba(255,255,255,.18)', background: 'rgba(0,0,0,.24)', color: '#fff', padding: '0 12px' };

/** @description Renders one server-bound tenant-branding management surface. */
export function TenantBrandingManagementPanel({ onAuthorityRefresh = noop }) {
  const [state, setState] = useState({ loading: true, error: null, data: null });
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState('');

  const refresh = useCallback(async ({ notify = false } = {}) => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const data = await fetchTenantBrandingManagement();
      setState({ loading: false, error: null, data });
      setForm((current) => ({
        ...current,
        profileLabel: current.profileLabel || data?.profile?.profileLabel || '',
        primaryColor: current.primaryColor || data?.profile?.primaryColor || '',
        secondaryColor: current.secondaryColor || data?.profile?.secondaryColor || '',
        accentColor: current.accentColor || data?.profile?.accentColor || '',
        emailDisplayName: current.emailDisplayName || data?.profile?.emailDisplayName || '',
      }));
      if (notify) onAuthorityRefresh(data);
      return data;
    } catch (error) {
      setState({ loading: false, error, data: null });
      return null;
    }
  }, [onAuthorityRefresh]);

  useEffect(() => { void refresh(); }, [refresh]);

  const logo = useAuthenticatedTenantBrandingAsset(state.data?.profile?.logo);
  const canManageProfile = state.data?.capabilities?.canManageProfile === true;
  const entitlement = state.data?.entitlement;
  const profile = state.data?.profile;

  const update = (key) => (event) => setForm((current) => ({ ...current, [key]: event.target.value }));

  const save = async (event) => {
    event.preventDefault();
    setSaving(true);
    setNotice('');
    try {
      await createTenantBrandingProfile(form);
      await refresh({ notify: true });
      setNotice('Profile approval committed by Python EOS.');
    } catch (error) {
      setNotice(error?.code || 'BRANDING_PROFILE_SAVE_FAILED');
    } finally {
      setSaving(false);
    }
  };

  const select = async () => {
    if (!profile?.profileId) return;
    setSaving(true);
    setNotice('');
    try {
      await selectTenantBrandingProfile(profile.profileId);
      await refresh({ notify: true });
      setNotice('Current profile pointer advanced by Python EOS.');
    } catch (error) {
      setNotice(error?.code || 'BRANDING_PROFILE_SELECT_FAILED');
    } finally {
      setSaving(false);
    }
  };

  const accent = useMemo(() => profile?.accentColor || '#4fd1ff', [profile?.accentColor]);

  return (
    <section style={panelStyle} data-testid="tenant-branding-management-panel" data-branding-authority="server">
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'start' }}>
        <div>
          <span style={{ color: '#b9eaff', fontSize: 11, letterSpacing: '.18em', fontWeight: 800 }}>TENANT BRANDING · COMMAND CENTER</span>
          <h3 style={{ margin: '8px 0 4px', fontSize: 26 }}>Brand authority</h3>
          <p style={{ margin: 0, color: 'rgba(255,255,255,.68)' }}>Current entitlement and profile truth, revalidated by Python EOS.</p>
        </div>
        <button type="button" onClick={() => void refresh()} disabled={state.loading} style={{ ...inputStyle, cursor: 'pointer', padding: '0 14px' }}>Refresh</button>
      </div>

      {state.loading && <p role="status">Loading authenticated branding authority…</p>}
      {state.error && <p role="alert">Branding authority unavailable: {state.error.code || 'REQUEST_FAILED'}</p>}
      {!state.loading && !state.error && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(170px,1fr))', gap: 10 }}>
            <article><small>Tier</small><strong style={{ display: 'block', color: accent }}>{entitlement?.brandingTier || 'Not entitled'}</strong></article>
            <article><small>Entitlement</small><strong style={{ display: 'block' }}>{entitlement?.lifecycleState || 'ABSENT'}</strong></article>
            <article><small>Current profile</small><strong style={{ display: 'block' }}>{profile?.profileLabel || 'No profile selected'}</strong></article>
            <article><small>Trust mark</small><strong style={{ display: 'block' }}>WILSY OS verified</strong></article>
          </div>

          {logo.objectUrl && <img src={logo.objectUrl} alt="Current tenant logo" style={{ maxWidth: 180, maxHeight: 72, objectFit: 'contain', borderRadius: 12 }} />}

          <form onSubmit={save} style={{ display: 'grid', gap: 10 }}>
            <label style={fieldStyle}>Profile label<input value={form.profileLabel} onChange={update('profileLabel')} disabled={!canManageProfile || saving} required maxLength={120} style={inputStyle} /></label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(150px,1fr))', gap: 10 }}>
              <label style={fieldStyle}>Primary color<input value={form.primaryColor} onChange={update('primaryColor')} disabled={!canManageProfile || saving} placeholder="#0f172a" style={inputStyle} /></label>
              <label style={fieldStyle}>Secondary color<input value={form.secondaryColor} onChange={update('secondaryColor')} disabled={!canManageProfile || saving} placeholder="#1e293b" style={inputStyle} /></label>
              <label style={fieldStyle}>Accent color<input value={form.accentColor} onChange={update('accentColor')} disabled={!canManageProfile || saving} placeholder="#4fd1ff" style={inputStyle} /></label>
            </div>
            <label style={fieldStyle}>Email display name<input value={form.emailDisplayName} onChange={update('emailDisplayName')} disabled={!canManageProfile || saving} style={inputStyle} /></label>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <button type="submit" disabled={!canManageProfile || saving} style={{ ...inputStyle, cursor: canManageProfile ? 'pointer' : 'not-allowed', padding: '0 16px' }}>{saving ? 'Saving…' : 'Approve profile'}</button>
              <button type="button" onClick={() => void select()} disabled={!canManageProfile || saving || !profile?.profileId} style={{ ...inputStyle, cursor: 'pointer', padding: '0 16px' }}>Make current</button>
            </div>
          </form>

          <p role="note" style={{ margin: 0, color: 'rgba(255,255,255,.65)' }}>Asset upload is governed separately; authenticated logo delivery remains available and no public asset URL is created here.</p>
          {!canManageProfile && <p role="note" style={{ margin: 0, color: 'rgba(255,255,255,.65)' }}>Your authenticated role has read-only branding authority.</p>}
          {notice && <p role="status" style={{ margin: 0, color: '#b9eaff' }}>{notice}</p>}
        </>
      )}
    </section>
  );
}

export default TenantBrandingManagementPanel;

// ARTIFACT: TenantBrandingManagementPanel.jsx
// VERSION: v1.0.0-L10-P2C6-D21B-BRANDING-COMMAND-CENTER
// AUTHORITY BOUNDARY: presentation and transport invocation only
// TENANT POSTURE: server-derived; no selector or local authority
// FAIL-CLOSED POSTURE: unavailable/denied mutation controls remain disabled
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
