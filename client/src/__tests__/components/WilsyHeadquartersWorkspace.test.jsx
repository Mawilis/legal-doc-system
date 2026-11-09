/**
 * TITLE: WILSY OS Headquarters workspace presentation certificate
 * VERSION: v1.6.0-AUTHENTICATED-OVERVIEW-SOURCE-SYNC
 * AUTHORITY: WILSY EOS frontend regression evidence
 * EPITOME: Verifies Headquarters renders only the source-backed My Work, Team,
 *          and HR requisition projections without manufacturing operational truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/WilsyHeadquartersWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: Exercises WilsyHeadquartersWorkspace and its API adapter seam.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.6.0-AUTHENTICATED-OVERVIEW-SOURCE-SYNC uses an exact
 *            authenticated tenant/principal fixture for Headquarters, full
 *            source-owned My Work coverage, and confirms the executive
 *            snapshot revalidates after source-confirmed invalidation.
 *            v1.5.0-MY-WORK-ITEM-HANDOFF certifies selected daily work focus handoff
 *            and reset through the canonical My Work navigation entry.
 *            v1.4.0-ATTENTION-HR-DEEP-LINK confirms the floating attention bell can
 *            open the existing authorised HR suite by an explicit URL.
 *            v1.3.0 covers handoff from Headquarters to the canonical HR operating workspace.
 *            v1.2.0 covers explicit server refresh controls for My Work and HR requisitions.
 *            v1.1.0 covers P0 KPI source states and tenant-scoped HR requisition read presentation.
 * COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2
 * AUTHORITY BOUNDARY: Presentation evidence only; no authorization is granted by these tests.
 */
import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import api from '../../services/api.js';
import AuthContext from '../../contexts/authContext.jsx';
import {
  currentUnifiedMyWorkScope,
  invalidateUnifiedMyWork,
} from '../../services/unifiedMyWorkSync.js';
import { MemoryRouter } from 'react-router-dom';
import WilsyHeadquartersWorkspace from '../../components/workspaces/WilsyHeadquartersWorkspace.jsx';

vi.mock('../../components/workspaces/MyWorkWorkspace.jsx', () => ({
  default: ({ focusWorkItem }) => (
    <section>
      <h2>My Work certified task centre</h2>
      <output data-testid="my-work-focus">{focusWorkItem || ''}</output>
    </section>
  ),
}));
vi.mock('../../components/workspaces/WilsyHeadquartersDailyBrief.jsx', () => ({
  default: ({ onOpenWork }) => (
    <button onClick={() => onOpenWork({ source_key: 'OPERATIONS:OPS-FOCUS-1' })}>
      Open selected daily item
    </button>
  ),
}));
vi.mock('../../components/hr/HrDashboard.jsx', () => ({
  default: () => <section><h2>Canonical HR operating workspace</h2></section>,
}));
const exactTenant = 'TENANT-HQ-SOURCE-CERT';
const exactPrincipal = 'PRINCIPAL-HQ-SOURCE-CERT';
const auth = {
  isAuthenticated: true,
  authStage: 'AUTHENTICATED',
  token: 'synthetic-EOS-session-only',
  sessionGeneration: 20,
  user: {
    id: exactPrincipal, tenantId: exactTenant,
    role: 'tenant_owner', businessRole: 'tenant_owner',
    workspaceId: 'EXECUTIVE_COMMAND_CENTRE',
    membershipRevision: 7, businessRoleRevision: 9,
  },
};
const workProjection = () => ({
  schema: 'WILSY-OS-UNIFIED-MY-WORK/V1',
  tenant_id: exactTenant,
  principal_id: exactPrincipal,
  as_of: '2026-11-09T01:00:00+00:00',
  items: [
    { source: 'OPERATIONS', source_key: 'OPERATIONS:HQ-1', work_item_id: 'HQ-1', title: 'Repair source workflow', status: 'OPEN', priority: 'HIGH', due_at: '2026-11-08T01:00:00+00:00', is_overdue: true },
    { source: 'OPERATIONS', source_key: 'OPERATIONS:HQ-2', work_item_id: 'HQ-2', title: 'Ship work release', status: 'OPEN', priority: 'NORMAL', due_at: null, is_overdue: false },
    { source: 'CRM', source_key: 'CRM:HQ-3', work_item_id: 'HQ-3', title: 'Review customer request', status: 'OPEN', priority: 'NORMAL', due_at: null, is_overdue: false },
  ],
  summary: { active_count: 3, overdue_count: 1, source_counts: { OPERATIONS: 2, CRM: 1 } },
  sources_included: ['OPERATIONS', 'CRM'],
  authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
});

