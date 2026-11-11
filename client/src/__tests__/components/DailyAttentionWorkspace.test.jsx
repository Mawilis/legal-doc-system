/**
 * TITLE: WILSY OS Daily Attention Inbox Window Certificate
 * VERSION: v1.6.0-BOUNDED-BULK-EXECUTION-CERT
 * AUTHORITY: Disposable client component test evidence only.
 * EPITOME: Prove the Daily Attention inbox exposes source priority/status and
 *          bounds mounted rows while retaining access to a 500-item snapshot.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/DailyAttentionWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: DailyAttentionWorkspace owns display/windowing;
 *          attentionFeedClient validates exact EOS source identity; source
 *          services continue to own every business transition.
 * CERTIFICATION / UPDATE DATE: 2026-11-11
 * CHANGELOG: v1.6.0-BOUNDED-BULK-EXECUTION-CERT proves
 *          capability-gated selection, source-owned result reconciliation,
 *          and retention of unsuccessful selected work.
 *          v1.5.0-SOURCE-COMPLETION-UI-CERT verifies
 *          capability-gated completion evidence and no uncontrolled mutation.
 *          v1.4.0-EXECUTIVE-TRIAGE-SELECTION-CERT checks
 *          multi-select, inspection handoff and clear controls without
 *          authorising a business mutation.
 *          v1.3.0-SEARCH-FOCUS-CONTINUITY-CERT proves
 *          existing rail selection survives same-page query edits.
 *          v1.2.0-DENSE-WINDOW-GEOMETRY-CERT verifies
 *          scroll access and bounded rendering with 44px executive rows.
 *          v1.1.0-EXECUTIVE-SOURCE-EVIDENCE-CERT verifies
 *          admitted-source evidence expansion and honest partial-scope
 *          empty copy alongside bounded 500-item rendering.
 *          v1.0.0-500-ITEM-BOUNDED-RENDER-CERT proves a bounded DOM row
 *          window, accessible position metadata, priority/status visibility,
 *          and keyboard-independent scroll access to the final loaded row.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic disposable AttentionItems; no tenant
 *          records, credentials, network calls or commands are used.
 * TENANT BOUNDARY: Synthetic items share one fixture tenant and source.
 * AUTHORITY BOUNDARY: OPEN callbacks are inert test spies; no source command.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement evidence.
 */
import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import DailyAttentionWorkspace from '../../components/attention/DailyAttentionWorkspace.jsx';

afterEach(cleanup);

const fixtureFeed = (count) => ({
  schema: 'WILSY-OS-ATTENTION-FEED/V1',
  tenantId: 'WILSY-ATTENTION-TEST-TENANT',
  principalId: 'WILSY-ATTENTION-TEST-PRINCIPAL',
  syncedAt: '2026-11-10T10:00:00+00:00',
  view: 'active',
  items: Array.from({ length: count }, (_, index) => ({
    id: `OPERATIONS:attention-${index}`,
    tenantId: 'WILSY-ATTENTION-TEST-TENANT',
    sourceModule: 'OPERATIONS',
    sourceType: 'TASK',
    sourceRecordId: `attention-${index}`,
    title: `Attention item ${index}`,
    summary: 'Source-owned test record',
    priority: index === 0 ? 'HIGH' : 'NORMAL',
    urgencyScore: index === 0 ? 70 : 10,
    whyRanked: index === 0 ? 'High source priority' : 'Authorised active work',
    dueAt: '2026-11-12T12:00:00+00:00',
    slaBreachAt: null,
    assigneeId: null,
    requesterId: null,
    status: 'OPEN',
    actionHints: ['OPEN'],
    deepLink: '/my-work',
    authzScope: 'SOURCE_SERVICE_ONLY',
    updatedAt: '2026-11-10T09:00:00+00:00',
    isOverdue: false,
  })),
  counts: { active: count, overdue: 0, dueToday: 0, highPriority: 1 },
  sources: [{ moduleId: 'OPERATIONS', state: count ? 'ok' : 'empty', count }],
  coverage: {
    admittedSources: ['OPERATIONS'],
    notRepresentedSources: ['LEGAL', 'INTELLIGENCE', 'CRM', 'FINANCE', 'PEOPLE'],
    completeEnterpriseCoverage: false,
  },
  filteredTotal: count,
  nextCursor: null,
  authority: { commandsOwnedBy: 'SOURCE_SERVICES', attentionCommandsEnabled: false },
});

