/**
 * TITLE: WILSY OS Mission and Strategy Authenticated Browser Certificate
 * VERSION: v1.5.0-GOVERNED-READER-PROVISIONING-CERT
 * AUTHORITY: Disposable browser evidence only; Python EOS owns publication/IAM.
 * EPITOME: Prove both approved control positions, real author-submit-independent
 * publication, private drafts, exact tenant denial and desktop/mobile documents.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/company-operating-documents.browser.spec.js
 * COLLABORATION / OWNERSHIP: Existing runner, companion company fixture, HQ/viewer.
 * CERTIFICATION / UPDATE DATE: 2026-11-14
 * CHANGELOG: v1.5.0-GOVERNED-READER-PROVISIONING-CERT adds real authenticated grant,
 * immediate read/revoke, membership/capacity/session currentness and bounded audit.
 * Prior certification verifies the preserved square header
 * hierarchy and modal priority over the movable companion while preserving
 * every independent source-publication and transport-recovery assertion.
 * CHANGELOG: v1.3.0-DOCUMENT-LIVE-TRANSPORT-RECOVERY-CERT records sanitized request scope/status,
 * tests actual denied readers and retry after injected transport failures, and
 * captures both document classifications at desktop and mobile widths.
 * CHANGELOG: v1.2.0-OFFICIAL-SQUARE-BRAND-BROWSER-CERT verifies the approved vivid square
 * asset and 64px header mark, with unchanged source-command and tenant gates.
 * CHANGELOG: v1.1.0-PLATFORM-OWNER-SUPPLIED-LOGO-BROWSER-CERT verifies the selected square navy logo,
 * exact company Headquarters, Legal exclusion despite legacy active entitlement,
 * internal Operations admission and retained Mission/Strategy lifecycle proof.
 * CHANGELOG: v1.0.0-COMPANY-DOCUMENT-BROWSER-CERT adds real source commands,
 * replay/conflict, approval independence, durable readback and responsive evidence.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic actors/content only; no credentials in evidence.
 * TENANT BOUNDARY: Exact company identifier inside UUID-owned disposable database.
 * AUTHORITY BOUNDARY: Test sessions are not human Founder acceptance or production grants.
 * FINANCIAL AUTHORITY BOUNDARY: No financial authority; Kennel EOS exclusively.
 */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { expect, test } from '@playwright/test';

const state = JSON.parse(fs.readFileSync(process.env.BROWSER_CERT_STATE, 'utf8'));
if (!/^wilsy_l8_8m_r3_[a-zA-Z0-9_-]+$/.test(state.database_name || '')) throw new Error('COMPANY_CERT_DISPOSABLE_DATABASE_REQUIRED');
const company = state.company_documents;
if (company?.tenant_id !== 'WILSYTENANT-4CD2FZ4O') throw new Error('COMPANY_CERT_EXACT_TENANT_REQUIRED');
const evidence = process.env.WILSY_HEADQUARTERS_EVIDENCE_DIR;
if (!evidence) throw new Error('COMPANY_CERT_EVIDENCE_DIRECTORY_REQUIRED');
fs.mkdirSync(evidence, { recursive: true, mode: 0o700 });


