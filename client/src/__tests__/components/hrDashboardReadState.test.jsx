/**
 * TITLE: WILSY OS HR Dashboard Read-State Runtime Regressions
 * VERSION: v1.8.2-HIRING-EMPTY-CONTRACT-RECONCILIATION
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Exercises mounted HR dashboard behavior when EOS invalidates a session,
 *          an exact tenant scope changes during an outstanding read, or a command
 *          acknowledgement cannot be confirmed by current source readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/hrDashboardReadState.test.jsx
 * COLLABORATION / OWNERSHIP: Runtime regression coverage for HrDashboard.jsx and its authenticated source adapters.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
 * CHANGELOG: v1.8.2-HIRING-EMPTY-CONTRACT-RECONCILIATION uses current People navigation and canonical workforce provenance; preserves source-readback, custody, 401 and cross-tenant race assertions.
 * CHANGELOG:
 *   v1.8.2-HIRING-EMPTY-CONTRACT-RECONCILIATION asserts the real verified-empty Hiring heading instead of deleted prototype copy; preserves all candidate command idempotency, evidence, tenant, session, and source readback journeys.
 *   v1.8.2-HIRING-EMPTY-CONTRACT-RECONCILIATION checks the canonical Workforce employee button after the tab's table-to-directory migration; existing candidate command, session invalidation, tenant swap and EOS readback checks are preserved.
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
    source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
    items: [{
      employeeId: name,
      displayName: name,
      preferredName: name,
      workEmail: `${name.toLowerCase().replaceAll(' ', '.')}@example.invalid`,
      jobTitle: 'Engineer',
      department: 'Engineering',
      employmentStatus: 'ACTIVE',
    }],
    total: 1,
    limit: 12,
    offset: 0,
    hasMore: false,
  },
});

const emptyPage = { items: [], total: 0, limit: 12, offset: 0, hasMore: false };
const emptySnapshot = {
  data: { summary: {}, sourceStatus: 'SOURCE_VERIFIED', timestamp: '2026-11-12T00:00:00Z' },
};

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
    user: { id: principalId, email: `${principalId}@example.invalid`, role: 'tenant_hr_manager' },
    logout: vi.fn(),
  };
  mockState.tenant = {
    activeTenant: { tenantId, name: `Synthetic ${tenantId}` },
    authorityMismatch: false,
  };
};

const openLane = async (name) => {
  const nav = await screen.findByRole('navigation', { name: 'People operating functions' });
  fireEvent.click(within(nav).getByRole('button', { name, exact: true }));
};

const renderDashboard = async () => {
  const view = render(<HrDashboard />);
  await openLane('Workforce');
  return view;
};

afterEach(() => {
  cleanup();
});

beforeEach(() => {
  window.history.replaceState(null, '', '/');
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
    if (path === '/hr/workforce/overview') return Promise.resolve({ data: {
      schema: 'WILSY-PEOPLE-WORKFORCE-OVERVIEW/V1', source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
      tenant_id: mockState.auth.tenantId, metrics: { active_employees: 1, departments: 1 },
      generated_at: '2026-11-27T00:00:00Z',
    } });
    if (path === '/hr/workforce') return Promise.resolve(validPage('Tenant A Verified Employee'));
    return Promise.reject(Object.assign(new Error('synthetic unavailable source'), { response: { status: 404 } }));
  });
});

describe('mounted HR dashboard read-state boundaries', () => {
  it('renders canonical candidate and offer pages without exposing profile references or legacy write controls', async () => {
    mockState.candidateRead.mockResolvedValue({
      items: [{
        tenant_id: 'TENANT-HR-A', candidate_id: 'CAN-EOS-2026-01',
        requisition_id: 'REQ-EOS-2026-01', candidate_profile_reference: 'PROFILE-PRIVATE-REF',
        source: 'CAREERS_PORTAL', stage: 'APPLIED', revision: 1, fingerprint: 'a'.repeat(128),
      }],
      total: 1, limit: 12, offset: 0, hasMore: false,
    });
    mockState.offerRead.mockResolvedValue({
      items: [{
        tenant_id: 'TENANT-HR-A', offer_id: 'OFFER-EOS-2026-01',
        candidate_id: 'CAN-EOS-2026-01', requisition_id: 'REQ-EOS-2026-01',
        status: 'DRAFT', revision: 1, fingerprint: 'b'.repeat(128), terms: { gross_compensation_minor: 123456789 },
      }],
      total: 1, limit: 12, offset: 0, hasMore: false,
    });

    await renderDashboard();
    expect(await screen.findByRole('button', { name: /Tenant A Verified Employee/ })).toBeInTheDocument();
    await openLane('Hiring');
    expect(await screen.findByText('CAN-EOS-2026-01')).toBeInTheDocument();
    expect(screen.getByText(/Requisition REQ-EOS-2026-01/)).toBeInTheDocument();
    expect(screen.queryByText('PROFILE-PRIVATE-REF')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create candidate', exact: true })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Advance with evidence' })).toBeInTheDocument();
    expect(mockState.candidateRead).toHaveBeenCalledWith('TENANT-HR-A', expect.objectContaining({ limit: 12, offset: 0 }));

    await openLane('Offers');
    expect(await screen.findByText('OFFER-EOS-2026-01')).toBeInTheDocument();
    expect(screen.queryByText('123456789')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Prepare offer', exact: true })).toBeEnabled();
    expect(mockState.offerRead).toHaveBeenCalledWith('TENANT-HR-A', expect.objectContaining({ limit: 12, offset: 0 }));
    expect(mockState.legacyCandidateRead).not.toHaveBeenCalled();
    expect(mockState.legacyCandidateCreate).not.toHaveBeenCalled();
    expect(mockState.legacyCandidateDelete).not.toHaveBeenCalled();
  });

  it('requires matching EOS custody readback before enabling a candidate stage transition', async () => {
    const candidate = {
      tenant_id: 'TENANT-HR-A', candidate_id: 'CAN-EVIDENCE-UI-1',
      requisition_id: 'REQ-APPROVED-UI-1', stage: 'APPLIED', revision: 1,
      fingerprint: 'a'.repeat(128),
    };
    const digest = sha3_512('candidate profile bytes');
    const file = new File(['candidate profile bytes'], 'founder-candidate-profile.pdf', { type: 'application/pdf' });
    file.arrayBuffer = vi.fn().mockResolvedValue(new TextEncoder().encode('candidate profile bytes').buffer);
    const evidenceId = 'EVD-fixed-uuid';
    const evidenceVersionId = 'VER-fixed-uuid';
    const reference = `candidate-evidence://${evidenceId}/${evidenceVersionId}`;
    const updatedCandidate = { ...candidate, stage: 'SCREENING', revision: 2, fingerprint: 'b'.repeat(128) };
    mockState.candidateRead
      .mockResolvedValue({ items: [candidate], total: 1, limit: 12, offset: 0, hasMore: false });
    mockState.candidateEvidenceUpload.mockResolvedValueOnce({
      status: 'CUSTODY_REGISTERED', custody_registered: true,
      candidate_id: candidate.candidate_id, evidence_id: evidenceId,
      evidence_version_id: evidenceVersionId, byte_length: file.size,
      content_digest_sha3_512: digest,
    });
    const readbackBlob = new Blob(['candidate profile bytes']);
    readbackBlob.arrayBuffer = vi.fn().mockResolvedValue(new TextEncoder().encode('candidate profile bytes').buffer);
    mockState.candidateEvidenceReadback.mockResolvedValueOnce({
      blob: readbackBlob, contentDigestSha3_512: digest, contentLength: file.size,
    });
    mockState.candidateTransition.mockImplementationOnce(async () => {
      mockState.candidateRead.mockResolvedValue({ items: [updatedCandidate], total: 1, limit: 12, offset: 0, hasMore: false });
      return { ...updatedCandidate, tenant_id: 'TENANT-HR-A' };
    });
    vi.stubGlobal('crypto', { randomUUID: () => 'fixed-uuid' });

    try {
      await renderDashboard();
      expect(await screen.findByRole('button', { name: /Tenant A Verified Employee/ })).toBeInTheDocument();
      await openLane('Hiring');
      expect(await screen.findByText(candidate.candidate_id)).toBeInTheDocument();
      fireEvent.click(screen.getByRole('button', { name: 'Advance with evidence' }));
      const runCommand = screen.getByRole('button', { name: 'Run EOS command' });
      expect(runCommand).toBeDisabled();
      fireEvent.change(screen.getByLabelText('Candidate evidence file *'), { target: { files: [file] } });
      fireEvent.click(screen.getByRole('button', { name: 'Upload and verify evidence' }));

      expect(await screen.findByText('EOS custody verified')).toBeInTheDocument();
      expect(runCommand).toBeEnabled();
      expect(mockState.candidateEvidenceUpload).toHaveBeenCalledWith(
        candidate.candidate_id, evidenceId, evidenceVersionId, file,
        { mediaType: 'application/pdf', originalFilename: 'candidate-profile.pdf', evidenceKind: 'CANDIDATE_PROFILE' },
        'TENANT-HR-A',
      );
      expect(mockState.candidateEvidenceReadback).toHaveBeenCalledWith(
        candidate.candidate_id, evidenceId, evidenceVersionId, 'TENANT-HR-A',
      );
      fireEvent.change(screen.getByLabelText('Decision reason *'), { target: { value: 'Reviewed candidate profile' } });
      fireEvent.click(runCommand);
      expect(await screen.findByText(/Requisition REQ-APPROVED-UI-1 · SCREENING/)).toBeInTheDocument();
      expect(mockState.candidateTransition).toHaveBeenCalledWith(candidate.candidate_id, {
        expected_revision: 1,
        target_stage: 'SCREENING',
        reason: 'Reviewed candidate profile',
        evidence_reference: reference,
        evidence_fingerprint: digest,
      }, 'TENANT-HR-A', expect.any(String));
    } finally {
      vi.unstubAllGlobals();
    }
  });

  it('ignores late candidate evidence upload results after authenticated tenant scope changes', async () => {
    const pendingUpload = deferred();
    const candidate = {
      tenant_id: 'TENANT-HR-A', candidate_id: 'CAN-EVIDENCE-RACE-1',
      requisition_id: 'REQ-APPROVED-RACE-1', stage: 'APPLIED', revision: 1,
      fingerprint: 'c'.repeat(128),
    };
    mockState.candidateRead.mockResolvedValue({
      items: [candidate], total: 1, limit: 12, offset: 0, hasMore: false,
    });
    mockState.candidateEvidenceUpload.mockReturnValueOnce(pendingUpload.promise);
    vi.stubGlobal('crypto', { randomUUID: () => 'race-uuid' });

    try {
      const view = await renderDashboard();
      expect(await screen.findByRole('button', { name: /Tenant A Verified Employee/ })).toBeInTheDocument();
      await openLane('Hiring');
      expect(await screen.findByText(candidate.candidate_id)).toBeInTheDocument();
      fireEvent.click(screen.getByRole('button', { name: 'Advance with evidence' }));
      const file = new File(['late evidence'], 'profile.pdf', { type: 'application/pdf' });
      file.arrayBuffer = vi.fn().mockResolvedValue(new TextEncoder().encode('late evidence').buffer);
      fireEvent.change(screen.getByLabelText('Candidate evidence file *'), { target: { files: [file] } });
      fireEvent.click(screen.getByRole('button', { name: 'Upload and verify evidence' }));
      await waitFor(() => expect(mockState.candidateEvidenceUpload).toHaveBeenCalled());

      setAuthenticatedScope('TENANT-HR-B', 'PRINCIPAL-HR-B', 2);
      view.rerender(<HrDashboard />);
      await act(async () => {
        pendingUpload.resolve({
          status: 'CUSTODY_REGISTERED', custody_registered: true,
          candidate_id: candidate.candidate_id, evidence_id: 'EVD-race-uuid',
          evidence_version_id: 'VER-race-uuid', byte_length: file.size,
          content_digest_sha3_512: sha3_512('late evidence'),
        });
        await pendingUpload.promise;
      });

      expect(screen.queryByRole('dialog', { name: 'Python EOS hiring command' })).not.toBeInTheDocument();
      expect(screen.queryByText(/candidate-evidence/)).not.toBeInTheDocument();
      expect(mockState.candidateEvidenceReadback).not.toHaveBeenCalled();
      expect(mockState.candidateTransition).not.toHaveBeenCalled();
    } finally {
      vi.unstubAllGlobals();
    }
  });

  it('creates a candidate through the canonical EOS route and requires exact durable readback', async () => {
    const candidate = {
      tenant_id: 'TENANT-HR-A', candidate_id: 'CAN-EOS-CREATE-1',
      requisition_id: 'REQ-EOS-APPROVED-1',
      candidate_profile_reference: 'candidate-profile://opaque/create-1',
      source: 'CAREERS_PORTAL', stage: 'APPLIED', revision: 1,
      fingerprint: 'c'.repeat(128),
    };
    mockState.candidateRead.mockResolvedValue(emptyPage);
    mockState.candidateCreate.mockImplementationOnce(async () => {
      mockState.candidateRead.mockResolvedValue({ items: [candidate], total: 1, limit: 12, offset: 0, hasMore: false });
      return candidate;
    });
    vi.stubGlobal('crypto', { randomUUID: () => 'candidate-command-key-1' });

    try {
      await renderDashboard();
      expect(await screen.findByRole('button', { name: /Tenant A Verified Employee/ })).toBeInTheDocument();
      await openLane('Hiring');
      expect(await screen.findByRole('heading', { name: 'No candidates yet' })).toBeInTheDocument();
      fireEvent.click(screen.getByRole('button', { name: 'Create candidate', exact: true }));
      fireEvent.change(screen.getByLabelText(/Candidate ID/), { target: { value: candidate.candidate_id } });
      fireEvent.change(screen.getByLabelText(/Approved requisition ID/), { target: { value: candidate.requisition_id } });
      fireEvent.change(screen.getByLabelText(/Opaque candidate profile reference/), { target: { value: candidate.candidate_profile_reference } });
      fireEvent.change(screen.getByLabelText(/Application source/), { target: { value: candidate.source } });
      fireEvent.click(screen.getByRole('button', { name: 'Run EOS command' }));

      expect(await screen.findByText(candidate.candidate_id)).toBeInTheDocument();
      expect(mockState.candidateCreate).toHaveBeenCalledWith({
        candidate_id: candidate.candidate_id,
        requisition_id: candidate.requisition_id,
        candidate_profile_reference: candidate.candidate_profile_reference,
        source: candidate.source,
      }, 'TENANT-HR-A', 'candidate-command-key-1');
      expect(mockState.candidateRead.mock.calls.length).toBeGreaterThanOrEqual(2);
      expect(mockState.legacyCandidateCreate).not.toHaveBeenCalled();
    } finally {
      vi.unstubAllGlobals();
    }
  });

  it('keeps an acknowledged candidate command unverified and reuses its idempotency key until readback succeeds', async () => {
    const candidate = {
      tenant_id: 'TENANT-HR-A', candidate_id: 'CAN-EOS-RETRY-1',
      requisition_id: 'REQ-EOS-APPROVED-2',
      candidate_profile_reference: 'candidate-profile://opaque/retry-1',
      source: 'CAREERS_PORTAL', stage: 'APPLIED', revision: 1,
      fingerprint: 'd'.repeat(128),
    };
    const readbackFailure = Object.assign(new Error('synthetic source timeout'), { response: { status: 503 } });
    mockState.candidateRead.mockResolvedValue(emptyPage);
    mockState.candidateCreate.mockImplementationOnce(async () => {
      mockState.candidateRead.mockRejectedValueOnce(readbackFailure);
      return candidate;
    }).mockImplementationOnce(async () => {
      mockState.candidateRead.mockResolvedValue({ items: [candidate], total: 1, limit: 12, offset: 0, hasMore: false });
      return candidate;
    });
    vi.stubGlobal('crypto', { randomUUID: () => 'candidate-command-key-retry' });

    try {
      await renderDashboard();
      expect(await screen.findByRole('button', { name: /Tenant A Verified Employee/ })).toBeInTheDocument();
      await openLane('Hiring');
      expect(await screen.findByRole('heading', { name: 'No candidates yet' })).toBeInTheDocument();
      fireEvent.click(screen.getByRole('button', { name: 'Create candidate', exact: true }));
      fireEvent.change(screen.getByLabelText(/Candidate ID/), { target: { value: candidate.candidate_id } });
      fireEvent.change(screen.getByLabelText(/Approved requisition ID/), { target: { value: candidate.requisition_id } });
      fireEvent.change(screen.getByLabelText(/Opaque candidate profile reference/), { target: { value: candidate.candidate_profile_reference } });
      fireEvent.change(screen.getByLabelText(/Application source/), { target: { value: candidate.source } });
      fireEvent.click(screen.getByRole('button', { name: 'Run EOS command' }));
      expect(await screen.findByText(/tenant-scoped durable readback is unavailable/i)).toBeInTheDocument();
      expect(screen.queryByText(candidate.candidate_id)).not.toBeInTheDocument();

      fireEvent.click(screen.getByRole('button', { name: 'Run EOS command' }));
      expect(await screen.findByText(candidate.candidate_id)).toBeInTheDocument();
      expect(mockState.candidateCreate).toHaveBeenCalledTimes(2);
      expect(mockState.candidateCreate).toHaveBeenNthCalledWith(
        1, expect.any(Object), 'TENANT-HR-A', 'candidate-command-key-retry',
      );
      expect(mockState.candidateCreate).toHaveBeenNthCalledWith(
        2, expect.any(Object), 'TENANT-HR-A', 'candidate-command-key-retry',
      );
    } finally {
      vi.unstubAllGlobals();
    }
  });

  it('clears retained rows and rejects pending source reads when any current-scope read returns 401', async () => {
    const pendingCandidate = deferred();
    let workforceReads = 0;
    let rejectWorkforce = false;

    mockState.apiGet.mockImplementation((path) => {
      if (path === '/hr/workforce/overview') return Promise.resolve({ data: {
      schema: 'WILSY-PEOPLE-WORKFORCE-OVERVIEW/V1', source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
      tenant_id: mockState.auth.tenantId, metrics: { active_employees: 1, departments: 1 },
      generated_at: '2026-11-27T00:00:00Z',
    } });
      if (path === '/hr/workforce') {
        workforceReads += 1;
        if (!rejectWorkforce) return Promise.resolve(validPage('Tenant A Verified Employee'));
        const error = new Error('synthetic expired session');
        error.response = { status: 401 };
        return Promise.reject(error);
      }
      return Promise.reject(Object.assign(new Error('synthetic unavailable source'), { response: { status: 404 } }));
    });

    await renderDashboard();
    expect(await screen.findByRole('button', { name: /Tenant A Verified Employee/ })).toBeInTheDocument();

    rejectWorkforce = true;
    mockState.candidateRead.mockReturnValue(pendingCandidate.promise);
    await openLane('Hiring');
    await waitFor(() => expect(mockState.candidateRead).toHaveBeenCalled());
    await openLane('Overview');
    expect(await screen.findByRole('heading', { name: 'Authentication required' })).toBeInTheDocument();
    expect(screen.queryByText('Tenant A Verified Employee')).not.toBeInTheDocument();

    await act(async () => {
      pendingCandidate.resolve({
        items: [{ candidate_id: 'LATE-CANDIDATE-A', stage: 'APPLIED' }],
        total: 1,
        limit: 12,
        offset: 0,
        hasMore: false,
      });
      await pendingCandidate.promise;
    });

    expect(screen.queryByText('LATE-CANDIDATE-A')).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Authentication required' })).toBeInTheDocument();
  });

  it('rejects a late tenant A response after the mounted dashboard moves to tenant B', async () => {
    const tenantARead = deferred();
    let tenantAStarted = false;
    mockState.apiGet.mockImplementation((path, config = {}) => {
      if (path === '/hr/workforce/overview') return Promise.resolve({ data: {
      schema: 'WILSY-PEOPLE-WORKFORCE-OVERVIEW/V1', source: 'AUTHORISED_HR_EMPLOYEE_REGISTRY',
      tenant_id: mockState.auth.tenantId, metrics: { active_employees: 1, departments: 1 },
      generated_at: '2026-11-27T00:00:00Z',
    } });
      if (path === '/hr/workforce' && config.headers?.['X-Tenant-ID'] === 'TENANT-HR-A') {
        tenantAStarted = true;
        return tenantARead.promise;
      }
      if (path === '/hr/workforce' && config.headers?.['X-Tenant-ID'] === 'TENANT-HR-B') {
        return Promise.resolve(validPage('Tenant B Verified Employee'));
      }
      return Promise.reject(Object.assign(new Error('synthetic unavailable source'), { response: { status: 404 } }));
    });

    const view = render(<HrDashboard />);
    await waitFor(() => expect(tenantAStarted).toBe(true));

    setAuthenticatedScope('TENANT-HR-B', 'PRINCIPAL-HR-B', 2);
    view.rerender(<HrDashboard />);
    await openLane('Workforce');
    expect(await screen.findByRole('button', { name: /Tenant B Verified Employee/ })).toBeInTheDocument();

    await act(async () => {
      tenantARead.resolve(validPage('Tenant A Late Employee'));
      await tenantARead.promise;
    });

    expect(screen.getByRole('button', { name: /Tenant B Verified Employee/ })).toBeInTheDocument();
    expect(screen.queryByText('Tenant A Late Employee')).not.toBeInTheDocument();
    expect(mockState.apiGet).toHaveBeenCalledWith('/hr/workforce', expect.objectContaining({
      headers: { 'X-Tenant-ID': 'TENANT-HR-B' },
    }));
  });

  it('rejects an acknowledged candidate when current readback has a different fingerprint', async () => {
    await renderDashboard();
    expect(await screen.findByRole('button', { name: /Tenant A Verified Employee/ })).toBeInTheDocument();
    await openLane('Hiring');
    expect(await screen.findByRole('heading', { name: 'No candidates yet' })).toBeInTheDocument();
    const candidate = {
      tenant_id: 'TENANT-HR-A', candidate_id: 'CAN-ACK-MISMATCH',
      requisition_id: 'REQ-ACK-MISMATCH', candidate_profile_reference: 'candidate-profile://opaque/mismatch',
      source: 'CAREERS_PORTAL', stage: 'APPLIED', revision: 1, fingerprint: 'e'.repeat(128),
    };
    mockState.candidateCreate.mockImplementationOnce(async () => {
      mockState.candidateRead.mockResolvedValue({ items: [{ ...candidate, fingerprint: 'f'.repeat(128) }],
        total: 1, limit: 12, offset: 0, hasMore: false });
      return candidate;
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create candidate', exact: true }));
    fireEvent.change(screen.getByLabelText(/Candidate ID/), { target: { value: candidate.candidate_id } });
    fireEvent.change(screen.getByLabelText(/Approved requisition ID/), { target: { value: candidate.requisition_id } });
    fireEvent.change(screen.getByLabelText(/Opaque candidate profile reference/), { target: { value: candidate.candidate_profile_reference } });
    fireEvent.change(screen.getByLabelText(/Application source/), { target: { value: candidate.source } });
    fireEvent.click(screen.getByRole('button', { name: 'Run EOS command' }));
    expect(await screen.findByText(/current source page does not prove the exact identity/)).toHaveTextContent('No success is claimed.');
    expect(screen.queryByText(/is confirmed by the current tenant-scoped EOS readback/)).not.toBeInTheDocument();
    expect(mockState.legacyCandidateCreate).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: client/src/__tests__/components/hrDashboardReadState.test.jsx
 * VERSION: v1.8.2-HIRING-EMPTY-CONTRACT-RECONCILIATION
 * AUTHORITY BOUNDARY: Mounted UI behavior only; Python EOS owns source and authorization truth.
 * TENANT POSTURE: Synthetic exact tenant/principal scopes; no cross-tenant source data is persisted.
 * FAIL-CLOSED POSTURE: A 401 clears retained HR rows, superseded tenant responses are ignored, and failed readback is not reported as verified success.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
