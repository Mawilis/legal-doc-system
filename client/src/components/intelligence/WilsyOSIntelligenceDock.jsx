/**
 * TITLE: WILSY OS Intelligence Dock and Movable AI Companion
 * VERSION: v4.14.0-EXPLICIT-AI-COMMERCIAL-READINESS
 * AUTHORITY: WILSY OS Core Governance; Python EOS owns all business authority.
 * EPITOME: Keep contextual intelligence alongside the operator's current work,
 * with a movable/minimizable launcher and preserved source-owned AI contracts.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/intelligence/WilsyOSIntelligenceDock.jsx
 * COLLABORATION / OWNERSHIP: App authenticated runtime gate, canonical api.js,
 * Legal advisory/deadline adapters and session-only conversation engines.
 * CERTIFICATION / UPDATE DATE: 2026-11-20
 * CHANGELOG: v4.14.0-EXPLICIT-AI-COMMERCIAL-READINESS separates EOS-verified work
 * from absent AI commercial capacity, disables only metered model requests
 * when the exact tenant has no AI entitlement and gives bounded guidance.
 * v4.13.1-OPERATOR-READABLE-SOURCE-STATUS replaces raw
 * Kennel machine tokens in the AI header with bounded, truthful human
 * availability language without altering diagnostic or authentication state.
 * v4.13.0-AUTHORIZED-HEADQUARTERS-WORK-FEED projects independently authorized
 * Headquarters My Work priorities as read-only task rows when AI commercial
 * admission is unavailable; tenant/principal and source-owned flags are
 * checked before display. These rows never enter the model from the browser.
 * v4.12.1-QUIET-REMEMBERED-CONSENT keeps previously accepted
 * usage consent collapsed into a discreet, reversible preference instead
 * of presenting the permission prompt again; rejects email values as first
 * names. v4.12.0-PERSONAL-CONVERSATION-AND-SCOPED-CONSENT greets new conversations from the authenticated
 * operator's first name and local time, remembers voluntary consent only
 * for the exact browser/tenant/principal/capacity and disclosure version,
 * and displays failed requests as errors, never fabricated AI turns.
 * v4.11.0-VERIFIED-SELECTED-TASK-FOCUS names the independently verified
 * selected task within the existing conversation context and empty-state
 * explanation, without trusting page-event titles or opening new cards.
 * v4.10.1-INDEPENDENT-AI-CONSENT-DISCLOSURE separates expandable usage
 * information from checkbox label activation, preventing an informational
 * disclosure action from inadvertently consenting to a metered request.
 * v4.10.0-VERIFIED-PROJECT-REASONING-LOCATOR forwards only a server-verified
 * project locator to Python EOS reasoning (never browser project facts), reuses
 * the exact locator on replay, blocks unverified project reasoning and revokes
 * in-flight turns when the observed workspace changes. Consent discloses that
 * EOS may pass verified source excerpts to the authorized model provider.
 * v4.9.1-CONVERSATION-FIRST-CONSENT removes the misleading generic readiness
 * messages, makes the active EOS workspace the conversational starting point,
 * and presents compact consent with an accessible optional disclosure. It
 * preserves metered opt-in and does not claim provider-grounded answers.
 * v4.9.0-VERIFIED-CONTEXT-INSPECTION reads independently admitted
 * workspace context only while open, validates exact scope and source locators,
 * cancels stale reads and exposes source citations and unavailable commercial
 * facts. Collapsible source details retain the mobile composer in view.
 * Inspection does not send source records to a model or issue authority.
 * CHANGELOG: v4.8.2-SESSION-OWNED-REASONING-CANCELLATION cancels obsolete
 * reasoning transport on scope exit and unmount, rejects late work by mount
 * generation, and releases submission state for the newly selected capacity.
 * Cancellation never claims to undo a server admission or quota reservation.
 * CHANGELOG: v4.8.1-EXACT-REPLAY-AI-CONSUMPTION preserves the exact EOS
 * idempotency key and canonical prompt after uncertain AI responses; retries
 * reuse the same admission instead of consuming capacity twice. A confirmed
 * response or changed tenant/session scope clears the replay anchor.
 * CHANGELOG: v4.8.0-ENTITLED-EOS-CONVERSATION sends general conversational
 * turns to the canonical Python EOS metered reasoning boundary only after
 * explicit usage consent. Client history is conversation continuity, not
 * verified workspace evidence. C1C legal authority remains independent.
 * CHANGELOG: v4.7.1-INDEPENDENT-KERNEL-HEALTH starts EOS kernel health independently
 * of optional finance evidence, publishes verified health immediately, and
 * enriches context only after independently verified optional evidence.
 * v4.7.0-MOVABLE-MINIMIZABLE-AI-COMPANION adds a distinct vector AI identity, pointer/keyboard
 * movement, viewport clamping, compact minimization and reset without navigation,
 * source commands, background modal interference or conversation resets.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; accessible controls.
 * SECURITY / PRIVACY POSTURE: Position and size are ephemeral React preferences;
 * no identity, message or layout is written to browser storage by these controls.
 * TENANT BOUNDARY: Existing exact tenant/principal/capacity scope remains owner
 * of all conversation/API state; layout controls never create permission.
 * AUTHORITY BOUNDARY: Companion presentation only; all source requests and
 * late-response guards remain unchanged. No route or workspace switch occurs.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
/**
 * HISTORICAL CHANGELOG
 * Change Log:
 *   2026-11-09 v4.6.1-STALE-OPERATOR-TURN-RENDER-GUARD discards responses, errors,
 *   replies and in-flight UI mutations from a superseded tenant, principal
 *   or business-capacity scope without inventing advisory authority.
 *   2026-11-09 v4.6.0-SESSION-OWNED-OPTIONAL-INTELLIGENCE cancels superseded EOS health probes,
 *   never presents a fabricated LIVE_EMPTY result as verified runtime health,
 *   and revokes transient conversation scope on logout, remount, tenant or
 *   capacity changes. Intelligence availability never gates Headquarters.
 *   2026-10-11 v4.5.0-LEGAL-DEADLINE-INTELLIGENCE-PROJECTION — Added an
 *     explicit-matter, explicit-time Core Legal deadline observation tab backed
 *     by D6B, with no AI, recommendation, reminder, mutation, or finance authority.
 *   2026-09-24 v4.4.1-LEGAL-AUTHORITY-AWARE-ARTIFACT-INTEGRITY — Aligned the sovereign artifact contract with
 *     canonical /kernel health transport, shared-api /ai/operator generic Ask,
 *     C1C legal-role routing, and session-only conversation history.
 *   2026-09-17 v4.4.0-LEGAL-AUTHORITY-AWARE-RUNTIME — Consumed only the
 *     bounded persisted session projection and replaced identity/tenant defaults
 *     with an explicit unresolved posture.
 *   2026-09-17 v4.3.1-C1E-R1D-A1-WILSY-OS-BRAND-CONSOLIDATION — Consolidated
 *     visible product branding to WILSY OS and source-gated secondary tenant identity.
 *   2026-09-17 v4.3.0-C1E-R1C-LEGAL-ADVISORY-PROJECTION — Added explicit
 *     evidence-backed Legal Advisory tab using only certified R1B operations;
 *     no C1E persistence, command affordances, or client-side reinterpretation.
 *   2026-09-13 v4.2.0-M14-P7-BILLING-INTELLIGENCE-EVIDENCE — Added optional
 *     canonical billing-intelligence evidence projection with explicit UTC
 *     snapshot request and explicit operator-context propagation; no client
 *     billing derivation or authorization inference.
 *   2026-08-06 v4.1.1-KENNEL-PHASE4 — Refined History Tab: Integrated New Thread & Sync 
 *     actions using dedicated CSS classes, achieving 10/10 UX parity.
 *   2026-08-06 v4.1.0-KENNEL-PHASE4 — Updated History Tab: Added manual "New Thread" and 
 *     "Sync/Refresh" actions. 
 *   2026-08-04 v4.0.0-KENNEL-PHASE4 — Replaced local buildWilsyOperatorIntelligence
 *     with backend POST /api/ai/operator; removed client engine import.
 *   2026-08-04 v3.1.0-KENNEL-PHASE1-FINAL — Raw fetch removed; api service only.
 *
 */
/* eslint-disable */

import React, { useCallback, useContext, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import {
  ArrowUpRight,
  FileCheck2,
  History,
  MessageSquareText,
  Minimize2,
  PanelRightOpen,
  SendHorizontal,
  ShieldCheck,
  Sparkles,
  GripVertical,
  Minus,
  RotateCcw,
  X,
} from 'lucide-react';
import api from '../../services/api.js'; // Sovereign HTTP client – forensic seals, tenant headers, auto refresh
import {
  executeWilsyAILegalServices,
  generateWilsyAILegalNextActions,
  readWilsyAILegalNextAction,
} from '../../services/wilsyAIAdvisoryApi.js';
import { getLegalMatterDeadlineIntelligence } from '../../services/legalMatterDeadlineService.js';
import {
  buildWilsyDynamicSuggestions,
  recordWilsyAISuggestionUsage,
} from './wilsyAIDynamicSuggestionEngine.js';
import {
  clearWilsyAIConversationThreads,
  resetWilsyAIConversationSession,
  createWilsyAIConversationThread,
  loadWilsyAIConversationThreads,
  persistWilsyAIConversationTurn,
} from './wilsyAIConversationHistoryEngine.js';
import styles from './WilsyOSIntelligenceDock.module.css';

/**
 * @function humanizeWilsyAIBackendToken
 * @description Maps kennel/backend tokens to operator-facing copy.
 * @collaboration Designed to make machine tokens human-readable for UI.
 */
function humanizeWilsyAIBackendToken(value = '') {
  const token = String(value || '').trim();
  const dictionary = {
    WILSY_AI_SOVEREIGN_CONTEXT_RESOLVED: 'Workspace intelligence ready',
    DETERMINISTIC_GOVERNANCE_REASONER: 'Live CRM setup guidance',
    EVIDENCE_COMPLETE: 'Checks complete',
    GOVERNANCE_AI_TIER: 'Governance guidance available',
    GOVERNANCE_AI_TIER_AVAILABLE_FOR_PACKAGING: 'Ready for workflow packaging',
    CORE_INTELLIGENCE: 'Core guidance active',
    SOURCE_REGISTRY_HEALTH_GET_CONTEXT_BRIDGE: 'Live workspace context',
    OPERATIONAL: 'Kennel operational',
  };
  if (dictionary[token]) return dictionary[token];
  if (!token) return '';
  return token
    .replace(/^WILSY_AI_/, '')
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (l) => l.toUpperCase());
}

