/**
 * TITLE: WILSY OS Legal Practice daily-operations browser certificate
 * VERSION: v1.0.0-LEGAL-OPS-DAILY-OPERATIONS-PARITY-CERT
 * AUTHORITY: Authenticated browser/runtime certification evidence only.
 * EPITOME: Proves all four Practice personas enter Legal OS, read their own
 *          productive work, receive exact conflict-review presentation, and
 *          exercise the certified deadline envelope through live Python EOS.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/legal-practice-daily-operations.browser.spec.js
 * COLLABORATION / OWNERSHIP: Python EOS owns IAM and durable truth; this file
 *                            observes transport, presentation and readback only.
 * CERTIFICATION / UPDATE DATE: 2026-10-16
 * CHANGELOG: 2026-10-16 v1.0.0 certifies Partner, Attorney, Paralegal and
 *            Secretary in one coherent live-EOS daily-operations journey.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Disposable synthetic identities only; bearer
 *                             material remains process-local and unprinted.
 * TENANT BOUNDARY: Exact fixture tenant and server-derived principal only.
 * AUTHORITY BOUNDARY: Browser controls only narrow server policy; direct
 *                     requests remain independently authorized by Python EOS.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED DECLARATION: Missing entry, canonical transport, durable
 *                          readback, role narrowing, denial or mobile sanity
 *                          fails this certificate.
 */

import fs from 'node:fs';

import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const baseURL = process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174';

const WRITE_PERSONAS = Object.freeze(['partner', 'attorney', 'paralegal']);
const ALL_PERSONAS = Object.freeze([...WRITE_PERSONAS, 'secretary']);

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
    localStorage.setItem('wilsy_sovereign_user', JSON.stringify({
      id: principalId,
      email,
      tenantId,
    }));
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
  await page.goto('/');
  expect((await bootstrap).status()).toBe(200);
  await expect(page.getByText('Legal Operations Command Center', { exact: true })).toBeVisible();
  return { actor, context, page };
}

async function openProductiveWork(page, actor) {
  const responsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/legal-operations/productive-work'
    && response.request().method() === 'GET'
  ));
  await page.getByRole('button', { name: 'My Work', exact: true }).first().click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  const payload = await response.json();
  expect(payload.tenant_id).toBe(state.tenant_id);
  expect(payload.principal_id).toBe(actor.principal_id);
  await expect(page.locator('[data-legal-productive-work="true"]')).toBeVisible();
}

async function openDeadlines(page) {
  const responsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname
      === `/api/legal-operations/matters/${state.matter_id}/deadlines`
    && response.request().method() === 'GET'
  ));
  await page.getByRole('button', { name: 'Deadlines', exact: true }).first().click();
  expect((await responsePromise).status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Matter deadlines', exact: true })).toBeVisible();
}

async function createDeadline(page, actorKey) {
  const title = `Daily operations ${actorKey} ${Date.now()}`;
  await page.getByLabel('Deadline title').fill(title);
  await page.getByLabel('Deadline due at').fill('2031-03-20T09:30');
  await page.getByLabel('Deadline source reference').fill(`daily-cert:${actorKey}`);
  await page.getByLabel('Deadline source evidence fingerprint').fill('a'.repeat(128));
  await page.getByLabel('Deadline jurisdiction reference').fill('daily-cert:za-high-court');
  const post = page.waitForResponse((response) => (
    new URL(response.url()).pathname
      === `/api/legal-operations/matters/${state.matter_id}/deadlines`
    && response.request().method() === 'POST'
  ));
  await page.getByRole('button', { name: 'Record deadline', exact: true }).click();
  expect((await post).status()).toBe(200);
  await expect(page.getByRole('status')).toContainText('canonical refresh confirmed');
  await expect(page.getByText(title, { exact: true })).toBeVisible();
}

for (const actorKey of ALL_PERSONAS) {
  test(`certifies ${actorKey} daily-work entry, exact controls and backend authority`, async ({ browser, request }) => {
    const { actor, context, page } = await openPersona(
      browser,
      actorKey,
      actorKey === 'secretary' ? { width: 390, height: 844 } : undefined,
    );
    const observedPaths = [];
    page.on('request', (requestEvent) => {
      observedPaths.push(new URL(requestEvent.url()).pathname);
    });

    await openProductiveWork(page, actor);
    await page.getByRole('button', { name: 'Command Center', exact: true }).first().click();

    if (['partner', 'attorney'].includes(actorKey)) {
      await expect(page.getByRole('button', { name: 'Review Conflict' })).toBeVisible();
    } else {
      await expect(page.getByRole('button', { name: 'Review Conflict' })).toHaveCount(0);
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

    await openDeadlines(page);
    if (WRITE_PERSONAS.includes(actorKey)) {
      await expect(page.getByLabel('Create matter deadline')).toBeVisible();
      await createDeadline(page, actorKey);
    } else {
      await expect(page.getByLabel('Create matter deadline')).toHaveCount(0);
      const deniedDeadline = await request.post(
        `/api/legal-operations/matters/${state.matter_id}/deadlines`,
        {
          headers: {
            Authorization: `Bearer ${actor.access_token}`,
            'X-Tenant-ID': state.tenant_id,
          },
          data: {
            deadline_id: `daily-denied-${Date.now()}`,
            deadline_kind: 'FILING',
            title: 'Denied Secretary deadline',
            due_at: '2031-03-20T09:30:00Z',
            source_type: 'COURT_ORDER',
            source_reference: 'daily-cert:denied',
            source_evidence_fingerprint: 'd'.repeat(128),
            jurisdiction_reference: 'daily-cert:za-high-court',
            created_at: new Date().toISOString(),
            supersedes_deadline_id: null,
          },
        },
      );
      expect(deniedDeadline.status()).toBe(403);
    }

    expect(observedPaths.some((path) => path.startsWith('/legal/'))).toBe(false);
    expect(observedPaths).toContain('/api/legal-operations/productive-work');
    if (actorKey === 'secretary') {
      const width = await page.evaluate(() => ({
        viewport: window.innerWidth,
        document: document.documentElement.scrollWidth,
      }));
      expect(width.document).toBeLessThanOrEqual(width.viewport + 1);
    }
    await context.close();
  });
}

// ARTIFACT: legal-practice-daily-operations.browser.spec.js
// VERSION: v1.0.0-LEGAL-OPS-DAILY-OPERATIONS-PARITY-CERT
// AUTHORITY BOUNDARY: live browser observation only; Python EOS authorizes every request
// TENANT POSTURE: exact disposable tenant and authenticated principal projection
// FAIL-CLOSED POSTURE: missing controls, denial, durable readback or canonical transport fails
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
