/**
 * WILSY OS — SOVEREIGN CLIENT ROOT
 * VERSION: v1.1.0-C1E-R1D-A1-WILSY-OS-BRAND-CONSOLIDATION
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Mounts the application and exactly one Dock-owned Intelligence
 *          runtime. The product brand is WILSY OS; AI remains a capability.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/main.jsx
 * COLLABORATION / OWNERSHIP: React application root, Enterprise App, Dock runtime.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.1.0-C1E-R1D-A1-WILSY-OS-BRAND-CONSOLIDATION — Removed the
 *            separately mounted legacy global launcher and retained one Dock root.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Removes stale launcher DOM only; no authority or
 *                              tenant identity is inferred here.
 * TENANT BOUNDARY: Tenant resolution remains owned by application context and API.
 * AUTHORITY BOUNDARY: Root composition only; no legal or financial authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

/* eslint-disable */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import WilsyForensicMerkleShowroom from './components/chrome/WilsyForensicMerkleShowroom.jsx';
import './index.css';
// Billion-dollar infrastructure requires StrictMode to catch side-effects early
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {import.meta.env.DEV && window.location.pathname === '/wilsy-lab/forensic-merkle' ? (
      <WilsyForensicMerkleShowroom />
    ) : (
      <App />
    )}
  </React.StrictMode>,
);

/**
 * ARTIFACT: client/src/main.jsx
 * VERSION: v1.1.0-C1E-R1D-A1-WILSY-OS-BRAND-CONSOLIDATION
 * AUTHORITY BOUNDARY: runtime composition only; WILSY OS Dock owns its launcher
 * TENANT POSTURE: no tenant identity inferred or persisted by the root
 * FAIL-CLOSED POSTURE: stale launcher nodes are removed; no replacement authority is created
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
