/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC STATS INTELLIGENCE HOOK [V1.1.0-KENNEL-BINDING]                                                                    ║
 * ║ [LIVE AGGREGATION STREAM | FRACTURE CONTAINMENT | BEHAVIORAL TRENDS | INVESTOR-READY]                                                  ║
 * ║ [RECONNECTED TO KENNEL: /api/v1/dashboard]                                                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-KENNEL-BINDING | PRODUCTION READY | BILLION DOLLAR SPEC                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/hooks/useTelemetryStats.js                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated live aggregated stat tracking for dashboard charting.                                ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Purged naked fetch. Anchored to Unified api.js bridge for SHA3-512 Seal integrity. [2026-05-06]    ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Injected Token Sanitizer to prevent 401 Identity Gate fractures. [2026-05-06]                   ║
 * ║ • Cline (Executor) - RECONNECTED: Changed endpoint to /api/v1/dashboard and mapped response to stat format.                           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import api from '../services/api'; // 🏛️ ANCHORED TO SOVEREIGN BRIDGE

// 🛡️ RECTIFIED: Sovereign Token Sanitizer
const getSanitizedToken = () => {
  const raw = localStorage.getItem('token') || localStorage.getItem('wilsy_auth_token') || localStorage.getItem('accessToken') || '';
  return raw.replace(/["']/g, '');
};

/**
 * @function useTelemetryStats
 * @description Aggregates behavioral trends via the Unified Sovereign Bridge.
 * Now fetches from /api/v1/dashboard and maps high-level metrics to a stat array.
 */
export const useTelemetryStats = (tenantId = 'WILSY_GLOBAL_ROOT', refreshInterval = 30000) => {
  const [stats, setStats] = useState([]);
  const [isSyncing, setIsSyncing] = useState(true);
  const [error, setError] = useState(null);
  const lastErrorLogRef = useRef({ message: null, at: 0 });
  const cooldownUntilRef = useRef(0);

  const resolvedId = (!tenantId || tenantId === 'TENANT-ID' || tenantId === 'TENANT_ID')
    ? 'WILSY_GLOBAL_ROOT'
    : tenantId;

  const fetchStats = useCallback(async () => {
    if (Date.now() < cooldownUntilRef.current) return;
    if (stats.length === 0) setIsSyncing(true);
    setError(null);

    try {
      const cleanToken = getSanitizedToken();

      // 🚀 RE-ANCHORED: Use /api/v1/dashboard to get health and metrics
      const response = await api.get('/api/v1/dashboard', {
        headers: {
          'Authorization': `Bearer ${cleanToken}`
        }
      });

      const result = response.data;
      const data = result.data || result;

      // Transform dashboard data into a stats array suitable for charts
      const statEntry = {
        _id: {
          day: new Date().toISOString().split('T')[0],
          type: 'DASHBOARD_SNAPSHOT'
        },
        count: data.active_tenants || 0,
        health: parseFloat(data.system_health) || 0,
        securityTier: data.security_tier || 'SOVEREIGN',
        auditChain: data.kernel_audit_chain || 'SECURED'
      };

      // Maintain array of stats (we keep last 7 days, but we only have current snapshot)
      // For simplicity, replace with a single entry or maintain history by storing in ref.
      // We'll keep a rolling 7-day history based on previous stats.
      setStats(prev => {
        const newStats = [statEntry, ...prev];
        // Keep only unique days (last 7)
        const uniqueDays = new Map();
        newStats.forEach(s => {
          const day = s._id.day;
          if (!uniqueDays.has(day)) {
            uniqueDays.set(day, s);
          }
        });
        return Array.from(uniqueDays.values()).slice(0, 7);
      });

      setIsSyncing(false);
    } catch (err) {
      const isCanceled = err.name === 'CanceledError'
        || err.name === 'AbortError'
        || err.code === 'ERR_CANCELED'
        || err.message === 'canceled';

      if (isCanceled) {
        setIsSyncing(false);
        return;
      }

      const status = err.response?.status;
      const message = status ? `HTTP_${status}` : (err.message || 'UNKNOWN_TELEMETRY_ERROR');
      const now = Date.now();

      if (status === 429) {
        const retryAfter = Number(err.response?.headers?.['retry-after'] || 0);
        cooldownUntilRef.current = now + Math.max(retryAfter * 1000, 60000);
      }

      if (lastErrorLogRef.current.message !== message || now - lastErrorLogRef.current.at > 30000) {
        console.warn('⚠️ [Telemetry] Stats degraded:', message);
        lastErrorLogRef.current = { message, at: now };
      }

      // Detailed error reporting for Dashboard HUD
      if (status === 403) {
        setError('FORENSIC_SEAL_DENIED');
      } else if (status === 401) {
        setError('IDENTITY_REVOKED');
      } else {
        setError('STATS_FRACTURE_DETECTED');
      }
      setIsSyncing(false);
    }
  }, [stats.length]);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchStats, refreshInterval]);

  return { stats, isSyncing, error, refresh: fetchStats };
};

export default useTelemetryStats;
