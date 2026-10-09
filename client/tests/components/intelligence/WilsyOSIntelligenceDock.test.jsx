/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign Intelligence Dock Unit Tests (Authority-Aware Runtime)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/intelligence/WilsyOSIntelligenceDock.test.jsx
 * Version:        v1.4.0-LEGAL-AUTHORITY-AWARE-RUNTIME-CERT
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Certifies authority-aware Intelligence Dock routing: generic
 *                 non-legal Ask uses the canonical shared-api operator transport,
 *                 legal roles remain on certified C1C legal-services transport,
 *                 and billing-intelligence evidence is probed only for bounded
 *                 legal-finance roles without creating financial authority.
 * Classification: Production Test Artifact — Institutional Contract
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) – Mandated sovereign test coverage.
 *   - AI Engineering – Corrected POST argument count; added third arg matcher.
 *
 * Change Log:
 *   2026-09-24 v1.4.0-LEGAL-AUTHORITY-AWARE-RUNTIME-CERT — Aligned direct
 *     certification with finance-only billing evidence probes, C1C legal-role
 *     routing, canonical /ai/operator shared-api transport, and the canonical
 *     object-shaped session-history persistence contract.
 *   2026-09-17 v1.3.0-C1E-R1D-A1-WILSY-OS-BRAND-CONSOLIDATION-CERT — Added WILSY OS brand,
 *     single-runtime, and source-gated tenant-brand certificates while preserving R1C coverage.
 *   2026-09-17 v1.2.0-C1E-R1C-LEGAL-ADVISORY-PROJECTION-CERT — Added C1C/C1E sequencing, governed status,
 *     replay/error, stale-successor, and authority-boundary certificates.
 *   2026-09-13 v1.1.0-M14-P7 — Added exact billing-intelligence evidence GET,
 *     canonical payload preservation, explicit operator-context propagation,
 *     and no-fabrication failure certificates.
 *   2026-08-07 v1.0.8-KENNEL-PHASE4 — Fixed POST calls to include third argument.
 *
 * Certification Seal: PRODUCTION_READY_v1.4.0-LEGAL-AUTHORITY-AWARE-RUNTIME-CERT
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import React from 'react';
import { readFileSync } from 'node:fs';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import api from '../../../src/services/api.js';

// ──────────────────────────────────────────────────────────────────────────────
// MOCK scrollIntoView globally
// ──────────────────────────────────────────────────────────────────────────────
beforeEach(() => {
  Element.prototype.scrollIntoView = vi.fn();
});

// ──────────────────────────────────────────────────────────────────────────────
// HOISTED MOCK FUNCTIONS
// ──────────────────────────────────────────────────────────────────────────────

const {
  mockApiGet,
  mockApiPost,
  mockBuildSuggestions,
  mockRecordSuggestionUsage,
  mockLoadThreads,
  mockCreateThread,
  mockPersistTurn,
  mockClearThreads,
  mockExecuteLegalServices,
  mockGenerateLegalNextActions,
  mockReadLegalNextAction,
} = vi.hoisted(() => {
  const mockApiGet = vi.fn();
  const mockApiPost = vi.fn();
  const mockBuildSuggestions = vi.fn(() => [
    { id: 'sug1', title: 'Test Suggestion', prompt: 'Test prompt' },
  ]);
  const mockRecordSuggestionUsage = vi.fn();
  const mockLoadThreads = vi.fn();
  const mockCreateThread = vi.fn();
  const mockPersistTurn = vi.fn();
  const mockClearThreads = vi.fn();
  const mockExecuteLegalServices = vi.fn();
  const mockGenerateLegalNextActions = vi.fn();
  const mockReadLegalNextAction = vi.fn();

  return {
    mockApiGet,
    mockApiPost,
    mockBuildSuggestions,
    mockRecordSuggestionUsage,
    mockLoadThreads,
    mockCreateThread,
    mockPersistTurn,
    mockClearThreads,
    mockExecuteLegalServices,
    mockGenerateLegalNextActions,
    mockReadLegalNextAction,
  };
});

