import { describe, expect, it } from 'vitest';
import { buildTenantBrandingConfig } from './ExecutiveCommandOrchestrator.js';

describe('executive tenant branding descriptor projection', () => {
  it('keeps canonical authenticated logo descriptors out of img src and exposes them to the asset hook', () => {
    const descriptor = {
      kind: 'LOGO',
      reference: 'asset:WILSYTENANT-TEST:logo:primary',
      contentFingerprint: 'a'.repeat(128),
      mediaType: 'image/jpeg',
    };
    const branding = buildTenantBrandingConfig({
      tenantId: 'WILSYTENANT-TEST',
      legalName: 'Example (Pty) Ltd',
      branding: { logo: descriptor },
    });

    expect(branding.logo).toBeNull();
    expect(branding.assetDescriptor).toEqual(descriptor);
    expect(branding.displayName).toBe('Example (Pty) Ltd');
  });

  it('does not treat opaque asset references or arbitrary objects as browser URLs', () => {
    for (const logo of [
      'asset:WILSYTENANT-TEST:logo:primary',
      { reference: 'asset:foreign:logo', contentFingerprint: 'b'.repeat(128) },
      { toString: () => '[object Object]' },
    ]) {
      const branding = buildTenantBrandingConfig({
        name: 'Tenant',
        branding: { logo },
      });
      expect(branding.logo).toBeNull();
      expect(branding.assetDescriptor).toBeNull();
    }
  });

  it('preserves text-only tenant branding when no authenticated logo descriptor exists', () => {
    const branding = buildTenantBrandingConfig({
      name: 'Wilsy Limited',
      branding: { primaryColor: '#D4AF37' },
    });
    expect(branding.logo).toBeNull();
    expect(branding.assetDescriptor).toBeNull();
    expect(branding.initials).toBe('WL');
  });
});
