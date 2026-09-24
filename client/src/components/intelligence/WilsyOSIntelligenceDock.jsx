/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign Intelligence Dock (Kennel Phase 4 – Backend Operator)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/src/components/intelligence/WilsyOSIntelligenceDock.jsx
 * Version:        v4.4.1-LEGAL-AUTHORITY-AWARE-ARTIFACT-INTEGRITY
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Authority-aware operator dock. Kernel posture comes only from
 *                 the canonical /kernel transport. Legal workspace Ask requests
 *                 use certified C1C legal-services transport rather than the
 *                 unmounted legacy /api/ai/operator route. Billing-intelligence
 *                 evidence is probed only for the bounded legal-finance role.
 *                 Conversation history is explicitly session-memory only until a
 *                 Python-EOS durable history authority is separately certified.
 * Classification: Production Artifact — Institutional Contract
 * Tenant Boundary: C1E payloads are server-scoped and rendered without client
 *                   tenant inference or persistence.
 * Authority Boundary: Python EOS owns legal advisory authority; this file is a
 *                     projection and exposes no legal command authority.
 * Financial Authority Boundary: None; Kennel EOS remains exclusive.
 * Compliance: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * Security / Privacy Posture: Authentication remains in api.js; C1E state is
 *                              held only in React memory.
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) – Mandated Kennel as Source of Truth.
 *   - AI Engineering – Phase 4: replace local engine with backend call.
 *
 * Change Log:
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
 * Forensic Relationships:
 *   Upstream:   ../../services/api, authContext/tenantContext (soft),
 *               suggestion + history engines
 *   Downstream: App shell, Boardroom, Founder chrome
 *   Kennel:     GET /kernel (health via canonical api.js transport)
 *               GET /billing/intelligence/evidence (LEGAL_FINANCE optimization only)
 *               C1C legal-services transport for legal workspace Ask
 *               C1C/C1E legal advisory transport (R1B adapter)
 *
 * Certification Seal: PRODUCTION_READY_v4.4.1-LEGAL-AUTHORITY-AWARE-ARTIFACT-INTEGRITY
 * ═══════════════════════════════════════════════════════════════════════════════
 */

/* eslint-disable */

