/* eslint-disable */
/**
 * @file /Users/wilsonkhanyezi/legal-doc-system/client/src/main.jsx
 * @version 1.0.1
 * @epitome Sovereign Root Initialization - Wilsy OS
 * @description Entry point for the Citadel UI. Enforces StrictMode and global theme injection.
 * * BIBLICAL STANDARDS:
 * - Worth: Billions.
 * - Integrity: StrictMode enabled for forensic debugging.
 * - Future-proof: No child's place.
 * * @collaboration Wilson Khanyezi (Founder), Gemini (Architect)
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import WilsyForensicMerkleShowroom from './components/chrome/WilsyForensicMerkleShowroom.jsx';
import './index.css';
import * as WilsyAISplitRuntimeReactDOM from 'react-dom/client';
import WilsyOSIntelligenceLauncher from './components/intelligence/WilsyOSIntelligenceLauncher.jsx';
import WilsyOSIntelligenceDockRuntime from './components/intelligence/WilsyOSIntelligenceDockRuntime.jsx';
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
 * @function mountWilsyOSIntelligenceSplitRuntimeRoots
 * @description Mounts one Wilsy-branded AI launcher and one separate dock root, then removes any duplicate AI launcher nodes left by stale runtime attempts.
 * @returns {void} Mounts the split AI runtime and enforces one visible Wilsy AI launcher.
 * @collaboration WilsyOSIntelligenceLauncher, WilsyOSIntelligenceDockRuntime, CRM workspace, and no-reset productivity shell.
 */
function mountWilsyOSIntelligenceSplitRuntimeRoots() {
  if (typeof document === 'undefined') {
    return;
  }

  const launcherRootId = 'wilsy-os-intelligence-split-launcher-root';
  const dockRootId = 'wilsy-os-intelligence-split-dock-root';

  const staleSelectors = [
    '#wilsy-os-intelligence-launcher-root',
    '#wilsy-os-intelligence-global-runtime-root',
    '#wilsy-os-intelligence-index-runtime-root',
    '#wilsy-os-intelligence-single-runtime-root',
    '#wilsy-os-ai-index-fallback-launcher',
    '#wilsy-os-intelligence-floating-launcher-guard',
  ];

  staleSelectors.forEach((selector) => {
    document.querySelectorAll(selector).forEach((node) => node.remove());
  });

  document.querySelectorAll(`#${launcherRootId}`).forEach((node, index) => {
    if (index > 0) {
      node.remove();
    }
  });

  let launcherRoot = document.getElementById(launcherRootId);

  if (!launcherRoot) {
    launcherRoot = document.createElement('div');
    launcherRoot.id = launcherRootId;
    launcherRoot.setAttribute('data-wilsy-ai-split-launcher-root', 'P60K5Q10CF');
    document.body.appendChild(launcherRoot);
  }

  if (launcherRoot.getAttribute('data-wilsy-ai-split-launcher-mounted') !== 'true') {
    WilsyAISplitRuntimeReactDOM.createRoot(launcherRoot).render(<WilsyOSIntelligenceLauncher />);
    launcherRoot.setAttribute('data-wilsy-ai-split-launcher-mounted', 'true');
  }

  let dockRoot = document.getElementById(dockRootId);

  if (!dockRoot) {
    dockRoot = document.createElement('div');
    dockRoot.id = dockRootId;
    dockRoot.setAttribute('data-wilsy-ai-split-dock-root', 'P60K5Q10CF');
    document.body.appendChild(dockRoot);
  }

  if (dockRoot.getAttribute('data-wilsy-ai-split-dock-mounted') !== 'true') {
    WilsyAISplitRuntimeReactDOM.createRoot(dockRoot).render(<WilsyOSIntelligenceDockRuntime />);
    dockRoot.setAttribute('data-wilsy-ai-split-dock-mounted', 'true');
  }

  /**
   * @function scrubWilsyAIDuplicateLaunchers
   * @description Removes stale AI launcher buttons that are not owned by the current split launcher root.
   * @returns {void} Removes duplicate launcher nodes.
   * @collaboration Split AI runtime, Wilsy-branded launcher, and stale HMR root cleanup.
   */
  function scrubWilsyAIDuplicateLaunchers() {
    const officialRoot = document.getElementById(launcherRootId);

    document.querySelectorAll('[data-wilsy-ai-global-launcher]').forEach((launcherNode) => {
      if (!officialRoot || !officialRoot.contains(launcherNode)) {
        launcherNode.remove();
      }
    });
  }

  scrubWilsyAIDuplicateLaunchers();
  window.requestAnimationFrame(scrubWilsyAIDuplicateLaunchers);
  window.setTimeout(scrubWilsyAIDuplicateLaunchers, 250);
  window.setTimeout(scrubWilsyAIDuplicateLaunchers, 1000);
}

/* WILSY_P60K5Q10CF_SPLIT_AI_RUNTIME_ROOTS */
mountWilsyOSIntelligenceSplitRuntimeRoots();

