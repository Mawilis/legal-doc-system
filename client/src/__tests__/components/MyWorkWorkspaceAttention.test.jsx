/**
 * TITLE: WILSY OS Source-owned My Work Attention Handoff Contract
 * VERSION: v1.1.0-NAVIGATION-SCOPE-CURRENTNESS-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Checks source-verified task focus and real canonical completion
 *          command invocation after a daily attention work-item selection.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/MyWorkWorkspaceAttention.test.jsx
 * COLLABORATION / OWNERSHIP: MyWorkWorkspace.jsx, EOS /my-work and
 *                            source-owned module completion commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.1.0-NAVIGATION-SCOPE-CURRENTNESS-CERT adds same-route source
 *            refresh, late-response rejection and authenticated-scope isolation.
 *            v1.0.1-EFFECT-FLUSH-FOCUS-CERT waited for React's
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
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, useNavigate } from 'react-router-dom';
import AuthContext from '../../contexts/authContext.jsx';
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

function NavigationHarness() {
  const navigate = useNavigate();
  return <><button onClick={() => navigate('/my-work', {state: {focusWorkItem: item.source_key}})}>
    Open attention item
  </button><MyWorkWorkspace /></>;
}

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

  it('re-reads EOS when attention selects newly arrived work on the same route', async () => {
    api.get.mockResolvedValueOnce({data: {...payload, items: [], summary: {active_count: 0, overdue_count: 0}}})
      .mockResolvedValueOnce({data: payload});
    render(<MemoryRouter initialEntries={['/my-work']}><NavigationHarness /></MemoryRouter>);
    await screen.findByText('You’re clear');
    fireEvent.click(screen.getByRole('button', {name: 'Open attention item'}));
    const card = (await screen.findByText(item.title)).closest('article');
    await waitFor(() => expect(document.activeElement).toBe(card));
    expect(api.get).toHaveBeenCalledTimes(2);
    expect(api.post).not.toHaveBeenCalled();
  });

  it('rejects a late previous navigation read after the current source readback', async () => {
    let resolveOld;
    api.get.mockImplementationOnce(() => new Promise(resolve => {resolveOld = resolve;}))
      .mockResolvedValueOnce({data: payload});
    render(<MemoryRouter initialEntries={['/my-work']}><NavigationHarness /></MemoryRouter>);
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByRole('button', {name: 'Open attention item'}));
    await screen.findByText(item.title);
    await act(async () => resolveOld({data: {...payload, items: [{...item, title: 'Obsolete source snapshot'}]}}));
    expect(screen.queryByText('Obsolete source snapshot')).toBeNull();
    expect(screen.getByText(item.title)).toBeTruthy();
  });

  it('clears prior-scope work and drafts on authenticated tenant and capacity changes', async () => {
    const userA = {id: 'principal-a', tenantId: 'tenant-a', role: 'TENANT_OWNER', businessRole: 'tenant_owner'};
    const userB = {id: 'principal-b', tenantId: 'tenant-b', role: 'TENANT_OWNER', businessRole: 'tenant_partner'};
    const other = {...item, title: 'Second tenant task'};
    api.get.mockResolvedValueOnce({data: {...payload, tenant_id: userA.tenantId, principal_id: userA.id}})
      .mockResolvedValueOnce({data: {...payload, tenant_id: userB.tenantId, principal_id: userB.id, items: [other]}});
    const harness = user => <AuthContext.Provider value={{user}}>
      <MemoryRouter><MyWorkWorkspace /></MemoryRouter>
    </AuthContext.Provider>;
    const {rerender} = render(harness(userA));
    await screen.findByText(item.title);
    fireEvent.change(screen.getByRole('textbox', {name: 'Completion note for ' + item.title}), {
      target: {value: 'Prior-scope private draft'},
    });
    rerender(harness(userB));
    expect(screen.queryByText(item.title)).toBeNull();
    await screen.findByText(other.title);
    expect(screen.getByRole('textbox', {name: 'Completion note for ' + other.title}).value).toBe('');
    expect(api.post).not.toHaveBeenCalled();
  });

  it('fails closed when a source returns a foreign tenant or principal', async () => {
    const user = {id: 'principal-a', tenantId: 'tenant-a'};
    api.get.mockResolvedValueOnce({data: {...payload, tenant_id: 'tenant-b', principal_id: user.id}});
    render(<AuthContext.Provider value={{user}}><MemoryRouter><MyWorkWorkspace /></MemoryRouter></AuthContext.Provider>);
    await screen.findByRole('alert');
    expect(screen.getByText('MY_WORK_SCOPE_MISMATCH')).toBeTruthy();
    expect(screen.queryByText(item.title)).toBeNull();
    expect(api.post).not.toHaveBeenCalled();
  });
});

/*
 * ARTIFACT: MyWorkWorkspaceAttention.test.jsx
 * VERSION: v1.1.0-NAVIGATION-SCOPE-CURRENTNESS-CERT
 * AUTHORITY BOUNDARY: Source-owned completion route only.
 * TENANT POSTURE: Only EOS-provided work list may be highlighted.
 * FAIL-CLOSED POSTURE: Forged state cannot add an action item.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS only.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