test('independent reader provisioning opens both company documents and revocation immediately closes access', async ({ browser, request }) => {
  const headers = actor => ({ Authorization: 'Bearer ' + company.actors[actor].access_token, 'X-Tenant-ID': company.tenant_id });
  const network = [];
  const get = async (actor, classification, expected) => {
    const response = await request.get('/api/company-operating-documents/' + classification, { headers: headers(actor) });
    expect(response.status()).toBe(expected);
    const body = await response.json();
    network.push({ method: 'GET', path: '/api/company-operating-documents/' + classification,
      actor_fixture: actor, tenant_id: company.tenant_id, bearer_present: true, status: response.status(),
      state: body.state || null, code: body.detail?.error || null });
    return body;
  };
  for (const classification of ['MISSION', 'STRATEGY']) await get('founder_label', classification, 403);
  const payload = { target_principal_id: company.actors.founder_label.principal_id,
    target_business_role: 'tenant_owner', expected_membership_revision: 0, expected_capacity_revision: 0,
    expected_assignment_revision: null, approval_reference: 'SYNTHETIC-INDEPENDENT-DECISION',
    reason_reference: 'SYNTHETIC-READ-ONLY-HEADQUARTERS', idempotency_key: 'synthetic-browser-grant' };
  const source = '/api/company-operating-documents/reader-grants';
  const forbidden = await request.post(source, { headers: headers('founder_label'), data: payload });
  expect(forbidden.status()).toBe(403);
  const grant = await request.post(source, { headers: headers('grantor'), data: payload });
  expect(grant.status()).toBe(200);
  const receipt = await grant.json();
  expect(receipt.state).toBe('NEWLY_GRANTED');
  expect(receipt.role_id).toBe('COMPANY_DOCUMENT_READER');
  expect(receipt.authorization_evidence_fingerprint).toMatch(/^[a-f0-9]{128}$/);
  const replay = await request.post(source, { headers: headers('grantor'), data: payload });
  expect(replay.status()).toBe(200);
  expect(await replay.json()).toEqual({ ...receipt, state: 'EXACT_REPLAY' });
  expect((await request.post(source, { headers: headers('grantor'), data: { ...payload, reason_reference: 'different' } })).status()).toBe(409);
  expect((await request.post(source, { headers: headers('grantor'), data: { ...payload, target_role_id: 'COMPANY_DOCUMENT_PUBLISHER' } })).status()).toBe(422);
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  try {
    const page = await context.newPage();
    await page.addInitScript(({ token }) => { localStorage.setItem('wilsy_auth_token', token); localStorage.setItem('token', token); }, { token: company.actors.founder_label.access_token });
    await page.goto('/headquarters');
    await expect(page.getByRole('heading', { name: 'WILSY Headquarters', exact: true })).toBeVisible();
    for (const classification of ['MISSION', 'STRATEGY']) {
      const view = await get('founder_label', classification, 200);
      expect(view.state).toBe('NOT_YET_PUBLISHED'); expect(view.document).toBeNull();
      expect(view.available_actions).toEqual(['READ_HISTORY']);
      for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
        await page.setViewportSize(viewport);
        await page.getByRole('button', { name: classification === 'MISSION' ? 'Our Mission' : 'Our Strategy', exact: true }).click();
        const dialog = page.getByRole('dialog', { name: classification === 'MISSION' ? 'Our Mission' : 'Our Strategy' });
        await expect(dialog.getByRole('heading', { name: 'Not yet published', exact: true })).toBeVisible();
        await expect(dialog.getByRole('button', { name: 'Prepare draft', exact: true })).toHaveCount(0);
        await expect(dialog.getByRole('button', { name: 'Review drafts', exact: true })).toHaveCount(0);
        await dialog.getByRole('button', { name: 'Refresh source', exact: true }).click();
        await expect(dialog.getByRole('heading', { name: 'Not yet published', exact: true })).toBeVisible();
        await expect(dialog.getByAltText('WILSY OS logo')).toHaveAttribute('src', '/brand/wilsy-os-official.png');
        await page.screenshot({ path: path.join(evidence, 'governed-reader-' + classification.toLowerCase() + '-' + viewport.width + '.png'), fullPage: true });
        await dialog.getByRole('button', { name: 'Close company document' }).click();
      }
    }
    for (const operation of ['drafts', 'submit', 'publish']) {
      const response = await request.post('/api/company-operating-documents/MISSION/' + operation, {
        headers: headers('founder_label'), data: { expected_revision: 0 } });
      expect(response.status()).toBe(403);
    }
    const revoke = await request.post('/api/tenants/role-assignments/revocations', { headers: headers('grantor'), data: {
      target_principal_id: payload.target_principal_id, target_role_id: 'COMPANY_DOCUMENT_READER',
      expected_target_assignment_revision: 0, reason_reference: 'SYNTHETIC-REVOKE', idempotency_key: 'synthetic-browser-revoke' } });
    expect(revoke.status()).toBe(200);
    for (const classification of ['MISSION', 'STRATEGY']) await get('founder_label', classification, 403);
    const historic = await request.post(source, { headers: headers('grantor'), data: payload });
    expect(historic.status()).toBe(200); expect((await historic.json()).state).toBe('EXACT_REPLAY');
    await get('founder_label', 'MISSION', 403);
    for (const actor of ['stale_session', 'revoked_member', 'revoked_capacity']) {
      await get(actor, 'MISSION', 200);
      execFileSync(path.resolve('.venv/bin/python'), [path.resolve('tests/e2e/company_document_cert_fixture.py'),
        'challenge', '--state', process.env.BROWSER_CERT_STATE, '--kind', actor], { stdio: 'pipe' });
      for (const classification of ['MISSION', 'STRATEGY']) await get(actor, classification, actor === 'stale_session' ? 401 : 403);
    }
    expect((await request.get('/api/company-operating-documents/MISSION')).status()).toBe(401);
  } finally {
    await context.close();
    fs.writeFileSync(path.join(evidence, 'reader-provisioning-network.json'), JSON.stringify({ synthetic_only: true,
      current_session_is_not_founder_acceptance: true, grant_receipt: receipt, network }, null, 2));
  }
});