/**
 * @function buildWilsyAIProductivityCopy
 * @description Normalises kennel / registry payloads for dock UI.
 * @institutional Preserves a truthful LIVE_EMPTY posture when the source registry is silent.
 */
function buildWilsyAIProductivityCopy(payload = {}) {
  if (!payload || typeof payload !== 'object') {
    return {
      result: 'LIVE_EMPTY',
      workspace: { operatingRole: 'UNRESOLVED', focus: 'UNRESOLVED' },
    };
  }
  const nextBestActions = Array.isArray(payload.nextBestActions)
    ? payload.nextBestActions.map((action) => ({
        ...action,
        title:
          action.rank === 1
            ? 'Review setup authority'
            : action.rank === 2
              ? 'Prepare release checklist'
              : action.title || 'Inspect setup queue',
        description:
          action.rank === 1
            ? 'Check role power, staged review proof, approval state, and release readiness before moving the setup forward.'
            : action.rank === 2
              ? 'Draft the evidence checklist needed before any release command is used.'
              : action.description || 'Check stale setup work and missing receipts before continuing.',
        billingTierSignal: humanizeWilsyAIBackendToken(action.billingTierSignal),
        evidenceStatus: humanizeWilsyAIBackendToken(action.evidenceStatus),
      }))
    : [];

  return {
    ...payload,
    result: humanizeWilsyAIBackendToken(payload.result || payload.status) || 'LIVE_EMPTY',
    bridge: humanizeWilsyAIBackendToken(payload.bridge),
    workspace: {
      ...(payload.workspace || {}),
      focus: payload.workspace?.focus || 'UNRESOLVED',
      operatingRole: payload.workspace?.operatingRole || 'UNRESOLVED',
      monetizationSignal: humanizeWilsyAIBackendToken(payload.workspace?.monetizationSignal),
    },
    modelRoute: {
      ...(payload.modelRoute || {}),
      selectedRoute: humanizeWilsyAIBackendToken(payload.modelRoute?.selectedRoute),
    },
    evidencePosture: {
      ...(payload.evidencePosture || {}),
      status: humanizeWilsyAIBackendToken(payload.evidencePosture?.status),
    },
    billingEntitlement: {
      ...(payload.billingEntitlement || {}),
      tier: humanizeWilsyAIBackendToken(payload.billingEntitlement?.tier),
      requiredTierSignal: humanizeWilsyAIBackendToken(payload.billingEntitlement?.requiredTierSignal),
      upgradeSignal: humanizeWilsyAIBackendToken(payload.billingEntitlement?.upgradeSignal),
    },
    nextBestActions,
    kennel: payload.kennel || payload.system || null,
    uiCopy: {
      statusTitle: 'Workspace status',
      statusSummary: 'Live setup guidance is ready for this workspace.',
      lensTitle: 'Operating lens',
      nextMoveTitle: 'Recommended next step',
      coverageTitle: 'AI coverage',
    },
  };
}

/**
 * @function formatLegalAdvisoryError
 * @description Maps bounded C1C/C1E transport failures to truthful operator copy.
 * @institutional Prevents failed, stale, or unauthorized requests from becoming
 * fabricated recommendations while retaining server-owned conflict classes.
 */
function formatLegalAdvisoryError(error) {
  const status = error?.response?.status ?? error?.status;
  const detail = error?.response?.data?.detail ?? error?.response?.data?.error;
  const code = String(detail || error?.code || '').toUpperCase();
  if (!status && !code) return 'Legal advisory source unavailable; no advisory was generated.';
  if (status === 403 || code === 'C1E_LEGAL_ACCESS_DENIED') {
    return 'Current legal advisory authority denied for this workspace.';
  }
  if (status === 404 || code === 'C1E_RESOURCE_NOT_FOUND') {
    return 'Requested legal advisory source or advisory is unavailable.';
  }
  if (status === 409 && code === 'C1E_TOOL_ASSISTED_REQUIRED') {
    return 'Evidence-backed advisory not generated: tool-assisted orchestration is required.';
  }
  if (status === 409 && code === 'C1E_SOURCE_SNAPSHOT_STALE') {
    return 'Source snapshot is stale; no advisory was created from stale evidence.';
  }
  if (status === 409) return 'Advisory conflict; no fabricated result was returned.';
  if (status === 422) return 'Legal advisory request contract rejected.';
  if (status === 503 && code === 'C1E_ADVISORY_RECONCILIATION_REQUIRED') {
    return 'Advisory state requires reconciliation; success cannot be claimed.';
  }
  if (status === 503) return 'Legal advisory service unavailable; no advisory was generated.';
  return 'Legal advisory source unavailable; no advisory was generated.';
}

/**
 * @function formatAdvisoryValue
 * @description Performs presentation-only formatting without deriving C1E meaning.
 */
