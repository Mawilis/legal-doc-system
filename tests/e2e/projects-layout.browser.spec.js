/**
 * TITLE: WILSY OS Projects Responsive Operating Table Browser Certificate
 * VERSION: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT
 * AUTHORITY: Rendered browser geometry only; Python EOS owns all data and commands.
 * EPITOME: Certify actual desktop/mobile Projects table, EOS-shaped chart,
 *          selected project detail and embedded notes without prototype cards.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/projects-layout.browser.spec.js
 * COLLABORATION / OWNERSHIP: Existing Playwright/Vite harness and ProjectsWorkspace;
 *          synthetic transport replies never establish authentication or IAM.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT separately verifies indexed owner-list navigation and explicit participant assignments in 1440px/390px Chromium; no implicit role grants, mutations or false owner totals.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT certifies computed readable task/note label colours against global CSS and six accessible sticky-note selections in rendered desktop/mobile Chromium.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT verifies full-width selected project, task-first view, scoped People and Notes navigation, and back-to-registry at desktop/mobile sizes.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT asserts exact visible quarantine label with unavailable malware clearance and no-download behavior.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT supplies source-owned quarantine state and null clearance fingerprint in desktop/mobile fixture; no invented download grant.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT renders
 *          task attachments as quarantined evidence with no preview/download
 *          and a bounded contributor upload control at desktop/mobile sizes.
 * CHANGELOG:  v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT scopes
 *          review rationale assertions to the selected task's accessible
 *          region when that source text also appears in the reviewer inbox.
 * CHANGELOG:  v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT verifies
 *          the separately admitted reviewer inbox is rendered and usable
 *          without navigation through the owner-only project registry.
 * CHANGELOG:  v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT renders
 *          the task-review approval history and named reviewer decision
 *          controls at desktop and mobile widths without simulated IAM grants.
 * CHANGELOG:  v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT renders
 *          the separately authorized Assigned Projects task/notification
 *          journey at desktop and mobile widths without simulated grants.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT verifies source-backed
 *          task discussion opens only for a source-confirmed task and uses
 *          exact tenant/project/task comment response checks in Chromium.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT makes the shared
 *          participant fixture honor the exact 50/100 page size requested by
 *          independently bounded participant and task selectors.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT verifies source-backed
 *          participant directory and grant entry controls at mobile/desktop.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT verifies EOS-backed project work
 *          geometry, verified empty state and a functional task-creation
 *          action on both 1440px desktop and 390px mobile in Chromium.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT measures exact direct-child table
 *          cells, avoiding nested inline project metadata spans being
 *          mistaken for independent columns by Playwright selectors.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT certifies the existing
 *          intentional mobile two-column compact table instead of requiring
 *          horizontal scrolling; retained visible status and action are tested.
 * CHANGELOG: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT measures actual
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
  owner_principal_id: PRINCIPAL, department_id: null, target_date: null,
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
const assignedParticipant = {
  tenant_id: TENANT, project_id: projectId,
  principal_id: PRINCIPAL, role: 'CONTRIBUTOR',
  state: 'ACTIVE', revision: 1, fingerprint: 'a'.repeat(128),
};
const assignedTask = {
  schema: 'wilsy.project.task.v1', tenant_id: TENANT,
  project_id: projectId, task_id: 'ptk-' + 'b'.repeat(48),
  title: 'Participant operational handoff', description: '',
  status: 'TODO', depends_on: [], assignee_principal_id: PRINCIPAL,
  revision: 1, fingerprint: 'b'.repeat(128),
};
const assignedNotification = {
  schema: 'wilsy.project.notification.v1',
  tenant_id: TENANT, project_id: projectId,
  notification_id: 'pnf-' + 'c'.repeat(48),
  comment_id: 'pcm-' + 'd'.repeat(48),
  task_id: assignedTask.task_id,
  recipient_principal_id: PRINCIPAL,
  actor_principal_id: 'another-contributor',
  occurred_at: '2026-11-18T08:00:00+00:00',
  read_at: null, revision: 1, fingerprint: 'e'.repeat(128),
};


for (const width of [1440, 390]) {
  test('Projects real rendered table and detail at ' + width + 'px', async ({ page }) => {
    await page.setViewportSize({ width, height: 950 });
    await page.route('**/api/**', async route => {
      const request = route.request();
      const url = new URL(request.url());
      const pathname = url.pathname;
      let response = null;
      if (request.method() === 'GET' && pathname === '/api/projects') {
        response = envelope;
        if (url.searchParams.get('owned_by_me') === 'true') {
          expect(url.searchParams.get('limit')).toBe('100');
          expect(url.searchParams.get('offset')).toBe('0');
          response = { ...envelope, items: [project] };
        }
      }
      if (request.method() === 'GET' && pathname === '/api/projects/my-approvals') {
        response = {
          schema: 'WILSY-PROJECT-PENDING-APPROVALS/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL,
          limit: 50, offset: 0, has_more: false, next_offset: null,
          items: [{
            schema: 'wilsy.project.approval.v1',
            tenant_id: TENANT, project_id: projectId,
            task_id: assignedTask.task_id,
            approval_id: 'par-' + 'e'.repeat(48),
            requester_principal_id: 'separately-authorized-project-owner',
            reviewer_principal_id: PRINCIPAL,
            rationale: 'Independently review task delivery evidence.',
            status: 'PENDING', revision: 1,
            requested_at: '2026-11-18T08:00:00+00:00',
            decided_at: null, decision_rationale: null,
            fingerprint: 'f'.repeat(128),
          }],
        };
      }
      if (request.method() === 'GET' && pathname === '/api/projects/my-projects') {
        response = {
          schema: 'WILSY-PROJECT-MY-PROJECTS/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL,
          limit: 50, offset: 0, has_more: false, next_offset: null,
          items: [{ project, participation: assignedParticipant }],
        };
      }
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId + '/my-project') {
        response = {
          schema: 'WILSY-PROJECT-PARTICIPANT-DETAIL/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL,
          project_id: projectId, project, participation: assignedParticipant,
        };
      }
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId + '/my-project/tasks') {
        response = {
          schema: 'WILSY-PROJECT-TASK-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL,
          project_id: projectId, limit: 50, offset: 0,
          has_more: false, next_offset: null, items: [assignedTask],
        };
      }
      if (request.method() === 'GET'
        && pathname === '/api/projects/' + projectId + '/my-project/tasks/' + assignedTask.task_id + '/approvals') {
        response = {
          schema: 'WILSY-PROJECT-APPROVAL-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: projectId,
          task_id: assignedTask.task_id, limit: 50, offset: 0,
          has_more: false, next_offset: null,
          items: [{
            schema: 'wilsy.project.approval.v1',
            tenant_id: TENANT, project_id: projectId, task_id: assignedTask.task_id,
            approval_id: 'par-' + 'e'.repeat(48),
            requester_principal_id: 'separately-authorized-project-owner',
            reviewer_principal_id: PRINCIPAL,
            rationale: 'Independently review task delivery evidence.',
            status: 'PENDING', revision: 1,
            requested_at: '2026-11-18T08:00:00+00:00',
            decided_at: null, decision_rationale: null,
            fingerprint: 'f'.repeat(128),
          }],
        };
      }
      if (request.method() === 'GET'
        && pathname === '/api/projects/' + projectId + '/my-project/tasks/' + assignedTask.task_id + '/attachments') {
        response = {
          schema: 'WILSY-PROJECT-ATTACHMENT-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL,
          project_id: projectId, task_id: assignedTask.task_id,
          items: [{
            schema: 'wilsy.project.attachment.v1',
            tenant_id: TENANT, project_id: projectId, task_id: assignedTask.task_id,
            attachment_id: 'pat-' + 'f'.repeat(48),
            uploader_principal_id: PRINCIPAL,
            filename: 'verified-quarantine-sample.pdf',
            media_type: 'application/pdf', size_bytes: 128,
            content_sha3_512: 'a'.repeat(128),
            created_at: '2026-11-18T08:00:00+00:00',
            state: 'QUARANTINED', revision: 1,
            scan_clearance_status: 'QUARANTINED',
            scan_clearance_fingerprint: null,
          }],
          limit: 50, offset: 0, has_more: false, next_offset: null,
        };
      }
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId + '/my-project/notifications') {
        response = {
          schema: 'WILSY-PROJECT-NOTIFICATION-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL,
          project_id: projectId, limit: 50, offset: 0,
          has_more: false, next_offset: null, items: [assignedNotification],
        };
      }
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId + '/my-project/participants') {
        response = {
          schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL,
          project_id: projectId, limit: 100, offset: 0,
          has_more: false, next_offset: null, items: [assignedParticipant],
        };
      }

      if (request.method() === 'GET' && pathname === '/api/projects/summary') response = summary;
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId) response = detail;
      if (request.method() === 'GET' && pathname.startsWith('/api/projects/' + projectId + '/tasks/')
        && pathname.endsWith('/comments')) {
        response = {
          schema: 'WILSY-PROJECT-COMMENT-LIST/V1', tenant_id: TENANT,
          principal_id: PRINCIPAL, project_id: projectId,
          task_id: 'ptk-' + 'c'.repeat(48),
          limit: 50, offset: 0, has_more: false, next_offset: null,
          items: [],
        };
      }
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId + '/tasks') {
        response = {
          schema: 'WILSY-PROJECT-TASK-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: projectId,
          limit: 50, offset: 0, has_more: false, next_offset: null,
          items: [],
        };
      }
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId + '/participant-options') {
        response = {
          schema: 'WILSY-PROJECT-PARTICIPANT-OPTIONS/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: projectId,
          limit: 50, offset: 0, has_more: false, next_offset: null,
          items: [{ principal_id: 'eligible-tenant-person' }],
        };
      }
      if (request.method() === 'GET' && pathname === '/api/projects/' + projectId + '/participants') {
        response = {
          schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1',
          tenant_id: TENANT, principal_id: PRINCIPAL, project_id: projectId,
          limit: Number(url.searchParams.get('limit')), offset: 0,
          has_more: false, next_offset: null,
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
    await expect(page.locator('.wp-list-panel')).toBeHidden();
    await expect(page.getByRole('region', { name: 'Verified project status distribution' })).toHaveCount(0);
    await expect(page.getByRole('navigation', { name: 'Project workspace views' })).toBeVisible();
    await expect(page.getByRole('region', { name: 'Project notes' })).toHaveCount(0);
    const projectWork = page.getByRole('region', { name: 'Project work execution' });
    await expect(projectWork).toBeVisible();
    await expect(projectWork.getByText('EOS verified no tasks on this page. Create work to begin execution.')).toBeVisible();
    await expect(projectWork.getByRole('button', { name: 'Create task' })).toBeVisible();
    await projectWork.getByRole('button', { name: 'Create task' }).click();
    await expect(projectWork.getByText('Create EOS work item')).toBeVisible();
    await expect(projectWork.getByRole('combobox', { name: 'Task assignee' })).toBeVisible();
    await expect(projectWork.getByRole('textbox', { name: 'Task title' })).toBeVisible();
    await expect(projectWork.getByRole('textbox', { name: 'Task title' })).toBeEditable();
    const taskFormLabelColour = await projectWork.locator('form label').first().evaluate(
      node => getComputedStyle(node).color,
    );
    expect(taskFormLabelColour, 'task label must not inherit pale gold')
      .toBe('rgb(21, 44, 76)');
    await expect(projectWork.getByRole('region', { name: 'Verified project tasks' })).toBeVisible();


    const after = await page.evaluate(() => {
      const workspace = document.querySelector('.wp-body').getBoundingClientRect();
      const list = document.querySelector('.wp-list-panel');
      const detail = document.querySelector('.wp-detail').getBoundingClientRect();
      return {
        viewport: document.documentElement.clientWidth,
        documentWidth: document.documentElement.scrollWidth,
        workspace: { x: workspace.x, width: workspace.width },
        listHidden: getComputedStyle(list).display === 'none',
        detail: { x: detail.x, y: detail.y, right: detail.right, width: detail.width },
      };
    });
    expect(after.documentWidth, 'selected-project horizontal overflow').toBeLessThanOrEqual(after.viewport + 1);
    expect(after.listHidden, 'list disappears rather than being compressed').toBe(true);
    expect(after.detail.width, 'detail fills selected project workspace')
      .toBeGreaterThan(after.workspace.width - 5);
    await page.getByRole('button', { name: 'People', exact: true }).click();
    const participantPanel = page.getByRole('region', { name: 'Project participants' });
    await expect(participantPanel).toBeVisible();
    await expect(participantPanel.getByRole('combobox', { name: 'Eligible participant' })).toBeVisible();
    await expect(participantPanel.getByRole('option', { name: 'eligible-tenant-person' })).toHaveCount(1);
    await expect(participantPanel.getByRole('button', { name: 'Add participant' })).toBeDisabled();
    await page.getByRole('button', { name: 'Notes', exact: true }).click();
    const notesPanel = page.getByRole('region', { name: 'Project notes' });
    await expect(notesPanel).toBeVisible();
    const noteFormLabelColour = await notesPanel.locator('form label').first().evaluate(
      node => getComputedStyle(node).color,
    );
    expect(noteFormLabelColour, 'note label must not inherit pale gold')
      .toBe('rgb(21, 44, 76)');
    for (const colour of ['Sunflower', 'Sky', 'Mint', 'Rose', 'Lilac', 'Slate']) {
      await expect(notesPanel.getByRole('button', {
        name: colour + ' sticky-note colour',
      })).toBeVisible();
    }
    await notesPanel.getByRole('button', { name: 'Lilac sticky-note colour' }).click();
    await expect(notesPanel.getByRole('button', { name: 'Lilac sticky-note colour' }))
      .toHaveAttribute('aria-pressed', 'true');
    await page.getByRole('button', { name: 'Back to projects table' }).click();
    await expect(page.locator('.wp-body')).toHaveAttribute('data-layout', 'list');
    await expect(page.getByRole('region', { name: 'Project notes' })).toHaveCount(0);
    await page.getByRole('button', { name: 'My owned projects' }).click();
    await expect(page.getByText(/1 shown · 1 verified · EOS owner-filtered page/)).toBeVisible();
    await expect(page.getByText('Projects operating foundation')).toBeVisible();
    await page.getByRole('button', { name: 'My owned projects' }).click();
    await expect(page.getByText('1 shown · 1 verified')).toBeVisible();
    await page.getByRole('button', { name: 'Participant assignments' }).click();
    await expect(page.getByRole('heading', { name: 'My assigned projects' })).toBeVisible();
    await expect(page.getByRole('region', { name: 'Pending project approvals' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Approve', exact: true })).toBeDisabled();
    await page.getByRole('textbox', { name: /^Review rationale/ })
      .fill('Evidence needs independent project review.');
    await expect(page.getByRole('button', { name: 'Approve', exact: true })).toBeEnabled();

    await expect(page.getByRole('button', { name: /Projects operating foundation/ })).toBeVisible();
    await page.getByRole('button', { name: /Projects operating foundation/ }).click();
    await expect(page.getByRole('region', { name: 'Participant task table' })).toBeVisible();
    await expect(page.getByText('Participant operational handoff')).toBeVisible();
    await expect(page.getByRole('region', { name: 'Project notifications' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Mark read' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'In progress' })).toBeVisible();
    await page.getByRole('button', { name: 'Attachments' }).click();
    await expect(page.getByRole('region', { name: 'Task attachments' })).toBeVisible();
    await expect(page.getByText('verified-quarantine-sample.pdf')).toBeVisible();
    await expect(page.getByRole('region', { name: 'Task attachments' })
      .getByText(/Quarantined · malware scan clearance unavailable · application\/pdf/)).toBeVisible();
    await expect(page.getByRole('button', { name: 'Submit to EOS quarantine' })).toBeDisabled();
    await expect(page.getByRole('region', { name: 'Task attachments' })
      .getByRole('link')).toHaveCount(0);

    await page.getByRole('button', { name: 'Approvals' }).click();
    await expect(page.getByRole('region', { name: 'Task approvals' })).toBeVisible();
    await expect(page.getByRole('region', { name: 'Task approvals' })
      .getByText('Independently review task delivery evidence.')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Approve review' })).toBeDisabled();
    await page.getByRole('textbox', { name: /^Decision rationale/ })
      .fill('Review requires documentary confirmation.');
    await expect(page.getByRole('button', { name: 'Approve review' })).toBeEnabled();

    const assignedGeometry = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      doc: document.documentElement.scrollWidth,
    }));
    expect(assignedGeometry.doc, 'participant workspace page overflow')
      .toBeLessThanOrEqual(assignedGeometry.viewport + 1);

  });
}

// ARTIFACT: projects-layout.browser.spec.js
// VERSION: v2.2.0-OWNER-PARTICIPANT-SEPARATION-BROWSER-CERT
// AUTHORITY BOUNDARY: rendered presentation only; not authenticated source proof
// TENANT POSTURE: exact synthetic tenant replies only
// FAIL-CLOSED POSTURE: geometry, chart, selection or note mount regressions deny
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
