/**
 * TITLE: WILSY OS Task Discussion Verified Source Client Certificate
 * VERSION: v1.2.0-CONTRIBUTOR-EVIDENCE-COMPOSER-CERT
 * AUTHORITY: Synthetic client contract evidence; Python EOS owns comments.
 * EPITOME: Certify exact task thread read, mention choice, publish, readback
 *          and foreign-tenant payload rejection without fabricated delivery.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProjectTaskCommentsPanel.test.jsx
 * COLLABORATION / OWNERSHIP: ProjectTaskCommentsPanel; mocked api.js transport.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.2.0-CONTRIBUTOR-EVIDENCE-COMPOSER-CERT confirms that task evidence upload is
 *          available only after verified active contributor participation
 *          and uses the independently authorised task evidence service.
 * CHANGELOG: v1.1.0-READ-FIRST-ACTIVITY-COMPOSER-CERT certifies
 *          read-first source activity, explicit Write update disclosure,
 *          source-preserving comment publication and bounded mention counts.
 * CHANGELOG: v1.0.0-PROJECT-TASK-COMMENT-READBACK-CERT covers verified task
 *          comment read/write and no inferred notifications.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Synthetic identities and mock-only API.
 * TENANT BOUNDARY: Response scope checked for every read and command.
 * AUTHORITY BOUNDARY: No live IAM, membership or notification delivery.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock('../../services/api.js', () => ({ default: api }));
import ProjectTaskCommentsPanel from '../../components/workspaces/ProjectTaskCommentsPanel.jsx';

const tenantId = 'comments-tenant';
const principalId = 'comment-owner';
const projectId = 'prj-' + 'a'.repeat(48);
const taskId = 'ptk-' + 'b'.repeat(48);
const member = 'verified-contributor';
const route = '/projects/' + projectId + '/tasks/' + taskId + '/comments';
const source = {
  schema: 'wilsy.project.comment.v1', tenant_id: tenantId,
  project_id: projectId, task_id: taskId,
  comment_id: 'pcm-' + 'c'.repeat(48),
  author_principal_id: principalId,
  body: 'Please verify this dependency.', mentions: [member],
  created_at: '2026-11-18T08:00:00+00:00',
  fingerprint: 'd'.repeat(128),
};

beforeEach(() => {
  vi.clearAllMocks();
  vi.stubGlobal('crypto', { randomUUID: () => 'source-comment-command' });
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function mount(contributor = false) {
  return render(<ProjectTaskCommentsPanel tenantId={tenantId}
    principalId={principalId} projectId={projectId} taskId={taskId}
    participants={[{ principal_id: member, role: 'CONTRIBUTOR', first_name: 'Verified', last_name: 'Member' },
      ...(contributor ? [{ principal_id: principalId, role: 'CONTRIBUTOR',
        first_name: 'Task', last_name: 'Owner' }] : [])]}
    tenantHeaders={{ 'X-Tenant-ID': tenantId }} onClose={() => {}}/>);
}

it('publishes a comment and mention only after verified source list readback', async () => {
  let items = [];
  api.get.mockImplementation(async path => {
    expect(path).toBe(route + '?limit=50&offset=0');
    return { data: {
      schema: 'WILSY-PROJECT-COMMENT-LIST/V1',
      tenant_id: tenantId, principal_id: principalId,
      project_id: projectId, task_id: taskId,
      items, limit: 50, offset: 0, has_more: false, next_offset: null,
    } };
  });
  api.post.mockImplementationOnce(async (path, body, options) => {
    expect(path).toBe(route);
    expect(body).toEqual({
      body: 'Please verify this dependency.', mentions: [member],
    });
    expect(options.headers['X-Tenant-ID']).toBe(tenantId);
    expect(options.headers['Idempotency-Key']).toBe('source-comment-command');
    items = [source];
    return { data: {
      schema: 'WILSY-PROJECT-COMMENT-RESULT/V1',
      tenant_id: tenantId, principal_id: principalId,
      project_id: projectId, task_id: taskId, comment: source,
    } };
  });
  mount();
  fireEvent.click(await screen.findByRole('button', { name: 'Write update' }));
  const message = await screen.findByRole('textbox', { name: 'New task comment' });
  const mention = screen.getByRole('checkbox', { name: 'Verified Member' });
  fireEvent.click(mention);
  fireEvent.change(message, { target: { value: 'Please verify this dependency.' } });
  fireEvent.click(screen.getByRole('button', { name: 'Publish to EOS' }));
  await waitFor(() => expect(screen.getByText('Please verify this dependency.')).toBeVisible());
  expect(api.post).toHaveBeenCalledTimes(1);
  expect(screen.getByText('Mentions: 1 source references')).toBeVisible();
  expect(screen.getByText(/not a delivered notification/)).toBeVisible();
});

it('offers contributor-only in-place evidence upload with no owner-route privilege fallback', async () => {
  api.get.mockImplementation(async path => {
    if (path === route + '?limit=50&offset=0') return { data: {
      schema: 'WILSY-PROJECT-COMMENT-LIST/V1', tenant_id: tenantId,
      principal_id: principalId, project_id: projectId, task_id: taskId,
      items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
    } };
    if (path.includes('/my-project/tasks/') && path.endsWith('/attachments?limit=50&offset=0'))
      return { data: {
        schema: 'WILSY-PROJECT-ATTACHMENT-LIST/V1', tenant_id: tenantId,
        principal_id: principalId, project_id: projectId, task_id: taskId,
        items: [], limit: 50, offset: 0, has_more: false, next_offset: null,
      } };
    throw new Error('Unexpected source ' + path);
  });
  const { unmount } = mount(false);
  expect(await screen.findByRole('button', { name: 'Write update' })).toBeVisible();
  expect(screen.queryByRole('button', { name: 'Upload task evidence' })).not.toBeInTheDocument();
  unmount();
  mount(true);
  fireEvent.click(await screen.findByRole('button', { name: 'Upload task evidence' }));
  expect(await screen.findByRole('region', { name: 'Task attachments' })).toBeVisible();
  expect(await screen.findByLabelText('Project attachment file')).toHaveAttribute('type', 'file');
  expect(api.post).not.toHaveBeenCalled();
});

it('fails closed on a foreign tenant thread and prevents publishing', async () => {
  api.get.mockResolvedValue({ data: {
    schema: 'WILSY-PROJECT-COMMENT-LIST/V1',
    tenant_id: 'foreign-tenant', principal_id: principalId,
    project_id: projectId, task_id: taskId,
    items: [source], limit: 50, offset: 0,
    has_more: false, next_offset: null,
  } });
  mount();
  expect(await screen.findByRole('alert')).toHaveTextContent('could not be verified');
  expect(screen.queryByRole('button', { name: 'Publish to EOS' })).not.toBeInTheDocument();
  expect(api.post).not.toHaveBeenCalled();
});

// ARTIFACT: ProjectTaskCommentsPanel.test.jsx
// VERSION: v1.2.0-CONTRIBUTOR-EVIDENCE-COMPOSER-CERT
// AUTHORITY BOUNDARY: mocked readback only, not a live authenticated journey
// TENANT POSTURE: foreign source rejected without leaking comments
// FAIL-CLOSED POSTURE: invalid source never displays or permits write
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
