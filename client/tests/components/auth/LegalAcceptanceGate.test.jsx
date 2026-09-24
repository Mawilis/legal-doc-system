/**
 * TITLE: WILSY OS Legal Admission Interaction-Shell Direct Certificate
 * VERSION: v1.7.1-DOM-COMPATIBLE-RECORD-SCROLL-RESET-CERT
 * AUTHORITY: Wilsy OS Core Governance; client projection evidence only
 * EPITOME: Certifies the legal gate as a compact, keyboard- and pointer-usable
 *           operating shell without duplicating Python EOS legal authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/auth/LegalAcceptanceGate.test.jsx
 * COLLABORATION / OWNERSHIP: Exercises LegalAcceptanceGate against the
 *                            server-owned legal-acceptance HTTP contract.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG: v1.7.1 certifies the DOM-compatible scrollTop/scrollLeft reset
 *            used by focus-mode record navigation without requiring scrollTo.
 *            v1.7.0 certified that focus-mode navigation resets the bounded
 *            document reading surface to top for each newly focused server
 *            record without posting or changing legal authority.
 *            v1.6.0 certifies server-confirmed focus feedback, explicit
 *            next-unresolved navigation, refresh-failure lockout, and
 *            server-derived progress after recording.
 *            v1.5.1 certifies center-aligned server-issued document prose.
 *            v1.5.0 certifies the centred md-breakpoint reader/dock grid,
 *            bounded mobile dock, compact OS chrome, non-card rail spine,
 *            and persistent bottom status bar.
 *            v1.3.0 certified the interaction shell.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic server-plan evidence only; the
 *                             certificate never persists credentials, secrets,
 *                             acceptance truth, or financial state.
 * AUTHORITY BOUNDARY: Presentation and transport evidence only; Python EOS
 *                     owns legal truth and workspace release.
 * TENANT BOUNDARY: Tenant identity is rendered only from the server plan.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */
import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import LegalAcceptanceGate from '../../../src/components/auth/LegalAcceptanceGate.jsx';
import api from '../../../src/services/api';

