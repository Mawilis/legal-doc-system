/**
 * TITLE: WILSY OS Founder-Supplied Brand Asset Certificate
 * VERSION: v1.3.1-FOUNDER-CORPORATE-IDENTITY-LOCK
 * AUTHORITY: Founder-selected original bitmap and canonical company identifier.
 * EPITOME: Pin the exact selected logo path and bytes so a letter or alternative
 * emblem cannot silently replace it in shared authenticated company surfaces.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/config/wilsyDashboardChromeConfig.test.js
 * COLLABORATION / OWNERSHIP: App, CompanyOperatingDocumentViewer and chrome identity config.
 * CERTIFICATION / UPDATE DATE: 2026-11-13
 * CHANGELOG: v1.3.1-FOUNDER-CORPORATE-IDENTITY-LOCK pins the vivid square corporate identity and separate AI symbol while preserving all square-source, icon and tenant-branding checks.
 * CHANGELOG: v1.2.0-OFFICIAL-SQUARE-ARTWORK-CERT pins the newly supplied source and
 * framed presentation derivative, preserves prior approved assets and verifies
 * embedded SVG compatibility bytes plus shared authentication/logo consumers.
 * CHANGELOG: v1.1.0-SUPPLIED-LOGO-IDENTITY-CERT retains exact tenant tests and
 * adds the shared logo constant plus original asset SHA3-512 regression.
 * COMPLIANCE: Presentation only; no personal data, logs or network.
 * SECURITY / PRIVACY POSTURE: Static asset bytes only; no authorization inference.
 * TENANT BOUNDARY: Only the exact canonical identifier matches company presentation.
 * AUTHORITY BOUNDARY: No role, entitlement, transaction or business mutation.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import { describe, expect, it } from 'vitest';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { isWilsyPlatformTenant, WILSY_PLATFORM_LOGO_SRC, WILSY_PLATFORM_LOGO_SOURCE_SRC } from '../../src/components/os/wilsyDashboardChromeConfig.js';

describe('WILSY platform tenant mark selection', () => {
  it('uses the canonical platform mark only for the exact WILSY tenant', () => {
    expect(isWilsyPlatformTenant('WILSYTENANT-4CD2FZ4O')).toBe(true);
    expect(isWilsyPlatformTenant('WILSYTENANT-OTHER')).toBe(false);
    expect(isWilsyPlatformTenant('wilsytenant-4cd2fz4o')).toBe(false);
    expect(isWilsyPlatformTenant(null)).toBe(false);
    expect(isWilsyPlatformTenant(undefined)).toBe(false);
  });
});


const asset = path => readFileSync(resolve(process.cwd(), path));
const digest = bytes => createHash('sha3-512').update(bytes).digest('hex');

describe('Founder-provided official WILSY OS artwork', () => {
  it('keeps the original master and approved icon bytes unchanged', () => {
    expect(digest(asset('public/brand/wilsy-os-master.png'))).toBe('3b04981ace59c96aec55f4543aad6c8e1e76ae5451cb8773eb4a3c3e24d5341f6f9d62ef7b6d9df7ec75c40a5281cdfc8604cd7e2f2c8fc069f34423e689e531');
    expect(digest(asset('public/icons/icon-192.png'))).toBe('de89f551130af8e95aba9a67fc1d865d047595544e43f4c638825c76626ef1ead9e493ed25cf9a261ad450f64724a043631c020e5053ac4cb9969fa982f92234');
  });
  it('pins the exact newly supplied source and complete framed presentation', () => {
    expect(WILSY_PLATFORM_LOGO_SOURCE_SRC).toBe('/brand/wilsy-os-official-source.png');
    expect(WILSY_PLATFORM_LOGO_SRC).toBe('/brand/wilsy-os-official.png');
    expect(digest(asset('public' + WILSY_PLATFORM_LOGO_SOURCE_SRC))).toBe('f2128965e52523e8bb2764e418ccc624040ab31d90e0d9b03158874a0a0f7a556003454315e6cfc308eb085740137f99909facc39b8a1482624a04a2fa55dc73');
    const presentation = asset('public' + WILSY_PLATFORM_LOGO_SRC);
    expect(presentation.readUInt32BE(16)).toBe(512); expect(presentation.readUInt32BE(20)).toBe(512);
    expect(digest(presentation)).toBe('6b2b21d4b0d7ccacd94aa7944cacaab921a60cfec8115b3e1a2907139bcf173b07754dfaa355ce3969b142b8cefc5e2a907a4bba12216b33667744651ed3d348');
  });
  it('keeps every compatibility SVG self-contained and bound to the same official artwork', () => {
    const expected = digest(asset('public' + WILSY_PLATFORM_LOGO_SRC));
    for (const path of ['src/assets/logo/wilsy-logo.svg', 'src/assets/logo/wilsy-icon.svg', 'src/assets/logo/wilsy-header-emblem.svg', 'public/assets/images/superadmin/wilsy-logo.svg', 'public/favicon.svg']) {
      const svg = asset(path).toString();
      const embedded = [...svg.matchAll(/href="data:image\/png;base64,([^"]+)"/g)];
      expect(embedded).toHaveLength(1);
      expect(digest(Buffer.from(embedded[0][1], 'base64'))).toBe(expected);
      expect(svg).not.toContain('<path');
      expect(svg).toContain('preserveAspectRatio="xMidYMid meet"');
    }
  });
  it('preserves the square corporate identity while keeping the creative AI symbol separate', () => {
    expect(asset('src/App.jsx').toString()).toContain('src={WILSY_PLATFORM_LOGO_SRC}');
    expect(asset('src/App.jsx').toString()).not.toContain('/brand/wilsy-ai-emblem.svg');
    expect(asset('src/App.jsx').toString()).not.toContain('WILSY_PLATFORM_HEADER_EMBLEM_SRC');
    expect(asset('src/components/workspaces/WilsyHeadquartersWorkspace.jsx').toString()).toContain('src={WILSY_PLATFORM_LOGO_SRC}');
    expect(asset('src/components/intelligence/WilsyOSIntelligenceDock.jsx').toString()).toContain('/brand/wilsy-ai-emblem.svg');
  });
  it('routes platform marks through the shared setting while preserving tenant branding', () => {
    for (const path of ['src/App.jsx', 'src/components/workspaces/CompanyOperatingDocumentViewer.jsx', 'src/components/auth/SovereignLogin.jsx', 'src/components/auth/SovereignMfaPortal.jsx', 'src/components/sovereign/TenantDiscovery.jsx']) {
      const code = asset(path).toString();
      expect(code).toContain('src={WILSY_PLATFORM_LOGO_SRC}');
      expect(code).not.toContain('src="/brand/wilsy-os-master.png"');
      expect(code).not.toContain('src="/brand/wilsy-gold-emblem.png"');
    }
  });
});

// ARTIFACT: wilsyDashboardChromeConfig.test.js
// VERSION: v1.3.1-FOUNDER-CORPORATE-IDENTITY-LOCK
// AUTHORITY BOUNDARY: Static brand/identity certificate only.
// TENANT POSTURE: Exact company selector; no new tenant authority.
// FAIL-CLOSED POSTURE: Changed logo path or bytes fails regression.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
