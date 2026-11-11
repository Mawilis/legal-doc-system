/**
 * TITLE: WILSY OS Daily Attention Executive Triage Workspace
 * VERSION: v1.3.0-EXECUTIVE-SOURCE-CLARITY
 * AUTHORITY: WILSY OS Core Governance; EOS source services own actions.
 * EPITOME: Replace passive zero tiles with an authenticated, dense, ranked,
 *          keyboard-navigable work queue, briefing, detail rail, calendar and
 *          honest source-specific operating states.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/attention/DailyAttentionWorkspace.jsx
 * COLLABORATION / OWNERSHIP: WilsyDailyAttentionCentre owns current-session
 *          EOS reads/revalidation; attentionFeedClient validates every page;
 *          WilsyWorkDeadlineCalendar reuses the authorised due-work model.
 * CERTIFICATION / UPDATE DATE: 2026-11-11
 * CHANGELOG: v1.3.0-EXECUTIVE-SOURCE-CLARITY adds verified-source
 *          inspection, truthful filtered and per-module empty states, and
 *          source-owned recovery without introducing unsupported commands.
 *          v1.2.0-BOUNDED-ATTENTION-INBOX-WINDOW adds fixed-height
 *          inbox windowing with overscan for loaded source pages and visible
 *          source priority/status labels. Commands remain OPEN-only.
 *          v1.1.1-CALENDAR-INDEPENDENT-AUTHORISED-SCOPE makes Calendar consume
 *          the verified complete My Work snapshot, never only the currently
 *          filtered AttentionItem page.
 *          v1.1.0-RESPONSIVE-CONTEXTUAL-DETAIL-RAIL mounts
 *          a 390px desktop detail rail beside the dense list and a bounded
 *          mobile inspection sheet without hiding source-owned record entry.
 *          v1.0.3-UNIQUE-OPERATIONS-ACTIONS distinguishes
 *          the empty-source creation handoff from the persistent Operations
 *          management shortcut for unambiguous accessible controls.
 *          v1.0.2-ESCAPE-AND-OPERATIONS-ACCESS ensures
 *          calendar-first Escape does not dismiss the parent dialog and
 *          preserves admitted Operations management even with existing work.
 *          v1.0.1-OPERATIONS-ACTION-COMPATIBILITY preserves
 *          the certified source-owned Operations handoff control while
 *          demoting it behind the empty-state explanation.
 *          v1.0.0-DENSE-ATTENTION-REPLACEMENT provides a responsive
 *          Orient/Triage/Open/Source-close-loop interface with 5-item briefing,
 *          compact counts, filtering, selection, detail inspection and scoped
 *          keyboard navigation; unavailable source commands are never faked.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No cached work, storage, unsourced PII, fabricated
 *          status/SLAs, approval controls, or browser-side authority.
 * TENANT BOUNDARY: Receives only validated exact-session EOS AttentionItem feed;
 *          every item is already checked against current tenant and source.
 * AUTHORITY BOUNDARY: OPEN delegates to existing EOS-authorised My Work.
 *          Selection is inspection only, not permission to bulk mutate.
 * TRANSACTION / IDEMPOTENCY BOUNDARY: Presentation only; zero writes, source
 *          services own transactions, replay evidence and audit.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes funds.
 * FAIL-CLOSED POSTURE: Missing source coverage is not interpreted as clear.
 */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle, ArrowRight, CalendarDays, CheckCircle2, ChevronRight,
  CircleHelp, Clock3, ExternalLink, FilterX, ListTodo, RefreshCw, Search,
  ShieldCheck, X,
} from 'lucide-react';
import WilsyWorkDeadlineCalendar from '../chrome/WilsyWorkDeadlineCalendar.jsx';

