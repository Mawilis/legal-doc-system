/**
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
 * TITLE: WILSY OS Headquarters in-view operating workspace browser certificate
 * VERSION: v1.7.0-COMPUTED-HQ-COLUMN-CERT
 * AUTHORITY: Disposable browser evidence only; EOS owns all business truth.
 * EPITOME: Compare desktop/mobile Headquarters density and execute a real
 *          source-owned work command without leaving its operating workspace.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/headquarters-operating-workspace.browser.spec.js
 * COLLABORATION / OWNERSHIP: Existing browser runner/fixture, App, Headquarters,
 *                            canonical Operations registry and scoped verifier.
 * CERTIFICATION / UPDATE DATE: 2026-11-15
 * CHANGELOG: v1.7.0-COMPUTED-HQ-COLUMN-CERT proves desktop navigation can collapse/reopen while preserving independent scroll rails and the closed-by-default mobile menu.
 * CHANGELOG: v1.5.0-BOUNDED-HQ-SCROLL-CERT verifies viewport-bounded workspace scrolling, a separately scrollable desktop sidebar, a closed-by-default mobile menu, and collapsed nested groups, while retaining independent columns and source-owned lifecycle gates.
 * CHANGELOG: v1.4.0-INDEPENDENT-HQ-COLUMN-CERT verifies independently stacked work/performance, organisation/department, and calendar/report/action columns while retaining responsive widths, honest source states, and authenticated lifecycle gates.
 * CHANGELOG: v1.3.0-RESPONSIVE-HQ-GRID-CERT certifies desktop 12-column, tablet two-column and mobile single-column home composition, honest source states, work priority, and overflow at 1440, 1024 and 390 pixels. Existing authenticated source-owned create/read/complete gates remain.
 * CHANGELOG: v1.2.0-ENTERPRISE-MOVABLE-AI-WORK-CERT verifies the preserved corporate square identity, movable AI
 * companion, retained workspace drafts and responsive visual hierarchy while
 * preserving all real Operations commands and durable readback gates.
 * CHANGELOG: v1.1.0-OFFICIAL-SQUARE-BRAND-WORK-CERT verifies the approved vivid square
 * asset and 64px header mark, with unchanged source-command and tenant gates.
 * CHANGELOG: v1.0.2-RESTORED-FOUNDER-SUPPLIED-LOGO-CERT requires the selected square navy logo
 * and preserves every source-work and customer Legal capacity assertion.
 * CHANGELOG: v1.0.1-FOUNDER-SQUARE-LOGO-CERT requires the supplied square navy logo and retains all source-owned command, layout and durable readback gates.
 *            v1.0.0-DISPOSABLE-HEADQUARTERS-OPERATING-LOOP proves real UI create,
 *            idempotent replay, Headquarters record selection/completion,
 *            fresh aggregate readback, foreign-tenant denial and responsive UI.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic fixture identities only; no credentials,
 *                             bearer values or personal records enter evidence.
 * TENANT BOUNDARY: One UUID-owned disposable tenant; foreign scope is denied.
 * AUTHORITY BOUNDARY: Fixture session evidence is never human Founder/MFA acceptance.
 * FINANCIAL AUTHORITY BOUNDARY: No financial command; Kennel EOS exclusively.
 */
import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { expect, test } from '@playwright/test';

const state = JSON.parse(fs.readFileSync(process.env.BROWSER_CERT_STATE, 'utf8'));
if (!/^wilsy_l8_8m_r3_[a-zA-Z0-9_-]+$/.test(state.database_name || '')) {
  throw new Error('HEADQUARTERS_DISPOSABLE_DATABASE_REQUIRED');
}
const evidence = process.env.WILSY_HEADQUARTERS_EVIDENCE_DIR;
if (!evidence) throw new Error('HEADQUARTERS_EVIDENCE_DIRECTORY_REQUIRED');
fs.mkdirSync(evidence, { recursive: true, mode: 0o700 });

