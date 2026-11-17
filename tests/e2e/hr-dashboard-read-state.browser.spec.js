/**
 * TITLE: WILSY OS authenticated HR dashboard read-state browser certificate
 * VERSION: v1.2.0-SINGLE-NAVIGATION-AUTH-CERT
 * AUTHORITY: Disposable browser certification only; EOS remains authorization authority.
 * EPITOME: Exercises the mounted Headquarters HR dashboard against a disposable EOS
 *          tenant whose Owner is intentionally denied workforce-directory capability.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/hr-dashboard-read-state.browser.spec.js
 * COLLABORATION / OWNERSHIP: HR dashboard consumer and L8-8M browser certification maintainers.
 * CERTIFICATION / UPDATE DATE: 2026-11-12
 * CHANGELOG:
 *   v1.2.0-SINGLE-NAVIGATION-AUTH-CERT — Opens the target Headquarters route once after installing session state and observers, avoiding duplicate bootstrap work while preserving source status and UI assertions.
 *   v1.1.0-HR-MALFORMED-UNAVAILABLE — Verifies incomplete workforce pages render unavailable with retry and never claim an empty employee ledger.
 *   v1.0.0-HR-DENIAL-DESKTOP-MOBILE — Verifies source-owned 403 presentation, suppresses false empty-employee claims, and checks desktop and 390px layout in a disposable fixture.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Uses only the disposable browser-certificate actor state;
 *                             no founder credentials, real employee data or business writes.
 * TENANT BOUNDARY: The generated test tenant is exact; the fixture Owner has no HR directory grant.
 * AUTHORITY BOUNDARY: The UI renders EOS denial; browser setup does not grant HR capability.
 * FINANCIAL AUTHORITY BOUNDARY: No financial command; Kennel EOS remains exclusive.
 */

import fs from 'node:fs';
import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const baseURL = process.env.BROWSER_CERT_BASE_URL || 'http://127.0.0.1:5174';
const WORKFORCE_ROUTE = '/api/hr/workforce';
const HR_WORKSPACE_PATH = '/headquarters?section=hr-workspace';

/**
 * @description Boots one exact fixture Owner directly into the mounted Headquarters HR surface.
 * @param {import('@playwright/test').Browser} browser - Isolated Chromium owner.
 * @param {{width:number,height:number}} viewport - Certified viewport dimensions.
 * @param {(page:import('@playwright/test').Page)=>Promise<void>} [beforeNavigation] - Optional route setup before the first document request.
 * @returns {Promise<{context:import('@playwright/test').BrowserContext,page:import('@playwright/test').Page,browserErrors:string[],bootstrapResponse:import('@playwright/test').Response,workforceResponse:import('@playwright/test').Response}>} Authenticated page and observed EOS responses.
 * @throws {Error} When the disposable actor or source bootstrap contract is missing.
 * @collaboration Uses only state minted by browser_cert_fixture.py; Python EOS revalidates the bearer and tenant membership.
 * @institutional One navigation prevents test-created duplicate bootstrap and source-read cascades; it changes no application authority or expected result.
 */
async function openOwnerDashboard(browser, viewport, beforeNavigation = async () => {}) {
  const actor = state.actors?.tenant_owner;
  if (!actor) throw new Error('HR_BROWSER_CERT_OWNER_ACTOR_REQUIRED');
  const context = await browser.newContext({ baseURL, viewport });
  const page = await context.newPage();
  const browserErrors = [];
  page.on('pageerror', error => browserErrors.push(error.message));
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
  const workforcePromise = page.waitForResponse(response => (
    new URL(response.url()).pathname === WORKFORCE_ROUTE
    && response.request().method() === 'GET'
  ));
  try {
    await beforeNavigation(page);
    await page.goto(HR_WORKSPACE_PATH);
    const [bootstrapResponse, workforceResponse] = await Promise.all([
      bootstrapPromise,
      workforcePromise,
    ]);
    expect(bootstrapResponse.status()).toBe(200);
    return { context, page, browserErrors, bootstrapResponse, workforceResponse };
  } catch (error) {
    await context.close();
    throw error;
  }
}

for (const viewport of [
  { name: 'desktop', width: 1440, height: 1000 },
  { name: 'mobile', width: 390, height: 844 },
]) {
  test(`mounted HR dashboard preserves EOS workforce denial at ${viewport.name}`, async ({ browser }) => {
    const { context, page, browserErrors, workforceResponse } = await openOwnerDashboard(browser, {
      width: viewport.width,
      height: viewport.height,
    });
    try {
      expect(workforceResponse.status()).toBe(403);
      await expect(page.getByRole('navigation', { name: 'HR workspace modules' })).toBeVisible();
      await expect(page.getByText('Access denied by Python EOS. No rows are displayed for this source.')).toBeVisible();
      await expect(page.getByText('No employees recorded.')).toHaveCount(0);
      await expect(page.getByText('Unavailable', { exact: true }).first()).toBeVisible();
      expect(browserErrors, browserErrors.join('\n')).toEqual([]);

      const dimensions = await page.evaluate(() => ({
        viewport: document.documentElement.clientWidth,
        document: document.documentElement.scrollWidth,
      }));
      expect(dimensions.document).toBeLessThanOrEqual(dimensions.viewport + 1);
    } finally {
      await context.close();
    }
  });
}

test('incomplete workforce page is unavailable and never verified empty', async ({ browser }) => {
  const { context, page, browserErrors, workforceResponse } = await openOwnerDashboard(
    browser,
    { width: 1440, height: 1000 },
    async (targetPage) => {
      await targetPage.route('**/api/hr/workforce**', route => route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      }));
    },
  );
  try {
    expect(workforceResponse.status()).toBe(200);
    await expect(page.getByText('Source unavailable (HR_SOURCE_RESPONSE_INVALID). No verified results are available.')).toBeVisible();
    await expect(page.getByText('No employees recorded.')).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Retry source read' })).toBeEnabled();
    expect(browserErrors, browserErrors.join('\n')).toEqual([]);
  } finally {
    await context.close();
  }
});

/**
 * ARTIFACT: tests/e2e/hr-dashboard-read-state.browser.spec.js
 * VERSION: v1.2.0-SINGLE-NAVIGATION-AUTH-CERT
 * AUTHORITY BOUNDARY: Verifies presentation of source-owned outcomes in a disposable fixture.
 * TENANT POSTURE: One generated test tenant; Owner has no workforce-directory capability.
 * FAIL-CLOSED POSTURE: A denied or malformed read is never presented as an empty employee ledger.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