const FILTERS = [
  ['ALL', 'All work', 'active'],
  ['OVERDUE', 'Overdue', 'overdue'],
  ['TODAY', 'Due today', 'dueToday'],
  ['HIGH', 'High priority', 'highPriority'],
];
const ATTENTION_ROW_HEIGHT = 68;
const ATTENTION_ROW_OVERSCAN = 10;
const DEFAULT_VIEWPORT_HEIGHT = 560;
const label = (source) => ({
  LEGAL: 'Legal', OPERATIONS: 'Operations', INTELLIGENCE: 'Intelligence',
  CRM: 'CRM', PEOPLE: 'People', FINANCE: 'Finance',
}[source] || source);
const dueLabel = (value) => value && !Number.isNaN(Date.parse(value))
  ? new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
  : 'No deadline recorded';
const toWorkItem = (item) => ({
  source_key: item.id,
  source: item.sourceModule,
  work_item_id: item.sourceRecordId,
  title: item.title,
  description: item.summary,
  priority: item.priority,
  status: item.status,
  due_at: item.dueAt,
  is_overdue: item.isOverdue,
});
const countLabel = (name, count) => name + ': ' + count;
const sourceStatus = (item) => typeof item?.status === 'string'
  && item.status.trim() ? item.status : 'Source status unavailable';

/**
 * @description Authenticated attention presentation over one verified EOS page.
 * @param {Object} props Verified projection, read filters and existing EOS navigation.
 * @returns {JSX.Element} Dense actionable-by-navigation triage interface.
 * @institutional No mutation, replay or financial authority; every OPEN
 *          request delegates to the source-owned My Work route.
 */
