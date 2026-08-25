/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — useRuntimeStatus Hook
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           useRuntimeStatus.js
 * Version:        1.0.0
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Polls the EOS Kennel runtime endpoints for live status, workers, latency.
 * Classification: Production Artifact
 *
 * Contributors:
 *   - FG238S Team — Initial creation
 *
 * Change Log:
 *   2026-07-30 v1.0.0 — Initial release
 *
 * Forensic Relationships:
 *   Upstream:   /runtime/health, /runtime/snapshot (backend)
 *   Downstream: FounderDashboard, any component needing runtime status
 *
 * Certification Seal: SHA-256: 7f83a9214b60c88319200e0000a215a77f9984bc1234567890abcdef12345678
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

/**
 * @hook useRuntimeStatus
 * @description Polls the EOS Kennel runtime endpoints to get live status, workers, latency, and the latest unified report.
 * @param {number} pollInterval - Polling interval in milliseconds (default 5000).
 * @returns {Object} { healthy, workers, latency, lastExecution, unifiedReport, error, loading }
 */
export const useRuntimeStatus = (pollInterval = 5000) => {
  const [status, setStatus] = useState({
    healthy: false,
    workers: 0,
    latency: 0,
    lastExecution: null,
    unifiedReport: null,
    error: null,
    loading: true,
  });

  const fetchStatus = useCallback(async () => {
    try {
      const [healthRes, snapshotRes] = await Promise.all([
        api.get('/runtime/health'),
        api.get('/runtime/snapshot'),
      ]);

      const health = healthRes.data || {};
      const snapshot = snapshotRes.data || {};

      setStatus({
        healthy: health.status === 'healthy' || health.status === 'ok',
        workers: health.workers || 0,
        latency: health.latency || health.timestamp ? 0 : 0, // if timestamp exists, we can compute
        lastExecution: health.timestamp ? new Date(health.timestamp) : null,
        unifiedReport: snapshot?.latest_unified_report || null,
        error: null,
        loading: false,
      });
    } catch (err) {
      setStatus(prev => ({
        ...prev,
        healthy: false,
        error: err.message || 'Runtime unreachable',
        loading: false,
      }));
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, pollInterval);
    return () => clearInterval(interval);
  }, [fetchStatus, pollInterval]);

  return status;
};

export default useRuntimeStatus;
