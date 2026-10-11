/**
 * TITLE: WILSY OS authenticated Legal Matter Deadline browser certificate
 * VERSION: v1.0.0-D6B-AUTHENTICATED-DEADLINE-BROWSER-CERT
 * AUTHORITY: Browser certification evidence only.
 * EPITOME: Prove the real authenticated client, EOS HTTP, durable IAM, Mongo
 *          deadline command/read path, canonical refresh, and independent D6
 *          Core Legal intelligence projection across the frozen role envelope.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/legal-matter-deadline.browser.spec.js
 * COLLABORATION / OWNERSHIP: D1-D6B remain canonical; this artifact observes
 *                            disposable runtime behavior without mocking HTTP.
 * CERTIFICATION / UPDATE DATE: 2026-10-11
 * CHANGELOG: 2026-10-11 v1.0.0 certifies Partner create/refresh/intelligence,
 *            Attorney and Paralegal read/write presentation, Secretary read-only
 *            intelligence, Legal Finance denial, and browser-body narrowing.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: UUID-isolated synthetic evidence only; tokens stay
 *                             in process memory and are never printed.
 * TENANT BOUNDARY: Every request is bound to the fixture tenant and durable IAM.
 * AUTHORITY BOUNDARY: Runtime assertions only; no legal/advisory/AI command truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED DECLARATION: Missing sessions, UI affordances, live requests,
 *                          canonical refresh, bounded bodies, or denials fail.
 */

import fs from 'node:fs';

import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const baseURL = process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174';

async function openAuthenticatedLegalWorkspace(browser, actorKey) {
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
  const workspaceBootstrap = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/auth/workspace-bootstrap'
    && response.request().method() === 'GET'
  ));
  await page.goto('/');
  expect((await workspaceBootstrap).status()).toBe(200);
  await expect(page.getByRole('button', { name: 'Deadlines', exact: true }).first()).toBeVisible();
  return { actor, context, page };
}

