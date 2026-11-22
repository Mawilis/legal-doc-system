/**
 * TITLE: WILSY OS Project Work Purpose Authenticated UI Certificate
 * VERSION: v1.0.0-SOURCE-CLASSIFICATION-READBACK-CERT
 * AUTHORITY: Synthetic UI verification only; EOS exclusively admits commands.
 * EPITOME: Tests source-verified purpose, human rationale, CAS and readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProjectWorkPurposePanel.test.jsx
 * COLLABORATION / OWNERSHIP: ProjectWorkPurposePanel, project source API contract.
 * CERTIFICATION / UPDATE DATE: 2026-11-23
 * CHANGELOG: v1.0.0-SOURCE-CLASSIFICATION-READBACK-CERT verifies no
 * unauthorized controls, authoritative initial purpose, exact revisioned
 * command, independent GET confirmation and unreadable/stale source denial.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Synthetic actor IDs and in-process HTTP stubs.
 * TENANT BOUNDARY: Full source response coordinates checked on readback.
 * AUTHORITY BOUNDARY: Client never grants project:update or signs evidence.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import ProjectWorkPurposePanel, { assertPurpose } from '../../components/workspaces/ProjectWorkPurposePanel.jsx';
import api from '../../services/api.js';

vi.mock('../../services/api.js', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

const TENANT = 'synthetic-tenant';
const PRINCIPAL = 'synthetic-project-owner';
const PROJECT = 'prj-' + 'a'.repeat(48);
const TASK = { task_id: 'ptk-' + 'b'.repeat(48), revision: 3 };
const HEADERS = { 'X-Tenant-ID': TENANT };
const props = {
  task: TASK, projectId: PROJECT, tenantId: TENANT,
  principalId: PRINCIPAL, tenantHeaders: HEADERS, canClassify: true,
};
const result = (audience = 'UNCLASSIFIED', purposeRevision = 0) => ({
  schema: 'WILSY-PROJECT-WORK-PURPOSE/V1',
  tenant_id: TENANT, principal_id: PRINCIPAL,
  project_id: PROJECT, task_id: TASK.task_id,
  task_revision: TASK.revision, purpose_revision: purposeRevision,
  audience, evidence_ref: audience === 'UNCLASSIFIED' ? null
    : 'project-work-purpose:synthetic-audit',
  source_revision: audience === 'UNCLASSIFIED' ? null : TASK.revision,
  critical_gate: false,
});

describe('source-owned work purpose panel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal('crypto', { randomUUID: () => 'synthetic-unique-command' });
  });
  afterEach(() => { vi.unstubAllGlobals(); });

  it('shows source-owned unclassified status and hides mutation from a read-only capacity', async () => {
    api.get.mockResolvedValue({ data: result() });
    render(<ProjectWorkPurposePanel {...props} canClassify={false}/>);
    expect(await screen.findByText('Needs classification')).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Save audited classification' })).toBeNull();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('persists selected purpose with reason, CAS, stable key and independent EOS readback', async () => {
    api.get.mockResolvedValueOnce({ data: result() })
      .mockResolvedValueOnce({ data: result('OPERATING', 1) });
    api.post.mockResolvedValue({ data: result('OPERATING', 1) });
    render(<ProjectWorkPurposePanel {...props}/>);
    await screen.findByText('Needs classification');
    fireEvent.change(screen.getByRole('combobox', { name: 'Classify project work purpose' }),
      { target: { value: 'OPERATING' } });
    fireEvent.change(screen.getByRole('textbox', { name: 'Work classification rationale' }),
      { target: { value: 'This activity operates our current business.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save audited classification' }));
    await screen.findByText('Source classification verified and audit persisted in EOS.');
    expect(api.post).toHaveBeenCalledWith(
      expect.stringContaining('/work-purpose'),
      {
        audience: 'OPERATING',
        reason: 'This activity operates our current business.',
        expected_task_revision: 3,
        expected_purpose_revision: 0,
      },
      { headers: { ...HEADERS, 'Idempotency-Key': 'synthetic-unique-command' } },
    );
    expect(api.get).toHaveBeenCalledTimes(2);
  });

  it('never accepts foreign scope or forged task revision as source truth', () => {
    expect(() => assertPurpose({ ...result('OPERATING', 1), tenant_id: 'other' }, props))
      .toThrow('PROJECT_WORK_PURPOSE_READBACK_INVALID');
    expect(() => assertPurpose({ ...result('OPERATING', 1), task_revision: 2 }, props))
      .toThrow('PROJECT_WORK_PURPOSE_READBACK_INVALID');
    expect(() => assertPurpose({ ...result('OPERATING', 1), evidence_ref: null }, props))
      .toThrow('PROJECT_WORK_PURPOSE_READBACK_INVALID');
  });

  it('preserves unclassified work when EOS source cannot be verified', async () => {
    api.get.mockRejectedValue({ response: { status: 503 } });
    render(<ProjectWorkPurposePanel {...props}/>);
    expect(await screen.findByText(/EOS could not verify the current work classification/)).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Save audited classification' })).toBeNull();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('accepts unclassified with nonzero persisted purpose revision after a task edit', () => {
    expect(assertPurpose(result('UNCLASSIFIED', 2), props).purpose_revision).toBe(2);
  });
});

// ARTIFACT: ProjectWorkPurposePanel.test.jsx
// VERSION: v1.0.0-SOURCE-CLASSIFICATION-READBACK-CERT
// AUTHORITY BOUNDARY: Source read/command UI verification only.
// TENANT POSTURE: Exact tenant/task/revision equality.
// FAIL-CLOSED POSTURE: No success until independent source readback.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
