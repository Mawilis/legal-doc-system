/**
 * TITLE: WILSY OS Daily Attention Executive Triage Workspace
 * VERSION: v3.14.0-CRM-DIRECT-SAVED-DRAFT
 * AUTHORITY: WILSY OS Core Governance; EOS source services own actions.
 * EPITOME: Replace passive zero tiles with an authenticated, dense, ranked,
 *          keyboard-navigable work queue, briefing, detail rail, calendar and
 *          honest source-specific operating states.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/attention/DailyAttentionWorkspace.jsx
 * COLLABORATION / OWNERSHIP: WilsyDailyAttentionCentre owns current-session
 *          EOS reads/revalidation; attentionFeedClient validates every page;
 *          WilsyWorkDeadlineCalendar reuses the authorised due-work model.
 * CERTIFICATION / UPDATE DATE: 2026-11-17
 * CHANGELOG: v3.14.0-CRM-DIRECT-SAVED-DRAFT adds an explicit
 *          Save Draft action for CRM source creation, with distinct
 *          same-intent idempotency keys and source-owned persisted status.
 *          Existing Operations/Intelligence create semantics remain OPEN.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No cached work, storage, unsourced PII, fabricated
 *          status/SLAs, approval controls, or browser-side authority.
 * TENANT BOUNDARY: Receives only validated exact-session EOS AttentionItem feed;
 *          every item is already checked against current tenant and source.
 * AUTHORITY BOUNDARY: Row Complete stages the existing evidence form in the
 *          detail rail; source POSTs independently reauthorize. Bulk completion
 *          submits separately per source item and reports partial outcomes.
 * TRANSACTION / IDEMPOTENCY BOUNDARY: Presentation only; zero writes, source
 *          services own transactions, replay evidence and audit.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes funds.
 * FAIL-CLOSED POSTURE: Missing source coverage is not interpreted as clear.
 * CHANGELOG: v3.13.0-SOURCE-IDENTITY-DISCLOSURE removes raw IDs
 *          from the executive detail and limits them to an explicit technical
 *          disclosure, preserving exact source coordinates and honest owner
 *          availability without inventing a human identity.
 *          v3.12.0-RESPONSIVE-OPERATING-WORKSPACE combines the
 *          38/62 independently scrollable desktop work/detail panes with
 *          full-workspace mobile detail and retains functional source triage.
 *          v3.11.0-FUNCTIONAL-TRIAGE-AND-EXPLICIT-SELECTION provides clickable
 *          EOS-backed workload filters, compact absent-source warning,
 *          optional bulk-selection controls and detail-open row density.
 *          v3.10.0-RECEIPT-RECONCILIATION-CONTROL displays an accepted
 *          completion note read-only and offers a readback-only reconciliation
 *          action while EOS receipt verification is pending.
 *          v3.9.0-READBACK-SUCCESS-FEEDBACK announces completion only
 *          after the parent confirms fresh authorized projection removal.
 *          v3.8.0-IN-PANEL-SOURCE-COMPLETION makes an admitted, EOS-
 *          preverified Complete command the primary row action, opens the
 *          existing detail evidence form in-place, focuses required evidence,
 *          and keeps a separate Details action. Unauthorized or unavailable
 *          source actions are omitted; the source controller and EOS receipt
 *          remain authoritative. Existing bounded sequential bulk semantics
 *          remain per-item and partial, never atomic.
 *          v3.7.0-COMPACT-EXECUTION-BAR compresses the list controls into
 *          one primary header, one data-driven summary row, and one toolbar;
 *          removes duplicate filter/severity rows; makes the ranked briefing
 *          opt-in; and adds deterministic local sorting only for fields in
 *          the validated AttentionItem contract. Creation, source commands,
 *          readback, authorization and audit ownership are unchanged.
 *          v3.6.0-CREATE-VALIDATION-AND-ACTION-CLARITY removes
 *          the mode badge that resembled a duplicate Create action, adds
 *          inline title and safe server-field validation, and keeps one submit.
 *          v3.5.1-CREATE-FOCUS-RESTORATION returns focus to the
 *          re-mounted LIST trigger after Cancel or Escape and prevents Escape
 *          from closing an in-flight source command.
 *          v3.5.0-EXCLUSIVE-CREATE-MODE makes LIST and CREATE mutually exclusive,
 *          hides list metrics and controls during creation, focuses the form,
 *          preserves failed submissions, and returns focus on cancel or success.
 *          Source commands, field contracts, My Work reads and authority remain unchanged.
 *          v3.4.0-MOBILE-SELECTED-LIST-SPACE reduces the
 *          scrollable control header while rows are selected, preserving
 *          a usable inbox viewport above the in-flow completion footer.
 *          v3.3.0-MOBILE-BULK-FOOTER-FLOW keeps the
 *          source-owned selection and completion controls in normal panel
 *          flow outside the scrollable inbox, so they cannot cover mobile
 *          work rows or intercept row selection.
 *          v3.2.0-VERIFIED-RESULT-STATUS labels the exact criteria and time
 *          for retained verified rows during revalidation, distinguishes
 *          pending controls, preserves selection and scroll, and keeps large
 *          queues within the established 32-row virtualization budget.
 *          v3.1.0-EXECUTIVE-TASK-COMPOSER-SURFACE places
 *          the real EOS create form in the panel's primary scroll region
 *          instead of nesting it inside clipped header and filter controls.
 *          v3.0.0-SMALL-QUEUE-ACTION-RELIABILITY renders
 *          all small admitted work queues directly for reliable mobile
 *          row selection; virtual windowing remains for large queues.
 *          v2.9.0-ACTION-CONFIRMED-MOBILE-RAIL
 *          closes the contextual rail only after EOS confirms a source
 *          completion; failed actions preserve evidence and selection.
 *          v2.8.0-EXECUTABLE-MOBILE-HEADER bounds the
 *          workspace control header on narrow screens and permits internal
 *          scrolling so source work submission remains reachable at 390px.
 *          v2.7.0-SOURCE-EXECUTION-IN-PANEL enables
 *          on-item completion evidence entry for a verified admitted work
 *          source even if optional command probing is unavailable; final
 *          success is exclusively the owning EOS POST/readback.
 *          v2.6.0-EXECUTABLE-SOURCE-CREATE-ENTRY permits
 *          operator-initiated create on a verified admitted source even
 *          when optional preflight capability checks are unavailable;
 *          EOS still refuses any unauthorized or unsubscribed source write.
 *          v2.5.0-ENTITLED-MODULE-COMMAND-CLARITY distinguishes
 *          source adapters not yet wired into inline create/complete from
 *          genuine current-session source IAM denial, without making
 *          claims about a tenant's subscription or employee privileges.
 *          v2.4.0-EXECUTIVE-SOURCE-COMMAND-DIAGNOSTICS
 *          identifies missing admitted-source command verification without
 *          concealing healthy source actions or conflating denial with outage.
 *          v2.3.0-SEMANTIC-SEVERITY-TRIAGE presents source
 *          priority and overdue urgency in labeled, distinct semantic
 *          colours across the inbox, legend and detail rail; no invented SLA.
 *          v2.2.0-EXECUTIVE-SIX-MODULE-CLARITY adds
 *          source-specific truthful zero-work explanations and denser
 *          module/priority/body/deadline information in 44px work rows.
 *          v2.1.1-ACTION-VERIFICATION-RECOVERY exposes
 *          failed command-availability verification and a source refresh,
 *          without erasing verified work or pretending commands exist.
 *          v2.1.0-SOURCE-SPECIFIC-EXECUTIVE-ENTRY makes
 *          single-source empty queues identify their actual module and
 *          offers a permitted create-work path instead of a passive zero.
 *          v2.0.0-EXECUTIVE-BULK-SOURCE-COMPLETION adds
 *          shared operator evidence and bounded 25-item source-owned
 *          completion with explicit partial-success reporting and no
 *          cross-source atomicity claim.
 *          v1.9.1-MOBILE-CREATION-BOUNDS keeps source
 *          work creation scrollable and usable inside narrow device panels.
 *          v1.9.0-AUTHORISED-WORK-CREATION adds a
 *          lightweight source-owned creation form for admitted CRM,
 *          Operations and Intelligence, with persistent intent idempotency.
 *          v1.8.0-KEYBOARD-EXECUTIVE-COMMANDS adds x selection
 *          toggling and e evidence-entry focus for source-admitted work;
 *          no keyboard key directly executes an unverified mutation.
 *          v1.7.0-SOURCE-CONFIRMED-COMPLETION shows a
 *          source-permitted completion form with operator evidence and
 *          explicit success/failure revalidation, never optimistic mutation.
 *          v1.6.0-EXECUTIVE-MULTI-ITEM-TRIAGE adds checkbox
 *          selection, clear/select-visible controls and an explicit bulk
 *          inspection handoff; server-authorised mutations remain source-owned.
 *          v1.5.0-EXECUTIVE-FOCUS-CONTINUITY retains row
 *          selection and scroll while executive search input changes and
 *          clamps scroll only after a narrower verified page arrives.
 *          v1.4.0-DENSE-EXECUTIVE-WORK-ROWS reduces task
 *          row geometry to 44px and aligns virtualised scroll math and
 *          compact priority/deadline/status labels for high-volume triage.
 *          v1.3.0-EXECUTIVE-SOURCE-CLARITY adds verified-source
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
 */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle, ArrowRight, CheckCircle2, ChevronRight,
  CircleHelp, Clock3, ExternalLink, FilterX, RefreshCw, Search,
  ShieldCheck, X,
} from 'lucide-react';
import WilsyWorkDeadlineCalendar from '../chrome/WilsyWorkDeadlineCalendar.jsx';

