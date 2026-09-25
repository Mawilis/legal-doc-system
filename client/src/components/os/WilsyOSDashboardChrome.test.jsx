/**
 * TITLE: WILSY OS Shared Dashboard Chrome Branding Presentation Certificate
 * VERSION: v2.0.0-D21B9-SHARED-CHROME-BRANDING-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certify that shared dashboard chrome accepts tenant branding only
 *          from the authenticated D21B8 tenant projection and never promotes
 *          legacy logo/path/browser fields into presentation authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/os/WilsyOSDashboardChrome.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-25
 * AUTHORITY BOUNDARY: Browser presentation only; Python EOS/D21B2B-D21B8 own branding truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
 */

import { describe, expect, it } from 'vitest';
import { resolveWilsyChromeIdentitySources } from './wilsyDashboardChromeConfig';

const fingerprint = (character) => character.repeat(128);

const authenticatedTenant = {
  tenantId: 'ACME-001',
  name: 'Acme Legal',
  status: 'ACTIVE',
  branding: {
    tenantId: 'ACME-001',
    profileId: 'profile-1',
    profileFingerprint: fingerprint('a'),
    selectionId: 'selection-1',
    selectionRevision: 2,
    entitlementId: 'entitlement-1',
    entitlementRevision: 3,
    entitlementFingerprint: fingerprint('b'),
    brandingTier: 'TENANT_BRANDING_PROFESSIONAL',
    profileLabel: 'Acme Legal Professional',
    primaryColor: '#112233',
    secondaryColor: '#445566',
    accentColor: '#AABBCC',
    emailDisplayName: 'Acme Legal',
    platformTrustMarkRequired: true,
    logo: {
      reference: 'asset:ACME-001:logo:primary',
      contentFingerprint: fingerprint('c'),
      mediaType: 'image/png',
      kind: 'LOGO',
    },
    favicon: null,
  },
};

describe('resolveWilsyChromeIdentitySources D21B9', () => {
  it('preserves descriptive explicit tenant/operator priority without trusting raw logo props', () => {
    const result = resolveWilsyChromeIdentitySources({
      tenant: {
        displayName: 'Acme Legal',
        logo: '/logos/acme.png',
        logoUrl: 'https://example.invalid/acme.png',
        status: 'ACTIVE',
        tenantId: 'ACME-001',
      },
      operator: {
        displayName: 'Jane Doe',
        roleLabel: 'General Counsel',
        email: 'jane@acme.com',
      },
      authUser: {
        firstName: 'Ada',
        lastName: 'Lovelace',
        role: 'Founder',
        email: 'ada@wilsy.os',
      },
      activeTenant: {
        name: 'Context Tenant',
        tenantId: 'CONTEXT-42',
        logo: '/logos/context.png',
      },
    });

    expect(result.tenant.displayName).toBe('Acme Legal');
    expect(result.tenant.tenantId).toBe('ACME-001');
    expect(result.tenant.logo).toBeNull();
    expect(result.tenant.branding).toBeNull();
    expect(result.operator.displayName).toBe('Jane Doe');
    expect(result.operator.roleLabel).toBe('General Counsel');
    expect(result.operator.email).toBe('jane@acme.com');
  });

  it('projects only D21B8 authenticated branding metadata and keeps assets opaque', () => {
    const result = resolveWilsyChromeIdentitySources({
      authenticatedTenant,
      tenant: {
        tenantId: 'ACME-001',
        displayName: 'Acme Legal Workspace',
        logo: '/legacy/should-not-render.png',
      },
    });

    expect(result.tenant.displayName).toBe('Acme Legal Workspace');
    expect(result.tenant.logo).toBeNull();
    expect(result.tenant.primaryColor).toBe('#112233');
    expect(result.tenant.secondaryColor).toBe('#445566');
    expect(result.tenant.accentColor).toBe('#AABBCC');
    expect(result.tenant.brandingProfileLabel).toBe('Acme Legal Professional');
    expect(result.tenant.platformTrustMarkRequired).toBe(true);
    expect(result.tenant.branding).toEqual({
      tenantId: 'ACME-001',
      profileId: 'profile-1',
      profileLabel: 'Acme Legal Professional',
      brandingTier: 'TENANT_BRANDING_PROFESSIONAL',
      primaryColor: '#112233',
      secondaryColor: '#445566',
      accentColor: '#AABBCC',
      emailDisplayName: 'Acme Legal',
      platformTrustMarkRequired: true,
      logo: {
        reference: 'asset:ACME-001:logo:primary',
        contentFingerprint: fingerprint('c'),
        mediaType: 'image/png',
        kind: 'LOGO',
      },
      favicon: null,
    });
    expect(JSON.stringify(result)).not.toContain('/legacy/');
    expect(JSON.stringify(result)).not.toContain('https://');
  });

  it('suppresses foreign authenticated branding instead of falling back to legacy branding', () => {
    const foreign = {
      ...authenticatedTenant,
      tenantId: 'ACME-001',
      branding: {
        ...authenticatedTenant.branding,
        tenantId: 'FOREIGN-999',
      },
      logo: '/legacy/acme.png',
    };
    const result = resolveWilsyChromeIdentitySources({
      authenticatedTenant: foreign,
      activeTenant: {
        tenantId: 'ACME-001',
        branding: { primaryColor: '#FFFFFF' },
        logoUrl: '/legacy/context.png',
      },
    });

    expect(result.tenant.branding).toBeNull();
    expect(result.tenant.logo).toBeNull();
    expect(result.tenant.primaryColor).toBeNull();
    expect(result.tenant.platformTrustMarkRequired).toBe(false);
  });

  it('does not treat non-authenticated tenant context branding as authority', () => {
    const result = resolveWilsyChromeIdentitySources({
      authUser: {
        firstName: 'Ada',
        lastName: 'Lovelace',
        role: 'Founder',
        email: 'ada@wilsy.os',
      },
      activeTenant: {
        name: 'Wilsy Tenant',
        tenantId: 'WILSY-42',
        branding: {
          tenantId: 'WILSY-42',
          profileId: 'browser-invented',
          primaryColor: '#FFFFFF',
        },
        logo: '/logos/wilsy.png',
        status: 'LIVE',
      },
    });

    expect(result.tenant.displayName).toBe('Wilsy Tenant');
    expect(result.tenant.tenantId).toBe('WILSY-42');
    expect(result.tenant.logo).toBeNull();
    expect(result.tenant.branding).toBeNull();
    expect(result.operator.displayName).toBe('Ada Lovelace');
    expect(result.operator.roleLabel).toBe('Founder');
  });
});

// ARTIFACT: WilsyOSDashboardChrome.test.jsx
// VERSION: v2.0.0-D21B9-SHARED-CHROME-BRANDING-CERT
// AUTHORITY BOUNDARY: browser presentation certificate only; no source authority
// TENANT POSTURE: branding accepted only from exact authenticated tenant projection
// FAIL-CLOSED POSTURE: legacy/foreign/browser branding is suppressed
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
