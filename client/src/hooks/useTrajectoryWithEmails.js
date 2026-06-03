/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ANALYTICS HOOK [V1.0.2-OMEGA-TRAJECTORY]                                                                                    ║
 * ║ [REAL-TIME TRAJECTORY HYDRATION | DUAL-SERIES DATA CONDUIT | INSTITUTIONAL ANALYTICS | BIBLICAL WORTH]                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.2-OMEGA | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                      ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | SOVEREIGN DATA STREAM | BOARDROOM READY                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/hooks/useTrajectoryWithEmails.js                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated high-fidelity trajectory syncing for boardroom dispatch analytics. [2026-05-04]       ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Integrated AbortController to sever unanchored promises and prevent race conditions.            ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Implemented institutional cleanup to mitigate resource-drain fractures. [2026-05-15]             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { useEffect, useState } from 'react';
import api from '../services/api.js';

/**
 * @hook useTrajectoryWithEmails
 * @description Decoupled data engine for aggregating report generation vs. email dispatch metrics with Sovereign Abort Shielding.
 * @param {string} tenantId - The Sovereign shard identifier.
 */
export const useTrajectoryWithEmails = (tenantId) => {
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 🛡️ INSTITUTIONAL GUARD: Prevent execution if tenant identity is missing or literal
    if (!tenantId || tenantId === 'TENANT-ID' || tenantId === 'GLOBAL_ROOT') {
      setLoading(false);
      return;
    }

    // ⚔️ SOVEREIGN ABORT SHIELD: Kill unanchored network pulses on cleanup or tenant rotation
    const controller = new AbortController();
    const { signal } = controller;

    const fetchStats = async () => {
      setLoading(true);
      console.log(`📡 [HOOK] Hydrating trajectory for Shard: ${tenantId}`);

      try {
        const res = await api.get(`/telemetry/${tenantId}/trajectoryWithEmails`, { signal });

        if (res.status >= 400) {
          throw new Error(`PROTOCOL_FRACTURE: ${res.status}`);
        }

        const result = res.data;

        // 🏛️ RECTIFIED: Multi-pattern alignment for API envelopes (success/data vs. direct array)
        const aggregatedData = result.success ? result.data : (Array.isArray(result) ? result : []);

        setStats(aggregatedData);
      } catch (err) {
        // 🛡️ Silent cleanup for intentional aborts to prevent console noise
        const isCanceled = err.name === 'AbortError'
          || err.name === 'CanceledError'
          || err.code === 'ERR_CANCELED'
          || err.message === 'canceled';

        if (isCanceled) {
          return;
        } else {
          console.warn('⚠️ [HOOK_FRACTURE] Failed to fetch trajectory with emails:', err.message);
          // Fallback to empty series to ensure charts don't fracture
          setStats([]);
        }
      } finally {
        // Only update loading state if the request wasn't aborted to avoid state updates on unmounted components
        if (!signal.aborted) {
          setLoading(false);
        }
      }
    };

    fetchStats();

    // 🧹 INSTITUTIONAL CLEANUP: Finality for the data conduit
    return () => {
      controller.abort();
    };
  }, [tenantId]);

  return { stats, loading };
};

export default useTrajectoryWithEmails;
