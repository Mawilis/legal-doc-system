/**
 * WILSY OS — PREMIUM TENANT IDENTITY PROJECTION
 * VERSION: v1.3.0-FINAL-PIXEL-CLOSURE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Presents the bounded, server-issued tenant identity beside the
 *          permanent WILSY OS platform trust mark without creating branding,
 *          authentication, entitlement, or tenant authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/TenantIdentityCard.jsx
 * COLLABORATION / OWNERSHIP: TenantDiscovery and SovereignLogin consume this
 *                            projection; Python EOS owns tenant truth.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.3.0-FINAL-PIXEL-CLOSURE — Makes monogram precedence follow
 *            authoritative display name first, removes punctuation and
 *            corporate designators from fallback initials, and removes the
 *            redundant platform image from the trust row.
 *            v1.2.0-PUBLIC-IDENTITY-CONTRACT — Removed the internal tenant ID
 *            disclosure from unauthenticated presentation while retaining the
 *            authoritative tenant object for downstream routing.
 *            v1.1.0-INSTITUTIONAL-AUTH-BRAND — Replaced the generic geometric
 *            mark with the established WILSY brand asset and made the tenant
 *            identity an integrated, non-card authentication zone.
 *            v1.0.0-PREMIUM-TENANT-IDENTITY-SLOT — Added a neutral tenant
 *            monogram fallback and bounded legal-name/verified presentation.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: No alias-to-logo mapping, inferred legal name,
 *                             secret, commercial, or security metadata.
 * TENANT BOUNDARY: Every visible tenant value comes from the authoritative
 *                  discovery projection supplied by the caller.
 * AUTHORITY BOUNDARY: Presentation projection only; no tenant membership,
 *                      authentication, authorization, or entitlement grant.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';

/**
 * @description Derive a neutral monogram from authoritative display/legal text.
 * @param {object} tenant - Server-issued bounded tenant projection.
 * @returns {string} One- or two-letter presentation monogram.
 * @institutional Prevents a missing tenant logo from becoming a fake
 *               alias-specific brand while retaining a premium identity slot.
 */
export function tenantMonogram(tenant = {}) {
  const displayName = typeof tenant.name === 'string' ? tenant.name.trim() : '';
  const legalName = typeof tenant.legalName === 'string' ? tenant.legalName.trim() : '';
  const alias = typeof tenant.alias === 'string' ? tenant.alias.trim() : '';
  const source = displayName || legalName || alias;
  if (!source) return 'W';

  const isLegalFallback = !displayName && Boolean(legalName);
  const corporateDesignators = new Set([
    'pty', 'proprietary', 'ltd', 'limited', 'inc', 'incorporated', 'llc',
    'llp', 'lp', 'plc', 'corp', 'corporation', 'company', 'co', 'gmbh',
    'bv', 'nv', 'ag', 'sa', 'sarl',
  ]);
  const words = source
    .split(/[^\p{L}\p{N}]+/u)
    .filter(Boolean)
    .filter((word) => !isLegalFallback || !corporateDesignators.has(word.toLocaleLowerCase()));
  if (!words.length) return 'W';

  const initials = words
    .slice(0, 2)
    .map((word) => Array.from(word)[0] || '')
    .join('')
    .toLocaleUpperCase();
  return Array.from(initials).slice(0, 2).join('') || 'W';
}

/**
 * @description Render the permanent platform mark and bounded tenant identity.
 * @param {object} props - Component properties.
 * @param {object|null} props.tenant - Authoritative discovery projection.
 * @param {string} [props.className] - Optional host class for future layouts.
 * @returns {JSX.Element} Institutional identity projection.
 * @institutional Keeps WILSY OS as the trust anchor while reserving a future
 *               chargeable branding slot that cannot grant authority.
 */
