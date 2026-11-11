/**
 * TITLE: WILSY OS Authenticated Daily Attention Centre
 * VERSION: v2.3.0-SOURCE-OWNED-EXECUTIVE-COMPLETION
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Interactive notification-bell entry to exact-tenant, authorised
 *          EOS My Work triage, with actionable navigation to source-owned
 *          completion. Does not masquerade task counts as unread notifications.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/chrome/WilsyDailyAttentionCentre.jsx
 * COLLABORATION / OWNERSHIP: Python EOS /api/my-work owns work visibility;
 *                            App.jsx owns authenticated chrome and navigation.
 * CERTIFICATION / UPDATE DATE: 2026-11-11
 * CHANGELOG: v2.3.0-SOURCE-OWNED-EXECUTIVE-COMPLETION checks
 *            EOS action availability independently, delegates Operations
 *            and Intelligence completion to source-owned authenticated POSTs,
 *            and invalidates current My Work only after source confirmation.
 *            v2.2.0-STABLE-ATTENTION-REVALIDATION keeps verified
 *            same-session work visible during refresh and preserves search
 *            focus, row selection and the detail rail across reads.
 *            v2.1.1-FULL-SCOPE-ATTENTION-CALENDAR passes the
 *            independently verified current My Work snapshot into Calendar,
 *            excluding filtered attention-page truncation from deadline view.
 *            v2.1.0-WIDE-AUTHORISED-EXECUTIVE-COCKPIT gives
 *            authenticated triage a responsive 920px cockpit with room for
 *            a 390px detail rail; isolated historic fixtures keep 460px.
 *            Floating clamp/docking uses actual matching panel width.
 *            v2.0.0-AUTHENTICATED-ATTENTION-WORKSPACE mounts a
 *            governed dense inbox/briefing/detail UI only after the authenticated
 *            AttentionItem feed validates; isolated My Work fixtures retain
 *            their historical verification seam and source-owned navigation.
 *            v1.9.2-LEGACY-EMPTY-COPY-COMPATIBILITY retains
 *            the proven isolated legacy empty-state copy, while real
 *            authenticated feeds add explicit omitted-source context.
 *            v1.9.1-FULL-FEED-RECOVERY-BACKOFF resets the retry
 *            schedule only after BOTH source aggregation and the AttentionItem
 *            read succeed, preventing repeated short retries on prolonged 503.
 *            v1.9.0-SAFE-ATTENTION-READ-RECOVERY preserves the Mac recovery contract in the
 *            integrated AttentionItem feed: transient failures recover via
 *            bounded delayed revalidation, browser reconnect and visibility;
 *            401/403 and malformed source evidence remain fail-closed.
 *            v1.8.1-EXACT-ATTENTION-COVERAGE-RESET shows all non-represented sources
 *            without inferring licence or permission, and clears obsolete
 *            pagination state whenever the source or filter changes.
 *            v1.8.0-SERVER-AUTHORISED-ATTENTION-TRIAGE consumes EOS-authorised cursor-paginated
 *            AttentionItems for real server-side triage and source selection;
 *            an unavailable feed cannot masquerade as a cleared enterprise
 *            queue. Direct OPEN navigation retains source-owned authority.
 *            v1.7.0-EXECUTIVE-TRIAGE-INTENT turns the four
 *            EOS-backed filter controls into an explained triage decision:
 *            per-filter verified counts, an explicit source-safe next action,
 *            and an empty-state recovery path without fabricated work.
 *            v1.6.0-OPERATIONAL-ATTENTION-HANDOFF gives zero-work
 *            Operations sessions a real source-owned create/manage entry,
 *            provides one-click work-item handoff without hidden expansion,
 *            labels source selection as filtering (not an executable command),
 *            and removes the unrelated HR shortcut from non-HR coverage.
 *            v1.5.1-VERIFIED-ZERO-VS-UNAVAILABLE distinguishes
 *            EOS-verified zero active work from a truly unavailable work
 *            count in the accessible bell label; a zero count never draws
 *            a decorative unread badge or invents notifications.
 *            v1.5.0-EXACT-SESSION-ATTENTION-COUNT-CURRENTNESS gives the
 *            independently source-confirmed current global count precedence
 *            over a formerly open panel's stale snapshot, clears stale closed
 *            projections and revalidates open panels on source invalidation
 *            via the same authenticated EOS work-read coordinator.
 *            v1.4.0-EOS-SOURCE-COVERAGE uses the canonical projection contract
 *            to derive source options and empty-state wording from EOS coverage;
 *            no empty queue is routed automatically into HR.
 *            v1.3.0-CALENDAR-EXPLICIT-DISMISSAL makes the date view explicitly dismissible
 *            with a prominent Close calendar action and layered Escape
 *            contract: calendar first, panel second. Work state is retained.
 *            v1.2.0-PORTALLED-VIEWPORT-FLOATING portals the floating panel beyond the
 *            backdrop-filtered app header, anchors dock position to the bell
 *            and keeps outside dismissal correct for portalled UI.
 *            v1.1.0-FLOATING-WORK-CALENDAR adds an accessible movable/dockable work panel,
 *            a real EOS work deadline calendar, and action handoffs to
 *            source-authorised My Work and HR workflows.
 *            v1.0.1-STRICT-PROJECTION-DATE-VALIDATION also rejects
 *            malformed EOS snapshot timestamps before UI date formatting.
 *            v1.0.0-EOS-AUTHORISED-DAILY-ATTENTION implements on-demand work
 *            fetching, scoped validation, due/priority/source triage, search,
 *            keyboard/outside dismissal, safe refresh, detail expansion and
 *            source-owned action navigation.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No browser-persisted queue, fabricated notices,
 *                            unread receipts, or client-derived permissions.
 * TENANT BOUNDARY: Rejects missing/mismatched tenant projections and stale
 *                  in-flight reads on authenticated scope changes.
 * AUTHORITY BOUNDARY: Read-only projection. Only EOS source services may
 *                     complete, approve, assign or acknowledge work.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
 */