vi.mock('../../../src/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

const digest = 'a'.repeat(128);
const requiredPlan = {
  status: 'USER_TERMS_REQUIRED',
  tenantId: 'WILSYTENANT-4CD2FZ4O',
  documents: [
    {
      agreementType: 'INSTITUTIONAL_CHARTER', documentId: 'charter-v1', version: '1.0.0-APPROVED',
      sha3_512: digest, title: 'WILSY OS Institutional Charter', locale: 'en-ZA',
      effectiveFrom: '2026-09-19T00:00:00Z', content: 'The full institutional charter text remains server-issued.', accepted: false,
    },
    {
      agreementType: 'USER_TERMS', documentId: 'terms-v1', version: '1.1.0-APPROVED',
      sha3_512: 'b'.repeat(128), title: 'WILSY OS User Terms', locale: 'en-ZA',
      effectiveFrom: '2026-09-19T00:00:00Z', content: 'The full user terms remain server-issued and accessible.', accepted: false,
    },
  ],
};
const acceptedPlan = { ...requiredPlan, documents: requiredPlan.documents.map((document, index) => ({ ...document, accepted: index === 0 })) };

describe('LegalAcceptanceGate institutional interaction shell', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.post.mockResolvedValue({ data: { status: 'RECORDED' } });
  });
  afterEach(() => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 1024 });
  });

  const renderRequired = async (plan = requiredPlan) => {
    api.get.mockResolvedValue({ data: plan });
    render(<LegalAcceptanceGate />);
    await screen.findByRole('heading', { name: /document ledger/i });
  };

  it('renders a compact ledger, control strip, rail, and selected-record inspector', async () => {
    await renderRequired();
    expect(screen.getByTestId('control-strip')).toBeInTheDocument();
    expect(screen.getByRole('table', { name: /required legal document records/i })).toBeInTheDocument();
    expect(screen.getByRole('complementary', { name: /selected legal record/i })).toBeInTheDocument();
    expect(screen.getByTestId('system-rail')).toHaveClass('w-[220px]');
    expect(screen.getByRole('row', { name: /WILSY OS Institutional Charter/i })).toHaveAttribute('aria-selected', 'true');
  });

  it('collapses and restores the desktop system rail', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /collapse system rail/i }));
    expect(screen.getByTestId('system-rail')).toHaveClass('w-[54px]');
    fireEvent.click(screen.getByRole('button', { name: /open system rail/i }));
    expect(screen.getByTestId('system-rail')).toHaveClass('w-[220px]');
  });

  it('opens and closes a recoverable mobile rail overlay', async () => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 375 });
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /open system rail/i }));
    expect(screen.getByTestId('mobile-system-rail')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /close system rail/i }));
    expect(screen.queryByTestId('mobile-system-rail')).not.toBeInTheDocument();
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 1024 });
  });

  it('has no bulk evidence action', async () => {
    await renderRequired();
    expect(screen.queryByRole('button', { name: /accept all|record all|continue all/i })).not.toBeInTheDocument();
  });

  it('opens the selected server record through Review document', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    expect(screen.getByTestId('document-focus-mode')).toBeInTheDocument();
    expect(screen.queryByRole('table', { name: /required legal document records/i })).not.toBeInTheDocument();
    expect(screen.getByTestId('legal-document-content')).toHaveTextContent(/full institutional charter text remains server-issued/i);
    expect(screen.getByTestId('system-rail')).toHaveClass('w-[54px]');
  });

  it('allows the rail to reopen while focus mode is active', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByRole('button', { name: /open system rail/i }));
    expect(screen.getByTestId('system-rail')).toHaveClass('w-[220px]');
  });

  it('has a persistent command deck and bounded reading surface in focus mode', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    expect(screen.getByRole('complementary', { name: /document command deck/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/document reading surface/i)).toBeInTheDocument();
    expect(screen.getByTestId('legal-document-content')).toHaveAttribute('tabindex', '0');
    expect(screen.getByRole('contentinfo')).toHaveTextContent('PYTHON EOS');
    expect(screen.getByRole('contentinfo')).toHaveTextContent('WORKSPACE SEALED');
    expect(screen.getByTestId('document-command-deck')).toHaveClass('md:border-l');
  });

  it('keeps the reader primary with an 860px column and no command card below it', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    const workspace = screen.getByTestId('focus-workspace-grid');
    expect(workspace).toHaveClass('max-w-[1280px]', 'md:grid-cols-[minmax(0,880px)_280px]', 'md:gap-6');
    const reader = screen.getByLabelText(/document reading surface/i);
    expect(reader).toHaveClass('overflow-y-auto');
    expect(screen.getByTestId('legal-document-content')).toHaveClass('text-center', 'text-base', 'leading-[1.75]');
    expect(screen.getByTestId('document-command-deck')).toHaveClass('md:border-l');
    expect(screen.getByTestId('document-command-deck')).toHaveClass('max-h-[42dvh]', 'overflow-y-auto');
    expect(screen.getByTestId('document-command-deck')).not.toHaveClass('bg-[#0a0c0b]');
  });

  it('uses acknowledgement semantics for the institutional charter', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    expect(screen.getByRole('button', { name: /record acknowledgement/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /record acceptance/i })).not.toBeInTheDocument();
  });

  it('uses acceptance semantics for non-charter records', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('row', { name: /WILSY OS User Terms/i }));
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    expect(screen.getByRole('button', { name: /record acceptance/i })).toBeInTheDocument();
  });

  it('keeps navigation read-only and does not POST on next or previous', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByRole('button', { name: /next record/i }));
    fireEvent.click(screen.getByRole('button', { name: /previous record/i }));
    expect(screen.getAllByRole('heading', { name: 'WILSY OS Institutional Charter' }).length).toBeGreaterThan(0);
    expect(api.post).not.toHaveBeenCalled();
  });

  it('resets the bounded reader to the top whenever focus moves to another record', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));

    const reader = screen.getByLabelText(/document reading surface/i);
    reader.scrollTop = 9999;
    reader.scrollLeft = 37;

    fireEvent.click(screen.getByRole('button', { name: /next record/i }));

    await waitFor(() => {
      expect(reader.scrollTop).toBe(0);
      expect(reader.scrollLeft).toBe(0);
    });
    expect(screen.getAllByRole('heading', { name: 'WILSY OS User Terms' }).length).toBeGreaterThan(0);
    expect(api.post).not.toHaveBeenCalled();
  });

  it('sends one exact server-identity POST only for the explicit action', async () => {
    api.get.mockResolvedValueOnce({ data: requiredPlan }).mockResolvedValueOnce({ data: acceptedPlan });
    render(<LegalAcceptanceGate />);
    fireEvent.click(await screen.findByRole('button', { name: /review document/i }));
    fireEvent.scroll(screen.getByLabelText(/document reading surface/i), { target: { scrollTop: 9999 } });
    expect(api.post).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: /record acknowledgement/i }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(api.post).toHaveBeenCalledWith('/legal-acceptance/accept', {
      document_id: 'charter-v1', document_version: '1.0.0-APPROVED', document_sha3_512: digest,
      acceptance_method: 'ACKNOWLEDGEMENT', locale: 'en-ZA',
    }, { headers: { 'Idempotency-Key': expect.any(String) } });
  });

  it('does not optimistically mark a record before server confirmation', async () => {
    let resolvePost;
    api.get.mockResolvedValue({ data: requiredPlan });
    api.post.mockReturnValue(new Promise((resolve) => { resolvePost = resolve; }));
    render(<LegalAcceptanceGate />);
    fireEvent.click(await screen.findByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByRole('button', { name: /record acknowledgement/i }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(screen.queryByTestId('evidence-recorded')).not.toBeInTheDocument();
    await act(async () => { resolvePost({ data: { status: 'RECORDED' } }); });
  });

  it('keeps the recorded document focused until explicit next navigation', async () => {
    const refreshed = { ...requiredPlan, documents: requiredPlan.documents.map((document, index) => ({ ...document, accepted: index === 0 })) };
    api.get.mockResolvedValueOnce({ data: requiredPlan }).mockResolvedValueOnce({ data: refreshed });
    render(<LegalAcceptanceGate />);
    fireEvent.click(await screen.findByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByRole('button', { name: /record acknowledgement/i }));
    await waitFor(() => expect(screen.getByTestId('evidence-recorded')).toHaveTextContent(/Acknowledgement recorded/i));
    expect(screen.getByTestId('evidence-recorded')).toHaveTextContent(/Server confirmed/i);
    expect(screen.getAllByRole('heading', { name: 'WILSY OS Institutional Charter' }).length).toBeGreaterThan(0);
    expect(screen.queryByRole('heading', { name: 'WILSY OS User Terms' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /record acknowledgement/i })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /next unresolved record/i })).toBeInTheDocument();
    expect(screen.getByRole('contentinfo')).toHaveTextContent('1/2');
    expect(api.get).toHaveBeenCalledTimes(2);
  });

  it('navigates to the next unresolved record without posting again', async () => {
    const refreshed = { ...requiredPlan, documents: requiredPlan.documents.map((document, index) => ({ ...document, accepted: index === 0 })) };
    api.get.mockResolvedValueOnce({ data: requiredPlan }).mockResolvedValueOnce({ data: refreshed });
    render(<LegalAcceptanceGate />);
    fireEvent.click(await screen.findByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByRole('button', { name: /record acknowledgement/i }));
    await screen.findByTestId('evidence-recorded');
    fireEvent.click(screen.getByRole('button', { name: /next unresolved record/i }));
    expect((await screen.findAllByRole('heading', { name: 'WILSY OS User Terms' })).length).toBeGreaterThan(0);
    expect(api.post).toHaveBeenCalledTimes(1);
  });

  it('does not claim recording when post succeeds but refreshed status is not accepted', async () => {
    api.get.mockResolvedValueOnce({ data: requiredPlan }).mockResolvedValueOnce({ data: requiredPlan });
    render(<LegalAcceptanceGate />);
    fireEvent.click(await screen.findByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByRole('button', { name: /record acknowledgement/i }));
    expect(await screen.findByTestId('evidence-confirmation-pending')).toHaveTextContent(/server confirmation pending/i);
    expect(screen.queryByTestId('evidence-recorded')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /record acknowledgement/i })).not.toBeInTheDocument();
    expect(screen.getAllByRole('heading', { name: 'WILSY OS Institutional Charter' }).length).toBeGreaterThan(0);
  });

  it('keeps focus and blocks repeat mutation when confirmation refresh is unavailable', async () => {
    api.get.mockResolvedValueOnce({ data: requiredPlan }).mockRejectedValueOnce({ response: { status: 503, data: { detail: 'LEGAL_ACCEPTANCE_STATUS_UNAVAILABLE' } } });
    render(<LegalAcceptanceGate />);
    fireEvent.click(await screen.findByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByRole('button', { name: /record acknowledgement/i }));
    expect(await screen.findByTestId('evidence-confirmation-pending')).toHaveTextContent(/confirmation refresh unavailable/i);
    expect(screen.queryByRole('button', { name: /record acknowledgement/i })).not.toBeInTheDocument();
    expect(screen.getAllByRole('heading', { name: 'WILSY OS Institutional Charter' }).length).toBeGreaterThan(0);
    expect(screen.getByRole('alert')).toHaveTextContent('HTTP 503');
    expect(api.post).toHaveBeenCalledTimes(1);
  });

  it('keeps the current record focused when the acceptance POST fails', async () => {
    api.get.mockResolvedValue({ data: requiredPlan });
    api.post.mockRejectedValueOnce({ response: { status: 409, data: { detail: 'LEGAL_ACCEPTANCE_REJECTED' } } });
    render(<LegalAcceptanceGate />);
    fireEvent.click(await screen.findByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByRole('button', { name: /record acknowledgement/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent('LEGAL_ACCEPTANCE_REJECTED');
    expect(screen.getAllByRole('heading', { name: 'WILSY OS Institutional Charter' }).length).toBeGreaterThan(0);
    expect(screen.queryByRole('heading', { name: 'WILSY OS User Terms' })).not.toBeInTheDocument();
  });

  it('renders a server-recorded state without inventing progress authority', async () => {
    await renderRequired(acceptedPlan);
    expect(screen.getByRole('row', { name: /WILSY OS Institutional Charter/i })).toHaveTextContent('RECORDED');
    fireEvent.click(screen.getByRole('row', { name: /WILSY OS Institutional Charter/i }));
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    expect(screen.getByTestId('evidence-recorded')).toHaveTextContent(/Acknowledgement recorded/i);
    expect(screen.getByTestId('evidence-recorded')).toHaveTextContent(/Server confirmed/i);
  });

  it('blocks the known stale Charter before any POST', async () => {
    const integrityPlan = { ...requiredPlan, documents: requiredPlan.documents.map((document, index) => index === 0 ? { ...document, content: 'DRAFT_REVIEW_REQUIRED — this record has not been approved.' } : document) };
    await renderRequired(integrityPlan);
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    expect(screen.getByText(/integrity review required/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /record acknowledgement/i })).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('permits a clean Charter acknowledgement when its server status is valid', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    expect(screen.getByRole('button', { name: /record acknowledgement/i })).toBeInTheDocument();
  });

  it('returns to control mode with Escape and the selected row preserved', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(screen.getByRole('table', { name: /required legal document records/i })).toBeInTheDocument();
    expect(screen.getByRole('row', { name: /WILSY OS Institutional Charter/i })).toHaveAttribute('aria-selected', 'true');
  });

  it('exposes canonical identity and digest without allowing edits', async () => {
    await renderRequired();
    fireEvent.click(screen.getByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByText('Canonical metadata'));
    expect(screen.getByText('DOCUMENT_ID · charter-v1')).toBeInTheDocument();
    expect(screen.getByText(`SHA3-512 · ${digest}`)).toBeInTheDocument();
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  });

  it('keeps an empty required corpus sealed and mutation-free', async () => {
    api.get.mockResolvedValue({ data: { status: 'USER_TERMS_REQUIRED', tenantId: requiredPlan.tenantId, documents: [], missingAgreementTypes: ['INSTITUTIONAL_CHARTER', 'USER_TERMS'] } });
    render(<LegalAcceptanceGate />);
    expect(await screen.findByRole('heading', { name: /required documents are not yet available/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /record acknowledgement|record acceptance|review document/i })).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('reports bounded server detail and HTTP status', async () => {
    api.get.mockRejectedValue({ response: { status: 401, data: { detail: 'LEGAL_ACCEPTANCE_STATUS_UNAVAILABLE' } } });
    render(<LegalAcceptanceGate />);
    const alert = (await screen.findAllByRole('alert'))[1];
    expect(alert).toHaveTextContent('LEGAL_ACCEPTANCE_STATUS_UNAVAILABLE');
    expect(alert).toHaveTextContent('HTTP 401');
    expect(alert).not.toHaveTextContent('Request failed with status code');
  });

  it('notifies completion only after the server declares COMPLETE', async () => {
    const onComplete = vi.fn();
    api.get.mockResolvedValue({ data: { status: 'COMPLETE', tenantId: requiredPlan.tenantId, documents: [] } });
    render(<LegalAcceptanceGate onComplete={onComplete} />);
    await waitFor(() => expect(onComplete).toHaveBeenCalledTimes(1));
  });

  it('does not expose signature, execution, settlement, or organisational authority language', async () => {
    await renderRequired();
    expect(screen.queryByText(/signature|execute|settle|accept all|organisational signatory/i)).not.toBeInTheDocument();
  });
});

// ARTIFACT: LegalAcceptanceGate.test.jsx
// VERSION: v1.7.1-DOM-COMPATIBLE-RECORD-SCROLL-RESET-CERT
// AUTHORITY BOUNDARY: deterministic client projection certificate only
// TENANT POSTURE: server-issued plan is displayed; no local legal truth
// FAIL-CLOSED POSTURE: unavailable or incomplete status never opens workspace
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
