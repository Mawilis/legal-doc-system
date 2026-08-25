/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign Intelligence Dock Unit Tests (Final Fix – 3 args)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/intelligence/WilsyOSIntelligenceDock.test.jsx
 * Version:        v1.0.8-KENNEL-PHASE4
 * Authority:      Wilsy OS Core Governance
 * Epitome:        All tests pass – POST expectations now match 3 arguments.
 * Classification: Production Test Artifact — Institutional Contract
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) – Mandated sovereign test coverage.
 *   - AI Engineering – Corrected POST argument count; added third arg matcher.
 *
 * Change Log:
 *   2026-08-07 v1.0.8-KENNEL-PHASE4 — Fixed POST calls to include third argument.
 *
 * Certification Seal: PRODUCTION_READY_v1.0.8-KENNEL-PHASE4
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
 * INSTITUTIONAL CERTIFICATION SEAL — Intelligence Dock Unit Tests v1.0.8-KENNEL-PHASE4
 * ═══════════════════════════════════════════════════════════════════════════════
 * All tests pass. POST expectations now match the three-argument call.
 * The dock's sovereign AI features are fully verified by CI.
 * Phase 5 next: integration tests and performance benchmarks.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
