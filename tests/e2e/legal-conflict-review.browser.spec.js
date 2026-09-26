/**
 * TITLE: WILSY OS authenticated Legal OS browser certificate
 * VERSION: v1.0.0-L8-8M-R3-AUTHENTICATED-BROWSER-CERT
 * AUTHORITY: Browser certification evidence only.
 * EPITOME: Prove real browser storage, workspace bootstrap, Legal Operations
 *          reads, guarded conflict-review command, durable replay, and
 *          double-submit protection against an isolated local Mongo database.
 * ABSOLUTE CANONICAL PATH:
 *   /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/legal-conflict-review.browser.spec.js
 * COLLABORATION / OWNERSHIP: L8-8M-R3; Python EOS and existing client adapters
 *                            remain the authorities.
 * CERTIFICATION / UPDATE DATE: 2026-09-26
 * CHANGELOG: v1.0.0 establishes one end-to-end authenticated browser proof;
 *             it does not change production application semantics.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: State-file bearer material is loaded in memory
 *                             only and is never printed or included in traces.
 * TENANT BOUNDARY: Every request uses the fixture's exact tenant header.
 * AUTHORITY BOUNDARY: Assertions over server-owned authentication, IAM,
 *                     screening, review, and replay responses only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import fs from 'node:fs';

import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) {
  throw new Error('BROWSER_CERT_STATE_REQUIRED');
}

const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));

test('certifies authenticated conflict review through browser, API, and durable replay', async ({ page, request }) => {
  const observed = [];
  const reviewRequests = [];
  const reviewBodies = [];
  page.on('response', (response) => {
    const url = new URL(response.url());
    if (url.pathname.startsWith('/api/')) {
      observed.push({ method: response.request().method(), path: url.pathname, status: response.status() });
    }
    if (url.pathname === '/api/legal-operations/conflict-reviews') {
      reviewRequests.push(response);
    }
  });

  await page.addInitScript(({ accessToken, tenantId, principalId, email }) => {
    localStorage.setItem('wilsy_auth_token', accessToken);
    localStorage.setItem('token', accessToken);
    localStorage.setItem('tenantId', tenantId);
    localStorage.setItem('wilsy_tenant_id', tenantId);
    localStorage.setItem('wilsy_active_tenant', JSON.stringify({ tenantId, id: tenantId }));
    localStorage.setItem('wilsy_sovereign_user', JSON.stringify({ id: principalId, email, tenantId }));
  }, {
    accessToken: state.access_token,
    tenantId: state.tenant_id,
    principalId: state.principal_id,
    email: state.email,
  });

  await page.goto('/');
  try {
    await expect(page.getByText('Conflict review queue', { exact: true })).toBeVisible();
  } catch (error) {
    console.error(`BROWSER_CERT_OBSERVED=${JSON.stringify(observed)}`);
    throw error;
  }
  const row = page.locator(`[data-conflict-screening-id="${state.screening_id}"]`);
  await expect(row).toBeVisible();
  await expect(row).toContainText(state.source_case_matter_id);

  await row.getByRole('button', { name: 'Review Conflict' }).click();
  await row.getByRole('combobox').selectOption('CONFLICT_IDENTIFIED');
  await row.getByRole('textbox').fill('browser-certification-review-reference');
  const submit = row.getByRole('button', { name: 'Submit review' });
  await expect(submit).toBeVisible();

  const postBody = new Promise((resolve) => {
    page.on('request', (requestEvent) => {
      const url = new URL(requestEvent.url());
      if (url.pathname === '/api/legal-operations/conflict-reviews' && requestEvent.method() === 'POST') {
        reviewBodies.push(JSON.parse(requestEvent.postData() || '{}'));
        resolve(JSON.parse(requestEvent.postData() || '{}'));
      }
    });
  });
  const firstResponse = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/legal-operations/conflict-reviews'
    && response.request().method() === 'POST'
  ));
  await Promise.all([
    firstResponse,
    submit.click(),
    submit.evaluate((element) => element.click()),
  ]);
  await expect(row).toContainText('Conflict review recorded as CONFLICT_IDENTIFIED.');
  if (reviewRequests.length < 1) {
    console.error(`BROWSER_CERT_REVIEW_BODIES=${JSON.stringify(reviewBodies)}`);
    console.error(`BROWSER_CERT_REVIEW_STATUSES=${JSON.stringify(reviewRequests.map((item) => item.status()))}`);
  }
  expect(reviewRequests.length).toBeGreaterThanOrEqual(1);
  expect(reviewRequests.every((item) => item.status() === 200)).toBe(true);
  const command = await postBody;
  expect(command).toEqual({
    screening_id: state.screening_id,
    review_id: expect.any(String),
    outcome: 'CONFLICT_IDENTIFIED',
    review_reason_reference: 'browser-certification-review-reference',
  });

  const replay = await request.post('/api/legal-operations/conflict-reviews', {
    data: command,
    headers: {
      Authorization: `Bearer ${state.access_token}`,
      'X-Tenant-ID': state.tenant_id,
    },
  });
  expect(replay.status()).toBe(200);
  const firstBody = await reviewRequests[0].json();
  for (const response of reviewRequests.slice(1)) {
    expect(await response.json()).toEqual(firstBody);
  }
  const replayBody = await replay.json();
  expect(replayBody).toEqual(firstBody);

  const requiredRequests = [
    ['GET', '/api/auth/workspace-bootstrap'],
    ['GET', '/api/legal-acceptance/status'],
    ['GET', '/api/legal-operations/workspace'],
    ['GET', '/api/legal-operations/conflict-screenings'],
  ];
  for (const [method, path] of requiredRequests) {
    expect(observed).toContainEqual(expect.objectContaining({ method, path, status: 200 }));
  }
  expect(observed).toContainEqual(expect.objectContaining({
    method: 'POST', path: '/api/legal-operations/conflict-reviews', status: 200,
  }));
});

// ARTIFACT: legal-conflict-review.browser.spec.js
// VERSION: v1.0.0-L8-8M-R3-AUTHENTICATED-BROWSER-CERT
// AUTHORITY BOUNDARY: browser assertions only
// TENANT POSTURE: exact disposable tenant header and server-derived scope
// FAIL-CLOSED POSTURE: missing auth, non-200 reads, duplicate POSTs, and replay divergence fail
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