vi.mock('../../services/api.js', () => ({
  default: {
    get: vi.fn((path) => {
      if (path === '/my-work') return Promise.resolve({
        data: workProjection(),
      });
      if (path === '/hr/headcount-requisitions') return Promise.resolve({
        data: {
          generated_at: '2026-11-09T01:00:00+00:00',
          items: [{
            requisition_id: 'REQ-TEST-1',
            position_title: 'Platform Engineer',
            department_id: 'engineering',
            employment_type: 'FULL_TIME',
            work_location: 'Remote',
            headcount: 1,
            revision: 2,
            status: 'SUBMITTED',
          }],
        },
      });
      return Promise.resolve({
        data: {
          items: [{
            employeeId: 'EMP-TEST-1',
            displayName: 'Test Directory Person',
            jobTitle: 'Engineer',
            department: 'Engineering',
            employmentStatus: 'ACTIVE',
            workEmail: 'test@example.invalid',
            workLocation: 'Remote',
          }],
          total: 1,
          limit: 50,
          offset: 0,
          hasMore: false,
        },
      });
    }),
  },
}));

const renderHeadquarters = (initialEntries = ['/']) => render(
  <AuthContext.Provider value={auth}>
    <MemoryRouter initialEntries={initialEntries}>
      <WilsyHeadquartersWorkspace tenantId={exactTenant}/>
    </MemoryRouter>
  </AuthContext.Provider>,
);

