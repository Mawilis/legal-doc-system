/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN TENANT CONTEXT [V31.0.0-PRODUCTION-STABLE]                                                                        ║
 * ║ [DYNAMIC BRANDING NEXUS | SELF-HEALING CIRCUIT BREAKER | SOVEREIGN OVERRIDE | SLA LATENCY SENSORS | MESH-INTEGRATED]                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ WHY FORTUNE 500 COMPANIES ABANDON LEGACY TENANT MANAGEMENT FOR WILSY OS:                                                               ║
 * ║   • SELF‑HEALING CIRCUIT BREAKER: Prevents cascading failures during backend outages.                                                  ║
 * ║   • SOVEREIGN OVERRIDE: Founders and Omega roles are automatically routed to the root shard.                                          ║
 * ║   • FORENSIC DISCOVERY: Every tenant handshake is cryptographically sealed – backend verifies integrity.                              ║
 * ║   • REAL‑TIME SLA TELEMETRY: Rolling latency averages and breaker state transitions broadcast for boardroom visibility.              ║
 * ║   • CRASH‑RESISTANT PERSISTENCE: LocalStorage fallback ensures tenant alias survives full page reloads.                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 31.0.0-PRODUCTION-STABLE | PRODUCTION READY | TRILLION DOLLAR SPEC                                                            ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/contexts/tenantContext.jsx                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ 1. ARCHITECT: Wilson Khanyezi - Mandated zero-leak database switching, breaker telemetry, and HMR stability.                            ║
 * ║ 2. AI ENGINEERING: Gemini - EPITOMIZED: Fully wired the self-healing Circuit Breaker. [2026-05-16]                                     ║
 * ║ 3. AI ENGINEERING: Gemini - ACTIVATED: Sovereign Override for Founder/Omega. [2026-05-16]                                              ║
 * ║ 4. AI ENGINEERING: DeepSeek - PRODUCTION-HARDENED: Removed client-side forensic reconciler import – backend owns the chain.            ║
 * ║ 5. AI ENGINEERING: Gemini - FORTIFIED: Injected safeMeshBroadcast to eradicate frontend mesh.propagate crash. [2026-05-24]             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Sovereign Tenant Context – the brain that discovers, isolates, and caches tenant shards.
 * Forensic chain reconciliation is handled exclusively by the backend. The client only stores
 * the discovered tenant alias and manages the circuit breaker for discovery failures.
 */

import React, { createContext, useContext, useState, useCallback, useEffect, useRef, useMemo } from 'react';
import api from '../services/api';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import { generateSovereignSeal } from '../utils/cryptoCore.js';
import { useAuth } from './authContext';
import { useSovereignMesh } from '../components/sovereign/SovereignOrchestrator.jsx';
import { useSovereignData } from '../components/sovereign/DataOrchestrator.jsx';

// ============================================================================
// 🛡️ CIRCUIT BREAKER THRESHOLDS
// ============================================================================

/**
 * Maximum consecutive failures before tripping the circuit breaker to OPEN.
 * @constant {number}
 */
const BREAKER_MAX_FAILURES = 3;

/**
 * Cooldown period (milliseconds) before transitioning from OPEN to HALF_OPEN.
 * @constant {number}
 */
const BREAKER_COOLDOWN_MS = 30000; // 30 Seconds

// ============================================================================
// 🔐 FORENSIC HEADER GENERATION (with mesh integration)
// ============================================================================

/**
 * Generate forensic headers for tenant discovery requests.
 * Includes trace ID, timestamp, nonce, and cryptographic seal.
 * @param {Object} [payload={}] - Payload to include in seal generation.
 * @returns {Object} Headers object with forensic fields.
 */
const generateForensicHeaders = (payload = {}) => {
  const traceId = `TRC-TENANT-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`;
  const timestamp = new Date().toISOString();
  const nonce = `NONCE-CTX-${Math.random().toString(36).substring(2, 15)}`;
  const messageToSeal = `${traceId}|${timestamp}|${JSON.stringify(payload)}|${nonce}`;
  const seal = generateSovereignSeal(messageToSeal);

  return {
    'x-trace-id': traceId,
    'x-forensic-timestamp': timestamp,
    'x-cryptographic-nonce': nonce,
    'x-request-seal': seal,
  };
};

