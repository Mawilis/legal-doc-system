/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — useKennelHealth Hook
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/src/hooks/useKennelHealth.js
 * Version:        v1.0.0-INSTITUTIONAL-SEAL
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Production‑grade custom hook that monitors the health of the
 *                 EOS Kernel API via the certified Node BFF bridge. Polls the
 *                 `/api/kernel` and `/api/kernel/status` endpoints at a
 *                 configurable interval, providing real‑time status, version,
 *                 and component readiness to the Founder Dashboard and other
 *                 sovereign surfaces.
 * Classification: Production Artifact
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) — Mandated zero‑loss real‑time
 *     observability and absolute system unification.
 *   - AI Engineering — RECTIFIED: Produced this hook under Sovereign Mandate v3.1.0
 *     as a foundational component for the Kennel‑integrated Living Cockpit.
 *
 * Change Log:
 *   2026-07-31 v1.0.0-INSTITUTIONAL-SEAL — Initial certified release.
 *
 * Forensic Relationships:
 *   Upstream:   react, ../services/api
 *   Downstream: client/src/components/sovereign/FounderDashboard.jsx,
 *               client/src/components/sovereign/CockpitStatusBar.jsx (to be created)
 *   Shared Crypto / Events / Config: api service (forensic headers), x-request-seal,
 *               X-Wilsy-Bridge: kernel-v1.1.1, PORT 4000, PORT 9095.
 *
 * Certification Seal: PRODUCTION_READY_v1.0.0-INSTITUTIONAL-SEAL
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import api from '../services/api';

/**
 * @constant DEFAULT_POLL_INTERVAL_MS
 * @description Default polling interval in milliseconds (30 seconds) for the health check.
 * Institutional Commentary: The interval is set to 30 seconds to balance real‑time
 * observability with network overhead. The hook is designed to be configurable via
 * the `pollInterval` option if more granularity is required.
 */
const DEFAULT_POLL_INTERVAL_MS = 30000;

/**
 * @function useKennelHealth
 * @description Custom hook that monitors the health of the EOS Kernel via the certified bridge.
 * @param {Object} [options] - Configuration options.
 * @param {number} [options.pollInterval] - Polling interval in milliseconds (default: 30000).
 * @param {boolean} [options.immediate=true] - Whether to perform the initial check immediately.
 * @returns {Object} kennelHealth object containing:
 *   - status: 'online' | 'degraded' | 'offline' | 'UNKNOWN'
 *   - version: string or null
 *   - components: object containing bootstrap, autonomous_kernel, swarm_governance, runner
 *   - lastChecked: ISO timestamp of the last successful check
 *   - error: error object if the last check failed
 */
export const useKennelHealth = (options = {}) => {
  const {
    pollInterval = DEFAULT_POLL_INTERVAL_MS,
    immediate = true,
  } = options;

  const [kennelHealth, setKennelHealth] = useState({
    status: 'UNKNOWN',
    version: null,
    components: {},
    lastChecked: null,
    error: null,
  });

  const isMounted = useRef(true);
  const intervalRef = useRef(null);

  /**
   * @function checkKennelHealth
   * @description Performs the health check by calling `/api/kernel` and `/api/kernel/status`.
   * Institutional Commentary: This function is the single source of truth for Kennel health.
   * It first pings the root endpoint to verify the bridge is operational, then fetches
   * component status. If any call fails, the status is set to 'offline' or 'degraded'.
   * The function never throws; all errors are captured in the state.
   */
  const checkKennelHealth = useCallback(async () => {
    if (!isMounted.current) return;

    try {
      // 1. Check the main kernel endpoint
      const rootResp = await api.get('/kernel');
      if (rootResp.status !== 200 || rootResp.data?.status !== 'OPERATIONAL') {
        setKennelHealth(prev => ({
          ...prev,
          status: 'degraded',
          lastChecked: new Date().toISOString(),
          error: new Error('Kernel responded with non‑OPERATIONAL status'),
        }));
        return;
      }

      // 2. Fetch detailed component status
      let components = {};
      let version = rootResp.data?.version || null;
      try {
        const statusResp = await api.get('/kernel/status');
        if (statusResp.status === 200 && statusResp.data?.components) {
          components = statusResp.data.components;
        }
      } catch (componentError) {
        // Non‑critical – we still have the root status
        console.warn('[useKennelHealth] Failed to fetch component status:', componentError.message);
      }

      setKennelHealth({
        status: 'online',
        version,
        components,
        lastChecked: new Date().toISOString(),
        error: null,
      });
    } catch (error) {
      // Determine if the bridge is offline or degraded
      const status = error.response?.status === 502 ? 'offline' : 'degraded';
      setKennelHealth(prev => ({
        ...prev,
        status,
        lastChecked: new Date().toISOString(),
        error: error.message || 'Unknown error',
      }));
    }
  }, []);

  /**
   * @effect Polling lifecycle
   * @description Sets up the interval to poll the health endpoint. Cleans up on unmount.
   */
  useEffect(() => {
    isMounted.current = true;

    if (immediate) {
      checkKennelHealth();
    }

    intervalRef.current = setInterval(checkKennelHealth, pollInterval);

    return () => {
      isMounted.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [checkKennelHealth, pollInterval, immediate]);

  return kennelHealth;
};

export default useKennelHealth;
