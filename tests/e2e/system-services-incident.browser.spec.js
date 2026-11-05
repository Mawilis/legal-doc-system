/**
 * TITLE: WILSY EOS System Services incident and responder browser certificate
 * VERSION: v1.0.0-SYSTEM-SERVICES-AUTHENTICATED-INCIDENT-JOURNEY
 * AUTHORITY: Browser certification evidence only.
 * EPITOME: Prove authenticated SYSTEM queue and responder inbox projections,
 *          independently seeded permissions and active PLATFORM workforce,
 *          exact assignment detail, and revision-guarded responder acceptance.
 * TENANT BOUNDARY: One UUID-isolated synthetic tenant and disposable database.
 * AUTHORITY BOUNDARY: EOS authorizer and canonical routes remain authoritative.
 * FINANCIAL AUTHORITY BOUNDARY: None.
 * FAIL-CLOSED DECLARATION: Missing permission, workforce evidence, API response,
 *                          assignment correlation or browser projection fails.
 */

import fs from 'node:fs';
import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const baseURL = process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174';
const systemTestPassword = ['Synthetic', 'Platform', 'Password', '123!'].join('-');

async function openSystemServices(browser, actorKey = 'system_responder') {
  const actor = state.system_actors?.[actorKey];
  if (!actor?.access_token) throw new Error('BROWSER_CERT_SYSTEM_ACTOR_MISSING:' + actorKey);
  const context = await browser.newContext({ baseURL, viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  await page.addInitScript(({ accessToken, tenantId, principalId, email }) => {
    localStorage.setItem('wilsy_auth_token', accessToken);
    localStorage.setItem('token', accessToken);
    localStorage.setItem('tenantId', tenantId);
    localStorage.setItem('wilsy_tenant_id', tenantId);
    localStorage.setItem('wilsy_active_tenant', JSON.stringify({ tenantId, id: tenantId }));
    localStorage.setItem('wilsy_sovereign_user', JSON.stringify({
      id: principalId, email, tenantId,
    }));
  }, {
    accessToken: actor.access_token,
    tenantId: state.tenant_id,
    principalId: actor.principal_id,
    email: actor.email,
  });
  const authBootstrap = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/auth/workspace-bootstrap'
    && response.request().method() === 'GET'
  ));
  const systemBootstrap = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/system-services/workspace-bootstrap'
    && response.request().method() === 'GET'
  ));
  await page.goto('/');
  const [tenantBootstrapResponse, systemBootstrapResponse] = await Promise.all([
    authBootstrap,
    systemBootstrap,
  ]);
  // SYSTEM workforce principals intentionally have no tenant membership.
  // Tenant bootstrap must deny; the separate SYSTEM authority must succeed.
  expect(tenantBootstrapResponse.status()).toBe(403);
  expect(systemBootstrapResponse.status()).toBe(200);
  await expect.poll(() => page.evaluate(() => {
    const user = JSON.parse(localStorage.getItem('wilsy_sovereign_user') || 'null');
    return {
      tenantId: localStorage.getItem('tenantId'),
      legacyTenantId: localStorage.getItem('wilsy_tenant_id'),
      activeTenant: localStorage.getItem('wilsy_active_tenant'),
      systemScope: user?.systemServicesWorkspace?.scope || null,
      principalMatches: user?.id === user?.systemServicesWorkspace?.principalId,
    };
  })).toEqual({
    tenantId: null,
    legacyTenantId: null,
    activeTenant: null,
    systemScope: 'SYSTEM',
    principalMatches: true,
  });
  console.log('[SYSTEM DASHBOARD SURFACE]', JSON.stringify({
    url: page.url(),
    bodyText: await page.locator('body').innerText(),
  }));
  // localStorage can be populated immediately before React commits the authenticated
  // SYSTEM dashboard. Wait for the rendered workspace before sending its shortcut.
  await expect(page.getByRole('heading', { name: 'System Services' })).toBeVisible();
  await page.keyboard.press('Control+k');
  const dialog = page.getByRole('dialog', { name: 'Wilsy OS Global Search' });
  await expect(dialog).toBeVisible();
  const workspaceResponse = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/system-services/workspace-bootstrap'
    && response.request().method() === 'GET'
  ));
  await dialog.getByPlaceholder(/Search Wilsy OS/).fill('System Services');
  await dialog.getByRole('button', { name: /System Services/ }).click();
  const resolvedWorkspaceResponse = await workspaceResponse;
  return { context, page, workspaceResponse: resolvedWorkspaceResponse };
}

test('certifies SYSTEM incident queue, principal-bound responder inbox and acceptance', async ({ browser }) => {
  const { context, page, workspaceResponse } = await openSystemServices(browser);

  expect(workspaceResponse.status()).toBe(200);
  const workspace = await workspaceResponse.json();
  expect(workspace.status).toBe('READY');
  expect(workspace.authority).toBe('EOS_SYSTEM_SERVICES');
  expect(workspace.capabilities).toContain('system_services:queue:read');
  expect(workspace.capabilities).toContain('system_services:incident:escalate');

  await expect(page.getByRole('heading', { name: 'System Services' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Security incident queue' })).toBeVisible();
  await expect(page.getByText('SUSPECTED_ACCOUNT_COMPROMISE')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'My responder assignments' })).toBeVisible();
  await expect(page.getByText(state.system_assignment_id)).toBeVisible();

  const detailResponsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname.endsWith('/security-incident-assignments/' + state.system_assignment_id)
    && response.request().method() === 'GET'
  ));
  await page.getByRole('button', { name: 'View incident' }).click();
  const detailResponse = await detailResponsePromise;
  expect(detailResponse.status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Incident detail' })).toBeVisible();
  await expect(page.getByText('Category: SUSPECTED_ACCOUNT_COMPROMISE')).toBeVisible();

  const decisionResponsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname.endsWith('/security-incident-assignments/' + state.system_assignment_id + '/accept')
    && response.request().method() === 'POST'
  ));
  await page.getByRole('button', { name: 'Accept' }).click();
  const decisionResponse = await decisionResponsePromise;
  expect(decisionResponse.status()).toBe(200);
  await expect(page.getByText('ACCEPTED', { exact: true })).toBeVisible();
  await expect(page.getByRole('status').filter({ hasText: 'No containment or account action was performed' })).toBeVisible();

  await context.close();
});

