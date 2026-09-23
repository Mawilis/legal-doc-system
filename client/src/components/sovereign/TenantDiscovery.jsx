/**
 * WILSY OS — SECURE WORKSPACE DISCOVERY
 * VERSION: v3.2.0-INSTITUTIONAL-AUTH-BRAND
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Resolves one organization/workspace through the bounded server
 *          discovery contract; never downloads or filters a tenant directory.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/TenantDiscovery.jsx
 * COLLABORATION / OWNERSHIP: authContext owns the exact `/api/auth/discover`
 *                            transport; this component is presentation only.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v3.2.0-INSTITUTIONAL-AUTH-BRAND — Uses the established WILSY
 *            brand asset and a restrained institutional discovery panel.
 *            v3.1.0-PREMIUM-TENANT-IDENTITY — Restored the real WILSY OS
 *            platform mark and added a bounded premium tenant identity slot.
 *            Tenant legal name and verification remain server-issued only.
 *            v3.0.0-SERVER-SIDE-EXACT-DISCOVERY — Removed full-directory fetch,
 *            kinetic security theater, synthetic tenant fallback, and client
 *            tenant-search authority.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Only the matched bounded tenant projection is shown.
 * TENANT BOUNDARY: No tenant is persisted unless returned by authoritative server discovery.
 * AUTHORITY BOUNDARY: Discovery projection only; no authentication or authorization grant.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
 */

import React, { useState } from 'react';
import { AlertCircle, ArrowRight, Loader2 } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/authContext.jsx';
import TenantIdentityCard from '../auth/TenantIdentityCard.jsx';
import wilsyBrandAsset from '../../assets/logo/wilsy.jpeg';

export default function TenantDiscovery({ savedTenant }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { discoverTenant, loading: authLoading } = useAuth();
  const [alias, setAlias] = useState(savedTenant?.alias || '');
  const [tenant, setTenant] = useState(null);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const cleanAlias = alias.trim();
    if (!cleanAlias || submitting) return;
    setSubmitting(true);
    setError('');
    try {
      const resolved = await discoverTenant(cleanAlias);
      setTenant(resolved);
      navigate('/login', {
        replace: true,
        state: { tenant: resolved, from: location.pathname },
      });
    } catch (discoveryError) {
      setTenant(null);
      setError(discoveryError.message || 'Workspace discovery is unavailable. Please retry.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main style={pageStyle}>
      <section style={cardStyle} aria-labelledby="discovery-title">
        <div style={platformBrandStyle}>
          <img src={wilsyBrandAsset} alt="WILSY OS platform mark" style={platformMarkStyle} />
          <div style={brandCopyStyle}><strong>WILSY OS</strong><span>Institutional access</span></div>
        </div>
        <h1 id="discovery-title" style={titleStyle}>Secure Workspace Access</h1>
        <p style={copyStyle}>Enter your organization or workspace identifier to continue.</p>

        {tenant && (
          <TenantIdentityCard tenant={tenant} />
        )}

        <form onSubmit={handleSubmit} style={formStyle}>
          <label htmlFor="workspace-alias" style={labelStyle}>Organization / workspace</label>
          <input
            id="workspace-alias"
            name="alias"
            value={alias}
            onChange={(event) => setAlias(event.target.value)}
            placeholder="e.g. acme-law"
            autoComplete="organization"
            disabled={submitting || authLoading}
            style={inputStyle}
            required
          />
          <button type="submit" disabled={submitting || authLoading || !alias.trim()} style={buttonStyle}>
            {submitting || authLoading ? <Loader2 size={18} className="animate-spin" /> : <ArrowRight size={18} />}
            <span>Continue securely</span>
          </button>
        </form>

        {error && (
          <div role="alert" style={errorStyle}>
            <AlertCircle size={16} aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}
      </section>
    </main>
  );
}

const pageStyle = {
  minHeight: '100vh', display: 'grid', placeItems: 'center', padding: '24px',
  background: '#101112', color: '#f5f1e8', fontFamily: 'Inter, system-ui, sans-serif',
};
const cardStyle = {
  width: 'min(100%, 560px)', padding: '44px clamp(28px, 6vw, 58px) 38px', background: 'linear-gradient(145deg, #1c1e20, #141617)',
  border: '1px solid rgba(213,176,79,.3)', borderRadius: '16px',
  boxShadow: '0 30px 90px rgba(0,0,0,.42)',
};
const platformBrandStyle = { display: 'flex', alignItems: 'center', gap: '14px', paddingBottom: '28px', borderBottom: '1px solid rgba(245,241,232,.1)', color: '#d5b04f' };
const platformMarkStyle = { width: '46px', height: '46px', objectFit: 'cover', objectPosition: '50% 13%', borderRadius: '8px', background: '#fff' };
const brandCopyStyle = { display: 'grid', gap: '3px' };
const titleStyle = { margin: '38px 0 10px', fontSize: 'clamp(32px, 5vw, 48px)', lineHeight: 1.04, fontWeight: 650, letterSpacing: '-.035em' };
const copyStyle = { margin: '0 0 32px', color: '#b8b6ae', lineHeight: 1.6, fontSize: '15px' };
const formStyle = { display: 'grid', gap: '10px' };
const labelStyle = { color: '#d8d4c9', fontSize: '14px', fontWeight: 600 };
const inputStyle = { width: '100%', boxSizing: 'border-box', padding: '14px 15px', borderRadius: '7px', border: '1px solid #4d4f51', background: '#0f1011', color: '#fff', fontSize: '16px', outlineColor: '#d5b04f' };
const buttonStyle = { display: 'inline-flex', justifyContent: 'center', alignItems: 'center', gap: '10px', marginTop: '12px', padding: '14px 18px', border: 0, borderRadius: '7px', background: '#d5b04f', color: '#141414', fontWeight: 700, fontSize: '15px', cursor: 'pointer' };
const errorStyle = { display: 'flex', gap: '9px', alignItems: 'flex-start', marginTop: '18px', padding: '12px', border: '1px solid #9e4b4b', borderRadius: '7px', color: '#ffb5b5', background: 'rgba(120,30,30,.18)' };

/**
 * ARTIFACT: client/src/components/sovereign/TenantDiscovery.jsx
 * VERSION: v3.2.0-INSTITUTIONAL-AUTH-BRAND
 * AUTHORITY BOUNDARY: bounded discovery projection only
 * TENANT POSTURE: no client-side directory enumeration or fallback tenant
 * FAIL-CLOSED POSTURE: discovery failure leaves tenant unresolved
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
