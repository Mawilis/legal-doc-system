/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - USE DASHBOARD HOOK [V1.0.0-PRODUCTION-GRADE]                                                                               ║
 * ║ [EPITOME: REACTIVE CONTRACT SUBSCRIPTION | AUTOMATIC POLLING & EVENT BUS SYNC]                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | BIBLICAL WORTH COMPLIANT                                       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/hooks/useDashboard.js                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Enforced real-time contract synchronization across operating console panels.                        ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: React hook delivering isolated panel state slices with zero local computation.               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchDashboardContract } from '../services/dashboardService';

/**
 * @function useDashboard
 * @description React hook that manages continuous synchronization with the authoritative kernel dashboard contract.
 * @param {number} [pollIntervalMs=3000] - Polling interval for live state sync.
 * @returns {Object} `{ dashboard, loading, error, refresh }`
 * @collaboration Provides reactive state updates to all modular console components.
 */
export function useDashboard(pollIntervalMs = 3000) {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const data = await fetchDashboardContract();
      setDashboard(data);
      setError(null);
    } catch (err) {
      console.warn('[WILSY-USE-DASHBOARD] Sync warning:', err.message);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, pollIntervalMs);
    return () => clearInterval(interval);
  }, [refresh, pollIntervalMs]);

  return { dashboard, loading, error, refresh };
}
