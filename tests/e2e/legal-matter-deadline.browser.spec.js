/**
 * TITLE: WILSY OS G68-aware Legal Matter Deadline browser certificate
 * AUTHORITY: Authenticated browser/runtime certification evidence only.
 * EPITOME: Prove matter-dependent deadline navigation is not exposed while
 *          the independently enforced G68 practice workspace remains denied.
 *          Retain the direct Legal Finance IAM write/read denial proof.
 * TENANT BOUNDARY: Exact disposable fixture tenant and authenticated principals.
 * AUTHORITY BOUNDARY: No matter identity or deadline capability is inferred in the browser.
 */

import fs from 'node:fs';
import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const baseURL = process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174';

async function openAuthenticatedPractice(browser, actorKey) {
  const actor = state.actors?.[actorKey];
  if (!actor) throw new Error(`D6B_BROWSER_ACTOR_MISSING:${actorKey}`);
  const context = await browser.newContext({ baseURL });
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
  const observed = [];
  page.on('request', (request) => observed.push(new URL(request.url()).pathname));
  await page.goto('/');
  expect((await bootstrap).status()).toBe(200);
  expect((await workspace).status()).toBe(503);
  await expect(page.getByText(
    'LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE',
    { exact: true },
  )).toBeVisible();
  await expect(page.getByRole('button', { name: 'Deadlines', exact: true })).toHaveCount(0);
  expect(observed.some((path) => /\/api\/legal-operations\/matters\/.*\/deadlines$/.test(path))).toBe(false);
  return { actor, context, page };
}

for (const actorKey of ['partner', 'attorney', 'paralegal', 'secretary']) {
  test(`keeps ${actorKey} matter deadlines behind the G68 workspace boundary`, async ({ browser }) => {
    const { context, page } = await openAuthenticatedPractice(browser, actorKey);
    await expect(page.getByText('Legal Operations Command Center', { exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'My Work', exact: true })).toBeVisible();
    await context.close();
  });
}

test('certifies Legal Finance write and read denial from durable IAM', async ({ request }) => {
  const actor = state.actors.finance;
  const headers = {
    Authorization: `Bearer ${actor.access_token}`,
    'X-Tenant-ID': state.tenant_id,
  };
  const deniedWrite = await request.post(
    `/api/legal-operations/matters/${state.matter_id}/deadlines`,
    {
      headers,
      data: {
        deadline_id: `denied-${Date.now()}`,
        deadline_kind: 'FILING',
        title: 'Denied synthetic deadline',
        due_at: '2030-01-15T10:00:00Z',
        source_type: 'COURT_ORDER',
        source_reference: 'browser-cert:denied',
        source_evidence_fingerprint: 'd'.repeat(128),
        jurisdiction_reference: 'browser-cert:za-high-court',
        created_at: new Date().toISOString(),
        supersedes_deadline_id: null,
      },
    },
  );
  expect(deniedWrite.status()).toBe(403);
  const deniedRead = await request.get(
    `/api/legal-operations/matters/${state.matter_id}/deadlines`,
    { headers },
  );
  expect(deniedRead.status()).toBe(403);
});

// ARTIFACT: legal-matter-deadline.browser.spec.js
// AUTHORITY BOUNDARY: G68 controls matter workspace; deadline routes retain independent IAM
// FAIL-CLOSED POSTURE: no matter-derived deadline UI without authorized workspace context
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