test('certifies Partner live create, canonical refresh, bounded body, and Core Legal intelligence', async ({ browser, request }) => {
  const { actor, context, page } = await openAuthenticatedLegalWorkspace(browser, 'partner');
  const observed = [];
  page.on('response', (response) => {
    const url = new URL(response.url());
    if (url.pathname.includes('/deadlines') || url.pathname.includes('/deadline-intelligence')) {
      observed.push({
        method: response.request().method(),
        path: url.pathname,
        status: response.status(),
      });
    }
  });

  const initialList = page.waitForResponse((response) => (
    new URL(response.url()).pathname === `/api/legal-operations/matters/${state.matter_id}/deadlines`
    && response.request().method() === 'GET'
  ));
  await page.getByRole('button', { name: 'Deadlines', exact: true }).first().click();
  expect((await initialList).status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Matter deadlines', exact: true })).toBeVisible();
  await expect(page.getByLabel('Create matter deadline')).toBeVisible();

  const title = `Synthetic browser deadline ${Date.now()}`;
  await page.getByLabel('Deadline title').fill(title);
  await page.getByLabel('Deadline due at').fill('2030-01-15T10:00');
  await page.getByLabel('Deadline source reference').fill('browser-cert:synthetic-court-order');
  await page.getByLabel('Deadline source evidence fingerprint').fill('a'.repeat(128));
  await page.getByLabel('Deadline jurisdiction reference').fill('browser-cert:za-high-court');

  const postRequest = page.waitForRequest((requestEvent) => (
    new URL(requestEvent.url()).pathname === `/api/legal-operations/matters/${state.matter_id}/deadlines`
    && requestEvent.method() === 'POST'
  ));
  const postResponse = page.waitForResponse((response) => (
    new URL(response.url()).pathname === `/api/legal-operations/matters/${state.matter_id}/deadlines`
    && response.request().method() === 'POST'
  ));
  await page.getByRole('button', { name: 'Record deadline', exact: true }).click();
  const actualRequest = await postRequest;
  const command = actualRequest.postDataJSON();
  expect(Object.keys(command).sort()).toEqual([
    'created_at',
    'deadline_id',
    'deadline_kind',
    'due_at',
    'jurisdiction_reference',
    'source_evidence_fingerprint',
    'source_reference',
    'source_type',
    'supersedes_deadline_id',
    'title',
  ]);
  for (const forbidden of [
    'tenant_id', 'principal_id', 'role', 'permissions', 'status', 'overdue',
    'ai_confidence', 'payment_state', 'settlement_state',
  ]) {
    expect(command).not.toHaveProperty(forbidden);
  }
  expect((await postResponse).status()).toBe(200);
  await expect(page.getByRole('status')).toContainText('canonical refresh confirmed');
  await expect(page.getByText(title, { exact: true })).toBeVisible();

  const postIndex = observed.findIndex((item) => item.method === 'POST');
  const refreshIndex = observed.findIndex((item, index) => (
    index > postIndex && item.method === 'GET' && item.path.endsWith('/deadlines')
  ));
  expect(postIndex).toBeGreaterThanOrEqual(0);
  expect(refreshIndex).toBeGreaterThan(postIndex);

  await page.getByTitle('Open Wilsy OS Intelligence Dock').click();
  await page.getByRole('button', { name: 'Deadlines', exact: true }).last().click();
  await page.getByLabel('Matter identifier for deadline observation').fill(state.matter_id);
  const intelligenceResponse = page.waitForResponse((response) => (
    new URL(response.url()).pathname === `/api/legal-operations/matters/${state.matter_id}/deadline-intelligence`
    && response.request().method() === 'GET'
  ));
  await page.getByRole('button', { name: 'Observe deadline posture', exact: true }).click();
  expect((await intelligenceResponse).status()).toBe(200);
  await expect(page.getByLabel('Matter deadline observation')).toBeVisible();
  await expect(page.getByText('READ ONLY', { exact: true })).toBeVisible();
  await expect(page.getByText(/Not legal advice or a recommendation/i)).toBeVisible();
  await expect(page.getByText(/No legal-period calculation/i)).toBeVisible();
  await expect(page.getByText(/FILING · due 2030-01-15/i)).toBeVisible();

  const invalid = await request.post(
    `/api/legal-operations/matters/${state.matter_id}/deadlines`,
    {
      headers: {
        Authorization: `Bearer ${actor.access_token}`,
        'X-Tenant-ID': state.tenant_id,
      },
      data: { ...command, source_evidence_fingerprint: 'invalid' },
    },
  );
  expect(invalid.status()).toBe(422);
  await context.close();
});

for (const actorKey of ['attorney', 'paralegal']) {
  test(`certifies ${actorKey} deadline read and create presentation`, async ({ browser }) => {
    const { context, page } = await openAuthenticatedLegalWorkspace(browser, actorKey);
    const listResponse = page.waitForResponse((response) => (
      new URL(response.url()).pathname === `/api/legal-operations/matters/${state.matter_id}/deadlines`
      && response.request().method() === 'GET'
    ));
    await page.getByRole('button', { name: 'Deadlines', exact: true }).first().click();
    expect((await listResponse).status()).toBe(200);
    await expect(page.getByRole('heading', { name: 'Matter deadlines', exact: true })).toBeVisible();
    await expect(page.getByLabel('Create matter deadline')).toBeVisible();
    await context.close();
  });
}

test('certifies Secretary read-only deadlines and independent intelligence', async ({ browser }) => {
  const { context, page } = await openAuthenticatedLegalWorkspace(browser, 'secretary');
  const listResponse = page.waitForResponse((response) => (
    new URL(response.url()).pathname === `/api/legal-operations/matters/${state.matter_id}/deadlines`
    && response.request().method() === 'GET'
  ));
  await page.getByRole('button', { name: 'Deadlines', exact: true }).first().click();
  expect((await listResponse).status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Matter deadlines', exact: true })).toBeVisible();
  await expect(page.getByLabel('Create matter deadline')).toHaveCount(0);

  await page.getByTitle('Open Wilsy OS Intelligence Dock').click();
  await page.getByRole('button', { name: 'Deadlines', exact: true }).last().click();
  await page.getByLabel('Matter identifier for deadline observation').fill(state.matter_id);
  const intelligenceResponse = page.waitForResponse((response) => (
    new URL(response.url()).pathname === `/api/legal-operations/matters/${state.matter_id}/deadline-intelligence`
    && response.request().method() === 'GET'
  ));
  await page.getByRole('button', { name: 'Observe deadline posture', exact: true }).click();
  expect((await intelligenceResponse).status()).toBe(200);
  await expect(page.getByLabel('Matter deadline observation')).toBeVisible();
  await context.close();
});

test('certifies Legal Finance write denial from durable IAM', async ({ request }) => {
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
// VERSION: v1.0.0-D6B-AUTHENTICATED-DEADLINE-BROWSER-CERT
// AUTHORITY BOUNDARY: authenticated real-browser assertions only
// TENANT POSTURE: exact disposable tenant and durable IAM sessions
// FAIL-CLOSED POSTURE: missing live evidence, authority narrowing, or canonical refresh fails
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
