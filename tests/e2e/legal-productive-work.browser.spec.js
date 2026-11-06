/**
 * TITLE: WILSY OS authenticated Legal productive-work browser certificate
 * VERSION: v1.2.0-R67-DAILY-QUEUE-AND-OWNER-COMMERCIAL-CERT
 * AUTHORITY: Browser certification evidence only.
 * EPITOME: Prove the Tenant Owner commercial-only Legal entry, authenticated operator
 *          workspace bootstrap, R67 daily-work response adaptation, own-principal scope,
 *          specialist workflow projection, and responsive rendering without browser authority.
 * TENANT BOUNDARY: Exact disposable fixture tenant only.
 * AUTHORITY BOUNDARY: Browser observation only; server IAM remains authoritative.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED DECLARATION: Missing authentication, request, authorization,
 *                          productive-work rendering, scope narrowing, responsive
 *                          presentation, or bounded denial fails certification.
 */

import fs from 'node:fs';

import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) {
  throw new Error('BROWSER_CERT_STATE_REQUIRED');
}

const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const baseURL = process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174';

async function openAuthenticatedLegalWorkspace(
  browser,
  actorKey,
  viewport = { width: 1440, height: 1000 },
) {
  const actor = state.actors?.[actorKey];

  if (!actor) {
    throw new Error(`PW_P11C_BROWSER_ACTOR_MISSING:${actorKey}`);
  }

  const context = await browser.newContext({
    baseURL,
    viewport,
  });

  const page = await context.newPage();
  const observedRequests = [];
  page.on('request', (request) => {
    observedRequests.push(new URL(request.url()).pathname);
  });

  await page.addInitScript(
    ({ accessToken, tenantId, principalId, email }) => {
      localStorage.setItem('wilsy_auth_token', accessToken);
      localStorage.setItem('token', accessToken);
      localStorage.setItem('tenantId', tenantId);
      localStorage.setItem('wilsy_tenant_id', tenantId);
      localStorage.setItem(
        'wilsy_active_tenant',
        JSON.stringify({
          tenantId,
          id: tenantId,
        }),
      );
      localStorage.setItem(
        'wilsy_sovereign_user',
        JSON.stringify({
          id: principalId,
          email,
          tenantId,
        }),
      );
    },
    {
      accessToken: actor.access_token,
      tenantId: state.tenant_id,
      principalId: actor.principal_id,
      email: actor.email,
    },
  );

  const bootstrap = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/auth/workspace-bootstrap'
    && response.request().method() === 'GET'
  ));

  await page.goto('/');

  const bootstrapResponse = await bootstrap;
  expect(bootstrapResponse.status()).toBe(200);
  const bootstrapPayload = await bootstrapResponse.json();

  return {
    actor,
    context,
    page,
    observedRequests,
    bootstrapPayload,
  };
}

async function openProductiveWork(page) {
  await expect(
    page.getByRole('button', {
      name: 'My Work',
      exact: true,
    }).first(),
  ).toBeVisible();

  const productiveRequest = page.waitForRequest((request) => (
    new URL(request.url()).pathname === '/api/legal-operations/productive-work'
    && request.method() === 'GET'
  ));

  const productiveResponse = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/legal-operations/productive-work'
    && response.request().method() === 'GET'
  ));

  await page.getByRole('button', {
    name: 'My Work',
    exact: true,
  }).first().click();

  const request = await productiveRequest;
  const response = await productiveResponse;

  return {
    request,
    response,
  };
}

test(
  'certifies Tenant Owner Legal commercial workspace without practice access',
  async ({ browser }) => {
    const {
      context,
      page,
      observedRequests,
      bootstrapPayload,
    } = await openAuthenticatedLegalWorkspace(browser, 'tenant_owner');

    expect(bootstrapPayload.workspace?.businessRole).toBe('TENANT_OWNER');
    await expect(page.getByRole('button', { name: 'LEGAL OS', exact: true })).toBeVisible();

    const commercialResponsePromise = page.waitForResponse((response) => (
      new URL(response.url()).pathname === '/api/legal-operations/commercial-context'
      && response.request().method() === 'GET'
    ));
    await page.getByRole('button', { name: 'LEGAL OS', exact: true }).click();

    const commercialResponse = await commercialResponsePromise;
    expect(commercialResponse.status()).toBe(200);
    const payload = await commercialResponse.json();
    expect(payload).toMatchObject({
      tenant_id: state.tenant_id,
      visibility: 'LEGAL_COMMERCIAL_CONTEXT_SUBSCRIPTION_READ',
      product: {
        product_id: 'LEGAL_OPERATIONS',
        available: true,
        access_basis: 'LEGAL_PLAN_FEATURE',
      },
      subscription: { status: 'active' },
    });

    await expect(
      page.getByRole('heading', { name: 'Legal Product Command' }),
    ).toBeVisible();
    await expect(page.getByText('Tenant owner · commercial authority only')).toBeVisible();
    await expect(page.getByText('ROLE-GATED')).toBeVisible();

    expect(observedRequests).not.toContain('/api/legal-operations/workspace');
    expect(observedRequests).not.toContain('/api/legal-operations/productive-work');
    expect(observedRequests).not.toContain('/api/legal-operations/conflict-screenings');

    await page.reload();
    await expect(
      page.getByRole('heading', { name: 'Legal Product Command' }),
    ).toBeVisible();
    await expect(page.getByText('ROLE-GATED')).toBeVisible();
    expect(observedRequests).not.toContain('/api/legal-operations/workspace');
    expect(observedRequests).not.toContain('/api/legal-operations/productive-work');
    expect(observedRequests).not.toContain('/api/legal-operations/conflict-screenings');

    await context.close();
  },
);

