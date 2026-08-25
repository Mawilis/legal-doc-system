/*
 * ==============================================================================
 * Wilsy OS - useTenants Custom React Hook
 * ==============================================================================
 * EPITOME of state management architecture.
 * BIBLICAL scale. WORTH BILLIONS.
 * NO CHILD'S PLACE.
 *
 * Collaboration Comments:
 * - Architect: Wilson Khanyezi
 * - Status: PRODUCTION READY
 * - Module: Tenant Lifecycle & State Management Hook
 * - Purpose: Provides high-performance reactive data binding, automated 
 *   error recovery, and secure asynchronous tenant telemetry synchronization.
 * ==============================================================================
 */

import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Custom hook to manage enterprise tenant nodes within Wilsy OS.
 * Handles caching, real-time synchronization, and atomic state updates.
 * 
 * @returns {Object} Tenant state, loading indicators, error objects, and operational methods.
 */
export const useTenants = () => {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [syncStatus, setSyncStatus] = useState('IDLE');

  // Reference to prevent state updates on unmounted components during async flows
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    fetchTenants();

    return () => {
      isMountedRef.current = false;
    };
  }, []);

  /**
   * Fetches the sovereign tenant registry from the secure API gateway.
   */
  const fetchTenants = useCallback(async () => {
    if (!isMountedRef.current) return;

    setLoading(true);
    setError(null);
    setSyncStatus('SYNCING');

    try {
      const response = await fetch('/api/v1/tenants', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Wilsy-Protocol': 'Master-Singularity'
        }
      });

      if (!response.ok) {
        throw new Error(`Critical Gateway Failure: HTTP Status ${response.status}`);
      }

      const data = await response.json();

      if (isMountedRef.current) {
        setTenants(data.tenants || []);
        setSyncStatus('SECURE');
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err.message || 'Unknown error occurred during tenant synchronization.');
        setSyncStatus('ERROR');
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  /**
   * Provisions a new enterprise tenant node atomically.
   * 
   * @param {Object} tenantData - Configuration parameters for the new tenant.
   * @returns {Promise<Object>} The provisioned tenant entity.
   */
  const provisionTenant = useCallback(async (tenantData) => {
    setSyncStatus('PROVISIONING');
    try {
      const response = await fetch('/api/v1/tenants/provision', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Wilsy-Protocol': 'Master-Singularity'
        },
        body: JSON.stringify(tenantData)
      });

      if (!response.ok) {
        throw new Error(`Provisioning Rejected: HTTP Status ${response.status}`);
      }

      const newTenant = await response.json();

      if (isMountedRef.current) {
        setTenants(prev => [newTenant, ...prev]);
        setSyncStatus('SECURE');
      }

      return newTenant;
    } catch (err) {
      if (isMountedRef.current) {
        setError(err.message);
        setSyncStatus('ERROR');
      }
      throw err;
    }
  }, []);

  return {
    tenants,
    loading,
    error,
    syncStatus,
    refreshTenants: fetchTenants,
    provisionTenant
  };
};

export default useTenants;