test('does not expose responder inbox to an independently authorized triage-only principal', async ({ browser }) => {
  const { context, page, workspaceResponse } = await openSystemServices(browser, 'system_triage');

  expect(workspaceResponse.status()).toBe(200);
  const workspace = await workspaceResponse.json();
  expect(workspace.capabilities).toContain('system_services:queue:read');
  expect(workspace.capabilities).not.toContain('system_services:incident:escalate');
  await expect(page.getByRole('heading', { name: 'Security incident queue' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'My responder assignments' })).toHaveCount(0);
  const deniedStatus = await page.evaluate(async () => {
    const token = localStorage.getItem('wilsy_auth_token');
    const response = await fetch('/api/system-services/security-incident-assignments/mine', {
      headers: { Authorization: 'Bearer ' + token },
    });
    return response.status;
  });
  expect(deniedStatus).toBe(403);
  await context.close();
});

test('certifies initial tenant-neutral SYSTEM credentials, MFA and workspace bootstrap in the browser', async ({ browser }) => {
  const context = await browser.newContext({
    baseURL,
    viewport: { width: 1440, height: 1000 },
  });
  const page = await context.newPage();
  const calls = [];

  await page.route('**/api/auth/global/login', async (route) => {
    calls.push('global-login');
    const body = route.request().postDataJSON();
    expect(body).toEqual({
      email: 'platform-responder@example.com',
      password: systemTestPassword,
    });
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'MFA_REQUIRED',
        scope: 'SYSTEM',
        mfa_challenge: 'sysmfa-browser-one-time',
        workspace_id: 'SYSTEM_SERVICES',
      }),
    });
  });

  await page.route('**/api/auth/global/verify-mfa', async (route) => {
    calls.push('global-mfa');
    expect(route.request().postDataJSON()).toEqual({
      mfa_challenge: 'sysmfa-browser-one-time',
      code: '123456',
    });
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'AUTHENTICATED',
        scope: 'SYSTEM',
        access_token: 'synthetic-system-access-token',
        refresh_token: 'sysrefresh-browser-token',
        principal_id: 'WILSYAUTH-browser-system-principal',
        workspace_id: 'SYSTEM_SERVICES',
      }),
    });
  });

  await page.route('**/api/system-services/workspace-bootstrap', async (route) => {
    calls.push('system-workspace');
    expect(route.request().headers().authorization).toBe('Bearer synthetic-system-access-token');
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'READY',
        authority: 'EOS_SYSTEM_SERVICES',
        principalId: 'WILSYAUTH-browser-system-principal',
        scope: 'SYSTEM',
        capabilities: ['system_services:queue:read'],
        summary: { openCases: 0, securityEscalations: 0 },
        cases: [],
      }),
    });
  });

  await page.route('**/api/system-services/security-incidents*', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: '[]',
  }));
  await page.route('**/api/system-services/security-incident-assignments/mine', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: '[]',
  }));

  await page.goto('/login');
  console.log('[SYSTEM LOGIN SURFACE]', JSON.stringify({ url: page.url(), bodyText: await page.locator('body').innerText() }));
  await page.getByLabel('Work email').fill('platform-responder@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill(systemTestPassword);
  await page.getByRole('button', { name: 'Continue securely' }).click();
  expect(calls).toContain('global-login');
  console.log('[SYSTEM LOGIN AFTER SUBMIT]', JSON.stringify({
    url: page.url(),
    authStage: await page.locator('[data-testid="login-panel"]').getAttribute('data-auth-stage'),
    alert: await page.getByRole('alert').allTextContents(),
  }));
  await expect(page).toHaveURL(/\/mfa$/);
  await page.getByLabel('Six-digit code').fill('123456');
  await page.getByRole('button', { name: 'Verify identity' }).click();

  await expect(page.getByRole('heading', { name: 'System Services' })).toBeVisible();
  await expect.poll(() => page.evaluate(() => {
    const user = JSON.parse(localStorage.getItem('wilsy_sovereign_user') || 'null');
    return {
      principalId: user?.id,
      scope: user?.systemServicesWorkspace?.scope,
      authority: user?.systemServicesWorkspace?.authority,
      tenantId: localStorage.getItem('tenantId'),
      activeTenant: localStorage.getItem('wilsy_active_tenant'),
      bearer: localStorage.getItem('wilsy_auth_token'),
      refresh: localStorage.getItem('wilsy_refresh_token'),
    };
  })).toEqual({
    principalId: 'WILSYAUTH-browser-system-principal',
    scope: 'SYSTEM',
    authority: 'EOS_SYSTEM_SERVICES',
    tenantId: null,
    activeTenant: null,
    bearer: 'synthetic-system-access-token',
    refresh: 'sysrefresh-browser-token',
  });
  expect(calls.slice(0, 2)).toEqual(['global-login', 'global-mfa']);
  expect(calls.filter((value) => value === 'system-workspace').length).toBeGreaterThanOrEqual(1);
  await context.close();
});

// ARTIFACT: system-services-incident.browser.spec.js
// AUTHORITY BOUNDARY: real browser plus EOS-authenticated disposable test authority
// END OF WILSY OS SOVEREIGN ARTIFACT