const FILTERS = [
  ['ALL', 'All work', 'active'],
  ['OVERDUE', 'Overdue', 'overdue'],
  ['TODAY', 'Due today', 'dueToday'],
  ['HIGH', 'High priority', 'highPriority'],
];
const SORT_MODES = [
  ['URGENCY', 'Urgency first'],
  ['DUE_ASC', 'Due date · earliest'],
  ['DUE_DESC', 'Due date · latest'],
  ['PRIORITY_DESC', 'Priority · highest'],
  ['PRIORITY_ASC', 'Priority · lowest'],
  ['TITLE', 'Title · A to Z'],
  ['SOURCE', 'Source · grouped'],
];
const PRIORITY_RANK = Object.freeze({ LOW: 1, NORMAL: 2, HIGH: 3, CRITICAL: 4 });
const ATTENTION_ROW_HEIGHT = 44;
const ATTENTION_ROW_OVERSCAN = 9;
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
const compareStable = (items, compare) => items
  .map((item, index) => ({ item, index }))
  .sort((left, right) => compare(left.item, right.item)
    || left.item.id.localeCompare(right.item.id)
    || left.index - right.index)
  .map(({ item }) => item);
const sortAttentionItems = (items, mode) => {
  // EOS already returns the AttentionItem page in canonical urgency order.
  // Preserve it verbatim so pagination and stable server tie-breaking remain
  // authoritative; client sorts below are explicit local presentation modes.
  if (mode === 'URGENCY') return items;
  if (mode === 'DUE_ASC' || mode === 'DUE_DESC') {
    const direction = mode === 'DUE_ASC' ? 1 : -1;
    return compareStable(items, (a, b) => {
      const left = a.dueAt ? Date.parse(a.dueAt) : null;
      const right = b.dueAt ? Date.parse(b.dueAt) : null;
      if (left === null || right === null) {
        return left === right ? 0 : left === null ? 1 : -1;
      }
      return (left - right) * direction;
    });
  }
  if (mode === 'PRIORITY_DESC' || mode === 'PRIORITY_ASC') {
    const direction = mode === 'PRIORITY_DESC' ? -1 : 1;
    return compareStable(items, (a, b) =>
      (PRIORITY_RANK[a.priority] - PRIORITY_RANK[b.priority]) * direction);
  }
  if (mode === 'TITLE') {
    return compareStable(items, (a, b) => a.title.localeCompare(b.title, undefined, {
      sensitivity: 'base', numeric: true,
    }));
  }
  if (mode === 'SOURCE') {
    return compareStable(items, (a, b) => a.sourceModule.localeCompare(b.sourceModule)
      || b.urgencyScore - a.urgencyScore);
  }
  return items;
};
const SOURCE_FIELD_NAMES = new Set(['title', 'description', 'priority', 'due_at']);
const sourceFieldErrors = (message) => {
  const errors = {};
  if (typeof message !== 'string') return errors;
  for (const match of message.matchAll(/(?:^|[, ])(title|description|priority|due_at) \(([a-z0-9_]{1,80})\)/g)) {
    if (SOURCE_FIELD_NAMES.has(match[1])) errors[match[1]] = match[2];
  }
  return errors;
};
const fieldErrorCopy = (field, reason) => {
  const label = field === 'due_at' ? 'deadline' : field;
  if (reason === 'missing' || reason === 'string_too_short') return 'Enter a valid ' + label + '.';
  if (reason === 'string_too_long') return 'Shorten the ' + label + ' to meet the source limit.';
  return 'EOS rejected the ' + label + '. Review it and retry.';
};
const EMPTY_SOURCE_COPY = Object.freeze({
  CRM: 'Deals, follow-ups and commercial tasks appear when the CRM source has active work.',
  LEGAL: 'Assigned legal reviews, matters and approved practice work appear when the Legal source reports them.',
  FINANCE: 'Authorised financial approvals and exceptions appear only when a Finance source is admitted.',
  PEOPLE: 'Assigned workforce requests and cases appear only when People is admitted.',
  OPERATIONS: 'Operational jobs, reminders and exceptions appear when the Operations source reports them.',
  INTELLIGENCE: 'Authorised alerts and review obligations appear when Intelligence raises them.',
});
const SEVERITY = Object.freeze({
  CRITICAL: { label: 'Critical', chip: 'border-rose-400/70 bg-rose-500/20 text-rose-100', rail: 'border-rose-400', row: 'border-l-rose-500 bg-rose-500/[0.045]', dot: 'bg-rose-400' },
  HIGH: { label: 'High', chip: 'border-orange-400/65 bg-orange-500/15 text-orange-100', rail: 'border-orange-400', row: 'border-l-orange-400 bg-orange-500/[0.035]', dot: 'bg-orange-400' },
  NORMAL: { label: 'Normal', chip: 'border-sky-400/55 bg-sky-500/15 text-sky-100', rail: 'border-sky-400', row: 'border-l-sky-500', dot: 'bg-sky-400' },
  LOW: { label: 'Low', chip: 'border-slate-400/50 bg-slate-400/10 text-slate-200', rail: 'border-slate-400', row: 'border-l-slate-500', dot: 'bg-slate-400' },
});
const severityFor = (item) => item.isOverdue
  ? { label: 'Overdue', chip: 'border-red-400/70 bg-red-500/20 text-red-100', rail: 'border-red-400', row: 'border-l-red-500 bg-red-500/[0.06]', dot: 'bg-red-400' }
  : SEVERITY[item.priority] || SEVERITY.NORMAL;
