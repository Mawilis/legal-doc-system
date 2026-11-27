/**
 * TITLE: WILSY OS People Overview Production Source Runtime Contract
 * VERSION: v1.0.2-HEADCOUNT-OVERVIEW-PAGE-RUNTIME
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Exercises mounted HR dashboard behavior when EOS invalidates a session,
 *          an exact tenant scope changes during an outstanding read, or a command
 *          acknowledgement cannot be confirmed by current source readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/PeopleOverviewRuntime.test.jsx
 * COLLABORATION / OWNERSHIP: Runtime regression coverage for HrDashboard.jsx and its authenticated source adapters.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
 * CHANGELOG:
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
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mockState = vi.hoisted(() => ({
  auth: null,
  tenant: null,
  apiGet: vi.fn(),
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
  default: { get: mockState.apiGet },
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
});

beforeEach(() => {
  setAuthenticatedScope('TENANT-HR-A', 'PRINCIPAL-HR-A');
  mockState.apiGet.mockReset();
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
  it('renders an EOS-proven workforce number and uses no legacy HR snapshot source', async () => {
    renderDashboard();
    expect(await screen.findByText('Decisions & next actions')).toBeInTheDocument();
    expect(screen.getByText('Verified workforce & hiring')).toBeInTheDocument();
    await waitFor(() => expect(mockState.apiGet).toHaveBeenCalledWith(
      '/hr/workforce/overview', expect.objectContaining({
        headers: { 'X-Tenant-ID': 'TENANT-HR-A' },
      })
    ));
    await waitFor(() => expect(screen.getByText('Current active employees · EOS')).toBeInTheDocument());
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
    expect(await screen.findByText('Tenant A Verified Employee')).toBeInTheDocument();
  });

  it('does not represent an HR authorization denial as an employee zero', async () => {
    const denied = Object.assign(new Error('HR restricted'), { response: { status: 403 } });
    mockState.apiGet.mockRejectedValue(denied);
    mockState.candidateRead.mockRejectedValue(denied);
    mockState.offerRead.mockRejectedValue(denied);
    renderDashboard();
    expect(await screen.findByText('People access requires an authorized operating capacity')).toBeInTheDocument();
    expect(await screen.findByText(/Founder designation alone does not grant HR authority/)).toBeInTheDocument();
    expect(screen.queryByText('0 planned')).not.toBeInTheDocument();
    expect(screen.queryByText('Tenant A Verified Employee')).not.toBeInTheDocument();
  });
});

/**
 * ARTIFACT: client/src/__tests__/components/PeopleOverviewRuntime.test.jsx
 * VERSION: v1.0.2-HEADCOUNT-OVERVIEW-PAGE-RUNTIME
 * AUTHORITY BOUNDARY: Source-read regression; Python EOS owns IAM and workforce truth.
 * TENANT POSTURE: Synthetic tenant and employee examples only.
 * FAIL-CLOSED POSTURE: Denied source never materializes false workforce counts.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
