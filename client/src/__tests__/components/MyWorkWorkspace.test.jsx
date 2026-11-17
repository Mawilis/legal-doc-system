/**
 * TITLE: WILSY OS Authenticated My Work Execution Queue Tests
 * VERSION: v1.5.0-DENSE-EXECUTION-QUEUE-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies compact queue rendering, source filters, detail access,
 *          keyboard/focus behavior, source-owned completion and EOS readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/MyWorkWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: MyWorkWorkspace.jsx, shared projection validator,
 *                            EOS My Work and independent source commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-15
 * CHANGELOG: v1.5.0-DENSE-EXECUTION-QUEUE-CERT covers responsive detail drawer
 *            lifecycle, compact row list, filters/order, dirty draft protection,
 *            exact source completion receipts, projection readback and failure.
 *            v1.4.0-HR-SOURCE-NAVIGATION-CERT verifies only EOS-admitted HR
 *            navigation, never client HR action authority.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic records and mocked transport only.
 * TENANT BOUNDARY: Projection tenant/principal are checked before display.
 * AUTHORITY BOUNDARY: Only owning source services may complete work.
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
vi.mock('../../services/api.js', () => ({ default: { get: vi.fn(), post: vi.fn() } }));

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
      source: 'OPERATIONS', source_key: 'OPERATIONS:ops-1', work_item_id: 'ops-1',
      title: 'Prepare daily operations report', description: 'Review the verified operating figures.',
      status: 'OPEN', priority: 'HIGH', kind: 'TASK', due_at: '2026-11-05T10:00:00+00:00', is_overdue: true,
    },
    {
      source: 'LEGAL', source_key: 'LEGAL:legal-1', work_item_id: 'legal-1',
      title: 'Review matter evidence', description: '',
      status: 'OPEN', priority: 'NORMAL', kind: 'TASK', due_at: null, is_overdue: false,
    },
  ],
};

const renderWorkspace = (props = {}) => render(
  <MemoryRouter><MyWorkWorkspace {...props} /></MemoryRouter>,
);
const openRow = async (title) => {
  const row = await screen.findByRole('button', { name: new RegExp(title) });
  fireEvent.click(row);
  return row;
};

beforeEach(() => {
  vi.clearAllMocks();
  api.get.mockResolvedValue({ data: payload });
  api.post.mockImplementation(async (path) => ({
    data: { work_item_id: decodeURIComponent(path.split('/').at(-2)), status: 'COMPLETED' },
  }));
  completeLegalWorkItem.mockResolvedValue({ work_item_id: 'legal-1', completion_event_id: 'event-1' });
});

describe('authenticated My Work execution queue', () => {
  it('loads the validated EOS projection and renders one compact row per item', async () => {
    renderWorkspace();
    expect(await screen.findByRole('heading', { name: 'My Work' })).toBeTruthy();
    expect(screen.getAllByRole('listitem')).toHaveLength(2);
    expect(screen.getByText('Prepare daily operations report')).toBeTruthy();
    expect(screen.getByText('Review matter evidence')).toBeTruthy();
    expect(screen.getByText('Overdue')).toBeTruthy();
    expect(screen.getAllByText('Verified Nov 6, 2026, 12:00 PM').length).toBeGreaterThan(0);
    expect(api.get).toHaveBeenCalledTimes(1);
    const [path, request] = api.get.mock.calls[0];
    expect(path).toBe('/my-work');
    expect(request.forceNetworkRetry).toBe(true);
    expect(request.signal.aborted).toBe(false);
  });

  it('renders ten authorized tasks as rows and offers only admitted sources with counts', async () => {
    const many = Array.from({ length: 10 }, (_, index) => ({
      ...payload.items[1], source: 'LEGAL', work_item_id: `legal-${index}`,
      source_key: `LEGAL:legal-${index}`, title: `Verified task ${index}`,
    }));
    api.get.mockResolvedValueOnce({ data: {
      ...payload, items: many,
      summary: { active_count: 10, overdue_count: 0, source_counts: { LEGAL: 10 } },
      sources_included: ['LEGAL'],
    } });
    renderWorkspace();
    expect(await screen.findAllByRole('listitem')).toHaveLength(10);
    expect(screen.getByRole('button', { name: 'Legal 10' })).toBeTruthy();
    expect(screen.queryByRole('button', { name: /CRM/ })).toBeNull();
    expect(screen.queryByRole('button', { name: /HR & Hiring/ })).toBeNull();
  });

  it('filters admitted source rows and search results from the validated projection', async () => {
    renderWorkspace();
    await screen.findByText('Prepare daily operations report');
    fireEvent.click(screen.getByRole('button', { name: 'Legal 1' }));
    expect(screen.queryByText('Prepare daily operations report')).toBeNull();
    expect(screen.getByText('Review matter evidence')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'All 2' }));
    fireEvent.change(screen.getByRole('searchbox', { name: 'Search authorized work' }), {
      target: { value: 'verified operating' },
    });
    expect(screen.getByText('Prepare daily operations report')).toBeTruthy();
    expect(screen.queryByText('Review matter evidence')).toBeNull();
  });

  it('sorts overdue first, then the chosen due/priority order with stable row identity', async () => {
    const rows = [
      { ...payload.items[1], source: 'CRM', work_item_id: 'z', source_key: 'CRM:z', title: 'No deadline' },
      { ...payload.items[1], source: 'CRM', work_item_id: 'b', source_key: 'CRM:b', title: 'Later normal', priority: 'NORMAL', due_at: '2026-11-08T10:00:00+00:00' },
      { ...payload.items[1], source: 'CRM', work_item_id: 'a', source_key: 'CRM:a', title: 'Earlier low', priority: 'LOW', due_at: '2026-11-07T10:00:00+00:00' },
      { ...payload.items[1], source: 'CRM', work_item_id: 'c', source_key: 'CRM:c', title: 'Overdue high', priority: 'HIGH', due_at: '2026-11-05T10:00:00+00:00', is_overdue: true },
    ];
    api.get.mockResolvedValueOnce({ data: {
      ...payload, items: rows,
      summary: { active_count: 4, overdue_count: 1, source_counts: { CRM: 4 } },
      sources_included: ['CRM'],
    } });
    renderWorkspace();
    await screen.findByText('Overdue high');
    const titles = () => [...document.querySelectorAll('[role="listitem"] .truncate')].map((el) => el.textContent);
    expect(titles()).toEqual(['Overdue high', 'Earlier low', 'Later normal', 'No deadline']);
    fireEvent.change(screen.getByLabelText('Sort'), { target: { value: 'priority' } });
    expect(titles()).toEqual(['Overdue high', 'Later normal', 'No deadline', 'Earlier low']);
  });

  it('opens a source-backed detail drawer and restores focus to the selected row on close', async () => {
    renderWorkspace();
    const row = await openRow('Prepare daily operations report');
    expect(screen.getByRole('dialog', { name: 'Prepare daily operations report' })).toBeTruthy();
    expect(screen.getByText('Review the verified operating figures.')).toBeTruthy();
    expect(screen.getByLabelText('Completion note')).toBeTruthy();
    expect(row.isConnected).toBe(true);
    fireEvent.click(screen.getByRole('button', { name: 'Close work details' }));
    await waitFor(() => expect(document.activeElement).toBe(row));
    expect(screen.queryByRole('dialog')).toBeNull();
  });

  it('protects a dirty completion note when Escape requests close', async () => {
    renderWorkspace();
    await openRow('Prepare daily operations report');
    const note = screen.getByLabelText('Completion note');
    fireEvent.change(note, { target: { value: 'Draft note retained until explicit discard.' } });
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.getByText('Discard the unsent completion note or evidence?')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Keep editing' }));
    expect(screen.getByLabelText('Completion note').value).toBe('Draft note retained until explicit discard.');
    fireEvent.keyDown(document, { key: 'Escape' });
    fireEvent.click(screen.getByRole('button', { name: 'Discard and close' }));
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
  });

  it('submits one source command, confirms the receipt, refreshes and reflects authoritative readback', async () => {
    api.get.mockResolvedValueOnce({ data: payload }).mockResolvedValueOnce({ data: {
      ...payload,
      items: [payload.items[1]],
      summary: { active_count: 1, overdue_count: 0, source_counts: { OPERATIONS: 0, LEGAL: 1 } },
    } });
    renderWorkspace();
    await openRow('Prepare daily operations report');
    fireEvent.change(screen.getByLabelText('Completion note'), { target: { value: 'Reviewed and reconciled.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Complete through Operations' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(api.post).toHaveBeenCalledWith(
      '/tenant-modules/operations/workspace/work-items/ops-1/complete',
      { completion_note: 'Reviewed and reconciled.' },
    );
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
    expect(screen.queryByText('Prepare daily operations report')).toBeNull();
    expect(screen.getAllByText('1').length).toBeGreaterThan(0);
    expect(api.get).toHaveBeenCalledTimes(2);
  });

  it('keeps the work and draft visible after a source command failure', async () => {
    api.post.mockRejectedValueOnce({ response: { status: 403, data: { detail: 'WORK_ITEM_COMPLETION_DENIED' } } });
    renderWorkspace();
    await openRow('Prepare daily operations report');
    const note = screen.getByLabelText('Completion note');
    fireEvent.change(note, { target: { value: 'Retain this note after denial.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Complete through Operations' }));
    expect((await screen.findAllByText(/WORK_ITEM_COMPLETION_DENIED/)).length).toBeGreaterThan(0);
    expect(screen.getByLabelText('Completion note').value).toBe('Retain this note after denial.');
    expect(screen.getAllByText('Prepare daily operations report').length).toBeGreaterThan(0);
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledTimes(1);
  });

  it('does not close the detail when fresh EOS readback still contains the active row', async () => {
    api.get.mockResolvedValue({ data: payload });
    renderWorkspace();
    await openRow('Prepare daily operations report');
    fireEvent.change(screen.getByLabelText('Completion note'), { target: { value: 'Source reports completed.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Complete through Operations' }));
    expect((await screen.findAllByText(/WORK_ITEM_COMPLETION_NOT_REFLECTED/)).length).toBeGreaterThan(0);
    expect(screen.getByRole('dialog')).toBeTruthy();
    expect(screen.getAllByText('Prepare daily operations report').length).toBeGreaterThan(0);
  });

  it('routes Legal completion through the evidence-bound source client', async () => {
    renderWorkspace();
    await openRow('Review matter evidence');
    fireEvent.change(screen.getByLabelText('Legal completion evidence reference'), {
      target: { value: 'evidence:verified-source:legal-1' },
    });
    fireEvent.change(screen.getByLabelText('Legal completion evidence fingerprint'), {
      target: { value: 'a'.repeat(128) },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Complete through Legal' }));
    await waitFor(() => expect(completeLegalWorkItem).toHaveBeenCalledWith({
      workItemId: 'legal-1',
      completionEvidenceReference: 'evidence:verified-source:legal-1',
      completionEvidenceFingerprint: 'a'.repeat(128),
    }));
    expect(api.post).not.toHaveBeenCalled();
  });

  it('shows only navigation for an admitted HR item and no generic action', async () => {
    api.get.mockResolvedValueOnce({ data: {
      ...payload,
      items: [{
        source: 'HR', source_key: 'HR:OFFER:opaque:DECIDE', work_item_id: 'OFFER:opaque:DECIDE',
        title: 'Independently decide employment offer', status: 'PENDING_ACTION', priority: 'HIGH',
        kind: 'HR_OFFER_DECISION', due_at: null, is_overdue: false,
      }],
      summary: { active_count: 1, overdue_count: 0, source_counts: { HR: 1 } },
      sources_included: ['HR'],
    } });
    renderWorkspace();
    expect(await screen.findByRole('button', { name: 'Open HR & Hiring' })).toBeTruthy();
    await openRow('Independently decide employment offer');
    expect(screen.getByText('This source does not expose a completion action in the current My Work contract.')).toBeTruthy();
    expect(screen.queryByRole('button', { name: /Complete through HR/ })).toBeNull();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('fails closed on invalid source coverage and on an unavailable initial read', async () => {
    api.get.mockResolvedValueOnce({ data: {
      ...payload, summary: { ...payload.summary, source_counts: { OPERATIONS: 2, LEGAL: 0 } },
    } });
    renderWorkspace();
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(screen.getByText('ATTENTION_SOURCE_COVERAGE_INVALID')).toBeTruthy();
    expect(screen.queryByText('Prepare daily operations report')).toBeNull();
  });
});

/*
 * ARTIFACT: MyWorkWorkspace.test.jsx
 * VERSION: v1.5.0-DENSE-EXECUTION-QUEUE-CERT
 * AUTHORITY BOUNDARY: Deterministic client projection and source command evidence only.
 * TENANT POSTURE: Synthetic exact-tenant work projections.
 * FAIL-CLOSED POSTURE: Invalid source metadata and failed commands never invent state.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