const sourceStatus = (item) => typeof item?.status === 'string'
  && item.status.trim() ? item.status : 'Source status unavailable';
const criteriaLabel = (criteria) => {
  if (!criteria) return 'no prior verified filter';
  const filterName = FILTERS.find(([id]) => id === criteria.filter)?.[1] || 'All work';
  const sourceName = criteria.source === 'ALL' ? 'all admitted sources' : label(criteria.source);
  const search = criteria.query ? ' · search “' + criteria.query + '”' : '';
  return filterName + ' · ' + sourceName + search;
};

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
  authorisedActions = {}, onCompleteWork, completingId = null, completionError = '',
  getCompletionReceipt = () => null, completionReadbackReady = false,
  onCreateWork, creatingWork = false, creationError = '', creationNotice = '', workUpdating = false,
  verifiedCriteria = null, requestedCriteria = null, resultsUpdating = false,
  resultsUnavailable = false, resultFailureCode = '',
  onBulkComplete, bulkCompleting = false, bulkResult = '',
  actionAvailabilityUnavailable = false, unavailableActionSources = [],
}) {
  const [mode, setMode] = useState('LIST');
  const [selectedId, setSelectedId] = useState(null);
  const completionFocusIdRef = useRef(null);
  const [checkedIds, setCheckedIds] = useState([]);
  const [bulkSelectionMode, setBulkSelectionMode] = useState(false);
  const [completionNote, setCompletionNote] = useState('');
  const [completionNotice, setCompletionNotice] = useState('');
  const [bulkNote, setBulkNote] = useState('');
  const [createSource, setCreateSource] = useState('');
  const [createTitle, setCreateTitle] = useState('');
  const [createTitleError, setCreateTitleError] = useState('');
  const [createDescription, setCreateDescription] = useState('');
  const [createPriority, setCreatePriority] = useState('NORMAL');
  const [createDue, setCreateDue] = useState('');
  const createKeyRef = useRef(null);
  const createIntentStatusRef = useRef(null);
  const createFieldErrors = sourceFieldErrors(creationError);
  const createTitleRef = useRef(null);
  const createTriggerRef = useRef(null);
  const previousModeRef = useRef(mode);
  const [showBriefing, setShowBriefing] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showSourceDetails, setShowSourceDetails] = useState(false);
  const [selectionIndex, setSelectionIndex] = useState(0);
  const [scrollTop, setScrollTop] = useState(0);
  const [viewportHeight, setViewportHeight] = useState(DEFAULT_VIEWPORT_HEIGHT);
  const [sortMode, setSortMode] = useState('URGENCY');
  const searchRef = useRef(null);
  const completionRef = useRef(null);
  const listRef = useRef(null);
  const inboxRef = useRef(null);
  const page = useMemo(() => sortAttentionItems(feed.items, sortMode), [feed.items, sortMode]);
  const inboxOffset = inboxRef.current?.offsetTop || 0;
  const firstVisibleIndex = Math.floor(Math.max(0, scrollTop - inboxOffset)
    / ATTENTION_ROW_HEIGHT);
  const windowStart = page.length <= 50
    ? 0 : Math.max(0, firstVisibleIndex - ATTENTION_ROW_OVERSCAN);
  const windowSize = Math.ceil(viewportHeight / ATTENTION_ROW_HEIGHT)
    + ATTENTION_ROW_OVERSCAN * 2;
  const windowEnd = page.length <= 50
    ? page.length : Math.min(page.length, windowStart + windowSize);
  const visibleItems = page.slice(windowStart, windowEnd).map((item, offset) => ({
    item, index: windowStart + offset,
  }));
  const rows = useMemo(() => Array.isArray(calendarItems)
    ? calendarItems : page.map(toWorkItem), [calendarItems, page]);
  const selected = page.find((item) => item.id === selectedId) || null;
  const selectedCompletionReceipt = selected ? getCompletionReceipt(selected) : null;
  const sourceCoverage = feed.sources || [];
  const canCompleteItem = (item) => Boolean(item
    && item.status === 'OPEN'
    && ['CRM', 'OPERATIONS', 'INTELLIGENCE'].includes(item.sourceModule)
    && sourceCoverage.some((entry) => entry.moduleId === item.sourceModule)
    && authorisedActions[item.sourceModule]?.includes('COMPLETE')
    && typeof onCompleteWork === 'function');
  const canComplete = canCompleteItem(selected);
  const checkedSet = useMemo(() => new Set(checkedIds), [checkedIds]);
  const checkedItems = page.filter((item) => checkedSet.has(item.id));
  const bulkEligible = checkedItems.filter((item) => item.status === 'OPEN'
    && authorisedActions[item.sourceModule]?.includes('COMPLETE'));
  const batchItems = bulkEligible.slice(0, 25);
  const ranked = page.slice(0, 5);
  const inlineCommandSources = ['CRM', 'OPERATIONS', 'INTELLIGENCE'];
  const unmappedSources = sourceCoverage.filter((entry) => !inlineCommandSources.includes(entry.moduleId));
  // An optional action-status read is not the authorization decision.
  // The source-owned POST independently authenticates, checks IAM/entitlement
  // and persists; expose a real user-initiated attempt only for admitted work.
  const creatableSources = sourceCoverage
    .map((entry) => entry.moduleId)
    .filter((moduleId) => inlineCommandSources.includes(moduleId));
  const unverifiedCreateSources = creatableSources.filter((moduleId) =>
    !authorisedActions[moduleId]?.includes('CREATE'));
  const createPreflightUnverified = unverifiedCreateSources.includes(
    creatableSources.includes(createSource) ? createSource : creatableSources[0]);
  const chosenCreateSource = creatableSources.includes(createSource)
    ? createSource : creatableSources[0];
  const missing = feed.coverage.notRepresentedSources || [];
  const allEmpty = feed.counts.active === 0 && !feed.nextCursor;
  const hasFiltered = filter !== 'ALL' || source !== 'ALL' || query.trim().length > 0;
  const filterEmpty = !page.length && hasFiltered;
  const singleSource = source !== 'ALL'
    ? sourceCoverage.find((entry) => entry.moduleId === source)
    : sourceCoverage.length === 1 ? sourceCoverage[0] : null;

  useEffect(() => { setCompletionNote(''); }, [selectedId]);

  useEffect(() => {
    if (completionFocusIdRef.current && selected?.id === completionFocusIdRef.current
      && canComplete) {
      completionRef.current?.focus();
      completionFocusIdRef.current = null;
    }
  }, [selectedId, selected?.id, canComplete]);

  useEffect(() => {
    if (mode === 'CREATE') {
      createTitleRef.current?.focus();
    } else if (previousModeRef.current === 'CREATE') {
      createTriggerRef.current?.focus();
    }
    previousModeRef.current = mode;
  }, [mode]);

  useEffect(() => {
    const node = listRef.current;
    if (!node || page.length === 0) return;
    const maximum = Math.max(0, page.length * ATTENTION_ROW_HEIGHT
      - (node.clientHeight || DEFAULT_VIEWPORT_HEIGHT));
    if (node.scrollTop > maximum) {
      node.scrollTop = maximum;
      setScrollTop(maximum);
    }
  }, [page.length]);

  useEffect(() => {
    const node = listRef.current;
    if (!node || mode !== 'LIST') return undefined;
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
    const selectedIndex = selectedId
      ? page.findIndex((item) => item.id === selectedId) : -1;
    if (selectedId && selectedIndex < 0) setSelectedId(null);
    setSelectionIndex((before) => selectedIndex >= 0
      ? selectedIndex
      : Math.max(0, Math.min(before, Math.max(0, page.length - 1))));
    setCheckedIds((before) => {
      const present = new Set(page.map((item) => item.id));
      const next = before.filter((id) => present.has(id));
      return next.length === before.length ? before : next;
    });
  }, [page, selectedId]);

  const openCreate = (moduleId) => {
    if (!moduleId || typeof onCreateWork !== 'function' || creatingWork || workUpdating) return;
    setCreateSource(moduleId);
    setMode('CREATE');
  };

  const cancelCreate = () => {
    if (creatingWork) return;
    setMode('LIST');
  };

  const submitCreate = async (event, requestedStatus = 'OPEN') => {
    event.preventDefault();
    const initialStatus = chosenCreateSource === 'CRM' && requestedStatus === 'DRAFT'
      ? 'DRAFT' : 'OPEN';
    if (createIntentStatusRef.current !== initialStatus) createKeyRef.current = null;
    createIntentStatusRef.current = initialStatus;
    if (!chosenCreateSource || creatingWork || workUpdating
      || typeof onCreateWork !== 'function') return;
    if (!createTitle.trim()) {
      setCreateTitleError('Enter a work title.');
      createTitleRef.current?.focus();
      return;
    }
    setCreateTitleError('');
    if (!createKeyRef.current) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') return;
      createKeyRef.current = globalThis.crypto.randomUUID();
    }
    const due_at = createDue ? new Date(createDue).toISOString() : null;
    const accepted = await onCreateWork(chosenCreateSource, {
      title: createTitle.trim(), description: createDescription,
      priority: createPriority, due_at,
      ...(chosenCreateSource === 'CRM' ? { initial_status: initialStatus } : {}),
    }, createKeyRef.current);
    if (accepted) {
      setMode('LIST');
      setCreateTitle('');
      setCreateTitleError('');
      setCreateDescription('');
      setCreatePriority('NORMAL');
      setCreateDue('');
      createKeyRef.current = null;
      createIntentStatusRef.current = null;
    }
  };

  const open = (item) => {
    if (!item) return;
    onOpenWork?.(toWorkItem(item));
  };

  const prepareCompletion = (item, index) => {
    if (!canCompleteItem(item) || completingId || workUpdating) return;
    setCompletionNotice('');
    completionFocusIdRef.current = item.id;
    setSelectionIndex(index);
    setSelectedId(item.id);
    if (selectedId === item.id) {
      completionRef.current?.focus();
      completionFocusIdRef.current = null;
    }
  };

  // Scoped shortcuts: never hijack a text field, modal, or other workspace.
  const handleKey = (event) => {
    const target = event.target;
    if (event.key === 'Escape' && mode === 'CREATE') {
      event.preventDefault();
      event.stopPropagation();
      cancelCreate();
      return;
    }
    if (mode === 'CREATE') return;
    if (event.altKey || event.metaKey || event.ctrlKey
      || /^(INPUT|TEXTAREA|SELECT)$/.test(target?.tagName || '')
      || target?.isContentEditable) return;
    if (event.key === 'Escape') {
      if (showShortcuts || mode === 'CALENDAR' || selectedId) {
        event.preventDefault();
        event.stopPropagation();
        if (showShortcuts) setShowShortcuts(false);
        else if (mode === 'CALENDAR') setMode('LIST');
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
    if (mode !== 'LIST' || page.length === 0) return;
    if (event.key === 'x' && selected && bulkSelectionMode) {
      event.preventDefault();
      setCheckedIds((before) => before.includes(selected.id)
        ? before.filter((id) => id !== selected.id) : [...before, selected.id]);
      return;
    }
    if (event.key === 'e' && canComplete && selected) {
      event.preventDefault();
      completionRef.current?.focus();
      return;
    }
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
      data-attention-production-ui="true" data-attention-mode={mode} onKeyDown={handleKey}>
      <div className="shrink-0 border-b border-white/10 bg-[#14243d] px-3 py-2 sm:px-4">
        {mode === 'CREATE' ? (
          <div className="flex min-h-12 items-center justify-between gap-3" aria-label="Create mode toolbar">
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-white">Create work in {label(chosenCreateSource)}</p>
              <p className="mt-1 text-xs text-slate-400">The source service confirms persistence before this work appears in the list.</p>
            </div>
          </div>
        ) : (
          <>
        <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1.5">
          <div className="flex min-w-0 items-baseline gap-2">
            <h2 className="shrink-0 text-sm font-bold text-white">Daily Attention</h2>
            <span className="truncate text-[10px] text-slate-400">
              {sourceCoverage.length} admitted {sourceCoverage.length === 1 ? 'source' : 'sources'} · verified {new Date(feed.syncedAt).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            {creatableSources.length > 0 && typeof onCreateWork === 'function' && (
              <button type="button" data-attention-create-trigger="true"
                ref={createTriggerRef}
                disabled={creatingWork || workUpdating}
                onClick={() => openCreate(chosenCreateSource)}
                className="rounded-lg bg-amber-300 px-3 py-2 text-xs font-bold text-slate-950">
                Create work
              </button>
            )}
            <button type="button" onClick={() => setShowShortcuts((v) => !v)}
              aria-label="Daily attention keyboard shortcuts" aria-expanded={showShortcuts}
              className="rounded-md border border-white/10 p-1.5 text-slate-300 hover:bg-white/10"><CircleHelp size={14}/></button>
            <button type="button" onClick={onRefresh} title={'Last synced: ' + feed.syncedAt}
              className="inline-flex items-center gap-1 rounded-md border border-white/10 px-2 py-1.5 text-[11px] text-slate-300 hover:bg-white/10">
              <RefreshCw size={13}/>Refresh
            </button>
          </div>
        </div>
        {resultsUpdating && (
          <p role="status" aria-live="polite" data-testid="attention-refresh-state"
            data-attention-refresh-state="UPDATING"
            className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-md border border-amber-300/15 bg-amber-300/[0.04] px-2 py-1.5 text-[10px] text-amber-100/90">
            <RefreshCw size={12} className="animate-spin"/>
            <span>Checking pending results: {criteriaLabel(requestedCriteria)}.</span>
            <span className="text-slate-300">Showing last verified results: {criteriaLabel(verifiedCriteria)} · verified {new Date(feed.syncedAt).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}.</span>
          </p>
        )}
        {resultsUnavailable && (
          <p role="alert" data-testid="attention-refresh-state"
            data-attention-refresh-state="UNAVAILABLE"
            className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-md border border-rose-300/15 bg-rose-300/[0.035] px-2 py-1.5 text-[10px] text-rose-100/90">
            <AlertTriangle size={12}/>
            <span>{resultFailureCode === 'ATTENTION_CONNECTION_UNAVAILABLE'
              ? 'EOS could not reverify the requested view.'
              : 'The requested view could not be verified.'}</span>
            <span className="text-slate-300">Still showing last verified results: {criteriaLabel(verifiedCriteria)} · verified {new Date(feed.syncedAt).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}. Pending: {criteriaLabel(requestedCriteria)}.</span>
            <button type="button" onClick={onRefresh} className="underline underline-offset-2">Retry</button>
          </p>
        )}
        {creationNotice && <p role="status" className="mt-2 text-xs text-emerald-200">{creationNotice}</p>}
        {actionAvailabilityUnavailable && <p role="alert" className="mt-1 text-[10px] text-amber-200">
          {unavailableActionSources.length ? unavailableActionSources.map(label).join(', ') + ': ' : ''}
          Some source commands could not be verified. Verified commands remain usable.
          <button type="button" onClick={onRefresh} className="ml-2 underline">Retry command verification</button>
        </p>}
        {showShortcuts && (
          <div role="note" className="mt-1 rounded-lg border border-amber-300/20 bg-[#0a1628] p-2 text-[10px] leading-4 text-slate-300">
            <strong className="text-amber-100">Shortcuts:</strong> j/k select work · Enter/o open
            · / search · 1–4 filters · x select · e complete evidence when permitted
            · Esc clear detail · ? toggle help.
            Completion, assignment and snooze shortcuts become available only
            when their source-owned action APIs are certified.
          </div>
        )}
        {mode === 'LIST' && <div className="mt-2 flex flex-wrap gap-2 text-[10px]" aria-label={resultsUpdating || resultsUnavailable
          ? 'Last verified current-source workload' : 'Verified current-source workload'}>
          {[
            ['ALL', 'Active', feed.counts.active],
            ['OVERDUE', 'Overdue', feed.counts.overdue],
            ['TODAY', 'Due today', feed.counts.dueToday],
            ['HIGH', 'High priority', feed.counts.highPriority],
          ].map(([id, name, count]) => (
            <button key={id} type="button"
              aria-label={name + ': ' + count}
              aria-pressed={filter === id}
              onClick={() => setFilter(id)}
              className={'inline-flex items-center gap-1.5 rounded-md border px-2 py-1 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300 ' +
                (filter === id ? 'ring-1 ring-inset ring-amber-300/65 ' : '') +
                (name === 'Overdue' && count > 0
                  ? 'border-rose-300/50 bg-rose-300/[0.08] text-rose-100'
                  : 'border-white/15 bg-white/[0.035] text-slate-200 hover:bg-white/[0.08]')}>
              <span>{name}</span>
              <strong className="font-semibold tabular-nums">{count}</strong>
            </button>
          ))}
          {(resultsUpdating || resultsUnavailable) && <span className="self-center text-amber-100/80">Last verified</span>}
        </div>}
        {mode === 'LIST' && <div className="mt-2 flex min-w-0 flex-wrap items-center gap-1.5" aria-label="Daily attention toolbar">
          <label className="flex min-w-[180px] flex-1 items-center gap-2 rounded-md border border-white/15 bg-[#0a1628] px-2.5">
            <Search size={14} className="shrink-0 text-slate-400"/>
            <input ref={searchRef} type="search" aria-label="Search authorised work"
              placeholder="Search work…" value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="h-8 min-w-0 flex-1 bg-transparent text-[11px] outline-none placeholder:text-slate-500"/>
          </label>
          <label className="sr-only" htmlFor="attention-work-view">Work view</label>
          <select id="attention-work-view" aria-label="Work view" value={mode}
            onChange={(event) => setMode(event.target.value)}
            className="h-8 rounded-md border border-white/15 bg-[#0a1628] px-2 text-[10px] text-slate-200">
            <option value="LIST">Work list</option><option value="CALENDAR">Calendar</option>
          </select>
          <label className="sr-only" htmlFor="attention-filter">Filter</label>
          <select id="attention-filter" aria-label="Filter daily attention" value={filter}
            onChange={(event) => setFilter(event.target.value)}
            className="h-8 rounded-md border border-white/15 bg-[#0a1628] px-2 text-[10px] text-slate-200">
            {FILTERS.map(([id, name]) => <option key={id} value={id}>{name}</option>)}
          </select>
          <label className="sr-only" htmlFor="attention-source-filter">Source</label>
          <select id="attention-source-filter" aria-label="Filter work by source" value={source}
            onChange={(event) => setSource(event.target.value)}
            className="h-8 max-w-[140px] rounded-md border border-white/15 bg-[#0a1628] px-2 text-[10px] text-slate-200">
            <option value="ALL">All sources</option>
            {sourceCoverage.map((entry) => <option key={entry.moduleId} value={entry.moduleId}>{label(entry.moduleId)}</option>)}
          </select>
          <label className="sr-only" htmlFor="attention-sort">Sort</label>
          <select id="attention-sort" aria-label="Sort attention work" value={sortMode}
            onChange={(event) => setSortMode(event.target.value)}
            className="h-8 max-w-[160px] rounded-md border border-white/15 bg-[#0a1628] px-2 text-[10px] text-slate-200">
            {SORT_MODES.map(([id, name]) => <option key={id} value={id}>{name}</option>)}
          </select>
          {page.length > 0 && <button type="button"
            aria-label={bulkSelectionMode ? 'Exit selection mode' : 'Select work'}
            aria-pressed={bulkSelectionMode}
            onClick={() => {
              if (bulkSelectionMode) setCheckedIds([]);
              setBulkSelectionMode((active) => !active);
            }}
            className="h-8 rounded-md border border-white/15 bg-[#0a1628] px-3 text-[10px] font-semibold text-amber-100 hover:bg-white/10">
            {bulkSelectionMode ? 'Exit selection' : 'Select work'}
          </button>}
        </div>}
        <div className="mt-1.5 flex flex-wrap items-center justify-between gap-2 text-[10px]">
          <button type="button" onClick={() => setShowSourceDetails((value) => !value)}
            aria-expanded={showSourceDetails} aria-controls="attention-source-evidence"
            className="inline-flex items-center gap-1.5 rounded-md text-slate-400 hover:text-emerald-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
            <ShieldCheck size={12}/> Source details
            <ChevronRight size={12} className={showSourceDetails ? 'rotate-90' : ''}/>
          </button>
          {ranked.length > 0 && <button type="button" onClick={() => setShowBriefing((value) => !value)}
            aria-expanded={showBriefing} className="text-slate-400 hover:text-amber-100">
            {showBriefing ? 'Hide' : 'Show'} briefing
          </button>}
        </div>
        {showSourceDetails && (
          <section id="attention-source-evidence" aria-label="Last verified attention source details"
            className="mt-2 rounded-lg border border-white/10 bg-[#0a1628] px-3 py-2 text-[11px] leading-5">
            <p className="font-semibold text-slate-200">Last verified source evidence for this session · {sourceCoverage.length} admitted · synced {new Date(feed.syncedAt).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</p>
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
            {unmappedSources.length > 0 && <p className="mt-2 text-slate-300">
              Source-owned commands outside this panel: {unmappedSources.map((item) => label(item.moduleId)).join(', ')}.
              A missing inline adapter does not imply a missing tenant subscription or permission.
            </p>}
            {!actionAvailabilityUnavailable && sourceCoverage.length > 0
              && creatableSources.length === 0 && <p className="mt-2 text-slate-300">
                {sourceCoverage.some((entry) => inlineCommandSources.includes(entry.moduleId))
                  ? 'No inline create-work permission was verified for admitted sources. Existing work remains readable.'
                  : 'No inline create-work adapter is available for admitted sources. Use their governed source workspaces for commands.'}
              </p>}
            <button type="button" onClick={onRefresh}
              className="mt-2 rounded-md border border-white/15 px-2.5 py-1 text-amber-100 hover:bg-white/5">
              Recheck authorised sources
            </button>
          </section>
        )}
        {missing.length > 0 && !showSourceDetails && <p className="mt-1 px-2 text-[10px] leading-4 text-amber-100/75">
          Not represented in this session: {missing.map(label).join(', ')}. No module access or cleared status is inferred.
        </p>}
          </>
        )}
      </div>
      {mode === 'CREATE' && chosenCreateSource ? (
        <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-3 py-4 sm:px-6" aria-label="New source work editor" data-attention-create-form="true">
          <div className="mx-auto mb-3 max-w-3xl">
            <h3 className="text-base font-semibold text-white">Create work in {label(chosenCreateSource)}</h3>
            <p className="mt-1 text-xs text-slate-400">
              EOS validates the task, records its owner and persists it in the source module.
            </p>
          </div>
          <form onSubmit={submitCreate} noValidate aria-busy={creatingWork}
            aria-label="Create source work"
            className="mx-auto grid w-full max-w-3xl gap-3 rounded-xl border border-amber-300/25 bg-[#0a1628] p-4 sm:p-5">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <label className="text-[11px] text-slate-300">Owning source
                <select value={chosenCreateSource}
                  onChange={(event) => { setCreateSource(event.target.value); createKeyRef.current = null; }}
                  className="mt-1 block w-full rounded-md border border-white/15 bg-[#14243d] p-2">
                  {creatableSources.map((moduleId) => <option key={moduleId} value={moduleId}>{label(moduleId)}</option>)}
                </select>
              </label>
              <label className="text-[11px] text-slate-300">Priority
                <select value={createPriority} aria-invalid={Boolean(createFieldErrors.priority)}
                  aria-describedby={createFieldErrors.priority ? 'attention-priority-error' : undefined}
                  onChange={(event) => { setCreatePriority(event.target.value); createKeyRef.current = null; }}
                  className="mt-1 block w-full rounded-md border border-white/15 bg-[#14243d] p-2">
                  {['NORMAL', 'LOW', 'HIGH', 'CRITICAL'].map((priority) =>
                    <option key={priority} value={priority}>{priority}</option>)}
                </select>
                {createFieldErrors.priority && <span id="attention-priority-error" role="alert" className="mt-1 block text-[11px] text-rose-200">{fieldErrorCopy('priority', createFieldErrors.priority)}</span>}
              </label>
            </div>
            <label className="text-[11px] text-slate-300">Work title
              <input ref={createTitleRef} value={createTitle} maxLength={240} required
                aria-invalid={Boolean(createTitleError || createFieldErrors.title)}
                aria-describedby={createTitleError || createFieldErrors.title ? 'attention-title-error' : undefined}
                onChange={(event) => {
                  setCreateTitle(event.target.value);
                  if (event.target.value.trim()) setCreateTitleError('');
                  createKeyRef.current = null;
                }}
                placeholder="What needs to be done?"
                className="mt-1 block w-full rounded-md border border-white/15 bg-[#14243d] p-2 text-xs"/>
              {(createTitleError || createFieldErrors.title) && <span id="attention-title-error" role="alert" className="mt-1 block text-[11px] text-rose-200">{createTitleError || fieldErrorCopy('title', createFieldErrors.title)}</span>}
            </label>
            <label className="text-[11px] text-slate-300">Description
              <textarea value={createDescription} maxLength={4000} rows={2}
                aria-invalid={Boolean(createFieldErrors.description)}
                aria-describedby={createFieldErrors.description ? 'attention-description-error' : undefined}
                onChange={(event) => { setCreateDescription(event.target.value); createKeyRef.current = null; }}
                placeholder="Outcome, owner context or instructions"
                className="mt-1 block w-full rounded-md border border-white/15 bg-[#14243d] p-2 text-xs"/>
              {createFieldErrors.description && <span id="attention-description-error" role="alert" className="mt-1 block text-[11px] text-rose-200">{fieldErrorCopy('description', createFieldErrors.description)}</span>}
            </label>
            <label className="text-[11px] text-slate-300">Deadline (optional)
              <input type="datetime-local" value={createDue}
                aria-invalid={Boolean(createFieldErrors.due_at)}
                aria-describedby={createFieldErrors.due_at ? 'attention-deadline-error' : undefined}
                onChange={(event) => { setCreateDue(event.target.value); createKeyRef.current = null; }}
                className="mt-1 block w-full rounded-md border border-white/15 bg-[#14243d] p-2 text-xs"/>
              {createFieldErrors.due_at && <span id="attention-deadline-error" role="alert" className="mt-1 block text-[11px] text-rose-200">{fieldErrorCopy('due_at', createFieldErrors.due_at)}</span>}
            </label>
            {createPreflightUnverified && <p className="text-[11px] text-amber-200">
              Source create permission is not preverified. Submitting will ask EOS to authorize the action;
              a denial will not create work.
            </p>}
            {creationError && <p role="alert" className="text-xs text-rose-200">{creationError}</p>}
            <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <button type="button" disabled={creatingWork}
                onClick={cancelCreate}
                className="rounded-md border border-white/20 px-4 py-3 text-sm font-semibold text-slate-100 disabled:opacity-50 sm:py-2">
                Cancel
              </button>
              {chosenCreateSource === 'CRM' && <button type="button"
                disabled={creatingWork || workUpdating}
                onClick={(event) => submitCreate(event, 'DRAFT')}
                className="rounded-md border border-amber-300/40 px-4 py-3 text-sm font-semibold text-amber-100 disabled:opacity-50 sm:py-2">
                Save draft
              </button>}
              <button type="submit" disabled={creatingWork || workUpdating}
                className="rounded-md bg-amber-300 px-4 py-3 text-sm font-bold text-slate-950 disabled:opacity-50 sm:py-2">
                {creatingWork ? 'Saving with EOS…' : 'Submit task to EOS'}
              </button>
            </div>
          </form>
        </div>
      ) : mode === 'CALENDAR' ? (
        <div className="min-h-0 flex-1 overflow-auto px-3 py-3">
          <WilsyWorkDeadlineCalendar items={rows} onOpenWork={onOpenWork}
            onOpenWorkforce={onOpenWorkforce}/>
          <button type="button" onClick={() => setMode('LIST')}
            aria-label="Close calendar and return to work list"
            className="mt-2 rounded-lg border border-amber-300/30 px-3 py-2 text-xs text-amber-100">
            Return to work list
          </button>
        </div>
      ) : (
        <div data-attention-detail-layout={selected ? "split" : "list"}
           className={selected
             ? "relative grid min-h-0 min-w-0 flex-1 grid-cols-1 overflow-hidden md:grid-cols-[minmax(0,38fr)_minmax(0,62fr)]"
             : "relative flex min-h-0 min-w-0 flex-1 overflow-hidden"}>
           <div data-attention-work-list="true"
             className={"relative min-h-0 min-w-0 flex-col overflow-hidden " + (selected ? "hidden md:flex" : "flex flex-1")}>
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
          {!page.length && (resultsUpdating || resultsUnavailable) && (
            <section aria-label="Last verified attention results" className="px-6 py-8"
              data-attention-verified-results="true">
              <RefreshCw size={23} className={resultsUpdating ? 'animate-spin text-amber-200' : 'text-slate-400'}/>
              <h3 className="mt-2 text-base font-semibold">No rows in the last verified result</h3>
              <p className="mt-2 text-xs leading-5 text-slate-400">
                The last verified criteria were {criteriaLabel(verifiedCriteria)}. The current request for {criteriaLabel(requestedCriteria)} has not been verified; no zero or empty status is asserted for it.
              </p>
            </section>
          )}
          {!page.length && !resultsUpdating && !resultsUnavailable && (
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
                    {' '}{singleSource ? EMPTY_SOURCE_COPY[singleSource.moduleId] : 'No next SLA or completed-work count is available from this feed.'}
                  </p>
                  {creatableSources.length > 0 && onCreateWork && (
                    <button type="button" onClick={() => openCreate(
                      creatableSources.includes(singleSource?.moduleId)
                        ? singleSource.moduleId : creatableSources[0],
                    )} className="mt-4 mr-2 rounded-lg bg-amber-300 px-3 py-2 text-xs font-semibold text-slate-950">
                      Create {label(creatableSources.includes(singleSource?.moduleId)
                        ? singleSource.moduleId : creatableSources[0])} work
                    </button>
                  )}
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
            <section aria-label={resultsUpdating || resultsUnavailable
              ? 'Last verified attention inbox' : 'Attention inbox'}
              data-attention-verified-results="true">
              {bulkSelectionMode && <div className="sticky top-0 z-[1] flex items-center justify-between gap-2 border-b border-white/10 bg-[#101d32] px-3 py-1.5 text-[11px]">
                <label className="inline-flex items-center gap-2 text-slate-300">
                  <input type="checkbox" aria-label="Select all loaded work"
                    checked={checkedItems.length === page.length && page.length > 0}
                    onChange={(event) => setCheckedIds(event.target.checked
                      ? page.map((item) => item.id) : [])}
                    className="accent-amber-300"/>
                  Select loaded · {checkedItems.length} selected
                </label>
                {checkedItems.length > 0 && (
                  <button type="button" onClick={() => setCheckedIds([])}
                    className="text-amber-200 hover:text-amber-100">Clear selection</button>
                )}
              </div>}
              <div ref={inboxRef} role="list" data-attention-inbox-window="true"
                style={{height: page.length * ATTENTION_ROW_HEIGHT, position: 'relative'}}>
                {visibleItems.map(({item, index}) => (
                  <article key={item.id} role="listitem" data-attention-row
                    aria-setsize={page.length} aria-posinset={index + 1}
                    style={{position: 'absolute', top: index * ATTENTION_ROW_HEIGHT,
                      left: 0, right: 0, height: ATTENTION_ROW_HEIGHT}}
                    className={'box-border flex items-center gap-2 border-b border-white/[0.07] border-l-[3px] px-3 py-0.5 transition-colors ' +
                      severityFor(item).row + (selectedId === item.id
                        ? ' ring-1 ring-inset ring-amber-300/60' : ' hover:bg-white/[0.06]')}>
                    {bulkSelectionMode && <input type="checkbox" aria-label={'Select ' + item.title}
                      checked={checkedSet.has(item.id)}
                      onChange={(event) => setCheckedIds((before) => event.target.checked
                        ? [...before.filter((id) => id !== item.id), item.id]
                        : before.filter((id) => id !== item.id))}
                      className="h-4 w-4 shrink-0 accent-amber-300"/>}
                    <span className="hidden w-14 shrink-0 rounded-md border border-white/10 bg-white/[0.035] px-1.5 py-1 text-center text-[10px] font-semibold text-slate-300 sm:block">
                      {label(item.sourceModule)}
                    </span>
                    <span aria-label={'Severity ' + severityFor(item).label + '; priority ' + item.priority}
                      className={'inline-flex w-[76px] shrink-0 items-center justify-center gap-1 rounded-md border px-1 py-1 text-[10px] font-bold ' + severityFor(item).chip}>
                      <span aria-hidden="true" className={'h-1.5 w-1.5 rounded-full ' + severityFor(item).dot}/>
                      {severityFor(item).label}
                    </span>
                    <button type="button" aria-label={'Inspect ' + item.title}
                      aria-pressed={selectedId === item.id}
                      onClick={() => { setSelectedId(item.id); setSelectionIndex(index); }}
                      className="min-w-0 flex-1 text-left focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
                      <span className="block truncate text-xs font-semibold text-white">{item.title}</span>
                      <span className={'mt-0.5 block truncate text-[10px] leading-4 ' +
                        (item.isOverdue ? 'text-rose-200' : 'text-slate-400')}>
                        <span>{label(item.sourceModule)} · {sourceStatus(item)}</span>{' · '}
                        <span>{item.summary || label(item.sourceModule)}</span>
                      </span>
                    </button>
                    <span className={'hidden w-[112px] shrink-0 truncate text-right text-[10px] ' +
                      (selected ? '2xl:block ' : 'sm:block ') +
                      (item.isOverdue ? 'text-rose-200' : 'text-slate-400')}
                      title={dueLabel(item.dueAt)}>
                      {dueLabel(item.dueAt)}
                    </span>
                    <div className="flex shrink-0 items-center gap-1">
                      {canCompleteItem(item) && <button type="button"
                        aria-label={'Complete ' + item.title}
                        onClick={() => prepareCompletion(item, index)}
                        disabled={Boolean(completingId) || workUpdating}
                        className="rounded-md bg-amber-300 px-2 py-1.5 text-[10px] font-bold text-slate-950 hover:bg-amber-200 disabled:cursor-not-allowed disabled:opacity-50">
                        Complete
                      </button>}
                      <button type="button" aria-label={'Open details for ' + item.title}
                        aria-pressed={selectedId === item.id}
                        onClick={() => { setSelectedId(item.id); setSelectionIndex(index); }}
                        className="rounded-md border border-white/20 px-2 py-1.5 text-[10px] font-semibold text-slate-100 hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
                        Details
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )}
          {feed.nextCursor && (
            <button type="button" onClick={onLoadMore} disabled={loadingMore || workUpdating}
              className="m-3 w-[calc(100%-1.5rem)] rounded-lg border border-white/20 px-3 py-2 text-xs text-amber-100 disabled:opacity-50">
              {loadingMore ? 'Loading verified work…' : 'Load more work'}
            </button>
          )}
          {pageError && <p role="alert" className="px-4 py-2 text-xs text-rose-200">
            Page verification failed. Refresh to reload EOS source truth.</p>}
          </div>
          {bulkResult && <p role="status" className="border-t border-emerald-300/20 bg-[#12302d] px-3 py-2 text-xs text-emerald-100">{bulkResult}</p>}
          {bulkSelectionMode && checkedItems.length > 0 && (
            <div className="shrink-0 space-y-2 border-t border-amber-300/20 bg-[#15263e] px-3 py-2 text-[11px]">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-amber-100">
                  {checkedItems.length} selected · {bulkEligible.length} permitted to complete
                </span>
                <button type="button" onClick={() => {
                  setSelectedId(checkedItems[0]?.id || null);
                  setSelectionIndex(page.findIndex((item) => item.id === checkedItems[0]?.id));
                }} className="rounded-md border border-amber-300/40 px-2 py-1 text-amber-100">
                  Inspect first selected
                </button>
              </div>
              {batchItems.length > 0 && typeof onBulkComplete === 'function' && (
                <form aria-label="Complete selected source work"
                  className="flex flex-wrap items-center gap-2"
                  onSubmit={async (event) => {
                    event.preventDefault();
                    if (!bulkNote.trim() || bulkCompleting || workUpdating) return;
                    const result = await onBulkComplete(batchItems, bulkNote);
                    if (result) {
                      const done = new Set(result.completedIds);
                      setCheckedIds((before) => before.filter((id) => !done.has(id)));
                      if (!result.failedIds.length) setBulkNote('');
                    }
                  }}>
                  <input aria-label="Bulk completion evidence" value={bulkNote}
                    maxLength={1000} required
                    onChange={(event) => setBulkNote(event.target.value)}
                    placeholder="Evidence for each selected completion"
                    className="min-w-[140px] flex-1 rounded-md border border-white/15 bg-[#0a1628] px-2 py-2 text-xs"/>
                  <button type="submit" disabled={!bulkNote.trim() || workUpdating || bulkCompleting}
                    className="rounded-md bg-amber-300 px-3 py-2 font-semibold text-slate-950 disabled:opacity-50">
                    {bulkCompleting ? 'Confirming source work…' : 'Complete up to ' + batchItems.length}
                  </button>
                </form>
              )}
              <p className="text-[10px] text-slate-400">
                Each source rechecks IAM and commits separately. Batch limit: 25; any failures remain selected.
              </p>
            </div>
          )}
          </div>
          {selected && (
            <aside aria-label="Attention detail rail"
              className="relative h-full min-h-0 min-w-0 w-full overflow-y-auto overscroll-contain border-t border-amber-300/25 bg-[#182842] px-4 py-3 md:border-l md:border-t-0 md:px-5 md:py-4">
          <div className="flex items-center justify-between gap-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-200">
              Work detail · {label(selected.sourceModule)}
            </h3>
            <button type="button" onClick={() => setSelectedId(null)}
              aria-label="Close attention detail" className="rounded-lg p-1 text-slate-300 hover:bg-white/10">
              <X size={16}/>
            </button>
          </div>
          <div className="mt-2 flex flex-wrap gap-1.5">
            <span className={'inline-flex items-center gap-1 rounded-md border px-2 py-1 text-[11px] font-bold ' + severityFor(selected).chip}>
              <span aria-hidden="true" className={'h-1.5 w-1.5 rounded-full ' + severityFor(selected).dot}/>
              {severityFor(selected).label} severity
            </span>
            {selected.isOverdue && <span className="rounded-md border border-orange-300/40 px-2 py-1 text-[11px] text-orange-100">
              {selected.priority} source priority · deadline passed
            </span>}
          </div>
          <p className="mt-2 text-sm font-semibold">{selected.title}</p>
          {selected.summary && <p className="mt-1 text-xs leading-5 text-slate-300">{selected.summary}</p>}
          <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
            <div><dt className="text-slate-400">Reason prioritised</dt><dd>{selected.whyRanked}</dd></div>
            <div><dt className="text-slate-400">Priority score</dt><dd>{selected.urgencyScore}/100</dd></div>
            <div><dt className="text-slate-400">Deadline</dt><dd>{dueLabel(selected.dueAt)}</dd></div>
            <div><dt className="text-slate-400">Source status</dt><dd>{sourceStatus(selected)}</dd></div>
            <div><dt className="text-slate-400">SLA</dt><dd>{selected.slaBreachAt ? dueLabel(selected.slaBreachAt) : 'Not supplied by source'}</dd></div>
            <div><dt className="text-slate-400">Owner</dt>
              <dd>{selected.assigneeId
                ? 'Principal recorded; name not supplied by source'
                : 'Not supplied by source'}</dd>
            </div>
          </dl>
          <details aria-label="Technical source details"
            className="mt-3 rounded-md border border-white/10 bg-black/10 px-3 py-2 text-xs">
            <summary className="cursor-pointer font-semibold text-amber-200">Technical source details</summary>
            <dl className="mt-3 grid grid-cols-[6rem_minmax(0,1fr)] gap-2 text-slate-300">
              <dt>Source</dt><dd>{label(selected.sourceModule)}</dd>
              <dt>Record</dt><dd className="break-all">{selected.sourceRecordId}</dd>
              <dt>Requester</dt><dd className="break-all">{selected.requesterId || 'Not supplied by source'}</dd>
              <dt>Assignee</dt><dd className="break-all">{selected.assigneeId || 'Not supplied by source'}</dd>
            </dl>
          </details>
          {canComplete && (
            <form className="mt-4 space-y-2 rounded-lg border border-amber-300/20 bg-[#102034] p-3"
              onSubmit={async (event) => {
                event.preventDefault();
                const receiptPending = Boolean(selectedCompletionReceipt);
                if ((!receiptPending && !completionNote.trim()) || completingId
                  || (receiptPending && !completionReadbackReady)) return;
                const note = receiptPending
                  ? selectedCompletionReceipt.completionNote : completionNote;
                const confirmed = await onCompleteWork(selected, note);
                if (confirmed === true) {
                  setCompletionNotice('Completion confirmed by EOS and a fresh authorized work readback.');
                  setSelectedId(null);
                  setCompletionNote('');
                }
              }}>
              <label htmlFor="attention-completion-evidence" className="block text-xs font-semibold text-amber-100">
                {selectedCompletionReceipt ? 'Accepted completion evidence' : 'Complete source work'}
              </label>
              <textarea ref={completionRef} id="attention-completion-evidence"
                value={selectedCompletionReceipt
                  ? selectedCompletionReceipt.completionNote : completionNote}
                maxLength={1000} rows={2} required={!selectedCompletionReceipt}
                readOnly={!!selectedCompletionReceipt}
                disabled={!!completingId}
                onChange={(event) => setCompletionNote(event.target.value)}
                placeholder="Record what was completed and the evidence for this decision"
                className="w-full rounded-md border border-white/20 bg-[#09162a] px-2 py-1.5 text-xs text-white"/>
              <button type="submit"
                disabled={!!completingId || workUpdating
                  || (selectedCompletionReceipt ? !completionReadbackReady : !completionNote.trim())}
                className="rounded-md bg-amber-300 px-3 py-2 text-xs font-bold text-slate-950 disabled:opacity-50">
                {completingId === selected.id
                  ? selectedCompletionReceipt ? 'Checking source readback…' : 'Confirming with EOS…'
                  : selectedCompletionReceipt
                    ? completionReadbackReady ? 'Reconcile completion' : 'Awaiting source readback'
                    : 'Confirm completion'}
              </button>
              <p className="text-[10px] text-slate-400">
                {selectedCompletionReceipt
                  ? 'EOS already accepted this evidence. Reconciliation reads source state only; it will not send another command.'
                  : 'EOS rechecks your permission and saves completion in the owning module.'}
              </p>
            </form>
          )}
          {completionError && <p role="alert" className="mt-2 text-xs text-rose-200">{completionError}</p>}
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
      {mode === 'LIST' && completionNotice && <p role="status" className="shrink-0 border-t border-emerald-300/20 bg-[#12302d] px-4 py-2 text-xs text-emerald-100">{completionNotice}</p>}
      {mode !== 'CREATE' && (
      <footer className="shrink-0 border-t border-white/10 bg-[#14243d] px-4 py-2.5">
        <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
          <span>{page.length} loaded · {feed.filteredTotal} matching in last verified view · {feed.counts.active} active in verified sources</span>
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
      )}
    </div>
  );
}

// ARTIFACT: client/src/components/attention/DailyAttentionWorkspace.jsx
// VERSION: v3.14.0-CRM-DIRECT-SAVED-DRAFT
// AUTHORITY BOUNDARY: EOS-attested rows; completion reuses source-owned commands.
 // TENANT POSTURE: Exact current-session authorised AttentionItem response.
 // FAIL-CLOSED POSTURE: Unrepresented modules never display verified-cleared.
 // FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 // END OF WILSY OS SOVEREIGN ARTIFACT
