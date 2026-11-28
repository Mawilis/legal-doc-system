/**
 * TITLE: WILSY OS People Overview Production Source Runtime Contract
 * VERSION: v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Exercises mounted HR dashboard behavior when EOS invalidates a session,
 *          an exact tenant scope changes during an outstanding read, or a command
 *          acknowledgement cannot be confirmed by current source readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/PeopleOverviewRuntime.test.jsx
 * COLLABORATION / OWNERSHIP: Runtime regression coverage for HrDashboard.jsx and its authenticated source adapters.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
 * CHANGELOG:
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION independently resets command transport and supplies deterministic secure random command IDs in mounted tests, preserving production crypto and exact idempotency assertions.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION covers exact-tenant organizational draft POST, independently verified registry readback and denied command without false success.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION asserts the source-denied organization without relying on retired EOS-voice copy; foreign-tenant response remains concealed and authority checks unchanged.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION uses the actual canonical requisition envelope (requisition_id, position_title, department_id) and bounded pagination semantics; rejects invented fixture shapes.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION verifies visible observed zeros, absent duplicate actions, independent headcount totals, page-scoped approved counts, and governed navigation without fabricating a position master.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION closes the candidate-intake dialog before the headcount handoff, preserving authentic modal interaction and proving no candidate write occurs without an explicit source-authorized command.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION verifies candidate intake remains accessible across paginated headcount, opens the existing EOS command modal, and performs no write before the governed submission.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION asserts both header and inline candidate intake remain disabled until a verified approved requisition exists, without relaxing backend command validation.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION verifies genuine zero-employee HR Director progressive navigation, Workforce first actions, Hiring pipeline, candidate admission guard and Headcount handoff without synthetic persisted state.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION verifies that an observed department navigates into existing authorized server-side directory search without inventing organization commands.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION asserts source-verified empty organization, exact tenant and schema verification, and foreign organization concealment in the Workforce subview.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION confirms global search exposes the accessible directory employee button, not a retired standalone table text node; source, tenant, detail and denial assertions remain in force.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION uses a canonical opaque synthetic employee identifier and waits for independently verified detail before asserting profile content; no production authority changed.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION certifies the authenticated Workforce directory and exact-tenant detail read, safe preview and denial-without-profile; earlier EOS provenance and tenant-invalidated contracts remain intact.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION verifies accessible Ready status for individually verified EOS sources after sentence-case UI simplification; retained tenant, provenance, denial and command-journey assertions remain unchanged.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION asserts the actual EOS-derived workforce metric, source readiness labels and governed empty-state headcount entry instead of retired presentation strings; prior tenant, denial and legacy-route assertions remain in force.
 *   v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION verifies that separate denied HR sources display an accurate capacity-specific warning without false zero.
 *   v1.0.2-HEADCOUNT-OVERVIEW-PAGE-RUNTIME models the source-bound paginated Python EOS headcount Overview envelope in mounted People runtime tests.
 *   v1.0.1-SINGLE-AUTHORIZED-OVERVIEW-RECOVERY expects the single governed capacity-recovery state rather than multiple denied notices and empty metrics.
 *   v1.0.0-PEOPLE-OVERVIEW-LIVE-SOURCE-CONTRACT — Exercises authenticated Python EOS workforce overview, exact-tenant source read and context-aware global People search.
 *   v1.7.0-EOS-CANDIDATE-EVIDENCE-LOOP — Certifies streamed candidate evidence custody, exact binary digest/size readback, stage-command gating, and stale-scope evidence response rejection.
 *   v1.6.0-EOS-HIRING-COMMAND-LOOP — Certifies source-owned candidate command acknowledgement, exact tenant readback, stable idempotent retry, and no legacy write path.
 *   v1.5.0-CANONICAL-HIRING-READS — Exercises the Python EOS candidate and offer projections, asserts opaque identity display, and prevents local legacy mutations.
 *   v1.4.0-ACT-DRIVEN-COMPONENT-REGRESSIONS — Wraps synchronous UI actions in Testing Library act-aware events so modal and async command state changes are observed deterministically.
 *   v1.3.0-EOS-WORKFORCE-PROJECTION — Uses the exact EOS workforce response fields so the race and invalidation assertions inspect rows as the live client receives them.
 *   v1.2.0-SHARED-CHROME-READBACK-CONTRACT — Models the shared Chrome callback keys and schedules the source readback outage before the command response resolves.
 *   v1.1.0-HR-SESSION-SCOPE-AND-READBACK — Adds readback-failure feedback coverage alongside the session invalidation and tenant-scope race regressions.
 *   v1.0.0-HR-SESSION-AND-SCOPE-RACES — Adds deterministic mounted-component coverage for session-wide 401 invalidation and late cross-tenant response rejection.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Uses synthetic identifiers and in-memory responses only; no credentials, network requests, or persisted records.
 * TENANT BOUNDARY: Each render uses an exact synthetic authenticated tenant; old-scope responses must not cross into the new tenant view.
 * AUTHORITY BOUNDARY: Tests client presentation and request sequencing only; Python EOS remains the authorization and HR business-truth authority.
 * FINANCIAL AUTHORITY BOUNDARY: No compensation execution or settlement authority is created or tested.
 */

