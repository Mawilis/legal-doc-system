/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN DASHBOARD CONTROLLER [V16.5.5-RESILIENT]                                                                          ║
 * ║ [SCHEMA-VALIDATED RESOLVER | SHARD-LEVEL RESILIENCE | MOUNT TELEMETRY | FORENSIC TRACE LINKAGE]                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.5.5-RESILIENT | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/SovereignDashboardController.jsx               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated shard-level fault isolation and forensic mount auditing.                             ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Injected ErrorBoundary wrappers around dashboard shards for institutional resilience.            ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { Suspense, useEffect, useMemo } from 'react';
import { Navigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { broadcastTelemetry } from '../../utils/telemetryHelper.js';
import ErrorBoundary from '../ErrorBoundary';

/**
 * 🏛️ COMMAND CENTER SHARDS
 * High-fidelity dashboards are lazily loaded to ensure code splitting aligns with institutional security.
 */
const FounderDashboard = React.lazy(() => import('./FounderDashboard'));
const GeneralDashboard = React.lazy(() => import('./GeneralDashboard'));

/**
 * @function SovereignDashboardController
 * @desc Evaluates the user's forensic role and mounts the corresponding Command Center shard.
 */
const SovereignDashboardController = ({ user: propUser }) => {

  /**
   * @function isValidUser
   * @desc Validates the identity shard schema before granting access to dashboard logic.
   */
  const isValidUser = (obj) => {
    return obj && typeof obj.role === 'string' && obj.role.length > 0 && obj.email;
  };

  /**
   * @function getSovereignIdentity
   * @desc Self-hydration fallback with investor-grade schema validation.
   */
  const user = useMemo(() => {
    if (isValidUser(propUser)) return propUser;

    // 🧬 Diagnostic Alignment: Matching keys verified in the Sovereign Identity Vault
    const vaultData = localStorage.getItem('wilsy_user') || localStorage.getItem('user');
    if (vaultData) {
      try {
        const parsed = JSON.parse(vaultData);
        if (isValidUser(parsed)) return parsed;
        console.error('[SOVEREIGN-CONTROLLER] 🚨 Vault schema validation failed.');
      } catch (e) {
        console.error('[SOVEREIGN-CONTROLLER] 🚨 Vault data corruption detected.');
      }
    }
    return null;
  }, [propUser]);

  const role = user?.role?.toUpperCase();
  const traceId = localStorage.getItem('traceId') || 'SYSTEM_CORE_INIT';

  /**
   * 🛰️ MOUNT TELEMETRY
   * Broadcasts successful entry into the Command Center for the forensic audit trail.
   */
  useEffect(() => {
    if (user && role) {
      broadcastTelemetry(user.tenantAlias || 'GLOBAL_ROOT', 'DASHBOARD_EVENT', 'DASHBOARD_MOUNT_SUCCESS', user.email, {
        role,
        traceId,
        version: '16.5.5'
      });
      console.log(`[SOVEREIGN-CONTROLLER] ✅ Shard Mounted: ${role} | Trace: ${traceId}`);
    }
  }, [user, role, traceId]);

  /**
   * @function resolveShard
   * @desc Executes the conditional logic to return the appropriate dashboard component.
   * 🛡️ RECTIFIED: Wrapped in ErrorBoundary for shard-level resilience.
   */
  const resolveShard = () => {
    const forensicContext = { role, traceId, timestamp: new Date().toISOString() };

    // 🛡️ FOUNDER & SUPER_ADMIN ACCESS: Unlocks the full forensic suite.
    if (role === 'FOUNDER' || role === 'SUPER_ADMIN') {
      return (
        <ErrorBoundary>
          <FounderDashboard user={user} />
        </ErrorBoundary>
      );
    }

    // 🛰️ GENERAL TENANT ACCESS: Normal operational node.
    if (role === 'TENANT_ADMIN' || role === 'USER') {
      return (
        <ErrorBoundary>
          <GeneralDashboard user={user} />
        </ErrorBoundary>
      );
    }

    // 🚨 UNAUTHORIZED ACCESS: Revert to gateway if no identity shard is anchored.
    if (!user) {
      console.warn('[SOVEREIGN-CONTROLLER] ⚠️ No identity shard discovered. Reverting to Gateway.', { traceId });
      return <Navigate to="/login" replace />;
    }

    console.error('[SOVEREIGN-CONTROLLER] 🚨 CRITICAL: Identity fragment unrecognized.', forensicContext);
    return <Navigate to="/unauthorized" replace />;
  };

  return (
    <Suspense
      fallback={
        <div className="h-screen bg-black flex flex-col items-center justify-center">
          <Loader2 className="w-12 h-12 text-[#D4AF37] animate-spin mb-6" />
          <p className="text-[#D4AF37] font-mono text-xs tracking-[0.3em] uppercase animate-pulse">
            Hydrating Sovereign Command Center...
          </p>
        </div>
      }
    >
      {resolveShard()}
    </Suspense>
  );
};

export default SovereignDashboardController;