function formatAdvisoryValue(value) {
  if (value === null || value === undefined || value === '') return 'Not supplied';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

/**
 * @function formatConfidenceScore
 * @description Displays the server-provided confidence score without recomputation.
 */
function formatConfidenceScore(value) {
  if (typeof value !== 'number') return formatAdvisoryValue(value);
  return `${(value <= 1 ? value * 100 : value).toFixed(1)}%`;
}

/**
 * @function resolveAuthoritativeTenantBrand
 * @description Resolves an optional organization label only from explicit active
 * tenant-context authority; email, role, and MASTER fallbacks are excluded.
 * @param {unknown} tenant - Browser-provided active tenant context.
 * @returns {string} Proven organization/legal name or an empty string.
 * @institutional Keeps WILSY OS as the product brand while preventing invented tenant identity.
 */
function resolveAuthoritativeTenantBrand(tenant) {
  if (!tenant || typeof tenant !== 'object') return '';
  const authority = String(
    tenant.source || tenant.authority_source || tenant.context_source || tenant.authority || ''
  ).toUpperCase();
  if (authority !== 'ACTIVE_TENANT_CONTEXT') return '';
  return String(
    tenant.legalName ||
    tenant.companyName ||
    tenant.organization?.legalName ||
    tenant.organization?.legal_name ||
    tenant.name ||
    ''
  ).trim();
}

const normalizeDockRole = (role) => String(role || '').trim().toUpperCase();

const isLegalDockRole = (role) => {
  const token = normalizeDockRole(role);
  return (
    token.startsWith('LEGAL_')
    || token.startsWith('TENANT_LEGAL_')
    || token === 'SHERIFF'
    || token === 'DEPUTY'
    || token === 'TENANT_SHERIFF'
    || token === 'TENANT_DEPUTY'
  );
};

const canProbeBillingIntelligence = (role) => (
  ['LEGAL_FINANCE', 'TENANT_LEGAL_FINANCE'].includes(normalizeDockRole(role))
);


/**
 * @function WilsyOSIntelligenceDock
 * @description Renders session-scoped conversation over the existing EOS authorities.
 * @collaboration Authenticated runtime, api.js and transient conversation engine.
 * @institutional Browser scope partitions presentation; EOS independently admits every command.
 * @returns {React.ReactElement} Accessible, movable conversation companion.
 * No IAM, workforce, commercial or financial authority is created.
 */
const AI_CONSENT_VERSION = 'WILSY-AI-USAGE-DISCLOSURE/V1';

/** Use authenticated display identity and local presentation time only. */
function operatorGreeting(user, hour = new Date().getHours()) {
  const raw = [user?.firstName, user?.first_name, user?.displayName, user?.name]
    .find(value => typeof value === 'string' && value.trim() && !value.includes('@'));
  const first = raw?.trim().split(/\s+/u)[0]?.replace(/[^\p{L}\p{M}'-]/gu, '').slice(0, 48);
  const period = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening';
  return `Good ${period}${first ? `, ${first}` : ''}.`;
}

/** Browser preference only: never an entitlement or authorized usage admission. */
function consentKeyFor(user, tenant, scope) {
  if (typeof user?.id !== 'string' || !user.id.trim()
    || typeof tenant !== 'string' || !tenant.trim()) return null;
  return 'wilsy.ai.usage-consent:' + JSON.stringify([
    AI_CONSENT_VERSION, tenant, user.id, scope,
  ]);
}

export function WilsyOSIntelligenceDock({
  authUser = null,
  activeTenant = null,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [launcherMinimized, setLauncherMinimized] = useState(false);
  const [dockPosition, setDockPosition] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [positionNotice, setPositionNotice] = useState('');
  const dockContainerRef = useRef(null);
  const dragRef = useRef(null);
  const companionPanelRef = useRef(null);
  const launcherButtonRef = useRef(null);
  const wasOpenRef = useRef(false);
  useEffect(() => {
    if (isOpen) companionPanelRef.current?.focus({ preventScroll: true });
    else if (wasOpenRef.current) launcherButtonRef.current?.focus({ preventScroll: true });
    wasOpenRef.current = isOpen;
  }, [isOpen]);

  // Geometry is a transient preference, never business or identity state.
  const clampDockPosition = useCallback((x, y) => {
    const bounds = dockContainerRef.current?.getBoundingClientRect();
    const width = bounds?.width || 44; const height = bounds?.height || 44;
    const top = Math.min(84, Math.max(12, window.innerHeight - height - 12));
    return { x: Math.max(12, Math.min(x, window.innerWidth - width - 12)),
      y: Math.max(top, Math.min(y, window.innerHeight - height - 12)) };
  }, []);
  useLayoutEffect(() => {
    const keepVisible = () => setDockPosition(current => current
      ? clampDockPosition(current.x, current.y) : current);
    keepVisible(); window.addEventListener('resize', keepVisible);
    return () => window.removeEventListener('resize', keepVisible);
  }, [isOpen, isExpanded, launcherMinimized, clampDockPosition]);
  const beginDockMove = event => {
    if (event.button !== 0) return;
    event.preventDefault(); event.stopPropagation();
    const bounds = dockContainerRef.current.getBoundingClientRect();
    dragRef.current = { id: event.pointerId, x: event.clientX, y: event.clientY,
      left: bounds.left, top: bounds.top };
    event.currentTarget.setPointerCapture?.(event.pointerId); setDragging(true);
  };
  const moveDock = event => {
    const start = dragRef.current;
    if (!start || start.id !== event.pointerId) return;
    event.preventDefault(); event.stopPropagation();
    setDockPosition(clampDockPosition(start.left + event.clientX - start.x,
      start.top + event.clientY - start.y));
  };
  const endDockMove = event => {
    if (!dragRef.current || dragRef.current.id !== event.pointerId) return;
    dragRef.current = null; setDragging(false);
    if (event.currentTarget.hasPointerCapture?.(event.pointerId)) event.currentTarget.releasePointerCapture?.(event.pointerId);
    setPositionNotice('AI companion moved. Your workspace is unchanged.');
  };
  const moveDockWithKeyboard = event => {
    if (event.key === 'Home') { event.preventDefault(); setDockPosition(null); setPositionNotice('AI companion position reset.'); return; }
    const deltas = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
    if (!deltas[event.key]) return;
    event.preventDefault(); event.stopPropagation();
    const bounds = dockContainerRef.current.getBoundingClientRect();
    const step = event.shiftKey ? 48 : 16; const [x, y] = deltas[event.key];
    setDockPosition(clampDockPosition(bounds.left + x * step, bounds.top + y * step));
    setPositionNotice('AI companion moved. Use Home to reset.');
  };
  const moveHandle = <button type="button" className={styles.moveHandle}
    title="Drag to move · arrow keys to adjust · Home to reset" aria-label="Move WILSY OS AI"
    onPointerDown={beginDockMove} onPointerMove={moveDock} onPointerUp={endDockMove}
    onPointerCancel={endDockMove} onKeyDown={moveDockWithKeyboard}><GripVertical size={16}/></button>;
  const [activeTab, setActiveTab] = useState('chat');
  const [prompt, setPrompt] = useState('');
  const [reasoningUsageConsent, setReasoningUsageConsent] = useState(false);
  const [workLocator, setWorkLocator] = useState({ workspace: 'HEADQUARTERS' });
  const [verifiedWorkspaceContext, setVerifiedWorkspaceContext] = useState(null);
  const [headquartersWork, setHeadquartersWork] = useState(null);
  const [contextRefresh, setContextRefresh] = useState(0);
  const workLocatorKey = JSON.stringify(workLocator);
  const reasoningReplayRef = useRef({ scope: '', text: '', prompt: '', key: '' });
  const reasoningAbortRef = useRef(null);
  const workLocatorKeyRef = useRef(workLocatorKey);
  const conversationGenerationRef = useRef(0);
  const sendLockRef = useRef(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [conversationThreads, setConversationThreads] = useState([]);
  const [activeThreadId, setActiveThreadId] = useState(null);
  const [dockContext, setDockContext] = useState(null);
  const [kennelPosture, setKennelPosture] = useState('STANDBY');
  const [errorMessage, setErrorMessage] = useState('');
  const [legalPrompt, setLegalPrompt] = useState('');
  const [legalSubmitting, setLegalSubmitting] = useState(false);
  const [legalRefreshing, setLegalRefreshing] = useState(false);
  const [legalError, setLegalError] = useState('');
  const [legalServiceResponse, setLegalServiceResponse] = useState(null);
  const [legalAdvisory, setLegalAdvisory] = useState(null);
  const [deadlineMatterId, setDeadlineMatterId] = useState('');
  const [deadlineIntelligence, setDeadlineIntelligence] = useState(null);
  const [deadlineLoading, setDeadlineLoading] = useState(false);
  const [deadlineError, setDeadlineError] = useState('');
  const messagesEndRef = useRef(null);
  const healthAbortRef = useRef(null);
  const healthGenerationRef = useRef(0);
  const dockScope = [
    authUser?.id, authUser?.tenantId,
    activeTenant?.tenantId || activeTenant?._id, authUser?.workspaceId,
    authUser?.businessRole || authUser?.role,
    authUser?.membershipRevision, authUser?.businessRoleRevision,
  ].map((part) => String(part ?? '')).join(':');
  const dockScopeRef = useRef(dockScope);
  const consentKey = consentKeyFor(authUser,
    activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId, dockScope);
  const consentKeyRef = useRef(consentKey);
  consentKeyRef.current = consentKey;
  const updateUsageConsent = useCallback(accepted => {
    const key = consentKeyRef.current;
    if (key) {
      try {
        if (accepted) window.localStorage.setItem(key, 'accepted');
        else window.localStorage.removeItem(key);
      } catch {
        // Browser storage is optional. EOS reauthorizes every reasoning call.
      }
    }
    setReasoningUsageConsent(accepted);
  }, []);

  // This module-level session history belongs to the current authenticated
  // capacity only. Changing identity, tenant or capacity revokes old turns and
  // aborts obsolete health probes before they can repaint the next workspace.
  useLayoutEffect(() => {
    conversationGenerationRef.current += 1;
    dockScopeRef.current = dockScope;
    reasoningAbortRef.current?.abort();
    reasoningAbortRef.current = null;
    sendLockRef.current = false;
    setIsSubmitting(false);
    setPrompt('');
    setErrorMessage('');
    setWorkLocator({ workspace: 'HEADQUARTERS' });
    setVerifiedWorkspaceContext(null);
    setHeadquartersWork(null);
    resetWilsyAIConversationSession();
    setConversationThreads([]);
    setActiveThreadId(null);
    let rememberedConsent = false;
    if (consentKey) {
      try {
        rememberedConsent = window.localStorage.getItem(consentKey) === 'accepted';
      } catch {
        rememberedConsent = false;
      }
    }
    setReasoningUsageConsent(rememberedConsent);
    reasoningReplayRef.current = { scope: '', text: '', prompt: '', key: '' };
    setDockContext(null);
    setKennelPosture('STANDBY');
    return () => {
      conversationGenerationRef.current += 1;
      reasoningAbortRef.current?.abort();
      healthAbortRef.current?.abort();
      healthGenerationRef.current += 1;
      resetWilsyAIConversationSession();
    };
  }, [dockScope, consentKey]);

  useLayoutEffect(() => {
    if (workLocatorKeyRef.current === workLocatorKey) return;
    workLocatorKeyRef.current = workLocatorKey;
    conversationGenerationRef.current += 1;
    reasoningAbortRef.current?.abort();
    reasoningAbortRef.current = null;
    sendLockRef.current = false;
    reasoningReplayRef.current = { scope: '', text: '', prompt: '', key: '' };
    setIsSubmitting(false);
    setErrorMessage('');
  }, [workLocatorKey]);

  // Navigation events are untrusted locators. No profile, permission, seat,
  // project title or other source fact is accepted from browser events.
  useEffect(() => {
    const receive = event => {
      const detail = event.detail;
      const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
      if (!authUser?.id || detail?.tenantId !== exactTenant || detail?.principalId !== authUser.id) return;
      const candidate = detail.locator;
      const allowed = ['workspace', 'project_id', 'project_revision', 'task_id', 'task_revision', 'participant_view'];
      if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate)
        || Object.keys(candidate).some(key => !allowed.includes(key))
        || !['HEADQUARTERS', 'PROJECTS'].includes(candidate.workspace)
        || (candidate.project_id && (!/^prj-[0-9a-f]{48}$/.test(candidate.project_id)
          || candidate.workspace !== 'PROJECTS'))
        || (candidate.project_revision !== undefined && (!candidate.project_id
          || !Number.isSafeInteger(candidate.project_revision) || candidate.project_revision < 1))
        || (candidate.task_id && (!candidate.project_id || !/^ptk-[0-9a-f]{48}$/.test(candidate.task_id)))
        || (candidate.task_revision !== undefined && (!candidate.task_id
          || !Number.isSafeInteger(candidate.task_revision) || candidate.task_revision < 1))
        || (candidate.participant_view !== undefined && typeof candidate.participant_view !== 'boolean')) return;
      setWorkLocator(previous => JSON.stringify(previous) === JSON.stringify(candidate) ? previous : { ...candidate });
    };
    window.addEventListener('wilsy:ai-context-locator', receive);
    window.dispatchEvent(new CustomEvent('wilsy:ai-context-request'));
    return () => window.removeEventListener('wilsy:ai-context-locator', receive);
  }, [dockScope]);

  useEffect(() => {
    const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
    if (!isOpen || !authUser?.id || !exactTenant || isLegalDockRole(authUser?.role)) {
      setVerifiedWorkspaceContext(null);
      return undefined;
    }
    const controller = new AbortController();
    let current = true;
    const base = { scope: dockScope, locatorKey: workLocatorKey };
    setVerifiedWorkspaceContext({ ...base, state: 'LOADING' });
    api.get('/wilsy-ai/reasoning/context', {
      params: workLocator, headers: { 'X-Tenant-ID': exactTenant },
      signal: controller.signal, timeout: 15000, forceNetworkRetry: true,
    }).then(response => {
      if (!current || controller.signal.aborted || dockScopeRef.current !== dockScope) return;
      const data = response?.data;
      if (data?.schema !== 'WILSY-AI-VERIFIED-CONTEXT/V1'
        || data.tenant_id !== exactTenant || data.principal_id !== authUser.id
        || data.authority?.source !== 'PYTHON_EOS' || data.authority?.read_only !== true
        || data.authority?.model_invoked !== false || data.authority?.financial_execution !== false
        || !/^[0-9a-f]{128}$/.test(data.context_fingerprint || '')
        || !Number.isFinite(Date.parse(data.observed_at))
        || data.locator?.workspace !== workLocator.workspace
        || (data.locator?.project_id || null) !== (workLocator.project_id || null)
        || (data.locator?.task_id || null) !== (workLocator.task_id || null)
        || (workLocator.project_id && data.work?.project?.project_id !== workLocator.project_id)
        || (workLocator.project_revision && data.work?.project?.revision !== workLocator.project_revision)
        || !Number.isSafeInteger(data.allowance?.available_request_units)
        || data.allowance.available_request_units < 0) throw new Error('WILSY_AI_CONTEXT_RESPONSE_INVALID');
      setVerifiedWorkspaceContext({ ...base, state: 'READY', data });
    }).catch(error => {
      if (!current || controller.signal.aborted || dockScopeRef.current !== dockScope) return;
      const status = error?.response?.status;
      setVerifiedWorkspaceContext({ ...base,
        state: status === 401 || status === 403 ? 'DENIED' : status === 409 ? 'STALE' : 'UNAVAILABLE' });
    });
    return () => { current = false; controller.abort(); };
  }, [isOpen, dockScope, workLocatorKey, contextRefresh]);

  // Read-only EOS My Work is independently authorized from AI commercial
  // entitlement. It is a UI projection only; never forwarded to a model as
  // client-provided fact or used to authorize workflow commands.
  useEffect(() => {
    const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
    if (!isOpen || !authUser?.id || !exactTenant || workLocator.workspace !== 'HEADQUARTERS') {
      setHeadquartersWork(null);
      return undefined;
    }
    const controller = new AbortController();
    let live = true;
    const scope = dockScope;
    setHeadquartersWork({ scope, state: 'LOADING' });
    api.get('/my-work', {
      headers: { 'X-Tenant-ID': exactTenant },
      signal: controller.signal,
      timeout: 15000,
    }).then(response => {
      if (!live || controller.signal.aborted || dockScopeRef.current !== scope) return;
      const data = response?.data;
      if (!data || data.tenant_id !== exactTenant || data.principal_id !== authUser.id
        || !Array.isArray(data.items)
        || !data.summary || !Number.isSafeInteger(data.summary.active_count)
        || !Number.isSafeInteger(data.summary.overdue_count)
        || data.authority?.commands_owned_by !== 'SOURCE_SERVICES'
        || data.authority?.permits_completion !== false
        || data.authority?.permits_approval !== false) {
        setHeadquartersWork({ scope, state: 'UNAVAILABLE' });
        return;
      }
      const items = data.items.slice(0, 3).map(item => ({
        title: typeof item.title === 'string' ? item.title.slice(0, 180) : '',
        source: typeof item.source === 'string' ? item.source.slice(0, 32) : '',
        overdue: item.is_overdue === true,
      })).filter(item => item.title && item.source);
      setHeadquartersWork({ scope, state: 'READY', items,
        activeCount: data.summary.active_count,
        overdueCount: data.summary.overdue_count });
    }).catch(() => {
      if (live && !controller.signal.aborted && dockScopeRef.current === scope) {
        setHeadquartersWork({ scope, state: 'UNAVAILABLE' });
      }
    });
    return () => { live = false; controller.abort(); };
  }, [isOpen, dockScope, workLocatorKey, contextRefresh]);

  const aiEntitlementNotProvisioned = verifiedWorkspaceContext?.scope === dockScope
    && verifiedWorkspaceContext?.locatorKey === workLocatorKey
    && verifiedWorkspaceContext?.state === 'READY'
    && verifiedWorkspaceContext.data?.allowance?.state === 'NOT_PROVISIONED';
  const visibleWorkspaceContext = verifiedWorkspaceContext?.scope === dockScope
    && verifiedWorkspaceContext?.locatorKey === workLocatorKey ? verifiedWorkspaceContext : null;

  /**
   * @function hydrateDockContext
   * @description Loads kennel posture via sovereign api – never window.fetch.
   * @collaboration Invoked on mount and during manual refresh.
   */
  const hydrateDockContext = useCallback(async () => {
    healthAbortRef.current?.abort();
    const controller = new AbortController();
    healthAbortRef.current = controller;
    const generation = ++healthGenerationRef.current;
    const isCurrent = () => (
      !controller.signal.aborted
      && healthGenerationRef.current === generation
      && dockScopeRef.current === dockScope
    );
    // Optional finance evidence must never serialize or delay kernel health.
    // Its own EOS IAM remains authoritative; a failure yields no finance facts.
    const billingEvidenceRead = canProbeBillingIntelligence(authUser?.role)
      ? api.get('/billing/intelligence/evidence', {
        params: { as_of: new Date().toISOString() },
        timeout: 8000,
        signal: controller.signal,
      }).then((response) => (
        response?.status === 200
        && response?.data
        && typeof response.data === 'object'
          ? response.data : null
      )).catch(() => null)
      : Promise.resolve(null);

    try {
      // Optional EOS health reads never authorize or block Headquarters.
      const kernelRes = await api.get('/kernel', {
        timeout: 8000,
        signal: controller.signal,
      });
      if (!isCurrent()) return;
      const kernel = kernelRes?.data || {};
      const live = String(kernel.status || '').toUpperCase() === 'OPERATIONAL';
      setKennelPosture(live ? 'OPERATIONAL' : 'DEGRADED');

      const normalizedDockContext = buildWilsyAIProductivityCopy({
        result: live ? 'WILSY_AI_SOVEREIGN_CONTEXT_RESOLVED' : 'SOURCE_DEGRADED',
        kennel: kernel,
        bridge: kernel.bridge,
        workspace: {
          operatingRole: authUser?.role || 'UNRESOLVED',
          tenantId: activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId || '',
        },
      });
      if (!isCurrent()) return;
      setDockContext(normalizedDockContext);
      // Publish the independent verified kernel result before optional finance
      // completion; late responses may enrich only the same live auth scope.
      const billingIntelligenceEvidence = await billingEvidenceRead;
      if (!isCurrent()) return;
      if (billingIntelligenceEvidence) {
        setDockContext({
          ...normalizedDockContext,
          billingIntelligenceEvidence,
        });
      }
    } catch (err) {
      if (!isCurrent()) return;
      // Absence of verified EOS health is not successful advisory context.
      setDockContext(null);
      setKennelPosture('SOURCE_SILENT');
      if (import.meta.env.DEV) {
        console.warn('[IntelligenceDock] EOS health unavailable; verified context withheld.', err);
      }
    }
  }, [dockScope, authUser?.role, activeTenant?.tenantId, activeTenant?._id]);

  /**
   * @function handleNewThread
   * @description Creates a new conversation thread without clearing existing history.
   * @institutional Allows operators to compartmentalize conversations by topic.
   */
  const handleNewThread = useCallback(async () => {
    const scopeAtStart = dockScopeRef.current;
    try {
      const fresh = await createWilsyAIConversationThread({
        title: 'New Sovereign Session',
        workspace: 'WILSY OS',
      });
      if (scopeAtStart !== dockScopeRef.current) return;
      setConversationThreads((prev) => [fresh, ...prev.filter((item) => item.id !== fresh.id)]);
      setActiveThreadId(fresh.id);
    } catch (err) {
      if (scopeAtStart === dockScopeRef.current) {
        setErrorMessage(err?.message || 'Failed to create a new thread.');
      }
    }
  }, []);

  /**
   * @function handleRefresh
   * @description Manually refreshes the conversation list and Kennel context.
   * @institutional Prevents stale data from persisting after external updates.
   */
  const handleRefresh = useCallback(async () => {
    const scopeAtStart = dockScopeRef.current;
    setErrorMessage('');
    try {
      const refreshed = await loadWilsyAIConversationThreads();
      if (scopeAtStart !== dockScopeRef.current) return;
      setConversationThreads(refreshed);
      if (!refreshed.find(t => t.id === activeThreadId)) {
        setActiveThreadId(refreshed[0]?.id || null);
      }
      await hydrateDockContext(); // Also refresh kennel context
    } catch (err) {
      if (scopeAtStart === dockScopeRef.current) {
        setErrorMessage('Failed to refresh threads.');
      }
    }
  }, [activeThreadId, hydrateDockContext]);

  useEffect(() => {
    let active = true;
    const hydrate = async () => {
      try {
        let threads = await loadWilsyAIConversationThreads();
        if (!threads.length) {
          const fresh = await createWilsyAIConversationThread({
            title: 'New Sovereign Session',
            workspace: 'WILSY OS',
          });
          threads = [fresh];
        }
        if (active) {
          setConversationThreads(threads);
          setActiveThreadId(threads[0]?.id || null);
        }
      } catch {
        if (active) {
          setConversationThreads([]);
          setActiveThreadId(null);
        }
      }
      if (active) await hydrateDockContext();
    };
    void hydrate();
    return () => {
      active = false;
      healthAbortRef.current?.abort();
      healthGenerationRef.current += 1;
    };
  }, [hydrateDockContext]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [conversationThreads, activeThreadId, isSubmitting]);

  const activeThread = useMemo(() => {
    return (
      conversationThreads.find((t) => t.id === activeThreadId) ||
      conversationThreads[0] || { id: null, messages: [] }
    );
  }, [conversationThreads, activeThreadId]);

  const dynamicSuggestions = useMemo(() => {
    try {
      return buildWilsyDynamicSuggestions({
        context: dockContext || {
          workspace: { focus: 'Authority graph', operatingRole: 'Guest Operator' },
        },
      });
    } catch {
      return [];
    }
  }, [dockContext]);

  /**
   * @function handleSendMessage
   * @description Legal roles keep C1C; ordinary turns use consented EOS metered reasoning, not the legacy operator BFF.
   */
  const handleSendMessage = useCallback(
    async (rawText) => {
      const text = String(rawText || prompt).trim();
      if (!text || isSubmitting || sendLockRef.current) return;
      if (!isLegalDockRole(authUser?.role) && aiEntitlementNotProvisioned) {
        setErrorMessage('Your workspace is verified, but AI reasoning is not yet activated for this tenant.');
        return;
      }
      if (!isLegalDockRole(authUser?.role) && !reasoningUsageConsent) {
        setErrorMessage('Confirm the WILSY AI usage terms before requesting reasoning.');
        return;
      }
      const currentProject = workLocator.project_id
        && visibleWorkspaceContext?.state === 'READY'
        && visibleWorkspaceContext.data.work?.project?.project_id === workLocator.project_id
        ? { ...workLocator } : null;
      if (!isLegalDockRole(authUser?.role) && workLocator.project_id && !currentProject) {
        setErrorMessage('EOS must verify the current project before AI can answer about it. Refresh context.');
        return;
      }
      const locatorKeyAtStart = workLocatorKey;
      const scopeAtStart = dockScopeRef.current;
      const generationAtStart = conversationGenerationRef.current;
      const controller = new AbortController();
      reasoningAbortRef.current = controller;
      sendLockRef.current = true;
      const requestIsCurrent = () => !controller.signal.aborted
        && conversationGenerationRef.current === generationAtStart
        && dockScopeRef.current === scopeAtStart
        && workLocatorKeyRef.current === locatorKeyAtStart;

      setIsSubmitting(true);
      setErrorMessage('');
      setPrompt('');

      const userTurn = {
        role: 'user',
        content: text,
        timestamp: new Date().toISOString(),
      };

      let threadId = activeThreadId;
      try {
        if (!threadId) {
          const fresh = await createWilsyAIConversationThread({
            title: text.slice(0, 48) || 'New Sovereign Session',
            promptText: text,
            workspace: 'WILSY OS',
          });
          if (!requestIsCurrent()) return;
          threadId = fresh.id;
          setActiveThreadId(threadId);
          setConversationThreads((prev) => [fresh, ...prev.filter((t) => t.id !== fresh.id)]);
        }
        const afterUser = await persistWilsyAIConversationTurn({
          threadId,
          message: userTurn,
        });
        if (!requestIsCurrent()) return;
        setConversationThreads((prev) => [
          afterUser,
          ...prev.filter((item) => item.id !== afterUser.id),
        ]);
      } catch (err) {
        if (requestIsCurrent()) {
          setErrorMessage(err?.message || 'Failed to record operator turn.');
          setIsSubmitting(false);
          sendLockRef.current = false;
          reasoningAbortRef.current = null;
        }
        return;
      }

      try {
        let result;
        if (isLegalDockRole(authUser?.role)) {
          const response = await executeWilsyAILegalServices(text, uuidv4());
          const legal = response?.data || {};
          result = {
            reply:
              legal.response_text
              || 'The legal-services authority returned no response text.',
            source: 'WILSY_AI_LEGAL_SERVICES',
            phase: 'C1C',
            intent: legal.outcome || 'LEGAL_SERVICES',
            domain: 'LEGAL',
            tenantId: activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId || '',
          };
        } else {
          const exactTenant = activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId;
          if (typeof exactTenant !== 'string' || !exactTenant.trim()) {
            throw new Error('WILSY_AI_TENANT_SCOPE_REQUIRED');
          }
          // Session conversation only: page location and browser role labels
          // are never promoted to verified EOS business evidence.
          const previous = (activeThread?.messages || [])
            .filter(item => ['user', 'assistant'].includes(item?.role)
              && typeof item?.content === 'string')
            .slice(-6)
            .map(item => (item.role === 'user' ? 'Operator' : 'WILSY AI')
              + ': ' + item.content.slice(0, 900))
            .join('\n');
          const reasoningPrompt = [
            'Current user question:', text,
            ...(previous ? ['Previous conversation (not EOS source evidence):', previous] : []),
            'Do not claim verified access to tenant projects, employee records, '
              + 'financial balances or legal matters without an authorized EOS '
              + 'tool result. Inferences are not authorizations or execution.',
          ].join('\n\n').slice(0, 12000);
          const pending = reasoningReplayRef.current;
          const replay = pending.scope === scopeAtStart && pending.text === text
            && pending.locatorKey === locatorKeyAtStart && pending.key && pending.prompt
            ? pending
            : { scope: scopeAtStart, text, prompt: reasoningPrompt, key: uuidv4(),
              locatorKey: locatorKeyAtStart, params: currentProject };
          reasoningReplayRef.current = replay;
          const response = await api.post('/wilsy-ai/reasoning', {
            prompt: replay.prompt,
          }, {
            headers: { 'X-Tenant-ID': exactTenant, 'Idempotency-Key': replay.key },
            ...(replay.params ? { params: replay.params } : {}),
            timeout: 30000,
            signal: controller.signal,
          });
          const data = response?.data;
          if (typeof data?.response_text !== 'string' || !data.response_text.trim()
            || typeof data?.usage_observation_id !== 'string') {
            throw new Error('WILSY_AI_REASONING_RESULT_UNVERIFIED');
          }
          if (!requestIsCurrent()) return;
          reasoningReplayRef.current = { scope: '', text: '', prompt: '', key: '' };
          result = {
            reply: data.response_text,
            source: 'PYTHON_EOS_WILSY_AI_REASONING',
            phase: 'ADMITTED_REASONING',
            domain: 'GENERAL',
            tenantId: exactTenant,
          };
        }

        if (!requestIsCurrent()) return;

        const content =
          result?.reply ||
          result?.content ||
          result?.message ||
          result?.answer ||
          result?.result ||
            'Operator source returned no intelligence; no recommendation was generated.';

        const assistantTurn = {
          role: 'assistant',
          content: String(content),
          timestamp: new Date().toISOString(),
          meta: {
            source: result?.source || 'OPERATOR_ENGINE_BACKEND',
            phase: result?.phase || 'KENNEL_PHASE_4',
            kennelPosture,
            intent: result?.intent,
            domain: result?.domain,
            tenantId: result?.tenantId || activeTenant?.tenantId || authUser?.tenantId || '',
          },
        };

        const afterAssistant = await persistWilsyAIConversationTurn({
          threadId,
          message: assistantTurn,
        });
        if (!requestIsCurrent()) return;
        setConversationThreads((prev) => [
          afterAssistant,
          ...prev.filter((item) => item.id !== afterAssistant.id),
        ]);
      } catch (err) {
        if (!requestIsCurrent()) return;
        const status = err?.response?.status;
        const safeMessage = status === 401
          ? 'Authentication is required to use WILSY AI.'
          : status === 403 ? 'WILSY AI permission or subscription entitlement is not verified.'
          : status === 429 ? 'WILSY AI usage capacity is exhausted for the current period.'
          : status === 503 ? 'The EOS AI provider or entitlement source is temporarily unavailable.'
          : 'WILSY AI could not verify this answer. Your question remains in the composer.';
        setErrorMessage(safeMessage);
        if (!isLegalDockRole(authUser?.role)) setPrompt(text);
        // A failure is not an AI answer; retain draft and show one error only.
      } finally {
        if (requestIsCurrent()) {
          sendLockRef.current = false;
          reasoningAbortRef.current = null;
          setIsSubmitting(false);
        }
      }
    },
    [
      prompt,
      isSubmitting,
      reasoningUsageConsent,
      aiEntitlementNotProvisioned,
      workLocatorKey,
      workLocator,
      visibleWorkspaceContext,
      authUser?.role,
      dockScope,
      activeThreadId,
      activeThread?.messages,
      dockContext,
      activeTenant,
      kennelPosture,
    ]
  );

  /**
   * @function handleGenerateLegalAdvisory
   * @description Explicitly composes C1C tool-assisted evidence with C1E advisory projection.
   * @institutional C1C/C1E remain server authorities; the Dock owns only a fresh
   * transport replay key and transient presentation state.
   */
  const handleGenerateLegalAdvisory = useCallback(async () => {
    const exactPrompt = legalPrompt.trim();
    if (!exactPrompt || legalSubmitting) return;

    setLegalSubmitting(true);
    setLegalError('');
    setLegalServiceResponse(null);
    setLegalAdvisory(null);
    try {
      const c1cResponse = await executeWilsyAILegalServices(exactPrompt, uuidv4());
      const c1cPayload = c1cResponse?.data || {};
      setLegalServiceResponse({
        orchestration_id: c1cPayload.orchestration_id,
        outcome: c1cPayload.outcome,
        response_text: c1cPayload.response_text,
        sources: c1cPayload.sources,
      });
      if (c1cPayload.outcome !== 'TOOL_ASSISTED') return;
      if (typeof c1cPayload.orchestration_id !== 'string' || !c1cPayload.orchestration_id) {
        setLegalError('Tool-assisted orchestration did not return an advisory identity.');
        return;
      }
      const c1eResponse = await generateWilsyAILegalNextActions(c1cPayload.orchestration_id);
      const advisory = c1eResponse?.data;
      if (!advisory || typeof advisory !== 'object') {
        setLegalError('Evidence-backed advisory was unavailable; no fabricated result was returned.');
        return;
      }
      setLegalAdvisory(advisory);
    } catch (error) {
      setLegalError(formatLegalAdvisoryError(error));
      setLegalAdvisory(null);
    } finally {
      setLegalSubmitting(false);
    }
  }, [legalPrompt, legalSubmitting]);

  /**
   * @function handleRefreshLegalAdvisory
   * @description Reads the current server-owned advisory status exactly once.
   */
  const handleRefreshLegalAdvisory = useCallback(async () => {
    const advisoryId = legalAdvisory?.advisory_id;
    if (!advisoryId || legalRefreshing) return;
    setLegalRefreshing(true);
    setLegalError('');
    try {
      const response = await readWilsyAILegalNextAction(advisoryId);
      setLegalAdvisory(response?.data || null);
    } catch (error) {
      setLegalError(formatLegalAdvisoryError(error));
    } finally {
      setLegalRefreshing(false);
    }
  }, [legalAdvisory?.advisory_id, legalRefreshing]);

  /**
   * @function handleViewSuccessor
   * @description Reads a server-owned successor advisory without generating a new one.
   * @param {string} successorId - Persisted successor identity from the stale advisory.
   */
  const handleViewSuccessor = useCallback(async (successorId) => {
    if (!successorId || legalRefreshing) return;
    setLegalRefreshing(true);
    setLegalError('');
    try {
      const response = await readWilsyAILegalNextAction(successorId);
      setLegalAdvisory(response?.data || null);
    } catch (error) {
      setLegalError(formatLegalAdvisoryError(error));
    } finally {
      setLegalRefreshing(false);
    }
  }, [legalRefreshing]);

  /**
   * @function clearLegalAdvisoryView
   * @description Clears transient C1E presentation state without touching history or storage.
   */
  const clearLegalAdvisoryView = useCallback(() => {
    setLegalPrompt('');
    setLegalError('');
    setLegalServiceResponse(null);
    setLegalAdvisory(null);
  }, []);

  /**
   * @function handleObserveDeadlines
   * @description Reads a certified D6 Core Legal observation for one explicit matter.
   * @institutional The browser supplies only a locator and observation instant;
   * server IAM and D6 own scope and temporal posture. No advice is generated.
   */
  const handleObserveDeadlines = useCallback(async () => {
    const exactMatterId = deadlineMatterId.trim();
    if (!exactMatterId || deadlineLoading) return;
    setDeadlineLoading(true);
    setDeadlineError('');
    setDeadlineIntelligence(null);
    try {
      const projection = await getLegalMatterDeadlineIntelligence(
        exactMatterId,
        new Date().toISOString(),
      );
      setDeadlineIntelligence(projection);
    } catch (error) {
      const status = error?.response?.status ?? error?.status;
      if (status === 403) {
        setDeadlineError('Current tenant authority does not permit deadline intelligence access.');
      } else if (status === 404) {
        setDeadlineError('No authorized deadline source is available for this matter.');
      } else if (status === 422) {
        setDeadlineError('Matter or observation input was rejected.');
      } else {
        setDeadlineError('Deadline observation is unavailable; no posture was inferred.');
      }
    } finally {
      setDeadlineLoading(false);
    }
  }, [deadlineMatterId, deadlineLoading]);

  const welcomeGreeting = operatorGreeting(authUser);
  const visibleHeadquartersWork = headquartersWork?.scope === dockScope
    && workLocator.workspace === 'HEADQUARTERS' ? headquartersWork : null;
  const operatorLabel =
    authUser?.displayName ||
    authUser?.name ||
    authUser?.email ||
    'Operator';
  const legalStatus = String(legalAdvisory?.status || '').toUpperCase();
  const authoritativeTenantBrand = resolveAuthoritativeTenantBrand(activeTenant);

  return (
    <div ref={dockContainerRef} className={styles.intelligenceDockContainer}
      data-wilsy-intelligence-dock="active" data-kennel={kennelPosture}
      data-ai-layout={isOpen ? 'OPEN' : launcherMinimized ? 'MINIMIZED' : 'LAUNCHER'}
      data-dragging={dragging ? 'true' : undefined}
      style={dockPosition ? { left: dockPosition.x, top: dockPosition.y, right: 'auto', bottom: 'auto' } : undefined}>
      <span className={styles.srOnly} role="status">{positionNotice}</span>
      {!isOpen && (
        <div className={`${styles.launcherTray} ${launcherMinimized ? styles.launcherMinimized : ''}`}>
          {moveHandle}
          <button ref={launcherButtonRef} type="button" className={styles.dockLauncherButton}
            onClick={() => setIsOpen(true)} title="Open Wilsy OS Intelligence Dock"
            aria-label="Open Wilsy OS Intelligence Dock" aria-expanded="false">
            <img src="/brand/wilsy-ai-emblem.svg" className={styles.aiEmblem} alt="" aria-hidden="true"/>
            {!launcherMinimized && <span>WILSY OS<small>AI COMPANION</small></span>}
          </button>
          <button type="button" className={styles.launcherSizeControl}
            title={launcherMinimized ? 'Restore AI launcher' : 'Minimize AI launcher'}
            onClick={() => { setLauncherMinimized(value => !value); setPositionNotice('AI launcher size changed.'); }}>
            {launcherMinimized ? <PanelRightOpen size={14}/> : <Minus size={14}/>}
          </button>
        </div>
      )}

      {isOpen && (
        <section className={`${styles.dockWindow} ${isExpanded ? styles.dockExpanded : ''}`} ref={companionPanelRef} tabIndex={-1} role="region" aria-label="WILSY OS AI companion"
          onKeyDown={event => { if (event.key === 'Escape') { event.stopPropagation(); setIsOpen(false); setLauncherMinimized(true); } }}>
          <div className={styles.dockHeader}>
            {moveHandle}
            <div className={styles.dockHeaderTitle}>
              <img src="/brand/wilsy-ai-emblem.svg" className={styles.headerEmblem} alt="Wilsy AI neural core"/>
              <div>
                <span>WILSY OS Intelligence Dock</span>
                <small className={styles.kennelBadge} data-posture={kennelPosture}>
                  {kennelPosture === 'OPERATIONAL' ? 'Kennel source connected'
                    : kennelPosture === 'SOURCE_SILENT' ? 'Kennel source not responding'
                      : kennelPosture === 'CLIENT_OFFLINE' ? 'Connection unavailable'
                        : 'Kennel source not verified'}
                </small>
                {authoritativeTenantBrand && (
                  <small className={styles.workspaceBrand} data-brand-source="ACTIVE_TENANT_CONTEXT">
                    {authoritativeTenantBrand}
                  </small>
                )}
              </div>
            </div>
            <div className={styles.dockHeaderActions}>
              <button type="button" className={styles.headerIconButton} title="Reset AI position"
                onClick={() => { setDockPosition(null); setPositionNotice('AI companion position reset.'); }}><RotateCcw size={15}/></button>
              <button type="button" className={styles.headerIconButton} title="Minimize dock"
                onClick={() => { setIsOpen(false); setLauncherMinimized(true); }}><Minus size={16}/></button>
              <button
                type="button"
                className={styles.headerIconButton}
                onClick={() => setIsExpanded(!isExpanded)}
                title={isExpanded ? 'Restore dock size' : 'Expand dock'}
              >
                {isExpanded ? <Minimize2 size={16} /> : <PanelRightOpen size={16} />}
              </button>
              <button
                type="button"
                className={styles.headerIconButton}
                onClick={() => { setIsOpen(false); setLauncherMinimized(false); }}
                title="Close dock"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          <div className={styles.dockNavBar}>
            <button
              type="button"
              className={`${styles.navTabButton} ${activeTab === 'chat' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <MessageSquareText size={15} />
              <span>Ask WILSY OS</span>
            </button>
            <button
              type="button"
              className={`${styles.navTabButton} ${activeTab === 'suggestions' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('suggestions')}
            >
              <Sparkles size={15} />
              <span>Suggestions</span>
            </button>
            <button
              type="button"
              className={`${styles.navTabButton} ${activeTab === 'legalAdvisory' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('legalAdvisory')}
            >
              <FileCheck2 size={15} />
              <span>Legal Advisory</span>
            </button>
            {isLegalDockRole(authUser?.role) && (
              <button
                type="button"
                className={`${styles.navTabButton} ${activeTab === 'deadlineIntelligence' ? styles.activeTab : ''}`}
                onClick={() => setActiveTab('deadlineIntelligence')}
              >
                <FileCheck2 size={15} />
                <span>Deadlines</span>
              </button>
            )}
            <button
              type="button"
              className={`${styles.navTabButton} ${activeTab === 'history' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('history')}
            >
              <History size={15} />
              <span>History</span>
            </button>
          </div>

          <div className={styles.dockBody}>
            {activeTab === 'chat' && (
              <div className={styles.chatTabContent}>
                {authUser?.id && !isLegalDockRole(authUser?.role) && <section
                  aria-label="Verified workspace context" aria-live="polite"
                  style={{ padding: '10px 14px', background: '#111827', color: '#f1f5f9',
                    borderBottom: '1px solid #475569', fontSize: 12, lineHeight: 1.5,
                    flexShrink: 0, maxHeight: 220, overflowY: 'auto' }}>
                  {visibleWorkspaceContext?.state === 'READY' ? <details>
                    <summary aria-label="Inspect verified workspace context"
                      style={{ cursor: 'pointer', minHeight: 44 }}>
                      <strong>{visibleWorkspaceContext.data.work?.project?.name || 'Current authorized workspace'}</strong>
                      {visibleWorkspaceContext.data.work?.selected_task?.title
                        ? <span style={{ display: 'block', overflowWrap: 'anywhere', fontWeight: 400 }}>
                          {'Viewing task: '}{visibleWorkspaceContext.data.work.selected_task.title}
                        </span> : null}
                      {' · '}{aiEntitlementNotProvisioned ? 'AI reasoning not activated'
                        : `${visibleWorkspaceContext.data.allowance.available_request_units} requests available`}
                    </summary>
                    <p style={{ margin: '4px 0' }}>
                      {visibleWorkspaceContext.data.work?.current_person_name || 'Person name unavailable'}
                      {' · '}{aiEntitlementNotProvisioned ? 'AI activation required'
                        : `${visibleWorkspaceContext.data.allowance.available_request_units} requests available`}
                      {' · Seats and pricing: '}{visibleWorkspaceContext.data.allowance.seat_allocation?.state === 'UNAVAILABLE'
                        ? 'unavailable' : 'require independent admission'}
                    </p>
                    <p style={{ margin: '4px 0' }}>Workforce and qualifications: unavailable without independent source authority.</p>
                    {(visibleWorkspaceContext.data.work?.sources || []).filter(source => source.kind === 'PROJECT'
                      && source.project_id === workLocator.project_id).map(source => <button type="button"
                      key={source.project_id} className={styles.historyActionButton}
                      style={{ minHeight: 44, color: '#f8fafc', padding: '6px 10px' }}
                      onClick={() => window.dispatchEvent(new CustomEvent('wilsy:ai-inspect-source', {
                        detail: { tenantId: visibleWorkspaceContext.data.tenant_id,
                          principalId: visibleWorkspaceContext.data.principal_id,
                          project_id: source.project_id },
                      }))}>Inspect source: {source.label}</button>)}
                    <p style={{ margin: '4px 0', color: '#cbd5e1' }}>
                      {aiEntitlementNotProvisioned
                        ? 'Your work is independently verified. Model requests remain disabled until the subscription-backed AI entitlement is activated.'
                        : 'Verified project sources can support reasoning only after independent EOS authorization and usage admission.'}
                    </p>
                  </details> : <span>{visibleWorkspaceContext?.state === 'LOADING' ? 'Verifying workspace context…'
                    : visibleWorkspaceContext?.state === 'DENIED' ? 'Workspace context access denied by EOS.'
                      : visibleWorkspaceContext?.state === 'STALE' ? 'Workspace context changed. Refresh the project source.'
                        : 'Verified workspace context unavailable.'}</span>}
                  <button type="button" className={styles.historyActionButton}
                    disabled={visibleWorkspaceContext?.state === 'LOADING'}
                    style={{ minHeight: 44, marginLeft: 6, color: '#f8fafc', padding: '6px 10px' }}
                    onClick={() => setContextRefresh(value => value + 1)}>Refresh context</button>
                </section>}
                {visibleHeadquartersWork?.state === 'READY'
                  && visibleHeadquartersWork.activeCount > 0
                  && <section aria-label="Current authorized work"
                    style={{ padding: '8px 14px', background: 'rgba(9,25,45,.74)',
                      borderBottom: '1px solid rgba(170,194,217,.15)',
                      color: '#d7e4f4', fontSize: 12, flexShrink: 0,
                      maxHeight: 160, overflowY: 'auto' }}>
                    <strong style={{ fontWeight: 550 }}>
                      Your work · {visibleHeadquartersWork.activeCount} active
                      {' · '}{visibleHeadquartersWork.overdueCount} overdue
                    </strong>
                    <ol style={{ margin: '6px 0 0', paddingLeft: 20 }}>
                      {visibleHeadquartersWork.items.map((item, index) =>
                        <li key={index} style={{ marginBottom: 4, overflowWrap: 'anywhere' }}>
                          {item.title} <span style={{ color: '#abbfd4' }}>
                            · {item.source}{item.overdue ? ' · Overdue' : ''}
                          </span>
                        </li>)}
                    </ol>
                  </section>}
                <div className={styles.messagesContainer} style={{ minHeight: 0 }}>
                  {(!activeThread?.messages || activeThread.messages.length === 0) && (
                    <div className={styles.emptyChatWelcome}>
                      <h4>{welcomeGreeting}</h4>
                      {visibleWorkspaceContext?.state === 'READY'
                        && visibleWorkspaceContext.data.work?.project?.name
                        ? <strong>{visibleWorkspaceContext.data.work.project.name}</strong> : null}
                      <p>{visibleWorkspaceContext?.state === 'READY'
                        ? (visibleWorkspaceContext.data.work?.selected_task?.title
                          ? `You're viewing the verified task “${visibleWorkspaceContext.data.work.selected_task.title}”. Ask about this task, its status or its project. EOS rechecks its facts before AI reasoning.`
                          : 'EOS has verified this workspace. With your consent, AI can use independently rechecked project facts for this request.')
                        : visibleWorkspaceContext?.state === 'LOADING'
                          ? 'Checking which workspace information EOS permits you to access.'
                          : visibleWorkspaceContext?.state === 'DENIED'
                            ? 'EOS did not authorize workspace context. I will not invent project or task facts.'
                            : 'Ask a general question, or open an authorized project for verified work context.'}</p>
                    </div>
                  )}
                  {(activeThread?.messages || []).map((msg, idx) => (
                    <div
                      key={`${msg.timestamp || idx}-${idx}`}
                      className={`${styles.chatMessageBubble} ${
                        msg.role === 'user' ? styles.userBubble : styles.assistantBubble
                      }`}
                    >
                      <div className={styles.bubbleHeader}>
                        <span>{msg.role === 'user' ? operatorLabel : 'WILSY OS'}</span>
                        <span>
                          {msg.timestamp
                            ? new Date(msg.timestamp).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                              })
                            : ''}
                        </span>
                      </div>
                      <div className={styles.bubbleBody}>{msg.content}</div>
                    </div>
                  ))}
                  {isSubmitting && (
                    <div className={styles.chatMessageBubble + ' ' + styles.assistantBubble}>
                      <div className={styles.bubbleBody}>Consulting operator intelligence…</div>
                    </div>
                  )}
                  {errorMessage && <div className={styles.errorBanner}>{errorMessage}</div>}
                  <div ref={messagesEndRef} />
                </div>

                {!isLegalDockRole(authUser?.role) && <div style={{
                  padding: '8px 14px', color: '#e7edf9', fontSize: 12,
                  lineHeight: 1.45, flexShrink: 0,
                }}>
                  {!reasoningUsageConsent ? <label style={{ display: 'flex', gap: 9,
                    alignItems: 'center', textTransform: 'none', letterSpacing: 0,
                    fontWeight: 400, color: '#e7edf9' }}>
                    <input type="checkbox" checked={false}
                      onChange={event => updateUsageConsent(event.target.checked)}
                      aria-label="Confirm WILSY AI usage admission"
                      style={{ width: 18, height: 18, flexShrink: 0, accentColor: '#72b8ff' }}/>
                    <span style={{ textTransform: 'none', letterSpacing: 0, fontWeight: 400,
                      color: '#e7edf9' }}>Allow AI usage for this conversation</span>
                  </label> : null}
                  <details style={{ marginTop: 3, paddingLeft: reasoningUsageConsent ? 0 : 27,
                    color: '#cbd5e1', fontWeight: 400, textTransform: 'none',
                    letterSpacing: 0 }}>
                    <summary style={{ cursor: 'pointer', minHeight: 28, fontSize: 12,
                      textTransform: 'none', letterSpacing: 0, color: '#cbd5e1' }}>
                      {reasoningUsageConsent ? 'AI usage preferences' : 'Usage and permissions'}
                    </summary>
                    <p style={{ margin: '4px 0' }}>Each request may consume metered AI usage.
                      EOS checks your permissions, subscription entitlement and capacity.
                      For a verified project, EOS may send bounded project and task
                      excerpts to its configured AI provider to answer. Consent does not
                      authorize project changes, staffing decisions or payments.</p>
                    {reasoningUsageConsent && <button type="button"
                      onClick={() => updateUsageConsent(false)}
                      aria-label="Revoke AI usage consent"
                      style={{ minHeight: 36, color: '#e7edf9', textDecoration: 'underline',
                        textTransform: 'none', fontSize: 12 }}>
                      Revoke AI usage consent
                    </button>}
                  </details>
                </div>}
                <div className={styles.chatInputArea} style={{ flexShrink: 0 }}>
                  <textarea
                    className={styles.promptInput}
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    placeholder="Ask Wilsy OS…"
                    rows={2}
                    disabled={isSubmitting}
                  />
                  <button
                    type="button"
                    className={styles.sendButton}
                    onClick={() => handleSendMessage()}
                    disabled={isSubmitting || !prompt.trim()
                      || (!isLegalDockRole(authUser?.role) && (!reasoningUsageConsent || aiEntitlementNotProvisioned))}
                    aria-label="Send"
                  >
                    <SendHorizontal size={18} />
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'suggestions' && (
              <div className={styles.suggestionsTabContent}>
                <h4>Dynamic Sovereign Suggestions</h4>
                <div className={styles.suggestionsList}>
                  {(dynamicSuggestions || []).length === 0 && (
                    <p className={styles.emptyChatWelcome}>No suggestions for current posture.</p>
                  )}
                  {(dynamicSuggestions || []).map((sug, i) => (
                    <button
                      type="button"
                      key={sug.id || i}
                      className={styles.suggestionCard}
                      onClick={() => {
                        try {
                          recordWilsyAISuggestionUsage(sug.id);
                        } catch {
                          /* ignore */
                        }
                        setActiveTab('chat');
                        handleSendMessage(sug.prompt || sug.title);
                      }}
                    >
                      <Sparkles size={16} className={styles.sugIcon} />
                      <div>
                        <h5>{sug.title}</h5>
                        <p>{sug.description}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'legalAdvisory' && (
              <div className={styles.legalAdvisoryTab}>
                <div className={styles.legalAdvisoryHeader}>
                  <div>
                    <span className={styles.legalAdvisoryEyebrow}>Legal Advisory</span>
                    <h4>Evidence-backed Legal Advisory</h4>
                  </div>
                  <ShieldCheck size={22} aria-hidden="true" />
                </div>
                <p className={styles.legalAdvisoryNotice}>
                  Evidence-backed advisory · No execution authority
                </p>
                <div className={styles.legalAdvisoryPrompt}>
                  <label htmlFor="legal-advisory-prompt">Legal-service question</label>
                  <textarea
                    id="legal-advisory-prompt"
                    aria-label="Legal advisory prompt"
                    value={legalPrompt}
                    onChange={(event) => setLegalPrompt(event.target.value)}
                    placeholder="Describe the legal-service question…"
                    rows={4}
                    disabled={legalSubmitting}
                  />
                  <button
                    type="button"
                    className={styles.legalAdvisoryGenerate}
                    onClick={handleGenerateLegalAdvisory}
                    disabled={legalSubmitting || !legalPrompt.trim()}
                  >
                    <FileCheck2 size={16} />
                    {legalSubmitting ? 'Generating evidence-backed next action…' : 'Generate evidence-backed next action'}
                  </button>
                </div>

                {legalError && (
                  <div className={styles.legalAdvisoryError} role="alert" aria-live="assertive">
                    {legalError}
                  </div>
                )}

                {legalServiceResponse && (
                  <section className={styles.legalServiceResponse} aria-live="polite">
                    <h5>Legal service response</h5>
                    <p>{formatAdvisoryValue(legalServiceResponse.response_text)}</p>
                    <div className={styles.legalAdvisoryGrid}>
                      <div className={styles.legalAdvisoryField}>
                        <small>Orchestration ID</small>
                        <strong>{formatAdvisoryValue(legalServiceResponse.orchestration_id)}</strong>
                      </div>
                      <div className={styles.legalAdvisoryField}>
                        <small>Outcome</small>
                        <strong>{formatAdvisoryValue(legalServiceResponse.outcome)}</strong>
                      </div>
                    </div>
                    {Array.isArray(legalServiceResponse.sources) && legalServiceResponse.sources.length > 0 && (
                      <ul className={styles.legalAdvisorySourceList}>
                        {legalServiceResponse.sources.map((source, index) => (
                          <li key={`${formatAdvisoryValue(source)}-${index}`}>{formatAdvisoryValue(source)}</li>
                        ))}
                      </ul>
                    )}
                    {legalServiceResponse.outcome !== 'TOOL_ASSISTED' && (
                      <strong className={styles.legalAdvisoryNotGenerated}>
                        Evidence-backed advisory not generated
                      </strong>
                    )}
                  </section>
                )}

                {legalAdvisory && (
                  <section className={styles.legalAdvisoryCard} aria-label="Evidence-backed advisory">
                    <div className={styles.legalAdvisoryCardHeader}>
                      <div>
                        <span className={styles.legalAdvisoryEyebrow}>Evidence-backed advisory</span>
                        <h5>{formatAdvisoryValue(legalAdvisory.title)}</h5>
                      </div>
                      <span
                        className={`${styles.legalAdvisoryStatus} ${
                          legalStatus === 'STALE'
                            ? styles.legalAdvisoryStatusStale
                            : styles.legalAdvisoryStatusCurrent
                        }`}
                      >
                        {formatAdvisoryValue(legalAdvisory.status)}
                      </span>
                    </div>
                    <p className={styles.legalAdvisoryNoAuthority}>
                      Evidence-backed advisory · No execution authority
                    </p>
                    <div className={styles.legalAdvisoryGrid}>
                      <div className={styles.legalAdvisoryField}><small>Advisory ID</small><strong>{formatAdvisoryValue(legalAdvisory.advisory_id)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Scope reference</small><strong>{formatAdvisoryValue(legalAdvisory.scope_ref)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Rationale</small><strong>{formatAdvisoryValue(legalAdvisory.rationale)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Confidence score</small><strong>{formatConfidenceScore(legalAdvisory.confidence_score)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Confidence basis</small><strong>{formatAdvisoryValue(legalAdvisory.confidence_basis)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Risk level</small><strong>{formatAdvisoryValue(legalAdvisory.risk_level)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Generated at</small><strong>{formatAdvisoryValue(legalAdvisory.generated_at)}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Superseded by advisory ID</small><strong>{formatAdvisoryValue(legalAdvisory.superseded_by_advisory_id)}</strong></div>
                    </div>
                    <div className={styles.legalAdvisoryActions}>
                      <button type="button" className={styles.legalAdvisoryRefresh} onClick={handleRefreshLegalAdvisory} disabled={legalRefreshing}>
                        {legalRefreshing ? 'Refreshing status…' : 'Refresh status'}
                      </button>
                      {legalAdvisory.superseded_by_advisory_id && (
                        <button type="button" className={styles.legalAdvisoryRefresh} onClick={() => handleViewSuccessor(legalAdvisory.superseded_by_advisory_id)} disabled={legalRefreshing}>
                          <ArrowUpRight size={15} /> View successor
                        </button>
                      )}
                      <button type="button" className={styles.legalAdvisoryClear} onClick={clearLegalAdvisoryView}>
                        Clear local view
                      </button>
                    </div>
                  </section>
                )}
              </div>
            )}

            {activeTab === 'deadlineIntelligence' && isLegalDockRole(authUser?.role) && (
              <div className={styles.legalAdvisoryTab}>
                <div className={styles.legalAdvisoryHeader}>
                  <div>
                    <span className={styles.legalAdvisoryEyebrow}>Core Legal observation</span>
                    <h4>Matter deadline posture</h4>
                  </div>
                  <ShieldCheck size={22} aria-hidden="true" />
                </div>
                <p className={styles.legalAdvisoryNotice}>
                  Observed canonical deadline posture · Not legal advice or a recommendation
                </p>
                <div className={styles.legalAdvisoryPrompt}>
                  <label htmlFor="deadline-intelligence-matter">Matter identifier</label>
                  <input
                    id="deadline-intelligence-matter"
                    aria-label="Matter identifier for deadline observation"
                    value={deadlineMatterId}
                    onChange={(event) => setDeadlineMatterId(event.target.value)}
                    placeholder="Enter the exact matter identifier"
                    disabled={deadlineLoading}
                  />
                  <button
                    type="button"
                    className={styles.legalAdvisoryGenerate}
                    onClick={handleObserveDeadlines}
                    disabled={deadlineLoading || !deadlineMatterId.trim()}
                  >
                    <FileCheck2 size={16} />
                    {deadlineLoading ? 'Observing canonical deadlines…' : 'Observe deadline posture'}
                  </button>
                </div>
                {deadlineError && (
                  <div className={styles.legalAdvisoryError} role="alert" aria-live="assertive">
                    {deadlineError}
                  </div>
                )}
                {deadlineIntelligence && (
                  <section className={styles.legalAdvisoryCard} aria-label="Matter deadline observation">
                    <div className={styles.legalAdvisoryCardHeader}>
                      <div>
                        <span className={styles.legalAdvisoryEyebrow}>Observed at</span>
                        <h5>{formatAdvisoryValue(deadlineIntelligence.observedAt)}</h5>
                      </div>
                      <span className={styles.legalAdvisoryStatus}>READ ONLY</span>
                    </div>
                    <p className={styles.legalAdvisoryNoAuthority}>
                      No legal-period calculation · No court-rule inference · No reminder or execution authority
                    </p>
                    <div className={styles.legalAdvisoryGrid}>
                      <div className={styles.legalAdvisoryField}><small>Upcoming</small><strong>{deadlineIntelligence.upcomingCount}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Due</small><strong>{deadlineIntelligence.dueCount}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Overdue</small><strong>{deadlineIntelligence.overdueCount}</strong></div>
                      <div className={styles.legalAdvisoryField}><small>Inactive</small><strong>{deadlineIntelligence.inactiveCount}</strong></div>
                    </div>
                    {deadlineIntelligence.items.length === 0 ? (
                      <p>No canonical deadline facts were returned for this authorized matter.</p>
                    ) : (
                      <ul className={styles.legalAdvisorySourceList}>
                        {deadlineIntelligence.items.map((item) => (
                          <li key={item.deadlineId}>
                            <strong>{item.temporalPosture}</strong>
                            {' · '}{item.deadlineKind}{' · due '}{item.dueAt}
                            {' · '}{item.jurisdictionReference}
                          </li>
                        ))}
                      </ul>
                    )}
                  </section>
                )}
              </div>
            )}

            {activeTab === 'history' && (
              <div className={styles.historyTabContent}>
                <div className={styles.historyHeaderRow}>
                  <h4>Conversation Threads</h4>
                  <div className={styles.historyHeaderActions}>
                    <button type="button" className={styles.historyActionButton} onClick={handleNewThread}>+ New</button>
                    <button type="button" className={styles.historyActionButton} onClick={handleRefresh}>⟳ Sync</button>
                    <button
                      type="button"
                      className={styles.clearHistoryButton}
                      onClick={() => {
                        clearWilsyAIConversationThreads();
                        const fresh = [createWilsyAIConversationThread('New Sovereign Session')];
                        setConversationThreads(fresh);
                        setActiveThreadId(fresh[0].id);
                      }}
                    >
                      Clear
                    </button>
                  </div>
                </div>
                <div className={styles.threadsList}>
                  {conversationThreads.map((thread) => (
                    <button
                      type="button"
                      key={thread.id}
                      className={`${styles.threadCard} ${
                        thread.id === activeThreadId ? styles.activeThreadCard : ''
                      }`}
                      onClick={() => setActiveThreadId(thread.id)}
                    >
                      <MessageSquareText size={16} />
                      <div>
                        <h5>{thread.title || 'Sovereign Session'}</h5>
                        <span>{thread.messages?.length || 0} messages</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}

export default WilsyOSIntelligenceDock;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL ARTIFACT SEAL — Intelligence Dock v4.14.0-EXPLICIT-AI-COMMERCIAL-READINESS
 * ═══════════════════════════════════════════════════════════════════════════════
 * General Ask uses Python EOS /wilsy-ai/reasoning with explicit consent and admission;
 * legal roles retain separately certified C1C legal-services transport.
 * Phase 4.1 complete: "New Thread" & manual "Refresh/Sync" UX added.
 * Phase 4.1.1 complete: CSS classes for action buttons formally integrated.
 * M14-P7 complete: optional billing-intelligence evidence remains a separate
 * server-returned canonical projection and is explicitly named in operator context.
 * The dock now uses the sovereign Kennel for all intelligence generation.
 * C1E-R1C complete: legal advisories remain server-owned, read-only projections;
 * no legal command, execution, financial authority, or browser persistence exists.
 * D6B complete: Core Legal deadline posture is an independent read-only D6
 * projection and does not require or enlarge WILSY AI entitlement or authority.
 * Durable conversation history remains unmounted until a separately certified Python-EOS authority exists; current history is session-memory only.
 * ═══════════════════════════════════════════════════════════════════════════════
 * ARTIFACT: WilsyOSIntelligenceDock.jsx
 * VERSION: v4.14.0-EXPLICIT-AI-COMMERCIAL-READINESS
 * AUTHORITY BOUNDARY: client projection only; Python EOS owns C1C/C1E truth
 * TENANT POSTURE: authenticated api.js context; C1E state is React memory only
 * FAIL-CLOSED POSTURE: transport errors render bounded status and never fabricate
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
