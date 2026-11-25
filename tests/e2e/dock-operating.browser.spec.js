/**
 * TITLE: WILSY OS Authenticated Dock Operating Browser Certificate
 * VERSION: v1.0.0
 * AUTHORITY: Disposable synthetic browser/EOS/Mongo evidence only.
 * EPITOME: Advance real source-owned work from the Dock and recover encrypted task conversations.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/dock-operating.browser.spec.js
 * COLLABORATION / OWNERSHIP: Existing browser harness, canonical EOS, Projects and Dock.
 * CERTIFICATION / UPDATE DATE: 2026-11-25
 * CHANGELOG: v1.0.0 adds desktop/mobile task commands, editable deterministic drafts and refresh continuity.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Runner-owned synthetic token; no real Founder credentials or S3 object writes.
 * TENANT BOUNDARY: Exact disposable tenant/principal; no mocked API success.
 * AUTHORITY BOUNDARY: Real authenticated source requests; fixture session is not Founder MFA acceptance.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively; no model invocation or financial mutation.
 */
import fs from 'node:fs';
import path from 'node:path';
import { expect, test } from '@playwright/test';

const state = JSON.parse(fs.readFileSync(process.env.BROWSER_CERT_STATE, 'utf8'));
if (!/^wilsy_l8_8m_r3_[a-zA-Z0-9_-]+$/.test(state.database_name || '') || !state.dock_operating) {
  throw new Error('DOCK_BROWSER_DISPOSABLE_FIXTURE_REQUIRED');
}
const fixture = state.dock_operating;
const actor = state.actors.commercial_admin;
const evidence = process.env.WILSY_DOCK_EVIDENCE_DIR;
if (!evidence) throw new Error('DOCK_BROWSER_EVIDENCE_DIRECTORY_REQUIRED');
fs.mkdirSync(evidence, { recursive: true, mode: 0o700 });

