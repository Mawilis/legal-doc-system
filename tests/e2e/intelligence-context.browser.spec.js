/**
 * TITLE: WILSY OS contextual Dock rendered browser certificate
 * VERSION: v1.1.0-CONTEXTUAL-GREETING-BROWSER-CERT
 * AUTHORITY: Synthetic Chromium presentation evidence; EOS owns admission.
 * EPITOME: Verify bounded page locators, visible source evidence, readable
 * mobile/desktop context and cancellation without a provider or real session.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/intelligence-context.browser.spec.js
 * COLLABORATION / OWNERSHIP: Existing Playwright/Vite harness and real Dock.
 * CERTIFICATION / UPDATE DATE: 2026-11-20
 * CHANGELOG: v1.1.0-CONTEXTUAL-GREETING-BROWSER-CERT certifies the
 * authenticated first-name greeting and truthful server-grounded source
 * disclosure at desktop/mobile sizes. v1.0.0-CONTEXT-INSPECTION-BROWSER-CERT establishes 1440px and
 * 390px source-inspection journeys and forbids model calls during inspection.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Synthetic names, no bearer or real database.
 * TENANT BOUNDARY: Fixture responses match one synthetic tenant and principal.
 * AUTHORITY BOUNDARY: Rendered inspection only; no live Founder acceptance,
 * contextual model execution, seat allocation or entitlement issuance claim.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import { expect, test } from '@playwright/test';

const TENANT = 'ai-browser-context-tenant';
const PRINCIPAL = 'ai-browser-context-person';
const PROJECT = 'prj-' + 'a'.repeat(48);

for (const width of [1440, 390]) {
  test('verified Dock context inspection at ' + width + 'px', async ({ page }) => {
    await page.setViewportSize({ width, height: 950 });
    const modelCalls = [];
    const contextReads = [];
    await page.route('**/api/**', async route => {
      const request = route.request();
      const url = new URL(request.url());
      if (request.method() === 'POST' && url.pathname.includes('/wilsy-ai/')) modelCalls.push(url.pathname);
      let status = 503;
      let response = { detail: 'SYNTHETIC_SOURCE_UNAVAILABLE' };
      if (url.pathname === '/api/kernel') {
        status = 200; response = { status: 'OPERATIONAL' };
      }
      if (request.method() === 'GET' && url.pathname === '/api/wilsy-ai/reasoning/context') {
        contextReads.push(Object.fromEntries(url.searchParams));
        expect(request.headers()['x-tenant-id']).toBe(TENANT);
        const isProject = url.searchParams.get('project_id') === PROJECT;
        status = 200;
        response = {
          schema: 'WILSY-AI-VERIFIED-CONTEXT/V1', tenant_id: TENANT, principal_id: PRINCIPAL,
          locator: { workspace: isProject ? 'PROJECTS' : 'HEADQUARTERS', project_id: isProject ? PROJECT : null },
          context_fingerprint: 'a'.repeat(128), observed_at: '2026-11-20T08:00:00+00:00',
          authority: { source: 'PYTHON_EOS', model_invoked: false, read_only: true, financial_execution: false },
          allowance: { available_request_units: 18, seat_allocation: { state: 'UNAVAILABLE' } },
          work: isProject ? { project: { project_id: PROJECT, name: 'Verified delivery project', revision: 1 },
            current_person_name: 'Verified Colleague',
            sources: [{ kind: 'PROJECT', label: 'Verified delivery project', project_id: PROJECT }] } : null,
        };
      }
      await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(response) });
    });
    await page.goto('/discovery', { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => { document.body.innerHTML = '<div id="dock-context-browser-root"></div>'; });
    await page.evaluate(async ({ tenant, principal }) => {
      const componentUrl = '/src/components/intelligence/WilsyOSIntelligenceDock.jsx';
      const transformed = await fetch(componentUrl).then(response => response.text());
      const reactMatch = transformed.match(/from ["']([^"']*\/react\.js\?v=[^"']+)["']/);
      if (!reactMatch) throw new Error('DOCK_BROWSER_REACT_DEPENDENCY_UNRESOLVED');
      const [react, dom, dock] = await Promise.all([
        import(reactMatch[1]), import(reactMatch[1].replace('/react.js?', '/react-dom.js?')), import(componentUrl),
      ]);
      // Supply only the same transport tenant selector established by the
      // authenticated root; this synthetic selector is never an IAM proof.
      const transport = await import('/src/services/api.js');
      transport.setActiveTenantTransportId(tenant);
      dom.default.createRoot(document.getElementById('dock-context-browser-root')).render(
        react.default.createElement(dock.default, {
          authUser: { id: principal, tenantId: tenant, role: 'OWNER', firstName: 'Nandi' },
          activeTenant: { tenantId: tenant },
        }),
      );
    }, { tenant: TENANT, principal: PRINCIPAL });
    await page.getByTitle('Open Wilsy OS Intelligence Dock').click();
    await expect(page.getByText(/^Good (morning|afternoon|evening), Nandi\.$/)).toBeVisible();
    const context = page.getByRole('region', { name: 'Verified workspace context' });
    await expect(context).toContainText('18 requests available');
    await page.evaluate(({ tenant, principal, project }) => {
      window.dispatchEvent(new CustomEvent('wilsy:ai-context-locator', { detail: {
        tenantId: tenant, principalId: principal,
        locator: { workspace: 'PROJECTS', project_id: project, project_revision: 1 },
      } }));
    }, { tenant: TENANT, principal: PRINCIPAL, project: PROJECT });
    await expect(context.getByLabel('Inspect verified workspace context')).toContainText('Verified delivery project');
    await context.getByLabel('Inspect verified workspace context').click();
    const source = context.getByRole('button', { name: 'Inspect source: Verified delivery project' });
    await expect(source).toBeVisible();
    await expect(context).toContainText('Verified Colleague');
    await expect(context).toContainText('Seats and pricing: unavailable');
    await expect(context).toContainText('Verified project sources can support reasoning only after independent EOS authorization');
    expect(contextReads.at(-1)).toMatchObject({ workspace: 'PROJECTS', project_id: PROJECT, project_revision: '1' });
    const geometry = await context.evaluate(element => {
      const bounds = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      return { left: bounds.left, right: bounds.right, width: bounds.width,
        color: style.color, background: style.backgroundColor };
    });
    expect(geometry.left).toBeGreaterThanOrEqual(0);
    expect(geometry.right).toBeLessThanOrEqual(width);
    expect(geometry.color).toBe('rgb(241, 245, 249)');
    expect(geometry.background).toBe('rgb(17, 24, 39)');
    await source.focus();
    await expect(source).toBeFocused();
    expect(modelCalls).toEqual([]);
    await page.screenshot({ path: test.info().outputPath('context-expanded-' + width + '.png'), fullPage: true });
    await context.getByLabel('Inspect verified workspace context').click();
    const composer = page.getByPlaceholder('Ask Wilsy OS…');
    await expect(composer).toBeVisible();
    await expect(page.getByRole('button', { name: 'Send', exact: true })).toBeVisible();
    const inputBounds = await composer.boundingBox();
    expect(inputBounds.y + inputBounds.height).toBeLessThanOrEqual(950);
    await composer.fill('A reviewable question');
    await expect(composer).toHaveValue('A reviewable question');
    expect(modelCalls).toEqual([]);
    await page.screenshot({ path: test.info().outputPath('context-' + width + '.png'), fullPage: true });
  });
}

// ARTIFACT: intelligence-context.browser.spec.js
// VERSION: v1.1.0-CONTEXTUAL-GREETING-BROWSER-CERT
// AUTHORITY BOUNDARY: synthetic browser inspection only; no authenticated IAM claim
// TENANT POSTURE: exact synthetic tenant and principal transport projection
// FAIL-CLOSED POSTURE: fixture cannot create a seat, grant or model execution
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
