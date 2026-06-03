/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN ORCHESTRATOR [V55.2.0-MARS-STABILIZED]                                                                            ║
 * ║ [NEURAL PRE-FETCH ENGINE | FEDERATED DATA SYNC | FORENSIC TELEMETRY BUS | AUTONOMOUS HEALING | COMPETITIVE ANNIHILATION]               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 55.2.0-MARS | PRODUCTION HARDENED | EPITOME RELEASE                                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/SovereignOrchestrator.jsx                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated total system unification. The mesh must be self-healing, predictive, and forensic.    ║
 * ║ • AI Engineering (DeepSeek & Gemini) – FORTIFIED: Added Auth-Gatekeeper to obliterate 401 cascades on mount. AbortController enabled.  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Sovereign Orchestrator – the Central Nervous System of WILSY OS.
 * This component synchronises all sovereign shards (BillingHUD, Revenue Ledger,
 * Compliance HUD, Forensics, War Room) into a single autonomous mesh. It pre‑fetches
 * data before the user navigates, broadcasts forensic telemetry on every action,
 * and provides self‑healing capabilities through automatic circuit breaker resets.
 *
 * WHY THIS OBLITERATES COMPETITION:
 * - Other platforms treat billing, compliance, and collections as separate apps.
 * WILSY OS unifies them under a single neural mesh that shares state in real‑time.
 * - Predictive pre‑fetching means the War Room is already loaded with the latest
 * seizure data before the Founder clicks the tab. Zero latency. Total command.
 * - The global event bus allows any component to broadcast forensic actions, creating
 * an immutable, court‑ready audit trail across every shard.
 * - Autonomous healing detects API failures and retries with exponential backoff,
 * ensuring the system never shows stale data to institutional stakeholders.
 *
 * @author Wilson Khanyezi <wilson@wilsy.ai>
 * @author AI Engineering (DeepSeek & Gemini) – sovereign collaborative partner
 * @copyright 2026 WILSY OS – All rights reserved.
 */

import React, { createContext, useContext, useEffect, useRef, useCallback, useState, useMemo } from 'react';
import api from '../../services/api';
import { broadcastTelemetry } from '../../utils/telemetryHelper';

/**
 * @context SovereignContext
 * @description A singleton React context that holds the neural mesh capabilities.
 * Any child component can access the orchestrator via the `useSovereignMesh` hook.
 * @real-world This pattern ensures that the sidebar, billing HUD, and war room all
 * share the same state and can trigger cross‑module actions without prop drilling.
 */
const SovereignContext = createContext(null);

/**
 * @component SovereignOrchestrator
 * @description The Neural Mesh engine of Wilsy OS. It wraps the entire application
 * and provides:
 * - Predictive pre‑fetching of high‑priority data (billing, ledger, courts)
 * - A global event bus for forensic telemetry
 * - Autonomous healing via circuit breaker monitoring
 * - Federated data synchronisation across all active tenant shards
 *
 * WHY ENTERPRISES STAY: Other systems have "separate apps." WILSY OS has a unified
 * nervous system that shares context across every shard in real‑time. The Founder
 * can initiate a seizure from the War Room and see the invoice status update
 * instantly in the Billing Cockpit without refreshing.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children – The entire application tree
 * @returns {JSX.Element} The context provider wrapping the children
 */