export default function TenantIdentityCard({ tenant, className = '', integrated = false }) {
  if (!tenant) return null;

  const legalName = typeof tenant.legalName === 'string' ? tenant.legalName.trim() : '';
  const displayName = typeof tenant.name === 'string' ? tenant.name.trim() : '';
  const alias = typeof tenant.alias === 'string' ? tenant.alias.trim() : '';
  const monogram = tenantMonogram(tenant);

  const shellStyle = integrated ? integratedCardStyle : cardStyle;

  return (
    <section className={`tenant-identity-card ${integrated ? 'tenant-identity-card--integrated' : ''} ${className}`.trim()} aria-label="Tenant identity" style={shellStyle}>
      <div style={identityRowStyle}>
        <div style={identityMarkStyle} aria-hidden="true">
          <span style={identityMarkTextStyle}>{monogram}</span>
        </div>
        <div style={identityTextStyle}>
          <span style={eyebrowStyle}>Institutional workspace</span>
          <strong style={legalName ? primaryNameStyle : displayNameStyle}>
            {legalName || displayName || 'Workspace'}
          </strong>
          {legalName && displayName && legalName !== displayName && (
            <span style={secondaryNameStyle}>{displayName}</span>
          )}
          {alias && <span style={aliasStyle}>Workspace: {alias}</span>}
          {tenant.verified === true && (
            <span style={verifiedStyle} role="status">Verified workspace</span>
          )}
        </div>
      </div>
      <div style={trustRowStyle}>
        <span style={trustAccentStyle} aria-hidden="true" />
        <span>Secured by WILSY OS</span>
      </div>
    </section>
  );
}

const identityRowStyle = { display: 'flex', alignItems: 'center', gap: '20px' };
const cardStyle = {
  marginBottom: '28px', padding: '20px', border: '1px solid rgba(213,176,79,.22)',
  borderRadius: '12px', background: 'linear-gradient(145deg, rgba(37,38,38,.86), rgba(25,27,28,.76))',
};
const integratedCardStyle = {
  margin: 0, padding: 0, border: 0, borderRadius: 0, background: 'transparent',
};
const identityMarkStyle = {
  display: 'grid', placeItems: 'center', flex: '0 0 72px', width: '72px', height: '72px',
  border: '1px solid rgba(213,176,79,.42)', borderRadius: '50%',
  background: 'radial-gradient(circle at 50% 40%, rgba(213,176,79,.16), rgba(20,22,23,.1) 68%)', color: '#e4c66f',
};
const identityMarkTextStyle = {
  margin: 0, color: '#f2d681', fontSize: '23px', fontWeight: 700, letterSpacing: '.08em', lineHeight: 1,
};
const identityTextStyle = { display: 'grid', gap: '6px', minWidth: 0 };
const eyebrowStyle = { color: '#a9a59b', fontSize: '10px', fontWeight: 700, letterSpacing: '.16em', textTransform: 'uppercase' };
const primaryNameStyle = { color: '#fbf8f0', fontSize: '21px', lineHeight: 1.15, letterSpacing: '-.01em' };
const displayNameStyle = { color: '#fbf8f0', fontSize: '21px', lineHeight: 1.15, letterSpacing: '-.01em' };
const secondaryNameStyle = { color: '#d0cbc0', fontSize: '14px' };
const aliasStyle = { color: '#aaa69c', fontSize: '12px', letterSpacing: '.04em' };
const verifiedStyle = { color: '#c9e7d5', fontSize: '11px', fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase' };
const trustRowStyle = {
  display: 'flex', alignItems: 'center', gap: '9px', marginTop: '22px', color: '#b8b6ae',
  fontSize: '11px', letterSpacing: '.08em', textTransform: 'uppercase',
};
const trustAccentStyle = { width: '8px', height: '8px', borderRadius: '50%', background: '#d5b04f', boxShadow: '0 0 0 4px rgba(213,176,79,.12)' };
/**
 * ARTIFACT: TenantIdentityCard.jsx
 * VERSION: v1.3.0-FINAL-PIXEL-CLOSURE
 * AUTHORITY BOUNDARY: bounded tenant presentation only
 * TENANT POSTURE: legal name, display name, alias, and verified state are
 *                 rendered only when supplied by the authoritative projection;
 *                 internal tenant identifiers stay out of public auth UI
 * FAIL-CLOSED POSTURE: missing tenant identity renders no fabricated tenant;
 *                      missing logo renders a neutral monogram
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