for (const [classification, viewport] of [
  ['MISSION', { width: 1440, height: 900 }],
  ['STRATEGY', { width: 390, height: 844 }],
]) {
  test(`${classification} governs private preparation and independent publication at ${viewport.width}px`, async ({ browser }) => {
    const contexts = []; const errors = []; const network = []; const captures = [];
    const source = '/api/company-operating-documents/' + classification;
    const headers = key => ({ Authorization: 'Bearer ' + company.actors[key].access_token, 'X-Tenant-ID': company.tenant_id });
    const login = async (key, selectedViewport = viewport) => {
      const context = await browser.newContext({ viewport: selectedViewport, timezoneId: 'Africa/Johannesburg' }); contexts.push(context);
      const page = await context.newPage();
      page.on('pageerror', error => errors.push(error.name));
      page.on('response', response => {
        const url = new URL(response.url());
        if (!url.pathname.startsWith('/api/company-operating-documents/')) return;
        captures.push((async () => {
          const request = response.request(); const headers = await request.allHeaders();
          const entry = { path: url.pathname, method: request.method(), status: response.status(),
            bearer_present: /^Bearer\s+\S+$/.test(headers.authorization || ''),
            tenant_id: headers['x-tenant-id'] || null, business_capacity: 'tenant_owner', actor_fixture: key };
          if (response.status() >= 400) {
            try {
              const body = await response.json();
              const code = body?.detail?.error || body?.error?.code || body?.code;
              entry.error_code = typeof code === 'string' && /^[A-Z][A-Z0-9_]{0,95}$/.test(code) ? code : null;
            } catch { entry.error_code = null; }
          }
          network.push(entry);
        })());
      });
      await page.addInitScript(({ token }) => { localStorage.setItem('wilsy_auth_token', token); localStorage.setItem('token', token); }, { token: company.actors[key].access_token });
      await page.goto('/headquarters');
      await expect(page.getByRole('heading', { name: 'WILSY Headquarters', exact: true })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Our Mission', exact: true })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Our Strategy', exact: true })).toBeVisible();
      await expect(page.getByAltText('WILSY OS logo')).toHaveAttribute('src', '/brand/wilsy-os-official.png');
      const mark = page.getByAltText('WILSY OS logo');
      expect(await mark.evaluate(image => image.complete && image.naturalWidth === 512)).toBe(true);
      const markBox = await mark.boundingBox(); expect(markBox.width).toBe(selectedViewport.width >= 768 ? 64 : 56); expect(markBox.height).toBe(selectedViewport.width >= 768 ? 64 : 56);
      const headerBox = await page.locator('header').first().boundingBox();
      expect(markBox.y).toBeGreaterThanOrEqual(headerBox.y); expect(markBox.y + markBox.height).toBeLessThanOrEqual(headerBox.y + headerBox.height);

      await expect(page.locator('.hq-work')).not.toContainText('Loading the authorized My Work projection');
      await expect(page.locator('[data-company-purpose="PLATFORM_OWNER"]')).toBeVisible();
      await expect(page.locator('[data-wilsy-platform-owner="true"]')).toBeVisible();
      await expect(page.locator('.hq-sidebar-title')).toHaveText('Platform owner workspace');
      await expect(page.locator('.hq-hero')).toContainText('Develop. Operate. Maintain — WILSY OS.');
      await expect(page.locator('[data-eos-controller-product-navigation]')).toContainText('INTERNAL WORKSPACES');
      await expect(page.locator('[data-eos-controller-product-navigation] [data-wilsy-module-entry="LEGAL_OS"]')).toHaveCount(0);
      const moduleResponse = await context.request.get('/api/auth/module-manifest', { headers: headers(key) });
      expect(moduleResponse.status()).toBe(200);
      const modules = (await moduleResponse.json()).workspace.modules;
      expect(modules.map(item => item.moduleId)).toEqual(['OPERATIONS']);
      const bootstrapResponse = await context.request.get('/api/auth/workspace-bootstrap', { headers: headers(key) });
      expect(bootstrapResponse.status()).toBe(200);
      const bootstrap = (await bootstrapResponse.json()).workspace;
      expect(bootstrap.workspaceId).toBe('WILSY_HEADQUARTERS');
      expect(bootstrap.businessRole).toBe('tenant_owner');
      expect(await page.evaluate(() => getComputedStyle(document.body, '::after').display)).toBe('none');
      await page.evaluate(() => window.dispatchEvent(new CustomEvent('wilsy:switch-dashboard', { detail: { dashboardKey: 'LEGAL_DASHBOARD' } })));
      await expect(page.getByRole('heading', { name: 'WILSY Headquarters', exact: true })).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
      return { page, context };
    };
    const open = async page => {
      await page.getByRole('button', { name: classification === 'MISSION' ? 'Our Mission' : 'Our Strategy', exact: true }).click();
      const dialog = page.getByRole('dialog');
      await expect(dialog).toHaveAttribute('data-company-document', classification);
      await expect(page.locator('[data-wilsy-intelligence-dock]')).not.toBeVisible();
      await expect(dialog.getByAltText('WILSY OS logo')).toHaveAttribute('src', '/brand/wilsy-os-official.png');
      await expect(dialog.getByRole('button', { name: 'Close company document' })).toBeFocused();
      return dialog;
    };
    try {
      const publicContext = await browser.newContext({ viewport }); contexts.push(publicContext);
      const publicPage = await publicContext.newPage();
      for (const route of ['/discovery', '/login']) {
        await publicPage.goto(route);
        const publicMark = publicPage.getByAltText('WILSY OS platform mark');
        await expect(publicMark).toHaveAttribute('src', '/brand/wilsy-os-official.png');
        await expect(publicMark).toHaveJSProperty('complete', true);
        expect(await publicMark.evaluate(image => image.naturalWidth)).toBe(512);
        expect(await publicPage.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
        expect(await publicPage.evaluate(() => getComputedStyle(document.body, '::after').content)).not.toContain('LEGAL');
        await publicPage.screenshot({ path: path.join(evidence, `${route.slice(1)}-${viewport.width}-official-brand.png`) });
      }
      const paintedAliases = await publicPage.evaluate(async paths => {
        const painted = [];
        for (const path of paths) {
          const image = await new Promise((resolve, reject) => {
            const candidate = new Image(); candidate.onload = () => resolve(candidate);
            candidate.onerror = () => reject(new Error('OFFICIAL_BRAND_COMPATIBILITY_IMAGE_FAILED'));
            candidate.src = path;
          });
          const canvas = document.createElement('canvas'); canvas.width = 180; canvas.height = 64;
          const context = canvas.getContext('2d'); context.drawImage(image, 0, 0, 180, 64);
          const pixels = context.getImageData(0, 0, 180, 64).data;
          painted.push({ path, loaded: image.naturalWidth > 0, visible: pixels.some((value, index) => index % 4 === 3 && value > 0) });
        }
        return painted;
      }, ['/src/assets/logo/wilsy-logo.svg', '/src/assets/logo/wilsy-icon.svg', '/src/assets/logo/wilsy-header-emblem.svg', '/assets/images/superadmin/wilsy-logo.svg', '/favicon.svg']);
      expect(paintedAliases.every(item => item.loaded && item.visible)).toBe(true);
      const author = await login('author');
      const hero = await author.page.locator('.hq-hero').boundingBox();
      const mission = await author.page.getByRole('button', { name: 'Our Mission', exact: true }).boundingBox();
      expect(mission.x).toBeGreaterThan(hero.x + hero.width / 2);
      expect(mission.y).toBeGreaterThan(hero.y + hero.height / 2);
      await expect(author.page.locator('.hq-strategy').getByRole('button', { name: 'Our Strategy', exact: true })).toBeVisible();
      await author.page.screenshot({ path: path.join(evidence, `headquarters-${viewport.width}-platform-owner.png`), fullPage: false });
      let dialog = await open(author.page);
      await expect(dialog.getByRole('heading', { name: 'Not yet published', exact: true })).toBeVisible();
      await author.page.screenshot({ path: path.join(evidence, `${classification.toLowerCase()}-${viewport.width}-unpublished.png`) });
      await dialog.getByRole('button', { name: 'Prepare draft', exact: true }).click();
      await dialog.getByLabel('Document title', { exact: true }).fill('Synthetic browser ' + classification.toLowerCase());
      await dialog.getByLabel('Document version', { exact: true }).fill('1.0.0');
      await dialog.getByLabel('Section title', { exact: true }).fill('Synthetic purpose');
      await dialog.getByLabel('Proposed content', { exact: true }).fill('Synthetic certification content only. This is not WILSY policy.');
      const [created] = await Promise.all([
        author.page.waitForResponse(response => new URL(response.url()).pathname === source + '/drafts' && response.request().method() === 'POST'),
        dialog.getByRole('button', { name: 'Save private draft', exact: true }).click(),
      ]);
      expect(created.status()).toBe(201);
      const saved = (await created.json()).document;
      const key = (await created.request().allHeaders())['idempotency-key'];
      const payload = created.request().postDataJSON();
      await expect(dialog.getByText('EOS confirmed the command and its durable document readback.')).toBeVisible();
      const replay = await author.context.request.post(source + '/drafts', { headers: { ...headers('author'), 'Idempotency-Key': key }, data: payload });
      expect(replay.status()).toBe(201); expect((await replay.json()).document).toEqual(saved);
      const conflict = await author.context.request.post(source + '/drafts', { headers: { ...headers('author'), 'Idempotency-Key': key }, data: { ...payload, title: 'Divergent synthetic intent' } });
      expect(conflict.status()).toBe(409);
      const reader = await login('reader'); const readerDialog = await open(reader.page);
      await expect(readerDialog.getByRole('heading', { name: 'Not yet published' })).toBeVisible();
      await expect(readerDialog).not.toContainText('Synthetic certification content only.');
      await expect(readerDialog.getByRole('button', { name: 'Prepare draft' })).toHaveCount(0);
      expect((await reader.context.request.get(source + '?review=true', { headers: headers('reader') })).status()).toBe(403);
      expect((await reader.context.request.get(source + '?revision=1', { headers: headers('reader') })).status()).toBe(404);
      expect((await reader.context.request.get(source, { headers: headers('founder_label') })).status()).toBe(403);
      expect((await reader.context.request.get(source, { headers: { ...headers('reader'), 'X-Tenant-ID': state.foreign_tenant_id } })).status()).toBe(403);
      expect((await reader.context.request.post(source + '/drafts', { headers: { ...headers('reader'), 'Idempotency-Key': 'forbidden-reader' }, data: payload })).status()).toBe(403);
      await dialog.getByRole('button', { name: 'Submit for approval', exact: true }).click();
      await expect(dialog.locator('[data-state="SUBMITTED"]')).toBeVisible();
      const self = await author.context.request.post(source + '/publish', { headers: { ...headers('author'), 'Idempotency-Key': 'forbidden-self-publication' }, data: { expected_revision: 2, approval_reference: 'not-independent', effective_from: new Date(Date.now() - 60000).toISOString() } });
      expect(self.status()).toBe(403);
      const publisher = await login('publisher'); const publishing = await open(publisher.page);
      await expect(publishing.getByRole('heading', { name: 'Not yet published' })).toBeVisible();
      await publishing.getByRole('button', { name: 'Review drafts', exact: true }).click();
      await expect(publishing.locator('[data-state="SUBMITTED"]')).toBeVisible();
      await publishing.getByLabel('Approval reference', { exact: true }).fill('SYNTHETIC-BROWSER-APPROVAL');
      await publishing.getByLabel('Effective date and time', { exact: true }).fill('2026-01-01T09:00');
      await publishing.getByRole('button', { name: 'Approve and publish', exact: true }).click();
      await expect(publishing.getByText('EOS confirmed the command and its durable document readback.')).toBeVisible();
      await expect(publishing.locator('[data-state="PUBLISHED"]')).toBeVisible();
      await readerDialog.getByRole('button', { name: 'Refresh source', exact: true }).click();
      await expect(readerDialog.getByRole('heading', { name: 'Synthetic browser ' + classification.toLowerCase(), exact: true })).toBeVisible();
      await expect(readerDialog.getByText('Synthetic certification content only. This is not WILSY policy.', { exact: true })).toBeVisible();
      const paper = readerDialog.locator('article');
      expect(await paper.locator('p').first().evaluate(node => getComputedStyle(node).color)).toBe('rgb(83, 100, 125)');
      expect(await readerDialog.evaluate(node => node.scrollWidth <= window.innerWidth)).toBe(true);
      const box = await readerDialog.boundingBox(); expect(box.y).toBe(0); expect(Math.abs(box.height - viewport.height)).toBeLessThanOrEqual(1);
      const close = readerDialog.getByRole('button', { name: 'Close document', exact: true });
      expect(await close.evaluate(node => { const box = node.getBoundingClientRect(); return node.contains(document.elementFromPoint(box.x + box.width / 2, box.y + box.height / 2)); })).toBe(true);
      await reader.page.screenshot({ path: path.join(evidence, `${classification.toLowerCase()}-${viewport.width}-published.png`) });
      // Separate context, same synthetic current source; never a human session.
      const otherViewport = viewport.width === 1440 ? { width: 390, height: 844 } : { width: 1440, height: 900 };
      const responsiveReader = await login('reader', otherViewport);
      const responsiveDialog = await open(responsiveReader.page);
      await expect(responsiveDialog.getByText('Synthetic certification content only. This is not WILSY policy.', { exact: true })).toBeVisible();
      expect(await responsiveDialog.evaluate(node => node.scrollWidth <= innerWidth)).toBe(true);
      await responsiveReader.page.screenshot({ path: path.join(evidence, `${classification.toLowerCase()}-${otherViewport.width}-published.png`) });
      await responsiveDialog.getByRole('button', { name: 'Close document', exact: true }).click();
      const deniedReader = await login('founder_label');
      const deniedDialog = await open(deniedReader.page);
      await expect(deniedDialog.getByRole('heading', { name: 'Access denied', exact: true })).toBeVisible();
      await expect(deniedDialog.getByText('HTTP 403', { exact: true })).toBeVisible();
      await expect(deniedDialog.getByRole('heading', { name: 'Next step', exact: true })).toBeVisible();
      await expect(deniedDialog.getByRole('button', { name: 'Prepare draft', exact: true })).toHaveCount(0);
      await expect(deniedDialog.getByRole('button', { name: 'Approve and publish', exact: true })).toHaveCount(0);
      await expect(deniedDialog).not.toContainText('Synthetic certification content only.');
      await deniedReader.page.screenshot({ path: path.join(evidence, `${classification.toLowerCase()}-${viewport.width}-actual-denied.png`) });
      await deniedDialog.getByRole('button', { name: 'Close document', exact: true }).click();
      // Faults affect only this disposable page's read transport. Retrying must
      // reach the unchanged real EOS publication and render verified content.
      for (const fault of ['503', '404', 'invalid', 'network']) {
        await reader.page.route('**/api/company-operating-documents/' + classification + '?*', async route => {
          if (fault === 'network') { await route.abort('connectionrefused'); return; }
          await route.fulfill({ status: fault === 'invalid' ? 200 : Number(fault), contentType: 'application/json',
            body: JSON.stringify(fault === 'invalid' ? { unexpected: 'not-a-publication' }
              : fault === '503' ? { detail: { error: 'COMPANY_DOCUMENT_SOURCE_UNAVAILABLE' } } : { detail: 'Not Found' }) });
        });
        await readerDialog.getByRole('button', { name: 'Refresh source', exact: true }).click();
        await expect(readerDialog.getByRole('heading', { name: fault === 'invalid' ? 'Document response could not be verified' : 'Document source unavailable', exact: true })).toBeVisible();
        await expect(readerDialog.getByRole('heading', { name: 'Not yet published', exact: true })).toHaveCount(0);
        await expect(readerDialog).not.toContainText('Synthetic certification content only.');
        await expect(readerDialog).not.toContainText('Current company session required');
        await expect(readerDialog.getByRole('heading', { name: 'Next step', exact: true })).toBeVisible();
        await reader.page.screenshot({ path: path.join(evidence, `${classification.toLowerCase()}-${viewport.width}-${fault}.png`) });
        await reader.page.unroute('**/api/company-operating-documents/' + classification + '?*');
        await readerDialog.getByRole('button', { name: 'Retry source read', exact: true }).click();
        await expect(readerDialog.getByText('Synthetic certification content only. This is not WILSY policy.', { exact: true })).toBeVisible();
      }

      await readerDialog.getByRole('button', { name: 'Synthetic purpose', exact: true }).click();
      await readerDialog.getByRole('button', { name: 'Revision history', exact: true }).click();
      await readerDialog.getByRole('button', { name: /Version 1.0.0 · revision 3/ }).click();
      await expect(readerDialog.getByText('Historical revision 3', { exact: true })).toBeVisible();
      await readerDialog.getByRole('button', { name: 'Current publication', exact: true }).click();
      await expect(readerDialog.getByRole('heading', { name: 'Synthetic browser ' + classification.toLowerCase(), exact: true })).toBeVisible();
      await readerDialog.getByRole('button', { name: 'Close document', exact: true }).focus();
      await reader.page.keyboard.press('Tab');
      await expect(readerDialog.getByRole('button', { name: 'Close company document', exact: true })).toBeFocused();
      await reader.page.keyboard.press('Escape'); await expect(readerDialog).toHaveCount(0);
      await expect(reader.page.getByRole('button', { name: classification === 'MISSION' ? 'Our Mission' : 'Our Strategy', exact: true })).toBeFocused();
      const other = classification === 'MISSION' ? 'Our Strategy' : 'Our Mission';
      await reader.page.getByRole('button', { name: other, exact: true }).click();
      await expect(reader.page.getByRole('dialog')).toHaveAttribute('data-company-document', classification === 'MISSION' ? 'STRATEGY' : 'MISSION');
      await reader.page.getByRole('button', { name: 'Close company document', exact: true }).click();
      expect(errors).toEqual([]);
    } finally {
      await Promise.all(captures);
      fs.writeFileSync(path.join(evidence, `${classification.toLowerCase()}-network.json`), JSON.stringify(network, null, 2));
      for (const context of contexts) await context.close();
    }
  });
}

// ARTIFACT: company-operating-documents.browser.spec.js
// VERSION: v1.5.0-GOVERNED-READER-PROVISIONING-CERT
// AUTHORITY BOUNDARY: Disposable automated browser evidence; no human acceptance.
// TENANT POSTURE: Exact company source inside UUID-owned database only.
// FAIL-CLOSED POSTURE: Missing readback or independent publication fails the test.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