import React, { useContext, useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import {
  AlertTriangle, ArrowRight, Bell, CalendarDays, CheckCircle2,
  ChevronDown, Clock3, Grip, Pin, RefreshCw, Search, X,
} from 'lucide-react';
import api from '../../services/api.js';
import AuthContext from '../../contexts/authContext.jsx';
import {
  currentUnifiedMyWorkScope,
  readUnifiedMyWork,
  subscribeUnifiedMyWork, invalidateUnifiedMyWork,
} from '../../services/unifiedMyWorkSync.js';
import {
  assertUnifiedMyWorkProjection,
  unifiedMyWorkSourceLabel,
} from '../../services/unifiedMyWorkProjection.js';
import WilsyWorkDeadlineCalendar from './WilsyWorkDeadlineCalendar.jsx';
import {
  readAttentionFeed, readAttentionSourceActions, completeAttentionSourceWork,
} from '../../services/attentionFeedClient.js';
import DailyAttentionWorkspace from '../attention/DailyAttentionWorkspace.jsx';

const FILTERS = Object.freeze([
  { id: 'ALL', label: 'All work', purpose: 'Review every active item currently included by EOS.' },
  { id: 'OVERDUE', label: 'Overdue', purpose: 'Address missed deadlines in the authorised queue.' },
  { id: 'TODAY', label: 'Due today', purpose: 'Act on commitments due before the working day ends.' },
  { id: 'HIGH', label: 'High priority', purpose: 'Review critical and high-priority work first.' },
]);

const urgencyOrder = (item) => item.is_overdue ? 0
  : ['CRITICAL', 'HIGH'].includes(item.priority) ? 1 : 2;
const nextWorkItem = (items) => [...items].sort((a, b) => {
  const urgency = urgencyOrder(a) - urgencyOrder(b);
  if (urgency) return urgency;
  const first = a.due_at ? Date.parse(a.due_at) : Number.POSITIVE_INFINITY;
  const second = b.due_at ? Date.parse(b.due_at) : Number.POSITIVE_INFINITY;
  const due = (Number.isFinite(first) ? first : Number.POSITIVE_INFINITY)
    - (Number.isFinite(second) ? second : Number.POSITIVE_INFINITY);
  return Number.isNaN(due) ? 0 : due;
})[0] || null;

const validCount = (value) => Number.isSafeInteger(value) && value >= 0;

const dueToday = (dateValue) => {
  if (!dateValue) return false;
  const due = new Date(dateValue);
  return !Number.isNaN(due.getTime()) && due.toDateString() === new Date().toDateString();
};

const dueLabel = (value) => {
  if (!value) return 'No due date';
  const due = new Date(value);
  return Number.isNaN(due.getTime())
    ? 'Due date unavailable'
    : due.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
};

/**
 * Preserve the established component export while delegating validation to the
 * shared read-only projection contract.
 *
 * @description Validates one EOS work snapshot and exact requested tenant.
 * @collaboration Headquarters Daily Brief and Daily Attention contract tests.
 * @institutional Compatibility export only; it grants no permission.
 * @param {Object} payload EOS unified My Work response body.
 * @param {string} tenantId Exact authenticated tenant.
 * @returns {Object} The same validated projection.
 * @throws {Error} Stable contract code when the projection is invalid.
 */
export function assertAttentionProjection(payload, tenantId) {
  return assertUnifiedMyWorkProjection(payload, { tenantId });
}

/**
 * @description Render authenticated EOS work and hand commands to source owners.
 * @collaboration App.jsx supplies exact tenant and source navigation callbacks.
 * @institutional The panel is a read-only projection; source metadata is
 * presentation scope, and source services retain all command authority.
 * @param {Object} props Authenticated chrome-only projection and callbacks.
 * @param {string|undefined} props.tenantId Exact current tenant from auth.
 * @param {boolean} props.systemServicesWorkspace System workspace exclusion.
 * @param {number|null} props.activeCount EOS-derived active work, NOT unread.
 * @param {boolean} props.open Whether the panel is expanded.
 * @param {Function} props.onToggle Toggles the panel.
 * @param {Function} props.onClose Dismisses the panel.
 * @param {Function} props.onOpenWork Navigates to canonical My Work commands.
 * @param {Function} props.onOpenWorkforce Navigates into governed HR workspace.
 * @param {Function} props.onOpenOperations Navigates to source-owned Operations work management.
 * @returns {JSX.Element} Accessible daily attention projection.
 */
export default function WilsyDailyAttentionCentre({
  tenantId,
  systemServicesWorkspace = false,
  activeCount = null,
  open,
  onToggle,
  onClose,
  onOpenWork,
  onOpenWorkforce,
  onOpenOperations,
}) {
  const auth = useContext(AuthContext);
  const workScope = currentUnifiedMyWorkScope(auth, tenantId);
  const rootRef = useRef(null);
  const panelRef = useRef(null);
  const dragRef = useRef(null);
  const [projection, setProjection] = useState(null);
  const [status, setStatus] = useState('IDLE');
  const [workError, setWorkError] = useState('');
  const [recoveryAttempts, setRecoveryAttempts] = useState(0);
  const [attentionFeed, setAttentionFeed] = useState(null);
  const [attentionStatus, setAttentionStatus] = useState('IDLE');
  const [attentionError, setAttentionError] = useState('');
  const [sourceActions, setSourceActions] = useState({});
  const [sourceActionsScope, setSourceActionsScope] = useState(null);
  const [completionId, setCompletionId] = useState(null);
  const [completionError, setCompletionError] = useState('');
  const [loadingMore, setLoadingMore] = useState(false);
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const feedGenerationRef = useRef(0);
  const verifiedProjectionScopeRef = useRef(null);
  const verifiedAttentionScopeRef = useRef(null);
  const liveScopeKey = workScope && tenantId && auth?.user?.id
    ? [workScope, tenantId, auth.user.id].join('::') : null;
  const [refreshId, setRefreshId] = useState(0);
  const [filter, setFilter] = useState('ALL');
  const [source, setSource] = useState('ALL');
  const [query, setQuery] = useState('');
  const [expanded, setExpanded] = useState(null);
  const [view, setView] = useState('WORK');
  const [floating, setFloating] = useState(null);
  const [docked, setDocked] = useState({ right: 16, top: 72 });

  useEffect(() => {
    setProjection(null);
    verifiedProjectionScopeRef.current = null;
    verifiedAttentionScopeRef.current = null;
    setStatus('IDLE');
    setWorkError('');
    setRecoveryAttempts(0);
    setAttentionFeed(null);
    setAttentionStatus('IDLE');
    setAttentionError('');
    setSourceActions({});
    setSourceActionsScope(null);
    setCompletionId(null);
    setCompletionError('');
    setLoadingMore(false);
    setFilter('ALL');
    setSource('ALL');
    setQuery('');
    setExpanded(null);
    setView('WORK');
    setFloating(null);
  }, [tenantId, systemServicesWorkspace]);

  useEffect(() => {
    if (!open) {
      // A closed panel must not override a freshly verified global work count
      // with its previous, potentially stale list or summary.
      setProjection(null);
      setStatus('IDLE');
      return undefined;
    }
    if (!tenantId || systemServicesWorkspace || (auth && !workScope)) {
      setProjection(null);
      setStatus('UNAVAILABLE');
      return undefined;
    }
    let active = true;
    const controller = new AbortController();
    if (!liveScopeKey || verifiedProjectionScopeRef.current !== liveScopeKey) {
      setProjection(null);
      setAttentionFeed(null);
      verifiedAttentionScopeRef.current = null;
      setStatus('LOADING');
    }
    setWorkError('');

    // Authenticated production reads share the exact current session and
    // source validator with global chrome. Isolated presentational fixtures
    // without an AuthProvider retain their existing mocked read seam.
    const request = workScope
      ? readUnifiedMyWork(
          workScope,
          { tenantId, principalId: auth.user.id },
          { signal: controller.signal, force: true },
        )
      : api.get('/my-work', { forceNetworkRetry: true })
          .then((response) => assertAttentionProjection(response?.data, tenantId));
    request
      .then((verified) => {
        if (active) {
          setProjection(verified);
          verifiedProjectionScopeRef.current = liveScopeKey;
          setWorkError('');
          if (!workScope) setRecoveryAttempts(0);
          setStatus('READY');
        }
      })
      .catch((error) => {
        if (active) {
          setProjection(null);
          setAttentionFeed(null);
          verifiedProjectionScopeRef.current = null;
          verifiedAttentionScopeRef.current = null;
          const http = error?.response?.status;
          setWorkError(http === 401 || http === 403
            ? 'ATTENTION_ACCESS_DENIED'
            : [502, 503, 504].includes(http)
              || ['ERR_NETWORK', 'ECONNABORTED', 'ETIMEDOUT'].includes(error?.code)
              ? 'ATTENTION_CONNECTION_UNAVAILABLE'
              : 'ATTENTION_PROJECTION_UNVERIFIED');
          setStatus('UNAVAILABLE');
        }
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [open, tenantId, systemServicesWorkspace, refreshId, workScope, liveScopeKey]);

  useEffect(() => {
    if (!open || !workScope) return undefined;
    return subscribeUnifiedMyWork(workScope, () => {
      setRefreshId((id) => id + 1);
    });
  }, [open, workScope]);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedQuery(query), 200);
    return () => window.clearTimeout(timer);
  }, [query]);

  // Authenticated sessions use the EOS AttentionItem feed as the triage list.
  // Existing isolated UI fixtures still exercise the canonical My Work seam.
  useEffect(() => {
    if (!open || !workScope || status !== 'READY' || !projection) {
      setAttentionFeed(null);
      setAttentionStatus('IDLE');
      return undefined;
    }
    const controller = new AbortController();
    const generation = ++feedGenerationRef.current;
    if (verifiedAttentionScopeRef.current !== liveScopeKey) setAttentionFeed(null);
    setLoadingMore(false);
    setAttentionStatus('LOADING');
    setAttentionError('');
    const selectedView = {
      ALL: 'active', OVERDUE: 'overdue', TODAY: 'due_today', HIGH: 'high_priority',
    }[filter];
    readAttentionFeed(
      { tenantId, principalId: auth.user.id },
      {
        view: selectedView,
        sources: source !== 'ALL' ? source : undefined,
        q: debouncedQuery,
        limit: 50,
        signal: controller.signal,
      },
    ).then((verified) => {
      if (controller.signal.aborted || generation !== feedGenerationRef.current) return;
      const included = projection.sources_included || [];
      if (
        verified.coverage.admittedSources.length !== included.length
        || included.some((item) => !verified.coverage.admittedSources.includes(item))
      ) throw new Error('ATTENTION_SOURCE_COVERAGE_MISMATCH');
      setAttentionFeed(verified);
      verifiedAttentionScopeRef.current = liveScopeKey;
      setRecoveryAttempts(0);
      setAttentionStatus('READY');
    }).catch((error) => {
      if (controller.signal.aborted || generation !== feedGenerationRef.current) return;
      setAttentionFeed(null);
      verifiedAttentionScopeRef.current = null;
      const http = error?.response?.status;
      setAttentionError(http === 401 || http === 403
        ? 'ATTENTION_ACCESS_DENIED'
        : [502, 503, 504].includes(http)
          || ['ERR_NETWORK', 'ECONNABORTED', 'ETIMEDOUT'].includes(error?.code)
            ? 'ATTENTION_CONNECTION_UNAVAILABLE'
            : error?.message?.startsWith('ATTENTION_')
              ? error.message : 'ATTENTION_SOURCE_READ_UNVERIFIED');
      setAttentionStatus('UNAVAILABLE');
    });
    return () => {
      controller.abort();
      feedGenerationRef.current += 1;
    };
  }, [
    open, workScope, status, projection, tenantId, auth?.user?.id,
    filter, source, debouncedQuery, refreshId, liveScopeKey,
  ]);

  // A failed source is never promoted to empty; revalidate transient outages
  // only in the same current AuthProvider session. No auth denial is retried.
  useEffect(() => {
    if (!open || !workScope) return undefined;
    const transientFailure = (status === 'UNAVAILABLE'
      && workError === 'ATTENTION_CONNECTION_UNAVAILABLE')
      || (attentionStatus === 'UNAVAILABLE'
        && attentionError === 'ATTENTION_CONNECTION_UNAVAILABLE');
    if (!transientFailure) return undefined;
    const refresh = () => {
      setRecoveryAttempts((previous) => previous + 1);
      setRefreshId((previous) => previous + 1);
    };
    const visible = () => {
      if (document.visibilityState === 'visible') refresh();
    };
    const delay = recoveryAttempts === 0 ? 1500
      : recoveryAttempts === 1 ? 5000 : 20000;
    const timer = window.setTimeout(refresh, delay);
    window.addEventListener('online', refresh);
    document.addEventListener('visibilitychange', visible);
    return () => {
      window.clearTimeout(timer);
      window.removeEventListener('online', refresh);
      document.removeEventListener('visibilitychange', visible);
    };
  }, [open, workScope, status, workError, attentionStatus, attentionError, recoveryAttempts]);

  // Optional command-availability read is separate from source visibility.
  // Its failure cannot confer an action or turn a verified work queue empty.
  useEffect(() => {
    if (!open || !workScope || status !== 'READY' || !projection) {
      setSourceActions({});
      setSourceActionsScope(null);
      return undefined;
    }
    let active = true;
    setSourceActions({});
    setSourceActionsScope(null);
    readAttentionSourceActions({ tenantId, principalId: auth.user.id })
      .then((actions) => {
        if (!active) return;
        setSourceActions(actions);
        setSourceActionsScope(liveScopeKey);
      })
      .catch(() => {
        if (!active) return;
        setSourceActions({});
        setSourceActionsScope(null);
      });
    return () => { active = false; };
  }, [open, workScope, status, projection, tenantId, auth?.user?.id, liveScopeKey]);

  const handleSourceCompletion = async (item, note) => {
    if (!workScope || attentionStatus !== 'READY' || status !== 'READY'
      || verifiedAttentionScopeRef.current !== liveScopeKey
      || sourceActionsScope !== liveScopeKey
      || !sourceActions[item?.sourceModule]?.includes('COMPLETE')
      || !attentionFeed?.items.some((row) => row.id === item.id)
      || completionId) return;
    setCompletionError('');
    setCompletionId(item.id);
    try {
      await completeAttentionSourceWork(item, note);
      invalidateUnifiedMyWork(workScope);
      setRefreshId((id) => id + 1);
    } catch (error) {
      const http = error?.response?.status;
      setCompletionError(http === 403 ? 'Source authorization denied this completion.'
        : http === 409 ? 'Work changed since inspection. Refresh and review again.'
          : http === 422 ? 'Completion evidence was rejected by its source.'
            : 'Source completion could not be confirmed. Refresh before retrying.');
    } finally {
      setCompletionId(null);
    }
  };

  const loadMoreAttention = () => {
    if (!workScope || !attentionFeed?.nextCursor || loadingMore) return;
    const generation = feedGenerationRef.current;
    const prior = attentionFeed;
    setLoadingMore(true);
    const selectedView = {
      ALL: 'active', OVERDUE: 'overdue', TODAY: 'due_today', HIGH: 'high_priority',
    }[filter];
    readAttentionFeed(
      { tenantId, principalId: auth.user.id },
      {
        view: selectedView,
        sources: source !== 'ALL' ? source : undefined,
        q: debouncedQuery,
        cursor: prior.nextCursor,
        limit: 50,
      },
    ).then((page) => {
      if (generation !== feedGenerationRef.current) return;
      if (
        page.filteredTotal !== prior.filteredTotal
        || page.counts.active !== prior.counts.active
        || page.coverage.admittedSources.join() !== prior.coverage.admittedSources.join()
      ) throw new Error('ATTENTION_PAGE_SOURCE_CHANGED');
      const already = new Set(prior.items.map((item) => item.id));
      if (page.items.some((item) => already.has(item.id))) {
        throw new Error('ATTENTION_PAGE_DUPLICATE');
      }
      setAttentionFeed({ ...page, items: [...prior.items, ...page.items] });
    }).catch(() => {
      if (generation !== feedGenerationRef.current) return;
      setAttentionError('ATTENTION_PAGE_REVALIDATION_FAILED');
    }).finally(() => {
      if (generation === feedGenerationRef.current) setLoadingMore(false);
    });
  };

  useEffect(() => {
    if (!open) return undefined;
    const handleKey = (event) => {
      if (event.key !== 'Escape') return;
      if (view === 'CALENDAR') {
        event.preventDefault();
        event.stopPropagation();
        setView('WORK');
        return;
      }
      onClose();
    };
    const handlePointer = (event) => {
      if (!rootRef.current?.contains(event.target) && !panelRef.current?.contains(event.target)) onClose();
    };
    document.addEventListener('keydown', handleKey);
    document.addEventListener('pointerdown', handlePointer);
    return () => {
      document.removeEventListener('keydown', handleKey);
      document.removeEventListener('pointerdown', handlePointer);
    };
  }, [open, onClose, view]);

  const items = workScope
    ? attentionFeed && verifiedAttentionScopeRef.current === liveScopeKey
      ? attentionFeed.items.map((item) => ({
          source_key: item.id,
          source: item.sourceModule,
          work_item_id: item.sourceRecordId,
          title: item.title,
          description: item.summary,
          priority: item.priority,
          status: item.status,
          due_at: item.dueAt,
          is_overdue: item.isOverdue,
          urgencyScore: item.urgencyScore,
          whyRanked: item.whyRanked,
        }))
      : []
    : projection?.items || [];
  const sourceIds = projection?.sources_included || [];
  const sourceOptions = sourceIds.map((id) => [id, unifiedMyWorkSourceLabel(id)]);
  const sourceLabels = sourceOptions.map(([, label]) => label);
  const operationsAdmitted = sourceIds.includes('OPERATIONS');
  const chosenSourceLabel = source === 'ALL' ? 'all admitted sources' : unifiedMyWorkSourceLabel(source);
  // A previously opened panel's read cannot outrank current EOS source
  // evidence received by the persistent global chrome.
  const verifiedCount = validCount(activeCount)
    ? activeCount
    : open && status === 'READY' ? projection.summary.active_count : null;
  const badgeCount = validCount(verifiedCount) && verifiedCount > 0 ? verifiedCount : null;
  const dueTodayCount = workScope && attentionFeed
    ? attentionFeed.counts.dueToday
    : items.filter((item) => dueToday(item.due_at)).length;
  const highCount = workScope && attentionFeed
    ? attentionFeed.counts.highPriority
    : items.filter((item) => ['CRITICAL', 'HIGH'].includes(item.priority)).length;
  const overdueCount = workScope && attentionFeed
    ? attentionFeed.counts.overdue
    : items.filter((item) => item.is_overdue).length;
  const activeTotal = workScope && attentionFeed
    ? attentionFeed.counts.active : items.length;
  const filterCounts = {
    ALL: activeTotal, OVERDUE: overdueCount, TODAY: dueTodayCount, HIGH: highCount,
  };

  useEffect(() => {
    if (projection && source !== 'ALL' && !projection.sources_included.includes(source)) {
      setSource('ALL');
    }
  }, [projection, source]);

  const filteredItems = useMemo(() => {
    if (workScope) return items;
    const phrase = query.trim().toLocaleLowerCase();
    return items.filter((item) => {
      if (filter === 'OVERDUE' && !item.is_overdue) return false;
      if (filter === 'TODAY' && !dueToday(item.due_at)) return false;
      if (filter === 'HIGH' && !['CRITICAL', 'HIGH'].includes(item.priority)) return false;
      if (source !== 'ALL' && item.source !== source) return false;
      if (!phrase) return true;
      return [
        item.title, item.description, item.status, item.priority,
        unifiedMyWorkSourceLabel(item.source), item.work_item_id,
      ].some((value) => typeof value === 'string'
        && value.toLocaleLowerCase().includes(phrase));
    });
  }, [items, filter, source, query, workScope]);
  const selectedFilter = FILTERS.find(({ id }) => id === filter) || FILTERS[0];
  const nextItem = nextWorkItem(filteredItems);
  const triageResult = nextItem
    ? 'Next: ' + nextItem.title + '. Source: ' + unifiedMyWorkSourceLabel(nextItem.source)
      + '. Due: ' + dueLabel(nextItem.due_at) + '.'
    : items.length === 0
      ? 'EOS has no active work in the admitted sources. This does not certify every business function is clear.'
      : 'No matching work in the current selection. Clear filters to review other authorised items.';

  // Render the movable surface outside header backdrop-filter/stacking contexts.
  useEffect(() => {
    if (!open) return undefined;
    const updateAnchor = () => {
      const anchor = rootRef.current?.getBoundingClientRect();
      if (!anchor) return;
      const width = Math.min(workScope ? 920 : 460, window.innerWidth - 32);
      setDocked({
        right: Math.max(8, Math.min(window.innerWidth - anchor.right,
          Math.max(8, window.innerWidth - width - 8))),
        top: Math.max(8, Math.min(anchor.bottom + 8, window.innerHeight - 88)),
      });
    };
    updateAnchor();
    window.addEventListener('resize', updateAnchor);
    return () => window.removeEventListener('resize', updateAnchor);
  }, [open, workScope]);

  // Floating position is a transient layout preference, not business state.
  const panelBounds = () => {
    const rect = panelRef.current?.getBoundingClientRect();
    return {
      x: rect?.left || 16, y: rect?.top || 72,
      width: rect?.width || Math.min(workScope ? 920 : 460, window.innerWidth - 32),
      height: rect?.height || Math.min(780, window.innerHeight - 80),
    };
  };
  const clamp = (x, y, w, h) => ({
    x: Math.max(8, Math.min(x, Math.max(8, window.innerWidth - w - 8))),
    y: Math.max(8, Math.min(y, Math.max(8, window.innerHeight - h - 8))),
  });
  const floatAtPanel = () => {
    const box = panelBounds();
    const pos = clamp(box.x, box.y, box.width, box.height);
    setFloating(pos);
    return pos;
  };
  const handlePointerDown = (event) => {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    const rect = panelBounds();
    dragRef.current = {
      id: event.pointerId, origin: floating || floatAtPanel(),
      x: event.clientX, y: event.clientY, w: rect.width, h: rect.height,
    };
    event.currentTarget.setPointerCapture?.(event.pointerId);
  };
  const handlePointerMove = (event) => {
    const drag = dragRef.current;
    if (!drag || drag.id !== event.pointerId) return;
    setFloating(clamp(drag.origin.x + event.clientX - drag.x,
      drag.origin.y + event.clientY - drag.y, drag.w, drag.h));
  };
  const handlePointerEnd = (event) => {
    if (dragRef.current?.id !== event.pointerId) return;
    dragRef.current = null;
    if (event.currentTarget.hasPointerCapture?.(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  };
  const handleDragKey = (event) => {
    const directions = { ArrowLeft: [-1, 0], ArrowRight: [1, 0],
      ArrowUp: [0, -1], ArrowDown: [0, 1] };
    const d = directions[event.key];
    if (!d) return;
    event.preventDefault();
    const bounds = panelBounds();
    const current = floating || floatAtPanel();
    const amount = event.shiftKey ? 40 : 16;
    setFloating(clamp(current.x + d[0] * amount,
      current.y + d[1] * amount, bounds.width, bounds.height));
  };
  useEffect(() => {
    if (!open || !floating) return undefined;
    const onResize = () => {
      const box = panelBounds();
      setFloating((before) => before && clamp(before.x, before.y, box.width, box.height));
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, [open, Boolean(floating)]);

  return (
    <div className="relative" ref={rootRef} data-wilsy-attention-centre="true">
      <button
        type="button"
        aria-label={validCount(verifiedCount)
          ? 'Open daily attention: ' + verifiedCount + ' active work items'
          : 'Open daily attention'}
        aria-haspopup="dialog"
        aria-expanded={Boolean(open)}
        onClick={onToggle}
        className="relative grid h-10 w-10 place-items-center rounded-full text-slate-300 transition hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300"
      >
        <Bell size={19} />
        {badgeCount !== null && (
          <span
            aria-label={badgeCount + ' active work items, not unread notifications'}
            className="absolute -right-1 -top-1 grid min-h-5 min-w-5 place-items-center rounded-full bg-amber-400 px-1 text-[10px] font-bold tabular-nums text-[#081326]"
          >
            {badgeCount > 99 ? '99+' : badgeCount}
          </span>
        )}
      </button>

      {open && createPortal(
        <section
          ref={panelRef}
          role="dialog"
          aria-label="Daily attention centre"
          data-floating={floating ? 'true' : 'false'}
          style={floating
            ? { position: 'fixed', left: floating.x, top: floating.y, right: 'auto' }
            : { position: 'fixed', right: docked.right, top: docked.top, left: 'auto' }}
          className={'fixed z-[90] flex max-h-[min(780px,calc(100vh-5rem))] flex-col overflow-hidden rounded-2xl border border-white/15 bg-[#101d32] text-slate-100 shadow-2xl shadow-black/60 ' +
            (workScope ? 'w-[min(920px,calc(100vw-2rem))]' : 'w-[min(460px,calc(100vw-2rem))]')}
        >
          <div className="flex shrink-0 items-start justify-between gap-3 border-b border-white/10 bg-[#14243d] px-5 py-4">
            <div>
              <div className="flex items-center gap-2">
                <Bell size={17} className="text-amber-300" />
                <h2 className="text-base font-semibold text-white">Daily attention</h2>
              </div>
              <p className="mt-1 text-xs leading-5 text-slate-400">
                Your authorised EOS work across business functions.
              </p>
            </div>
            <div className="flex items-center gap-1">
              <button type="button" aria-label="Move daily attention panel with pointer or arrow keys"
                title="Drag to move; arrow keys to reposition"
                onPointerDown={handlePointerDown} onPointerMove={handlePointerMove}
                onPointerUp={handlePointerEnd} onPointerCancel={handlePointerEnd}
                onKeyDown={handleDragKey} style={{ touchAction: 'none' }}
                className="cursor-grab rounded-lg p-2 text-slate-300 hover:bg-white/10 active:cursor-grabbing focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
                <Grip size={18}/>
              </button>
              <button type="button" aria-label={floating ? 'Dock daily attention panel' : 'Float daily attention panel'}
                onClick={() => { dragRef.current = null; floating ? setFloating(null) : floatAtPanel(); }}
                className="rounded-lg p-2 text-slate-300 hover:bg-white/10">
                <Pin size={17} className={floating ? 'text-amber-300' : ''}/>
              </button>
              <button type="button" aria-label="Close daily attention" onClick={onClose}
                className="rounded-lg p-2 text-slate-300 hover:bg-white/10"><X size={17}/></button>
            </div>
          </div>

          {(status === 'LOADING' || (status === 'READY' && workScope && attentionStatus === 'LOADING'
            && (!attentionFeed || verifiedAttentionScopeRef.current !== liveScopeKey))) && (
            <div role="status" className="flex items-center gap-2 px-5 py-8 text-sm text-amber-200">
              <RefreshCw size={16} className="animate-spin"/> Checking current work…
            </div>
          )}

          {(status === 'UNAVAILABLE' || (status === 'READY' && workScope && attentionStatus === 'UNAVAILABLE')) && (
            <div role="alert" className="space-y-3 px-5 py-6">
              <div className="flex items-center gap-2 font-medium text-rose-200">
                <AlertTriangle size={17}/> Work source unavailable
              </div>
              <p className="text-sm leading-6 text-slate-300">
                {(attentionError || workError) === 'ATTENTION_ACCESS_DENIED'
                  ? 'This session is not authorised for the requested attention source.'
                  : (attentionError || workError) === 'ATTENTION_CONNECTION_UNAVAILABLE'
                    ? 'EOS is temporarily unavailable. Recovery retries automatically; no stale business work is presented.'
                    : (attentionError || workError)
                      ? 'The authorised attention feed could not be verified. No cached or invented work is shown.'
                      : 'Current tenant authorisation or an EOS work source could not be verified. No cached or invented work is shown.'}
              </p>
              {!systemServicesWorkspace && tenantId && (
                <button type="button" onClick={() => setRefreshId((id) => id + 1)}
                  className="rounded-lg border border-white/20 px-3 py-2 text-xs hover:bg-white/10">
                  Retry authorised read
                </button>
              )}
            </div>
          )}

          {status === 'READY' && workScope && attentionFeed
            && verifiedProjectionScopeRef.current === liveScopeKey
            && verifiedAttentionScopeRef.current === liveScopeKey
            && ['READY', 'LOADING'].includes(attentionStatus) && (
            <div aria-busy={attentionStatus === 'LOADING'} className="min-h-0 flex flex-1 flex-col">
              {attentionStatus === 'LOADING' && (
                <p role="status" className="shrink-0 border-b border-amber-300/20 px-5 py-2 text-xs text-amber-200">
                  <RefreshCw size={12} className="mr-2 inline animate-spin"/>
                  Updating authorised work. Previous verified results remain visible until the new view is checked.
                </p>
              )}
            <DailyAttentionWorkspace
              key={liveScopeKey}
              feed={attentionFeed}
              calendarItems={projection.items}
              filter={filter}
              setFilter={setFilter}
              source={source}
              setSource={setSource}
              query={query}
              setQuery={setQuery}
              onRefresh={() => setRefreshId((id) => id + 1)}
              onOpenWork={onOpenWork}
              onOpenOperations={onOpenOperations}
              onOpenWorkforce={onOpenWorkforce}
              authorisedActions={sourceActionsScope === liveScopeKey ? sourceActions : {}}
              onCompleteWork={handleSourceCompletion}
              completingId={completionId}
              completionError={completionError}
              onLoadMore={loadMoreAttention}
              loadingMore={loadingMore}
              pageError={attentionError === 'ATTENTION_PAGE_REVALIDATION_FAILED'}
            />
            </div>
          )}
          {status === 'READY' && !workScope && (
            <>
              <div className="shrink-0 border-b border-white/10 px-4 pb-3 pt-4">
                <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                  <div role="tablist" aria-label="Daily attention views" className="flex items-center gap-2">
                    <button type="button" role="tab" aria-selected={view === 'WORK'}
                      onClick={() => setView('WORK')}
                      className={'rounded-lg px-3 py-2 text-xs font-semibold ' +
                        (view === 'WORK' ? 'bg-amber-300 text-[#081326]' : 'text-slate-300 hover:bg-white/10')}>
                      Work list
                    </button>
                    <button type="button" role="tab" aria-selected={view === 'CALENDAR'}
                      onClick={() => setView('CALENDAR')}
                      className={'inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold ' +
                        (view === 'CALENDAR' ? 'bg-amber-300 text-[#081326]' : 'text-slate-300 hover:bg-white/10')}>
                      <CalendarDays size={14}/> Calendar
                    </button>
                  </div>
                  {view === 'CALENDAR' && (
                    <button type="button" aria-label="Close calendar and return to work list"
                      onClick={() => setView('WORK')}
                      className="inline-flex min-h-10 items-center gap-1.5 rounded-lg border border-amber-300/40 px-3 py-2 text-xs font-semibold text-amber-100 hover:bg-amber-300/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
                      <X size={15}/> Close calendar
                    </button>
                  )}
                </div>
                <div className="flex flex-wrap gap-2" aria-label="Verified current-source workload">
                  <Stat label="Active" value={activeTotal} />
                  <Stat label="Overdue" value={overdueCount} urgent={overdueCount > 0}/>
                  <Stat label="Due today" value={dueTodayCount}/>
                  <Stat label="High priority" value={highCount}/>
                </div>
                {workScope && attentionFeed && (
                  <p className="mt-2 text-[10px] leading-5 text-slate-400">
                    Verified sources: {attentionFeed.sources.map((entry) =>
                      entry.moduleId + ' (' + entry.state + ')').join(', ') || 'none'}.
                    Not represented in this session: {attentionFeed.coverage.notRepresentedSources.join(', ') || 'none'}.
                    No omitted source is assumed licensed or authorised.
                    This is not an enterprise-wide clearance.
                  </p>
                )}
                <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
                  <p className="text-[11px] text-slate-400">{highCount} high-priority items in authorised sources</p>
                  <button type="button" onClick={() => setRefreshId((id) => id + 1)}
                    className="flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs text-amber-200 hover:bg-white/10">
                    <RefreshCw size={13}/> Refresh
                  </button>
                </div>
                {view === 'WORK' && (<>
                  <div role="group" aria-label="Filter daily attention" className="mt-3 flex flex-wrap gap-1.5">
                    {FILTERS.map(({ id, label }) => (
                      <button key={id} type="button" aria-pressed={filter === id}
                        title={FILTERS.find((choice) => choice.id === id)?.purpose}
                        onClick={() => { setFilter(id); setExpanded(null); }}
                        className={'rounded-full border px-2.5 py-1.5 text-[11px] font-medium transition ' +
                          (filter === id
                            ? 'border-amber-300/40 bg-amber-300/15 text-amber-100'
                            : 'border-white/10 text-slate-300 hover:bg-white/10')}
                      >{label}<span aria-hidden="true" className="ml-1.5 tabular-nums opacity-70">{filterCounts[id]}</span></button>
                    ))}
                  </div>
                  <div className="mt-3 flex gap-2">
                    <label className="flex min-w-0 flex-1 items-center gap-2 rounded-lg border border-white/15 bg-[#0b1729] px-2.5">
                      <Search size={15} className="shrink-0 text-slate-500"/>
                      <input type="search" aria-label="Search authorised work" value={query}
                        onChange={(event) => setQuery(event.target.value)}
                        placeholder="Search your work"
                        className="h-9 w-full min-w-0 bg-transparent text-xs text-white outline-none placeholder:text-slate-500"/>
                    </label>
                    <label className="relative flex min-w-0 items-center rounded-lg border border-white/15 bg-[#0b1729]" title="Filter existing EOS work; use an authorised work action to create or complete work">
                      <span className="sr-only">Work source</span>
                      <select aria-label="Filter work by source" value={source}
                        onChange={(event) => setSource(event.target.value)}
                        className="h-9 max-w-[45vw] appearance-none bg-transparent pl-2.5 pr-6 text-xs text-white outline-none sm:max-w-[160px]">
                        <option className="bg-[#101d32]" value="ALL">All included sources</option>
                        {sourceOptions.map(([id, label]) => (
                          <option className="bg-[#101d32]" key={id} value={id}>{label}</option>
                        ))}
                      </select>
                      <ChevronDown size={12} className="pointer-events-none absolute right-2 text-slate-400"/>
                    </label>
                  </div>
                  <section aria-label="Daily attention next decision" className="mt-3 rounded-xl border border-amber-300/20 bg-amber-300/[0.055] px-3 py-3">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <h3 className="text-xs font-semibold text-amber-100">{selectedFilter.label}: {workScope && attentionFeed ? attentionFeed.filteredTotal : filteredItems.length} to review</h3>
                        <p className="mt-1 text-[11px] leading-5 text-slate-300">{selectedFilter.purpose}</p>
                        <p className="mt-1 text-[11px] leading-5 text-slate-400" role="status">
                          {triageResult} Showing {chosenSourceLabel}.
                        </p>
                      </div>
                      {nextItem && (
                        <button type="button" onClick={() => onOpenWork(nextItem)}
                          aria-label={'Work next: ' + nextItem.title}
                          className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-amber-300 px-3 py-2 text-xs font-semibold text-[#081326] hover:bg-amber-200">
                          Work next <ArrowRight size={13}/>
                        </button>
                      )}

                    </div>
                  </section>
                  <p className="mt-2 text-[10px] text-slate-500">The source menu filters existing work. EOS owns creation, assignment and completion.</p>
                </>)}
              </div>

              <div className="min-h-0 flex-1 overflow-y-auto px-3 py-2" aria-live="polite">
                {view === 'CALENDAR' ? (
                  <WilsyWorkDeadlineCalendar items={items}
                    onOpenWork={onOpenWork} onOpenWorkforce={onOpenWorkforce}/>
                ) : filteredItems.length === 0 ? (
                  <div className="py-9 text-center">
                    <CheckCircle2 size={26} className="mx-auto text-emerald-300"/>
                    <p className="mt-3 text-sm font-medium text-white">
                      {items.length > 0
                        ? 'No work matches these filters'
                        : workScope && attentionFeed && attentionFeed.counts.active > 0
                          ? 'No work matches this view'
                          : workScope && attentionFeed && sourceIds.length > 0
                            ? 'Queue clear in verified sources — not across all WILSY modules'
                            : sourceIds.length > 0
                              ? 'No active work in the included sources'
                              : 'No work source was included in this session'}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">
                      {items.length > 0
                        ? 'Try another filter or search term.'
                        : workScope && attentionFeed && attentionFeed.counts.active > 0
                          ? 'Other source-authorised active work exists. Clear filters to review it.'
                          : sourceIds.length > 0
                            ? 'EOS returned no active work from ' + sourceLabels.join(', ') + '.'
                            : 'EOS returned no source projection. This is not evidence that every business queue is empty.'}
                    </p>
                    {(filter !== 'ALL' || source !== 'ALL' || query.trim()) && (
                      <button type="button" onClick={() => { setFilter('ALL'); setSource('ALL'); setQuery(''); }}
                        className="mt-4 rounded-lg border border-white/20 px-3 py-2 text-xs text-white hover:bg-white/10">
                        Clear filters
                      </button>
                    )}
                    {operationsAdmitted && onOpenOperations && (items.length === 0 || source === 'OPERATIONS' || (items.length > 0 && filteredItems.length === 0)) && (
                      <button type="button" onClick={onOpenOperations}
                        className="mt-4 inline-flex items-center gap-2 rounded-lg bg-amber-300 px-4 py-2.5 text-xs font-semibold text-[#081326] hover:bg-amber-200">
                        Create or manage Operations work <ArrowRight size={14}/>
                      </button>
                    )}
                  </div>
                ) : filteredItems.map((item) => (
                  <article key={item.source_key} className="mb-1 flex flex-col gap-1 rounded-lg border border-white/10 bg-white/[0.025] px-3 py-2">
                    <div className="flex items-center justify-between gap-2 text-[10px] uppercase tracking-[0.08em]">
                      <span className="font-semibold text-amber-200">{unifiedMyWorkSourceLabel(item.source)}</span>
                      <span className={item.is_overdue ? 'font-semibold text-rose-300' : 'text-slate-400'}>
                        {item.is_overdue ? 'Overdue' : item.priority + ' priority'}
                      </span>
                    </div>
                    <button type="button" aria-expanded={expanded === item.source_key}
                      onClick={() => setExpanded((previous) => previous === item.source_key ? null : item.source_key)}
                      className="mt-2 flex w-full items-start justify-between gap-2 text-left text-sm font-medium text-white hover:text-amber-100">
                      <span className="min-w-0 break-words">{item.title}</span>
                      <ChevronDown size={15} className={'mt-0.5 shrink-0 transition ' +
                        (expanded === item.source_key ? 'rotate-180' : '')}/>
                    </button>
                    {item.whyRanked && (
                      <p className="mt-1 text-[11px] text-amber-100/80">
                        Priority {item.urgencyScore}/100 · {item.whyRanked}
                      </p>
                    )}
                    <div className="mt-1 flex flex-wrap items-center gap-3 text-[11px] text-slate-400">
                      <span className="inline-flex items-center gap-1"><Clock3 size={12}/>{dueLabel(item.due_at)}</span>
                      <span>{item.status}</span>
                    </div>
                    <button type="button" onClick={() => onOpenWork(item)}
                      aria-label={'Act on ' + item.title + ' in My Work'}
                      className="mt-1 inline-flex w-fit items-center gap-2 rounded-lg border border-amber-300/50 px-3 py-1.5 text-xs font-semibold text-amber-100 hover:bg-amber-300/10">
                      Act in My Work <ArrowRight size={13}/>
                    </button>
                    {expanded === item.source_key && (
                      <div className="mt-3 border-t border-white/10 pt-3">
                        {item.description && (
                          <p className="mb-3 whitespace-pre-wrap break-words text-xs leading-5 text-slate-300">
                            {item.description}
                          </p>
                        )}
                        <p className="text-[11px] leading-5 text-slate-400">
                          Work actions are verified and recorded by the owning EOS service.
                        </p>
                        <button type="button" onClick={() => onOpenWork(item)}
                          className="mt-3 inline-flex items-center gap-2 rounded-lg bg-amber-300 px-3 py-2 text-xs font-semibold text-[#081326] hover:bg-amber-200">
                          Open in My Work <ArrowRight size={14}/>
                        </button>
                      </div>
                    )}
                  </article>
                ))}
                {workScope && attentionFeed?.nextCursor && (
                  <button type="button" disabled={loadingMore} onClick={loadMoreAttention}
                    className="mb-2 w-full rounded-lg border border-amber-300/40 px-3 py-2 text-xs font-semibold text-amber-100 hover:bg-white/10 disabled:opacity-50">
                    {loadingMore ? 'Loading authorised work…' : 'Load more authorised work'}
                  </button>
                )}
                {attentionError === 'ATTENTION_PAGE_REVALIDATION_FAILED' && (
                  <p role="alert" className="p-2 text-xs text-rose-200">
                    The current work page changed or failed verification. Refresh to reread EOS.
                  </p>
                )}
              </div>

              <div className="shrink-0 border-t border-white/10 bg-[#14243d] px-4 py-3">
                <div className="mb-2 flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-400">
                  <span>{items.length} of {activeTotal} active authorised items · {workScope && attentionFeed ? attentionFeed.filteredTotal + ' matching' : 'local projection'}</span>
                  <span>Included: {sourceLabels.length ? sourceLabels.join(', ') : 'no source projection'}</span>
                </div>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="min-w-0 text-[10px] text-slate-500">
                    Updated {new Date(projection.as_of).toLocaleTimeString([], {
                      hour: '2-digit', minute: '2-digit',
                    })}
                  </span>
                  <button type="button" aria-label="Open work deadline calendar"
                    onClick={() => setView('CALENDAR')}
                    className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-amber-200 hover:bg-white/10">
                    <CalendarDays size={14}/>
                    <span>Calendar · {new Date(projection.as_of).toLocaleTimeString([], {
                      hour: '2-digit', minute: '2-digit',
                    })}</span>
                  </button>
                </div>
                <div className="mt-2 flex gap-2">
                  {operationsAdmitted && onOpenOperations && (
                    <button type="button" onClick={onOpenOperations}
                      className="min-w-0 flex-1 rounded-lg border border-amber-300/40 px-3 py-2.5 text-xs font-semibold text-amber-100 hover:bg-white/10">
                      Manage Operations
                    </button>
                  )}
                  <button type="button" onClick={() => onOpenWork(null)}
                    className="flex min-w-0 flex-[2] items-center justify-center gap-2 rounded-lg bg-amber-300 px-3 py-2.5 text-xs font-semibold text-[#091426] hover:bg-amber-200">
                    Open My Work <ArrowRight size={14}/>
                  </button>
                </div>
              </div>
            </>
          )}
        </section>, document.body
      )}
    </div>
  );
}

/** Read-only summary tile for EOS-authorised active work. */
function Stat({ label, value, urgent = false }) {
  return (
    <div className="min-w-[90px] flex-1 rounded-lg border border-white/10 bg-white/[0.04] px-3 py-1.5">
      <p className="text-[10px] text-slate-400">{label}</p>
      <p className={'mt-1 text-lg font-semibold tabular-nums ' +
        (urgent ? 'text-rose-200' : 'text-white')}>{value}</p>
    </div>
  );
}

/*
 * ARTIFACT: WilsyDailyAttentionCentre.jsx
 * VERSION: v2.3.0-SOURCE-OWNED-EXECUTIVE-COMPLETION
 * AUTHORITY BOUNDARY: Authenticated read-only EOS work triage.
 * TENANT POSTURE: Exact tenant; only EOS-included source coverage is rendered.
 * FAIL-CLOSED POSTURE: Invalid, denied or unavailable sources show no fabricated items.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
