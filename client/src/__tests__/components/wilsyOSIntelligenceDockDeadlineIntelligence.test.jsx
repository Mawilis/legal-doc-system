/**
 * WILSY OS — INTELLIGENCE DOCK DEADLINE OBSERVATION CERTIFICATE
 * VERSION: v1.0.0-D6B-INTELLIGENCE-DOCK-DEADLINE-CERT
 * AUTHORITY: Browser presentation and transport-wiring evidence only.
 * EPITOME: Certifies that the global Dock reads the independent Core Legal D6
 *          projection for an explicit matter and renders observed posture without
 *          generating advice, due dates, reminders, mutations, or financial truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/wilsyOSIntelligenceDockDeadlineIntelligence.test.jsx
 * COLLABORATION / OWNERSHIP: D6/D6B and legalMatterDeadlineService own projection
 *                            truth and validation; this certificate owns synthetic UI evidence.
 * CERTIFICATION / UPDATE DATE: 2026-10-11
 * CHANGELOG: 2026-10-11 v1.0.0-D6B-INTELLIGENCE-DOCK-DEADLINE-CERT establishes
 *            explicit locator/time transport, read-only rendering, and denial posture.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only.
 * TENANT BOUNDARY: Tenant remains authenticated interceptor/server authority.
 * AUTHORITY BOUNDARY: UI certificate only; Python EOS remains sovereign.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED DECLARATION: Denied or unavailable reads render no fabricated posture.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';

const { apiGet, getDeadlineIntelligence } = vi.hoisted(() => ({
  apiGet: vi.fn(),
  getDeadlineIntelligence: vi.fn(),
}));

vi.mock('../../services/api.js', () => ({
  default: { get: apiGet, post: vi.fn() },
}));
vi.mock('../../services/legalMatterDeadlineService.js', () => ({
  getLegalMatterDeadlineIntelligence: getDeadlineIntelligence,
}));
vi.mock('../../services/wilsyAIAdvisoryApi.js', () => ({
  executeWilsyAILegalServices: vi.fn(),
  generateWilsyAILegalNextActions: vi.fn(),
  readWilsyAILegalNextAction: vi.fn(),
}));
vi.mock('../../components/intelligence/wilsyAIDynamicSuggestionEngine.js', () => ({
  buildWilsyDynamicSuggestions: () => [],
  recordWilsyAISuggestionUsage: vi.fn(),
}));
vi.mock('../../components/intelligence/wilsyAIConversationHistoryEngine.js', () => ({
  clearWilsyAIConversationThreads: vi.fn(),
  createWilsyAIConversationThread: vi.fn(async () => ({ id: 'thread-1', messages: [] })),
  loadWilsyAIConversationThreads: vi.fn(async () => [{ id: 'thread-1', messages: [] }]),
  persistWilsyAIConversationTurn: vi.fn(),
}));

import WilsyOSIntelligenceDock from '../../components/intelligence/WilsyOSIntelligenceDock.jsx';

beforeAll(() => {
  Element.prototype.scrollIntoView = vi.fn();
});

const projection = Object.freeze({
  caseMatterId: 'matter-1',
  observedAt: '2026-10-11T18:00:00.000Z',
  activeCount: 1,
  upcomingCount: 0,
  dueCount: 0,
  overdueCount: 1,
  inactiveCount: 0,
  fingerprint: 'a'.repeat(128),
  items: Object.freeze([
    Object.freeze({
      deadlineId: 'deadline-1',
      caseMatterId: 'matter-1',
      deadlineKind: 'FILING',
      dueAt: '2026-10-10T10:00:00.000000Z',
      sourceType: 'COURT_ORDER',
      jurisdictionReference: 'court:gp-hc',
      status: 'ACTIVE',
      temporalPosture: 'OVERDUE',
      deadlineFingerprint: 'b'.repeat(128),
    }),
  ]),
});

function renderDock() {
  return render(
    <WilsyOSIntelligenceDock
      authUser={{ id: 'principal-1', tenantId: 'tenant-1', role: 'LEGAL_PARTNER' }}
      activeTenant={{ tenantId: 'tenant-1', source: 'ACTIVE_TENANT_CONTEXT' }}
    />,
  );
}

describe('Intelligence Dock deadline observation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiGet.mockResolvedValue({ data: { status: 'OPERATIONAL' } });
  });

  it('reads explicit matter posture and labels it as observation, not advice', async () => {
    getDeadlineIntelligence.mockResolvedValueOnce(projection);
    renderDock();
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    fireEvent.click(await screen.findByRole('button', { name: /Deadlines/i }));
    fireEvent.change(screen.getByLabelText('Matter identifier for deadline observation'), {
      target: { value: 'matter-1' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Observe deadline posture' }));

    await waitFor(() => expect(getDeadlineIntelligence).toHaveBeenCalledTimes(1));
    const [matterId, observedAt] = getDeadlineIntelligence.mock.calls[0];
    expect(matterId).toBe('matter-1');
    expect(Number.isFinite(Date.parse(observedAt))).toBe(true);
    expect(screen.getByText(/Not legal advice or a recommendation/i)).toBeInTheDocument();
    expect(screen.getByText(/No legal-period calculation/i)).toBeInTheDocument();
    expect(screen.getByText('OVERDUE')).toBeInTheDocument();
    expect(screen.getByText(/FILING · due 2026-10-10/i)).toBeInTheDocument();
    expect(screen.queryByText(/generate reminder/i)).not.toBeInTheDocument();
  });

  it('renders bounded denial and never fabricates projection counts', async () => {
    getDeadlineIntelligence.mockRejectedValueOnce({ response: { status: 403 } });
    renderDock();
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    fireEvent.click(await screen.findByRole('button', { name: /Deadlines/i }));
    fireEvent.change(screen.getByLabelText('Matter identifier for deadline observation'), {
      target: { value: 'matter-denied' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Observe deadline posture' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Current tenant authority does not permit deadline intelligence access.',
    );
    expect(screen.queryByLabelText('Matter deadline observation')).not.toBeInTheDocument();
  });
});

/**
 * ARTIFACT: wilsyOSIntelligenceDockDeadlineIntelligence.test.jsx
 * VERSION: v1.0.0-D6B-INTELLIGENCE-DOCK-DEADLINE-CERT
 * AUTHORITY BOUNDARY: browser presentation/wiring certificate only
 * TENANT POSTURE: authenticated server-derived tenant scope only
 * FAIL-CLOSED POSTURE: denied/unavailable sources never produce observed posture
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
