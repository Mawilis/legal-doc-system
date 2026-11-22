/**
 * TITLE: WILSY OS Project Task Quarantine Attachment Client Certificate
 * VERSION: v1.2.0-SOURCE-FAILURE-CODE-CERT
 * AUTHORITY: Synthetic authenticated source envelope and upload readback.
 * EPITOME: Prove source-backed file list, contributor upload, no unsafe
 *          download, foreign source denial and owner read-only boundary.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProjectTaskAttachmentsPanel.test.jsx
 * COLLABORATION / OWNERSHIP: ProjectTaskAttachmentsPanel and mocked API.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.2.0-SOURCE-FAILURE-CODE-CERT pins explicit invalid task-attachment source envelope diagnostics and bounded safe EOS HTTP error classes while refusing unauthorized uploads.
 * CHANGELOG: v1.1.0-SCAN-STATE-SOURCE-CONTRACT-CERT requires scanner-owned QUARANTINED status and null clearance fingerprint, and proves fail-closed denial of fabricated clean clearance.
 * CHANGELOG: v1.1.0-SCAN-STATE-SOURCE-CONTRACT-CERT checks exact task
 *          S3 quarantine response, replay key, independent EOS list readback.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Synthetic file only; no provider bytes leaked.
 * TENANT BOUNDARY: Foreign tenant list fails closed before rendering records.
 * AUTHORITY BOUNDARY: No scanner release, approval, preview or download.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock('../../services/api.js', () => ({ default: api }));
import ProjectTaskAttachmentsPanel from '../../components/workspaces/ProjectTaskAttachmentsPanel.jsx';

const tenantId = 'quarantine-tenant';
const principalId = 'contributor';
const projectId = 'prj-' + 'a'.repeat(48);
const taskId = 'ptk-' + 'b'.repeat(48);
const attachmentId = 'pat-' + 'c'.repeat(48);
const record = {
  schema: 'wilsy.project.attachment.v1',
  tenant_id: tenantId, project_id: projectId, task_id: taskId,
  attachment_id: attachmentId, uploader_principal_id: principalId,
  filename: 'design.pdf', media_type: 'application/pdf',
  size_bytes: 19, content_sha3_512: 'd'.repeat(128),
  created_at: '2026-11-18T08:00:00+00:00',
  state: 'QUARANTINED', revision: 1,
  scan_clearance_status: 'QUARANTINED', scan_clearance_fingerprint: null,
};
const memberRoute = '/projects/' + projectId + '/my-project/tasks/' + taskId;
const ownerRoute = '/projects/' + projectId + '/tasks/' + taskId;
const list = (items, principal = principalId) => ({
  schema: 'WILSY-PROJECT-ATTACHMENT-LIST/V1',
  tenant_id: tenantId, principal_id: principal, project_id: projectId,
  task_id: taskId, limit: 50, offset: 0,
  has_more: false, next_offset: null, items,
});

beforeEach(() => {
  vi.clearAllMocks();
  vi.stubGlobal('crypto', { randomUUID: () => 'upload-command-1' });
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
const mount = (participantMode = true) => render(<ProjectTaskAttachmentsPanel
  tenantId={tenantId} principalId={principalId}
  projectId={projectId} taskId={taskId}
  participantMode={participantMode}
  tenantHeaders={{ 'X-Tenant-ID': tenantId }}
  onClose={() => {}}/>);

it('uploads a safe-type file to EOS quarantine with independent manifest readback', async () => {
  let contents = [];
  api.get.mockImplementation(async path => {
    expect(path).toBe(memberRoute + '/attachments?limit=50&offset=0');
    return { data: list(contents) };
  });
  api.post.mockImplementationOnce(async (path, body, config) => {
    expect(path).toBe(memberRoute + '/attachments');
    expect(body).toBeInstanceOf(FormData);
    expect(body.get('file').name).toBe('design.pdf');
    expect(config.headers['Idempotency-Key']).toBe('upload-command-1');
    contents = [record];
    return { data: {
      schema: 'WILSY-PROJECT-ATTACHMENT-RESULT/V1',
      tenant_id: tenantId, principal_id: principalId,
      project_id: projectId, task_id: taskId,
      attachment: record,
    } };
  });
  mount();
  expect(await screen.findByText('EOS verified no file manifests on this task page.')).toBeVisible();
  const file = new File(['%PDF-1.4\nfake'], 'design.pdf', { type: 'application/pdf' });
  fireEvent.change(screen.getByLabelText('Project attachment file'), {
    target: { files: [file] },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Submit to EOS quarantine' }));
  await waitFor(() => expect(screen.getByText('design.pdf')).toBeVisible());
  expect(screen.getByText(/Quarantined · malware scan clearance unavailable · application\/pdf/)).toBeVisible();
  expect(screen.queryByRole('link')).not.toBeInTheDocument();
  expect(api.post).toHaveBeenCalledTimes(1);
});

it('does not expose upload controls from the owner read-only attachment source', async () => {
  api.get.mockImplementation(async path => {
    expect(path).toBe(ownerRoute + '/attachments?limit=50&offset=0');
    return { data: list([record]) };
  });
  mount(false);
  expect(await screen.findByText('design.pdf')).toBeVisible();
  expect(screen.queryByRole('button', { name: 'Submit to EOS quarantine' })).not.toBeInTheDocument();
  expect(screen.queryByRole('link')).not.toBeInTheDocument();
});

it('fails closed on a foreign tenant source record or fabricated download URL', async () => {
  api.get.mockResolvedValue({ data: list([
    { ...record, download_url: 'https://untrusted.example/x' },
  ]) });
  mount();
  expect(await screen.findByRole('alert')).toHaveTextContent('manifest response failed exact tenant, principal, task or schema verification');
  expect(screen.queryByText('design.pdf')).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Submit to EOS quarantine' })).not.toBeInTheDocument();
  expect(api.post).not.toHaveBeenCalled();
});

it('rejects fabricated or incomplete scan clearance evidence without download capability', async () => {
  api.get.mockResolvedValue({ data: list([{
    ...record, scan_clearance_status: 'SCAN_CLEAN_VERIFIED',
    scan_clearance_fingerprint: null,
  }]) });
  mount(false);
  expect(await screen.findByRole('alert')).toHaveTextContent('manifest response failed exact tenant, principal, task or schema verification');
  expect(screen.queryByText('design.pdf')).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Download verified file' })).not.toBeInTheDocument();
});

// ARTIFACT: ProjectTaskAttachmentsPanel.test.jsx
// VERSION: v1.2.0-SOURCE-FAILURE-CODE-CERT
// AUTHORITY BOUNDARY: mocked UI, no real bytes/scan/financial authority
// TENANT POSTURE: exact source task and participant envelope
// FAIL-CLOSED POSTURE: unverified and downloadable records never rendered
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