describe('Daily Attention bounded inbox', () => {
  it('renders a bounded 500-item window and keeps trailing rows reachable', async () => {
    const inert = vi.fn();
    const { container } = render(
      <DailyAttentionWorkspace
        feed={fixtureFeed(500)}
        calendarItems={[]}
        filter="ALL"
        setFilter={inert}
        source="ALL"
        setSource={inert}
        query=""
        setQuery={inert}
        onRefresh={inert}
        onOpenWork={inert}
        onOpenOperations={inert}
        onOpenWorkforce={inert}
        onLoadMore={inert}
        loadingMore={false}
        pageError=""
      />,
    );

    const firstWindow = container.querySelectorAll('[data-attention-row]');
    expect(firstWindow.length).toBeGreaterThan(0);
    expect(firstWindow.length).toBeLessThanOrEqual(32);
    expect(firstWindow[0].getAttribute('aria-setsize')).toBe('500');
    expect(firstWindow[0].getAttribute('aria-posinset')).toBe('1');
    expect(firstWindow[0].textContent).toContain('HIGH');
    expect(firstWindow[0].textContent).toContain('OPEN');

    const scroller = container.querySelector('[data-attention-scroll-container="true"]');
    Object.defineProperty(scroller, 'scrollTop', {
      configurable: true,
      writable: true,
      value: 499 * 44,
    });
    fireEvent.scroll(scroller);

    const finalItem = await screen.findByRole('button', {
      name: 'Inspect Attention item 499',
    });
    expect(finalItem.closest('[data-attention-row]')?.getAttribute('aria-posinset'))
      .toBe('500');
    expect(container.querySelectorAll('[data-attention-row]').length)
      .toBeLessThanOrEqual(32);
  });
  it('lets executives inspect exact admitted-source evidence without claiming platform clearance', () => {
    const inert = vi.fn();
    const feed = fixtureFeed(0);
    render(
      <DailyAttentionWorkspace
        feed={feed}
        calendarItems={[]}
        filter="ALL"
        setFilter={inert}
        source="ALL"
        setSource={inert}
        query=""
        setQuery={inert}
        onRefresh={inert}
        onOpenWork={inert}
        onOpenOperations={inert}
        onWorkforce={inert}
        onLoadMore={inert}
        loadingMore={false}
        pageError=""
      />,
    );

    expect(screen.getByText('No active work in verified sources')).toBeTruthy();
    expect(screen.getByText(/were not verified for this session/)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /Verified from 1 admitted source/ }));
    const evidence = screen.getByRole('region', { name: 'Verified attention source details' });
    expect(evidence.textContent).toContain('Operations');
    expect(evidence.textContent).toContain('Verified · empty');
    expect(evidence.textContent).toContain('Not verified in this session');
    fireEvent.click(screen.getByRole('button', { name: 'Recheck authorised sources' }));
    expect(inert).toHaveBeenCalledTimes(1);
  });

  it('provides accurate no-matches recovery even when active counts are zero', () => {
    const clearFilter = vi.fn();
    const clearSource = vi.fn();
    const clearQuery = vi.fn();
    render(
      <DailyAttentionWorkspace
        feed={fixtureFeed(0)}
        calendarItems={[]}
        filter="HIGH"
        setFilter={clearFilter}
        source="ALL"
        setSource={clearSource}
        query=""
        setQuery={clearQuery}
        onRefresh={vi.fn()}
        onOpenWork={vi.fn()}
        onLoadMore={vi.fn()}
        loadingMore={false}
        pageError=""
      />,
    );
    expect(screen.getByText('No matches in this view')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Clear filters' }));
    expect(clearFilter).toHaveBeenCalledWith('ALL');
    expect(clearSource).toHaveBeenCalledWith('ALL');
    expect(clearQuery).toHaveBeenCalledWith('');
  });

  it('preserves inspected work while search input changes before server revalidation', () => {
    const inert = vi.fn();
    const feed = fixtureFeed(1);
    const build = (query) => (
      <DailyAttentionWorkspace
        feed={feed}
        calendarItems={[]}
        filter="ALL"
        setFilter={inert}
        source="ALL"
        setSource={inert}
        query={query}
        setQuery={inert}
        onRefresh={inert}
        onOpenWork={inert}
        onLoadMore={inert}
        loadingMore={false}
        pageError=""
      />
    );
    const { rerender } = render(build(''));
    fireEvent.click(screen.getByRole('button', { name: 'Inspect Attention item 0' }));
    expect(screen.getByRole('complementary', { name: 'Attention detail rail' })).toBeTruthy();
    rerender(build('attention'));
    expect(screen.getByRole('complementary', { name: 'Attention detail rail' })).toBeTruthy();
  });

  it('selects and inspects multiple verified work rows without inventing a mutation', () => {
    const inert = vi.fn();
    render(
      <DailyAttentionWorkspace
        feed={fixtureFeed(3)}
        calendarItems={[]}
        filter="ALL"
        setFilter={inert}
        source="ALL"
        setSource={inert}
        query=""
        setQuery={inert}
        onRefresh={inert}
        onOpenWork={inert}
        onLoadMore={inert}
        loadingMore={false}
        pageError=""
      />,
    );
    fireEvent.click(screen.getByRole('checkbox', { name: 'Select all loaded work' }));
    expect(screen.getByText('3 selected for triage')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Inspect first selected' }));
    expect(screen.getByRole('complementary', { name: 'Attention detail rail' })).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Clear selection' }));
    expect(screen.queryByText('3 selected for triage')).toBeNull();
    expect(inert).not.toHaveBeenCalled();
  });

  it('exposes source completion only for EOS-admitted commands and submits operator evidence', () => {
    const onComplete = vi.fn();
    const feed = fixtureFeed(1);
    const base = {
      feed, calendarItems: [], filter: 'ALL', setFilter: vi.fn(),
      source: 'ALL', setSource: vi.fn(), query: '', setQuery: vi.fn(),
      onRefresh: vi.fn(), onOpenWork: vi.fn(), onLoadMore: vi.fn(),
      loadingMore: false, pageError: '', onCompleteWork: onComplete,
    };
    const { rerender } = render(<DailyAttentionWorkspace {...base} authorisedActions={{}} />);
    fireEvent.click(screen.getByRole('button', { name: 'Inspect Attention item 0' }));
    expect(screen.queryByRole('button', { name: 'Confirm completion' })).toBeNull();
    rerender(<DailyAttentionWorkspace {...base}
      authorisedActions={{ OPERATIONS: ['COMPLETE'] }} />);
    fireEvent.change(screen.getByPlaceholderText('Record what was completed and the evidence for this decision'), {
      target: { value: 'Verified operational delivery and recorded completion evidence' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm completion' }));
    expect(onComplete).toHaveBeenCalledTimes(1);
    expect(onComplete.mock.calls[0][0].sourceRecordId).toBe('attention-0');
    expect(onComplete.mock.calls[0][1]).toContain('Verified operational delivery');
  });

  it('keeps failed selected work when independently confirmed bulk completions succeed', async () => {
    const onBulkComplete = vi.fn().mockResolvedValue({
      completedIds: ['OPERATIONS:attention-0', 'OPERATIONS:attention-1'],
      failedIds: ['OPERATIONS:attention-2'],
    });
    render(
      <DailyAttentionWorkspace
        feed={fixtureFeed(3)}
        calendarItems={[]}
        filter="ALL"
        setFilter={vi.fn()}
        source="ALL"
        setSource={vi.fn()}
        query=""
        setQuery={vi.fn()}
        onRefresh={vi.fn()}
        onOpenWork={vi.fn()}
        onLoadMore={vi.fn()}
        authorisedActions={{ OPERATIONS: ['COMPLETE'] }}
        onBulkComplete={onBulkComplete}
        loadingMore={false}
        pageError=""
      />,
    );
    fireEvent.click(screen.getByRole('checkbox', { name: 'Select all loaded work' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Bulk completion evidence' }), {
      target: { value: 'All selected operations tasks verified and completed' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Complete up to 3' }));
    await waitFor(() => expect(onBulkComplete).toHaveBeenCalledTimes(1));
    expect(onBulkComplete.mock.calls[0][0]).toHaveLength(3);
    await waitFor(() => expect(screen.getByText('1 selected · 1 permitted to complete')).toBeTruthy());
    expect(screen.getByRole('checkbox', { name: 'Select Attention item 2' }).checked).toBe(true);
  });

});

// ARTIFACT: client/src/__tests__/components/DailyAttentionWorkspace.test.jsx
// VERSION: v1.6.0-BOUNDED-BULK-EXECUTION-CERT
// AUTHORITY BOUNDARY: Client rendering evidence only; no commands or persistence.
// TENANT POSTURE: Synthetic single-tenant source snapshot; no cross-tenant data.
// FAIL-CLOSED POSTURE: Window must expose accurate size and absolute item position.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
