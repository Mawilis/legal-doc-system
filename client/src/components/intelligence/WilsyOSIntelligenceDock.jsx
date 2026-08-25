/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign Intelligence Dock (Kennel Phase 4 – Backend Operator)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/src/components/intelligence/WilsyOSIntelligenceDock.jsx
 * Version:        v4.1.1-KENNEL-PHASE4
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Operator AI dock. Uses sovereign `api` service exclusively.
 *                 Kennel health and registry are fetched via `/kernel` and
 *                 `/source-registry/health`. Assistant replies are generated via
 *                 backend `POST /api/ai/operator` – Phase 4 complete.
 * Classification: Production Artifact — Institutional Contract
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) – Mandated Kennel as Source of Truth.
 *   - AI Engineering – Phase 4: replace local engine with backend call.
 *
 * Change Log:
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
 *   Kennel:     GET /api/kernel (health) + GET /source-registry/health (optional)
 *               POST /api/ai/operator (Phase 4)
 *
 * Certification Seal: PRODUCTION_READY_v4.1.1-KENNEL-PHASE4
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import React, { useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import {
  BrainCircuit,
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
 * @institutional Ensures fallback data is provided when the source registry is silent.
 */
function buildWilsyAIProductivityCopy(payload = {}) {
  if (!payload || typeof payload !== 'object') {
    return {
      result: 'Workspace intelligence active',
      workspace: { operatingRole: 'Operator', focus: 'Authority graph' },
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
    result: humanizeWilsyAIBackendToken(payload.result || payload.status) || 'Workspace intelligence active',
    bridge: humanizeWilsyAIBackendToken(payload.bridge),
    workspace: {
      ...(payload.workspace || {}),
      focus: payload.workspace?.focus || 'Authority graph',
      operatingRole: payload.workspace?.operatingRole || 'Security Admin',
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
 * @function WilsyOSIntelligenceDock
 * @description Kennel Phase‑4 intelligence surface – sovereign api + backend operator.
 */
export function WilsyOSIntelligenceDock() {
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
  const messagesEndRef = useRef(null);

  // Optional React context (auth / tenant) – soft failure if outside providers
  // We'll read from window globals as fallback (populated by auth provider)
  const authUser = typeof window !== 'undefined' ? window.__WILSY_AUTH_USER__ : null;
  const activeTenant = typeof window !== 'undefined' ? window.__WILSY_ACTIVE_TENANT__ : null;

  /**
   * @function hydrateDockContext
   * @description Loads kennel posture via sovereign api – never window.fetch.
   * @collaboration Invoked on mount and during manual refresh.
   */
  const hydrateDockContext = useCallback(async () => {
    const fallback = buildWilsyAIProductivityCopy({
      result: 'Workspace intelligence active',
      workspace: {
        operatingRole: authUser?.role || 'Founder & Architect',
        focus: 'Authority graph',
        tenantId: activeTenant?.tenantId || activeTenant?._id || 'MASTER',
      },
    });

    try {
      // Kennel source of truth – public health probe on BFF
      const kernelRes = await api.get('/kernel', { timeout: 8000 });
      const kernel = kernelRes?.data || {};
      const live = String(kernel.status || '').toUpperCase() === 'OPERATIONAL';
      setKennelPosture(live ? 'OPERATIONAL' : 'DEGRADED');

      let registry = {};
      try {
        const regRes = await api.get('/source-registry/health', {
          params: { wilsyAiContext: 'RESOLVE' },
          timeout: 6000,
        });
        if (regRes?.status === 200) registry = regRes.data || {};
      } catch {
        // optional surface – quiet
      }

      setDockContext(
        buildWilsyAIProductivityCopy({
          ...registry,
          result: live ? 'WILSY_AI_SOVEREIGN_CONTEXT_RESOLVED' : registry.result,
          kennel: kernel,
          bridge: kernel.bridge || registry.bridge,
          workspace: {
            ...(registry.workspace || {}),
            operatingRole: authUser?.role || registry.workspace?.operatingRole || 'Founder & Architect',
            tenantId: activeTenant?.tenantId || activeTenant?._id || registry.workspace?.tenantId || 'MASTER',
          },
        })
      );
    } catch (err) {
      // Fallback when kernel is unreachable
      setDockContext(fallback);
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
  const handleNewThread = useCallback(() => {
    try {
      const fresh = createWilsyAIConversationThread('New Sovereign Session');
      setConversationThreads(prev => [fresh, ...prev]);
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
      const refreshed = loadWilsyAIConversationThreads() || [];
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
    let threads = [];
    try {
      threads = loadWilsyAIConversationThreads() || [];
    } catch {
      threads = [];
    }
    if (!threads.length) {
      const fresh = createWilsyAIConversationThread('New Sovereign Session');
      threads = [fresh];
    }
    setConversationThreads(threads);
    setActiveThreadId(threads[0]?.id || null);
    hydrateDockContext();
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
   * @description Operator turn – uses backend POST /api/ai/operator (Phase 4).
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
          const fresh = createWilsyAIConversationThread(
            text.slice(0, 48) || 'New Sovereign Session'
          );
          threadId = fresh.id;
          setActiveThreadId(threadId);
          setConversationThreads((prev) => [fresh, ...prev.filter((t) => t.id !== fresh.id)]);
        }
        const afterUser = persistWilsyAIConversationTurn(threadId, userTurn);
        setConversationThreads([...afterUser]);
      } catch (err) {
        setErrorMessage(err?.message || 'Failed to record operator turn.');
        setIsSubmitting(false);
        return;
      }

      try {
        // --- Phase 4: Backend call to /api/ai/operator ---
        const requestBody = {
          prompt: text,
          context: {
            ...dockContext,
            threadId,
            history: activeThread?.messages || [],
          },
          forcedIntent: '',
          kennelPosture: kennelPosture,
        };

        // Inject tenant header via api service (already handles x-tenant-id)
        // We can also pass tenantId in body for explicit scoping
        const response = await api.post('/api/ai/operator', requestBody, {
          headers: {
            'X-Tenant-Id': activeTenant?.tenantId || activeTenant?._id || 'MASTER',
            'X-Wilsy-Kennel-Posture': kennelPosture,
          },
          timeout: 30000, // Allow up to 30s for engine reasoning
        });

        const result = response?.data?.intelligence || response?.data?.data || null;
        if (!result) {
          throw new Error('Backend returned empty intelligence.');
        }

        const content =
          result?.reply ||
          result?.content ||
          result?.message ||
          result?.answer ||
          result?.result ||
          'Sovereign intelligence processed your request. Refine the prompt or open the related module for live data.';

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
            tenantId: result?.tenantId || activeTenant?.tenantId || 'MASTER',
          },
        };

        const afterAssistant = persistWilsyAIConversationTurn(threadId, assistantTurn);
        setConversationThreads([...afterAssistant]);
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
          const afterFail = persistWilsyAIConversationTurn(threadId, failTurn);
          setConversationThreads([...afterFail]);
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

  const operatorLabel =
    authUser?.displayName ||
    authUser?.name ||
    authUser?.email ||
    'Operator';

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
          <span>Wilsy AI</span>
        </button>
      )}

      {isOpen && (
        <div className={`${styles.dockWindow} ${isExpanded ? styles.dockExpanded : ''}`}>
          <div className={styles.dockHeader}>
            <div className={styles.dockHeaderTitle}>
              <BrainCircuit className={styles.headerLogo} />
              <div>
                <span>Wilsy OS Intelligence Dock</span>
                <small className={styles.kennelBadge} data-posture={kennelPosture}>
                  Kennel {kennelPosture}
                </small>
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
              <span>Ask Wilsy</span>
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
                        <span>{msg.role === 'user' ? operatorLabel : 'Wilsy AI'}</span>
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
 * INSTITUTIONAL CERTIFICATION SEAL — Intelligence Dock v4.1.1-KENNEL-PHASE4
 * ═══════════════════════════════════════════════════════════════════════════════
 * Phase 4 complete: local engine replaced with backend POST /api/ai/operator.
 * Phase 4.1 complete: "New Thread" & manual "Refresh/Sync" UX added.
 * Phase 4.1.1 complete: CSS classes for action buttons formally integrated.
 * The dock now uses the sovereign Kennel for all intelligence generation.
 * Phase 5 next: move conversation history to server (tenant‑scoped).
 * ═══════════════════════════════════════════════════════════════════════════════
 */