import React from 'react';
import { sha3_512 } from 'js-sha3';
import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mockState = vi.hoisted(() => ({
  auth: null,
  tenant: null,
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  candidateRead: vi.fn(),
  offerSend: vi.fn(),
  offerDecision: vi.fn(),
  offerSubmit: vi.fn(),
  offerCreate: vi.fn(),
  candidateTransition: vi.fn(),
  candidateCreate: vi.fn(),
  candidateEvidenceUpload: vi.fn(),
  candidateEvidenceReadback: vi.fn(),
  offerRead: vi.fn(),
  legacyCandidateRead: vi.fn(),
  legacyCandidateCreate: vi.fn(),
  legacyCandidateDelete: vi.fn(),
  jobOpeningRead: vi.fn(),
  jobOpeningCreate: vi.fn(),
}));

vi.mock('../../contexts/authContext', () => ({
  useAuth: () => mockState.auth,
}));

vi.mock('../../contexts/tenantContext', () => ({
  useTenants: () => mockState.tenant,
}));

vi.mock('../../services/api', () => ({
  default: { get: mockState.apiGet, post: mockState.apiPost },
}));

vi.mock('../../services/hrService', () => {
  const emptyPage = () => Promise.resolve({
    items: [], total: 0, limit: 12, offset: 0, hasMore: false,
  });
  return {
    getRecruitmentCandidates: mockState.legacyCandidateRead,
    getHiringCandidates: mockState.candidateRead,
    getHiringOffers: mockState.offerRead,
    createHiringCandidate: mockState.candidateCreate,
    uploadHiringCandidateEvidence: mockState.candidateEvidenceUpload,
    readHiringCandidateEvidence: mockState.candidateEvidenceReadback,
    transitionHiringCandidate: mockState.candidateTransition,
    createHiringOffer: mockState.offerCreate,
    submitHiringOffer: mockState.offerSubmit,
    decideHiringOffer: mockState.offerDecision,
    sendHiringOffer: mockState.offerSend,
    getJobOpenings: mockState.jobOpeningRead,
    getPayrollSummary: emptyPage,
    getBenefits: emptyPage,
    getPerformanceReviews: emptyPage,
    getTimeOffRequests: emptyPage,
    createCandidate: mockState.legacyCandidateCreate,
    updateCandidateStage: vi.fn(),
    deleteCandidate: mockState.legacyCandidateDelete,
    createJobOpening: mockState.jobOpeningCreate,
    updateJobOpening: vi.fn(),
    deleteJobOpening: vi.fn(),
    syncPayroll: vi.fn(),
    createBenefit: vi.fn(),
    updateBenefit: vi.fn(),
    deleteBenefit: vi.fn(),
    createPerformanceReview: vi.fn(),
    updatePerformanceReview: vi.fn(),
    deletePerformanceReview: vi.fn(),
    createTimeOffRequest: vi.fn(),
    updateTimeOffRequest: vi.fn(),
    approveTimeOff: vi.fn(),
    denyTimeOff: vi.fn(),
    deleteTimeOffRequest: vi.fn(),
  };
});

vi.mock('../../hooks/useTelemetryFeed', () => ({
  useTelemetryFeed: () => ({ events: [], isSyncing: false, error: null }),
}));

