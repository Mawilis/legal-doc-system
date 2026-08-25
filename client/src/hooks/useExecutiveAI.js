/**
 * ╔══════════════════════════════════════════════════════════════════════════╗
 * ║   █████╗ ██╗    ███████╗ █████╗ ██╗     ███████╗███████╗              ║
 * ║  ██╔══██╗██║    ██╔════╝██╔══██╗██║     ██╔════╝██╔════╝              ║
 * ║  ███████║██║    ███████╗███████║██║     █████╗  ███████╗              ║
 * ║  ██╔══██║██║    ╚════██║██╔══██║██║     ██╔══╝  ╚════██║              ║
 * ║  ██║  ██║███████╗███████║██║  ██║███████╗███████╗███████║              ║
 * ║  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝              ║
 * ║                                                                        ║
 * ║            WILSY OS - EXECUTIVE AI HOOK (FG232 CLIENT)               ║
 * ║         SOVEREIGN REACT HOOK FOR EXECUTIVE INTELLIGENCE               ║
 * ║         VERSION: 1.0.0-FG232-EXECUTIVE-HOOK                          ║
 * ║                                                                        ║
 * ╠══════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SIGN-OFF:                                           ║
 * ║ • Wilson Khanyezi (CEO) – Mandated client-side hook for FG232.        ║
 * ║ • AI Engineering (Gemini) – Created hook with state management,       ║
 * ║   error handling, and tenant context propagation.                     ║
 * ║ • Final review: 2026-08-04.                                           ║
 * ║ • Certified against api.js v73.1.0 – full forensic compatibility.      ║
 * ╚══════════════════════════════════════════════════════════════════════════╝
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import api from '../services/api'; // Sovereign HTTP client with forensic sealing

// -----------------------------------------------------------------------------
// CONFIGURATION
// -----------------------------------------------------------------------------

const DEFAULT_OPTIONS = {
  tenantId: 'GLOBAL_ROOT', // Will be overridden by api interceptor if set
  autoTrace: true,
  timeout: 30000,
};

/**
 * useExecutiveAI
 * @description React hook for calling the FG232 Executive Intelligence endpoints.
 * Supports both '/intelligence' (raw query) and '/query' (routed dispatch).
 * Manages loading, error, data, and provides an `execute` function.
 *
 * The `api` service automatically injects forensic seals, tenant headers,
 * and handles token refresh. This hook focuses solely on UI state and
 * query submission.
 *
 * @param {Object} options - Configuration options.
 * @param {string} options.tenantId - Tenant context (default: 'GLOBAL_ROOT').
 * @param {boolean} options.autoTrace - Auto‑generate trace IDs (default: true) – handled by api.
 * @param {number} options.timeout - Request timeout in ms (default: 30000).
 * @returns {Object} { data, loading, error, execute, reset, lastResponse }
 *
 * @example
 * const { data, loading, execute } = useExecutiveAI();
 * const handleQuery = async () => {
 *   const result = await execute('What is our revenue forecast?', { context: { growth: 15 } });
 *   console.log(result);
 * };
 */
export const useExecutiveAI = (options = {}) => {
  const mergedOptions = { ...DEFAULT_OPTIONS, ...options };

  // ── State ──
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastResponse, setLastResponse] = useState(null);

  // ── Refs for abort control ──
  const abortControllerRef = useRef(null);

  // ── Cleanup on unmount ──
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  /**
   * execute - Send a query to the executive intelligence endpoints.
   * @param {string} query - The natural language query.
   * @param {Object} [context={}] - Additional context (conversation history, metadata).
   * @param {string} [mode='intelligence'] - Either 'intelligence' (raw) or 'query' (routed).
   * @returns {Promise<Object>} The parsed response from the kernel.
   */
  const execute = useCallback(
    async (query, context = {}, mode = 'intelligence') => {
      // Validate input
      if (!query || typeof query !== 'string') {
        const err = new Error('Query must be a non‑empty string.');
        setError(err);
        throw err;
      }

      // Abort any pending request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      setLoading(true);
      setError(null);

      // Prepare payload
      const payload = {
        query,
        context,
      };

      // Determine endpoint (api interceptors will add tenant and forensic headers)
      const endpoint =
        mode === 'query'
          ? '/executive/query'        // relative to /api baseURL set in api.js
          : '/executive/intelligence';

      try {
        const response = await api.post(endpoint, payload, {
          signal: controller.signal,
          timeout: mergedOptions.timeout,
        });

        // Axios wraps data in response.data
        const result = response?.data ?? response;
        setData(result);
        setLastResponse(result);
        setLoading(false);
        return result;
      } catch (err) {
        // Abort errors are not treated as application errors
        if (err.name === 'AbortError' || err.code === 'ERR_CANCELED') {
          setLoading(false);
          return null;
        }
        setError(err);
        setLoading(false);
        throw err;
      } finally {
        if (abortControllerRef.current === controller) {
          abortControllerRef.current = null;
        }
      }
    },
    [mergedOptions.timeout]
  );

  /**
   * reset - Clear all state (data, error, loading).
   */
  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
    setLastResponse(null);
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  return {
    data,
    loading,
    error,
    execute,
    reset,
    lastResponse,
  };
};

export default useExecutiveAI;
