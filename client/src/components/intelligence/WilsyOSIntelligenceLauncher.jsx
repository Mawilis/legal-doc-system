/* eslint-disable */
import { useEffect, useRef } from 'react';
import wilsySeal from '../../assets/logo/wilsy.jpeg';
import styles from './WilsyOSIntelligenceLauncher.module.css';

const WILSY_AI_OPEN_EVENTS = ['wilsy-os-intelligence-open-request'];

/**
 * @function removeDuplicateWilsyAILaunchers
 * @description Removes stale, unbranded, and duplicate AI launcher controls so only the official Wilsy-branded launcher remains visible and clickable.
 * @param {HTMLElement|null} currentLauncher - Current official Wilsy AI launcher button.
 * @returns {void} Removes stale launcher controls.
 * @collaboration Wilsy branded launcher, split runtime root, CRM workspace, and browser DOM cleanup.
 */
function removeDuplicateWilsyAILaunchers(currentLauncher) {
  if (typeof document === 'undefined') {
    return;
  }

  const staleRootIds = [
    'wilsy-os-ai-index-fallback-launcher',
    'wilsy-os-intelligence-floating-launcher-guard',
    'wilsy-os-intelligence-launcher-root',
    'wilsy-os-intelligence-global-runtime-root',
    'wilsy-os-intelligence-index-runtime-root',
    'wilsy-os-intelligence-single-runtime-root',
  ];

  staleRootIds.forEach((rootId) => {
    const staleRoot = document.getElementById(rootId);

    if (staleRoot && (!currentLauncher || !staleRoot.contains(currentLauncher))) {
      staleRoot.remove();
    }
  });

  document
    .querySelectorAll('[data-wilsy-ai-global-launcher], [data-wilsy-ai-index-fallback-launcher], [data-wilsy-ai-floating-launcher]')
    .forEach((launcherNode) => {
      if (currentLauncher && launcherNode === currentLauncher) {
        return;
      }

      launcherNode.remove();
    });

  document.querySelectorAll('button, [role="button"]').forEach((buttonNode) => {
    if (currentLauncher && buttonNode === currentLauncher) {
      return;
    }

    const brand = buttonNode.getAttribute('data-wilsy-ai-brand');
    const text = String(buttonNode.textContent || '').replace(/\s+/g, ' ').trim();
    const looksLikeGenericAI = text === 'AI' || text === '• AI' || text === '● AI';

    if (brand !== 'WILSY_OS_SOVEREIGN_AI' && looksLikeGenericAI) {
      buttonNode.remove();
    }
  });
}

/**
 * @function dispatchWilsyAIOpenRequest
 * @description Opens the Wilsy AI dock from the official Wilsy-branded launcher using the mapped dock open event.
 * @returns {void} Dispatches the mapped open request.
 * @collaboration Wilsy OS Intelligence Dock, mapped event bridge, CRM workspace, tenant identity, and no-reset AI workflow.
 */
function dispatchWilsyAIOpenRequest() {
  if (typeof document !== 'undefined') {
    const currentLauncher = document.querySelector('[data-wilsy-ai-brand="WILSY_OS_SOVEREIGN_AI"]');
    removeDuplicateWilsyAILaunchers(currentLauncher);
    document.body.setAttribute('data-wilsy-ai-dock-requested-open', 'true');
  }

  if (typeof window !== 'undefined') {
    WILSY_AI_OPEN_EVENTS.forEach((eventName) => {
      window.dispatchEvent(
        new CustomEvent(eventName, {
          detail: {
            source: 'P60K5Q10CL_SINGLE_WILSY_BRANDED_LAUNCHER',
            generatedAt: new Date().toISOString(),
          },
        })
      );
    });
  }
}

/**
 * @function WilsyOSIntelligenceLauncher
 * @description Renders the only allowed AI launcher: the Wilsy-branded sovereign AI control with seal and mapped dock open behavior.
 * @returns {JSX.Element} Wilsy-branded AI launcher.
 * @collaboration Wilsy OS Intelligence Dock, Wilsy seal identity, split runtime root, tenant productivity shell, and global AI access.
 */
export default function WilsyOSIntelligenceLauncher() {
  const launcherRef = useRef(null);

  useEffect(() => {
    /**
     * @function scrubDuplicateWilsyAILaunchers
     * @description Repeatedly removes stale launcher controls left by hot reloads or previous runtime attempts.
     * @returns {void} Removes duplicate launcher nodes.
     * @collaboration Wilsy branded launcher, browser DOM cleanup, split runtime root, and CRM workspace.
     */
    function scrubDuplicateWilsyAILaunchers() {
      removeDuplicateWilsyAILaunchers(launcherRef.current);
    }

    scrubDuplicateWilsyAILaunchers();
    window.requestAnimationFrame(scrubDuplicateWilsyAILaunchers);

    const sweeps = [
      window.setTimeout(scrubDuplicateWilsyAILaunchers, 100),
      window.setTimeout(scrubDuplicateWilsyAILaunchers, 500),
      window.setTimeout(scrubDuplicateWilsyAILaunchers, 1500),
    ];

    const observer = new MutationObserver(scrubDuplicateWilsyAILaunchers);
    observer.observe(document.body, { childList: true, subtree: true });

    return () => {
      sweeps.forEach((sweep) => window.clearTimeout(sweep));
      observer.disconnect();
    };
  }, []);

  return (
    <button
      ref={launcherRef}
      type="button"
      className={styles.launcher}
      aria-label="Open Wilsy AI"
      data-wilsy-ai-global-launcher="P60K5Q10CL"
      data-wilsy-ai-brand="WILSY_OS_SOVEREIGN_AI"
      onClick={dispatchWilsyAIOpenRequest}
    >
      <span className={styles.sealFrame} aria-hidden="true">
        <img className={styles.seal} src={wilsySeal} alt="" />
      </span>
      <span className={styles.copy}>
        <span className={styles.eyebrow}>WILSY</span>
        <strong>AI</strong>
      </span>
    </button>
  );
}