vi.mock('../../components/os/WilsyOSDashboardChrome', async () => {
  const { createElement } = await import('react');
  return {
    default: ({ children, actions, leftRail }) => createElement(
      'div',
      { 'data-testid': 'hr-dashboard-test-shell' },
      createElement('header', null,
        createElement('button', {
          type: 'button',
          onClick: actions?.onLiveSync,
          disabled: Boolean(actions?.isRefreshing),
        }, actions?.liveSyncLabel || 'LIVE SYNC'),
        createElement('button', {
          type: 'button',
          'aria-label': 'Open primary HR command',
          title: actions?.primaryLabel || 'Open HR command',
          onClick: actions?.onPrimaryAction,
          disabled: Boolean(actions?.primaryDisabled),
        }, actions?.primaryLabel || 'Open HR command'),
        leftRail,
      ),
      children,
    ),
  };
});

vi.mock('../../components/shared/WilsyProfilePanel', () => ({
  default: () => null,
  hydrateWilsyProfileRuntime: () => ({
    mode: { selectedMode: 'day', resolvedMode: 'day' },
    theme: { id: 'test', color: '#123456' },
  }),
}));

vi.mock('../../components/account/WilsyAccountCommandCenter', () => ({
  default: () => null,
}));

import HrDashboard from '../../components/hr/HrDashboard.jsx';

const validPage = (name) => ({
  data: {
    items: [{
      employeeId: name,
      displayName: name,
      preferredName: name,
      workEmail: `${name.toLowerCase().replaceAll(' ', '.')}@example.invalid`,
      jobTitle: 'Engineer',
      department: 'Engineering',
      employmentStatus: 'ACTIVE',
    }],
    source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
    total: 1,
    limit: 12,
    offset: 0,
    hasMore: false,
  },
});

const emptyPage = { items: [], total: 0, limit: 12, offset: 0, hasMore: false };
const overviewResponse = (tenantId = 'TENANT-HR-A') => ({ data: {
  schema: 'WILSY-PEOPLE-WORKFORCE-OVERVIEW/V1',
  source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
  tenant_id: tenantId,
  generated_at: '2026-11-27T05:00:00+00:00',
  metrics: { active_employees: 1, departments: 1 },
} });

const deferred = () => {
  let resolve;
  let reject;
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
};

const setAuthenticatedScope = (tenantId, principalId, sessionGeneration = 1) => {
  mockState.auth = {
    isAuthenticated: true,
    tenantId,
    sessionGeneration,
    user: { id: principalId, email: `${principalId}@example.invalid`, role: 'HR_OPERATOR' },
    logout: vi.fn(),
  };
  mockState.tenant = {
    activeTenant: { tenantId, name: `Synthetic ${tenantId}` },
    authorityMismatch: false,
  };
};

const renderDashboard = () => render(<HrDashboard />);

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

beforeEach(() => {
  window.history.replaceState(null, '', '/');
  setAuthenticatedScope('TENANT-HR-A', 'PRINCIPAL-HR-A');
  mockState.apiGet.mockReset();
  mockState.apiPost.mockReset();
  mockState.candidateRead.mockReset().mockResolvedValue(emptyPage);
  mockState.offerRead.mockReset().mockResolvedValue(emptyPage);
  mockState.candidateCreate.mockReset();
  mockState.candidateEvidenceUpload.mockReset();
  mockState.candidateEvidenceReadback.mockReset();
  mockState.candidateTransition.mockReset();
  mockState.offerCreate.mockReset();
  mockState.offerSubmit.mockReset();
  mockState.offerDecision.mockReset();
  mockState.offerSend.mockReset();
  mockState.legacyCandidateRead.mockReset();
  mockState.legacyCandidateCreate.mockReset();
  mockState.legacyCandidateDelete.mockReset();
  mockState.jobOpeningRead.mockReset().mockResolvedValue(emptyPage);
  mockState.jobOpeningCreate.mockReset().mockResolvedValue({ id: 'synthetic-opening-1' });
  mockState.apiGet.mockImplementation((path) => {
    if (path === '/hr/workforce/overview') return Promise.resolve(overviewResponse());
    if (path === '/hr/headcount-requisitions/overview') return Promise.resolve({ data: { schema: 'WILSY-HEADCOUNT-OVERVIEW/V1', source: 'EOS_HEADCOUNT_REQUISITIONS', tenant_id: 'TENANT-HR-A', items: [], total: 0, limit: 12, offset: 0, hasMore: false } });
    if (path === '/hr/workforce') return Promise.resolve(validPage('Tenant A Verified Employee'));
    return Promise.reject(Object.assign(new Error('synthetic unavailable source'), { response: { status: 404 } }));
  });
});

