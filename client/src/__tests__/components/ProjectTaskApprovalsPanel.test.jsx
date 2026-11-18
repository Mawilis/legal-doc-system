/**
 * TITLE: WILSY OS Exact Task Approval Client Decision Certificate
 * VERSION: v1.0.0-NAMED-REVIEWER-AUDITED-READBACK-CERT
 * AUTHORITY: Synthetic EOS client contract; Python EOS owns permission truth.
 * EPITOME: Certify owner request, independently authorized reviewer decision,
 *          durable readback, foreign source denial and no self-approval action.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProjectTaskApprovalsPanel.test.jsx
 * COLLABORATION / OWNERSHIP: ProjectTaskApprovalsPanel; mocked api.js.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.0.0-NAMED-REVIEWER-AUDITED-READBACK-CERT tests both separated
 *          user journeys without granting financial or task status authority.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Synthetic identities; no live IAM credentials.
 * TENANT BOUNDARY: Foreign/project/principal source envelopes are rejected.
 * AUTHORITY BOUNDARY: No source readback, no client success claim.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock('../../services/api.js', () => ({ default: api }));
import ProjectTaskApprovalsPanel from '../../components/workspaces/ProjectTaskApprovalsPanel.jsx';

const tenantId = 'approval-test-tenant';
const projectId = 'prj-' + 'a'.repeat(48);
const taskId = 'ptk-' + 'b'.repeat(48);
const approvalId = 'par-' + 'c'.repeat(48);
const requester = 'principal-owner';
const reviewer = 'principal-contributor';

const record = (changes = {}) => ({
  schema: 'wilsy.project.approval.v1',
  tenant_id: tenantId, project_id: projectId, task_id: taskId,
  approval_id: approvalId, requester_principal_id: requester,
  reviewer_principal_id: reviewer,
  rationale: 'Review the current delivery evidence.',
  status: 'PENDING', requested_at: '2026-11-18T08:00:00+00:00',
  decided_at: null, decision_rationale: null, revision: 1,
  fingerprint: 'a'.repeat(128), ...changes,
});
const prefix = '/projects/' + projectId + '/tasks/' + taskId + '/approvals';
const memberPrefix = '/projects/' + projectId + '/my-project/tasks/' + taskId + '/approvals';

beforeEach(() => {
  vi.clearAllMocks();
  let counter = 0;
  vi.stubGlobal('crypto', { randomUUID: () => 'review-command-' + (++counter) });
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const mount = (principalId, participantMode = false) =>
  render(<ProjectTaskApprovalsPanel tenantId={tenantId} principalId={principalId}
    projectId={projectId} taskId={taskId} participantMode={participantMode}
    tenantHeaders={{ 'X-Tenant-ID': tenantId }}
    participants={[{
      tenant_id: tenantId, project_id: projectId,
      principal_id: reviewer, state: 'ACTIVE', role: 'CONTRIBUTOR',
    }]} onClose={() => {}}/>);

it('requests a separately reviewed task decision and checks canonical source readback', async () => {
  let current = [];
  api.get.mockImplementation(async path => {
    expect(path).toBe(prefix + '?limit=50&offset=0');
    return { data: {
      schema: 'WILSY-PROJECT-APPROVAL-LIST/V1',
      tenant_id: tenantId, principal_id: requester, project_id: projectId,
      task_id: taskId, items: current, offset: 0, limit: 50,
      has_more: false, next_offset: null,
    } };
  });
  api.post.mockImplementationOnce(async (path, body, options) => {
    expect(path).toBe(prefix);
    expect(body).toEqual({
      reviewer_principal_id: reviewer, rationale: 'Independent review required.',
    });
    expect(options.headers['Idempotency-Key']).toBe('review-command-1');
    current = [record()];
    return { data: {
      schema: 'WILSY-PROJECT-APPROVAL-RESULT/V1',
      tenant_id: tenantId, principal_id: requester,
      project_id: projectId, task_id: taskId, approval: current[0],
    } };
  });
  mount(requester);
  expect(await screen.findByText('EOS verified no approvals on this task page.')).toBeVisible();
  fireEvent.change(screen.getByRole('combobox', { name: 'Review contributor' }), {
    target: { value: reviewer },
  });
  fireEvent.change(screen.getByRole('textbox', { name: 'Review request rationale' }), {
    target: { value: 'Independent review required.' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Request EOS review' }));
  await waitFor(() => expect(screen.getByText('Review the current delivery evidence.')).toBeVisible());
  expect(api.post).toHaveBeenCalledTimes(1);
  expect(screen.queryByRole('button', { name: 'Approve review' })).not.toBeInTheDocument();
});

it('permits the exact named reviewer to decide once with a revisioned readback', async () => {
  let current = record();
  api.get.mockImplementation(async path => {
    expect(path).toBe(memberPrefix + '?limit=50&offset=0');
    return { data: {
      schema: 'WILSY-PROJECT-APPROVAL-LIST/V1',
      tenant_id: tenantId, principal_id: reviewer, project_id: projectId,
      task_id: taskId, items: [current], offset: 0, limit: 50,
      has_more: false, next_offset: null,
    } };
  });
  api.post.mockImplementationOnce(async (path, body) => {
    expect(path).toBe(memberPrefix + '/' + approvalId + '/decision');
    expect(body).toEqual({
      expected_revision: 1, decision: 'APPROVED',
      rationale: 'Evidence independently verified.',
    });
    current = record({
      status: 'APPROVED', revision: 2,
      decided_at: '2026-11-18T08:01:00+00:00',
      decision_rationale: 'Evidence independently verified.',
      fingerprint: 'b'.repeat(128),
    });
    return { data: {
      schema: 'WILSY-PROJECT-APPROVAL-RESULT/V1',
      tenant_id: tenantId, principal_id: reviewer,
      project_id: projectId, task_id: taskId, approval: current,
    } };
  });
  mount(reviewer, true);
  expect(await screen.findByRole('button', { name: 'Approve review' })).toBeVisible();
  fireEvent.change(screen.getByRole('textbox', { name: 'Decision rationale ' + approvalId }), {
    target: { value: 'Evidence independently verified.' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Approve review' }));
  await waitFor(() => expect(screen.getByText('Decision rationale: Evidence independently verified.')).toBeVisible());
  expect(screen.queryByRole('button', { name: 'Approve review' })).not.toBeInTheDocument();
  expect(api.post).toHaveBeenCalledTimes(1);
});

it('never offers review decision to another project participant', async () => {
  api.get.mockResolvedValue({ data: {
    schema: 'WILSY-PROJECT-APPROVAL-LIST/V1',
    tenant_id: tenantId, principal_id: 'another-principal',
    project_id: projectId, task_id: taskId,
    items: [record()], offset: 0, limit: 50,
    has_more: false, next_offset: null,
  } });
  mount('another-principal', true);
  expect(await screen.findByText('Review the current delivery evidence.')).toBeVisible();
  expect(screen.queryByRole('button', { name: 'Approve review' })).not.toBeInTheDocument();
  expect(api.post).not.toHaveBeenCalled();
});

it('rejects cross-tenant approval list without exposing decision controls', async () => {
  api.get.mockResolvedValue({ data: {
    schema: 'WILSY-PROJECT-APPROVAL-LIST/V1',
    tenant_id: 'foreign-tenant', principal_id: reviewer,
    project_id: projectId, task_id: taskId,
    items: [record()], offset: 0, limit: 50,
    has_more: false, next_offset: null,
  } });
  mount(reviewer, true);
  expect(await screen.findByRole('alert')).toHaveTextContent('could not verify');
  expect(screen.queryByRole('button', { name: 'Approve review' })).not.toBeInTheDocument();
  expect(api.post).not.toHaveBeenCalled();
});

// ARTIFACT: ProjectTaskApprovalsPanel.test.jsx
// VERSION: v1.0.0-NAMED-REVIEWER-AUDITED-READBACK-CERT
// AUTHORITY BOUNDARY: mocked client only, no live IAM or financial approval
// TENANT POSTURE: exact tenant/project/task/actor source readback
// FAIL-CLOSED POSTURE: foreign, unknown and non-reviewer denied
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
