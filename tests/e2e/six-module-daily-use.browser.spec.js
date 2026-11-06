/**
 * TITLE: WILSY OS authenticated seven-module daily-use browser certificate
 * AUTHORITY: Disposable authenticated browser evidence only.
 * EPITOME: Prove all six server-entitled module destinations, CRM/Operations/
 *          Intelligence task lifecycle, refresh/re-entry, People and Billing
 *          work surfaces, Legal commercial boundary, and deny-only specialist
 *          access to owner Operations/Intelligence queues.
 * TENANT BOUNDARY: One UUID-isolated synthetic tenant and a foreign unjoined tenant.
 * AUTHORITY BOUNDARY: EOS authorizes every request; browser navigation is presentation only.
 */

import fs from 'node:fs';
import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));

const moduleIds = Object.freeze([
  'LEGAL_OS', 'BILLING', 'CRM', 'PEOPLE', 'OPERATIONS', 'INTELLIGENCE', 'POS',
]);

async function openAuthenticated(browser, actorKey, viewport = { width: 1440, height: 1000 }) {
  const actor = state.actors?.[actorKey];
  if (!actor) throw new Error(`SIX_MODULE_ACTOR_MISSING:${actorKey}`);
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const browserErrors = [];
  page.on('pageerror', error => browserErrors.push(error.message));
  page.on('console', message => {
    if (message.type() === 'error') browserErrors.push(message.text());
  });
  await page.addInitScript(({ accessToken, tenantId, principalId, email }) => {
    localStorage.setItem('wilsy_auth_token', accessToken);
    localStorage.setItem('token', accessToken);
    localStorage.setItem('tenantId', tenantId);
    localStorage.setItem('wilsy_tenant_id', tenantId);
    localStorage.setItem('wilsy_active_tenant', JSON.stringify({ tenantId, id: tenantId }));
    localStorage.setItem('wilsy_sovereign_user', JSON.stringify({ id: principalId, email, tenantId }));
  }, {
    accessToken: actor.access_token,
    tenantId: state.tenant_id,
    principalId: actor.principal_id,
    email: actor.email,
  });

  const bootstrapPromise = page.waitForResponse(response => (
    new URL(response.url()).pathname === '/api/auth/workspace-bootstrap'
    && response.request().method() === 'GET'
  ));
  await page.goto('/');
  const bootstrap = await bootstrapPromise;
  expect(bootstrap.status()).toBe(200);
  return { context, page, browserErrors };
}

async function openModuleNavigation(page) {
  // The shared product rail is intentionally collapsed on first render.
  // Open it explicitly; module navigation remains a server-issued projection.
  const openRail = page.getByRole('button', { name: 'Open workspace modules' });
  if (await openRail.isVisible()) await openRail.click();
  await expect(page.getByRole('navigation', { name: 'Available WILSY OS products' })).toBeVisible();
  await expect(page.locator('[data-wilsy-module-entry="LEGAL_OS"]')).toBeVisible();
  const manifestPromise = page.waitForResponse(response => (
    new URL(response.url()).pathname === '/api/auth/module-manifest'
    && response.request().method() === 'GET'
  ));
  await page.locator('[data-wilsy-module-entry="LEGAL_OS"]').click();
  const response = await manifestPromise;
  expect(response.status()).toBe(200);
  const payload = await response.json();
  expect(payload.workspace?.tenantId).toBe(state.tenant_id);
  const actual = payload.workspace?.modules?.map(module => module.moduleId) || [];
  for (const moduleId of moduleIds) expect(actual).toContain(moduleId);
  for (const label of ['Legal OS', 'Billing', 'CRM', 'People', 'Operations', 'Intelligence', 'Point of Sale']) {
    await expect(page.getByRole('button', { name: new RegExp(label, 'i') }).first()).toBeVisible();
  }
  return payload.workspace.modules;
}

