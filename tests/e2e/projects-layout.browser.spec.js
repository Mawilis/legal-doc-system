/**
 * TITLE: WILSY OS Projects Responsive Operating Table Browser Certificate
 * VERSION: v1.1.0-PROJECT-TASK-BROWSER-READBACK-CERT
 * AUTHORITY: Rendered browser geometry only; Python EOS owns all data and commands.
 * EPITOME: Certify actual desktop/mobile Projects table, EOS-shaped chart,
 *          selected project detail and embedded notes without prototype cards.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/projects-layout.browser.spec.js
 * COLLABORATION / OWNERSHIP: Existing Playwright/Vite harness and ProjectsWorkspace;
 *          synthetic transport replies never establish authentication or IAM.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.1.0-PROJECT-TASK-BROWSER-READBACK-CERT verifies EOS-backed project work
 *          geometry, verified empty state and a functional task-creation
 *          action on both 1440px desktop and 390px mobile in Chromium.
 * CHANGELOG: v1.1.0-PROJECT-TASK-BROWSER-READBACK-CERT measures exact direct-child table
 *          cells, avoiding nested inline project metadata spans being
 *          mistaken for independent columns by Playwright selectors.
 * CHANGELOG: v1.1.0-PROJECT-TASK-BROWSER-READBACK-CERT certifies the existing
 *          intentional mobile two-column compact table instead of requiring
 *          horizontal scrolling; retained visible status and action are tested.
 * CHANGELOG: v1.1.0-PROJECT-TASK-BROWSER-READBACK-CERT measures actual
 *          viewport overflow, table width, two-column/stacked layout,
 *          source-backed status visualization, selection and note surface.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Synthetic records and mocked EOS responses only;
 *          no credentials, live database, external service or project mutation.
 * TENANT BOUNDARY: API responses have one exact synthetic tenant/principal,
 *          while the test does not claim authenticated source authority.
 * AUTHORITY BOUNDARY: Presentation-only certification, not authenticated
 *          browser acceptance or permission/entitlement verification.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import { expect, test } from '@playwright/test';

const TENANT = 'project-visual-cert-tenant';
const PRINCIPAL = 'project-visual-cert-principal';
const projectId = 'prj-' + 'a'.repeat(48);
const project = {
  tenant_id: TENANT, project_id: projectId, code: 'VISUAL-001',
  name: 'Projects operating foundation', summary: 'Source-owned execution scope.',
  status: 'planned', revision: 1, archived_at: null,
  created_at: '2026-11-18T09:00:00+00:00',
  updated_at: '2026-11-18T09:00:00+00:00',
  owner_principal_id: null, department_id: null, target_date: null,
};
const projectEvent = {
  tenant_id: TENANT, project_id: projectId,
  event_id: 'event-visual-01', event_type: 'PROJECT_CREATED',
  actor_principal_id: PRINCIPAL, revision: 1,
  occurred_at: '2026-11-18T09:00:00+00:00',
};
const envelope = {
  schema: 'WILSY-PROJECT-LIST/V1', tenant_id: TENANT, principal_id: PRINCIPAL,
  items: [project], offset: 0, limit: 100, has_more: false, next_offset: null,
};
const summary = {
  schema: 'WILSY-PROJECT-SUMMARY/V1', tenant_id: TENANT,
  principal_id: PRINCIPAL,
  counts: { total: 1, planned: 1, active: 0, on_hold: 0, done: 0, cancelled: 0 },
};
const detail = {
  schema: 'WILSY-PROJECT-RESULT/V1', tenant_id: TENANT,
  principal_id: PRINCIPAL, project, events: [projectEvent],
  authority: { source: 'PYTHON_EOS_PROJECT_REGISTRY', financial_execution: false },
};

for (const width of [1440, 390]) {
  test('Projects real rendered table and detail at ' + width + 'px', async ({ page }) => {
    await page.setViewportSize({ width, height: 950 });
    await page.route('**/api/**', async route => {
      const request = route.request();
      const url = new URL(request.url());
      const pathname = url.pathname;
      let response = null;
      if (request.method() === 'GET' && pathname === '/api/projects') response = envelope;
      if (request.method() === 'GET' && pathname === '/api/projects/summary') response = summary;
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId) response = detail;
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId + '/tasks') {
        response = {
          schema: 'WILSY-PROJECT-TASK-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: projectId,
          limit: 50, offset: 0, has_more: false, next_offset: null,
          items: [],
        };
      }
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId + '/participants') {
        response = {
          schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: projectId,
          limit: 100, offset: 0, has_more: false, next_offset: null,
          items: [],
        };
      }
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId + '/notes') {
        response = {
          schema: 'WILSY-PROJECT-NOTE-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: projectId,
          items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
        };
      }
      if (response) {
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(response) });
      } else {
        await route.fulfill({ status: 401, contentType: 'application/json', body: '{"detail":"AUTHENTICATION_REQUIRED"}' });
      }
    });
    // A Vite-served page gives the existing module its actual runtime CSS and
    // React dependencies; the app root is replaced by an isolated test mount.
    await page.goto('/discovery', { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => { document.body.innerHTML = '<div id="project-visual-cert-root"></div>'; });
    await page.evaluate(async ({ tenantId, principalId }) => {
      const componentUrl = '/src/components/workspaces/ProjectsWorkspace.jsx';
      const transformed = await fetch(componentUrl).then(response => response.text());
      const reactMatch = transformed.match(/from ["']([^"']*\/react\.js\?v=[^"']+)["']/);
      if (!reactMatch) throw new Error('PROJECTS_BROWSER_REACT_DEPENDENCY_UNRESOLVED');
      const reactUrl = reactMatch[1];
      const domUrl = reactUrl.replace('/react.js?', '/react-dom.js?');
      const [ReactModule, ReactDomModule, WorkspaceModule] = await Promise.all([
        import(reactUrl), import(domUrl), import(componentUrl),
      ]);
      const React = ReactModule.default;
      const root = ReactDomModule.default.createRoot(document.getElementById('project-visual-cert-root'));
      root.render(React.createElement(WorkspaceModule.default, {
        tenantId, principalId, sessionScope: 'visual-cert-session',
      }));
      window.__projectVisualCertRoot = root;
    }, { tenantId: TENANT, principalId: PRINCIPAL });

    await expect(page.locator('.wp-list-panel')).toBeVisible();
    await expect(page.getByRole('region', { name: 'Verified project status distribution' })).toBeVisible();
    await expect(page.getByRole('img', { name: 'Planned: 1 of 1 projects' })).toBeVisible();
    await expect(page.getByRole('button', { name: /View project Projects operating foundation/ })).toBeVisible();

    const before = await page.evaluate(() => {
      const workspace = document.querySelector('.wilsy-projects');
      const list = document.querySelector('.wp-list-panel');
      const shell = document.querySelector('.wp-table-shell');
      const row = document.querySelector('.wp-table-row');
      const body = document.querySelector('.wp-body');
      const bounds = node => {
        const rect = node.getBoundingClientRect();
        return { x: rect.x, y: rect.y, width: rect.width, right: rect.right, bottom: rect.bottom };
      };
      return {
        viewport: document.documentElement.clientWidth,
        documentWidth: document.documentElement.scrollWidth,
        workspace: bounds(workspace), list: bounds(list),
        body: bounds(body), row: bounds(row),
        table: {
          clientWidth: shell.clientWidth, scrollWidth: shell.scrollWidth,
          headDisplay: getComputedStyle(document.querySelector('.wp-table-head')).display,
          codeDisplay: getComputedStyle(row.querySelector(':scope > span:nth-child(2)')).display,
          dateDisplay: getComputedStyle(row.querySelector(':scope > span:nth-child(4)')).display,
          statusDisplay: getComputedStyle(row.querySelector(':scope > span:nth-child(3)')).display,
          actionDisplay: getComputedStyle(row.querySelector(':scope > span:nth-child(5)')).display,
        },
      };
    });
    expect(before.documentWidth, 'outer horizontal overflow').toBeLessThanOrEqual(before.viewport + 1);
    expect(before.list.width, 'Projects list occupies full workspace width').toBeGreaterThan(before.body.width - 3);
    if (width === 1440) {
      expect(before.row.width, 'readable desktop table').toBeGreaterThan(740);
      expect(before.table.scrollWidth).toBeLessThanOrEqual(before.table.clientWidth + 2);
    } else {
      expect(before.table.scrollWidth, 'mobile table must fit its compact region')
        .toBeLessThanOrEqual(before.table.clientWidth + 2);
      expect(before.table.headDisplay).toBe('none');
      expect(before.table.codeDisplay).toBe('none');
      expect(before.table.dateDisplay).toBe('none');
      expect(before.table.statusDisplay).not.toBe('none');
      expect(before.table.actionDisplay).not.toBe('none');
    }

    await page.getByRole('button', { name: /View project Projects operating foundation/ }).click();
    await expect(page.getByRole('heading', { name: 'Projects operating foundation' })).toBeVisible();
    await expect(page.getByRole('region', { name: 'Project notes' })).toBeVisible();
    const projectWork = page.getByRole('region', { name: 'Project work execution' });
    await expect(projectWork).toBeVisible();
    await expect(projectWork.getByText('EOS verified no tasks on this page. Create work to begin execution.')).toBeVisible();
    await expect(projectWork.getByRole('button', { name: 'Create task' })).toBeVisible();
    await projectWork.getByRole('button', { name: 'Create task' }).click();
    await expect(projectWork.getByText('Create EOS work item')).toBeVisible();
    await expect(projectWork.getByRole('combobox', { name: 'Task assignee' })).toBeVisible();
    await expect(projectWork.getByRole('textbox', { name: 'Task title' })).toBeVisible();
    await expect(projectWork.getByRole('textbox', { name: 'Task title' })).toBeEditable();

    const after = await page.evaluate(() => {
      const list = document.querySelector('.wp-list-panel').getBoundingClientRect();
      const detail = document.querySelector('.wp-detail').getBoundingClientRect();
      return {
        viewport: document.documentElement.clientWidth,
        documentWidth: document.documentElement.scrollWidth,
        list: { x: list.x, y: list.y, right: list.right, bottom: list.bottom, width: list.width },
        detail: { x: detail.x, y: detail.y, right: detail.right, width: detail.width },
      };
    });
    expect(after.documentWidth, 'selected-project horizontal overflow').toBeLessThanOrEqual(after.viewport + 1);
    if (width === 1440) {
      expect(after.detail.x).toBeGreaterThanOrEqual(after.list.right - 2);
      expect(after.list.width).toBeGreaterThan(300);
      expect(after.detail.width).toBeGreaterThan(300);
    } else {
      expect(after.detail.y).toBeGreaterThanOrEqual(after.list.bottom - 2);
      expect(after.detail.width).toBeGreaterThan(320);
    }
    await page.getByRole('button', { name: 'Close project details' }).click();
    await expect(page.locator('.wp-body')).toHaveAttribute('data-layout', 'list');
    await expect(page.getByRole('region', { name: 'Project notes' })).toHaveCount(0);
  });
}

// ARTIFACT: projects-layout.browser.spec.js
// VERSION: v1.1.0-PROJECT-TASK-BROWSER-READBACK-CERT
// AUTHORITY BOUNDARY: rendered presentation only; not authenticated source proof
// TENANT POSTURE: exact synthetic tenant replies only
// FAIL-CLOSED POSTURE: geometry, chart, selection or note mount regressions deny
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