// ──────────────────────────────────────────────────────────────────────────────
// MOCKS
// ──────────────────────────────────────────────────────────────────────────────

vi.mock('../../../src/services/api.js', () => ({
  default: {
    get: mockApiGet,
    post: mockApiPost,
  },
}));

vi.mock('../../../src/services/wilsyAIAdvisoryApi.js', () => ({
  executeWilsyAILegalServices: mockExecuteLegalServices,
  generateWilsyAILegalNextActions: mockGenerateLegalNextActions,
  readWilsyAILegalNextAction: mockReadLegalNextAction,
}));

vi.mock('../../../src/components/intelligence/wilsyAIDynamicSuggestionEngine.js', () => ({
  buildWilsyDynamicSuggestions: mockBuildSuggestions,
  recordWilsyAISuggestionUsage: mockRecordSuggestionUsage,
}));

let mockThreads = [
  { id: 'thread1', title: 'Thread 1', messages: [] },
  { id: 'thread2', title: 'Thread 2', messages: [] },
];

vi.mock('../../../src/components/intelligence/wilsyAIConversationHistoryEngine.js', () => ({
  loadWilsyAIConversationThreads: mockLoadThreads,
  createWilsyAIConversationThread: mockCreateThread,
  persistWilsyAIConversationTurn: mockPersistTurn.mockImplementation(({ threadId, message } = {}) => {
    const thread = mockThreads.find((item) => item.id === threadId);
    if (!thread) throw new Error('WILSY_AI_SESSION_THREAD_NOT_FOUND');
    if (message && typeof message === 'object') thread.messages.push(message);
    return { ...thread, messages: [...thread.messages] };
  }),
  clearWilsyAIConversationThreads: mockClearThreads,
}));

mockLoadThreads.mockImplementation(() => mockThreads);

import WilsyOSIntelligenceDock from '../../../src/components/intelligence/WilsyOSIntelligenceDock.jsx';

const openLegalAdvisory = async () => {
  fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
  fireEvent.click(screen.getByRole('button', { name: /Legal Advisory/i }));
  await waitFor(() => expect(screen.getByText('Evidence-backed Legal Advisory')).toBeInTheDocument());
};

const advisoryFixture = (overrides = {}) => ({
  advisory_id: 'adv-001',
  scope_ref: 'matter-001',
  title: 'Confirm service address',
  rationale: 'The source record requires an address check.',
  confidence_score: 0.87,
  confidence_basis: { source_count: 2 },
  risk_level: 'MEDIUM',
  generated_at: '2026-09-17T09:00:00Z',
  status: 'CURRENT',
  superseded_by_advisory_id: null,
  ...overrides,
});

const rejectedResponse = (status, detail) => Object.assign(new Error(detail), {
  response: { status, data: { detail } },
});

// ──────────────────────────────────────────────────────────────────────────────
// TESTS
// ──────────────────────────────────────────────────────────────────────────────

