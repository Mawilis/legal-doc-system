/**
 * WILSY OS — LEGAL ROLE EXPERIENCE MATRIX CERTIFICATE
 * VERSION: v1.3.0-LEGAL-CLIENT-ACCEPTANCE-REVIEW-CERT
 * AUTHORITY: Browser presentation/wiring evidence only.
 * EPITOME: Certifies that every published Legal persona renders from authenticated
 *          identity plus server-derived authority/capability projections, exposes
 *          only its current activities, and never falls back to another role's
 *          endpoint family.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardRoleExperienceMatrix.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-25
 * CHANGELOG: 2026-09-25 v1.3.0-LEGAL-CLIENT-ACCEPTANCE-REVIEW-CERT updates Legal Practice fixtures with the certified conflict-screening read projection; role identity/activity and permission posture assertions remain unchanged.
 *            v1.1.0-D24C-AUTHENTICATED-PERSON-NAME-PRESENTATION-CERT proves exact authenticated firstName/lastName presentation across Legal practice, finance, client, sheriff and deputy postures; email remains separately visible when distinct, while malformed names and forged legacy displayName/name fields cannot override the bounded fallback. Identity presentation creates no tenant, membership, role, permission, capability, legal lifecycle, billing, payment, execution or settlement authority.
 *            v1.0.0-L8-7D20-MULTI-ROLE-IDENTITY-ACTIVITY-POSTURE-CERT established the multi-role Legal identity/activity and permission-posture matrix.
 * TENANT BOUNDARY: Every fixture is tenant-scoped and synthetic.
 * AUTHORITY BOUNDARY: UI posture is explanatory only; Python EOS owns legal
 *                     authorization and Kennel EOS owns financial execution.
 * FAIL-CLOSED DECLARATION: Missing permissions/capabilities remove controls;
 *                          browser role labels never create authority.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const {
  generateLegalReturnOfService,
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getLegalClientMatters,
  getLegalClientAcceptanceInstruments,
  createLegalClientAcceptanceContext,
  getLegalClientAcceptanceContent,
  confirmLegalClientAcceptance,
  getLegalConflictScreenings,
  getLegalFinanceEvidence,
  getLegalPracticeWorkspace,
  getSheriffOperationalQueues,
  recordDeputyFieldOutcome,
  registerLegalIntake,
  transitionDeputyFieldAttempt,
} = vi.hoisted(() => ({
  generateLegalReturnOfService: vi.fn(),
  getDeputyFieldCapabilities: vi.fn(),
  getDeputyPersonalActiveWork: vi.fn(),
  getLegalClientMatters: vi.fn(),
  getLegalClientAcceptanceInstruments: vi.fn(),
  createLegalClientAcceptanceContext: vi.fn(),
  getLegalClientAcceptanceContent: vi.fn(),
  confirmLegalClientAcceptance: vi.fn(),
  getLegalConflictScreenings: vi.fn(),
  getLegalFinanceEvidence: vi.fn(),
  getLegalPracticeWorkspace: vi.fn(),
  getSheriffOperationalQueues: vi.fn(),
  recordDeputyFieldOutcome: vi.fn(),
  registerLegalIntake: vi.fn(),
  transitionDeputyFieldAttempt: vi.fn(),
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'v1.6.0-L8-7D15-MATTER-WORKSPACE-COMPATIBILITY',
  generateLegalReturnOfService,
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getLegalClientMatters,
  getLegalClientAcceptanceInstruments,
  createLegalClientAcceptanceContext,
  getLegalClientAcceptanceContent,
  confirmLegalClientAcceptance,
  getLegalConflictScreenings,
  getLegalFinanceEvidence,
  getLegalPracticeWorkspace,
  getSheriffOperationalQueues,
  recordDeputyFieldOutcome,
  registerLegalIntake,
  transitionDeputyFieldAttempt,
}));

vi.mock('../../contexts/authContext', () => ({
  useAuth: () => ({
    user: {
      id: 'context-principal',
      email: 'context@example.test',
      role: 'tenant_legal_partner',
      tenantId: 'tenant-law',
    },
    tenant: {
      tenantId: 'tenant-law',
      displayName: 'Context Legal Tenant',
      status: 'ACTIVE',
    },
  }),
}));

vi.mock('../../contexts/tenantContext', () => ({
  useTenants: () => ({
    activeTenant: {
      tenantId: 'tenant-law',
      displayName: 'Context Legal Tenant',
      status: 'ACTIVE',
    },
    tenants: [],
  }),
}));

import LegalDashboard from '../../components/industry/LegalDashboard.jsx';

const ALL_LEGAL_PERMISSIONS = Object.freeze([
  'legal_operations:instruction:write',
  'legal_operations:return:write',
  'legal_operations:billing:read',
  'legal_operations:invoice:read',
]);

const practiceWorkspace = () => ({
  schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2',
  version: 'v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API',
  tenantId: 'tenant-law',
  visibility: 'LEGAL_PRACTICE_WORKSPACE',
  summary: {
    matters_total: 0,
    matters_open: 0,
    matters_closed: 0,
    instructions_total: 0,
    instructions_registered: 0,
    instructions_accepted: 0,
    instructions_closed: 0,
    instructions_cancelled: 0,
    documents_total: 0,
    documents_registered: 0,
    documents_received: 0,
    documents_allocated: 0,
    documents_returned: 0,
    attempts_total: 0,
    attempts_allocated: 0,
    attempts_attempted: 0,
    attempts_completed: 0,
    attempts_not_completed: 0,
    attempts_cancelled: 0,
    executions_total: 0,
    executions_completed: 0,
    executions_not_completed: 0,
    returns_total: 0,
  },
  matters: [],
  instructions: [],
  documents: [],
  attempts: [],
  executions: [],
  returns: [],
});

const clientMatters = () => ({
  schema: 'WILSY-LEGAL-CLIENT-MATTER-PROJECTION/V1',
  version: 'v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION',
  tenantId: 'tenant-client',
  visibility: 'LEGAL_CLIENT_EXPLICIT_MATTERS',
  matters: [],
});

const clientMatterReviewSet = () => ({
  ...clientMatters(),
  matters: [
    {
      caseMatterId: 'matter-open',
      matterReference: 'CLIENT-OPEN',
      openedAt: '2026-10-01T08:00:00+00:00',
      state: 'OPEN',
    },
    {
      caseMatterId: 'matter-closed',
      matterReference: 'CLIENT-CLOSED',
      openedAt: '2026-09-01T08:00:00+00:00',
      state: 'CLOSED',
    },
  ],
});

const acceptanceInstrumentProjection = () => ({
  schema: 'WILSY-LEGAL-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION/V1',
  version: 'v1.0.0-L9A4-P2E-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION',
  tenantId: 'tenant-client',
  caseMatterId: 'matter-open',
  visibility: 'LEGAL_CLIENT_ACTIONABLE_ACCEPTANCE_INSTRUMENTS',
  instruments: [
    {
      instrumentId: 'terms-1',
      version: '1.0.0',
      instrumentKind: 'CLIENT_REVIEW_TERMS',
      title: 'Client review terms',
      reviewScope: 'client-information-review:v1',
      effectiveFrom: '2026-10-10T08:00:00+00:00',
      instrumentFingerprint: 'a'.repeat(128),
      contentFingerprint: 'b'.repeat(128),
    },
  ],
});

const acceptanceContext = () => ({
  acceptanceContextId: 'context-1',
  caseMatterId: 'matter-open',
  instrumentId: 'terms-1',
  instrumentVersion: '1.0.0',
  title: 'Client review terms',
  reviewScope: 'client-information-review:v1',
  issuedAt: '2026-10-12T05:00:00+00:00',
  expiresAt: '2026-10-12T05:10:00+00:00',
  contentFingerprint: 'b'.repeat(128),
});

const acceptanceContent = () => ({
  acceptanceContextId: 'context-1',
  instrumentId: 'terms-1',
  instrumentVersion: '1.0.0',
  contentFingerprint: 'b'.repeat(128),
  mediaType: 'text/plain',
  content: 'Certified client review content.',
});

const acceptanceReceipt = () => ({
  acceptanceId: 'LEGAL-CLIENT-ACCEPT:context-1',
  caseMatterId: 'matter-open',
  acceptanceScope: 'client-information-review:v1',
  acceptedAt: '2026-10-12T05:05:00+00:00',
  fingerprint: 'c'.repeat(128),
});

const sheriffQueues = () => ({
  tenantId: 'tenant-sheriff',
  visibility: 'SHERIFF_OPERATIONAL_QUEUE',
  officeReceipt: [],
  deputyAssignment: [],
  activeAttempts: [],
});

const CURRENT_EVIDENCE = 'a'.repeat(128);

const deputyWork = () => ({
  tenantId: 'tenant-deputy',
  visibility: 'DEPUTY_PERSONAL_ACTIVE_WORK',
  deputyId: 'deputy-bound',
  activeAttempts: [{
    tenant_id: 'tenant-deputy',
    attempt_id: 'attempt-mine',
    instruction_id: 'instruction-mine',
    document_id: 'document-mine',
    deputy_id: 'deputy-bound',
    state: 'ATTEMPTED',
    allocated_at: '2026-09-24T18:00:00+00:00',
  }],
});

const deputyCapabilities = () => ({
  tenantId: 'tenant-deputy',
  visibility: 'DEPUTY_FIELD_COMMAND_CAPABILITIES',
  deputyId: 'deputy-bound',
  capabilities: [{
    tenantId: 'tenant-deputy',
    attemptId: 'attempt-mine',
    instructionId: 'instruction-mine',
    documentId: 'document-mine',
    deputyId: 'deputy-bound',
    currentState: 'ATTEMPTED',
    currentEvidenceIdentity: CURRENT_EVIDENCE,
    nextCommandKinds: [
      'RECORD_COMPLETED_OUTCOME',
      'RECORD_NOT_COMPLETED_OUTCOME',
    ],
  }],
});

function installLocalStorageStub() {
  const values = new Map();
  const storage = {
    getItem: vi.fn((key) => values.get(String(key)) ?? null),
    setItem: vi.fn((key, value) => values.set(String(key), String(value))),
    removeItem: vi.fn((key) => values.delete(String(key))),
    clear: vi.fn(() => values.clear()),
  };
  Object.defineProperty(window, 'localStorage', { configurable: true, value: storage });
  Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: storage });
  storage.setItem('wilsy.legal-operations.field-device.v1', 'browser-device:matrix');
}

function authoritativeUser(
  role,
  permissions,
  email,
  firstName = 'Avery',
  lastName = 'Counsel',
) {
  return {
    id: `principal-${role.toLowerCase()}`,
    email,
    firstName,
    lastName,
    role: `tenant_${role.toLowerCase()}`,
    tenantId: 'tenant-law',
    permissions,
    legalPermissionsAuthoritative: true,
  };
}

function assertNoSpecialistFallback() {
  expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
  expect(getDeputyPersonalActiveWork).not.toHaveBeenCalled();
  expect(getDeputyFieldCapabilities).not.toHaveBeenCalled();
  expect(getLegalClientMatters).not.toHaveBeenCalled();
}

describe('D20 Legal role experience matrix', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getLegalConflictScreenings.mockResolvedValue({
      schema: 'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1',
      version: 'v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API',
      tenantId: 'tenant-law',
      visibility: 'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE',
      screenings: [],
    });
    installLocalStorageStub();
  });

  for (const {
    role,
    permissions,
    expectedLanes,
    email,
  } of [
    {
      role: 'LEGAL_PARTNER',
      permissions: ALL_LEGAL_PERMISSIONS,
      expectedLanes: 'Intake · Return generation · Billing evidence · Invoice evidence',
      email: 'partner@example.test',
    },
    {
      role: 'LEGAL_ATTORNEY',
      permissions: ALL_LEGAL_PERMISSIONS,
      expectedLanes: 'Intake · Return generation · Billing evidence · Invoice evidence',
      email: 'attorney@example.test',
    },
    {
      role: 'LEGAL_PARALEGAL',
      permissions: [
        'legal_operations:instruction:write',
        'legal_operations:return:write',
        'legal_operations:invoice:read',
      ],
      expectedLanes: 'Intake · Return generation · Invoice evidence',
      email: 'paralegal@example.test',
    },
    {
      role: 'LEGAL_SECRETARY',
      permissions: [
        'legal_operations:return:write',
        'legal_operations:invoice:read',
      ],
      expectedLanes: 'Return generation · Invoice evidence',
      email: 'secretary@example.test',
    },
  ]) {
    it(`binds ${role} UI to the authenticated principal and authoritative permission projection`, async () => {
      getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());
      render(
        <LegalDashboard
          roleView={role}
          user={authoritativeUser(role, permissions, email)}
          tenantConfig={{ tenantId: 'tenant-law', displayName: 'Matrix Legal Practice' }}
        />,
      );

      await screen.findByText('Legal Operations Command Center');
      const posture = screen.getByLabelText('Legal presentation authority posture');
      expect(within(posture).getByText('Server permission projection')).toBeInTheDocument();
      expect(within(posture).getByText('Avery Counsel')).toBeInTheDocument();
      expect(within(posture).getByText(email)).toBeInTheDocument();
      expect(within(posture).getByText(role)).toBeInTheDocument();
      expect(within(posture).getByText(expectedLanes)).toBeInTheDocument();
      expect(getLegalPracticeWorkspace).toHaveBeenCalledTimes(1);
      assertNoSpecialistFallback();
    });
  }

  it('binds LEGAL_FINANCE to exact evidence lanes without practice/client/field reads', async () => {
    const user = authoritativeUser(
      'LEGAL_FINANCE',
      ['legal_operations:billing:read', 'legal_operations:invoice:read'],
      'finance@example.test',
    );
    render(
      <LegalDashboard
        roleView="LEGAL_FINANCE"
        user={user}
        tenantConfig={{ tenantId: 'tenant-law' }}
      />,
    );

    expect(await screen.findByText('Legal Finance Evidence')).toBeInTheDocument();
    const posture = screen.getByLabelText('Legal presentation authority posture');
    expect(within(posture).getByText('Server permission projection')).toBeInTheDocument();
    expect(within(posture).getByText('Avery Counsel')).toBeInTheDocument();
    expect(within(posture).getByText('finance@example.test')).toBeInTheDocument();
    expect(within(posture).getByText('LEGAL_FINANCE')).toBeInTheDocument();
    expect(within(posture).getByText('Billing evidence · Invoice evidence')).toBeInTheDocument();
    expect(getLegalPracticeWorkspace).not.toHaveBeenCalled();
    assertNoSpecialistFallback();
  });

  it('binds LEGAL_CLIENT to the server client-visibility projection only', async () => {
    getLegalClientMatters.mockResolvedValueOnce(clientMatters());
    render(
      <LegalDashboard
        roleView="LEGAL_CLIENT"
        user={{
          id: 'principal-client',
          email: 'client@example.test',
          firstName: 'Casey',
          lastName: 'Client',
        }}
        tenantConfig={{ tenantId: 'tenant-client' }}
      />,
    );

    await screen.findByText('Client Matter Workspace');
    const posture = screen.getByLabelText('Legal identity and activity posture');
    expect(within(posture).getByText('Casey Client')).toBeInTheDocument();
    expect(within(posture).getByText('client@example.test')).toBeInTheDocument();
    expect(within(posture).getByText('LEGAL_CLIENT')).toBeInTheDocument();
    expect(within(posture).getByText('Server client visibility projection')).toBeInTheDocument();
    expect(within(posture).getByText('Visible matter read · Matter search · Acceptance review · Explicit confirmation · Canonical refresh')).toBeInTheDocument();
    expect(getLegalClientMatters).toHaveBeenCalledTimes(1);
    expect(getLegalPracticeWorkspace).not.toHaveBeenCalled();
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
    expect(getDeputyPersonalActiveWork).not.toHaveBeenCalled();
  });

  it('allows acceptance review only from an OPEN visible matter and records only explicit confirmation', async () => {
    getLegalClientMatters.mockResolvedValueOnce(clientMatterReviewSet());
    getLegalClientAcceptanceInstruments.mockResolvedValueOnce(
      acceptanceInstrumentProjection(),
    );
    createLegalClientAcceptanceContext.mockResolvedValueOnce(
      acceptanceContext(),
    );
    getLegalClientAcceptanceContent.mockResolvedValueOnce(
      acceptanceContent(),
    );
    confirmLegalClientAcceptance.mockResolvedValueOnce(
      acceptanceReceipt(),
    );

    render(
      <LegalDashboard
        roleView="LEGAL_CLIENT"
        user={{
          id: 'principal-client',
          email: 'client@example.test',
          firstName: 'Casey',
          lastName: 'Client',
        }}
        tenantConfig={{ tenantId: 'tenant-client' }}
      />,
    );

    await screen.findByText('CLIENT-OPEN');
    expect(
      screen.getByRole('button', { name: 'Review acceptance for CLIENT-OPEN' }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: 'Review acceptance for CLIENT-CLOSED' }),
    ).not.toBeInTheDocument();

    fireEvent.click(
      screen.getByRole('button', { name: 'Review acceptance for CLIENT-OPEN' }),
    );
    await screen.findByText('Available certified reviews');
    expect(getLegalClientAcceptanceInstruments).toHaveBeenCalledTimes(1);
    expect(getLegalClientAcceptanceInstruments).toHaveBeenCalledWith('matter-open');
    expect(createLegalClientAcceptanceContext).not.toHaveBeenCalled();
    expect(confirmLegalClientAcceptance).not.toHaveBeenCalled();

    fireEvent.click(
      screen.getByRole('button', { name: 'Open certified review' }),
    );
    await screen.findByText('Certified client review content.');
    expect(createLegalClientAcceptanceContext).toHaveBeenCalledTimes(1);
    expect(getLegalClientAcceptanceContent).toHaveBeenCalledTimes(1);
    expect(confirmLegalClientAcceptance).not.toHaveBeenCalled();

    fireEvent.click(
      screen.getByRole('button', { name: 'Confirm acceptance' }),
    );
    await screen.findByText(/Acceptance recorded at/);
    expect(confirmLegalClientAcceptance).toHaveBeenCalledTimes(1);
    expect(confirmLegalClientAcceptance).toHaveBeenCalledWith(
      expect.objectContaining({
        acceptanceContextId: 'context-1',
        confirmed: true,
      }),
    );
  });

  it('binds SHERIFF to tenant operational queues without Deputy or practice fallback', async () => {
    getSheriffOperationalQueues.mockResolvedValueOnce(sheriffQueues());
    render(
      <LegalDashboard
        roleView="SHERIFF"
        user={{
          id: 'principal-sheriff',
          email: 'sheriff@example.test',
          firstName: 'Sam',
          lastName: 'Sheriff',
        }}
        tenantConfig={{ tenantId: 'tenant-sheriff' }}
      />,
    );

    const posture = await screen.findByLabelText('Legal identity and activity posture');
    expect(within(posture).getByText('Sam Sheriff')).toBeInTheDocument();
    expect(within(posture).getByText('sheriff@example.test')).toBeInTheDocument();
    expect(within(posture).getByText('SHERIFF')).toBeInTheDocument();
    expect(within(posture).getByText('Server operational queue projection')).toBeInTheDocument();
    expect(within(posture).getByText('Office receipt queue · Deputy assignment queue · Active service attempts')).toBeInTheDocument();
    expect(getSheriffOperationalQueues).toHaveBeenCalledTimes(1);
    expect(getDeputyPersonalActiveWork).not.toHaveBeenCalled();
    expect(getDeputyFieldCapabilities).not.toHaveBeenCalled();
    expect(getLegalPracticeWorkspace).not.toHaveBeenCalled();
    expect(getLegalClientMatters).not.toHaveBeenCalled();
  });

  it('binds DEPUTY activities to the current server-issued capability packet only', async () => {
    getDeputyPersonalActiveWork.mockResolvedValueOnce(deputyWork());
    getDeputyFieldCapabilities.mockResolvedValueOnce(deputyCapabilities());
    render(
      <LegalDashboard
        roleView="DEPUTY"
        user={{
          id: 'principal-deputy',
          email: 'deputy@example.test',
          firstName: 'Drew',
          lastName: 'Deputy',
        }}
        tenantConfig={{ tenantId: 'tenant-deputy' }}
      />,
    );

    const posture = await screen.findByLabelText('Legal identity and activity posture');
    expect(within(posture).getByText('Drew Deputy')).toBeInTheDocument();
    expect(within(posture).getByText('deputy@example.test')).toBeInTheDocument();
    expect(within(posture).getByText('DEPUTY')).toBeInTheDocument();
    expect(within(posture).getByText('Server bound-work + capability projection')).toBeInTheDocument();
    expect(within(posture).getByText('Record completed outcome · Record not completed')).toBeInTheDocument();
    expect(within(posture).queryByText('Begin attempt')).not.toBeInTheDocument();
    expect(getDeputyPersonalActiveWork).toHaveBeenCalledTimes(1);
    expect(getDeputyFieldCapabilities).toHaveBeenCalledTimes(1);
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
    expect(getLegalPracticeWorkspace).not.toHaveBeenCalled();
    expect(getLegalClientMatters).not.toHaveBeenCalled();
  });

  it('does not normalize malformed names or trust legacy display-name fields', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());

    render(
      <LegalDashboard
        roleView="LEGAL_PARTNER"
        user={{
          ...authoritativeUser(
            'LEGAL_PARTNER',
            ALL_LEGAL_PERMISSIONS,
            'partner@example.test',
            ' Avery ',
            '',
          ),
          displayName: 'FORGED DISPLAY NAME',
          name: 'FORGED NAME',
        }}
        tenantConfig={{ tenantId: 'tenant-law' }}
      />,
    );

    await screen.findByText('Legal Operations Command Center');
    const posture = screen.getByLabelText('Legal presentation authority posture');
    expect(within(posture).getByText('partner@example.test')).toBeInTheDocument();
    expect(within(posture).queryByText('Avery')).not.toBeInTheDocument();
    expect(within(posture).queryByText('FORGED DISPLAY NAME')).not.toBeInTheDocument();
    expect(within(posture).queryByText('FORGED NAME')).not.toBeInTheDocument();
  });

  it('keeps unresolved Legal scope network-silent', async () => {
    render(
      <LegalDashboard
        roleView="LEGAL_VIEW"
        user={{ id: 'principal-unknown', email: 'unknown@example.test' }}
      />,
    );

    expect(await screen.findByText('LEGAL_ROLE_SCOPE_REQUIRED')).toBeInTheDocument();
    expect(getLegalPracticeWorkspace).not.toHaveBeenCalled();
    expect(getLegalClientMatters).not.toHaveBeenCalled();
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
    expect(getDeputyPersonalActiveWork).not.toHaveBeenCalled();
    expect(getDeputyFieldCapabilities).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: legalDashboardRoleExperienceMatrix.test.jsx
 * VERSION: v1.3.0-LEGAL-CLIENT-ACCEPTANCE-REVIEW-CERT
 * AUTHORITY BOUNDARY: browser presentation evidence only; D24C person-name rendering is descriptive AuthContext projection and Python EOS owns authentication/authorization
 * TENANT POSTURE: synthetic exact tenant scopes only; no cross-tenant fallback
 * FAIL-CLOSED POSTURE: malformed/absent person names are never normalized or inferred, forged legacy name fields do not override bounded identity, permissions/capabilities narrow controls, and unresolved role is network-silent
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
