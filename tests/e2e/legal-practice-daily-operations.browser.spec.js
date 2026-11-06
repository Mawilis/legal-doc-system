/**
 * TITLE: WILSY OS Legal Practice operation-specific browser certificate
 * AUTHORITY: Authenticated browser/runtime certification evidence only.
 * EPITOME: Prove G68 workspace denial remains intact while independently
 *          authorized productive-work and conflict-review projections remain
 *          available under their own server-owned permission boundaries.
 * TENANT BOUNDARY: Exact disposable fixture tenant and authenticated principal.
 * AUTHORITY BOUNDARY: Browser presentation never grants authority; EOS authorizes every request.
 */

import fs from 'node:fs';
import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const baseURL = process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174';
const ALL_PERSONAS = Object.freeze(['partner', 'attorney', 'paralegal', 'secretary']);

async function openPersona(browser, actorKey, viewport = { width: 1440, height: 1000 }) {
  const actor = state.actors?.[actorKey];
  if (!actor) throw new Error(`DAILY_OPERATIONS_ACTOR_MISSING:${actorKey}`);
  const context = await browser.newContext({ baseURL, viewport });
  const page = await context.newPage();
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
  const bootstrap = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/auth/workspace-bootstrap'
    && response.request().method() === 'GET'
  ));
  const workspace = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/legal-operations/workspace'
    && response.request().method() === 'GET'
  ));
  await page.goto('/');
  expect((await bootstrap).status()).toBe(200);
  expect((await workspace).status()).toBe(503);
  await expect(page.getByText(
    'LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE',
    { exact: true },
  )).toBeVisible();
  await expect(page.getByText('Legal Operations Command Center', { exact: true })).toBeVisible();
  return { actor, context, page };
}

async function openProductiveWork(page, actor) {
  const responsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/legal-operations/productive-work'
    && response.request().method() === 'GET'
  ));
  await page.getByRole('button', { name: 'My Work', exact: true }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  const payload = await response.json();
  expect(payload.tenant_id).toBe(state.tenant_id);
  expect(payload.principal_id).toBe(actor.principal_id);
  await expect(page.locator('[data-legal-productive-work="true"]')).toBeVisible();
}

for (const actorKey of ALL_PERSONAS) {
  test(`certifies ${actorKey} operation-specific access under G68 workspace denial`, async ({ browser, request }) => {
    const { actor, context, page } = await openPersona(
      browser,
      actorKey,
      actorKey === 'secretary' ? { width: 390, height: 844 } : undefined,
    );
    const observedPaths = [];
    page.on('request', (requestEvent) => observedPaths.push(new URL(requestEvent.url()).pathname));

    await openProductiveWork(page, actor);

    const canReview = ['partner', 'attorney'].includes(actorKey);
    const conflictReviewNavigation = page.getByRole('button', {
      name: 'Conflict Reviews',
      exact: true,
    });
    if (canReview) {
      await expect(conflictReviewNavigation).toBeVisible();
      await conflictReviewNavigation.click();
      await expect(page.getByRole('button', { name: 'Review Conflict' })).toBeVisible();
    } else {
      await expect(conflictReviewNavigation).toHaveCount(0);
      const deniedReview = await request.post('/api/legal-operations/conflict-reviews', {
        headers: {
          Authorization: `Bearer ${actor.access_token}`,
          'X-Tenant-ID': state.tenant_id,
        },
        data: {
          screening_id: state.screening_id,
          review_id: `daily-denied-${actorKey}-${Date.now()}`,
          outcome: 'ESCALATION_REQUIRED',
          review_reason_reference: 'daily-cert:denied-role',
        },
      });
      expect(deniedReview.status()).toBe(403);
    }

    // Deadlines and matter-dependent controls stay hidden until the G68
    // workspace authority exists; no client-side matter list is synthesized.
    await expect(page.getByRole('button', { name: 'Deadlines', exact: true })).toHaveCount(0);
    expect(observedPaths).toContain('/api/legal-operations/productive-work');
    // openPersona already proves the G68 workspace request returned 503 and
    // rendered the deny state before this post-navigation observer was attached.
    expect(observedPaths.some((path) => /\/api\/legal-operations\/matters\/.*\/deadlines$/.test(path))).toBe(false);

    if (actorKey === 'secretary') {
      const width = await page.evaluate(() => ({
        viewport: window.innerWidth,
        document: document.documentElement.scrollWidth,
        body: document.body.scrollWidth,
      }));
      expect(width.viewport).toBe(390);
      expect(width.document).toBeLessThanOrEqual(width.viewport + 1);
      expect(width.body).toBeLessThanOrEqual(width.viewport + 1);
    }
    await context.close();
  });
}

// ARTIFACT: legal-practice-daily-operations.browser.spec.js
// AUTHORITY BOUNDARY: operation-specific server authorization; G68 remains deny-only
// TENANT POSTURE: exact disposable tenant and authenticated principal projection
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
