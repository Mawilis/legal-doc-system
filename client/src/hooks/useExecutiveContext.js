/**
 * ╔══════════════════════════════════════════════════════════════════════════╗
 * ║   █████╗ ██╗    ███████╗ █████╗ ██╗     ███████╗███████╗              ║
 * ║  ██╔══██╗██║    ██╔════╝██╔══██╗██║     ██╔════╝██╔════╝              ║
 * ║  ███████║██║    ███████╗███████║██║     █████╗  ███████╗              ║
 * ║  ██╔══██║██║    ╚════██║██╔══██║██║     ██╔══╝  ╚════██║              ║
 * ║  ██║  ██║███████╗███████║██║  ██║███████╗███████╗███████║              ║
 * ║  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝              ║
 * ║                                                                        ║
 * ║         WILSY OS - EXECUTIVE CONTEXT HOOK (FG232 CLIENT)              ║
 * ║      SOVEREIGN REACT HOOK FOR CONVERSATION STATE MANAGEMENT           ║
 * ║         VERSION: 1.0.0-FG232-CONTEXT-HOOK                            ║
 * ║                                                                        ║
 * ╠══════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SIGN-OFF:                                           ║
 * ║ • Wilson Khanyezi (CEO) – Mandated client-side context persistence.    ║
 * ║ • AI Engineering (Gemini) – Created hook for GET/POST context.        ║
 * ║ • Final review: 2026-08-04.                                           ║
 * ╚══════════════════════════════════════════════════════════════════════════╝
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import api from '../services/api';

const DEFAULT_OPTIONS = {
  tenantId: 'GLOBAL_ROOT',
  autoLoad: true,
  contextId: null, // Optional: specific context ID to load
};

/**
 * useExecutiveContext
 * @description React hook for managing executive conversation context via the FG232 kernel.
 * Provides functions to:
 *   - loadContext: GET /api/ai/executive/context (retrieve current state)
 *   - updateContext: POST /api/ai/executive/context (update/merge state)
 *   - resetContext: clear local context (optional)
 * Manages loading, error, and data state.
 *
 * @param {Object} options - Configuration options.
 * @param {string} options.tenantId - Tenant context (default: 'GLOBAL_ROOT').
 * @param {boolean} options.autoLoad - Automatically load context on mount (default: true).
 * @param {string|null} options.contextId - Optional context ID to load.
 * @returns {Object} { context, loading, error, loadContext, updateContext, resetContext }
 *
 * @example
 * const { context, loading, updateContext } = useExecutiveContext();
 * const handleUpdate = async () => {
 *   await updateContext({ currentQuery: 'What is our growth rate?' });
 * };
 */
export const useExecutiveContext = (options = {}) => {
  const mergedOptions = { ...DEFAULT_OPTIONS, ...options };

  const [context, setContext] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
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
   * loadContext - Retrieve current context from the kernel.
   * @param {string} [contextId] - Optional specific context ID.
   * @returns {Promise<Object>} The context object.
   */
  const loadContext = useCallback(async (contextId = null) => {
    const id = contextId || mergedOptions.contextId;
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setLoading(true);
    setError(null);

    try {
      const params = id ? { contextId: id } : {};
      const response = await api.get('/ai/executive/context', {
        params,
        signal: controller.signal,
        headers: {
          'X-Tenant-ID': mergedOptions.tenantId,
        },
      });
      const result = response?.data ?? response;
      setContext(result);
      setLoading(false);
      return result;
    } catch (err) {
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
  }, [mergedOptions.tenantId, mergedOptions.contextId]);

  /**
   * updateContext - Update/merge context state in the kernel.
   * @param {Object} newContext - Partial context object to merge.
   * @param {string} [contextId] - Optional specific context ID.
   * @returns {Promise<Object>} The updated context.
   */
  const updateContext = useCallback(async (newContext, contextId = null) => {
    const id = contextId || mergedOptions.contextId;
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setLoading(true);
    setError(null);

    try {
      const payload = { context: newContext };
      if (id) payload.contextId = id;

      const response = await api.post('/ai/executive/context', payload, {
        signal: controller.signal,
        headers: {
          'X-Tenant-ID': mergedOptions.tenantId,
        },
      });
      const result = response?.data ?? response;
      setContext(result);
      setLoading(false);
      return result;
    } catch (err) {
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
  }, [mergedOptions.tenantId, mergedOptions.contextId]);

  /**
   * resetContext - Clear local context state (does not delete server-side).
   */
  const resetContext = useCallback(() => {
    setContext(null);
    setError(null);
    setLoading(false);
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  // ── Auto‑load on mount ──
  useEffect(() => {
    if (mergedOptions.autoLoad) {
      loadContext();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    context,
    loading,
    error,
    loadContext,
    updateContext,
    resetContext,
  };
};

export default useExecutiveContext;