for (const viewport of [{ width: 1440, height: 900 }, { width: 1760, height: 1000 }, { width: 1024, height: 900 }, { width: 390, height: 844 }]) {
  test(`Headquarters executes real in-view work at ${viewport.width}px`, async ({ browser }) => {
    const actor = state.actors.tenant_owner;
    const context = await browser.newContext({ viewport, timezoneId: 'Africa/Johannesburg' });
    const page = await context.newPage();
    const errors = [];
    const network = [];
    page.on('pageerror', (error) => errors.push(error.name));
    page.on('response', (response) => {
      const url = new URL(response.url());
      if (/^\/api\/(my-work|attention\/actions|hr\/workforce|tenant-modules\/operations)/.test(url.pathname)) {
        network.push({ path: url.pathname, method: response.request().method(), status: response.status() });
      }
    });
    const headers = { Authorization: `Bearer ${actor.access_token}`, 'X-Tenant-ID': state.tenant_id };
    const title = `Headquarters source work hq-browser-${randomUUID()}`;
    const sourcePath = '/api/tenant-modules/operations/workspace/work-items';
    const openHeadquarters = async () => {
      const menu = page.getByRole('button', { name: 'WILSY Headquarters', exact: true });
      if (await menu.isVisible()) await menu.click();
      await page.getByRole('navigation', { name: 'Headquarters navigation' })
        .getByRole('button', { name: 'Headquarters', exact: true }).click();
    };
    try {
      await page.addInitScript(({ token }) => {
        localStorage.setItem('wilsy_auth_token', token);
        localStorage.setItem('token', token);
      }, { token: actor.access_token });
      await page.goto('/');
      await expect(page.getByRole('heading', { name: 'WILSY Headquarters', exact: true })).toBeVisible();
      await expect(page.locator('.hq-work')).toBeVisible();
      await expect(page.locator('.hq-work')).not.toContainText('Loading the authorized My Work projection');
      await expect(page.getByText('Performance source unavailable')).toBeVisible();
      await expect(page.getByText('Reporting source unavailable')).toBeVisible();
      await expect(page.locator('.hq-department-pending[aria-disabled="true"]')).toHaveCount(5);
      await expect(page.locator('.hq-department-grid > *')).toHaveCount(6);
      await expect(page.locator('.hq-kpi-unavailable')).not.toHaveAttribute('role', 'button');
      const navigation = page.getByRole('navigation', { name: 'Headquarters navigation' });
      expect(await navigation.locator('.hq-nav-group-toggle').evaluateAll((buttons) =>
        buttons.every((button) => button.getAttribute('aria-expanded') === 'false'))).toBe(true);
      if (viewport.width < 768) {
        await expect(page.getByRole('button', { name: 'WILSY Headquarters' })).toHaveAttribute('aria-expanded', 'false');
        await page.getByRole('button', { name: 'WILSY Headquarters' }).click();
        await expect(navigation).toBeVisible();
      }
      const groupToggles = await navigation.locator('.hq-nav-group-toggle').all();
      for (const toggle of groupToggles) await toggle.click();
      const scrollProof = await page.evaluate((mobile) => {
        const content = document.querySelector('.hq-content');
        const sideRail = document.querySelector('.hq-sidebar');
        const scrollable = mobile ? document.querySelector('.hq-nav') : sideRail;
        const contentCanScroll = content.scrollHeight > content.clientHeight;
        const navigationCanScroll = scrollable.scrollHeight > scrollable.clientHeight;
        if (contentCanScroll) content.scrollTop = content.scrollHeight;
        if (navigationCanScroll) scrollable.scrollTop = scrollable.scrollHeight;
        const result = {
          contentOverflowY: getComputedStyle(content).overflowY,
          navigationOverflowY: getComputedStyle(scrollable).overflowY,
          contentCanScroll,
          navigationCanScroll,
          contentScrollTop: content.scrollTop,
          navigationScrollTop: scrollable.scrollTop,
        };
        content.scrollTop = 0;
        scrollable.scrollTop = 0;
        return result;
      }, viewport.width < 768);
      expect(scrollProof.contentOverflowY).toBe('auto');
      expect(scrollProof.navigationOverflowY).toBe('auto');
      expect(scrollProof.contentCanScroll).toBe(true);
      expect(scrollProof.navigationCanScroll).toBe(true);
      expect(scrollProof.contentScrollTop).toBeGreaterThan(0);
      expect(scrollProof.navigationScrollTop).toBeGreaterThan(0);
      for (const toggle of groupToggles) await toggle.click();
      if (viewport.width < 768) await page.getByRole('button', { name: 'WILSY Headquarters' }).click();
      else {
        await page.getByRole('button', { name: 'Collapse Headquarters navigation' }).click();
        await expect(navigation).toBeHidden();
        await page.getByRole('button', { name: 'Open Headquarters navigation' }).click();
        await expect(navigation).toBeVisible();
      }
      const layout = await page.evaluate(() => {
        const rect = (selector) => {
          const { x, y, width, height } = document.querySelector(selector).getBoundingClientRect();
          return { x, y, width, height };
        };
        return {
          columns: getComputedStyle(document.querySelector('.hq-overview')).gridTemplateColumns.split(' ').length,
          viewport: document.documentElement.clientWidth,
          document: document.documentElement.scrollWidth,
          hero: rect('.hq-hero'), glance: rect('.hq-glance'), kpis: rect('.hq-kpis'),
          workColumn: rect('[data-hq-column="work"]'),
          organisationColumn: rect('[data-hq-column="organisation"]'),
          reportingColumn: rect('[data-hq-column="reporting"]'),
          work: rect('.hq-work'), organisation: rect('.hq-organisation'),
          reporting: rect('.hq-main-reporting'), performance: rect('.hq-performance'),
          departments: rect('.hq-departments'), strategy: rect('.hq-strategy'),
          release: rect('.hq-release-panel'), actions: rect('.hq-quick-actions-panel'),
        };
      });
      expect(layout.document).toBeLessThanOrEqual(layout.viewport + 1);
      if (viewport.width >= 1200) {
        expect(layout.columns).toBe(12);
        expect(Math.abs(layout.hero.y - layout.glance.y)).toBeLessThanOrEqual(1);
        expect(layout.kpis.width).toBeGreaterThan(layout.hero.width + 10);
        expect(Math.abs(layout.workColumn.y - layout.organisationColumn.y)).toBeLessThanOrEqual(1);
        expect(Math.abs(layout.workColumn.y - layout.reportingColumn.y)).toBeLessThanOrEqual(1);
        expect(layout.workColumn.x).toBeLessThan(layout.organisationColumn.x);
        expect(layout.organisationColumn.x).toBeLessThan(layout.reportingColumn.x);
        expect(layout.workColumn.width).toBeGreaterThan(layout.organisationColumn.width);
        expect(layout.organisationColumn.width).toBeGreaterThan(layout.reportingColumn.width);
        expect(layout.workColumn.x + layout.workColumn.width).toBeLessThanOrEqual(layout.organisationColumn.x + 1);
        expect(layout.organisationColumn.x + layout.organisationColumn.width).toBeLessThanOrEqual(layout.reportingColumn.x + 1);
        expect(layout.performance.x).toBe(layout.workColumn.x);
        expect(layout.performance.y).toBeGreaterThanOrEqual(layout.work.y + layout.work.height);
        expect(layout.departments.x).toBe(layout.organisationColumn.x);
        expect(layout.departments.y).toBeGreaterThanOrEqual(layout.organisation.y + layout.organisation.height);
        expect(layout.strategy.x).toBe(layout.organisationColumn.x);
        expect(layout.strategy.y).toBeGreaterThanOrEqual(layout.departments.y + layout.departments.height);
        expect(layout.reporting.x).toBe(layout.reportingColumn.x);
        expect(layout.release.y).toBeGreaterThanOrEqual(layout.reporting.y + layout.reporting.height);
        expect(layout.actions.y).toBeGreaterThanOrEqual(layout.release.y + layout.release.height);
      } else if (viewport.width >= 768) {
        expect(layout.columns).toBe(2);
        expect(layout.work.x).toBeLessThan(layout.organisation.x);
        expect(Math.abs(layout.work.y - layout.organisation.y)).toBeLessThanOrEqual(1);
        expect(layout.performance.x).toBe(layout.work.x);
        expect(layout.departments.x).toBe(layout.organisationColumn.x);
        expect(layout.strategy.x).toBe(layout.organisationColumn.x);
        expect(layout.performance.y).toBeGreaterThanOrEqual(layout.work.y + layout.work.height);
        expect(layout.departments.y).toBeGreaterThanOrEqual(layout.organisation.y + layout.organisation.height);
        expect(layout.reportingColumn.y).toBeGreaterThan(layout.performance.y);
      } else {
        expect(layout.columns).toBe(1);
        expect(layout.hero.y).toBeLessThan(layout.work.y);
        expect(layout.work.y).toBeLessThan(layout.kpis.y);
        expect(layout.kpis.y).toBeLessThan(layout.glance.y);
      }
      const brand = page.getByAltText('WILSY OS logo');
      await expect(brand).toHaveAttribute('src', '/brand/wilsy-os-official.png');
      const brandBox = await brand.boundingBox(); expect(brandBox.width).toBe(viewport.width >= 768 ? 64 : 56); expect(brandBox.height).toBe(viewport.width >= 768 ? 64 : 56);
      expect(await brand.evaluate((image) => image.complete && image.naturalWidth > 0)).toBe(true);
      expect(await page.locator('[data-eos-controller-product-navigation]').evaluateAll((nodes) =>
        nodes.every((node) => Boolean(node.closest('.hq-sidebar'))))).toBe(true);
      const companion = page.locator('[data-wilsy-intelligence-dock]');
      const move = page.getByRole('button', { name: 'Move WILSY OS AI', exact: true });
      const originalAI = await companion.boundingBox();
      await move.focus(); await page.keyboard.press('ArrowLeft');
      const movedAI = await companion.boundingBox(); expect(movedAI.x).toBeLessThan(originalAI.x);
      await page.keyboard.press('Home');
      const handle = await move.boundingBox();
      await page.mouse.move(handle.x + handle.width / 2, handle.y + handle.height / 2);
      await page.mouse.down(); await page.mouse.move(42, 130, { steps: 10 }); await page.mouse.up();
      const draggedAI = await companion.boundingBox();
      expect(draggedAI.x).toBeGreaterThanOrEqual(12); expect(draggedAI.y).toBeGreaterThanOrEqual(84);
      expect(draggedAI.y).toBeLessThan(originalAI.y);
      await move.focus(); await page.keyboard.press('Home');
      await page.getByTitle('Minimize AI launcher', { exact: true }).click();
      await expect(companion).toHaveAttribute('data-ai-layout', 'MINIMIZED');
      const miniAI = await companion.boundingBox(); expect(miniAI.width).toBeLessThan(originalAI.width);
      await page.locator('.hq-quick-actions').getByRole('button', { name: 'Create work' }).click();
      const operations = page.getByRole('main', { name: 'Operations OS' });
      await expect(operations).toBeVisible();
      await operations.getByRole('textbox', { name: 'Action title' }).fill(title);
      await operations.getByRole('combobox', { name: 'Priority' }).selectOption('HIGH');
      const [created] = await Promise.all([
        page.waitForResponse((response) => new URL(response.url()).pathname === sourcePath && response.request().method() === 'POST'),
        operations.getByRole('button', { name: 'Create action', exact: true }).click(),
      ]);
      expect(created.status()).toBe(201);
      const item = await created.json();
      const command = created.request().postDataJSON();
      const key = (await created.request().allHeaders())['idempotency-key'];
      expect(key).toMatch(/^[a-f0-9-]{36}$/i);
      const replay = await context.request.post(sourcePath, { headers: { ...headers, 'Idempotency-Key': key }, data: command });
      expect(replay.status()).toBe(201);
      expect((await replay.json()).work_item_id).toBe(item.work_item_id);
      const divergent = await context.request.post(sourcePath, { headers: { ...headers, 'Idempotency-Key': key }, data: { ...command, title: title + ' divergent' } });
      expect(divergent.status()).toBe(409);
      await openHeadquarters();
      const row = page.getByRole('button', { name: 'Open authorized record: ' + title, exact: true });
      await expect(row).toBeVisible();
      await page.getByRole('button', { name: 'Open workspace navigation', exact: true }).click();
      const sourceSearch = page.getByRole('searchbox', { name: 'Search headquarters work' });
      await expect(sourceSearch).toBeFocused();
      await sourceSearch.fill('No matching authorized record in this fixture');
      await expect(row).toHaveCount(0);
      await expect(page.getByText('No work matches these filters.')).toBeVisible();
      await sourceSearch.fill('');
      await expect(row).toBeVisible();
      const before = await context.request.get('/api/my-work', { headers });
      expect(before.status()).toBe(200);
      const beforeProjection = await before.json();
      expect(beforeProjection.items.some((work) => work.source_key === 'OPERATIONS:' + item.work_item_id)).toBe(true);
      const dimensions = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, document: document.documentElement.scrollWidth }));
      expect(dimensions.document).toBeLessThanOrEqual(dimensions.viewport + 1);
      if (viewport.width === 1440) {
        const queue = await page.locator('.hq-work').boundingBox();
        expect(queue.y).toBeLessThan(400);
        expect(queue.y + queue.height).toBeLessThan(viewport.height);
      }
      await expect(page.locator('.hq-glance h2')).toHaveCSS('color', 'rgb(16, 30, 66)');
      await expect(page.locator('.hq-kpi strong').first()).toHaveCSS('color', 'rgb(16, 30, 66)');
      await expect(row.locator('strong')).toHaveCSS('color', 'rgb(16, 30, 66)');
      const dock = page.getByTitle('Open Wilsy OS Intelligence Dock', { exact: true });
      await expect(dock).toBeVisible();
      const dockBox = await dock.boundingBox();
      const refreshBox = await page.getByRole('button', { name: 'Refresh snapshot', exact: true }).boundingBox();
      const overlapWidth = Math.max(0, Math.min(dockBox.x + dockBox.width, refreshBox.x + refreshBox.width) - Math.max(dockBox.x, refreshBox.x));
      const overlapHeight = Math.max(0, Math.min(dockBox.y + dockBox.height, refreshBox.y + refreshBox.height) - Math.max(dockBox.y, refreshBox.y));
      expect(overlapWidth * overlapHeight).toBe(0);
      await page.screenshot({ path: path.join(evidence, `headquarters-${viewport.width}.png`) });
      await row.click();
      await expect(page.getByRole('region', { name: 'Selected work record' })).toBeVisible();
      await page.getByLabel('Completion note for ' + title).fill('Headquarters source-owned completion evidence');
      const retainedUrl = page.url();
      await page.getByTitle('Open Wilsy OS Intelligence Dock', { exact: true }).click();
      const aiPanel = page.getByRole('region', { name: 'WILSY OS AI companion', exact: true });
      await expect(aiPanel).toBeVisible();
      await expect(aiPanel.getByAltText('Wilsy AI neural core')).toHaveAttribute('src', '/brand/wilsy-ai-emblem.svg');
      await page.getByPlaceholder('Ask Wilsy OS…', { exact: true }).fill('Keep my unsent AI draft');
      await page.screenshot({ path: path.join(evidence, `headquarters-${viewport.width}-ai-companion.png`) });
      await page.getByTitle('Minimize dock', { exact: true }).click();
      expect(page.url()).toBe(retainedUrl);
      await expect(page.getByRole('region', { name: 'Selected work record' })).toBeVisible();
      await expect(page.getByLabel('Completion note for ' + title)).toHaveValue('Headquarters source-owned completion evidence');
      await page.getByTitle('Open Wilsy OS Intelligence Dock', { exact: true }).click();
      await expect(page.getByPlaceholder('Ask Wilsy OS…', { exact: true })).toHaveValue('Keep my unsent AI draft');
      await aiPanel.press('Escape');
      await expect(companion).toHaveAttribute('data-ai-layout', 'MINIMIZED');
      const completeControl = page.getByRole('button', { name: 'Complete work', exact: true });
      const completeBox = await completeControl.boundingBox();
      expect(completeBox.y).toBeGreaterThanOrEqual(64);
      expect(completeBox.y + completeBox.height).toBeLessThanOrEqual(viewport.height);
      await page.screenshot({ path: path.join(evidence, `headquarters-${viewport.width}-record.png`) });
      await page.getByRole('button', { name: 'Complete work', exact: true }).click();
      await expect(page.getByText('Completion confirmed by EOS and a fresh authorized work readback.')).toBeVisible();
      await expect(row).toHaveCount(0);
      const after = await context.request.get('/api/my-work', { headers });
      expect(after.status()).toBe(200);
      const afterProjection = await after.json();
      expect(afterProjection.tenant_id).toBe(state.tenant_id);
      expect(afterProjection.principal_id).toBe(actor.principal_id);
      expect(afterProjection.items.some((work) => work.work_item_id === item.work_item_id)).toBe(false);
      expect(afterProjection.summary.active_count).toBe(beforeProjection.summary.active_count - 1);
      const completionReplay = await context.request.post(sourcePath + '/' + item.work_item_id + '/complete', { headers, data: { completion_note: 'Headquarters source-owned completion evidence' } });
      expect(completionReplay.status()).toBe(200);
      expect((await completionReplay.json()).status).toBe('COMPLETED');
      const foreign = await context.request.get('/api/my-work', { headers: { ...headers, 'X-Tenant-ID': state.foreign_tenant_id } });
      expect(foreign.status()).toBe(403);
      expect(await foreign.text()).not.toContain(title);
      await page.getByRole('button', { name: 'WILSY home', exact: true }).click();
      await expect(page.getByRole('heading', { name: 'WILSY Headquarters', exact: true })).toBeVisible();
      const menu = page.getByRole('button', { name: 'WILSY Headquarters', exact: true });
      if (await menu.isVisible()) await menu.click();
      await expect(page.getByRole('navigation', { name: 'Available WILSY OS products' })).toBeVisible();
      if (await menu.isVisible()) await menu.click();
      expect(errors).toEqual([]);
      await page.screenshot({ path: path.join(evidence, `headquarters-${viewport.width}-readback.png`) });
      fs.writeFileSync(path.join(evidence, `headquarters-${viewport.width}-network.json`), JSON.stringify({ viewport, fixture: 'DISPOSABLE_SYNTHETIC_SESSION', founderMfaAcceptance: false, network, browserErrors: errors }, null, 2));
    } finally { await context.close(); }
  });
}

