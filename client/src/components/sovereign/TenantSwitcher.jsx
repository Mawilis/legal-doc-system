/**
 * TITLE: WILSY OS Authenticated Tenant Scope Notice
 * VERSION: v2.0.0-GOVERNED-C2-LIFECYCLE-DENY
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Preserves the TenantSwitcher import surface while presenting only the
 *          authenticated workspace tenant and truthful C2 lifecycle availability.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/TenantSwitcher.jsx
 * COLLABORATION / OWNERSHIP: Legacy BillingHUD consumer; TenantContext supplies
 *                            the Python EOS authenticated workspace projection.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v2.0.0-GOVERNED-C2-LIFECYCLE-DENY removes global list, switch,
 *            verify, and suspend controls; renders current scope and C2 status.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No browser role or caller-selected tenant grants authority.
 * TENANT BOUNDARY: Displays only the current authenticated TenantContext projection.
 * AUTHORITY BOUNDARY: Cross-tenant list and lifecycle remain disabled pending governed Python EOS C2.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution and settlement.
 */

import React from 'react';
import { useTenants } from '../../contexts/tenantContext';

/**
 * @description Shows the authenticated current tenant and unavailable C2 controls.
 * @collaboration Retained for former BillingHUD integrations; TenantProvider owns scope.
 * @institutional Prevents old switcher callers from rendering global tenant actions.
 * @returns {JSX.Element} Read-only tenant identity and lifecycle availability.
 */
export default function TenantSwitcher() {
  const { activeTenant, bootstrapReady, authorityMismatch } = useTenants();
  const tenantId = String(
    activeTenant?.tenant_id || activeTenant?.tenantId || activeTenant?.id || '',
  ).trim();
  const available = Boolean(bootstrapReady && !authorityMismatch && tenantId);

  return (
    <section aria-label="Authenticated tenant scope" role="region">
      <h3>Authenticated tenant</h3>
      <p>{available ? (activeTenant?.name || tenantId) : 'Tenant workspace unavailable'}</p>
      {available && <small>{tenantId}</small>}
      <p role="status">
        Global tenant listing, switching, creation, and suspension remain unavailable pending governed Python EOS C2 authority.
      </p>
    </section>
  );
}

/**
 * ARTIFACT: client/src/components/sovereign/TenantSwitcher.jsx
 * VERSION: v2.0.0-GOVERNED-C2-LIFECYCLE-DENY
 * AUTHORITY BOUNDARY: Read-only current workspace projection; no tenant mutation.
 * TENANT POSTURE: Exact authenticated workspace only.
 * FAIL-CLOSED POSTURE: Unavailable until Python EOS bootstrap supplies current scope.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
