/**
 * TITLE: WILSY OS Participant Projects and Inbox Client Certificate
 * VERSION: v1.0.0-PARTICIPANT-WORK-AND-RECEIPT-CERT
 * AUTHORITY: Mocked EOS client presentation only; server retains all IAM.
 * EPITOME: Certify participant-only assigned project selection, own-assignee
 *          lifecycle, mention notification acknowledgement and tenant isolation.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/AssignedProjectsWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: AssignedProjectsWorkspace, api.js mock.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.0.0-PARTICIPANT-WORK-AND-RECEIPT-CERT asserts source-backed
 *          assigned project task and unread/read notification UI lifecycle.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Synthetic tenant and principal records only.
 * TENANT BOUNDARY: Foreign source records rejected without business display.
 * AUTHORITY BOUNDARY: Mock source is not proof of authenticated IAM.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock('../../services/api.js', () => ({ default: api }));
import AssignedProjectsWorkspace from '../../components/workspaces/AssignedProjectsWorkspace.jsx';

const tenantId = 'assigned-project-tenant';
const principalId = 'participant-one';
const projectId = 'prj-' + 'a'.repeat(48);
const taskId = 'ptk-' + 'b'.repeat(48);
const noticeId = 'pnf-' + 'c'.repeat(48);
const project = {
  tenant_id: tenantId, project_id: projectId, name: 'Assigned design deliverable',
  status: 'planned', revision: 1,
};
const participation = {
  tenant_id: tenantId, project_id: projectId, principal_id: principalId,
  role: 'CONTRIBUTOR', state: 'ACTIVE', revision: 1,
  fingerprint: 'a'.repeat(128),
};
const work = {
  schema: 'wilsy.project.task.v1',
  tenant_id: tenantId, project_id: projectId, task_id: taskId,
  title: 'Review the dependency', description: '',
  status: 'TODO', assignee_principal_id: principalId,
  depends_on: [], revision: 1, fingerprint: 'b'.repeat(128),
};
const notice = {
  schema: 'wilsy.project.notification.v1',
  tenant_id: tenantId, project_id: projectId, task_id: taskId,
  comment_id: 'pcm-' + 'd'.repeat(48),
  notification_id: noticeId,
  recipient_principal_id: principalId,
  actor_principal_id: 'another-contributor',
  occurred_at: '2026-11-18T08:00:00+00:00',
  read_at: null, revision: 1, fingerprint: 'e'.repeat(128),
};

beforeEach(() => {
  vi.clearAllMocks();
  let sequence = 0;
  vi.stubGlobal('crypto', { randomUUID: () => 'participant-action-' + (++sequence) });
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const response = data => ({ data });

it('lists only assigned projects, acts on own task and marks own mention read', async () => {
  let task = work;
  let notification = notice;
  let commands = 0;
  api.get.mockImplementation(async path => {
    if (path === '/projects/my-projects?limit=50&offset=0') return response({
      schema: 'WILSY-PROJECT-MY-PROJECTS/V1',
      tenant_id: tenantId, principal_id: principalId,
      items: [{ project, participation }],
      limit: 50, offset: 0, has_more: false, next_offset: null,
    });
    if (path === '/projects/' + projectId + '/my-project') return response({
      schema: 'WILSY-PROJECT-PARTICIPANT-DETAIL/V1',
      tenant_id: tenantId, principal_id: principalId, project_id: projectId,
      project, participation,
    });
    if (path === '/projects/' + projectId + '/my-project/tasks?limit=50&offset=0') return response({
      schema: 'WILSY-PROJECT-TASK-LIST/V1',
      tenant_id: tenantId, principal_id: principalId, project_id: projectId,
      items: [task], limit: 50, offset: 0, has_more: false, next_offset: null,
    });
    if (path === '/projects/' + projectId + '/my-project/notifications?limit=50&offset=0') return response({
      schema: 'WILSY-PROJECT-NOTIFICATION-LIST/V1',
      tenant_id: tenantId, principal_id: principalId, project_id: projectId,
      items: [notification], limit: 50, offset: 0, has_more: false, next_offset: null,
    });
    if (path === '/projects/' + projectId + '/my-project/participants?limit=100&offset=0') return response({
      schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1',
      tenant_id: tenantId, principal_id: principalId, project_id: projectId,
      items: [participation], limit: 100, offset: 0, has_more: false, next_offset: null,
    });
    throw new Error('Unexpected participant source read ' + path);
  });
  api.post.mockImplementation(async (path, payload, options) => {
    expect(options.headers['X-Tenant-ID']).toBe(tenantId);
    expect(options.headers['Idempotency-Key']).toBeTruthy();
    commands += 1;
    if (path.endsWith('/transition')) {
      expect(payload).toEqual({ expected_revision: 1, status: 'IN_PROGRESS' });
      task = { ...task, status: 'IN_PROGRESS', revision: 2, fingerprint: 'f'.repeat(128) };
      return response({
        schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: tenantId, principal_id: principalId,
        project_id: projectId, task,
      });
    }
    expect(path).toBe('/projects/' + projectId
      + '/my-project/notifications/' + noticeId + '/read');
    expect(payload).toEqual({ expected_revision: 1 });
    notification = {
      ...notification, revision: 2, read_at: '2026-11-18T08:02:00+00:00',
      fingerprint: '1'.repeat(128),
    };
    return response({
      schema: 'WILSY-PROJECT-NOTIFICATION-RESULT/V1',
      tenant_id: tenantId, principal_id: principalId,
      project_id: projectId, notification,
    });
  });
  render(<AssignedProjectsWorkspace
    tenantId={tenantId} principalId={principalId}
    sessionScope="participant-test-scope"
    tenantHeaders={{ 'X-Tenant-ID': tenantId }}
    onBack={() => {}}/>);
  fireEvent.click(await screen.findByRole('button', { name: /Assigned design deliverable/ }));
  expect(await screen.findByRole('region', { name: 'Assigned project tasks' })).toBeVisible();
  expect(screen.getByText('Review the dependency')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'In progress' }));
  await waitFor(() => expect(screen.getByRole('region', { name: 'Assigned project tasks' }))
    .toHaveTextContent('In progress'));
  fireEvent.click(screen.getByRole('button', { name: 'Mark read' }));
  await waitFor(() => expect(screen.getByText('0 unread on this page')).toBeVisible());
  expect(commands).toBe(2);
  expect(project.status).toBe('planned');
  expect(api.get.mock.calls.some(([path]) => path.startsWith('/projects?'))).toBe(false);
});

it('fails closed on a foreign assigned-project list', async () => {
  api.get.mockResolvedValue(response({
    schema: 'WILSY-PROJECT-MY-PROJECTS/V1',
    tenant_id: 'foreign', principal_id: principalId,
    items: [{ project, participation }],
    limit: 50, offset: 0, has_more: false, next_offset: null,
  }));
  render(<AssignedProjectsWorkspace
    tenantId={tenantId} principalId={principalId}
    sessionScope="foreign-cert"
    tenantHeaders={{ 'X-Tenant-ID': tenantId }}
    onBack={() => {}}/>);
  expect(await screen.findByRole('alert')).toHaveTextContent('could not be verified');
  expect(screen.queryByRole('region', { name: 'Assigned project tasks' })).not.toBeInTheDocument();
  expect(api.post).not.toHaveBeenCalled();
});

// ARTIFACT: AssignedProjectsWorkspace.test.jsx
// VERSION: v1.0.0-PARTICIPANT-WORK-AND-RECEIPT-CERT
// AUTHORITY BOUNDARY: client mock only, no real principal IAM claims
// TENANT POSTURE: foreign tenant response is rejected
// FAIL-CLOSED POSTURE: no task actions or unread claims without EOS
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
