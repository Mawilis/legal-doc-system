/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign Intelligence Dock Unit Tests (M14-P7 Evidence Projection)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/intelligence/WilsyOSIntelligenceDock.test.jsx
 * Version:        v1.1.0-M14-P7-BILLING-INTELLIGENCE-EVIDENCE-CERT
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Certifies canonical billing-intelligence evidence projection,
 *                 explicit snapshot requests, payload preservation, and
 *                 fail-quiet optional behavior alongside the Phase 4 operator seam.
 * Classification: Production Test Artifact — Institutional Contract
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) – Mandated sovereign test coverage.
 *   - AI Engineering – Corrected POST argument count; added third arg matcher.
 *
 * Change Log:
 *   2026-09-13 v1.1.0-M14-P7 — Added exact billing-intelligence evidence GET,
 *     canonical payload preservation, explicit operator-context propagation,
 *     and no-fabrication failure certificates.
 *   2026-08-07 v1.0.8-KENNEL-PHASE4 — Fixed POST calls to include third argument.
 *
 * Certification Seal: PRODUCTION_READY_v1.1.0-M14-P7-BILLING-INTELLIGENCE-EVIDENCE-CERT
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import React from 'react';
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
} = vi.hoisted(() => {
  const mockApiGet = vi.fn();
  const mockApiPost = vi.fn();
  const mockBuildSuggestions = vi.fn(() => [
    { id: 'sug1', title: 'Test Suggestion', prompt: 'Test prompt' },
  ]);
  const mockRecordSuggestionUsage = vi.fn();
  const mockLoadThreads = vi.fn();
  const mockCreateThread = vi.fn(() => ({ id: 'newThread', title: 'New Sovereign Session' }));
  const mockPersistTurn = vi.fn();
  const mockClearThreads = vi.fn();

  return {
    mockApiGet,
    mockApiPost,
    mockBuildSuggestions,
    mockRecordSuggestionUsage,
    mockLoadThreads,
    mockCreateThread,
    mockPersistTurn,
    mockClearThreads,
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
  persistWilsyAIConversationTurn: vi.fn((threadId, turn) => {
    const thread = mockThreads.find(t => t.id === threadId);
    if (thread) thread.messages.push(turn);
    return [...mockThreads];
  }),
  clearWilsyAIConversationThreads: mockClearThreads,
}));

mockLoadThreads.mockImplementation(() => mockThreads);

import WilsyOSIntelligenceDock from '../../../src/components/intelligence/WilsyOSIntelligenceDock.jsx';

// ──────────────────────────────────────────────────────────────────────────────
// TESTS
// ──────────────────────────────────────────────────────────────────────────────

describe('WilsyOSIntelligenceDock', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApiGet.mockReset();
    mockApiPost.mockReset();
    mockThreads = [
      { id: 'thread1', title: 'Thread 1', messages: [] },
      { id: 'thread2', title: 'Thread 2', messages: [] },
    ];
    window.__WILSY_ACTIVE_TENANT__ = { tenantId: 'TEST_TENANT' };
    window.__WILSY_AUTH_USER__ = { displayName: 'Test User' };
  });

  it('renders the launcher button when dock is closed', () => {
    render(<WilsyOSIntelligenceDock />);
    expect(screen.getByTitle('Open Wilsy OS Intelligence Dock')).toBeInTheDocument();
    expect(screen.queryByText('Wilsy OS Intelligence Dock')).not.toBeInTheDocument();
  });

  it('opens the dock when launcher is clicked', async () => {
    render(<WilsyOSIntelligenceDock />);
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    await waitFor(() => {
      expect(screen.getByText('Wilsy OS Intelligence Dock')).toBeInTheDocument();
    });
  });

  it('requests canonical billing evidence with an explicit aware ISO as_of boundary', async () => {
    mockApiGet.mockImplementation((path) => {
      if (path === '/billing/intelligence/evidence') {
        return Promise.resolve({ status: 403, data: { detail: 'forbidden' } });
      }
      return Promise.resolve({ status: path === '/kernel' ? 200 : 404, data: { status: 'OPERATIONAL' } });
    });

    render(<WilsyOSIntelligenceDock />);

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

  it('preserves the canonical billing payload and names operator-context propagation explicitly', async () => {
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
    mockApiPost.mockResolvedValue({ data: { intelligence: { reply: 'ok' } } });

    render(<WilsyOSIntelligenceDock />);
    await waitFor(() => {
      expect(mockApiGet).toHaveBeenCalledWith(
        '/billing/intelligence/evidence',
        expect.objectContaining({ params: expect.objectContaining({ as_of: expect.any(String) }) })
      );
    });
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    const textarea = screen.getByPlaceholderText('Ask Wilsy OS…');
    fireEvent.change(textarea, { target: { value: 'Show billing evidence' } });
    fireEvent.click(screen.getByLabelText('Send'));

    await waitFor(() => expect(mockApiPost).toHaveBeenCalled());
    const requestBody = mockApiPost.mock.calls[0][1];
    expect(requestBody.context.canonicalBillingIntelligenceEvidence).toEqual(canonicalEvidence);
    expect(requestBody.context).not.toHaveProperty('billingIntelligenceEvidence');
  });

  it.each([
    ['unavailable', 'reject'],
    ['forbidden', 'forbidden'],
  ])('fails quiet without fabrication when billing evidence is %s', async (_label, billingMode) => {
    mockApiGet.mockImplementation((path) => {
      if (path === '/billing/intelligence/evidence') {
        return billingMode === 'reject'
          ? Promise.reject(new Error('billing unavailable'))
          : Promise.resolve({ status: 403, data: { detail: 'forbidden' } });
      }
      if (path === '/kernel') return Promise.resolve({ status: 200, data: { status: 'OPERATIONAL' } });
      return Promise.resolve({ status: 200, data: {} });
    });
    mockApiPost.mockResolvedValue({ data: { intelligence: { reply: 'ok' } } });

    render(<WilsyOSIntelligenceDock />);
    await waitFor(() => {
      expect(mockApiGet).toHaveBeenCalledWith(
        '/billing/intelligence/evidence',
        expect.anything()
      );
    });
    fireEvent.click(screen.getByTitle('Open Wilsy OS Intelligence Dock'));
    const textarea = screen.getByPlaceholderText('Ask Wilsy OS…');
    fireEvent.change(textarea, { target: { value: 'No fabricated billing facts' } });
    fireEvent.click(screen.getByLabelText('Send'));

    await waitFor(() => expect(mockApiPost).toHaveBeenCalled());
    const requestBody = mockApiPost.mock.calls[0][1];
    expect(requestBody.context).not.toHaveProperty('canonicalBillingIntelligenceEvidence');
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
      expect(mockApiPost).toHaveBeenCalledWith('/api/ai/operator', expect.objectContaining({}), expect.anything());
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
      expect(mockApiPost).toHaveBeenCalledWith('/api/ai/operator', expect.objectContaining({}), expect.anything());
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
      expect(mockApiPost).toHaveBeenCalledWith('/api/ai/operator', expect.objectContaining({}), expect.anything());
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
});

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — Intelligence Dock Unit Tests v1.1.0-M14-P7-BILLING-INTELLIGENCE-EVIDENCE-CERT
 * ═══════════════════════════════════════════════════════════════════════════════
 * Direct tests certify the canonical billing-intelligence GET projection,
 * explicit snapshot boundary, unchanged payload forwarding, and fail-quiet behavior.
 * Broader client/CI certification remains a separate gate beyond this direct certificate.
 * Host-backed billing-intelligence evidence remains a separate runtime gate.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