describe('production People Overview source contracts', () => {

  it('creates an organization draft only after an exact-tenant persisted readback', async () => {
    vi.stubGlobal('crypto',{randomUUID:()=>'org-command-unique-uuid-0001'});
    const scope = 'TENANT-HR-A';
    let created = false;
    const registry = () => ({data: {
      schema:'WILSY-HR-ORGANIZATION-REGISTRY/V1', source:'EOS_HR_ORGANIZATION_REGISTRY',
      tenant_id:scope, count:created?1:0, items:created?[{
        kind:'DEPARTMENT', record_id:'DEP-OPS', name:'Operations',
        effective_from:'2026-12-01', status:'DRAFT', revision:1,
      }]:[],
    }});
    mockState.apiGet.mockImplementation(path => {
      if (path === '/hr/workforce/overview') return Promise.resolve(overviewResponse());
      if (path === '/hr/workforce') return Promise.resolve(validPage('Tenant A Verified Employee'));
      if (path === '/hr/workforce/structure') return Promise.resolve(registry());
      if (path === '/hr/workforce/organization') return Promise.resolve({data: {
        schema:'WILSY-HR-WORKFORCE-ORGANIZATION/V1',
        source:'AUTHORISED_HR_EMPLOYEE_REGISTRY',
        status:'OBSERVED_EMPLOYEE_DISTRIBUTION',
        tenant_id:scope,active_employees:0,department_count:0,
        unassigned_employees:0,departments:[],
      }});
      return Promise.reject(Object.assign(new Error('unavailable'),{response:{status:404}}));
    });
    mockState.apiPost.mockImplementation(async (path,body,options) => {
      expect(path).toBe('/hr/workforce/structure/departments');
      expect(options.headers['X-Tenant-ID']).toBe(scope);
      expect(options.headers['Idempotency-Key']).toBeTruthy();
      expect(body).toMatchObject({record_id:'DEP-OPS',name:'Operations',effective_from:'2026-12-01'});
      created = true;
      return {data:{
        schema:'WILSY-HR-ORGANIZATION-COMMAND/V1',tenant_id:scope,
        record: {kind:'DEPARTMENT',record_id:'DEP-OPS',name:'Operations',
          effective_from:'2026-12-01',status:'DRAFT',revision:1},
      }};
    });
    renderDashboard();
    fireEvent.click(await screen.findByRole('button',{name:'Workforce',exact:true}));
    fireEvent.click(screen.getByRole('button',{name:'Organization',exact:true}));
    fireEvent.click(await screen.findByRole('button',{name:'Create department'}));
    const form = screen.getByRole('form',{name:'Organization draft form'});
    fireEvent.change(within(form).getByLabelText('Unique code'),{target:{value:'DEP-OPS'}});
    fireEvent.change(within(form).getByLabelText('Name'),{target:{value:'Operations'}});
    fireEvent.change(within(form).getByLabelText('Effective from (YYYY-MM-DD)'),{target:{value:'2026-12-01'}});
    fireEvent.click(within(form).getByRole('button',{name:'Save draft'}));
    await waitFor(() => expect(mockState.apiPost).toHaveBeenCalledTimes(1));
    expect(await screen.findByText(/DEP-OPS · DRAFT · Revision 1/)).toBeInTheDocument();
    expect(screen.getByText(/verified after readback/)).toBeInTheDocument();
  });

  it('does not display a successful organization record when write permission is denied',async () => {
    vi.stubGlobal('crypto',{randomUUID:()=>'org-command-unique-uuid-0002'});
    mockState.apiGet.mockImplementation(path => {
      if (path === '/hr/workforce/overview') return Promise.resolve(overviewResponse());
      if (path === '/hr/workforce') return Promise.resolve(validPage('Tenant A Verified Employee'));
      if (path === '/hr/workforce/structure') return Promise.resolve({data:{
        schema:'WILSY-HR-ORGANIZATION-REGISTRY/V1',
        source:'EOS_HR_ORGANIZATION_REGISTRY',tenant_id:'TENANT-HR-A',
        count:0,items:[],
      }});
      if (path === '/hr/workforce/organization') return Promise.resolve({data:{
        schema:'WILSY-HR-WORKFORCE-ORGANIZATION/V1',
        source:'AUTHORISED_HR_EMPLOYEE_REGISTRY',
        status:'OBSERVED_EMPLOYEE_DISTRIBUTION',tenant_id:'TENANT-HR-A',
        active_employees:0,department_count:0,unassigned_employees:0,departments:[],
      }});
      return Promise.reject(Object.assign(new Error('unavailable'),{response:{status:404}}));
    });
    mockState.apiPost.mockRejectedValue(Object.assign(new Error('denied'),{response:{status:403}}));
    renderDashboard();
    fireEvent.click(await screen.findByRole('button',{name:'Workforce',exact:true}));
    fireEvent.click(screen.getByRole('button',{name:'Organization',exact:true}));
    fireEvent.click(await screen.findByRole('button',{name:'Create department'}));
    const form = screen.getByRole('form',{name:'Organization draft form'});
    fireEvent.change(within(form).getByLabelText('Unique code'),{target:{value:'DEP-TEST'}});
    fireEvent.change(within(form).getByLabelText('Name'),{target:{value:'Test department'}});
    fireEvent.change(within(form).getByLabelText('Effective from (YYYY-MM-DD)'),{target:{value:'2026-12-01'}});
    fireEvent.click(within(form).getByRole('button',{name:'Save draft'}));
    expect(await screen.findByText(/does not have the independent organization command permission/)).toBeInTheDocument();
    expect(screen.queryByText(/verified after readback/)).not.toBeInTheDocument();
  });


  it('builds a verified first-use HR Director journey without fabricated people or bypassed admission', async () => {
    setAuthenticatedScope('TENANT-HR-A', 'PRINCIPAL-HR-A');
    mockState.auth.user.role = 'tenant_hr_director';
    mockState.apiGet.mockImplementation(path => {
      if (path === '/hr/workforce/overview') return Promise.resolve({data: {
        ...overviewResponse().data, metrics: {active_employees: 0, departments: 0},
      }});
      if (path === '/hr/headcount-requisitions/overview') return Promise.resolve({data: {
        schema: 'WILSY-HEADCOUNT-OVERVIEW/V1',
        source: 'EOS_HEADCOUNT_REQUISITIONS', tenant_id: 'TENANT-HR-A',
        items: [], total: 0, limit: 12, offset: 0, hasMore: false,
      }});
      if (path === '/hr/workforce') return Promise.resolve({data: {
        ...validPage('Synthetic Employee').data, items: [], total: 0,
      }});
      return Promise.reject(Object.assign(new Error('no source'), {response: {status: 404}}));
    });
    renderDashboard();
    expect(await screen.findByRole('button', {name: 'Workforce', exact: true})).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole('button', {name: /More functions/})).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', {name: 'Workforce', exact: true}));
    expect(await screen.findByText('No people yet')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: /Request headcount/})).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', {name: /Hiring pipeline/}));
    expect(await screen.findByRole('heading', {name: 'Hiring pipeline'})).toBeInTheDocument();
    expect(screen.getByText('No candidates yet')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Create candidate', exact: true})).toBeEnabled();
    fireEvent.click(screen.getByRole('button', {name: 'Start candidate intake'}));
    expect(await screen.findByRole('dialog', {name: 'Python EOS hiring command'})).toBeInTheDocument();
    expect(mockState.candidateCreate).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', {name: 'Close hiring command'}));
    expect(screen.queryByRole('dialog', {name: 'Python EOS hiring command'})).not.toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Request headcount'})).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', {name: 'Request headcount'}));
    expect(await screen.findByRole('heading', {name: /Headcount & roles/})).toBeInTheDocument();
  });



  it('shows verified zero organization truth without manufacturing departments or positions', async () => {
    mockState.apiGet.mockImplementation(path => {
      if (path === '/hr/workforce/overview') return Promise.resolve(overviewResponse());
      if (path === '/hr/workforce') return Promise.resolve(validPage('Tenant A Verified Employee'));
      if (path === '/hr/workforce/organization') return Promise.resolve({data: {
        schema: 'WILSY-HR-WORKFORCE-ORGANIZATION/V1',
        tenant_id: 'TENANT-HR-A',
        source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
        status: 'OBSERVED_EMPLOYEE_DISTRIBUTION',
        active_employees: 0, unassigned_employees: 0,
        department_count: 0, departments: [],
      }});
      return Promise.reject(Object.assign(new Error('unavailable'), {response: {status: 404}}));
    });
    renderDashboard();
    fireEvent.click(await screen.findByRole('button', {name: 'Workforce', exact: true}));
    fireEvent.click(screen.getByRole('button', {name: 'Organization', exact: true}));
    expect(await screen.findByRole('heading', {name: 'Organization & positions'})).toBeInTheDocument();
    const governed = screen.getByRole('heading', {name: 'Governed structure'});
    const secondary = screen.getByText(/Observed workforce and headcount planning/);
    expect(governed.compareDocumentPosition(secondary) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(secondary).toHaveAttribute('aria-expanded', 'false');
    fireEvent.click(secondary);
    expect(secondary).toHaveAttribute('aria-expanded', 'true');

    await waitFor(() => expect(mockState.apiGet).toHaveBeenCalledWith(
      '/hr/workforce/organization',
      expect.objectContaining({headers: {'X-Tenant-ID': 'TENANT-HR-A'}}),
    ));
    expect(await screen.findByText('No departments with people yet')).toBeInTheDocument();
    expect(screen.getByLabelText('Current observed organization')).toHaveTextContent('0');
    expect(screen.getByRole('heading', {name: 'Position planning'})).toBeInTheDocument();
    expect(screen.queryByRole('button', {name: 'Plan roles'})).not.toBeInTheDocument();
    expect(screen.queryByText('Engineering')).not.toBeInTheDocument();
  });


  it('shows authorized headcount planning without claiming approved positions from a partial page', async () => {
    mockState.apiGet.mockImplementation(path => {
      if (path === '/hr/workforce/overview') return Promise.resolve(overviewResponse());
      if (path === '/hr/headcount-requisitions/overview') return Promise.resolve({data: {
        schema: 'WILSY-HEADCOUNT-OVERVIEW/V1',
        source: 'EOS_HEADCOUNT_REQUISITIONS',
        tenant_id: 'TENANT-HR-A',
        items: [{requisition_id: 'REQ-1', position_title: 'Clinical coordinator',
          department_id: 'Operations', work_location: 'Remote', headcount: 1,
          revision: 1, status: 'SUBMITTED'}],
        total: 20, limit: 12, offset: 0, hasMore: true,
      }});
      if (path === '/hr/workforce') return Promise.resolve(validPage('Tenant A Verified Employee'));
      if (path === '/hr/workforce/organization') return Promise.resolve({data: {
        schema: 'WILSY-HR-WORKFORCE-ORGANIZATION/V1',
        source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
        tenant_id: 'TENANT-HR-A',
        status: 'OBSERVED_EMPLOYEE_DISTRIBUTION',
        active_employees: 2, unassigned_employees: 0, department_count: 1,
        departments: [{name: 'Operations', active_employees: 2}],
      }});
      return Promise.reject(Object.assign(new Error('unavailable'), {response: {status: 404}}));
    });
    renderDashboard();
    fireEvent.click(await screen.findByRole('button', {name: 'Workforce', exact: true}));
    fireEvent.click(screen.getByRole('button', {name: 'Organization', exact: true}));
    expect(await screen.findByRole('heading', {name: 'Organization & positions'})).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', {name: /Observed workforce and headcount planning/}));
    expect(await screen.findByText('Operations')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: /Search workforce in Operations, 2 active employees/})).toBeInTheDocument();
    expect(await screen.findByRole('heading', {name: 'Position planning'})).toBeInTheDocument();
    expect(screen.getByText('Clinical coordinator')).toBeInTheDocument();
    expect(screen.getByText(/Approved requests on the loaded page: 0/)).toBeInTheDocument();
    expect(screen.getByText(/Additional requests are available/)).toBeInTheDocument();
    const action = screen.getByRole('button', {name: /Manage headcount requests/});
    expect(action).toBeInTheDocument();
    fireEvent.click(action);
    expect(await screen.findByRole('heading', {name: /Headcount & roles/})).toBeInTheDocument();
  });

  it('opens verified observed department members through the existing tenant-scoped directory search', async () => {
    mockState.apiGet.mockImplementation(path => {
      if (path === '/hr/workforce/overview') return Promise.resolve(overviewResponse());
      if (path === '/hr/workforce') return Promise.resolve(validPage('Tenant A Verified Employee'));
      if (path === '/hr/workforce/organization') return Promise.resolve({data: {
        schema: 'WILSY-HR-WORKFORCE-ORGANIZATION/V1',
        tenant_id: 'TENANT-HR-A',
        source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
        status: 'OBSERVED_EMPLOYEE_DISTRIBUTION',
        active_employees: 2, unassigned_employees: 0,
        department_count: 1,
        departments: [{name: 'Engineering', active_employees: 2}],
      }});
      return Promise.reject(Object.assign(new Error('unavailable'), {response: {status: 404}}));
    });
    renderDashboard();
    fireEvent.click(await screen.findByRole('button', {name: 'Workforce', exact: true}));
    fireEvent.click(screen.getByRole('button', {name: 'Organization', exact: true}));
    const department = await screen.findByRole('button', {name: /Search workforce in Engineering, 2 active employees/});
    fireEvent.click(department);
    expect(await screen.findByRole('heading', {name: 'Workforce directory'})).toBeInTheDocument();
    await waitFor(() => expect(mockState.apiGet).toHaveBeenCalledWith(
      '/hr/workforce',
      expect.objectContaining({
        headers: {'X-Tenant-ID': 'TENANT-HR-A'},
        params: expect.objectContaining({q: 'Engineering'}),
      }),
    ));
    expect(screen.getByRole('searchbox', {name: 'Search workforce'})).toHaveValue('Engineering');
  });

  it('rejects cross-tenant organization readback rather than showing a foreign department', async () => {
    mockState.apiGet.mockImplementation(path => {
      if (path === '/hr/workforce/overview') return Promise.resolve(overviewResponse());
      if (path === '/hr/workforce') return Promise.resolve(validPage('Tenant A Verified Employee'));
      if (path === '/hr/workforce/organization') return Promise.resolve({data: {
        schema: 'WILSY-HR-WORKFORCE-ORGANIZATION/V1',
        tenant_id: 'TENANT-HR-B',
        source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
        status: 'OBSERVED_EMPLOYEE_DISTRIBUTION',
        active_employees: 7, unassigned_employees: 0,
        department_count: 1,
        departments: [{name: 'Foreign Department', active_employees: 7}],
      }});
      return Promise.reject(Object.assign(new Error('unavailable'), {response: {status: 404}}));
    });
    renderDashboard();
    fireEvent.click(await screen.findByRole('button', {name: 'Workforce', exact: true}));
    fireEvent.click(screen.getByRole('button', {name: 'Organization', exact: true}));
    expect(await screen.findByText('Organization is temporarily unavailable')).toBeInTheDocument();
    expect(screen.getByText(/The current organization records could not be confirmed/)).toBeInTheDocument();
    expect(screen.queryByText('Foreign Department')).not.toBeInTheDocument();
  });


  it('opens a readable source-backed Workforce directory and verifies an exact-tenant detail before preview', async () => {
    mockState.apiGet.mockImplementation((path) => {
      if (path === '/hr/workforce/overview') return Promise.resolve(overviewResponse());
      if (path === '/hr/headcount-requisitions/overview') return Promise.resolve({
        data: { schema: 'WILSY-HEADCOUNT-OVERVIEW/V1', source: 'EOS_HEADCOUNT_REQUISITIONS',
          tenant_id: 'TENANT-HR-A', items: [], total: 0, limit: 12, offset: 0, hasMore: false },
      });
      if (path === '/hr/workforce') return Promise.resolve({ data: { ...validPage('Tenant A Verified Employee').data, items: [{ ...validPage('Tenant A Verified Employee').data.items[0], employeeId: 'EMP-A-001' }] } });
      if (path === '/hr/workforce/EMP-A-001') return Promise.resolve({
        data: {
          schema: 'WILSY-HR-WORKFORCE-DIRECTORY-DETAIL/V1',
          source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
          tenant_id: 'TENANT-HR-A',
          employee: { employeeId: 'EMP-A-001', displayName: 'Tenant A Verified Employee',
            jobTitle: 'Engineer', department: 'Engineering', managerId: null,
            employmentStatus: 'ACTIVE', workEmail: 'synthetic@example.invalid' },
        },
      });
      return Promise.reject(Object.assign(new Error('unavailable'), { response: { status: 404 } }));
    });
    renderDashboard();
    fireEvent.click(screen.getByRole('button', { name: 'Workforce', exact: true }));
    expect(await screen.findByRole('heading', { name: 'Workforce directory' })).toBeInTheDocument();
    const employee = await screen.findByRole('button', { name: /Tenant A Verified Employee/ });
    fireEvent.click(employee);
    await waitFor(() => expect(mockState.apiGet).toHaveBeenCalledWith(
      '/hr/workforce/EMP-A-001',
      expect.objectContaining({ headers: { 'X-Tenant-ID': 'TENANT-HR-A' } }),
    ));
    await waitFor(() => expect(screen.getByRole('region', { name: 'Employee directory preview' })).toHaveTextContent('Engineer'));
    expect(screen.queryByText('bankAccount')).not.toBeInTheDocument();
  });

  it('never shows an unverified employee preview when the detail source denies read', async () => {
    mockState.apiGet.mockImplementation((path) => {
      if (path === '/hr/workforce/overview') return Promise.resolve(overviewResponse());
      if (path === '/hr/headcount-requisitions/overview') return Promise.resolve({
        data: { schema: 'WILSY-HEADCOUNT-OVERVIEW/V1', source: 'EOS_HEADCOUNT_REQUISITIONS',
          tenant_id: 'TENANT-HR-A', items: [], total: 0, limit: 12, offset: 0, hasMore: false },
      });
      if (path === '/hr/workforce') return Promise.resolve({ data: { ...validPage('Tenant A Verified Employee').data, items: [{ ...validPage('Tenant A Verified Employee').data.items[0], employeeId: 'EMP-A-001' }] } });
      return Promise.reject(Object.assign(new Error('denied'), { response: { status: 403 } }));
    });
    renderDashboard();
    fireEvent.click(screen.getByRole('button', { name: 'Workforce', exact: true }));
    const employee = await screen.findByRole('button', { name: /Tenant A Verified Employee/ });
    fireEvent.click(employee);
    expect(await screen.findByText('EOS denied this employee detail read for the current session.')).toBeInTheDocument();
    expect(screen.queryByText('Directory preview · Tenant A Verified Employee')).not.toBeInTheDocument();
  });

  it('renders an EOS-proven workforce number and uses no legacy HR snapshot source', async () => {
    renderDashboard();
    expect(await screen.findByText('Decisions & next actions')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'People lifecycle at a glance' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Lifecycle coverage' })).toBeInTheDocument();
    await waitFor(() => expect(mockState.apiGet).toHaveBeenCalledWith(
      '/hr/workforce/overview', expect.objectContaining({
        headers: { 'X-Tenant-ID': 'TENANT-HR-A' },
      })
    ));
    await waitFor(() => expect(screen.getByRole('button', {
      name: /Active workforce: 1\. Open Employee authority/,
    })).toBeInTheDocument());
    expect(screen.getByRole('button', { name: /Open Workforce source: Ready/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Open Headcount source: Ready/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Open Headcount requests/ })).toBeInTheDocument();
    expect(mockState.apiGet.mock.calls.some(([path]) => path === '/hr/snapshot')).toBe(false);
    expect(mockState.apiGet.mock.calls.some(([path]) => path === '/hr/headcount-requisitions/overview')).toBe(true);
  });

  it('routes a global People query to the independently authorized workforce search', async () => {
    renderDashboard();
    await waitFor(() => expect(mockState.apiGet.mock.calls.some(([path]) => path === '/hr/workforce')).toBe(true));
    act(() => window.dispatchEvent(new CustomEvent('wilsy:people-context-search', {
      detail: { query: 'Synthetic' },
    })));
    await waitFor(() => expect(mockState.apiGet).toHaveBeenCalledWith(
      '/hr/workforce',
      expect.objectContaining({
        headers: { 'X-Tenant-ID': 'TENANT-HR-A' },
        params: expect.objectContaining({ q: 'Synthetic' }),
      })
    ));
    expect(await screen.findByRole('button', { name: /Tenant A Verified Employee/ })).toBeInTheDocument();
  });

  it('does not represent an HR authorization denial as an employee zero', async () => {
    const denied = Object.assign(new Error('HR restricted'), { response: { status: 403 } });
    mockState.apiGet.mockRejectedValue(denied);
    mockState.candidateRead.mockRejectedValue(denied);
    mockState.offerRead.mockRejectedValue(denied);
    renderDashboard();
    expect(await screen.findByText('People source access needs an authorized capacity')).toBeInTheDocument();
    expect(await screen.findByText(/Founder designation alone does not grant HR permission/)).toBeInTheDocument();
    expect(screen.queryByText('0 planned')).not.toBeInTheDocument();
    expect(screen.queryByText('Tenant A Verified Employee')).not.toBeInTheDocument();
  });
});

/**
 * ARTIFACT: client/src/__tests__/components/PeopleOverviewRuntime.test.jsx
 * VERSION: v1.4.1-ORGANIZATION-CRYPTO-TEST-ISOLATION
 * AUTHORITY BOUNDARY: Source-read regression; Python EOS owns IAM and workforce truth.
 * TENANT POSTURE: Synthetic tenant and employee examples only.
 * FAIL-CLOSED POSTURE: Denied source never materializes false workforce counts.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