async function authenticatedApi(page, path) {
  return page.evaluate(async ({ path, tenantId }) => {
    const response = await fetch(path, {
      method: 'GET',
      credentials: 'include',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('wilsy_auth_token') || localStorage.getItem('token') || ''}`,
        'X-Tenant-ID': tenantId,
      },
    });
    return { status: response.status, payload: await response.json().catch(() => ({})) };
  }, { path, tenantId: state.tenant_id });
}

async function switchModule(page, label, workspacePath, method = 'GET', expectedStatus = 200) {
  const responsePromise = page.waitForResponse(response => (
    new URL(response.url()).pathname.endsWith(workspacePath)
    && response.request().method() === method
  ));
  await page.getByRole('navigation', { name: 'Available WILSY OS products' })
    .getByRole('button', { name: label, exact: true }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(expectedStatus);
  return response;
}

async function createAndComplete(page, moduleId, title) {
  const path = `/api/tenant-modules/${moduleId.toLowerCase()}/workspace/work-items`;
  const createResponsePromise = page.waitForResponse(response => (
    new URL(response.url()).pathname === path
    && response.request().method() === 'POST'
  ));
  await page.getByLabel('Action title').fill(title);
  await page.getByRole('button', { name: 'Create action' }).click();
  const created = await createResponsePromise;
  expect(created.status()).toBe(201);
  const item = await created.json();
  await expect(page.getByText(title, { exact: true })).toBeVisible();

  const completePath = `${path}/${encodeURIComponent(item.work_item_id)}/complete`;
  const completeResponsePromise = page.waitForResponse(response => (
    new URL(response.url()).pathname === completePath
    && response.request().method() === 'POST'
  ));
  await page.getByRole('button', { name: 'Complete', exact: true }).click();
  const completed = await completeResponsePromise;
  expect(completed.status()).toBe(200);
  expect((await completed.json()).status).toBe('COMPLETED');
}

test('owner completes the authenticated seven-module daily-use journey', async ({ browser }) => {
  const { context, page, browserErrors } = await openAuthenticated(browser, 'tenant_owner');
  try {
    const modules = await openModuleNavigation(page);
    expect(modules).toHaveLength(7);

    // Legal is a commercial-only presentation for the Tenant Owner.
    await page.getByRole('button', { name: /Legal OS/i }).click();
    await expect(page.getByRole('heading', { name: 'Legal Product Command' })).toBeVisible();
    await expect(page.getByText('Tenant owner · commercial authority only')).toBeVisible();
    await expect(page.getByText('ROLE-GATED')).toBeVisible();

    // Billing remains its own invoice/dunning product surface.
    await page.getByRole('button', { name: /Billing/i }).click();
    await expect(page.getByRole('heading', { name: 'Billing command center' })).toBeVisible();

    // CRM retains its own durable owner task queue and command service.
    const crmQueue = await switchModule(page, 'CRM', '/api/crm/owner-workspace');
    expect(crmQueue.status()).toBe(200);
    await expect(page.getByRole('heading', { name: 'Owner operating workspace' })).toBeVisible();
    const crmTitle = `Browser CRM follow-up ${state.database_name}`;
    const crmCreatePromise = page.waitForResponse(response => (
      new URL(response.url()).pathname === '/api/crm/owner-workspace/work-items'
      && response.request().method() === 'POST'
    ));
    await page.getByLabel('What needs to happen?').fill(crmTitle);
    await page.getByRole('button', { name: 'Create action' }).click();
    expect((await crmCreatePromise).status()).toBe(201);
    await expect(page.getByText(crmTitle, { exact: true })).toBeVisible();
    const crmItem = page.getByRole('listitem').filter({ hasText: crmTitle });
    const crmCompletePromise = page.waitForResponse(response => (
      new URL(response.url()).pathname.includes('/api/crm/owner-workspace/work-items/')
      && new URL(response.url()).pathname.endsWith('/complete')
      && response.request().method() === 'POST'
    ));
    await crmItem.getByRole('button', { name: 'Complete' }).click();
    expect((await crmCompletePromise).status()).toBe(200);

    // People is the existing workforce/time-off workspace, not an alias for Operations.
    await page.getByRole('button', { name: /People/i }).click();
    await expect(page.getByRole('navigation', { name: 'HR workspace modules' })).toBeVisible();

    // Operations has its own product entitlement, task collection and permissions.
    const operationsQueue = await switchModule(
      page, 'Operations', '/api/tenant-modules/operations/workspace',
    );
    expect((await operationsQueue.json()).product_id).toBe('OPERATIONS');
    await expect(page.getByRole('heading', { name: 'Operations OS' })).toBeVisible();
    await createAndComplete(
      page, 'OPERATIONS', `Browser Operations action ${state.database_name}`,
    );

    // Intelligence has an independent entitlement and queue; it is not a read-only Operations alias.
    const intelligenceQueue = await switchModule(
      page, 'Intelligence', '/api/tenant-modules/intelligence/workspace',
    );
    expect((await intelligenceQueue.json()).product_id).toBe('INTELLIGENCE');
    await expect(page.getByRole('heading', { name: 'Intelligence OS' })).toBeVisible();
    await createAndComplete(
      page, 'INTELLIGENCE', `Browser Intelligence action ${state.database_name}`,
    );

    // Refresh and re-entry are fresh server reads, not local task resurrection.
    const refreshPromise = page.waitForResponse(response => (
      new URL(response.url()).pathname === '/api/tenant-modules/intelligence/workspace'
      && response.request().method() === 'GET'
    ));
    await page.getByRole('button', { name: 'Refresh EOS' }).click();
    expect((await refreshPromise).status()).toBe(200);
    await page.reload();
    await openModuleNavigation(page);
    const reentry = await switchModule(
      page, 'Intelligence', '/api/tenant-modules/intelligence/workspace',
    );
    expect(reentry.status()).toBe(200);
    await expect(page.getByRole('heading', { name: 'Intelligence OS' })).toBeVisible();
    expect(browserErrors).toEqual([]);
  } finally {
    await context.close();
  }
});

test('Legal specialist cannot use Owner Operations or Intelligence queues', async ({ browser }) => {
  const { context, page } = await openAuthenticated(browser, 'partner');
  try {
    const deniedOperations = await authenticatedApi(
      page, '/api/tenant-modules/operations/workspace',
    );
    expect(deniedOperations.status).toBe(403);
    expect(deniedOperations.payload.error_code).toBe('FORBIDDEN');
    expect(deniedOperations.payload.details).toEqual([]);

    const deniedIntelligence = await authenticatedApi(
      page, '/api/tenant-modules/intelligence/workspace',
    );
    expect(deniedIntelligence.status).toBe(403);
    expect(deniedIntelligence.payload.error_code).toBe('FORBIDDEN');
    expect(deniedIntelligence.payload.details).toEqual([]);

    // The Legal specialist's UI does not expose the Owner-only queue controls.
    await expect(page.getByText(/Browser Operations action/)).toHaveCount(0);
    await expect(page.getByText(/Browser Intelligence action/)).toHaveCount(0);
  } finally {
    await context.close();
  }
});

test('Operations and Intelligence workspaces remain usable at a narrow viewport', async ({ browser }) => {
  const { context, page } = await openAuthenticated(
    browser, 'tenant_owner', { width: 390, height: 844 },
  );
  try {
    await openModuleNavigation(page);
    await switchModule(page, 'Operations', '/api/tenant-modules/operations/workspace');
    await expect(page.getByRole('heading', { name: 'Operations OS' })).toBeVisible();
    await expect.poll(() => page.evaluate(() => (
      document.documentElement.scrollWidth <= window.innerWidth
    ))).toBe(true);
    await switchModule(page, 'Intelligence', '/api/tenant-modules/intelligence/workspace');
    await expect(page.getByRole('heading', { name: 'Intelligence OS' })).toBeVisible();
    await expect.poll(() => page.evaluate(() => (
      document.documentElement.scrollWidth <= window.innerWidth
    ))).toBe(true);
  } finally {
    await context.close();
  }
});
