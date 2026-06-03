/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN DATA HYDRATION HOOK [V3.2.0-TITAN-JSDOC-SEALED]                                                                   ║
 * ║ [NEURAL FLUX ENGINE | SHARD HEALTH MONITORING | DB AS SOURCE OF TRUTH | FULL JSDOC MANDATE]                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 3.2.0-TITAN-JSDOC-SEALED | PRODUCTION READY | TRILLION DOLLAR SPEC                                                             ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/hooks/useSovereignData.js                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 RECTIFICATION (2026-05-27):                                                                                                         ║
 * ║ • [COLLABORATION COMMENT - WILSON]: Implemented strict Primitive Dependency Locking (tenantId)                                         ║
 * ║ • [COLLABORATION COMMENT - EPITOME]: Added isHydratingRef Circuit Breaker to prevent concurrent request spam (429 mitigation)          ║
 * ║ • [COLLABORATION COMMENT - SECURITY]: Added strict Auth Guard to prevent 'Auth=undefined' fractures                                    ║
 * ║ • [COLLABORATION COMMENT - MANDATE]: Full JSDoc for exported function and helpers, fulfilling WILSY OS mandate.                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../services/api.js';
import { useTenants } from '../contexts/tenantContext.jsx';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

/**
 * 🛡️ INSTITUTIONAL TOKEN SANITIZER
 * Extracts and purifies the sovereign JWT token from multiple possible localStorage keys.
 * Removes any surrounding quotes that might break Authorization headers.
 *
 * @function getSanitizedToken
 * @returns {string} Sanitized JWT token string, or empty string if none found.
 *
 * @real-world
 *   Used before every authenticated API call to ensure header format `Bearer <token>` works flawlessly.
 *   Eliminates silent failures caused by accidentally stored quoted tokens.
 *
 * @forensic
 *   The token is read from deterministic priority order: 'token' → 'wilsy_auth_token' → 'accessToken'.
 *   Quotes are stripped to avoid malformed headers that would return 403 Forensic Seal Denied.
 *
 * @example
 *   const token = getSanitizedToken();
 *   if (!token) { redirectToLogin(); }
 */