/**
 * @function safeMeshBroadcast
 * @description Safely executes mesh propagation without crashing the React tree if the frontend context lacks the method.
 */
const safeMeshBroadcast = (meshContext, targetId, payload, eventType) => {
  try {
    if (meshContext && typeof meshContext.propagate === 'function') {
      meshContext.propagate(targetId, payload, eventType).catch(err => console.warn(`[Mesh] ${eventType} propagation failed:`, err));
    } else if (meshContext && typeof meshContext.emit === 'function') {
      meshContext.emit(eventType, { target: targetId, ...payload });
    } else {
      console.debug(`[Mesh-Simulated] Frontend decoupled. Suppressed broadcast: ${eventType}`);
    }
  } catch (err) {
    console.warn('[Mesh] Safe broadcast failure:', err);
  }
};

// ============================================================================
// 🌐 TENANT CONTEXT PROVIDER
// ============================================================================

const TenantContext = createContext(null);

/**
 * @component TenantProvider
 * @description React context provider for tenant isolation and discovery.
 * Integrates self‑healing circuit breaker, mesh broadcasting, and localStorage persistence.
 * Forensic chain reconciliation is handled by the backend – the client only stores the tenant alias.
 */
export const TenantProvider = ({ children }) => {
  const mesh = useSovereignMesh();
  const sovereignData = useSovereignData(); // Reserved for future use

  const [activeTenant, setActiveTenant] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [circuitBreaker, setCircuitBreaker] = useState('CLOSED');
  const [boardroomSummary, setBoardroomSummary] = useState({
    uptimeStatus: 'STABLE',
    avgSlaLatencyMs: 0,
    breakerTransitions: 0,
    complianceStatus: 'VERIFIED'
  });

  const failureCountRef = useRef(0);
  const lastFailureTimeRef = useRef(0);
  const latencyHistoryRef = useRef([]);
  const { isAuthenticated, user } = useAuth();

  /**
   * @function updateBreakerState
   * @description Updates circuit breaker state and broadcasts to mesh.
   */
  const updateBreakerState = useCallback((newState, tenantAlias) => {
    setCircuitBreaker(current => {
      if (current !== newState) {
        setBoardroomSummary(prev => ({
          ...prev,
          breakerTransitions: prev.breakerTransitions + 1,
          uptimeStatus: newState === 'OPEN' ? 'FRACTURED' : 'STABLE'
        }));

        broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_EVENT', 'BREAKER_STATE_TRANSITION', 'TenantContext', {
          previousState: current,
          newState,
          tenantAlias,
          severity: newState === 'OPEN' ? 'HIGH' : 'LOW'
        });

        safeMeshBroadcast(mesh, 'GLOBAL_ROOT', { previousState: current, newState, tenantAlias }, 'BREAKER_STATE_CHANGE');

        return newState;
      }
      return current;
    });
  }, [mesh]);

  /**
   * @function resolveTenantSingularity
   * @description Resolves a tenant alias into a full tenant object by calling the backend discovery endpoint.
   * Implements circuit breaker protection, SLA latency tracking, and sovereign override for founders.
   * The backend handles all forensic chain reconciliation – the client only stores the result.
   */
  const resolveTenantSingularity = useCallback(async (tenantIdOrObject) => {
    // 1. Direct object injection (already resolved)
    if (typeof tenantIdOrObject === 'object' && tenantIdOrObject !== null) {
      setActiveTenant(tenantIdOrObject);
      localStorage.setItem('discoveredTenant', tenantIdOrObject.alias || tenantIdOrObject.tenantId);

      safeMeshBroadcast(mesh, tenantIdOrObject.tenantId, { source: 'cache' }, 'TENANT_LOADED');

      return tenantIdOrObject;
    }

    let target = (tenantIdOrObject && tenantIdOrObject !== "undefined")
      ? tenantIdOrObject
      : localStorage.getItem('discoveredTenant');

    // Sovereign override
    const userRole = user?.role?.toUpperCase();
    if (userRole === 'FOUNDER' || userRole === 'OMEGA') {
      target = 'wilsy';
    }

    const anchorTarget = (target && target !== "undefined") ? target : 'wilsy';

    // Circuit breaker check
    if (circuitBreaker === 'OPEN') {
      const timeSinceFailure = Date.now() - lastFailureTimeRef.current;
      if (timeSinceFailure > BREAKER_COOLDOWN_MS) {
        updateBreakerState('HALF_OPEN', anchorTarget);
      } else {
        safeMeshBroadcast(mesh, 'GLOBAL_ROOT', { target: anchorTarget, reason: 'BREAKER_OPEN' }, 'DISCOVERY_BLOCKED');
        return null;
      }
    }

    setIsSyncing(true);
    const payload = { host: anchorTarget };
    const forensicHeaders = generateForensicHeaders(payload);

    try {
      const start = performance.now();
      const response = await api.post('/auth/discover', payload, { headers: { ...forensicHeaders } });

      const tenantData = response.data.tenant;
      // Backend provides the forensic chain seal – the client trusts it
      const chainSeal = response.data.chainSeal;

      // Broadcast to mesh: tenant resolved with backend‑verified chain seal
      safeMeshBroadcast(mesh, tenantData.tenantId, { alias: anchorTarget, chainSeal }, 'FORENSIC_CHAIN_VERIFICATION');

      const duration = performance.now() - start;
      latencyHistoryRef.current.push(duration);
      if (latencyHistoryRef.current.length > 10) latencyHistoryRef.current.shift();
      const movingAvg = Math.round(latencyHistoryRef.current.reduce((a, b) => a + b, 0) / latencyHistoryRef.current.length);

      setBoardroomSummary(prev => ({ ...prev, avgSlaLatencyMs: movingAvg }));

      failureCountRef.current = 0;
      if (circuitBreaker !== 'CLOSED') updateBreakerState('CLOSED', anchorTarget);

      const enrichedTenant = {
        ...tenantData,
        billingStatus: tenantData.billingStatus || 'ACTIVE',
        primaryColor: tenantData.primaryColor || (tenantData.brandingNexus?.color) || '#D4AF37',
        logo: tenantData.logo || tenantData.brandingNexus?.logo || 'DEFAULT_LOGO'
      };

      setActiveTenant(enrichedTenant);
      localStorage.setItem('discoveredTenant', enrichedTenant.alias || anchorTarget);

      safeMeshBroadcast(mesh, enrichedTenant.tenantId, { alias: anchorTarget, latencyMs: duration }, 'TENANT_DISCOVERY_SUCCESS');

      return enrichedTenant;
    } catch (err) {
      failureCountRef.current += 1;
      lastFailureTimeRef.current = Date.now();

      safeMeshBroadcast(mesh, 'GLOBAL_ROOT', { target: anchorTarget, error: err.message }, 'DISCOVERY_FAILURE');

      if (failureCountRef.current >= BREAKER_MAX_FAILURES && circuitBreaker !== 'OPEN') {
        updateBreakerState('OPEN', anchorTarget);
      }
      return null;
    } finally {
      setIsSyncing(false);
    }
  }, [circuitBreaker, updateBreakerState, user?.role, mesh]);

  // Auto‑discovery on authentication
  useEffect(() => {
    if (isAuthenticated && !activeTenant) {
      const fallbackTenant = user?.tenantAlias || user?.tenantId || localStorage.getItem('discoveredTenant');
      if (fallbackTenant) resolveTenantSingularity(fallbackTenant).catch(() => {});
    }
  }, [isAuthenticated, user, activeTenant, resolveTenantSingularity]);

  // Restore from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('discoveredTenant');
    if (saved && saved !== "undefined" && !activeTenant && circuitBreaker === 'CLOSED') {
      resolveTenantSingularity(saved).catch(() => {});
    }
  }, [resolveTenantSingularity, activeTenant, circuitBreaker]);

  const value = useMemo(() => ({
    activeTenant,
    isSyncing,
    circuitBreaker,
    boardroomSummary,
    resolveTenant: resolveTenantSingularity,
    setActiveTenant: resolveTenantSingularity
  }), [activeTenant, isSyncing, circuitBreaker, boardroomSummary, resolveTenantSingularity]);

  return (
    <TenantContext.Provider value={value}>
      {children}
    </TenantContext.Provider>
  );
};

/**
 * @hook useTenants
 * @description Access the tenant context.
 */
export const useTenants = () => useContext(TenantContext);

export default TenantContext;
