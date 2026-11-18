/**
 * TITLE: WILSY OS Named Project Reviewer Inbox Client Certificate
 * VERSION: v1.0.0-REVIEWER-INBOX-DECISION-READBACK-CERT
 * AUTHORITY: Synthetic source-controlled EOS reviewer inbox contract.
 * EPITOME: Reject foreign inboxes, read exact named decisions and validate
 *          approved review disappearance after a source-owned CAS command.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProjectApprovalInbox.test.jsx
 * COLLABORATION / OWNERSHIP: ProjectApprovalInbox and mocked api.js.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.0.0-REVIEWER-INBOX-DECISION-READBACK-CERT verifies
 *          recipient-only inbox, approval request identity and readback.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Synthetic tenant/project/actor records only.
 * TENANT BOUNDARY: Exact tenant and authenticated principal checked on read.
 * AUTHORITY BOUNDARY: No live IAM assertion, payment or task completion.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock('../../services/api.js', () => ({ default: api }));
import ProjectApprovalInbox from '../../components/workspaces/ProjectApprovalInbox.jsx';

const tenant = 'recipient-tenant';
const principal = 'current-reviewer';
const project = 'prj-' + 'a'.repeat(48);
const task = 'ptk-' + 'b'.repeat(48);
const approval = 'par-' + 'c'.repeat(48);
const pending = {
  schema: 'wilsy.project.approval.v1',
  tenant_id: tenant, project_id: project, task_id: task,
  approval_id: approval, requester_principal_id: 'separate-project-owner',
  reviewer_principal_id: principal, rationale: 'Accept completed deliverable.',
  status: 'PENDING', revision: 1,
  requested_at: '2026-11-18T08:00:00+00:00',
  decided_at: null, decision_rationale: null,
  fingerprint: 'a'.repeat(128),
};
const list = items => ({
  schema: 'WILSY-PROJECT-PENDING-APPROVALS/V1',
  tenant_id: tenant, principal_id: principal, items,
  limit: 50, offset: 0, has_more: false, next_offset: null,
});
beforeEach(() => {
  vi.clearAllMocks();
  vi.stubGlobal('crypto', { randomUUID: () => 'stable-review-command' });
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
const mount = () => render(<ProjectApprovalInbox
  tenantId={tenant} principalId={principal}
  tenantHeaders={{ 'X-Tenant-ID': tenant }} sessionScope="recipient-test"/>);

it('approves exactly its own pending review after source readback', async () => {
  let items = [pending];
  api.get.mockImplementation(async path => {
    expect(path).toBe('/projects/my-approvals?limit=50&offset=0');
    return { data: list(items) };
  });
  api.post.mockImplementationOnce(async (path, payload, options) => {
    expect(path).toBe('/projects/' + project + '/my-project/tasks/' + task
      + '/approvals/' + approval + '/decision');
    expect(payload).toEqual({
      expected_revision: 1, decision: 'APPROVED', rationale: 'Verified evidence.',
    });
    expect(options.headers['Idempotency-Key']).toBe('stable-review-command');
    items = [];
    return { data: {
      schema: 'WILSY-PROJECT-APPROVAL-RESULT/V1',
      tenant_id: tenant, principal_id: principal,
      project_id: project, task_id: task,
      approval: {
        ...pending, status: 'APPROVED', revision: 2,
        decision_rationale: 'Verified evidence.',
        decided_at: '2026-11-18T08:02:00+00:00',
        fingerprint: 'b'.repeat(128),
      },
    } };
  });
  mount();
  expect(await screen.findByText('Accept completed deliverable.')).toBeVisible();
  fireEvent.change(screen.getByRole('textbox', { name: 'Review rationale ' + approval }), {
    target: { value: 'Verified evidence.' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Approve' }));
  await waitFor(() => expect(screen.getByText(
    'EOS verified no pending reviews assigned to your principal on this page.',
  )).toBeVisible());
  expect(api.post).toHaveBeenCalledTimes(1);
});

it('blocks foreign tenant inbox without exposing any review decision', async () => {
  api.get.mockResolvedValue({ data: {
    ...list([pending]), tenant_id: 'another-tenant',
  } });
  mount();
  expect(await screen.findByRole('alert')).toHaveTextContent('could not verify');
  expect(screen.queryByRole('button', { name: 'Approve' })).not.toBeInTheDocument();
  expect(api.post).not.toHaveBeenCalled();
});

// ARTIFACT: ProjectApprovalInbox.test.jsx
// VERSION: v1.0.0-REVIEWER-INBOX-DECISION-READBACK-CERT
// AUTHORITY BOUNDARY: client source evidence only, no IAM financial approvals
// TENANT POSTURE: exact tenant, recipient and approval command
// FAIL-CLOSED POSTURE: foreign or unverified inbox cannot expose decisions
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