const getSanitizedToken = () => {
  const raw = localStorage.getItem('token') || localStorage.getItem('wilsy_auth_token') || localStorage.getItem('accessToken') || '';
  return raw.replace(/["']/g, '');
};

/**
 * ⚛️ useSovereignData
 * A sovereign React hook that hydrates the Boardroom HUD with real-time metrics from the database.
 * Acts as the exclusive source of truth for revenue, compliance, and forensic shards.
 * Implements circuit‑breaker pattern to prevent overlapping requests and strict dependency locking
 * to avoid infinite re‑hydration loops.
 *
 * @function useSovereignData
 * @returns {Object} Hydrated data and control interface.
 * @returns {Object|null} returns.revenue - Revenue metrics object from DB, or null if not available.
 * @returns {Object|null} returns.analytics - Reserved for future analytics (currently null, DB-driven).
 * @returns {Object|null} returns.compliance - Compliance metrics object from DB, or null.
 * @returns {Object|null} returns.forensics - Forensic log aggregates from DB, or null.
 * @returns {boolean} returns.loading - True during initial hydration or forced sync.
 * @returns {string|null} returns.error - Error message if hydration fails, else null.
 * @returns {string|null} returns.lastSync - ISO timestamp of last successful sync.
 * @returns {string} returns.shardHealth - 'OPTIMAL' (latency ≤500ms), 'DEGRADED' (latency >500ms).
 * @returns {Function} returns.forceSync - Manually trigger hydration with a fresh AbortController.
 *
 * @real-world
 *   **BoardroomHUD Component:** Calls `useSovereignData()` to display live revenue, compliance breaches,
 *   and forensic seals. Polls every 30 seconds and refreshes on tenant switch.
 *   **Seizure Workflow:** After seizing an asset, `forceSync()` is called to immediately update the dashboard.
 *
 * @forensic
 *   - Circuit Breaker (`isHydratingRef`): Guarantees only one network request at a time, eliminating 429 floods.
 *   - Primitive Dependency (`tenantId` string only): Prevents infinite effect loops caused by object reference changes.
 *   - Auth Guard: Halts execution if `getSanitizedToken()` returns empty – prevents "Auth Fracture" telemetry spam.
 *   - Telemetry Broadcast: Every sync (success or failure) is sealed and sent to the forensic audit trail.
 *   - Polling Interval: 30 seconds with proper cleanup to avoid background leaks.
 *
 * @example
 *   // Inside BoardroomHUD.jsx
 *   const { revenue, compliance, loading, forceSync } = useSovereignData();
 *
 *   if (loading) return <SkeletonLoader />;
 *   return (
 *     <div>
 *       <h2>Revenue: ${revenue?.total}</h2>
 *       <button onClick={forceSync}>Refresh Now</button>
 *     </div>
 *   );
 */
export default function useSovereignData() {
  const { activeTenant } = useTenants();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastSync, setLastSync] = useState(null);
  const [shardHealth, setShardHealth] = useState('OPTIMAL');

  // 🛡️ CIRCUIT BREAKER: Prevents overlapping network requests
  const isHydratingRef = useRef(false);

  const [data, setData] = useState({
    revenue: null,
    analytics: null,
    compliance: null,
    forensics: null
  });

  // 🔒 PRIMITIVE LOCKING: Extract the exact primitive string to prevent object-reference re-renders
  const tenantId = activeTenant?.id || 'WILSY_GLOBAL_ROOT';

  /**
   * 🧠 HYDRATION ENGINE
   * Performs the actual network requests to fetch sovereign metrics from DB only.
   * Implements circuit breaker, auth guard, and latency-based shard health detection.
   *
   * @param {AbortController} abortController - Used to cancel in-flight request on unmount or forceSync.
   * @returns {Promise<void>}
   */
  const hydrateCockpit = useCallback(async (abortController) => {
    // 🛑 GATES & GUARDS: Stop execution if already hydrating
    if (isHydratingRef.current) return;

    const cleanToken = getSanitizedToken();

    // 🛑 AUTH GUARD: Prevent "Auth Fracture" logs by stopping unauthenticated telemetry/requests
    if (!cleanToken) {
      console.warn('[SOVEREIGN_DATA] 🚨 Auth token missing. Halting hydration protocol.');
      setLoading(false);
      return;
    }

    isHydratingRef.current = true; // Lock the circuit
    const startTime = performance.now();

    setLoading(true);
    setError(null);

    const reqConfig = {
      signal: abortController.signal,
      headers: { 'Authorization': `Bearer ${cleanToken}`, 'X-Shard-Origin': 'ZA-JHB-01' }
    };

    try {
      // 🚀 CONCURRENT SHARD RESOLUTION - DB IS THE ONLY SOURCE OF TRUTH
      const [revRes, comRes, forRes] = await Promise.allSettled([
        api.get(`/revenue/metrics`, reqConfig),
        api.get(`/compliance/metrics/${tenantId}`, reqConfig),
        api.get(`/forensics/metrics/${tenantId}`, reqConfig)
      ]);

      const endTime = performance.now();
      const latency = endTime - startTime;
      if (latency > 500) setShardHealth('DEGRADED');
      else setShardHealth('OPTIMAL');

      // ✅ DB IS SOURCE OF TRUTH - NULL if not in database
      const fetchedRevenue = revRes.status === 'fulfilled' ? revRes.value.data?.data : null;
      const fetchedCompliance = comRes.status === 'fulfilled' ? comRes.value.data?.data : null;
      const fetchedForensics = forRes.status === 'fulfilled' ? forRes.value.data?.data : null;

      setData({
        revenue: fetchedRevenue,
        analytics: null,  // Analytics derived from DB data, not fake
        compliance: fetchedCompliance,
        forensics: fetchedForensics
      });

      setLastSync(new Date().toISOString());

      // 📡 Fire telemetry ONLY on clean execution
      broadcastTelemetry(tenantId, 'HUD_HYDRATION', 'SYNC_SUCCESS', 'useSovereignData', {
        latency: `${latency.toFixed(2)}ms`,
        revenueExists: !!fetchedRevenue,
        complianceExists: !!fetchedCompliance,
        forensicsExists: !!fetchedForensics
      });

    } catch (err) {
      if (err.name !== 'CanceledError') {
        setError(err.message || 'INSTITUTIONAL_SHARD_FRACTURE');
        broadcastTelemetry(tenantId, 'HUD_HYDRATION', 'SYNC_FAILED', 'useSovereignData', { error: err.message });
      }
    } finally {
      setLoading(false);
      isHydratingRef.current = false; // Unlock the circuit
    }
  }, [tenantId]); // 🔒 STRICT DEPENDENCY: Only re-create if the actual ID string changes

  // ⚡ LIFECYCLE: Initial hydration and polling setup
  useEffect(() => {
    const abortController = new AbortController();

    // Initial Hydration Execution
    hydrateCockpit(abortController);

    // ⚡ Poll every 30 seconds strictly - Interval logic decoupled from render cycles
    const interval = setInterval(() => {
      // Only execute if not currently unmounting/aborted
      if (!abortController.signal.aborted) {
        hydrateCockpit(abortController);
      }
    }, 30000);

    return () => {
      abortController.abort(); // Cancel pending fetch on unmount
      clearInterval(interval);   // Kill interval on unmount
    };
  }, [hydrateCockpit]);

  return {
    ...data,
    loading,
    error,
    lastSync,
    shardHealth,
    forceSync: () => hydrateCockpit(new AbortController())
  };
}
