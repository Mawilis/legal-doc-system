/**
 * TITLE: D21B13 authenticated tenant-branding HTTP and browser certificate
 * VERSION: v1.0.0-D21B13-AUTHENTICATED-BRANDING-BROWSER-CERT
 * AUTHORITY: Disposable browser and HTTP observation only.
 * EPITOME: Prove real authenticated workspace-bootstrap and logo/favicon byte
 *          delivery from UUID-scoped canonical Mongo branding records, tenant
 *          selector resistance, transport headers, and transient browser render.
 * ABSOLUTE CANONICAL PATH:
 *   /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/tenant-branding.browser.spec.js
 * COLLABORATION / OWNERSHIP: EOS owns tenant/IAM/branding truth; this certificate
 *                            observes the existing authenticated route/client.
 * CERTIFICATION / UPDATE DATE: 2026-10-24
 * CHANGELOG: v1.0.0 certifies authenticated logo/favicon responses, forged
 *            selector resistance, and shared-chrome blob rendering from the
 *            disposable D21B13 fixture without logging tokens or image bytes.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic principal only; bearer values and image
 *                             bodies are never printed or embedded in failures.
 * TENANT BOUNDARY: One authenticated tenant and a distinct unjoined foreign
 *                  tenant, both inside the fixture-owned disposable database.
 * AUTHORITY BOUNDARY: Test evidence only; no IAM, branding, legal, or financial
 *                     authority is created.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { createHash } from 'node:crypto';
import fs from 'node:fs';

import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
const baseURL = process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174';
const pngSignature = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

if (!statePath) {
  throw new Error('BROWSER_CERT_STATE_REQUIRED');
}

const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));

function endpoint(path) {
  return new URL(path, baseURL).toString();
}

async function expectPngResponse(response, expectedFingerprint) {
  expect(response.status(), 'authenticated branding response status').toBe(200);
  const headers = response.headers();
  expect(headers['content-type']?.split(';', 1)[0]).toBe('image/png');
  expect(headers['cache-control']).toBe('private, no-store');
  expect(headers.pragma).toBe('no-cache');
  expect(headers['x-content-type-options']).toBe('nosniff');
  expect(headers['cross-origin-resource-policy']).toBe('same-origin');

  const body = await response.body();
  expect(body.length, 'branding response body must be nonempty').toBeGreaterThan(8);
  expect(body.subarray(0, 8).equals(pngSignature), 'branding PNG signature').toBe(true);
  expect(createHash('sha3-512').update(body).digest('hex')).toBe(expectedFingerprint);
}

test('authenticated branding HTTP is tenant-bound and shared chrome renders its blob', async ({
  browser,
  request,
}) => {
  const actor = state.actors?.partner;
  expect(actor, 'synthetic authenticated Legal actor is present').toBeTruthy();
  expect(state.branding?.logo_fingerprint).toMatch(/^[0-9a-f]{128}$/);
  expect(state.foreign_branding?.logo_fingerprint).toMatch(/^[0-9a-f]{128}$/);
  expect(state.branding.logo_fingerprint).not.toBe(state.foreign_branding.logo_fingerprint);

  const authorization = { Authorization: `Bearer ${actor.access_token}` };
  const bootstrapResponse = await request.get(endpoint('/api/auth/workspace-bootstrap'), {
    headers: authorization,
  });
  expect(bootstrapResponse.status(), 'authenticated workspace bootstrap').toBe(200);
  const bootstrap = await bootstrapResponse.json();
  expect(bootstrap.workspace.tenant.tenantId).toBe(state.tenant_id);
  expect(bootstrap.workspace.branding.logo.reference).toBe(state.branding.logo_reference);
  expect(bootstrap.workspace.branding.logo.contentFingerprint).toBe(
    state.branding.logo_fingerprint,
  );

  const forgedSelectors = new URLSearchParams({
    tenant_id: state.foreign_tenant_id,
    tenantId: state.foreign_tenant_id,
    reference: state.foreign_branding.logo_reference,
    asset_reference: state.foreign_branding.logo_reference,
    content_fingerprint: state.foreign_branding.logo_fingerprint,
  });
  const logoResponse = await request.get(
    endpoint(`/api/auth/workspace-branding/logo?${forgedSelectors.toString()}`),
    { headers: authorization },
  );
  await expectPngResponse(logoResponse, state.branding.logo_fingerprint);

  const faviconResponse = await request.get(
    endpoint(`/api/auth/workspace-branding/favicon?${forgedSelectors.toString()}`),
    { headers: authorization },
  );
  await expectPngResponse(faviconResponse, state.branding.favicon_fingerprint);

  const unauthenticatedResponse = await request.get(
    endpoint('/api/auth/workspace-branding/logo'),
  );
  expect(unauthenticatedResponse.status(), 'branding route requires authentication').toBe(401);

  const context = await browser.newContext({ baseURL });
  try {
    const page = await context.newPage();
    await page.addInitScript(
      ({ accessToken, tenantId, principalId, email }) => {
        localStorage.setItem('wilsy_auth_token', accessToken);
        localStorage.setItem('token', accessToken);
        localStorage.setItem('tenantId', tenantId);
        localStorage.setItem('wilsy_tenant_id', tenantId);
        localStorage.setItem(
          'wilsy_active_tenant',
          JSON.stringify({ tenantId, id: tenantId }),
        );
        localStorage.setItem(
          'wilsy_sovereign_user',
          JSON.stringify({ id: principalId, email, tenantId }),
        );
      },
      {
        accessToken: actor.access_token,
        tenantId: state.tenant_id,
        principalId: actor.principal_id,
        email: actor.email,
      },
    );

    const browserBootstrap = page.waitForResponse((response) => (
      new URL(response.url()).pathname === '/api/auth/workspace-bootstrap'
      && response.request().method() === 'GET'
    ));
    const browserLogo = page.waitForResponse((response) => (
      new URL(response.url()).pathname === '/api/auth/workspace-branding/logo'
      && response.request().method() === 'GET'
    ));
    await page.goto('/');

    const browserBootstrapResponse = await browserBootstrap;
    expect(browserBootstrapResponse.status(), 'browser authenticated workspace bootstrap').toBe(200);
    const browserProjection = await browserBootstrapResponse.json();
    expect(browserProjection.workspace.tenant.tenantId).toBe(state.tenant_id);
    const renderedLogoResponse = await browserLogo;
    await expectPngResponse(renderedLogoResponse, state.branding.logo_fingerprint);

    const logo = page.locator('[data-wilsy-legal-tenant-logo="ready"] img');
    await expect(logo, 'shared Legal chrome renders authenticated tenant logo').toBeVisible();
    await expect(logo).toHaveAttribute('src', /^blob:/);
    await expect(page.getByLabel('WILSY Legal OS platform mark')).toBeVisible();
  } finally {
    await context.close();
  }
});

// ARTIFACT: tenant-branding.browser.spec.js
// VERSION: v1.0.0-D21B13-AUTHENTICATED-BRANDING-BROWSER-CERT
// AUTHORITY BOUNDARY: disposable live-route and browser observation only
// TENANT POSTURE: authenticated synthetic tenant plus unjoined foreign tenant
// FAIL-CLOSED POSTURE: absent auth, wrong tenant, response metadata, bytes, or render fails
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