test(
  'certifies Partner authenticated own-principal productive work on the canonical Legal dashboard',
  async ({ browser }) => {
    const {
      actor,
      context,
      page,
    } = await openAuthenticatedLegalWorkspace(browser, 'partner');

    const observed = [];

    page.on('request', (request) => {
      const path = new URL(request.url()).pathname;

      if (path === '/api/legal-operations/productive-work') {
        observed.push({
          method: request.method(),
          path,
          postData: request.postData(),
        });
      }
    });

    const { request, response } = await openProductiveWork(page);

    expect(response.status()).toBe(200);
    expect(request.method()).toBe('GET');
    expect(request.postData()).toBeNull();

    const url = new URL(request.url());

    expect(url.pathname).toBe('/api/legal-operations/productive-work');
    expect(url.search).toBe('');

    expect(observed).toEqual([
      {
        method: 'GET',
        path: '/api/legal-operations/productive-work',
        postData: null,
      },
    ]);

    const payload = await response.json();

    expect(payload).toMatchObject({
      tenant_id: state.tenant_id,
      principal_id: actor.principal_id,
    });

    expect(payload.principal_id).toBe(actor.principal_id);

    await expect(
      page.locator('[data-legal-productive-work="true"]'),
    ).toBeVisible();

    await context.close();
  },
);

for (const actorKey of ['attorney', 'paralegal', 'secretary']) {
  test(
    `certifies ${actorKey} authenticated productive-work projection`,
    async ({ browser }) => {
      const {
        actor,
        context,
        page,
      } = await openAuthenticatedLegalWorkspace(browser, actorKey);

      const { request, response } = await openProductiveWork(page);

      expect(request.method()).toBe('GET');
      expect(new URL(request.url()).search).toBe('');
      expect(response.status()).toBe(200);

      const payload = await response.json();

      expect(payload.tenant_id).toBe(state.tenant_id);
      expect(payload.principal_id).toBe(actor.principal_id);

      await expect(
        page.locator('[data-legal-productive-work="true"]'),
      ).toBeVisible();

      await context.close();
    },
  );
}

test(
  'certifies productive-work narrow viewport without horizontal document overflow',
  async ({ browser }) => {
    const {
      actor,
      context,
      page,
    } = await openAuthenticatedLegalWorkspace(
      browser,
      'attorney',
      {
        width: 390,
        height: 844,
      },
    );

    const { response } = await openProductiveWork(page);

    expect(response.status()).toBe(200);

    const payload = await response.json();

    expect(payload.tenant_id).toBe(state.tenant_id);
    expect(payload.principal_id).toBe(actor.principal_id);

    const productiveWork = page.locator(
      '[data-legal-productive-work="true"]',
    );

    await expect(productiveWork).toBeVisible();

    const metrics = await page.evaluate(() => ({
      viewportWidth: window.innerWidth,
      documentScrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
    }));

    expect(metrics.viewportWidth).toBe(390);
    expect(metrics.documentScrollWidth).toBeLessThanOrEqual(
      metrics.viewportWidth + 1,
    );
    expect(metrics.bodyScrollWidth).toBeLessThanOrEqual(
      metrics.viewportWidth + 1,
    );

    await context.close();
  },
);

// ARTIFACT: legal-productive-work.browser.spec.js
// VERSION: v1.0.0-PW-P11C-AUTHENTICATED-PRODUCTIVE-WORK-BROWSER-CERT
// AUTHORITY BOUNDARY: authenticated real-browser assertions only
// TENANT POSTURE: exact disposable tenant and durable IAM actor
// FAIL-CLOSED POSTURE: missing live evidence or scope narrowing fails
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