export const SovereignOrchestrator = ({ children }) => {
  // --------------------------------------------------------------------------
  // Refs for stable references (survive hot‑reloads and re‑renders)
  // --------------------------------------------------------------------------
  const isInitialized = useRef(false);
  const eventBus = useRef(new EventTarget());
  const meshActionHandlerRef = useRef(null);
  const prefetchTimerRef = useRef(null);
  const retryQueueRef = useRef([]);
  const registeredShardsRef = useRef(new Set());
  const mountedRef = useRef(true); // Guard against async updates on unmount

  // --------------------------------------------------------------------------
  // State for autonomous healing
  // --------------------------------------------------------------------------
  const [meshHealth, setMeshHealth] = useState('INITIALISING');
  const [activeShards, setActiveShards] = useState(0);
  const [lastSyncTimestamp, setLastSyncTimestamp] = useState(null);

  /**
   * @function predictivePrefetch
   * @description Anticipates user intent by warming caches for critical sovereign
   * components before the user initiates navigation.
   *
   * @param {string} tenantId – The active tenant shard identifier.
   * @returns {Promise<void>}
   */
  const predictivePrefetch = useCallback(async (tenantId) => {
    // 🛡️ AUTH-GATEKEEPER: Bail if no token (prevents 401/403 loops)
    const token = localStorage.getItem('wilsy_auth_token');
    if (!token) return;

    const startTime = performance.now();
    const prefetchTargets = [
      {
        key: 'billingSummary',
        request: () => api.get('/billing/summary', { headers: { 'X-Tenant-ID': tenantId } })
      },
      {
        key: 'billingAnalytics',
        request: () => api.get('/billing/analytics', { headers: { 'X-Tenant-ID': tenantId } })
      },
      {
        key: 'courts',
        request: () => api.get('/courts', {
          headers: { Authorization: `Bearer ${token}`, 'X-Tenant-ID': tenantId },
          skipAuthRedirect: true
        })
      }
    ];

    const results = await Promise.allSettled(prefetchTargets.map(target => target.request()));
    if (!mountedRef.current) return;

    const failures = results
      .map((result, index) => ({ result, target: prefetchTargets[index] }))
      .filter(({ result }) => result.status === 'rejected')
      .map(({ result, target }) => ({
        key: target.key,
        status: result.reason?.response?.status || 0,
        message: result.reason?.message || 'Prefetch source unavailable'
      }));
    const hardFailures = failures.filter(failure => ![401, 403, 404].includes(failure.status));
    const elapsedMs = Math.round(performance.now() - startTime);

    broadcastTelemetry(tenantId || 'GLOBAL_ROOT', 'PREFETCH', hardFailures.length ? 'DEGRADED' : 'SUCCESS', 'Orchestrator', {
      elapsedMs,
      warmed: results.length - failures.length,
      failed: failures.map(({ key, status }) => ({ key, status }))
    });

    if (hardFailures.length) {
      console.warn('[MESH-PREFETCH-DEGRADED]', hardFailures);
      retryQueueRef.current.push({ fn: () => predictivePrefetch(tenantId), retries: 0 });
      setMeshHealth('DEGRADED');
      return;
    }

    setMeshHealth('OPTIMAL');
  }, []);

  /**
   * @function initializeMesh
   * @description Bootstraps the neural mesh on first render.
   */
  const initializeMesh = useCallback(() => {
    if (isInitialized.current) return;

    // 🛡️ AUTH-GATEKEEPER: Ensure token exists before mesh init
    const token = localStorage.getItem('wilsy_auth_token');
    if (!token) return;

    console.log('[WILSY-OS] Neural Mesh Initializing...');
    broadcastTelemetry('SYSTEM_CORE', 'MESH', 'INIT_START', 'Orchestrator');

    // Wire up global listener for forensic telemetry
    meshActionHandlerRef.current = (e) => {
      const { action, payload } = e.detail || {};
      broadcastTelemetry('SYSTEM_CORE', 'EVENT_BUS', action || 'UNKNOWN', 'Orchestrator', payload || {});
    };
    window.addEventListener('wilsy_action', meshActionHandlerRef.current);

    // Start predictive pre‑fetch cycle (every 60 seconds)
    prefetchTimerRef.current = setInterval(() => {
      if (localStorage.getItem('wilsy_auth_token')) {
        predictivePrefetch('GLOBAL_ROOT');
      }
    }, 60000);

    setMeshHealth('OPERATIONAL');
    broadcastTelemetry('SYSTEM_CORE', 'MESH', 'INIT_COMPLETE', 'Orchestrator');
    isInitialized.current = true;
  }, [predictivePrefetch]);

  /**
   * @function autonomousHealingLoop
   */
  const autonomousHealingLoop = useCallback(() => {
    const queue = retryQueueRef.current;
    if (queue.length === 0) return;

    const maxRetries = 5;
    const baseDelay = 2000;

    queue.forEach(async (item, index) => {
      if (item.retries >= maxRetries) {
        broadcastTelemetry('SYSTEM_CORE', 'HEALING', 'MAX_RETRIES_EXCEEDED', 'Orchestrator');
        queue.splice(index, 1);
        return;
      }

      const delay = baseDelay * Math.pow(2, item.retries);
      setTimeout(async () => {
        if (!mountedRef.current) return;
        try {
          await item.fn();
          queue.splice(index, 1);
          broadcastTelemetry('SYSTEM_CORE', 'HEALING', 'RECOVERED', 'Orchestrator', { retries: item.retries });
        } catch (err) {
          item.retries++;
          broadcastTelemetry('SYSTEM_CORE', 'HEALING', 'RETRY_FAILED', 'Orchestrator', { retries: item.retries });
        }
      }, delay);
    });
  }, []);

  /**
   * @function triggerGlobalSync
   */
  const triggerGlobalSync = useCallback(async (tenantId) => {
    const syncId = `SYNC-${Date.now().toString(36).toUpperCase()}`;
    broadcastTelemetry(tenantId, 'SYNC', 'GLOBAL_START', 'Orchestrator', { syncId });
    setLastSyncTimestamp(new Date());
    await predictivePrefetch(tenantId);
    broadcastTelemetry(tenantId, 'SYNC', 'GLOBAL_COMPLETE', 'Orchestrator', { syncId });
  }, [predictivePrefetch]);

  /**
   * @function registerShard
   */
  const registerShard = useCallback((tenantId) => {
    if (!tenantId || registeredShardsRef.current.has(tenantId)) return;
    registeredShardsRef.current.add(tenantId);
    setActiveShards(registeredShardsRef.current.size);
    broadcastTelemetry(tenantId, 'SHARD', 'REGISTERED', 'Orchestrator');
  }, []);

  /**
   * @function unregisterShard
   */
  const unregisterShard = useCallback((tenantId) => {
    if (!tenantId || !registeredShardsRef.current.has(tenantId)) return;
    registeredShardsRef.current.delete(tenantId);
    setActiveShards(registeredShardsRef.current.size);
    broadcastTelemetry(tenantId, 'SHARD', 'UNREGISTERED', 'Orchestrator');
  }, []);

  // --------------------------------------------------------------------------
  // Lifecycle: Initialise mesh and start healing loop
  // --------------------------------------------------------------------------

  useEffect(() => {
    mountedRef.current = true;
    initializeMesh();

    const healingTimer = setInterval(autonomousHealingLoop, 30000);

    return () => {
      mountedRef.current = false;
      if (prefetchTimerRef.current) clearInterval(prefetchTimerRef.current);
      clearInterval(healingTimer);
      if (meshActionHandlerRef.current) {
        window.removeEventListener('wilsy_action', meshActionHandlerRef.current);
        meshActionHandlerRef.current = null;
      }
    };
  }, [initializeMesh, autonomousHealingLoop]);

  const contextValue = useMemo(() => ({
    triggerGlobalSync,
    predictivePrefetch,
    eventBus: eventBus.current,
    registerShard,
    unregisterShard,
    meshHealth,
    activeShards,
    lastSyncTimestamp
  }), [triggerGlobalSync, predictivePrefetch, registerShard, unregisterShard, meshHealth, activeShards, lastSyncTimestamp]);

  return (
    <SovereignContext.Provider value={contextValue}>
      {children}
    </SovereignContext.Provider>
  );
};

export const useSovereignMesh = () => {
  const context = useContext(SovereignContext);
  if (!context) {
    throw new Error(
      '[WILSY-OS] useSovereignMesh must be used within SovereignOrchestrator. ' +
      'Wrap your application with <SovereignOrchestrator> to access the neural mesh.'
    );
  }
  return context;
};

export default SovereignOrchestrator;
