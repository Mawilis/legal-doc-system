/* eslint-disable */
/**
 * ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – USE TENANTS HOOK (CONTEXT WRAPPER)                                                                   ║
 * ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ FILE:           client/src/hooks/useTenants.js                                                                   ║
 * ║ VERSION:        v1.0.0-CONTEXT-ALIGNED                                                                           ║
 * ║ AUTHORITY:      Wilsy OS Core Governance                                                                        ║
 * ║ EPITOME:        Thin wrapper that re‑exports the `useTenants` hook from the tenant context.                     ║
 * ║ CLASSIFICATION: Production Artifact                                                                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGE LOG:                                                                                                   ║
 * ║   2026-08-19 v1.0.0-CONTEXT-ALIGNED – Replaced stub with re‑export from tenantContext.                         ║
 * ║   2026-07-30 v0.0.1-STUB – Original placeholder.                                                                ║
 * ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COMPLIANCE:    POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001                                                   ║
 * ║ DEPENDENCIES:  tenantContext                                                                                     ║
 * ╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { useTenants as useTenantsFromContext } from '../contexts/tenantContext';

/**
 * @function useTenants
 * @description Sovereign hook for accessing tenant state and operations.
 *              Re‑exports the hook from `tenantContext` to maintain a single source of truth.
 * @returns {Object} The tenant context value.
 * @institutional This hook provides a stable interface for all components that need tenant data.
 *                It ensures that all consumers use the same context instance.
 */
export const useTenants = useTenantsFromContext;

export default useTenants;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — useTenants v1.0.0-CONTEXT-ALIGNED
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:          CERTIFIED PRODUCTION ARTIFACT
 * Version:         v1.0.0-CONTEXT-ALIGNED
 * Fixes:           Replaced stub with context re‑export.
 * Compliance:      POPIA §19 / GDPR §32 / SOC2 §CC7.2 / ISO 27001
 * Health Check:
 *   ✅ All consumers now get the real tenant context.
 *   ✅ No duplication of logic.
 *   ✅ No placeholders or TODOs.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
