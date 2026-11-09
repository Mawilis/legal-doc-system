/**
 * TITLE: WILSY OS Authenticated My Work Workspace Tests
 * VERSION: v1.3.0-EXPLICIT-FOCUS-RESET
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies server-projected My Work rendering and source-owned
 *          completion commands against the shared EOS projection contract.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/MyWorkWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: MyWorkWorkspace.jsx, the shared client projection
 *                            contract, and canonical source completion services.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.3.0-EXPLICIT-FOCUS-RESET proves parent null clears stale
 *            router focus while route-only focus remains covered separately.
 *            v1.2.0-SHARED-PROJECTION-CONTRACT supplies complete EOS projection
 *            metadata, requires the cancellable read signal, and rejects
 *            divergent source counts before rendering or enabling commands.
 *            v1.1.0-ABORTABLE-MY-WORK-READS requires My Work projections to
 *            use an abortable authenticated GET while preserving source-owned
 *            Legal, Operations, CRM and Intelligence completion routes.
 *            v1.0.0-SOURCE-OWNED-MY-WORK-COMMANDS covered queue projection
 *            and source command dispatch.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic records and mocked transport only.
 * TENANT BOUNDARY: Server-projected tenant and principal records only.
 * AUTHORITY BOUNDARY: Only owning EOS source services may complete work.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import MyWorkWorkspace from '../../components/workspaces/MyWorkWorkspace.jsx';
import api from '../../services/api.js';
import { completeLegalWorkItem } from '../../services/legalOperationsService.js';

vi.mock('../../services/legalOperationsService.js', () => ({
  completeLegalWorkItem: vi.fn(),
}));

vi.mock('../../services/api.js', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

const payload = {
  schema: 'WILSY-OS-UNIFIED-MY-WORK/V1',
  tenant_id: 'tenant-a',
  principal_id: 'principal-a',
  as_of: '2026-11-06T10:00:00+00:00',
  summary: {
    active_count: 2,
    overdue_count: 1,
    source_counts: { OPERATIONS: 1, LEGAL: 1 },
  },
  sources_included: ['OPERATIONS', 'LEGAL'],
  authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
  items: [
    {
      source: 'OPERATIONS',
      source_key: 'OPERATIONS:ops-1',
      work_item_id: 'ops-1',
      title: 'Prepare daily operations report',
      description: 'Review the verified operating figures.',
      status: 'OPEN',
      priority: 'HIGH',
      kind: 'TASK',
      due_at: '2026-11-05T10:00:00+00:00',
      is_overdue: true,
    },
    {
      source: 'LEGAL',
      source_key: 'LEGAL:legal-1',
      work_item_id: 'legal-1',
      title: 'Review matter evidence',
      status: 'OPEN',
      priority: 'NORMAL',
      kind: 'TASK',
      due_at: null,
      is_overdue: false,
    },
  ],
};

const renderWorkspace = () => render(
  <MemoryRouter>
    <MyWorkWorkspace />
  </MemoryRouter>,
);

describe('authenticated My Work workspace', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.get.mockResolvedValue({ data: payload });
    api.post.mockResolvedValue({ data: { status: 'COMPLETED' } });
    completeLegalWorkItem.mockResolvedValue({ work_item_id: 'legal-1', status: 'COMPLETED' });
  });

  it('loads an abortable server projection and presents only its authorized queue', async () => {
    renderWorkspace();
    expect(await screen.findByRole('heading', { name: 'My Work' })).toBeTruthy();
    expect(screen.getByText('Prepare daily operations report')).toBeTruthy();
    expect(screen.getByText('Review matter evidence')).toBeTruthy();
    expect(screen.getAllByText('Overdue').length).toBeGreaterThan(0);
    expect(api.get).toHaveBeenCalledTimes(1);
    const [path, request] = api.get.mock.calls[0];
    expect(path).toBe('/my-work');
    expect(request.forceNetworkRetry).toBe(true);
    expect(request.signal).toBeTruthy();
    expect(typeof request.signal.addEventListener).toBe('function');
    expect(request.signal.aborted).toBe(false);
  });

  it('clears older route focus when the parent explicitly supplies null', async () => {
    render(
      <MemoryRouter initialEntries={[{
        pathname: '/my-work',
        state: { focusWorkItem: 'OPERATIONS:ops-1' },
      }]}>
        <MyWorkWorkspace focusWorkItem={null} />
      </MemoryRouter>,
    );
    const heading = await screen.findByText('Prepare daily operations report');
    expect(heading.closest('article').className).not.toContain('ring-2');
  });

  it('rejects inconsistent source counts before rendering any source work', async () => {
    api.get.mockResolvedValueOnce({
      data: {
        ...payload,
        summary: {
          ...payload.summary,
          source_counts: { OPERATIONS: 2, LEGAL: 0 },
        },
      },
    });
    renderWorkspace();
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(screen.getByText('ATTENTION_SOURCE_COVERAGE_INVALID')).toBeTruthy();
    expect(screen.queryByText('Prepare daily operations report')).toBeNull();
    expect(screen.queryByText('Review matter evidence')).toBeNull();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('routes completion to the owning module command and refreshes the projection', async () => {
    api.get
      .mockResolvedValueOnce({ data: payload })
      .mockResolvedValueOnce({
        data: {
          ...payload,
          items: [payload.items[1]],
          summary: {
            active_count: 1,
            overdue_count: 0,
            source_counts: { OPERATIONS: 0, LEGAL: 1 },
          },
        },
      });
    renderWorkspace();
    const note = await screen.findByLabelText('Completion note for Prepare daily operations report');
    fireEvent.change(note, { target: { value: 'Report checked against the approved daily figures.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Complete' }));

    await waitFor(() => expect(api.post).toHaveBeenCalledWith(
      '/tenant-modules/operations/workspace/work-items/ops-1/complete',
      { completion_note: 'Report checked against the approved daily figures.' },
    ));
    await waitFor(() => expect(screen.queryByText('Prepare daily operations report')).toBeNull());
  });

  it('routes Legal completion through the canonical evidence-bound command', async () => {
    renderWorkspace();
    expect(await screen.findByText('Review matter evidence')).toBeTruthy();
    const reference = screen.getByLabelText('Legal completion evidence reference for Review matter evidence');
    const fingerprint = screen.getByLabelText('Legal completion evidence fingerprint for Review matter evidence');
    const submit = screen.getByRole('button', { name: 'Submit evidenced Legal completion' });
    expect(submit.disabled).toBe(true);
    fireEvent.change(reference, { target: { value: 'evidence:verified-source:legal-1' } });
    fireEvent.change(fingerprint, { target: { value: 'a'.repeat(128) } });
    fireEvent.click(submit);
    await waitFor(() => expect(completeLegalWorkItem).toHaveBeenCalledWith({
      workItemId: 'legal-1',
      completionEvidenceReference: 'evidence:verified-source:legal-1',
      completionEvidenceFingerprint: 'a'.repeat(128),
    }));
    expect(api.post).not.toHaveBeenCalled();
  });

  it('fails closed and displays no stale queue when the authenticated API is unavailable', async () => {
    api.get.mockRejectedValueOnce({ response: { status: 503, data: { detail: 'MY_WORK_SOURCE_UNAVAILABLE' } } });
    renderWorkspace();
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(screen.queryByText('Prepare daily operations report')).toBeNull();
    expect(screen.getByText('MY_WORK_SOURCE_UNAVAILABLE')).toBeTruthy();
  });
});

describe.each([
  ['CRM', 'crm-1', '/crm/owner-workspace/work-items/crm-1/complete'],
  ['INTELLIGENCE', 'intel-1', '/tenant-modules/intelligence/workspace/work-items/intel-1/complete'],
])('%s source command ownership', (source, workItemId, expectedPath) => {
  it('routes completion to the owning source service', async () => {
    const item = {
      ...payload.items[0],
      source,
      source_key: source + ':' + workItemId,
      work_item_id: workItemId,
      title: source + ' action',
      is_overdue: false,
    };
    api.get.mockResolvedValue({
      data: {
        ...payload,
        items: [item],
        summary: { active_count: 1, overdue_count: 0, source_counts: { [source]: 1 } },
        sources_included: [source],
      },
    });
    renderWorkspace();
    const note = await screen.findByLabelText('Completion note for ' + item.title);
    fireEvent.change(note, { target: { value: 'Verified ' + source + ' completion.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Complete' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledWith(
      expectedPath,
      { completion_note: 'Verified ' + source + ' completion.' },
    ));
  });
});

/*
 * ARTIFACT: MyWorkWorkspace.test.jsx
 * VERSION: v1.3.0-EXPLICIT-FOCUS-RESET
 * AUTHORITY BOUNDARY: Deterministic client contract evidence only.
 * TENANT POSTURE: Synthetic exact-tenant work projections.
 * FAIL-CLOSED POSTURE: Unavailable reads and invalid source metadata render no stale work.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