test('explicit Headquarters preserves an authenticated Legal capacity without changing its source authority', async ({ browser }) => {
  const actor = state.actors.partner;
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  try {
    await page.addInitScript(({ token }) => {
      localStorage.setItem('wilsy_auth_token', token);
      localStorage.setItem('token', token);
    }, { token: actor.access_token });
    await page.goto('/headquarters');
    await expect(page.getByRole('heading', { name: 'WILSY Headquarters', exact: true })).toBeVisible();
    await expect(page.getByRole('navigation', { name: 'Available WILSY OS products' })).toBeVisible();
    await expect(page.locator('[data-wilsy-module-entry="LEGAL_OS"]')).toBeVisible();
    const bootstrap = await context.request.get('/api/auth/workspace-bootstrap', {
      headers: { Authorization: `Bearer ${actor.access_token}`, 'X-Tenant-ID': state.tenant_id },
    });
    expect(bootstrap.status()).toBe(200);
    expect((await bootstrap.json()).workspace.workspaceId).toBe('LEGAL_PRACTICE');
  } finally { await context.close(); }
});

// ARTIFACT: headquarters-operating-workspace.browser.spec.js
// VERSION: v1.7.0-COMPUTED-HQ-COLUMN-CERT
// AUTHORITY BOUNDARY: Test-only authenticated UI evidence, not Founder acceptance.
// TENANT POSTURE: Exact disposable synthetic tenant; foreign query denied.
// FAIL-CLOSED POSTURE: Any missing command, readback, image or layout proof fails.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
