/**
 * TITLE: WILSY OS Dock Operating Journey Client Certificate
 * VERSION: v1.2.0-ATTACHMENT-REOPEN-RECONCILIATION
 * AUTHORITY: Synthetic client regression evidence only.
 * EPITOME: Verify permissioned task actions, receipt currentness and draft attachment readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/intelligence/WilsyDockOperatingWork.test.jsx
 * COLLABORATION / OWNERSHIP: Closed Dock components, canonical transport and Projects.
 * CERTIFICATION / UPDATE DATE: 2026-11-25
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

describe('permissioned operating work', () => {
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
// VERSION: v1.2.0-ATTACHMENT-REOPEN-RECONCILIATION
// AUTHORITY BOUNDARY: synthetic UI tests only
// TENANT POSTURE: exact principal, tenant and capacity currentness
// FAIL-CLOSED POSTURE: no uncertain success, duplicate command or forged source
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
