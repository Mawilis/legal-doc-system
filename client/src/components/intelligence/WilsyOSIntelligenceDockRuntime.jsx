/**
 * TITLE: Wilsy OS Intelligence Dock Runtime Gate.
 * VERSION: v2.0.0-AUTHENTICATED-MOUNT-GATE
 * AUTHORITY: Wilsy OS Core Governance.
 * EPITOME: Mounts the Intelligence Dock only after a server-issued browser
 *          session exists and the browser is outside the authentication flow.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/intelligence/WilsyOSIntelligenceDockRuntime.jsx
 * COLLABORATION / OWNERSHIP: React root and WilsyOSIntelligenceDock; authContext
 *                            emits the session-state event consumed here.
 * CERTIFICATION / UPDATE DATE: 2026-09-17.
 * CHANGELOG: v2.0.0-AUTHENTICATED-MOUNT-GATE — Prevented protected Dock
 *            hydration and API prefetch before authoritative authentication.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No tenant or identity is inferred; local storage
 *                             is used only as a browser session presence signal.
 * TENANT BOUNDARY: Dock remains downstream of authenticated tenant context.
 * AUTHORITY BOUNDARY: Runtime composition only; legal and financial authority
 *                     remain in their canonical backend authorities.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import WilsyOSIntelligenceDock from './WilsyOSIntelligenceDock.jsx';

export default function WilsyOSIntelligenceDockRuntime({
  authenticated = false,
  authUser = null,
  activeTenant = null,
}) {
  const authTenantId = String(authUser?.tenantId || '').trim();
  const activeTenantId = String(
    activeTenant?.tenantId || activeTenant?._id || '',
  ).trim();

  const eligible = Boolean(
    authenticated === true
    && authUser?.id
    && authTenantId
    && activeTenantId
    && authTenantId === activeTenantId
  );

  if (!eligible) return null;

  return (
    <WilsyOSIntelligenceDock
      authUser={authUser}
      activeTenant={activeTenant}
    />
  );
}

/**
 * ARTIFACT: client/src/components/intelligence/WilsyOSIntelligenceDockRuntime.jsx
 * VERSION: v2.0.0-AUTHENTICATED-MOUNT-GATE
 * AUTHORITY BOUNDARY: runtime composition only; Dock owns its UI projection.
 * TENANT POSTURE: no tenant identity is fabricated by this gate.
 * FAIL-CLOSED POSTURE: absent token or public auth route yields no Dock mount.
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
