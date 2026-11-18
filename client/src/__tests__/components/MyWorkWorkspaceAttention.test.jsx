/**
 * TITLE: WILSY OS Source-owned My Work Attention Handoff Tests
 * VERSION: v1.4.0-QUEUE-DETAIL-HANDOFF-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Verifies that Daily Attention and Headquarters focus only exact
 *          work keys admitted by fresh EOS projection and retain session scope.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/MyWorkWorkspaceAttention.test.jsx
 * COLLABORATION / OWNERSHIP: MyWorkWorkspace.jsx, shared projection validator,
 *                            EOS /api/my-work and source-owned completion routes.
 * CERTIFICATION / UPDATE DATE: 2026-11-15
 * CHANGELOG: v1.4.0-QUEUE-DETAIL-HANDOFF-CERT validates compact queue row
 *            highlighting, focused detail handoff, current session isolation,
 *            route refresh and dirty draft clearing when authority scope changes.
 *            v1.3.0-SHARED-PROJECTION-FOCUS-HANDOFF certified source-key handoff
 *            and session-generation invalidation before the queue refactor.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic exact-scope records and mocked reads only.
 * TENANT BOUNDARY: Route state never inserts unauthorized work.
 * AUTHORITY BOUNDARY: Source-owned completion endpoints remain exclusive.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, useNavigate } from 'react-router-dom';
import AuthContext from '../../contexts/authContext.jsx';
import api from '../../services/api.js';
import MyWorkWorkspace from '../../components/workspaces/MyWorkWorkspace.jsx';

vi.mock('../../services/api.js', () => ({ default: { get: vi.fn(), post: vi.fn() } }));
vi.mock('../../services/legalOperationsService.js', () => ({ completeLegalWorkItem: vi.fn() }));

const item = {
  source: 'OPERATIONS', source_key: 'OPERATIONS:WORK-1', work_item_id: 'WORK-1',
  kind: 'TASK', title: 'Confirm dispatch evidence', description: 'Source-generated work',
  status: 'OPEN', priority: 'HIGH', is_overdue: false, due_at: null,
};
const payload = {
  schema: 'WILSY-OS-UNIFIED-MY-WORK/V1', tenant_id: 'tenant-a', principal_id: 'principal-a',
  as_of: '2026-11-09T06:00:00+00:00', items: [item],
  summary: { active_count: 1, overdue_count: 0, source_counts: { OPERATIONS: 1 } },
  sources_included: ['OPERATIONS'],
  authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
};
const selectedRow = () => document.querySelector('[role="listitem"] > button');

const renderWithFocus = (focusWorkItem) => render(
  <MemoryRouter initialEntries={[{ pathname: '/my-work', state: { focusWorkItem } }]}>
    <MyWorkWorkspace />
  </MemoryRouter>,
);
function NavigationHarness() {
  const navigate = useNavigate();
  return <><button onClick={() => navigate('/my-work', { state: { focusWorkItem: item.source_key } })}>Open attention item</button><MyWorkWorkspace /></>;
}

beforeEach(() => {
  vi.clearAllMocks();
  api.get.mockResolvedValue({ data: payload });
  api.post.mockResolvedValue({ data: { work_item_id: item.work_item_id, status: 'COMPLETED' } });
});

describe('Daily Attention and Headquarters My Work handoff', () => {
  it('opens only the EOS-admitted work selected by route state', async () => {
    renderWithFocus(item.source_key);
    await screen.findByRole('dialog', { name: item.title });
    expect(selectedRow().closest('article').className).toContain('ring-2');
    await waitFor(() => expect(document.activeElement).toBe(screen.getByRole('button', { name: 'Close work details' })));
    expect(api.get).toHaveBeenCalledTimes(1);
    expect(api.post).not.toHaveBeenCalled();
  });

  it('opens the exact verified source key supplied by Headquarters', async () => {
    render(<MemoryRouter><MyWorkWorkspace focusWorkItem={item.source_key} /></MemoryRouter>);
    await screen.findByRole('dialog', { name: item.title });
    expect(selectedRow().closest('article').className).toContain('ring-2');
    expect(api.post).not.toHaveBeenCalled();
  });

  it('does not create or highlight a record from a forged route key', async () => {
    renderWithFocus('OPERATIONS:NOT-AUTHORISED');
    await screen.findByText(item.title);
    expect(selectedRow().getAttribute('aria-pressed')).toBe('false');
    expect(screen.queryByText('NOT-AUTHORISED')).toBeNull();
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('re-reads EOS when Attention hands off newly arrived work on the same route', async () => {
    api.get.mockResolvedValueOnce({ data: {
      ...payload, items: [], summary: { active_count: 0, overdue_count: 0, source_counts: { OPERATIONS: 0 } },
    } }).mockResolvedValueOnce({ data: payload });
    render(<MemoryRouter initialEntries={['/my-work']}><NavigationHarness /></MemoryRouter>);
    await screen.findByText('No active work in admitted sources');
    fireEvent.click(screen.getByRole('button', { name: 'Open attention item' }));
    await screen.findByRole('dialog', { name: item.title });
    expect(api.get).toHaveBeenCalledTimes(2);
  });

  it('rejects a late prior route read after the new source readback', async () => {
    let resolveOld;
    api.get.mockImplementationOnce(() => new Promise((resolve) => { resolveOld = resolve; }))
      .mockResolvedValueOnce({ data: payload });
    render(<MemoryRouter initialEntries={['/my-work']}><NavigationHarness /></MemoryRouter>);
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByRole('button', { name: 'Open attention item' }));
    await screen.findByRole('dialog', { name: item.title });
    await act(async () => resolveOld({ data: { ...payload, items: [{ ...item, title: 'Obsolete source snapshot' }] } }));
    expect(screen.queryByText('Obsolete source snapshot')).toBeNull();
    expect(screen.getByRole('dialog', { name: item.title })).toBeTruthy();
  });

  it('aborts and suppresses a projection read after session generation changes', async () => {
    const user = { id: 'principal-a', tenantId: 'tenant-a', role: 'TENANT_OWNER', businessRole: 'tenant_owner', membershipRevision: 4, businessRoleRevision: 9 };
    let oldRequestConfig;
    let resolveOld;
    api.get.mockImplementationOnce((_path, config) => {
      oldRequestConfig = config;
      return new Promise((resolve) => { resolveOld = resolve; });
    }).mockResolvedValueOnce({ data: { ...payload, items: [{ ...item, title: 'Current session work' }] } });
    const harness = (sessionGeneration) => <AuthContext.Provider value={{ user, sessionGeneration }}><MemoryRouter><MyWorkWorkspace /></MemoryRouter></AuthContext.Provider>;
    const { rerender } = render(harness(12));
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(1));
    rerender(harness(13));
    await screen.findByText('Current session work');
    expect(oldRequestConfig.signal.aborted).toBe(true);
    await act(async () => resolveOld({ data: { ...payload, items: [{ ...item, title: 'Obsolete session work' }] } }));
    expect(screen.queryByText('Obsolete session work')).toBeNull();
    expect(screen.getByText('Current session work')).toBeTruthy();
  });

  it('clears an unsent completion note and drawer when same-principal capacity changes', async () => {
    const userA = { id: 'principal-a', tenantId: 'tenant-a', role: 'TENANT_OWNER', businessRole: 'tenant_owner', membershipRevision: 4, businessRoleRevision: 9 };
    const userB = { ...userA, businessRole: 'tenant_partner', businessRoleRevision: 10 };
    api.get.mockResolvedValueOnce({ data: payload }).mockResolvedValueOnce({ data: {
      ...payload, items: [{ ...item, title: 'Revised capacity task' }],
    } });
    const harness = (user) => <AuthContext.Provider value={{ user, sessionGeneration: 20 }}><MemoryRouter><MyWorkWorkspace /></MemoryRouter></AuthContext.Provider>;
    const { rerender } = render(harness(userA));
    await screen.findByText(item.title);
    fireEvent.click(selectedRow());
    fireEvent.change(screen.getByLabelText('Completion note'), { target: { value: 'Private draft from former capacity' } });
    rerender(harness(userB));
    expect(screen.queryByText(item.title)).toBeNull();
    await screen.findByText('Revised capacity task');
    fireEvent.click(screen.getByRole('button', { name: /Revised capacity task/ }));
    expect(screen.getByLabelText('Completion note').value).toBe('');
    expect(api.get).toHaveBeenCalledTimes(2);
    expect(api.post).not.toHaveBeenCalled();
  });

  it('clears prior tenant rows and drafts after authenticated tenant scope changes', async () => {
    const userA = { id: 'principal-a', tenantId: 'tenant-a', role: 'TENANT_OWNER', businessRole: 'tenant_owner' };
    const userB = { id: 'principal-b', tenantId: 'tenant-b', role: 'TENANT_OWNER', businessRole: 'tenant_partner' };
    const other = { ...item, source_key: 'OPERATIONS:WORK-B', work_item_id: 'WORK-B', title: 'Second tenant task' };
    api.get.mockResolvedValueOnce({ data: payload }).mockResolvedValueOnce({ data: {
      ...payload, tenant_id: userB.tenantId, principal_id: userB.id, items: [other],
    } });
    const harness = (user) => <AuthContext.Provider value={{ user }}><MemoryRouter><MyWorkWorkspace /></MemoryRouter></AuthContext.Provider>;
    const { rerender } = render(harness(userA));
    await screen.findByText(item.title);
    fireEvent.click(selectedRow());
    fireEvent.change(screen.getByLabelText('Completion note'), { target: { value: 'Prior tenant private draft' } });
    rerender(harness(userB));
    expect(screen.queryByText(item.title)).toBeNull();
    await screen.findByText('Second tenant task');
    fireEvent.click(screen.getByRole('button', { name: /Second tenant task/ }));
    expect(screen.getByLabelText('Completion note').value).toBe('');
    expect(api.post).not.toHaveBeenCalled();
  });

  it('fails closed when the server projection tenant differs from AuthContext', async () => {
    const user = { id: 'principal-a', tenantId: 'tenant-a' };
    api.get.mockResolvedValueOnce({ data: { ...payload, tenant_id: 'tenant-b' } });
    render(<AuthContext.Provider value={{ user }}><MemoryRouter><MyWorkWorkspace /></MemoryRouter></AuthContext.Provider>);
    await screen.findByRole('alert');
    expect(screen.getByText('MY_WORK_SCOPE_MISMATCH')).toBeTruthy();
    expect(screen.queryByText(item.title)).toBeNull();
    expect(api.post).not.toHaveBeenCalled();
  });
});

/*
 * ARTIFACT: MyWorkWorkspaceAttention.test.jsx
 * VERSION: v1.4.0-QUEUE-DETAIL-HANDOFF-CERT
 * AUTHORITY BOUNDARY: Authenticated projection handoff; source owns commands.
 * TENANT POSTURE: Only current exact-scope EOS rows may be focused.
 * FAIL-CLOSED POSTURE: Forged, stale and foreign route records are not displayed.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
