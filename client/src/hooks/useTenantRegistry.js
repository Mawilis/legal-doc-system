/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TENANT REGISTRY HOOK [V1.0.0-SINGULARITY]                                                                                   ║
 * ║ [SHARD DISCOVERY | ATOMIC STATE | MULTI-TENANT GOVERNANCE | BILLION DOLLAR SPEC]                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-SINGULARITY | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL FINALITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/hooks/useTenantRegistry.js                                            ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export const useTenantRegistry = () => {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTenants = useCallback(async (signal) => {
    try {
      setLoading(true);
      const response = await api.get('/tenants', { signal });
      setTenants(response.data.tenants || []);
    } catch (err) {
      if (err.name !== 'AbortError' && err.name !== 'CanceledError') {
        setError(err.message || 'SHARD_DISCOVERY_FAILURE');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetchTenants(controller.signal);
    return () => controller.abort();
  }, [fetchTenants]);

  return { tenants, loading, error, refresh: fetchTenants };
};

export default useTenantRegistry;
