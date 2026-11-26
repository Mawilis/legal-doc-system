/**
 * TITLE: WILSY OS Dock Operating Journey Client Certificate
 * VERSION: v1.9.3-ALIGNED-EVIDENCE-COLUMNS-CERT
 * AUTHORITY: Synthetic client regression evidence only.
 * EPITOME: Verify permissioned task actions, receipt currentness and draft attachment readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/intelligence/WilsyDockOperatingWork.test.jsx
 * COLLABORATION / OWNERSHIP: Closed Dock components, canonical transport and Projects.
 * CERTIFICATION / UPDATE DATE: 2026-11-26
 * CHANGELOG: v1.9.3-ALIGNED-EVIDENCE-COLUMNS-CERT validates all five evidence values share the same responsive fixed-start grid column, left alignment and narrow stacking without changing source-evidence assertions.
 * CHANGELOG: v1.9.2-STRICT-SOURCE-RECORD-CERT uses fully scoped synthetic event records to require EOS event authorship/time validation and rejects mismatched source items as unverified.
 * CHANGELOG: v1.9.1-SOURCE-ACCEPTANCE-EVIDENCE-CERT requires task's original acceptance text and lifecycle to remain visible while activity and attachment presence are not falsely treated as completion.
 * CHANGELOG: v1.9.0-EOS-CROSS-SOURCE-ASSESSMENT-CERT verifies bounded independent task event, comment, attachment and approval counts with missing evidence named explicitly, no false completion, no cross-tenant read acceptance, and unchanged source-backed navigation.
 * CHANGELOG: v1.8.0-ACTIONABLE-TASK-ASSESSMENT-CERT certifies the compact embedded view uses independently read EOS revision/blocker state, routes to existing task Activity/Evidence/Approvals callbacks, and exposes no model/command controls.
 * CHANGELOG: v1.7.0-IN-MODAL-READONLY-CERT checks a sourced task brief remains available in the modal-safe read-only projection without exposing transition, draft or attachment execution affordances.
 * CHANGELOG: v1.6.1-SPA-INTERNAL-WORK-FOCUS-CERT checks client-side Open yields task focus through one callback, retaining no reload and no write.
 * CHANGELOG: v1.6.0-SPA-INTERNAL-WORK-ROUTE-CERT certifies CRM Open changes React Router location without document reload or task mutation and retains a valid canonical href for direct navigation. Existing mock-only tests remain Router-independent.
 * CHANGELOG: v1.5.0-MW-T11-QUIET-TYPOGRAPHY-CERT checks tenant-neutral sentence-case metadata and preserved full EOS rank explanation without changing task identity or action rights.
 * CHANGELOG: v1.4.0-MW-T11-SCANNABLE-SOURCE-CERT certifies readable work title and quiet metadata, preserved EOS ordinal and full source explanation in the accessible row, unchanged canonical selection, and no exposed opaque task ID.
 * CHANGELOG: v1.3.0-MW-T11-RANKED-HANDOFF-CERT checks exact-source work ordering, task handoff proof and wrong-identity rejection without executing mutations.
 * CHANGELOG: v1.2.0-ATTACHMENT-REOPEN-RECONCILIATION certifies a lost-response accepted PDF attachment across unmount/remount with independent manifest reconciliation, no duplicate POST and no scan-clearance claim.
 * CHANGELOG: v1.1.0-REMOUNT-RECONCILIATION certifies a committed-but-lost HTTP response across unmount/remount with exactly one POST and independently verified receipt readback.
 * CHANGELOG: v1.0.0 covers action races, unknown outcomes, drafts and exact source isolation.
 * COMPLIANCE: AGENTS.md; synthetic records; keyboard-accessible semantic controls.
 * SECURITY / PRIVACY POSTURE: No provider, secret or live record used.
 * TENANT BOUNDARY: Exact tenant/principal/capacity generation.
 * AUTHORITY BOUNDARY: Test doubles establish no real IAM or persistence certificate.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { act, render, screen, fireEvent, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { sha3_512 } from 'js-sha3';
import OperatingWork from '../../../src/components/intelligence/WilsyDockOperatingWork.jsx';
import { dockEnvelope, TENANT, PERSON, PROJECT, TASK } from '../../fixtures/dockOperatingEnvelope.js';

const { get, post } = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock('../../../src/services/api.js', () => ({ default: { get, post } }));
vi.mock('../../../src/components/intelligence/wilsyDockContract.js', async importOriginal => ({
  ...await importOriginal(), createDockPlanPdf: vi.fn(async () => ({
    blob: new Blob(['%PDF synthetic']), digest: 'e'.repeat(128), filename: 'alignment-plan-r1.pdf', size: 14,
  })),
}));
let sequence = 0;
let source;
let failReceipt;
let manifests;
let selected;
let record;
const refusal = status => Object.assign(new Error('synthetic refusal'), { response: { status } });
const scope = () => 'scope-' + (++sequence);
function mount(props = {}) {
  return render(<OperatingWork tenantId={TENANT} principalId={PERSON} scope={scope()}
    locator={{ workspace: 'PROJECTS', project_id: PROJECT, task_id: TASK, participant_view: false }}
    onRecord={record} onSelectWork={selected} {...props}/>);
}
beforeEach(() => {
  source = dockEnvelope(); failReceipt = false; manifests = []; record = vi.fn(); selected = vi.fn();
  get.mockReset().mockImplementation(async path => {
    if (path === '/wilsy-ai/dock/context') return { data: structuredClone(source) };
    if (path.endsWith('/transition-receipt')) {
      if (failReceipt) throw refusal(503);
      return { data: { schema: 'WILSY-PROJECT-TASK-RESULT/V1', tenant_id: TENANT, principal_id: PERSON,
        project_id: PROJECT, task: { tenant_id: TENANT, project_id: PROJECT, task_id: TASK,
          revision: 2, status: 'IN_PROGRESS', fingerprint: '2'.repeat(128) } } };
    }
    if (path.endsWith('/attachments')) return { data: { schema: 'WILSY-PROJECT-ATTACHMENT-LIST/V1', tenant_id: TENANT,
      principal_id: PERSON, project_id: PROJECT, task_id: TASK, items: manifests,
      limit: 50, offset: 0, has_more: false, next_offset: null } };
    throw refusal(503);
  });
  post.mockReset().mockImplementation(async (path, body, options) => {
    if (path.endsWith('/transition')) source = dockEnvelope({ revision: 2, status: 'IN_PROGRESS' });
    if (path.endsWith('/attachments')) {
      const id = 'pat-' + sha3_512([TENANT, PROJECT, TASK, PERSON, options.headers['Idempotency-Key']].join('\0')).slice(0, 48);
      manifests = [{ schema: 'wilsy.project.attachment.v1', tenant_id: TENANT, project_id: PROJECT, task_id: TASK,
        attachment_id: id, uploader_principal_id: PERSON, filename: 'alignment-plan-r1.pdf',
        content_sha3_512: 'e'.repeat(128), size_bytes: 14, media_type: 'application/pdf', state: 'QUARANTINED', revision: 1 }];
    }
    return { data: {} };
  });
  vi.spyOn(window, 'confirm').mockReturnValue(true);
});

function RouteLocationProbe() {
  const location = useLocation();
  return <output aria-label="Current client route">{location.pathname + location.search}</output>;
}

describe('permissioned operating work', () => {
  it('reads independent EOS task evidence and recommends the actual missing source', async () => {
    const taskBase = '/projects/' + PROJECT + '/tasks/' + TASK;
    const pages = {
      events: { schema: 'WILSY-PROJECT-TASK-EVENT-LIST/V1', items: [{
        schema: 'wilsy.project.task.event.v1', tenant_id: TENANT, project_id: PROJECT,
        task_id: TASK, revision: 1, event_type: 'PROJECT_TASK_CREATED', status_after: 'TODO',
        actor_principal_id: PERSON, occurred_at: '2026-11-26T08:00:00Z',
      }] },
      comments: { schema: 'WILSY-PROJECT-COMMENT-LIST/V1', items: [{
        schema: 'wilsy.project.comment.v1', tenant_id: TENANT, project_id: PROJECT,
        task_id: TASK, comment_id: 'pcm-' + 'c'.repeat(48),
        author_principal_id: PERSON, body: 'Engineering activity recorded',
        mentions: [], fingerprint: 'a'.repeat(128),
      }] },
      attachments: { schema: 'WILSY-PROJECT-ATTACHMENT-LIST/V1', items: [] },
      approvals: { schema: 'WILSY-PROJECT-APPROVAL-LIST/V1', items: [] },
    };
    get.mockImplementation(async path => {
      if (path === '/wilsy-ai/dock/context') return { data: structuredClone(source) };
      const kind = Object.keys(pages).find(k => path === taskBase + '/' + k + '?limit=50&offset=0');
      if (!kind) throw refusal(503);
      return { data: { ...pages[kind], tenant_id: TENANT, principal_id: PERSON,
        project_id: PROJECT, task_id: TASK, limit: 50, offset: 0,
        has_more: false, next_offset: null } };
    });
    const evidence = vi.fn();
    mount({ readOnly: true, embedded: true, onReviewEvidence: evidence });
    const assessment = await screen.findByRole('region', { name: 'WILSY AI task assessment' });
    await waitFor(() => expect(assessment).toHaveTextContent('1 updates recorded'));
    expect(assessment).toHaveTextContent('1 events recorded');
    expect(assessment).toHaveTextContent('Acceptance definition: Align the Dock with authorized work.');
    expect(assessment).toHaveTextContent('to do · revision 1');
    expect(assessment).toHaveTextContent('0 attachments recorded');
    expect(assessment).toHaveTextContent('0 decisions recorded');
    const rows = [...screen.getByRole('list', { name: 'Verified completion evidence' }).children];
    expect(rows).toHaveLength(5);
    for (const row of rows) {
      expect(row).toHaveClass('grid', 'grid-cols-1',
        'sm:grid-cols-[minmax(0,1fr)_minmax(0,42%)]');
      expect(row.children).toHaveLength(2);
      expect(row.children[1]).toHaveClass('min-w-0', 'text-left');
    }
    expect(assessment).toHaveTextContent('do not prove the task');
    fireEvent.click(screen.getByRole('button', { name: /Next: Review the missing supporting evidence/i }));
    expect(evidence).toHaveBeenCalledTimes(1);
    expect(post).not.toHaveBeenCalled();
  });

  it('does not treat cross-tenant approval evidence as verified or permit closing', async () => {
    get.mockImplementation(async path => {
      if (path === '/wilsy-ai/dock/context') return { data: structuredClone(source) };
      if (path.endsWith('/approvals?limit=50&offset=0')) return { data: {
        schema: 'WILSY-PROJECT-APPROVAL-LIST/V1', tenant_id: 'OTHER_TENANT',
        principal_id: PERSON, project_id: PROJECT, task_id: TASK,
        limit: 50, offset: 0, has_more: false, next_offset: null, items: [],
      } };
      throw refusal(503);
    });
    mount({ readOnly: true, embedded: true });
    const assessment = await screen.findByRole('region', { name: 'WILSY AI task assessment' });
    await waitFor(() => expect(assessment).toHaveTextContent('Reviewer decisions'));
    await waitFor(() => expect(assessment).toHaveTextContent('decisions not verified'));
    expect(assessment).not.toHaveTextContent('0 decisions recorded');
    expect(screen.queryByRole('button', { name: /Complete task/ })).not.toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it('explains verified task attention and opens the canonical task work views without an AI command', async () => {
    const activity = vi.fn(); const evidence = vi.fn(); const approvals = vi.fn();
    mount({ readOnly: true, embedded: true,
      onReviewActivity: activity, onReviewEvidence: evidence,
      onReviewApprovals: approvals });
    expect(await screen.findByText('Task source verified')).toBeVisible();
    const assessment = screen.getByRole('region', { name: 'WILSY AI task assessment' });
    expect(assessment).toHaveTextContent('EOS · Revision 1');
    expect(assessment).toHaveTextContent('Completion evidence');
    expect(assessment).toHaveTextContent('not verified');
    expect(assessment).not.toHaveTextContent('EOS action order');
    expect(assessment).not.toHaveTextContent('Draft alignment plan');
    fireEvent.click(screen.getByRole('button', { name: 'Activity' }));
    fireEvent.click(screen.getByRole('button', { name: 'Evidence' }));
    fireEvent.click(screen.getByRole('button', { name: 'Approvals' }));
    expect(activity).toHaveBeenCalledTimes(1);
    expect(evidence).toHaveBeenCalledTimes(1);
    expect(approvals).toHaveBeenCalledTimes(1);
    expect(post).not.toHaveBeenCalled();
  });

  it('fails closed in embedded mode when the EOS task source is unavailable', async () => {
    get.mockRejectedValue(refusal(503));
    mount({ readOnly: true, embedded: true });
    expect(await screen.findByRole('button', { name: 'Retry verification' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Activity' })).not.toBeInTheDocument();
    expect(screen.queryByText('Task source verified')).not.toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it('presents source-verified task intelligence inside a modal without any mutation affordance', async () => {
    mount({ readOnly: true });
    expect(await screen.findByRole('status', { name: 'EOS-confirmed work handoff' })).toBeVisible();
    expect(screen.getByText(/Read-only EOS task inspection/)).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Draft alignment plan' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Start work/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Accept and attach PDF' })).not.toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it('opens CRM work within React Router without restarting application bootstrap', async () => {
    const crmId = 'owk_' + 'a'.repeat(32);
    get.mockImplementation(async path => {
      if (path !== '/my-work') throw refusal(503);
      return { data: {
        schema: 'WILSY-OS-UNIFIED-MY-WORK/V1',
        tenant_id: TENANT, principal_id: PERSON,
        as_of: '2026-11-26T08:00:00Z',
        items: [{ source: 'CRM', source_key: 'CRM:' + crmId,
          work_item_id: crmId, title: 'Open authorized CRM work',
          status: 'IN_PROGRESS', priority: 'HIGH',
          due_at: null, due_date: null, is_overdue: false,
          action_authority: 'SOURCE_SERVICE_ONLY', completion_route: null }],
        summary: { active_count: 1, overdue_count: 0, source_counts: { CRM: 1 } },
        sources_included: ['CRM'],
        authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
      } };
    });
    const navigated = vi.fn();
    render(<MemoryRouter initialEntries={['/headquarters?section=my-work']}>
      <OperatingWork tenantId={TENANT} principalId={PERSON} scope={scope()}
        locator={{ workspace: 'HEADQUARTERS' }}
        onRecord={record} onSelectWork={selected} onNavigateWork={navigated} />
      <RouteLocationProbe />
    </MemoryRouter>);
    const action = await screen.findByRole('link', { name: /Open authorized CRM work/ });
    expect(action).toHaveAttribute('href',
      '/headquarters?section=my-work&work=' + encodeURIComponent('CRM:' + crmId));
    fireEvent.click(action);
    expect(screen.getByLabelText('Current client route')).toHaveTextContent(
      '/headquarters?section=my-work&work=' + encodeURIComponent('CRM:' + crmId));
    expect(navigated).toHaveBeenCalledTimes(1);
    expect(post).not.toHaveBeenCalled();
  });

  it('preserves EOS queue order and confirms only its ranking evidence', async () => {
    const second = 'ptk-' + 'c'.repeat(48);
    const row = (taskId, title, priority, dueDate, overdue) => ({
      tenant_id: TENANT, source: 'PROJECTS', source_key: 'PROJECTS:' + taskId,
      work_item_id: taskId, project_id: PROJECT, owner_principal_id: PERSON,
      title, description: '', status: 'OPEN', kind: 'TASK', priority,
      due_at: null, due_date: dueDate, is_overdue: overdue,
      action_authority: 'SOURCE_SERVICE_ONLY', completion_route: null,
    });
    get.mockImplementation(async path => {
      if (path !== '/my-work') throw refusal(503);
      return { data: { schema: 'WILSY-OS-UNIFIED-MY-WORK/V1',
        tenant_id: TENANT, principal_id: PERSON, as_of: '2026-11-26T08:00:00Z',
        items: [row(TASK, 'First source item', 'NORMAL', '2026-12-12', false),
          row(second, 'Second source item', 'HIGH', '2026-11-26', true)],
        summary: { active_count: 2, overdue_count: 1, source_counts: { PROJECTS: 2 } },
        sources_included: ['PROJECTS'],
        authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
      } };
    });
    mount({ locator: { workspace: 'HEADQUARTERS' } });
    const first = await screen.findByRole('button', { name: /First source item/ });
    const secondRow = screen.getByRole('button', { name: /Second source item/ });
    expect(first).toHaveTextContent('01');
    expect(first).toHaveTextContent('Projects · normal · Due 2026-12-12');
    expect(first).toHaveAttribute('title', expect.stringContaining(
      'Position 1 in the current EOS-authorized My Work response'));
    expect(secondRow).toHaveTextContent('02');
    expect(secondRow).toHaveTextContent('Projects · high · Overdue');
    expect(secondRow).toHaveAttribute('title', expect.stringContaining(
      'Position 2 in the current EOS-authorized My Work response'));
    expect(secondRow).toHaveTextContent('Inspect');
    expect(first).toHaveAttribute('title', expect.stringContaining('PROJECTS source, normal priority'));
    expect(secondRow).toHaveAttribute('title', expect.stringContaining('PROJECTS source, high priority'));
    expect(first).not.toHaveTextContent('PRIORITY');
    expect(first).not.toHaveTextContent('EOS order');
    expect(first).not.toHaveTextContent(TASK);
    fireEvent.click(secondRow);
    expect(selected).toHaveBeenCalledWith({ workspace: 'PROJECTS',
      project_id: PROJECT, task_id: second, participant_view: true });
    expect(post).not.toHaveBeenCalled();
  });

  it('confirms a handoff only after exact EOS task source verification', async () => {
    mount();
    const status = await screen.findByRole('status', { name: 'EOS-confirmed work handoff' });
    expect(status).toHaveTextContent('Projects source verified · revision 1');
    expect(screen.getByRole('link', { name: 'Open full task' }))
      .toHaveAttribute('href', expect.stringContaining('task=' + TASK));
    expect(post).not.toHaveBeenCalled();
  });

  it('rejects a task identity mismatch with no handoff or write', async () => {
    source.source.task_id = 'ptk-' + 'd'.repeat(48);
    mount();
    await screen.findByRole('button', { name: 'Retry authorized work' });
    expect(screen.queryByRole('status', { name: 'EOS-confirmed work handoff' }))
      .not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Open full task' }))
      .not.toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it('renders a compact brief and four permitted source actions without a model call', async () => {
    mount();
    expect(await screen.findByRole('button', { name: 'Draft alignment plan' })).toBeVisible();
    expect(screen.getByText('Align the Dock with authorized work.')).toBeVisible();
    expect(screen.getByRole('link', { name: 'Open full task' })).toHaveAttribute('href', expect.stringContaining('section=projects'));
    expect(screen.queryByRole('button', { name: 'Complete task' })).not.toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });
  it('uses the participant route, stable command identity and independently verified receipt and source', async () => {
    source = dockEnvelope({ participant: true });
    mount({ locator: { workspace: 'PROJECTS', project_id: PROJECT, task_id: TASK, participant_view: true } });
    const previous = post.getMockImplementation();
    post.mockImplementation(async (...args) => { const result = await previous(...args); source = dockEnvelope({ participant: true, revision: 2, status: 'IN_PROGRESS' }); return result; });
    fireEvent.click(await screen.findByRole('button', { name: 'Start work' }));
    await screen.findByText(/EOS verified the command receipt/);
    expect(post).toHaveBeenCalledTimes(1);
    expect(post.mock.calls[0][0]).toContain('/my-project/tasks/');
    expect(post.mock.calls[0][2].headers['Idempotency-Key']).toMatch(/^[a-f0-9-]{36}$/);
    expect(get.mock.calls.some(([path]) => path.endsWith('/transition-receipt'))).toBe(true);
    expect(screen.getByRole('button', { name: 'Complete task' })).toBeVisible();
  });
  it('does not announce success or admit a second click while the write is pending', async () => {
    let resolve;
    post.mockImplementation(() => new Promise(done => { resolve = done; }));
    mount(); const start = await screen.findByRole('button', { name: 'Start work' });
    fireEvent.click(start); fireEvent.click(start);
    await waitFor(() => expect(post).toHaveBeenCalledTimes(1));
    expect(screen.queryByText(/EOS verified the command receipt/)).not.toBeInTheDocument();
    source = dockEnvelope({ revision: 2, status: 'IN_PROGRESS' });
    await act(async () => resolve({ data: {} }));
    await screen.findByText(/EOS verified the command receipt/);
  });
  it('reconciles a possibly committed network failure using reads only', async () => {
    post.mockImplementation(async () => { source = dockEnvelope({ revision: 2, status: 'IN_PROGRESS' }); throw new Error('lost response'); });
    mount(); fireEvent.click(await screen.findByRole('button', { name: 'Start work' }));
    await screen.findByText(/Command outcome unverified/);
    expect(screen.getByRole('button', { name: 'Start work' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Reconcile task command' }));
    await screen.findByText(/EOS verified the command receipt/);
    expect(post).toHaveBeenCalledTimes(1);
  });
  it('rehydrates an uncertain committed command after unmount and reconciles without a second POST', async () => {
    const stableScope = scope();
    post.mockImplementation(async () => {
      source = dockEnvelope({ revision: 2, status: 'IN_PROGRESS' });
      throw new Error('synthetic lost HTTP response after source commit');
    });
    const first = mount({ scope: stableScope });
    fireEvent.click(await screen.findByRole('button', { name: 'Start work' }));
    await screen.findByText(/Command outcome unverified/);
    expect(post).toHaveBeenCalledTimes(1);
    // A complete component remount must recover the pending command through
    // session continuity metadata, not just the previous component's Map.
    first.unmount();
    mount({ scope: stableScope });
    const reconcile = await screen.findByRole('button', { name: 'Reconcile task command' });
    expect(screen.queryByRole('button', { name: 'Start work' })).not.toBeInTheDocument();
    fireEvent.click(reconcile);
    await screen.findByText(/EOS verified the command receipt/);
    expect(post).toHaveBeenCalledTimes(1);
    expect(get.mock.calls.some(([path]) => path.endsWith('/transition-receipt'))).toBe(true);
  });
  it('retains uncertainty when readback fails after an accepted POST, including permission revocation', async () => {
    failReceipt = true;
    mount(); fireEvent.click(await screen.findByRole('button', { name: 'Start work' }));
    await screen.findByText(/Command outcome unverified/);
    fireEvent.click(screen.getByRole('button', { name: 'Reconcile task command' }));
    await waitFor(() => expect(get.mock.calls.filter(([path]) => path.endsWith('/transition-receipt'))).toHaveLength(2));
    expect(post).toHaveBeenCalledTimes(1);
    expect(screen.queryByText(/EOS verified the command receipt/)).not.toBeInTheDocument();
  });
  it('rejects stale actions following source refresh or source permission revocation', async () => {
    mount(); const button = await screen.findByRole('button', { name: 'Start work' });
    source = dockEnvelope({ revision: 2, mutate: false });
    fireEvent.click(button);
    await screen.findByText(/Task or authority changed/);
    expect(post).not.toHaveBeenCalled();
    expect(screen.queryByRole('button', { name: 'Start work' })).not.toBeInTheDocument();
  });
  it('does not expose a foreign scope or unrecognized catalog after a successful GET', async () => {
    source.tenant_id = 'foreign'; mount();
    await screen.findByRole('button', { name: 'Retry authorized work' });
    expect(screen.queryByText('Align the Dock with authorized work.')).not.toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });
  it('suppresses late results when the principal or capacity changes during a write', async () => {
    let resolve; post.mockImplementation(() => new Promise(done => { resolve = done; }));
    const view = mount(); fireEvent.click(await screen.findByRole('button', { name: 'Start work' }));
    await waitFor(() => expect(post).toHaveBeenCalledTimes(1));
    view.rerender(<OperatingWork tenantId="foreign" principalId="foreign" scope="revoked"
      locator={{ workspace: 'HEADQUARTERS' }}/>);
    await act(async () => resolve({ data: {} }));
    expect(screen.queryByText(/EOS verified the command receipt/)).not.toBeInTheDocument();
    expect(record).not.toHaveBeenCalled();
    expect(get.mock.calls.filter(([path]) => path.endsWith('/transition-receipt'))).toHaveLength(0);
  });
  it('creates, edits, accepts and independently verifies one quarantined PDF artifact', async () => {
    mount(); fireEvent.click(await screen.findByRole('button', { name: 'Draft alignment plan' }));
    const editor = await screen.findByRole('textbox', { name: 'Edit plan' });
    expect(editor.value).toContain('No AI model invoked.');
    fireEvent.change(editor, { target: { value: 'Edited human-reviewed alignment checklist\n[ ] Verify EOS evidence' } });
    fireEvent.click(screen.getByRole('button', { name: 'Accept and attach PDF' }));
    await screen.findByText(/EOS independently verified the attached PDF/);
    expect(post).toHaveBeenCalledTimes(1);
    expect(post.mock.calls[0][0]).toContain('/my-project/tasks/');
    expect(post.mock.calls[0][1]).toBeInstanceOf(FormData);
    expect(screen.getByRole('textbox', { name: 'Edit plan' })).toHaveAttribute('readonly');
  });
  it('keeps an upload unsaved when the independent manifest is absent and reconciles without a duplicate', async () => {
    post.mockResolvedValue({ data: {} });
    mount(); fireEvent.click(await screen.findByRole('button', { name: 'Draft alignment plan' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Accept and attach PDF' }));
    await screen.findByText(/Attachment outcome unverified/);
    expect(screen.getByRole('button', { name: 'Accept and attach PDF' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Reconcile attachment' }));
    await waitFor(() => expect(get.mock.calls.filter(([path]) => path.endsWith('/attachments'))).toHaveLength(2));
    expect(post).toHaveBeenCalledTimes(1);
  });
  it('restores an uncertain attachment across unmount and verifies its manifest with no duplicate upload', async () => {
    const stableScope = scope();
    const original = post.getMockImplementation();
    let acceptedUpload = false;
    post.mockImplementation(async (...args) => {
      const result = await original(...args);
      if (args[0].endsWith('/attachments') && !acceptedUpload) {
        acceptedUpload = true;
        throw new Error('synthetic committed upload with lost HTTP response');
      }
      return result;
    });
    const initial = mount({ scope: stableScope });
    fireEvent.click(await screen.findByRole('button', { name: 'Draft alignment plan' }));
    fireEvent.change(await screen.findByRole('textbox', { name: 'Edit plan' }), {
      target: { value: 'Human-reviewed alignment plan; no unverified claims.' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Accept and attach PDF' }));
    await screen.findByText(/Attachment outcome unverified/);
    expect(post.mock.calls.filter(([path]) => path.endsWith('/attachments'))).toHaveLength(1);
    initial.unmount();

    mount({ scope: stableScope });
    expect(await screen.findByRole('button', { name: 'Reconcile attachment' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Accept and attach PDF' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Reconcile attachment' }));
    await screen.findByText(/EOS independently verified the attached PDF/);
    expect(post.mock.calls.filter(([path]) => path.endsWith('/attachments'))).toHaveLength(1);
    expect(get.mock.calls.some(([path]) => path.endsWith('/attachments'))).toBe(true);
    expect(screen.getByText(/quarantined pending scan clearance/i)).toBeVisible();
    expect(screen.getByRole('button', { name: 'Back to task' })).toBeEnabled();
  });

  it('discards an unaccepted draft without a write, and disables attachment without contributor admission', async () => {
    source = dockEnvelope({ mutate: false, attach: false });
    mount(); fireEvent.click(await screen.findByRole('button', { name: 'Draft alignment plan' }));
    expect(await screen.findByRole('button', { name: 'Accept and attach PDF' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Discard draft' }));
    expect(screen.queryByRole('textbox', { name: 'Edit plan' })).not.toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });
});

// ARTIFACT: WilsyDockOperatingWork.test.jsx
// VERSION: v1.9.3-ALIGNED-EVIDENCE-COLUMNS-CERT
// AUTHORITY BOUNDARY: synthetic UI tests only
// TENANT POSTURE: exact principal, tenant and capacity currentness
// FAIL-CLOSED POSTURE: no uncertain success, duplicate command or forged source
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