for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
  test(`authenticated Dock advances source work and resumes at ${viewport.width}px`, async ({ browser }) => {
    const context = await browser.newContext({ viewport, timezoneId: 'Africa/Johannesburg' });
    const page = await context.newPage();
    const errors = []; const modelCalls = [];
    const task = fixture.task_ids[String(viewport.width)];
    page.on('pageerror', error => errors.push(error.name));
    page.on('request', request => {
      if (request.method() === 'POST' && new URL(request.url()).pathname === '/api/wilsy-ai/reasoning') modelCalls.push('MODEL_POST');
    });
    page.on('dialog', dialog => dialog.accept());
    // Isolate the real Dock component from unrelated App startup. All API
    // transport below is the actual authenticated EOS, never an API route mock.
    await page.route('**/src/main.jsx', route => route.fulfill({ contentType: 'application/javascript', body: '' }));
    await page.addInitScript(({ token, tenant }) => {
      localStorage.setItem('wilsy_auth_token', token); localStorage.setItem('token', token);
      window.__WILSY_ACTIVE_TENANT__ = { tenantId: tenant };
    }, { token: actor.access_token, tenant: state.tenant_id });
    const mount = async () => {
      await page.evaluate(async ({ tenant, principal }) => {
        document.body.innerHTML = '<div id="dock-operating-certificate-root"></div>';
        const componentUrl = '/src/components/intelligence/WilsyOSIntelligenceDock.jsx';
        const transformed = await fetch(componentUrl).then(response => response.text());
        const match = transformed.match(/from ["']([^"']*\/react\.js\?v=[^"']+)["']/);
        if (!match) throw new Error('DOCK_BROWSER_REACT_IMPORT_UNAVAILABLE');
        const [react, dom, dock, transport] = await Promise.all([
          import(match[1]), import(match[1].replace('/react.js?', '/react-dom.js?')),
          import(componentUrl), import('/src/services/api.js'),
        ]);
        transport.setActiveTenantTransportId(tenant);
        dom.default.createRoot(document.getElementById('dock-operating-certificate-root')).render(
          react.default.createElement(dock.default, { authUser: {
            id: principal, tenantId: tenant, role: 'OWNER', businessRole: 'tenant_owner', firstName: 'Synthetic',
          }, activeTenant: { tenantId: tenant } }),
        );
      }, { tenant: state.tenant_id, principal: actor.principal_id });
      await page.getByTitle('Open Wilsy OS Intelligence Dock').click();
    };
    try {
      await page.goto('/discovery', { waitUntil: 'domcontentloaded' }); await mount();
      if (viewport.width === 1440) {
        const attention = page.getByRole('region', { name: 'Needs your attention' });
        await expect(attention.getByRole('heading', { name: 'Needs your attention' })).toBeVisible();
        await expect(attention).toContainText('MW-T11 browser alignment');
      }
      await page.evaluate(({ tenant, principal, project, task }) => {
        window.dispatchEvent(new CustomEvent('wilsy:ai-context-locator', { detail: {
          tenantId: tenant, principalId: principal,
          locator: { workspace: 'PROJECTS', project_id: project, task_id: task, participant_view: true },
        } }));
      }, { tenant: state.tenant_id, principal: actor.principal_id, project: fixture.project_id, task });
      await expect(page.getByRole('button', { name: 'Start work', exact: true })).toBeVisible();
      await page.getByRole('button', { name: 'Start work', exact: true }).click();
      await expect(page.getByText('EOS verified the command receipt and independently read the current task.', { exact: true })).toBeVisible();
      await page.getByRole('button', { name: 'Draft alignment plan', exact: true }).click();
      const editor = page.getByRole('textbox', { name: 'Edit plan' });
      await expect(editor).toHaveValue(/No AI model invoked/);
      const edited = 'Human-reviewed deterministic alignment checklist\n[ ] Review current dependency evidence\n[ ] Verify source result independently';
      await editor.fill(edited);
      await expect(editor).toHaveValue(edited);
      await expect(page.getByRole('button', { name: 'Accept and attach PDF' })).toBeEnabled();
      const pdfBytes = await page.evaluate(async ({ text, project, task }) => {
        const contract = await import('/src/components/intelligence/wilsyDockContract.js');
        // Read the exact current source again; the PDF generator receives no
        // fabricated task facts or provider output.
        const transport = await import('/src/services/api.js');
        const envelope = (await transport.default.get('/wilsy-ai/dock/context', { params: {
          workspace: 'PROJECTS', project_id: project, task_id: task, participant_view: true,
        } })).data;
        const artifact = { ...contract.draftDockPlan(envelope), content: text };
        const result = await contract.createDockPlanPdf(artifact);
        return [...new Uint8Array(await result.blob.arrayBuffer())];
      }, { text: edited, project: fixture.project_id, task });
      // UI screenshots are required even when external object storage is not
      // configured. Attachment persistence is independently certified by Mongo
      // integration with an explicitly injected object capability.
      fs.writeFileSync(path.join(evidence, `plan-${viewport.width}.pdf`), Buffer.from(pdfBytes));
      await page.screenshot({ path: path.join(evidence, `draft-${viewport.width}.png`) });
      await page.getByRole('button', { name: 'Discard draft' }).click();
      await page.getByRole('button', { name: 'Complete task', exact: true }).click();
      await expect(page.getByRole('region', { name: 'Live EOS task' })).toContainText('done');
      const headers = { Authorization: `Bearer ${actor.access_token}`, 'X-Tenant-ID': state.tenant_id };
      const source = await page.request.get('/api/wilsy-ai/dock/context', { headers,
        params: { workspace: 'PROJECTS', project_id: fixture.project_id, task_id: task, participant_view: true } });
      expect(source.status()).toBe(200); expect((await source.json()).source.revision).toBe(3);
      await page.getByRole('button', { name: 'Recent conversations' }).click();
      await expect(page.getByText('Encrypted conversation archive connected')).toBeVisible();
      await expect(page.getByRole('button', { name: /^Open conversation/ }).first()).toContainText('Saved in EOS');
      await page.reload({ waitUntil: 'domcontentloaded' }); await mount();
      await page.getByRole('button', { name: 'Recent conversations' }).click();
      await expect(page.getByRole('button', { name: /^Open conversation/ }).first()).toContainText('Saved in EOS');
      await page.getByRole('button', { name: /^Open conversation/ }).first().click();
      await expect(page.getByRole('region', { name: 'Live EOS task' })).toContainText(`MW-T11 browser alignment ${viewport.width}`);
      await expect(page.getByRole('region', { name: 'Live EOS task' })).toContainText('done');
      await page.screenshot({ path: path.join(evidence, `reopened-${viewport.width}.png`) });
      const composer = page.getByPlaceholder('Ask Wilsy OS…');
      await expect(composer).toBeVisible();
      const bounds = await composer.boundingBox(); expect(bounds.y + bounds.height).toBeLessThanOrEqual(viewport.height);
      expect(modelCalls).toEqual([]); expect(errors).toEqual([]);
    } finally { await context.close(); }
  });
}

// ARTIFACT: dock-operating.browser.spec.js
// VERSION: v1.0.0
// AUTHORITY BOUNDARY: authenticated synthetic browser evidence; no Founder acceptance
// TENANT POSTURE: UUID disposable database and explicit synthetic owner/contributor
// FAIL-CLOSED POSTURE: real source state, saved history and no model call required
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT


