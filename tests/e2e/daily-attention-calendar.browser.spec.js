/**
 * TITLE: WILSY OS Authenticated Daily Attention Calendar Browser Certificate
 * VERSION: v1.4.0-AUTHORISED-FEED-PERSISTENCE-READBACK
 * AUTHORITY: Repository-governed disposable browser fixture only.
 * EPITOME: Verify real EOS work creation, replay, tenant denial, calendar
 * navigation, window bounds, dismissal and persisted source-owned completion.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/daily-attention-calendar.browser.spec.js
 * COLLABORATION / OWNERSHIP: browser_cert_fixture.py, run-browser-cert.mjs,
 * App.jsx, WilsyDailyAttentionCentre, WilsyWorkDeadlineCalendar and My Work.
 * CERTIFICATION / UPDATE DATE: 2026-11-09.
 * CHANGELOG: v1.4.0-AUTHORISED-FEED-PERSISTENCE-READBACK adds real
 *          authenticated attention feed/counts/calendar/coverage reads,
 *          foreign scope rejection and post-completion count reconciliation.
 *          v1.3.0-DAILY-ATTENTION-FIRST-DURABLE-WORK begins at the
 *          global authenticated bell and exercises Operations handoff
 *          before source-created durable work, calendar and EOS completion.
 *          v1.2.0-REAL-UI-SOURCE-ENTRY-BADGE-RECONCILIATION creates source work using
 *          the live Operations action form reached from My Work, then certifies
 *          browser idempotent replay, calendar selection, EOS-owned completion,
 *          durable registry rehydrate, aggregate counts and current global
 *          badge refresh. No dummy UI action or API-only creation substitutes.
 *          v1.1.0-DURABLE-AGGREGATE-COUNT-RECONCILIATION requires the just-created
 *          Operations item in the exact tenant/principal aggregate snapshot,
 *          then demands current EOS active and source counts each decrement by
 *          exactly one after source-owned completion and durable rehydration.
 *          v1.0.0-DISPOSABLE-CALENDAR-SOURCE-COMMAND-CERT adds desktop and
 * narrow-view acceptance using the existing synthetic Tenant Owner actor.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic fixture sessions only. No real MFA,
 * user password, OTP, production credential or human session is consumed.
 * TENANT BOUNDARY: UUID-isolated loopback database; exact synthetic tenant.
 * AUTHORITY BOUNDARY: A preissued fixture session proves only synthetic
 * authenticated request behavior. It is never proof of human-completed MFA.
 * TRANSACTION BOUNDARY: EOS source services own persistence and replay;
 * browser actions cannot acknowledge notifications or complete work locally.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import fs from 'node:fs';
import { randomUUID } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { expect, test } from '@playwright/test';

const statePath = process.env.BROWSER_CERT_STATE;
if (!statePath) throw new Error('BROWSER_CERT_STATE_REQUIRED');
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
if (!/^wilsy_l8_8m_r3_[a-zA-Z0-9_-]+$/.test(state.database_name || '')) {
  throw new Error('BROWSER_CERT_DISPOSABLE_DATABASE_REQUIRED');
}

for (const viewport of [{width: 1440, height: 1000}, {width: 390, height: 844}]) {
  test(`daily attention calendar executes source-owned work at ${viewport.width}px`, async ({browser}) => {
    const actor = state.actors.tenant_owner;
    const context = await browser.newContext({viewport, timezoneId: 'America/Los_Angeles'});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.name));
    const headers = {'Authorization': `Bearer ${actor.access_token}`, 'X-Tenant-ID': state.tenant_id};
    try {
      await page.addInitScript(({token}) => {
        localStorage.setItem('wilsy_auth_token', token);
        localStorage.setItem('token', token);
      }, {token: actor.access_token});
      const bootstrap = page.waitForResponse(response => (
        new URL(response.url()).pathname === '/api/auth/workspace-bootstrap'
        && response.request().method() === 'GET'
      ));
      await page.goto('/headquarters');
      expect((await bootstrap).status()).toBe(200);
      // The first productive action begins at the authenticated global bell,
      // including when EOS has not yet returned an active Operations item.
      const entryBell = page.getByRole('button', {name: /^Open daily attention/});
      await expect(entryBell).toBeVisible();
      await entryBell.click();
      const entryPanel = page.getByRole('dialog', {name: 'Daily attention centre'});
      await expect(entryPanel).toBeVisible();
      await expect(entryPanel.getByRole('button', {name: 'Manage Operations', exact: true})).toBeVisible();

      const title = `Calendar source work calendar-browser-${randomUUID()}`;
      const due = await page.evaluate(() => {
        const today = new Date();
        today.setHours(12, 0, 0, 0);
        const pad = value => String(value).padStart(2, '0');
        return {
          iso: today.toISOString(),
          local: `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}T${pad(today.getHours())}:${pad(today.getMinutes())}`,
        };
      });
      const path = '/api/tenant-modules/operations/workspace/work-items';

      // Real workforce-facing creation UI. The click routes into the existing
      // canonical Operations source, whose own IAM and entitlement gate owns
      // the command and its durable Mongo transaction.
      await entryPanel.getByRole('button', {name: 'Manage Operations', exact: true}).click();
      await expect(entryPanel).toHaveCount(0);
      const operations = page.getByRole('main', {name: 'Operations OS'});
      await expect(operations).toBeVisible();
      await operations.getByRole('textbox', {name: 'Action title'}).fill(title);
      await operations.getByRole('combobox', {name: 'Priority'}).selectOption('HIGH');
      await operations.getByLabel('Due date and time').fill(due.local);
      const [created] = await Promise.all([
        page.waitForResponse(response => (
          new URL(response.url()).pathname === path
          && response.request().method() === 'POST'
        )),
        operations.getByRole('button', {name: 'Create action'}).click(),
      ]);
      expect(created.status()).toBe(201);
      const command = created.request().postDataJSON();
      expect(command).toEqual({
        title, description: '', kind: 'TASK', priority: 'HIGH', due_at: due.iso,
      });
      const key = (await created.request().allHeaders())['idempotency-key'];
      expect(key).toMatch(/^[0-9a-f]{8}-[0-9a-f-]{27,}$/i);
      const work = await created.json();
      await expect(operations.getByText(title, {exact: true})).toBeVisible();
      const replay = await context.request.post(path, {
        headers: {...headers, 'Idempotency-Key': key}, data: command,
      });
      expect(replay.status()).toBe(201);
      expect((await replay.json()).work_item_id).toBe(work.work_item_id);
      const divergent = await context.request.post(path, {
        headers: {...headers, 'Idempotency-Key': key}, data: {...command, title: title + ' divergent'},
      });
      expect(divergent.status()).toBe(409);
      const foreign = await context.request.get('/api/my-work', {
        headers: {...headers, 'X-Tenant-ID': state.foreign_tenant_id},
      });
      expect(foreign.status()).toBe(403);
      expect(await foreign.text()).not.toContain(title);

      // Current EOS aggregate must independently prove that source creation is
      // visible to this authenticated exact tenant and selected capacity.
      const beforeAggregateResponse = await context.request.get('/api/my-work', {headers});
      expect(beforeAggregateResponse.status()).toBe(200);
      const beforeAggregate = await beforeAggregateResponse.json();
      expect(beforeAggregate.schema).toBe('WILSY-OS-UNIFIED-MY-WORK/V1');
      expect(beforeAggregate.tenant_id).toBe(state.tenant_id);
      expect(beforeAggregate.principal_id).toBe(actor.principal_id);
      expect(beforeAggregate.sources_included).toContain('OPERATIONS');
      expect(beforeAggregate.items.filter(item => (
        item.source_key === 'OPERATIONS:' + work.work_item_id
        && item.title === title
      ))).toHaveLength(1);
      expect(beforeAggregate.summary.source_counts.OPERATIONS).toBeGreaterThanOrEqual(1);

      const attentionFeedResponse = await context.request.get('/api/attention/feed?limit=100', {headers});
      expect(attentionFeedResponse.status()).toBe(200);
      const attentionFeed = await attentionFeedResponse.json();
      expect(attentionFeed.schema).toBe('WILSY-OS-ATTENTION-FEED/V1');
      expect(attentionFeed.tenantId).toBe(state.tenant_id);
      expect(attentionFeed.principalId).toBe(actor.principal_id);
      expect(attentionFeed.counts.active).toBe(beforeAggregate.summary.active_count);
      expect(attentionFeed.coverage.admittedSources).toContain('OPERATIONS');
      expect(attentionFeed.coverage.completeEnterpriseCoverage).toBe(false);
      expect(attentionFeed.items.some(item => (
        item.id === 'OPERATIONS:' + work.work_item_id
        && item.title === title
        && item.actionHints.length === 1
        && item.actionHints[0] === 'OPEN'
        && item.authzScope === 'SOURCE_SERVICE_ONLY'
      ))).toBe(true);

      const attentionCounts = await context.request.get('/api/attention/counts', {headers});
      expect(attentionCounts.status()).toBe(200);
      expect((await attentionCounts.json()).counts.active).toBe(attentionFeed.counts.active);

      const attentionCoverage = await context.request.get('/api/attention/sources/health', {headers});
      expect(attentionCoverage.status()).toBe(200);
      expect((await attentionCoverage.json()).sources.some(source => (
        source.moduleId === 'OPERATIONS' && source.state === 'ok'
      ))).toBe(true);

      const start = new Date(new Date(due.iso).getTime() - 86400000).toISOString();
      const end = new Date(new Date(due.iso).getTime() + 86400000).toISOString();
      const calendarResponse = await context.request.get(
        '/api/attention/calendar?' + new URLSearchParams({from: start, to: end}),
        {headers},
      );
      expect(calendarResponse.status()).toBe(200);
      expect((await calendarResponse.json()).items.some(item => (
        item.id === 'OPERATIONS:' + work.work_item_id
      ))).toBe(true);

      const unauthorisedSource = await context.request.get('/api/attention/feed?sources=PEOPLE', {headers});
      expect(unauthorisedSource.status()).toBe(403);
      expect(await unauthorisedSource.text()).not.toContain(title);
      const foreignAttention = await context.request.get('/api/attention/feed', {
        headers: {...headers, 'X-Tenant-ID': state.foreign_tenant_id},
      });
      expect(foreignAttention.status()).toBe(403);
      expect(await foreignAttention.text()).not.toContain(title);

      await page.goto('/headquarters');
      const bell = page.getByRole('button', {name: /^Open daily attention/});
      await expect(bell).toBeVisible();
      await bell.click();
      const panel = page.getByRole('dialog', {name: 'Daily attention centre'});
      await expect(panel).toBeVisible();
      await panel.getByRole('tab', {name: 'Calendar', exact: true}).click();
      const dates = panel.getByRole('group', {name: 'Choose work deadline date'});
      await expect(dates).toBeVisible();
      const agendaItem = panel.getByRole('article').filter({hasText: title});
      await expect(agendaItem).toBeVisible();
      const selected = dates.locator('button[aria-pressed="true"]');
      await selected.focus();
      await page.keyboard.press('ArrowRight');
      await expect(dates.locator('button[aria-pressed="true"]')).toBeFocused();
      await page.keyboard.press('ArrowLeft');
      await expect(agendaItem).toBeVisible();
      await panel.getByRole('button', {name: 'Next month'}).click();
      await panel.getByRole('button', {name: 'Today', exact: true}).click();
      await expect(agendaItem).toBeVisible();

      await panel.getByRole('button', {name: 'Float daily attention panel'}).click();
      await expect(panel).toHaveAttribute('data-floating', 'true');
      const mover = panel.getByRole('button', {name: 'Move daily attention panel with pointer or arrow keys'});
      await mover.focus();
      await page.keyboard.press('Shift+ArrowRight');
      await page.keyboard.press('ArrowDown');
      const bounds = await panel.boundingBox();
      expect(bounds.x).toBeGreaterThanOrEqual(8);
      expect(bounds.y).toBeGreaterThanOrEqual(8);
      expect(bounds.x + bounds.width).toBeLessThanOrEqual(viewport.width);
      expect(bounds.y + bounds.height).toBeLessThanOrEqual(viewport.height);
      await panel.getByRole('button', {name: 'Dock daily attention panel'}).click();
      await expect(panel).toHaveAttribute('data-floating', 'false');
      await panel.getByRole('button', {name: 'Close calendar and return to work list'}).click();
      await expect(panel.getByRole('tab', {name: 'Work list'})).toHaveAttribute('aria-selected', 'true');
      await panel.getByRole('tab', {name: 'Calendar', exact: true}).click();
      await page.keyboard.press('Escape');
      await expect(panel).toBeVisible();
      await expect(panel.getByRole('tab', {name: 'Work list'})).toHaveAttribute('aria-selected', 'true');
      await page.keyboard.press('Escape');
      await expect(panel).toHaveCount(0);

      await bell.click();
      await panel.getByRole('tab', {name: 'Calendar', exact: true}).click();
      await agendaItem.getByRole('button', {name: 'Review and complete in My Work'}).click();
      await expect(panel).toHaveCount(0);
      const workItem = page.getByRole('article').filter({hasText: title});
      await expect(workItem).toBeFocused();
      await workItem.getByRole('textbox', {name: `Completion note for ${title}`}).fill('Source-owned calendar completion evidence');
      const completedResponse = page.waitForResponse(response => (
        new URL(response.url()).pathname === `${path}/${work.work_item_id}/complete`
        && response.request().method() === 'POST'
      ));
      await workItem.getByRole('button', {name: 'Complete', exact: true}).click();
      const completed = await completedResponse;
      expect(completed.status()).toBe(200);
      expect((await completed.json()).status).toBe('COMPLETED');
      await expect(workItem).toHaveCount(0);
      const readback = await context.request.get('/api/tenant-modules/operations/workspace', {headers});
      expect(readback.status()).toBe(200);
      // Workspace reads expose active work only. Independently rehydrate the
      // completed record through the canonical Python registry in the same
      // fixture-owned database; absence from an active queue is not completion.
      expect((await readback.json()).items.some(item => item.work_item_id === work.work_item_id)).toBe(false);
      let durableEvidence;
      try {
        durableEvidence = execFileSync(process.env.BROWSER_CERT_PYTHON || 'python', ['-c', [
          'import json, os, sys',
          'sys.path.insert(0, os.path.join(os.getcwd(), "tests", "e2e"))',
          'from browser_cert_fixture import _uri, _owned_database',
          'from pymongo import MongoClient',
          'from tools.eos.workspaces.persistence.tenant_module_work_registry import TenantModuleWorkRegistry',
          'command = json.load(sys.stdin)',
          'with MongoClient(_uri(), serverSelectionTimeoutMS=5000) as client:',
          '    database = _owned_database(client)',
          '    with client.start_session() as session:',
          '        session.start_transaction()',
          '        try:',
          '            item = TenantModuleWorkRegistry(database["tenant_operations_work_items"]).get(tenant_id=command["tenant_id"], work_item_id=command["work_item_id"], session=session)',
          '            assert item.status.value == "COMPLETED"',
          '            assert item.completion_note == "Source-owned calendar completion evidence"',
          '        finally:',
          '            session.abort_transaction()',
          'print("CALENDAR_SOURCE_COMPLETION_REHYDRATED")',
        ].join('\n')], {
          input: JSON.stringify({tenant_id: state.tenant_id, work_item_id: work.work_item_id}),
          encoding: 'utf8', timeout: 15000, maxBuffer: 4096,
          stdio: ['pipe', 'pipe', 'pipe'],
        });
      } catch {
        throw new Error('CALENDAR_SOURCE_COMPLETION_READBACK_FAILED');
      }
      expect(durableEvidence.trim()).toBe('CALENDAR_SOURCE_COMPLETION_REHYDRATED');

      // Re-read EOS rather than believing optimistic browser removal; a
      // successful source command must reconcile both global and source counts.
      const afterAggregateResponse = await context.request.get('/api/my-work', {headers});
      expect(afterAggregateResponse.status()).toBe(200);
      const afterAggregate = await afterAggregateResponse.json();
      expect(afterAggregate.tenant_id).toBe(state.tenant_id);
      expect(afterAggregate.principal_id).toBe(actor.principal_id);
      expect(afterAggregate.sources_included).toContain('OPERATIONS');
      expect(afterAggregate.items.some(item => (
        item.source_key === 'OPERATIONS:' + work.work_item_id
      ))).toBe(false);
      expect(afterAggregate.summary.active_count).toBe(
        beforeAggregate.summary.active_count - 1
      );
      expect(afterAggregate.summary.source_counts.OPERATIONS).toBe(
        beforeAggregate.summary.source_counts.OPERATIONS - 1
      );

      const afterAttentionResponse = await context.request.get('/api/attention/feed?limit=100', {headers});
      expect(afterAttentionResponse.status()).toBe(200);
      const afterAttention = await afterAttentionResponse.json();
      expect(afterAttention.counts.active).toBe(attentionFeed.counts.active - 1);
      expect(afterAttention.items.some(item => (
        item.id === 'OPERATIONS:' + work.work_item_id
      ))).toBe(false);

      // A verified source completion must refresh global chrome in the same
      // authenticated browser session, not wait for the old periodic poll.
      await expect(bell).toHaveAttribute(
        'aria-label',
        `Open daily attention: ${afterAggregate.summary.active_count} active work items`,
      );
      await bell.click();
      await panel.getByRole('tab', {name: 'Calendar', exact: true}).click();
      await expect(agendaItem).toHaveCount(0);
      expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(viewport.width + 1);
      expect(errors).toEqual([]);
    } finally {
      await context.close();
    }
  });
}

// ARTIFACT: daily-attention-calendar.browser.spec.js
// VERSION: v1.4.0-AUTHORISED-FEED-PERSISTENCE-READBACK
// AUTHORITY BOUNDARY: Synthetic authenticated browser and source-command evidence only.
// TENANT POSTURE: Existing approved fixture actor in a disposable loopback database.
// FAIL-CLOSED POSTURE: Missing source, replay conflict, wrong scope or browser error fails.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