import React, { useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import {
  ArrowUpRight,
  BrainCircuit,
  FileCheck2,
  History,
  MessageSquareText,
  Minimize2,
  PanelRightOpen,
  SendHorizontal,
  ShieldCheck,
  Sparkles,
  X,
} from 'lucide-react';
import api from '../../services/api.js'; // Sovereign HTTP client – forensic seals, tenant headers, auto refresh
import {
  executeWilsyAILegalServices,
  generateWilsyAILegalNextActions,
  readWilsyAILegalNextAction,
} from '../../services/wilsyAIAdvisoryApi.js';
import {
  buildWilsyDynamicSuggestions,
  recordWilsyAISuggestionUsage,
} from './wilsyAIDynamicSuggestionEngine.js';
import {
  clearWilsyAIConversationThreads,
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
 * @description Kennel Phase‑4 intelligence surface – sovereign api + backend operator.
 */
export function WilsyOSIntelligenceDock({
  authUser = null,
  activeTenant = null,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [prompt, setPrompt] = useState('');
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
  const messagesEndRef = useRef(null);

  /**
   * @function hydrateDockContext
   * @description Loads kennel posture via sovereign api – never window.fetch.
   * @collaboration Invoked on mount and during manual refresh.
   */
  const hydrateDockContext = useCallback(async () => {
    const fallback = buildWilsyAIProductivityCopy({
      result: 'LIVE_EMPTY',
      workspace: {
        operatingRole: authUser?.role || 'UNRESOLVED',
        focus: 'Authority graph',
        tenantId: activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId || '',
      },
    });

    let billingIntelligenceEvidence;
    if (canProbeBillingIntelligence(authUser?.role)) {
      try {
        const asOf = new Date().toISOString();
        const billingRes = await api.get('/billing/intelligence/evidence', {
          params: { as_of: asOf },
          timeout: 8000,
        });
        if (
          billingRes?.status === 200
          && billingRes?.data
          && typeof billingRes.data === 'object'
        ) {
          billingIntelligenceEvidence = billingRes.data;
        }
      } catch {
        // Optional finance evidence remains server-authorized and fail-quiet.
      }
    }

    try {
      // Kennel source of truth – public health probe on BFF
      const kernelRes = await api.get('/kernel', { timeout: 8000 });
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
      if (billingIntelligenceEvidence) {
        normalizedDockContext.billingIntelligenceEvidence = billingIntelligenceEvidence;
      }
      setDockContext(normalizedDockContext);
    } catch (err) {
      // Fallback when kernel is unreachable
      setDockContext(
        billingIntelligenceEvidence
          ? { ...fallback, billingIntelligenceEvidence }
          : fallback
      );
      setKennelPosture('SOURCE_SILENT');
      // Log silently in production; in dev we can show a warning
      if (import.meta.env.DEV) {
        console.warn('[IntelligenceDock] Kennel unreachable, using fallback context.', err);
      }
    }
  }, [authUser?.role, activeTenant?.tenantId, activeTenant?._id]);

  /**
   * @function handleNewThread
   * @description Creates a new conversation thread without clearing existing history.
   * @institutional Allows operators to compartmentalize conversations by topic.
   */
  const handleNewThread = useCallback(async () => {
    try {
      const fresh = await createWilsyAIConversationThread({
        title: 'New Sovereign Session',
        workspace: 'WILSY OS',
      });
      setConversationThreads((prev) => [fresh, ...prev.filter((item) => item.id !== fresh.id)]);
      setActiveThreadId(fresh.id);
    } catch (err) {
      setErrorMessage(err?.message || 'Failed to create a new thread.');
    }
  }, []);

  /**
   * @function handleRefresh
   * @description Manually refreshes the conversation list and Kennel context.
   * @institutional Prevents stale data from persisting after external updates.
   */
  const handleRefresh = useCallback(async () => {
    setErrorMessage('');
    try {
      const refreshed = await loadWilsyAIConversationThreads();
      setConversationThreads(refreshed);
      if (!refreshed.find(t => t.id === activeThreadId)) {
        setActiveThreadId(refreshed[0]?.id || null);
      }
      await hydrateDockContext(); // Also refresh kennel context
    } catch (err) {
      setErrorMessage('Failed to refresh threads.');
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
      await hydrateDockContext();
    };
    void hydrate();
    return () => { active = false; };
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
   * @description Authority-aware Ask turn: legal roles use certified C1C legal-services transport; other roles use shared api.post('/ai/operator', ...).
   */
  const handleSendMessage = useCallback(
    async (rawText) => {
      const text = String(rawText || prompt).trim();
      if (!text || isSubmitting) return;

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
          threadId = fresh.id;
          setActiveThreadId(threadId);
          setConversationThreads((prev) => [fresh, ...prev.filter((t) => t.id !== fresh.id)]);
        }
        const afterUser = await persistWilsyAIConversationTurn({
          threadId,
          message: userTurn,
        });
        setConversationThreads((prev) => [
          afterUser,
          ...prev.filter((item) => item.id !== afterUser.id),
        ]);
      } catch (err) {
        setErrorMessage(err?.message || 'Failed to record operator turn.');
        setIsSubmitting(false);
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
          const { billingIntelligenceEvidence, ...operatorDockContext } = dockContext || {};
          const requestBody = {
            prompt: text,
            context: {
              ...operatorDockContext,
              ...(billingIntelligenceEvidence
                ? { canonicalBillingIntelligenceEvidence: billingIntelligenceEvidence }
                : {}),
              threadId,
              history: activeThread?.messages || [],
            },
            forcedIntent: '',
            kennelPosture,
          };

          const response = await api.post('/ai/operator', requestBody, {
            headers: {
              'X-Tenant-Id': activeTenant?.tenantId || activeTenant?._id || authUser?.tenantId || '',
              'X-Wilsy-Kennel-Posture': kennelPosture,
            },
            timeout: 30000,
          });
          result = response?.data?.intelligence || response?.data?.data || null;
          if (!result) throw new Error('Backend returned empty intelligence.');
        }

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
        setConversationThreads((prev) => [
          afterAssistant,
          ...prev.filter((item) => item.id !== afterAssistant.id),
        ]);
      } catch (err) {
        // Fallback: use local engine only if backend fails (but Phase 4 removes local engine)
        // We can either show an error or use a simple fallback message.
        setErrorMessage(err?.message || 'Backend intelligence failed. Please try again.');
        const failTurn = {
          role: 'assistant',
          content:
            'I could not reach the Wilsy Operator Kernel. Check the Kennel status or retry later. Error: ' +
            (err?.message || 'unknown'),
          timestamp: new Date().toISOString(),
        };
        try {
          const afterFail = await persistWilsyAIConversationTurn({
            threadId,
            message: failTurn,
          });
          setConversationThreads((prev) => [
            afterFail,
            ...prev.filter((item) => item.id !== afterFail.id),
          ]);
        } catch {
          /* ignore */
        }
      } finally {
        setIsSubmitting(false);
      }
    },
    [
      prompt,
      isSubmitting,
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

  const operatorLabel =
    authUser?.displayName ||
    authUser?.name ||
    authUser?.email ||
    'Operator';
  const legalStatus = String(legalAdvisory?.status || '').toUpperCase();
  const authoritativeTenantBrand = resolveAuthoritativeTenantBrand(activeTenant);

  return (
    <div className={styles.intelligenceDockContainer} data-wilsy-intelligence-dock="active" data-kennel={kennelPosture}>
      {!isOpen && (
        <button
          type="button"
          className={styles.dockLauncherButton}
          onClick={() => setIsOpen(true)}
          title="Open Wilsy OS Intelligence Dock"
        >
          <Sparkles className={styles.launcherIcon} />
          <span>WILSY OS</span>
        </button>
      )}

      {isOpen && (
        <div className={`${styles.dockWindow} ${isExpanded ? styles.dockExpanded : ''}`}>
          <div className={styles.dockHeader}>
            <div className={styles.dockHeaderTitle}>
              <BrainCircuit className={styles.headerLogo} />
              <div>
                <span>WILSY OS Intelligence Dock</span>
                <small className={styles.kennelBadge} data-posture={kennelPosture}>
                  Kennel {kennelPosture}
                </small>
                {authoritativeTenantBrand && (
                  <small className={styles.workspaceBrand} data-brand-source="ACTIVE_TENANT_CONTEXT">
                    {authoritativeTenantBrand}
                  </small>
                )}
              </div>
            </div>
            <div className={styles.dockHeaderActions}>
              <button
                type="button"
                className={styles.headerIconButton}
                onClick={() => setIsExpanded(!isExpanded)}
                title={isExpanded ? 'Minimize dock' : 'Expand dock'}
              >
                {isExpanded ? <Minimize2 size={16} /> : <PanelRightOpen size={16} />}
              </button>
              <button
                type="button"
                className={styles.headerIconButton}
                onClick={() => setIsOpen(false)}
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
                <div className={styles.messagesContainer}>
                  {(!activeThread?.messages || activeThread.messages.length === 0) && (
                    <div className={styles.emptyChatWelcome}>
                      <ShieldCheck size={32} className={styles.welcomeShield} />
                      <h4>Sovereign Intelligence Ready</h4>
                      <p>
                        {dockContext?.result ||
                          'Ask about CRM, billing ledger, legal drafts, or tenant posture. Turns run through the Kennel-aware operator engine.'}
                      </p>
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

                <div className={styles.chatInputArea}>
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
                    disabled={isSubmitting || !prompt.trim()}
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
        </div>
      )}
    </div>
  );
}

export default WilsyOSIntelligenceDock;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — Intelligence Dock v4.4.1-LEGAL-AUTHORITY-AWARE-ARTIFACT-INTEGRITY
 * ═══════════════════════════════════════════════════════════════════════════════
 * Generic Ask uses the canonical shared api.js POST /ai/operator transport; legal roles use certified C1C legal-services transport.
 * Phase 4.1 complete: "New Thread" & manual "Refresh/Sync" UX added.
 * Phase 4.1.1 complete: CSS classes for action buttons formally integrated.
 * M14-P7 complete: optional billing-intelligence evidence remains a separate
 * server-returned canonical projection and is explicitly named in operator context.
 * The dock now uses the sovereign Kennel for all intelligence generation.
 * C1E-R1C complete: legal advisories remain server-owned, read-only projections;
 * no legal command, execution, financial authority, or browser persistence exists.
 * Durable conversation history remains unmounted until a separately certified Python-EOS authority exists; current history is session-memory only.
 * ═══════════════════════════════════════════════════════════════════════════════
 * ARTIFACT: WilsyOSIntelligenceDock.jsx
 * VERSION: v4.4.1-LEGAL-AUTHORITY-AWARE-ARTIFACT-INTEGRITY
 * AUTHORITY BOUNDARY: client projection only; Python EOS owns C1C/C1E truth
 * TENANT POSTURE: authenticated api.js context; C1E state is React memory only
 * FAIL-CLOSED POSTURE: transport errors render bounded status and never fabricate
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