export default function DailyAttentionWorkspace({
  feed, calendarItems, filter, setFilter, source, setSource, query, setQuery,
  onRefresh, onOpenWork, onOpenOperations, onOpenWorkforce,
  onLoadMore, loadingMore, pageError,
}) {
  const [mode, setMode] = useState('WORK');
  const [selectedId, setSelectedId] = useState(null);
  const [showBriefing, setShowBriefing] = useState(true);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showSourceDetails, setShowSourceDetails] = useState(false);
  const [selectionIndex, setSelectionIndex] = useState(0);
  const [scrollTop, setScrollTop] = useState(0);
  const [viewportHeight, setViewportHeight] = useState(DEFAULT_VIEWPORT_HEIGHT);
  const searchRef = useRef(null);
  const listRef = useRef(null);
  const inboxRef = useRef(null);
  const page = feed.items;
  const inboxOffset = inboxRef.current?.offsetTop || 0;
  const firstVisibleIndex = Math.floor(Math.max(0, scrollTop - inboxOffset)
    / ATTENTION_ROW_HEIGHT);
  const windowStart = Math.max(0, firstVisibleIndex - ATTENTION_ROW_OVERSCAN);
  const windowSize = Math.ceil(viewportHeight / ATTENTION_ROW_HEIGHT)
    + ATTENTION_ROW_OVERSCAN * 2;
  const windowEnd = Math.min(page.length, windowStart + windowSize);
  const visibleItems = page.slice(windowStart, windowEnd).map((item, offset) => ({
    item, index: windowStart + offset,
  }));
  const rows = useMemo(() => Array.isArray(calendarItems)
    ? calendarItems : page.map(toWorkItem), [calendarItems, page]);
  const selected = page.find((item) => item.id === selectedId) || null;
  const ranked = page.slice(0, 5);
  const sourceCoverage = feed.sources || [];
  const missing = feed.coverage.notRepresentedSources || [];
  const allEmpty = feed.counts.active === 0 && !feed.nextCursor;
  const filterEmpty = !page.length && hasFiltered;
  const singleSource = source !== 'ALL' ? sourceCoverage.find((entry) => entry.moduleId === source) : null;
  const hasFiltered = filter !== 'ALL' || source !== 'ALL' || query.trim().length > 0;

  useEffect(() => {
    setSelectionIndex(0);
    setSelectedId(null);
    if (listRef.current) listRef.current.scrollTop = 0;
    setScrollTop(0);
  }, [filter, source, query]);

  useEffect(() => {
    const node = listRef.current;
    if (!node || mode !== 'WORK') return undefined;
    const measure = () => setViewportHeight(
      node.clientHeight || DEFAULT_VIEWPORT_HEIGHT,
    );
    measure();
    const observer = typeof ResizeObserver === 'function'
      ? new ResizeObserver(measure) : null;
    observer?.observe(node);
    window.addEventListener('resize', measure);
    return () => {
      observer?.disconnect();
      window.removeEventListener('resize', measure);
    };
  }, [mode, page.length]);
  useEffect(() => {
    if (selectedId && !page.some((item) => item.id === selectedId)) setSelectedId(null);
  }, [page, selectedId]);

  const open = (item) => {
    if (!item) return;
    onOpenWork?.(toWorkItem(item));
  };

  // Scoped shortcuts: never hijack a text field, modal, or other workspace.
  const handleKey = (event) => {
    const target = event.target;
    if (event.altKey || event.metaKey || event.ctrlKey
      || /^(INPUT|TEXTAREA|SELECT)$/.test(target?.tagName || '')
      || target?.isContentEditable) return;
    if (event.key === 'Escape') {
      if (showShortcuts || mode === 'CALENDAR' || selectedId) {
        event.preventDefault();
        event.stopPropagation();
        if (showShortcuts) setShowShortcuts(false);
        else if (mode === 'CALENDAR') setMode('WORK');
        else setSelectedId(null);
      }
      return;
    }
    if (event.key === '?') {
      event.preventDefault();
      setShowShortcuts((value) => !value);
      return;
    }
    if (event.key === '/') {
      event.preventDefault();
      searchRef.current?.focus();
      return;
    }
    if (event.key >= '1' && event.key <= '4') {
      event.preventDefault();
      setFilter(FILTERS[Number(event.key) - 1][0]);
      return;
    }
    if (mode !== 'WORK' || page.length === 0) return;
    if (event.key === 'j' || event.key === 'k') {
      event.preventDefault();
      const next = Math.max(0, Math.min(page.length - 1,
        selectionIndex + (event.key === 'j' ? 1 : -1)));
      setSelectionIndex(next);
      setSelectedId(page[next].id);
      listRef.current?.scrollTo?.({
        top: (inboxRef.current?.offsetTop || 0) + next * ATTENTION_ROW_HEIGHT,
        behavior: 'auto',
      });
    } else if (event.key === 'Enter' && selected) {
      event.preventDefault();
      open(selected);
    } else if (event.key === 'o' && selected) {
      event.preventDefault();
      open(selected);
    }
  };
  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden text-slate-100"
      data-attention-production-ui="true" onKeyDown={handleKey}>
      <div className="shrink-0 border-b border-white/10 px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div role="tablist" aria-label="Daily attention views"
            className="flex items-center gap-1 rounded-xl bg-[#0a1628] p-1">
            <button type="button" role="tab" aria-selected={mode === 'WORK'}
              onClick={() => setMode('WORK')}
              className={'rounded-lg px-3 py-2 text-xs font-semibold ' +
                (mode === 'WORK' ? 'bg-amber-300 text-slate-950' : 'text-slate-300 hover:bg-white/10')}>
              <ListTodo size={14} className="mr-1.5 inline"/>Work list
            </button>
            <button type="button" role="tab" aria-selected={mode === 'CALENDAR'}
              onClick={() => setMode('CALENDAR')}
              className={'rounded-lg px-3 py-2 text-xs font-semibold ' +
                (mode === 'CALENDAR' ? 'bg-amber-300 text-slate-950' : 'text-slate-300 hover:bg-white/10')}>
              <CalendarDays size={14} className="mr-1.5 inline"/>Calendar
            </button>
          </div>
          <div className="flex items-center gap-1.5">
            <button type="button" onClick={() => setShowShortcuts((v) => !v)}
              aria-label="Daily attention keyboard shortcuts" aria-expanded={showShortcuts}
              className="rounded-lg border border-white/10 p-2 text-slate-300 hover:bg-white/10"><CircleHelp size={15}/></button>
            <button type="button" onClick={onRefresh} title={'Last synced: ' + feed.syncedAt}
              className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 px-2.5 py-2 text-xs text-slate-300 hover:bg-white/10">
              <RefreshCw size={14}/>Refresh
            </button>
          </div>
        </div>
        {showShortcuts && (
          <div role="note" className="mt-2 rounded-lg border border-amber-300/20 bg-[#0a1628] p-2 text-xs leading-5 text-slate-300">
            <strong className="text-amber-100">Shortcuts:</strong> j/k select work · Enter/o open
            · / search · 1–4 filters · Esc clear detail · ? toggle help.
            Completion, assignment and snooze shortcuts become available only
            when their source-owned action APIs are certified.
          </div>
        )}
        <div className="mt-3 flex flex-wrap gap-1.5" aria-label="Verified current-source workload">
          {[
            ['Active', feed.counts.active, 'ALL'],
            ['Overdue', feed.counts.overdue, 'OVERDUE'],
            ['Due today', feed.counts.dueToday, 'TODAY'],
            ['High priority', feed.counts.highPriority, 'HIGH'],
          ].map(([name, count, target]) => (
            <button key={name} type="button" onClick={() => setFilter(target)}
              aria-label={countLabel(name, count)}
              aria-pressed={filter === target}
              className={'flex items-center gap-2 rounded-lg border px-3 py-2 text-xs transition-colors ' +
                (filter === target ? 'border-amber-300/70 bg-amber-300/10' : 'border-white/10 bg-white/[0.025]') +
                (name === 'Overdue' && count > 0 ? ' text-rose-200' : ' text-slate-200')}>
              <span className="text-slate-400">{name}</span>
              <strong className="font-semibold tabular-nums">{count}</strong>
            </button>
          ))}
        </div>
        <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-[11px]">
          <button type="button" onClick={() => setShowSourceDetails((value) => !value)}
            aria-expanded={showSourceDetails} aria-controls="attention-source-evidence"
            className="inline-flex items-center gap-1.5 rounded-md text-emerald-200 hover:text-emerald-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
            <ShieldCheck size={13}/> Verified from {sourceCoverage.length} admitted {sourceCoverage.length === 1 ? 'source' : 'sources'}
            <ChevronRight size={12} className={showSourceDetails ? 'rotate-90' : ''}/>
          </button>
          <span className="text-slate-400" title={feed.syncedAt}>
            Synced {new Date(feed.syncedAt).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
          </span>
        </div>
        {showSourceDetails && (
          <section id="attention-source-evidence" aria-label="Verified attention source details"
            className="mt-2 rounded-lg border border-white/10 bg-[#0a1628] px-3 py-2 text-[11px] leading-5">
            <p className="font-semibold text-slate-200">Source verification for this session</p>
            {sourceCoverage.length === 0 && <p className="text-amber-200">No source has returned an admitted work projection.</p>}
            {sourceCoverage.map((entry) => (
              <div key={entry.moduleId} className="flex items-center justify-between gap-2 border-b border-white/5 py-1 last:border-0">
                <span>{label(entry.moduleId)}</span>
                <span className={entry.state === 'empty' ? 'text-slate-400' : 'text-emerald-200'}>
                  {entry.state === 'empty' ? 'Verified · empty' : 'Verified · active'} · {entry.count} items
                </span>
              </div>
            ))}
            {missing.length > 0 && <p className="mt-2 text-amber-100/80">
              Not verified in this session: {missing.map(label).join(', ')}.
              Absence does not establish lack of entitlement, an outage or a cleared queue.
            </p>}
            <button type="button" onClick={onRefresh}
              className="mt-2 rounded-md border border-white/15 px-2.5 py-1 text-amber-100 hover:bg-white/5">
              Recheck authorised sources
            </button>
          </section>
        )}
        {missing.length > 0 && (
          <p className="mt-1 text-[11px] leading-4 text-amber-100/75">
            Not represented in this session: {missing.map(label).join(', ')}.
            No module access or cleared status is inferred.
          </p>
        )}
        {mode === 'WORK' && (
          <>
            <div role="group" aria-label="Filter daily attention"
              className="mt-3 flex flex-wrap gap-1.5">
              {FILTERS.map(([id, name]) => (
                <button key={id} type="button" aria-pressed={filter === id}
                  onClick={() => setFilter(id)}
                  className={'rounded-full border px-2.5 py-1.5 text-[11px] ' +
                    (filter === id ? 'border-amber-300/50 bg-amber-300/15 text-amber-100'
                      : 'border-white/15 text-slate-300 hover:bg-white/5')}>{name}</button>
              ))}
            </div>
            <div className="mt-2 flex min-w-0 gap-2">
              <label className="flex min-w-0 flex-1 items-center gap-2 rounded-lg border border-white/15 bg-[#0a1628] px-3">
                <Search size={15} className="text-slate-400"/>
                <input ref={searchRef} type="search" aria-label="Search authorised work"
                  placeholder="Search title, record, source…" value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  className="h-9 min-w-0 flex-1 bg-transparent text-xs outline-none placeholder:text-slate-500"/>
              </label>
              <select aria-label="Filter work by source" value={source}
                onChange={(event) => setSource(event.target.value)}
                className="max-w-[38%] rounded-lg border border-white/15 bg-[#0a1628] px-2 text-xs">
                <option value="ALL">All included sources</option>
                {sourceCoverage.map((entry) => (
                  <option key={entry.moduleId} value={entry.moduleId}>{label(entry.moduleId)}</option>
                ))}
              </select>
            </div>
          </>
        )}
      </div>
      {mode === 'CALENDAR' ? (
        <div className="min-h-0 flex-1 overflow-auto px-3 py-3">
          <WilsyWorkDeadlineCalendar items={rows} onOpenWork={onOpenWork}
            onOpenWorkforce={onOpenWorkforce}/>
          <button type="button" onClick={() => setMode('WORK')}
            aria-label="Close calendar and return to work list"
            className="mt-2 rounded-lg border border-amber-300/30 px-3 py-2 text-xs text-amber-100">
            Return to work list
          </button>
        </div>
      ) : (
        <div className="relative flex min-h-0 flex-1 overflow-hidden">
          <div className="relative min-h-0 flex-1 overflow-y-auto" ref={listRef}
            data-attention-scroll-container="true"
            onScroll={(event) => setScrollTop(event.currentTarget.scrollTop)}>
          {ranked.length > 0 && showBriefing && filter === 'ALL' && !query.trim() && source === 'ALL' && (
            <section aria-label="Today's attention briefing" className="border-b border-white/10 bg-amber-300/[0.035] px-4 py-3">
              <div className="mb-2 flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider text-amber-200">Start here</h3>
                <button type="button" onClick={() => setShowBriefing(false)}
                  className="text-[11px] text-slate-400 hover:text-white">Collapse briefing</button>
              </div>
              <div className="space-y-1">
                {ranked.map((item, index) => (
                  <button key={item.id} type="button" onClick={() => {
                    setSelectedId(item.id); setSelectionIndex(page.findIndex((x) => x.id === item.id));
                  }} className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-xs hover:bg-white/5">
                    <span className="w-4 text-amber-300">{index + 1}</span>
                    <span className="min-w-0 flex-1 truncate font-medium">{item.title}</span>
                    <span className="shrink-0 text-[10px] text-slate-400">{label(item.sourceModule)}</span>
                    <ChevronRight size={13}/>
                  </button>
                ))}
              </div>
            </section>
          )}
          {!showBriefing && page.length > 0 && (
            <button type="button" onClick={() => setShowBriefing(true)}
              className="m-3 text-xs text-amber-200">Show ranked briefing</button>
          )}
          {!page.length && (
            <section aria-label="Attention empty state" className="px-6 py-8">
              {filterEmpty ? (
                <>
                  <FilterX size={23} className="text-slate-400"/>
                  <h3 className="mt-2 text-base font-semibold">No matches in this view</h3>
                  <p className="mt-2 text-xs leading-5 text-slate-400">
                    No work matched your current search, source and priority filters.
                    {feed.counts.active > 0
                      ? ` ${feed.counts.active} active items exist in the verified source scope.`
                      : ' The admitted source scope currently reports no active work.'}
                  </p>
                  {hasFiltered && <button type="button" onClick={() => {
                    setFilter('ALL'); setSource('ALL'); setQuery('');
                  }} className="mt-4 rounded-lg bg-amber-300 px-3 py-2 text-xs font-semibold text-slate-950">Clear filters</button>}
                </>
              ) : sourceCoverage.length === 0 ? (
                <>
                  <AlertTriangle size={23} className="text-amber-200"/>
                  <h3 className="mt-2 text-base font-semibold">No authorised attention sources</h3>
                  <p className="mt-2 text-xs leading-5 text-slate-400">
                    Your current session has no verified admitted work sources.
                    Contact your tenant administrator to review your membership,
                    role and module access. No empty-business claim is made.
                  </p>
                </>
              ) : (
                <>
                  <CheckCircle2 size={23} className="text-emerald-300"/>
                  <h3 className="mt-2 text-base font-semibold">
                    {singleSource ? `No active ${label(singleSource.moduleId)} work` : 'No active work in verified sources'}
                  </h3>
                  <p className="mt-2 text-xs leading-5 text-slate-400">
                    {singleSource
                      ? `${label(singleSource.moduleId)} returned an empty active queue.`
                      : `${sourceCoverage.map((entry) => label(entry.moduleId)).join(', ')} returned an empty active queue.`}
                    {missing.length > 0
                      ? ` ${missing.map(label).join(', ')} ${missing.length === 1 ? 'was' : 'were'} not verified for this session.`
                      : ' Every admitted source currently reports no active work.'}
                    {' '}No next SLA or completed-work count is available from this feed.
                  </p>
                  {sourceCoverage.some((entry) => entry.moduleId === 'OPERATIONS') && onOpenOperations && (
                    <button type="button" onClick={onOpenOperations}
                      className="mt-4 rounded-lg border border-amber-300/50 px-3 py-2 text-xs font-semibold text-amber-100">
                      Create Operations work <ArrowRight size={13} className="ml-1 inline"/>
                    </button>
                  )}
                </>
              )}
            </section>
          )}
          {page.length > 0 && (
            <section aria-label="Attention inbox">
              <div ref={inboxRef} role="list" data-attention-inbox-window="true"
                style={{height: page.length * ATTENTION_ROW_HEIGHT, position: 'relative'}}>
                {visibleItems.map(({item, index}) => (
                  <article key={item.id} role="listitem" data-attention-row
                    aria-setsize={page.length} aria-posinset={index + 1}
                    style={{position: 'absolute', top: index * ATTENTION_ROW_HEIGHT,
                      left: 0, right: 0, height: ATTENTION_ROW_HEIGHT}}
                    className={'box-border flex items-center gap-2 border-b border-white/[0.07] border-l-[3px] px-3 py-1.5 transition-colors ' +
                      (selectedId === item.id ? 'border-l-amber-300 bg-amber-300/[0.07]'
                        : item.isOverdue ? 'border-l-rose-400/70 hover:bg-white/[0.04]'
                          : 'border-l-transparent hover:bg-white/[0.04]')}>
                    <button type="button" aria-label={'Inspect ' + item.title}
                      aria-pressed={selectedId === item.id}
                      onClick={() => { setSelectedId(item.id); setSelectionIndex(index); }}
                      className="min-w-0 flex-1 text-left focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
                      <span className="block truncate text-xs font-semibold text-white">{item.title}</span>
                      <span className="mt-0.5 block truncate text-[10px] text-slate-400">
                        {label(item.sourceModule)} · {item.sourceRecordId} · {item.priority} · {sourceStatus(item)}
                      </span>
                      <span className={'mt-0.5 block truncate text-[10px] ' +
                        (item.isOverdue ? 'text-rose-200' : 'text-amber-100/70')}>
                        {dueLabel(item.dueAt)} · {item.isOverdue ? 'Overdue · ' : ''}{item.whyRanked}
                      </span>
                    </button>
                    <button type="button" aria-label={'Act on ' + item.title + ' in My Work'}
                      onClick={() => open(item)}
                      className="shrink-0 rounded-lg border border-amber-300/35 px-2.5 py-1.5 text-[11px] font-semibold text-amber-100 hover:bg-amber-300/10">
                      Open <ArrowRight size={13} className="ml-1 inline"/>
                    </button>
                  </article>
                ))}
              </div>
            </section>
          )}
          {feed.nextCursor && (
            <button type="button" onClick={onLoadMore} disabled={loadingMore}
              className="m-3 w-[calc(100%-1.5rem)] rounded-lg border border-white/20 px-3 py-2 text-xs text-amber-100 disabled:opacity-50">
              {loadingMore ? 'Loading verified work…' : 'Load more work'}
            </button>
          )}
          {pageError && <p role="alert" className="px-4 py-2 text-xs text-rose-200">
            Page verification failed. Refresh to reload EOS source truth.</p>}
          </div>
          {selected && (
            <aside aria-label="Attention detail rail"
              className="absolute inset-x-0 bottom-0 z-10 max-h-[75%] shrink-0 overflow-auto border-t border-amber-300/25 bg-[#182842] px-4 py-3 shadow-2xl md:static md:inset-auto md:w-[390px] md:max-h-full md:border-l md:border-t-0 md:shadow-none">
          <div className="flex items-center justify-between gap-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-200">
              Work detail · {label(selected.sourceModule)}
            </h3>
            <button type="button" onClick={() => setSelectedId(null)}
              aria-label="Close attention detail" className="rounded-lg p-1 text-slate-300 hover:bg-white/10">
              <X size={16}/>
            </button>
          </div>
          <p className="mt-2 text-sm font-semibold">{selected.title}</p>
          {selected.summary && <p className="mt-1 text-xs leading-5 text-slate-300">{selected.summary}</p>}
          <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
            <div><dt className="text-slate-400">Reason prioritised</dt><dd>{selected.whyRanked}</dd></div>
            <div><dt className="text-slate-400">Priority score</dt><dd>{selected.urgencyScore}/100</dd></div>
            <div><dt className="text-slate-400">Deadline</dt><dd>{dueLabel(selected.dueAt)}</dd></div>
            <div><dt className="text-slate-400">Source status</dt><dd>{sourceStatus(selected)}</dd></div>
            <div><dt className="text-slate-400">SLA</dt><dd>{selected.slaBreachAt ? dueLabel(selected.slaBreachAt) : 'Not supplied by source'}</dd></div>
            <div><dt className="text-slate-400">Record</dt><dd className="break-all">{selected.sourceRecordId}</dd></div>
          </dl>
          <div className="mt-3 flex items-center justify-between gap-2 border-t border-white/10 pt-3">
            <p className="text-[10px] text-slate-400">Only source-owned actions are authorised.</p>
            <button type="button" onClick={() => open(selected)}
              className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-amber-300 px-3 py-2 text-xs font-bold text-slate-950">
              Open full record <ExternalLink size={13}/>
            </button>
          </div>
            </aside>
          )}
        </div>
      )}
      <footer className="shrink-0 border-t border-white/10 bg-[#14243d] px-4 py-2.5">
        <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
          <span>{page.length} loaded · {feed.filteredTotal} matching · {feed.counts.active} active</span>
          <div className="flex items-center gap-3">
            {sourceCoverage.some((entry) => entry.moduleId === 'OPERATIONS')
              && onOpenOperations && (
              <button type="button" onClick={onOpenOperations}
                className="inline-flex items-center gap-1 text-xs text-slate-300 hover:text-amber-100">
                Manage Operations
              </button>
            )}
            <button type="button" onClick={() => onOpenWork?.(null)}
              className="inline-flex items-center gap-1 text-amber-200 hover:text-amber-100">
              Open My Work <ArrowRight size={13}/>
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

// ARTIFACT: client/src/components/attention/DailyAttentionWorkspace.jsx
// VERSION: v1.3.0-EXECUTIVE-SOURCE-CLARITY
// AUTHORITY BOUNDARY: Read-only EOS-attested items; OPEN delegates to source.
 // TENANT POSTURE: Exact current-session authorised AttentionItem response.
 // FAIL-CLOSED POSTURE: Unrepresented modules never display verified-cleared.
 // FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 // END OF WILSY OS SOVEREIGN ARTIFACT