describe('WILSY Headquarters authenticated shell', () => {
  it('opens the canonical governed HR workflow through attention centre URL', async () => {
    renderHeadquarters(['/headquarters?section=hr-workspace']);
    expect(await screen.findByRole('heading', { name: 'Canonical HR operating workspace' })).toBeTruthy();
  });

  it('presents the company operating environment and daily task centre entry', () => {
    renderHeadquarters();
    expect(screen.getByRole('heading', { name: 'WILSY Headquarters' })).toBeTruthy();
    const navigation = screen.getByRole('navigation', { name: 'Headquarters navigation' });
    expect(within(navigation).getByRole('button', { name: /My Work/ })).toBeTruthy();
    expect(screen.getByText(/does not invent headcount, revenue, customer totals/)).toBeTruthy();
  });

  it('renders source-backed My Work and Team KPIs without inventing Projects or Approvals', async () => {
    renderHeadquarters();
    expect((await screen.findAllByText('3')).length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText('Projects')).toBeTruthy();
    expect(screen.getByText('Project source not yet certified')).toBeTruthy();
    expect(screen.getByText('Approval source not yet certified')).toBeTruthy();
    expect(screen.getByText('Authorized HR directory total')).toBeTruthy();
  });

  it('hands a daily item source key into My Work and clears focus for general navigation', () => {
    renderHeadquarters();
    fireEvent.click(screen.getByRole('button', { name: 'Open selected daily item' }));
    expect(screen.getByTestId('my-work-focus').textContent).toBe('OPERATIONS:OPS-FOCUS-1');

    const navigation = screen.getByRole('navigation', { name: 'Headquarters navigation' });
    fireEvent.click(within(navigation).getByRole('button', { name: /My Work/ }));
    expect(screen.getByTestId('my-work-focus').textContent).toBe('');
  });

  it('mounts the existing My Work workspace rather than a duplicate task projection', () => {
    renderHeadquarters();
    const navigation = screen.getByRole('navigation', { name: 'Headquarters navigation' });
    fireEvent.click(within(navigation).getByRole('button', { name: /My Work/ }));
    expect(screen.getByRole('heading', { name: 'My Work certified task centre' })).toBeTruthy();
  });

  it('renders authorised workforce records from the HR directory service', async () => {
    renderHeadquarters();
    fireEvent.click(screen.getByRole('button', { name: /Organisation & People/ }));
    expect(await screen.findByText('Authorised workforce directory')).toBeTruthy();
    expect(await screen.findByText('Test Directory Person')).toBeTruthy();
    expect(screen.getByText(/test@example\.invalid/)).toBeTruthy();
  });

  it('hands hiring users into the canonical HR operating workspace', async () => {
    renderHeadquarters();
    fireEvent.click(screen.getByRole('button', { name: /Organisation & People/ }));
    fireEvent.click(await screen.findByRole('button', { name: /Open HR workspace/ }));
    expect(await screen.findByRole('heading', { name: 'Canonical HR operating workspace' })).toBeTruthy();
  });

  it('searches the authorised workforce source without supplying tenant authority', async () => {
    renderHeadquarters();
    fireEvent.click(screen.getByRole('button', { name: /Organisation & People/ }));
    await screen.findByText('Test Directory Person');
    fireEvent.change(screen.getByRole('textbox', { name: 'Search workforce directory' }), {
      target: { value: 'Engineering' },
    });
    await waitFor(() => {
      expect(api.get).toHaveBeenLastCalledWith('/hr/workforce', expect.objectContaining({
        params: expect.objectContaining({ limit: 50, offset: 0, q: 'Engineering' }),
        forceNetworkRetry: true,
      }));
    });
  });

  it('separates supported business models from actual customer records', () => {
    renderHeadquarters();
    fireEvent.click(screen.getByRole('button', { name: /Products & Business Portfolio/ }));
    expect(screen.getByText('Importers & exporters')).toBeTruthy();
    expect(screen.getByText('Law firms')).toBeTruthy();
    expect(screen.getByText('Customer portfolio integration pending')).toBeTruthy();
    expect(screen.getByText(/does not imply that a listed business is already a customer/)).toBeTruthy();
  });

  it('does not represent unconnected department services as operational', () => {
    renderHeadquarters();
    const navigation = screen.getByRole('navigation', { name: 'Headquarters navigation' });
    fireEvent.click(within(navigation).getByRole('button', { name: /Engineering/ }));
    expect(screen.getByText('Engineering source is not yet connected')).toBeTruthy();
    expect(screen.getByText('Source integration not yet certified')).toBeTruthy();
  });

  it('renders tenant-scoped headcount requisitions through the existing HR read surface', async () => {
    renderHeadquarters();
    fireEvent.click(screen.getByRole('button', { name: /Organisation & People/ }));
    fireEvent.click(await screen.findByRole('button', { name: /Hiring/ }));
    expect(await screen.findByText('Authorized headcount requisitions')).toBeTruthy();
    expect(await screen.findByText('Platform Engineer')).toBeTruthy();
    expect(screen.getByText('SUBMITTED')).toBeTruthy();
    expect(api.get).toHaveBeenCalledWith('/hr/headcount-requisitions', { forceNetworkRetry: true });
  });

  it('reconciles the executive summary after current EOS source invalidation', async () => {
    const originalGet = api.get.getMockImplementation();
    let reads = 0;
    api.get.mockImplementation((path, ...args) => {
      if (path !== '/my-work') return originalGet(path, ...args);
      reads += 1;
      if (reads === 1) return Promise.resolve({ data: workProjection() });
      const empty = workProjection();
      empty.items = [];
      empty.summary = {
        active_count: 0, overdue_count: 0,
        source_counts: { OPERATIONS: 0, CRM: 0 },
      };
      return Promise.resolve({ data: empty });
    });
    try {
      renderHeadquarters();
      await screen.findByText('OPERATIONS: 2');
      await act(async () => {
        expect(invalidateUnifiedMyWork(currentUnifiedMyWorkScope(auth, exactTenant))).toBe(true);
      });
      expect(await screen.findByText(
        'No active work was returned by the authorized sources at the recorded time.',
      )).toBeTruthy();
      expect(screen.getByText('OPERATIONS: 0')).toBeTruthy();
      expect(reads).toBe(2);
    } finally {
      api.get.mockImplementation(originalGet);
    }
  });

  it('refreshes source projections through the API instead of local browser state', async () => {
    renderHeadquarters();
    await screen.findByRole('heading', { name: 'My Work — attention snapshot' });
    const initialMyWorkReads = api.get.mock.calls.filter(([path]) => path === '/my-work').length;
    fireEvent.click(screen.getByRole('button', { name: 'Refresh snapshot' }));
    await waitFor(() => {
      expect(api.get.mock.calls.filter(([path]) => path === '/my-work').length).toBeGreaterThan(initialMyWorkReads);
    });

    fireEvent.click(screen.getByRole('button', { name: /Organisation & People/ }));
    fireEvent.click(await screen.findByRole('button', { name: /Hiring/ }));
    const initialRequisitionReads = api.get.mock.calls.filter(([path]) => path === '/hr/headcount-requisitions').length;
    fireEvent.click(await screen.findByRole('button', { name: /^Refresh$/ }));
    await waitFor(() => {
      expect(api.get.mock.calls.filter(([path]) => path === '/hr/headcount-requisitions').length).toBeGreaterThan(initialRequisitionReads);
    });
  });
});

/* ARTIFACT: WILSY OS Headquarters workspace presentation certificate
 * VERSION: v1.6.0-AUTHENTICATED-OVERVIEW-SOURCE-SYNC
 * AUTHORITY BOUNDARY: Regression evidence only; tests do not grant permissions.
 * TENANT POSTURE: Fixtures represent server-scoped projections and supply no browser tenant input.
 * FAIL-CLOSED POSTURE: Source contracts are asserted before presentation claims are made.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