describe('WilsyOSIntelligenceDock', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApiGet.mockReset();
    mockApiPost.mockReset();
    mockExecuteLegalServices.mockReset();
    mockGenerateLegalNextActions.mockReset();
    mockReadLegalNextAction.mockReset();
    mockThreads = [
      { id: 'thread1', title: 'Thread 1', messages: [] },
      { id: 'thread2', title: 'Thread 2', messages: [] },
    ];
    mockCreateThread.mockReset();
    mockCreateThread.mockImplementation((payload = {}) => {
      const thread = {
        id: 'newThread',
        title: payload.title || 'New Sovereign Session',
        workspace: payload.workspace || 'WILSY OS',
        messages: [],
      };
      mockThreads = [thread, ...mockThreads.filter((item) => item.id !== thread.id)];
      return thread;
    });
    window.__WILSY_ACTIVE_TENANT__ = { tenantId: 'TEST_TENANT' };
    window.__WILSY_AUTH_USER__ = { displayName: 'Test User' };
  });

  it('renders the launcher button when dock is closed', () => {
    render(<WilsyOSIntelligenceDock />);
    expect(screen.getByTitle('Open Wilsy OS Intelligence Dock')).toBeInTheDocument();
    expect(screen.queryByText('WILSY OS Intelligence Dock')).not.toBeInTheDocument();
  });

  it('opens the dock when launcher is clicked', async () => {
    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    await waitFor(() => {
      expect(screen.getByText('WILSY OS Intelligence Dock')).toBeInTheDocument();
    });
  });

  it('uses WILSY OS for the Dock-owned closed launcher and never exposes Wilsy AI as product copy', () => {
    render(<WilsyOSIntelligenceDock />);
    expect(screen.getByText('WILSY OS')).toBeInTheDocument();
    expect(screen.queryByText('Wilsy AI')).not.toBeInTheDocument();
    expect(screen.queryByText('WILSY AI')).not.toBeInTheDocument();
  });

  it('uses WILSY OS in the open Dock header and Ask surface', async () => {
    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    await waitFor(() => expect(screen.getByText('WILSY OS Intelligence Dock')).toBeInTheDocument());
    expect(screen.getByRole('button', { name: /Ask WILSY OS/i })).toBeInTheDocument();
  });

  it('uses WILSY OS as the assistant identity without changing generic operator transport', async () => {
    mockApiPost.mockResolvedValue({ data: { intelligence: { reply: 'Brand-safe reply' } } });
    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    fireEvent.change(screen.getByPlaceholderText('Ask Wilsy OS…'), { target: { value: 'Hello' } });
    fireEvent.click(screen.getByLabelText('Send'));
    await waitFor(() => expect(screen.getByText('Brand-safe reply')).toBeInTheDocument());
    expect(screen.getByText('WILSY OS')).toBeInTheDocument();
    expect(screen.queryByText('Wilsy AI')).not.toBeInTheDocument();
  });

  it('displays Wilsy (Pty) Ltd only when active tenant context explicitly proves it', async () => {
    const activeTenant = {
      tenantId: 'WILSY_ROOT',
      legalName: 'Wilsy (Pty) Ltd',
      source: 'ACTIVE_TENANT_CONTEXT',
    };
    render(<WilsyOSIntelligenceDock activeTenant={activeTenant} />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    await waitFor(() => expect(screen.getByText('Wilsy (Pty) Ltd')).toBeInTheDocument());
  });

  it('does not fabricate Wilsy (Pty) Ltd from unknown or MASTER-only tenant context', async () => {
    window.__WILSY_ACTIVE_TENANT__ = { tenantId: 'MASTER' };
    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    await waitFor(() => expect(screen.getByText('WILSY OS Intelligence Dock')).toBeInTheDocument());
    expect(screen.queryByText('Wilsy (Pty) Ltd')).not.toBeInTheDocument();
  });

  it('certifies the Dock runtime lives inside the authoritative App tree with no independent React root', () => {
    const mainSource = readFileSync(`${process.cwd()}/src/main.jsx`, 'utf8');
    const appSource = readFileSync(`${process.cwd()}/src/App.jsx`, 'utf8');

    expect(mainSource).not.toMatch(/import\s+WilsyOSIntelligenceDockRuntime/);
    expect(mainSource).not.toMatch(/createRoot\(dockRoot\)/);
    expect(mainSource).not.toContain('wilsy-os-intelligence-dock-root');

    expect(appSource).toMatch(/import\s+WilsyOSIntelligenceDockRuntime/);
    expect(appSource.match(/<WilsyOSIntelligenceDockRuntime\b/g)).toHaveLength(1);
  });

  it('does not probe billing intelligence for an unresolved or non-finance role', async () => {
    mockApiGet.mockResolvedValue({ status: 200, data: { status: 'OPERATIONAL' } });

    render(<WilsyOSIntelligenceDock authUser={{ role: 'LEGAL_ATTORNEY', tenantId: 'TEST_TENANT' }} />);

    await waitFor(() => {
      expect(mockApiGet).toHaveBeenCalledWith('/kernel', expect.objectContaining({}));
    });
    expect(
      mockApiGet.mock.calls.some(([path]) => path === '/billing/intelligence/evidence')
    ).toBe(false);
  });

  it('requests canonical billing evidence only for legal-finance authority with an aware ISO as_of boundary', async () => {
    mockApiGet.mockImplementation((path) => {
      if (path === '/billing/intelligence/evidence') {
        return Promise.resolve({ status: 403, data: { detail: 'forbidden' } });
      }
      return Promise.resolve({ status: path === '/kernel' ? 200 : 404, data: { status: 'OPERATIONAL' } });
    });

    render(<WilsyOSIntelligenceDock authUser={{ role: 'LEGAL_FINANCE', tenantId: 'TEST_TENANT' }} />);

    await waitFor(() => {
      const billingCall = mockApiGet.mock.calls.find(
        ([path]) => path === '/billing/intelligence/evidence'
      );
      expect(billingCall).toBeDefined();
      const asOf = billingCall[1]?.params?.as_of;
      expect(asOf).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
      expect(new Date(asOf).toISOString()).toBe(asOf);
    });
  });

  it('keeps legal-finance Ask on C1C legal-services authority even when billing evidence is available', async () => {
    const canonicalEvidence = {
      tenant_id: 'TEST_TENANT',
      as_of: '2026-09-13T12:00:00+00:00',
      evidence_contract: 'WILSY-BILLING-INTELLIGENCE-EVIDENCE/V1',
      unsupported_outputs: ['invoice', 'payment', 'settlement'],
      recurring_revenue: { mrr_minor: 49900, arr_minor: 598800, currency: 'ZAR' },
      recurring_revenue_growth: { classification: 'NO_CHANGE', numerator: 0, denominator: 49900 },
      evidence_fingerprint: 'a'.repeat(128),
      evidence_identity: 'evidence-test-1',
    };
    mockApiGet.mockImplementation((path) => {
      if (path === '/billing/intelligence/evidence') {
        return Promise.resolve({ status: 200, data: canonicalEvidence });
      }
      if (path === '/kernel') {
        return Promise.resolve({ status: 200, data: { status: 'OPERATIONAL' } });
      }
      return Promise.resolve({ status: 200, data: {} });
    });
    mockExecuteLegalServices.mockResolvedValue({
      status: 200,
      data: {
        outcome: 'DIRECT_RESPONSE',
        response_text: 'Finance-scoped legal response',
      },
    });

    render(<WilsyOSIntelligenceDock authUser={{ role: 'LEGAL_FINANCE', tenantId: 'TEST_TENANT' }} />);
    await waitFor(() => {
      expect(mockApiGet).toHaveBeenCalledWith(
        '/billing/intelligence/evidence',
        expect.objectContaining({ params: expect.objectContaining({ as_of: expect.any(String) }) })
      );
    });

    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    fireEvent.change(screen.getByPlaceholderText('Ask Wilsy OS…'), {
      target: { value: 'Show finance context' },
    });
    fireEvent.click(screen.getByLabelText('Send'));

    await waitFor(() => {
      expect(mockExecuteLegalServices).toHaveBeenCalledTimes(1);
    });
    expect(mockApiPost).not.toHaveBeenCalled();
    expect(screen.getByText('Finance-scoped legal response')).toBeInTheDocument();
  });

  it.each([
    ['unavailable', 'reject'],
    ['forbidden', 'forbidden'],
  ])('fails quiet without fabricating or widening authority when finance evidence is %s', async (_label, billingMode) => {
    mockApiGet.mockImplementation((path) => {
      if (path === '/billing/intelligence/evidence') {
        return billingMode === 'reject'
          ? Promise.reject(new Error('billing unavailable'))
          : Promise.resolve({ status: 403, data: { detail: 'forbidden' } });
      }
      if (path === '/kernel') return Promise.resolve({ status: 200, data: { status: 'OPERATIONAL' } });
      return Promise.resolve({ status: 200, data: {} });
    });
    mockExecuteLegalServices.mockResolvedValue({
      status: 200,
      data: {
        outcome: 'DIRECT_RESPONSE',
        response_text: 'Bounded legal response',
      },
    });

    render(<WilsyOSIntelligenceDock authUser={{ role: 'LEGAL_FINANCE', tenantId: 'TEST_TENANT' }} />);
    await waitFor(() => {
      expect(mockApiGet).toHaveBeenCalledWith(
        '/billing/intelligence/evidence',
        expect.anything()
      );
    });

    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    fireEvent.change(screen.getByPlaceholderText('Ask Wilsy OS…'), {
      target: { value: 'No fabricated finance facts' },
    });
    fireEvent.click(screen.getByLabelText('Send'));

    await waitFor(() => expect(mockExecuteLegalServices).toHaveBeenCalledTimes(1));
    expect(mockApiPost).not.toHaveBeenCalled();
    expect(screen.getByText('Bounded legal response')).toBeInTheDocument();
  });

  it('switches tabs correctly', async () => {
    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));

    fireEvent.click(screen.getByText('Suggestions'));
    await waitFor(() => {
      expect(screen.getByText('Dynamic Sovereign Suggestions')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('History'));
    await waitFor(() => {
      expect(screen.getByText('Conversation Threads')).toBeInTheDocument();
    });
  });

  it('sends a message when Enter is pressed', async () => {
    const mockReply = { data: { intelligence: { reply: 'Test reply' } } };
    mockApiPost.mockResolvedValue(mockReply);

    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));

    const textarea = screen.getByPlaceholderText('Ask Wilsy OS…');
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(mockApiPost).toHaveBeenCalledWith('/ai/operator', expect.objectContaining({}), expect.anything());
    });
    await waitFor(() => {
      expect(screen.getByText('Test reply')).toBeInTheDocument();
    });
  });

  it('sends a message when Send button is clicked', async () => {
    const mockReply = { data: { intelligence: { reply: 'Button reply' } } };
    mockApiPost.mockResolvedValue(mockReply);

    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));

    const textarea = screen.getByPlaceholderText('Ask Wilsy OS…');
    fireEvent.change(textarea, { target: { value: 'World' } });
    fireEvent.click(screen.getByLabelText('Send'));

    await waitFor(() => {
      expect(mockApiPost).toHaveBeenCalledWith('/ai/operator', expect.objectContaining({}), expect.anything());
    });
    await waitFor(() => {
      expect(screen.getByText('Button reply')).toBeInTheDocument();
    });
  });

  it('displays error when API call fails and falls back to error message', async () => {
    mockApiPost.mockRejectedValue(new Error('Network error'));

    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));

    const textarea = screen.getByPlaceholderText('Ask Wilsy OS…');
    fireEvent.change(textarea, { target: { value: 'Error test' } });
    fireEvent.click(screen.getByLabelText('Send'));

    await waitFor(() => {
      expect(screen.getByText(/I could not reach the Wilsy Operator Kernel/i)).toBeInTheDocument();
    });
  });

  it('creates a new thread when "New thread" is clicked', async () => {
    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    fireEvent.click(screen.getByText('History'));
    fireEvent.click(screen.getByText('+ New'));

    await waitFor(() => {
      expect(mockCreateThread).toHaveBeenCalled();
    });
    expect(screen.getByText('New Sovereign Session')).toBeInTheDocument();
  });

  it('refreshes threads and context when "Sync" is clicked', async () => {
    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    fireEvent.click(screen.getByText('History'));
    fireEvent.click(screen.getByText('⟳ Sync'));

    await waitFor(() => {
      expect(mockLoadThreads).toHaveBeenCalled();
      expect(mockApiGet).toHaveBeenCalledWith('/kernel', expect.objectContaining({}));
    });
  });

  it('clears history when "Clear" is clicked', async () => {
    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    fireEvent.click(screen.getByText('History'));
    fireEvent.click(screen.getByText('Clear'));

    await waitFor(() => {
      expect(mockClearThreads).toHaveBeenCalled();
      expect(mockCreateThread).toHaveBeenCalled();
    });
  });

  it('triggers a suggestion click and sends its prompt', async () => {
    const mockReply = { data: { intelligence: { reply: 'Suggestion reply' } } };
    mockApiPost.mockResolvedValue(mockReply);

    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    fireEvent.click(screen.getByText('Suggestions'));

    const suggestionButton = screen.getByText('Test Suggestion');
    fireEvent.click(suggestionButton);

    await waitFor(() => {
      expect(mockRecordSuggestionUsage).toHaveBeenCalledWith('sug1');
      expect(mockApiPost).toHaveBeenCalledWith('/ai/operator', expect.objectContaining({}), expect.anything());
    });
    await waitFor(() => {
      expect(screen.getByText('Suggestion reply')).toBeInTheDocument();
    });
  });

  it('handles empty prompt gracefully', async () => {
    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));

    const textarea = screen.getByPlaceholderText('Ask Wilsy OS…');
    fireEvent.change(textarea, { target: { value: '   ' } });
    fireEvent.click(screen.getByLabelText('Send'));

    expect(mockApiPost).not.toHaveBeenCalled();
  });

  it('disables send button while submitting', async () => {
    mockApiPost.mockReturnValue(new Promise(() => {}));

    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));

    const textarea = screen.getByPlaceholderText('Ask Wilsy OS…');
    fireEvent.change(textarea, { target: { value: 'Test' } });
    fireEvent.click(screen.getByLabelText('Send'));

    await waitFor(() => {
      expect(screen.getByLabelText('Send')).toBeDisabled();
    });
  });

  it('keeps Legal Advisory distinct and never auto-runs C1C/C1E', async () => {
    render(<WilsyOSIntelligenceDock />);
    expect(mockExecuteLegalServices).not.toHaveBeenCalled();
    expect(mockGenerateLegalNextActions).not.toHaveBeenCalled();
    await openLegalAdvisory();
    expect(screen.getByRole('button', { name: /Suggestions/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /History/i })).toBeInTheDocument();
    expect(mockExecuteLegalServices).not.toHaveBeenCalled();
  });

  it('requires explicit prompt submission, creates one UUID replay key, and sequences C1C before C1E', async () => {
    mockExecuteLegalServices.mockResolvedValue({
      status: 200,
      data: { orchestration_id: 'orch-001', outcome: 'TOOL_ASSISTED', response_text: 'Evidence found', sources: ['registry'] },
    });
    mockGenerateLegalNextActions.mockResolvedValue({ status: 201, data: advisoryFixture() });
    render(<WilsyOSIntelligenceDock />);
    await openLegalAdvisory();
    fireEvent.change(screen.getByLabelText('Legal advisory prompt'), { target: { value: 'Check service address' } });
    fireEvent.click(screen.getByRole('button', { name: /Generate evidence-backed next action/i }));
    await waitFor(() => expect(mockGenerateLegalNextActions).toHaveBeenCalledWith('orch-001'));
    expect(mockExecuteLegalServices).toHaveBeenCalledTimes(1);
    expect(mockExecuteLegalServices).toHaveBeenCalledWith('Check service address', expect.stringMatching(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i));
    expect(mockExecuteLegalServices.mock.invocationCallOrder[0]).toBeLessThan(mockGenerateLegalNextActions.mock.invocationCallOrder[0]);
  });

  it('does not call C1E for a non-tool-assisted C1C outcome', async () => {
    mockExecuteLegalServices.mockResolvedValue({ status: 200, data: { orchestration_id: 'orch-002', outcome: 'DIRECT_RESPONSE', response_text: 'Service response', sources: [] } });
    render(<WilsyOSIntelligenceDock />);
    await openLegalAdvisory();
    fireEvent.change(screen.getByLabelText('Legal advisory prompt'), { target: { value: 'Status?' } });
    fireEvent.click(screen.getByRole('button', { name: /Generate evidence-backed next action/i }));
    await waitFor(() => expect(screen.getByText('Legal service response')).toBeInTheDocument());
    expect(screen.getByText('Evidence-backed advisory not generated')).toBeInTheDocument();
    expect(mockGenerateLegalNextActions).not.toHaveBeenCalled();
  });

  it('renders the server-owned advisory fields and current status without rewriting rationale', async () => {
    mockExecuteLegalServices.mockResolvedValue({ status: 200, data: { orchestration_id: 'orch-003', outcome: 'TOOL_ASSISTED', response_text: 'Evidence', sources: ['source-a'] } });
    mockGenerateLegalNextActions.mockResolvedValue({ status: 200, data: advisoryFixture() });
    render(<WilsyOSIntelligenceDock />);
    await openLegalAdvisory();
    fireEvent.change(screen.getByLabelText('Legal advisory prompt'), { target: { value: 'Prompt' } });
    fireEvent.click(screen.getByRole('button', { name: /Generate evidence-backed next action/i }));
    await waitFor(() => expect(screen.getByRole('region', { name: 'Evidence-backed advisory' })).toBeInTheDocument());
    for (const field of ['adv-001', 'matter-001', 'Confirm service address', 'The source record requires an address check.', '87.0%', 'source_count', 'MEDIUM', '2026-09-17T09:00:00Z']) {
      expect(screen.getByText(field, { exact: false })).toBeInTheDocument();
    }
    expect(screen.getByText('CURRENT')).toBeInTheDocument();
    expect(mockApiPost).not.toHaveBeenCalledWith('/ai/operator', expect.anything(), expect.anything());
  });

  it('renders stale state and only permits read-only refresh or successor viewing', async () => {
    const stale = advisoryFixture({ status: 'STALE', superseded_by_advisory_id: 'adv-002' });
    mockExecuteLegalServices.mockResolvedValue({ status: 200, data: { orchestration_id: 'orch-004', outcome: 'TOOL_ASSISTED', response_text: 'Evidence', sources: [] } });
    mockGenerateLegalNextActions.mockResolvedValue({ status: 201, data: stale });
    mockReadLegalNextAction.mockResolvedValue({ status: 200, data: advisoryFixture({ advisory_id: 'adv-002', title: 'Successor', status: 'CURRENT' }) });
    render(<WilsyOSIntelligenceDock />);
    await openLegalAdvisory();
    fireEvent.change(screen.getByLabelText('Legal advisory prompt'), { target: { value: 'Prompt' } });
    fireEvent.click(screen.getByRole('button', { name: /Generate evidence-backed next action/i }));
    await waitFor(() => expect(screen.getByText('STALE')).toBeInTheDocument());
    expect(screen.queryByRole('button', { name: /Execute|Approve|Serve|Issue|Release|Pay|Settle|Invoice|Quote|Send command/i })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /View successor/i }));
    await waitFor(() => expect(mockReadLegalNextAction).toHaveBeenCalledWith('adv-002'));
    fireEvent.click(screen.getByRole('button', { name: /Refresh status/i }));
    await waitFor(() => expect(mockReadLegalNextAction).toHaveBeenCalledWith('adv-002'));
    expect(mockGenerateLegalNextActions).toHaveBeenCalledTimes(1);
  });

  it.each([
    [403, 'C1E_LEGAL_ACCESS_DENIED', /authority denied/i],
    [404, 'C1E_RESOURCE_NOT_FOUND', /unavailable/i],
    [409, 'C1E_TOOL_ASSISTED_REQUIRED', /tool-assisted orchestration is required/i],
    [409, 'C1E_SOURCE_SNAPSHOT_STALE', /source snapshot is stale/i],
    [409, 'C1E_ADVISORY_CONFLICT', /advisory conflict/i],
    [422, 'VALIDATION_ERROR', /request contract rejected/i],
    [503, 'C1E_ADVISORY_RECONCILIATION_REQUIRED', /requires reconciliation/i],
    [503, 'C1E_ADVISORY_UNAVAILABLE', /service unavailable/i],
  ])('maps C1C failures (%s) without creating an advisory', async (status, detail, message) => {
    mockExecuteLegalServices.mockRejectedValue(rejectedResponse(status, detail));
    render(<WilsyOSIntelligenceDock />);
    await openLegalAdvisory();
    fireEvent.change(screen.getByLabelText('Legal advisory prompt'), { target: { value: 'Prompt' } });
    fireEvent.click(screen.getByRole('button', { name: /Generate evidence-backed next action/i }));
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(message));
    expect(mockExecuteLegalServices).toHaveBeenCalledTimes(1);
    expect(mockGenerateLegalNextActions).not.toHaveBeenCalled();
    expect(screen.queryByRole('region', { name: 'Evidence-backed advisory' })).not.toBeInTheDocument();
  });

  it('maps network failure, does not retry, and keeps C1E out of browser persistence and history', async () => {
    mockExecuteLegalServices.mockRejectedValue(new Error('offline'));
    const setItem = vi.spyOn(Storage.prototype, 'setItem');
    render(<WilsyOSIntelligenceDock />);
    await openLegalAdvisory();
    fireEvent.change(screen.getByLabelText('Legal advisory prompt'), { target: { value: 'Prompt' } });
    fireEvent.click(screen.getByRole('button', { name: /Generate evidence-backed next action/i }));
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(/source unavailable/i));
    expect(mockExecuteLegalServices).toHaveBeenCalledTimes(1);
    expect(mockPersistTurn).not.toHaveBeenCalled();
    expect(setItem).not.toHaveBeenCalled();
    setItem.mockRestore();
  });

  it('keeps generic Suggestions separate from the C1E advisory surface', async () => {
    render(<WilsyOSIntelligenceDock />);
    await openLegalAdvisory();
    expect(screen.queryByText('Dynamic Sovereign Suggestions')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Suggestions/i }));
    expect(screen.getByText('Dynamic Sovereign Suggestions')).toBeInTheDocument();
    expect(screen.queryByText('Evidence-backed Legal Advisory')).not.toBeInTheDocument();
  });
});

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — Intelligence Dock Unit Tests v1.4.0-LEGAL-AUTHORITY-AWARE-RUNTIME-CERT
 * ═══════════════════════════════════════════════════════════════════════════════
 * Direct tests certify finance-only billing-intelligence probing, non-finance
 * exclusion, canonical generic operator transport, C1C legal-role routing, and
 * same-session conversation-history interaction without widening authority.
 * Broader client/CI certification remains a separate gate beyond this direct certificate.
 * Host-backed billing-intelligence evidence remains a separate runtime gate.
 * C1E legal advisory proof remains a read-only client projection; no command,
 * payment, settlement, subscription, tenant-plan, or financial authority is introduced.
 * ARTIFACT: WilsyOSIntelligenceDock.test.jsx
 * VERSION: v1.4.0-LEGAL-AUTHORITY-AWARE-RUNTIME-CERT
 * AUTHORITY BOUNDARY: certificate only; Python EOS remains sovereign
 * TENANT POSTURE: adapter calls preserve authenticated api.js context
 * FAIL-CLOSED POSTURE: failed/stale outcomes never produce advisory cards
 * FINANCIAL EXECUTION AUTHORITY: none
 * END OF WILSY OS SOVEREIGN ARTIFACT
 * ═══════════════════════════════════════════════════════════════════════════════
 */
