/**
 * TITLE: WILSY OS Source-owned My Work Attention Handoff Contract
 * VERSION: v1.0.1-EFFECT-FLUSH-FOCUS-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Checks source-verified task focus and real canonical completion
 *          command invocation after a daily attention work-item selection.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/MyWorkWorkspaceAttention.test.jsx
 * COLLABORATION / OWNERSHIP: MyWorkWorkspace.jsx, EOS /my-work and
 *                            source-owned module completion commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.1-EFFECT-FLUSH-FOCUS-CERT waits for React's
 *            async item-focus effect before asserting real keyboard focus.
 *            v1.0.0-ATTENTION-SELECTED-COMPLETION-CERT covers selected
 *            work item navigation, actual server command and forged focus denial.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic records and stubbed API, no credentials.
 * TENANT BOUNDARY: Browser route state never inserts unauthorised work.
 * AUTHORITY BOUNDARY: Completion must go through owning EOS source route.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import api from '../../services/api.js';
import MyWorkWorkspace from '../../components/workspaces/MyWorkWorkspace.jsx';

vi.mock('../../services/api.js', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));
vi.mock('../../services/legalOperationsService.js', () => ({
  completeLegalWorkItem: vi.fn(),
}));

const item = {
  source: 'OPERATIONS', source_key: 'OPERATIONS:WORK-1',
  work_item_id: 'WORK-1', kind: 'TASK',
  title: 'Confirm dispatch evidence', description: 'Source-generated work',
  status: 'OPEN', priority: 'HIGH', is_overdue: false, due_at: null,
};
const payload = {
  as_of: '2026-11-09T06:00:00+00:00',
  items: [item],
  summary: {active_count: 1, overdue_count: 0},
  sources_included: ['OPERATIONS'],
};

const renderWithFocus = (focusWorkItem) => render(
  <MemoryRouter initialEntries={[{
    pathname: '/my-work', state: { focusWorkItem },
  }]}>
    <MyWorkWorkspace />
  </MemoryRouter>,
);

beforeEach(() => {
  vi.clearAllMocks();
  api.get.mockResolvedValue({data: payload});
  api.post.mockResolvedValue({data: {status: 'COMPLETED'}});
});

describe('Daily attention selected My Work action', () => {
  it('focuses the verified item and invokes the real source-owned completion route', async () => {
    renderWithFocus(item.source_key);
    const heading = await screen.findByText('Confirm dispatch evidence');
    const card = heading.closest('article');
    expect(card).not.toBeNull();
    expect(card.className).toContain('ring-2');
    await waitFor(() => expect(document.activeElement).toBe(card));
    fireEvent.change(screen.getByRole('textbox', {name: 'Completion note for Confirm dispatch evidence'}), {
      target: {value: 'Verified authorised dispatch evidence'},
    });
    fireEvent.click(screen.getByRole('button', {name: 'Complete'}));
    await waitFor(() => expect(api.post).toHaveBeenCalledWith(
      '/tenant-modules/operations/workspace/work-items/WORK-1/complete',
      {completion_note: 'Verified authorised dispatch evidence'},
    ));
  });

  it('never creates or highlights an item from a forged route-state work key', async () => {
    renderWithFocus('OPERATIONS:NOT-AUTHORISED');
    const heading = await screen.findByText('Confirm dispatch evidence');
    expect(heading.closest('article').className).not.toContain('ring-2');
    expect(screen.queryByText('NOT-AUTHORISED')).toBeNull();
    expect(api.post).not.toHaveBeenCalled();
  });
});

/*
 * ARTIFACT: MyWorkWorkspaceAttention.test.jsx
 * VERSION: v1.0.1-EFFECT-FLUSH-FOCUS-CERT
 * AUTHORITY BOUNDARY: Source-owned completion route only.
 * TENANT POSTURE: Only EOS-provided work list may be highlighted.
 * FAIL-CLOSED POSTURE: Forged state cannot add an action item.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS only.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
