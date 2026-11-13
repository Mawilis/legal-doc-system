/**
 * TITLE: WILSY OS SuperAdmin Tenant Lifecycle Availability Page
 * VERSION: v4.0.0-GOVERNED-C2-LIFECYCLE-DENY
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Keeps the legacy navigation target while displaying the exact
 *          authenticated workspace and truthful cross-tenant C2 availability.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/pages/superadmin/Tenants.jsx
 * COLLABORATION / OWNERSHIP: Sidebar route consumer; Python EOS workspace bootstrap
 *                            and Sovereign_TenantManager own the visible projection.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v4.0.0-GOVERNED-C2-LIFECYCLE-DENY removes mock tenant data, global
 *            aggregation, create/suspend/verify API calls, and role-derived authority.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No fake tenants, identity data, or browser-side audit claims.
 * TENANT BOUNDARY: Exact authenticated TenantContext projection only.
 * AUTHORITY BOUNDARY: SuperAdmin presentation does not grant cross-tenant C2 capability.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution and settlement.
 */

import React from 'react';
import SovereignTenantManager from '../../components/sovereign/Sovereign_TenantManager';

/**
 * @description Exposes the read-only Python EOS tenant workspace to the legacy route.
 * @collaboration Mounted by the SuperAdmin tenant navigation surface.
 * @institutional Keeps tenant lifecycle commands disabled until separately governed C2.
 * @returns {JSX.Element} Authenticated current-tenant projection and C2 availability.
 */
export default function Tenants() {
  return <SovereignTenantManager />;
}

/**
 * ARTIFACT: client/src/pages/superadmin/Tenants.jsx
 * VERSION: v4.0.0-GOVERNED-C2-LIFECYCLE-DENY
 * AUTHORITY BOUNDARY: Read-only projection; frontend roles grant no tenant lifecycle authority.
 * TENANT POSTURE: Exact authenticated workspace only.
 * FAIL-CLOSED POSTURE: No directory fallback, fake tenant, or mutation path remains.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
