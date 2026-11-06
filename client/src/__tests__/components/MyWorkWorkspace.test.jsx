import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import MyWorkWorkspace from '../../components/workspaces/MyWorkWorkspace.jsx';
import api from '../../services/api.js';

vi.mock('../../services/api.js', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

const payload = {
  tenant_id: 'tenant-a',
  principal_id: 'principal-a',
  as_of: '2026-11-06T10:00:00+00:00',
  summary: { active_count: 2, overdue_count: 1 },
  sources_included: ['OPERATIONS', 'LEGAL'],
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
  });

  it('loads and presents only the server-projected authorized queue', async () => {
    renderWorkspace();
    expect(await screen.findByRole('heading', { name: 'My Work' })).toBeTruthy();
    expect(screen.getByText('Prepare daily operations report')).toBeTruthy();
    expect(screen.getByText('Review matter evidence')).toBeTruthy();
    expect(screen.getAllByText('Overdue').length).toBeGreaterThan(0);
    expect(api.get).toHaveBeenCalledWith('/my-work', { forceNetworkRetry: true });
  });

  it('routes completion to the owning module command and refreshes the projection', async () => {
    api.get
      .mockResolvedValueOnce({ data: payload })
      .mockResolvedValueOnce({ data: { ...payload, items: [payload.items[1]], summary: { active_count: 1, overdue_count: 0 } } });
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

  it('does not invent a generic Legal completion command', async () => {
    renderWorkspace();
    expect(await screen.findByText('Review matter evidence')).toBeTruthy();
    expect(screen.getByText(/Legal completion must be recorded in the owning Legal workflow/i)).toBeTruthy();
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
      source_key: `${source}:${workItemId}`,
      work_item_id: workItemId,
      title: `${source} action`,
      is_overdue: false,
    };
    api.get.mockResolvedValue({ data: { ...payload, items: [item], summary: { active_count: 1, overdue_count: 0 } } });
    renderWorkspace();
    const note = await screen.findByLabelText(`Completion note for ${item.title}`);
    fireEvent.change(note, { target: { value: `Verified ${source} completion.` } });
    fireEvent.click(screen.getByRole('button', { name: 'Complete' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledWith(
      expectedPath,
      { completion_note: `Verified ${source} completion.` },
    ));
  });
});
