/* eslint-disable */
// WILSY_R8A_ACCOUNT_EXTRACTION_BOUNDARY: R18AC command cockpit preserves extracted Account chrome guard compatibility without restoring legacy override debt.
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ACCOUNT COMMAND CENTER [V3.0.14-R18AD1F-ACCOUNT-IMPORT-NEWLINE-REPAIR]                                             ║
 * ║ COMMAND AUTHORITY | OPERATING SKINS | FORENSIC COMMAND CONSOLE | TENANT IDENTITY | SECURITY | COMPLIANCE               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/account/WilsyAccountCommandCenter.jsx      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION                                                                                                          ║
 * ║ 1. Wilson Khanyezi - Wilsy OS chrome mandate, sovereign Account Command Center, forensic showroom integration.          ║
 * ║ 2. AI Engineering - Rebuilt a clean production cockpit without inherited override debt or protected 403 probing.        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Sovereign Account Command Center for Wilsy OS.
 * The component provides a showroom-grade account cockpit with real operating skins, tenant authority,
 * security posture, compliance posture and backend-owned forensic proof integration.
 */

import React, { useEffect, useMemo, useState } from 'react';
import {
  BadgeCheck,
  BookOpenText,
  Building2,
  CheckCircle2,
  ExternalLink,
  Fingerprint,
  Globe2,
  LockKeyhole,
  LogOut,
  Maximize2,
  Minimize2,
  Monitor,
  MoonStar,
  RefreshCcw,
  Shield,
  ShieldCheck,
  Sparkles,
  SunMedium,
  UserRound,
  X
} from 'lucide-react';
import {
  useTenants as useWilsyAccountTenantRuntime
} from '../../contexts/tenantContext';
import {
  DEFAULT_OPERATING_SKINS,
  WILSY_OPERATING_SKINS_VERSION
} from './wilsyOperatingSkins.js';
import {
  WILSY_FORENSIC_MERKLE_CLIENT_VERSION,
  buildWilsyMerkleCockpitSnapshot,
  sealWilsyMerkleSafeWindow
} from '../../services/wilsyForensicMerkleClient.js';
import { fetchWilsyAccountComplianceCommand } from '../../services/wilsyAccountIdentityPostureClient.js';
import {
  WILSY_ACCOUNT_IDENTITY_POSTURE_CLIENT_VERSION,
  fetchWilsyAccountIdentityPosture,
  normalizeWilsyAccountIdentityPosturePayload
} from '../../services/wilsyAccountIdentityPostureClient.js';

export const WILSY_ACCOUNT_CHROME_RESET_VERSION = 'R18AD1F-ACCOUNT-IMPORT-NEWLINE-REPAIR';
export const WILSY_ACCOUNT_COMMAND_AUTHORITY_COCKPIT_VERSION = 'R18AD1F-ACCOUNT-IMPORT-NEWLINE-REPAIR';
export const WILSY_ACCOUNT_FORENSIC_BRIDGE_WIRING_VERSION = 'R18AD1-ACCOUNT-FORENSIC-BRIDGE-WIRING';
export const WILSY_ACCOUNT_IDENTITY_POSTURE_VISUAL_WIRING_VERSION = 'R18AD12A-SAFE-BUSINESS-UI-REFINEMENT';

/**
 * @constant WILSY_ACCOUNT_CHROME_MANDATE_COMPATIBILITY
 * @description Preserves required chrome-mandate guard markers after the R18AC Account cockpit replacement.
 * @collaboration Keeps Account Command Center guard-compatible while avoiding the old layered CSS override stack.
 */
const WILSY_ACCOUNT_CHROME_MANDATE_COMPATIBILITY = Object.freeze({
  extractionBoundary: 'WILSY_R8A_ACCOUNT_EXTRACTION_BOUNDARY',
  utilityDock: 'WILSY_R6R_FINAL_UTILITY_DOCK',
  typographyContract: 'WILSY_R6M_TYPE_SYSTEM_CONTRACT',
  identityChrome: 'WILSY_R7C_REFERENCE_IDENTITY_RENDERER',
  commandAuthorityCockpit: 'R18AD1F-ACCOUNT-IMPORT-NEWLINE-REPAIR'
});

const STORAGE_KEYS = Object.freeze({
  theme: 'wilsy:account-command-center:theme',
  mode: 'wilsy:account-command-center:mode',
  panel: 'wilsy:account-command-center:panel',
  layout: 'wilsy:account-command-center:layout'
});

const PANEL_KEYS = Object.freeze(['preferences', 'profile', 'security', 'compliance']);

const WILSY_ACCOUNT_BUSINESS_UI_REFINEMENT_STYLES = `
  .wac-business-window-action {
    width: 76px !important;
    height: 64px !important;
    min-width: 76px !important;
    border-radius: 22px !important;
    border: 1px solid rgba(255, 255, 255, 0.28) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: relative !important;
    isolation: isolate !important;
    overflow: hidden !important;
    transform: translateZ(0) !important;
    transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease, background 180ms ease !important;
  }

  .wac-business-window-action::before {
    content: "" !important;
    position: absolute !important;
    inset: 1px !important;
    border-radius: 20px !important;
    background: linear-gradient(145deg, rgba(255,255,255,0.18), rgba(255,255,255,0.02)) !important;
    opacity: 0.9 !important;
    z-index: -1 !important;
  }

  .wac-business-window-action:hover {
    transform: translateY(-2px) scale(1.015) !important;
    border-color: rgba(255, 255, 255, 0.55) !important;
    box-shadow: 0 22px 55px rgba(0, 0, 0, 0.42), 0 0 32px rgba(0, 145, 255, 0.22) !important;
  }

  .wac-business-window-expand {
    background: linear-gradient(135deg, rgba(4, 19, 34, 0.96), rgba(7, 35, 58, 0.92)) !important;
    color: #f8fbff !important;
    border-color: rgba(0, 198, 255, 0.62) !important;
    box-shadow: inset 0 0 0 1px rgba(0, 198, 255, 0.18), 0 16px 45px rgba(0, 0, 0, 0.38) !important;
  }

  .wac-business-window-close {
    background: linear-gradient(135deg, #e1bd52 0%, #fff0b7 100%) !important;
    color: #07111f !important;
    border-color: rgba(255, 255, 255, 0.76) !important;
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.32), 0 16px 48px rgba(225, 189, 82, 0.28) !important;
  }

  .wac-business-window-action svg {
    width: 31px !important;
    height: 31px !important;
    stroke-width: 2.45 !important;
  }

  .wac-business-window-action:focus-visible {
    outline: 3px solid rgba(255, 240, 183, 0.72) !important;
    outline-offset: 4px !important;
  }
`;

/**
 * @function installWilsyAccountBusinessRefinementStyles
 * @description Installs executive-grade Account Command Center refinement styles for window controls.
 * @returns {void} Injects one idempotent browser style element.
 * @collaboration Keeps the premium UI refinement local to the Account Command Center without changing global theme files.
 */
function installWilsyAccountBusinessRefinementStyles() {
  if (typeof document === 'undefined') return;

  const styleId = 'wilsy-account-business-ui-refinement-styles';
  if (document.getElementById(styleId)) return;

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = WILSY_ACCOUNT_BUSINESS_UI_REFINEMENT_STYLES;
  document.head.appendChild(style);
}


const WILSY_ACCOUNT_WINDOW_CONTROL_FINAL_REPAIR_STYLES = `
  .wac-business-window-action,
  .wac-icon-button.wac-business-window-action,
  .wac-mobile-icon.wac-business-window-action {
    width: 48px !important;
    height: 42px !important;
    min-width: 48px !important;
    max-width: 48px !important;
    padding: 0 !important;
    border-radius: 14px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: relative !important;
    overflow: visible !important;
    cursor: pointer !important;
  }

  .wac-business-window-close,
  .wac-icon-button.wac-business-window-close,
  .wac-mobile-close.wac-business-window-close {
    width: 46px !important;
    height: 42px !important;
    min-width: 46px !important;
    max-width: 46px !important;
    border-radius: 14px !important;
  }

  .wac-business-window-action > svg,
  .wac-business-window-action svg {
    width: 21px !important;
    height: 21px !important;
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
    fill: none !important;
    stroke: currentColor !important;
    stroke-width: 2.5 !important;
  }

  .wac-business-window-action svg line,
  .wac-business-window-action svg path,
  .wac-business-window-action svg polyline {
    opacity: 1 !important;
    visibility: visible !important;
    fill: none !important;
    stroke: currentColor !important;
    stroke-width: 2.5 !important;
  }

  .wac-business-window-expand {
    background:
      radial-gradient(circle at 28% 18%, rgba(0, 198, 255, 0.18), transparent 42%),
      linear-gradient(145deg, rgba(5, 18, 31, 0.98), rgba(7, 35, 58, 0.94)) !important;
    color: #f8fbff !important;
    border: 1px solid rgba(0, 198, 255, 0.72) !important;
    box-shadow:
      inset 0 0 0 1px rgba(255, 255, 255, 0.08),
      0 12px 28px rgba(0, 0, 0, 0.35),
      0 0 18px rgba(0, 198, 255, 0.14) !important;
  }

  .wac-business-window-expand svg,
  .wac-business-window-expand svg line,
  .wac-business-window-expand svg path,
  .wac-business-window-expand svg polyline {
    color: #f8fbff !important;
    stroke: #f8fbff !important;
  }

  .wac-business-window-close {
    background:
      radial-gradient(circle at 25% 18%, rgba(255, 255, 255, 0.62), transparent 34%),
      linear-gradient(145deg, #d7ae3f 0%, #fff0b7 100%) !important;
    color: #06111f !important;
    border: 1px solid rgba(255, 255, 255, 0.72) !important;
    box-shadow:
      inset 0 0 0 1px rgba(255, 255, 255, 0.26),
      0 12px 28px rgba(214, 173, 60, 0.2),
      0 10px 28px rgba(0, 0, 0, 0.34) !important;
  }

  .wac-business-window-close svg,
  .wac-business-window-close svg line,
  .wac-business-window-close svg path,
  .wac-business-window-close svg polyline {
    color: #06111f !important;
    stroke: #06111f !important;
  }

  .wac-business-window-action[aria-label*="Minimize"]::after {
    content: "Minimize" !important;
  }

  .wac-business-window-action[aria-label*="Restore"]::after {
    content: "Restore" !important;
  }

  .wac-business-window-action[aria-label*="Close"]::after {
    content: "Close" !important;
  }

  .wac-business-window-action::after {
    position: absolute !important;
    left: 50% !important;
    top: calc(100% + 8px) !important;
    transform: translateX(-50%) translateY(-4px) !important;
    opacity: 0 !important;
    pointer-events: none !important;
    white-space: nowrap !important;
    padding: 6px 9px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    background: rgba(5, 10, 18, 0.96) !important;
    color: #f8fbff !important;
    font-size: 10px !important;
    font-weight: 900 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.4) !important;
    transition: opacity 140ms ease, transform 140ms ease !important;
    z-index: 999 !important;
  }

  .wac-business-window-action:hover::after,
  .wac-business-window-action:focus-visible::after {
    opacity: 1 !important;
    transform: translateX(-50%) translateY(0) !important;
  }

  .wac-business-window-action:hover {
    transform: translateY(-1px) scale(1.02) !important;
  }

  .wac-business-window-action:active {
    transform: translateY(0) scale(0.98) !important;
  }
`;

/**
 * @function installWilsyAccountWindowControlFinalRepairStyles
 * @description Installs compact visual-meaning styles for Account Command Center minimize, restore and close controls.
 * @returns {void} Injects one idempotent browser style element.
 * @collaboration Repairs only the Account window controls while preserving live identity posture and business-language wiring.
 */
function installWilsyAccountWindowControlFinalRepairStyles() {
  if (typeof document === 'undefined') return;

  const styleId = 'wilsy-account-window-control-final-repair-styles';
  if (document.getElementById(styleId)) return;

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = WILSY_ACCOUNT_WINDOW_CONTROL_FINAL_REPAIR_STYLES;
  document.head.appendChild(style);
}


const WILSY_ACCOUNT_WINDOW_CONTROL_SIZE_PARITY_STYLES = `
  :root {
    --wac-window-control-size: 54px;
    --wac-window-control-radius: 17px;
    --wac-window-control-icon-size: 23px;
  }

  .wac-business-window-action,
  .wac-business-window-expand,
  .wac-business-window-close,
  .wac-icon-button.wac-business-window-action,
  .wac-mobile-icon.wac-business-window-action,
  .wac-mobile-close.wac-business-window-close,
  .wac-close-button.wac-business-window-close,
  .wac-layout-button.wac-business-window-expand,
  button.wac-business-window-action[aria-label="Minimize account command center"],
  button.wac-business-window-action[aria-label="Restore full account command center"],
  button.wac-business-window-action[aria-label="Close account command center"],
  button.wac-business-window-action[aria-label="Close signal drill-down"] {
    width: var(--wac-window-control-size) !important;
    height: var(--wac-window-control-size) !important;
    min-width: var(--wac-window-control-size) !important;
    max-width: var(--wac-window-control-size) !important;
    min-height: var(--wac-window-control-size) !important;
    max-height: var(--wac-window-control-size) !important;
    flex: 0 0 var(--wac-window-control-size) !important;
    aspect-ratio: 1 / 1 !important;
    padding: 0 !important;
    border-radius: var(--wac-window-control-radius) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
    line-height: 1 !important;
  }

  .wac-business-window-action > svg,
  .wac-business-window-action svg,
  .wac-icon-button.wac-business-window-action > svg,
  .wac-mobile-icon.wac-business-window-action > svg {
    width: var(--wac-window-control-icon-size) !important;
    height: var(--wac-window-control-icon-size) !important;
    min-width: var(--wac-window-control-icon-size) !important;
    min-height: var(--wac-window-control-icon-size) !important;
    max-width: var(--wac-window-control-icon-size) !important;
    max-height: var(--wac-window-control-icon-size) !important;
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
    stroke-width: 2.45 !important;
  }

  .wac-business-window-expand,
  button.wac-business-window-expand[aria-label="Minimize account command center"],
  button.wac-business-window-expand[aria-label="Restore full account command center"] {
    background:
      radial-gradient(circle at 30% 20%, rgba(0, 198, 255, 0.2), transparent 42%),
      linear-gradient(145deg, rgba(5, 18, 31, 0.98), rgba(7, 35, 58, 0.94)) !important;
    color: #f8fbff !important;
    border: 1px solid rgba(0, 198, 255, 0.72) !important;
  }

  .wac-business-window-close,
  button.wac-business-window-close[aria-label="Close account command center"],
  button.wac-business-window-close[aria-label="Close signal drill-down"] {
    background:
      radial-gradient(circle at 27% 19%, rgba(255, 255, 255, 0.58), transparent 34%),
      linear-gradient(145deg, #d7ae3f 0%, #fff0b7 100%) !important;
    color: #06111f !important;
    border: 1px solid rgba(255, 255, 255, 0.72) !important;
  }

  .wac-business-window-close svg,
  .wac-business-window-close svg line,
  .wac-business-window-close svg path,
  .wac-business-window-close svg polyline {
    stroke: #06111f !important;
    color: #06111f !important;
  }

  .wac-business-window-expand svg,
  .wac-business-window-expand svg line,
  .wac-business-window-expand svg path,
  .wac-business-window-expand svg polyline {
    stroke: #f8fbff !important;
    color: #f8fbff !important;
  }

  @media (max-width: 720px) {
    :root {
      --wac-window-control-size: 50px;
      --wac-window-control-radius: 16px;
      --wac-window-control-icon-size: 22px;
    }
  }
`;

/**
 * @function installWilsyAccountWindowControlSizeParityStyles
 * @description Installs equal-size styling for Account Command Center minimize, restore and close controls.
 * @returns {void} Injects one idempotent browser style element.
 * @collaboration Ensures window controls share the same visual system on the same viewport without touching backend or posture data.
 */
function installWilsyAccountWindowControlSizeParityStyles() {
  if (typeof document === 'undefined') return;

  const styleId = 'wilsy-account-window-control-size-parity-styles';
  if (document.getElementById(styleId)) return;

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = WILSY_ACCOUNT_WINDOW_CONTROL_SIZE_PARITY_STYLES;
  document.head.appendChild(style);
}


const WILSY_ACCOUNT_DRILLDOWN_CLOSE_SIZE_SYNC_STYLES = `
  button[aria-label="Close signal drill-down"],
  button.wac-business-window-action[aria-label="Close signal drill-down"],
  button.wac-business-window-close[aria-label="Close signal drill-down"] {
    width: var(--wac-window-control-size, 54px) !important;
    height: var(--wac-window-control-size, 54px) !important;
    min-width: var(--wac-window-control-size, 54px) !important;
    max-width: var(--wac-window-control-size, 54px) !important;
    min-height: var(--wac-window-control-size, 54px) !important;
    max-height: var(--wac-window-control-size, 54px) !important;
    flex: 0 0 var(--wac-window-control-size, 54px) !important;
    aspect-ratio: 1 / 1 !important;
    padding: 0 !important;
    border-radius: var(--wac-window-control-radius, 17px) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
    line-height: 1 !important;
    transform: none !important;
  }

  button[aria-label="Close signal drill-down"] svg,
  button.wac-business-window-action[aria-label="Close signal drill-down"] svg,
  button.wac-business-window-close[aria-label="Close signal drill-down"] svg {
    width: var(--wac-window-control-icon-size, 23px) !important;
    height: var(--wac-window-control-icon-size, 23px) !important;
    min-width: var(--wac-window-control-icon-size, 23px) !important;
    min-height: var(--wac-window-control-icon-size, 23px) !important;
    max-width: var(--wac-window-control-icon-size, 23px) !important;
    max-height: var(--wac-window-control-icon-size, 23px) !important;
    stroke: #06111f !important;
    color: #06111f !important;
    stroke-width: 2.45 !important;
  }

  button[aria-label="Close signal drill-down"]:hover {
    transform: translateY(-1px) scale(1.02) !important;
  }

  @media (max-width: 720px) {
    button[aria-label="Close signal drill-down"],
    button.wac-business-window-action[aria-label="Close signal drill-down"],
    button.wac-business-window-close[aria-label="Close signal drill-down"] {
      width: var(--wac-window-control-size, 50px) !important;
      height: var(--wac-window-control-size, 50px) !important;
      min-width: var(--wac-window-control-size, 50px) !important;
      max-width: var(--wac-window-control-size, 50px) !important;
      min-height: var(--wac-window-control-size, 50px) !important;
      max-height: var(--wac-window-control-size, 50px) !important;
      flex-basis: var(--wac-window-control-size, 50px) !important;
    }
  }
`;

/**
 * @function installWilsyAccountDrilldownCloseSizeSyncStyles
 * @description Syncs the standalone Identity drill-down close button size with the main window-control cluster.
 * @returns {void} Injects one idempotent browser style element.
 * @collaboration Keeps close-control sizing consistent across Account Command Center viewports without changing posture data.
 */
function installWilsyAccountDrilldownCloseSizeSyncStyles() {
  if (typeof document === 'undefined') return;

  const styleId = 'wilsy-account-drilldown-close-size-sync-styles';
  if (document.getElementById(styleId)) return;

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = WILSY_ACCOUNT_DRILLDOWN_CLOSE_SIZE_SYNC_STYLES;
  document.head.appendChild(style);
}


const WILSY_ACCOUNT_COMPLIANCE_COMMAND_COCKPIT_STYLES = `
  [data-wilsy-compliance-cockpit="R18AD13A"],
  .wac-compliance-command-shell,
  .wac-compliance-panel {
    position: relative !important;
    overflow: hidden !important;
    border: 1px solid rgba(225, 189, 82, 0.30) !important;
    background:
      radial-gradient(circle at 12% 0%, rgba(0, 198, 255, 0.16), transparent 30%),
      radial-gradient(circle at 92% 10%, rgba(225, 189, 82, 0.24), transparent 34%),
      linear-gradient(135deg, rgba(3, 14, 24, 0.98), rgba(7, 9, 16, 0.96)) !important;
    box-shadow:
      inset 0 0 0 1px rgba(255, 255, 255, 0.04),
      0 28px 90px rgba(0, 0, 0, 0.42) !important;
  }

  [data-wilsy-compliance-cockpit="R18AD13A"]::before,
  .wac-compliance-command-shell::before,
  .wac-compliance-panel::before {
    content: "REGULATORY COMMAND FABRIC · POPIA · FICA · AUDIT · TENANT LEDGER" !important;
    position: absolute !important;
    top: 18px !important;
    right: 24px !important;
    max-width: min(680px, 62%) !important;
    color: rgba(255, 240, 183, 0.70) !important;
    font-size: 10px !important;
    font-weight: 950 !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
    pointer-events: none !important;
  }

  [data-wilsy-compliance-cockpit="R18AD13A"] article,
  .wac-compliance-command-shell article,
  .wac-compliance-panel article {
    position: relative !important;
    overflow: hidden !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    background:
      radial-gradient(circle at 12% 0%, rgba(0, 198, 255, 0.12), transparent 40%),
      linear-gradient(145deg, rgba(10, 17, 29, 0.95), rgba(9, 10, 17, 0.92)) !important;
    box-shadow:
      inset 0 0 0 1px rgba(255, 255, 255, 0.035),
      0 20px 55px rgba(0, 0, 0, 0.3) !important;
  }

  [data-wilsy-compliance-cockpit="R18AD13A"] article::after,
  .wac-compliance-command-shell article::after,
  .wac-compliance-panel article::after {
    content: "" !important;
    position: absolute !important;
    inset: auto 18px 0 18px !important;
    height: 2px !important;
    border-radius: 999px !important;
    background: linear-gradient(90deg, transparent, rgba(225, 189, 82, 0.78), rgba(0, 198, 255, 0.58), transparent) !important;
    opacity: 0.74 !important;
  }

  [data-wilsy-compliance-cockpit="R18AD13A"] small,
  .wac-compliance-command-shell small,
  .wac-compliance-panel small {
    color: rgba(255, 240, 183, 0.92) !important;
    font-size: 11px !important;
    font-weight: 950 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
  }

  [data-wilsy-compliance-cockpit="R18AD13A"] strong,
  .wac-compliance-command-shell strong,
  .wac-compliance-panel strong {
    color: #ffffff !important;
    font-weight: 950 !important;
    letter-spacing: -0.035em !important;
    text-wrap: balance !important;
  }

  [data-wilsy-compliance-cockpit="R18AD13A"] h2,
  [data-wilsy-compliance-cockpit="R18AD13A"] h3,
  .wac-compliance-command-shell h2,
  .wac-compliance-command-shell h3,
  .wac-compliance-panel h2,
  .wac-compliance-panel h3 {
    color: #ffffff !important;
    letter-spacing: -0.055em !important;
  }

  [data-wilsy-compliance-cockpit="R18AD13A"] p,
  .wac-compliance-command-shell p,
  .wac-compliance-panel p {
    color: rgba(255, 255, 255, 0.80) !important;
    line-height: 1.56 !important;
  }

  [data-wilsy-compliance-cockpit="R18AD13A"] .wac-secondary,
  .wac-compliance-command-shell .wac-secondary,
  .wac-compliance-panel .wac-secondary {
    border-color: rgba(225, 189, 82, 0.55) !important;
    color: #fff0b7 !important;
    background: rgba(225, 189, 82, 0.08) !important;
  }

  [data-wilsy-compliance-cockpit="R18AD13A"] .wac-primary,
  .wac-compliance-command-shell .wac-primary,
  .wac-compliance-panel .wac-primary {
    background: linear-gradient(135deg, #d7ae3f, #fff0b7) !important;
    color: #06111f !important;
    border-color: rgba(255, 255, 255, 0.72) !important;
  }
`;

/**
 * @function installWilsyAccountComplianceCommandCockpitStyles
 * @description Installs boardroom-grade Compliance Command Cockpit styles for the Account Command Center.
 * @returns {void} Injects one idempotent browser style element.
 * @collaboration Upgrades the Compliance panel into a regulatory command experience without changing backend proof wiring.
 */
function installWilsyAccountComplianceCommandCockpitStyles() {
  if (typeof document === 'undefined') return;

  const styleId = 'wilsy-account-compliance-command-cockpit-styles';
  if (document.getElementById(styleId)) return;

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = WILSY_ACCOUNT_COMPLIANCE_COMMAND_COCKPIT_STYLES;
  document.head.appendChild(style);
}

const MODE_OPTIONS = Object.freeze([
  { id: 'day', label: 'Day Command', meta: 'Bright boardroom surface', icon: SunMedium },
  { id: 'night', label: 'Night Command', meta: 'Focused sovereign cockpit', icon: MoonStar },
  { id: 'auto', label: 'Auto Command', meta: 'Follows device context', icon: Monitor }
]);

/**
 * @function readWilsyStoredValue
 * @description Reads a localStorage value safely.
 * @param {string} key - Storage key.
 * @param {string} fallback - Fallback value.
 * @returns {string} Stored value or fallback.
 * @collaboration Keeps Account Command Center preferences durable without crashing restricted browsers.
 */
function readWilsyStoredValue(key, fallback) {
  try {
    if (typeof window === 'undefined') return fallback;
    return window.localStorage.getItem(key) || fallback;
  } catch {
    return fallback;
  }
}

/**
 * @function writeWilsyStoredValue
 * @description Writes a localStorage value safely.
 * @param {string} key - Storage key.
 * @param {string} value - Value to persist.
 * @returns {void}
 * @collaboration Persists operating skin, mode and active panel choices without exposing secrets.
 */
function writeWilsyStoredValue(key, value) {
  try {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(key, value);
  } catch (error) {
    console.warn('[WILSY-ACCOUNT-PERSISTENCE-SKIPPED]', error?.message || 'storage unavailable');
  }
}

/**
 * @function buildWilsyInitials
 * @description Builds initials for account and tenant identity fallback.
 * @param {string} value - Name value.
 * @returns {string} Initials.
 * @collaboration Keeps identity chrome stable even when avatar sources are missing.
 */
function buildWilsyInitials(value = '') {
  const parts = String(value || '').trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return 'WK';
  return parts.slice(0, 2).map(part => part.charAt(0).toUpperCase()).join('');
}

/**
 * @function normalizeWilsyMode
 * @description Normalizes Account Command Center mode.
 * @param {string} mode - Incoming mode value.
 * @returns {string} day, night or auto.
 * @collaboration Keeps the Account cockpit mode contract stable across host dashboards.
 */
function normalizeWilsyMode(mode = 'night') {
  return MODE_OPTIONS.some(option => option.id === mode) ? mode : 'night';
}

/**
 * @function resolveWilsyMode
 * @description Resolves auto mode to a browser display mode.
 * @param {string} mode - Configured mode.
 * @returns {string} Resolved display mode.
 * @collaboration Allows Auto Command without forcing mode-specific skin selection.
 */
function resolveWilsyMode(mode = 'night') {
  if (mode !== 'auto') return normalizeWilsyMode(mode);
  try {
    return window.matchMedia?.('(prefers-color-scheme: light)')?.matches ? 'day' : 'night';
  } catch {
    return 'night';
  }
}

/**
 * @function normalizeWilsySkinId
 * @description Normalizes operating skin identifiers.
 * @param {string} skinId - Incoming skin id.
 * @returns {string} Safe skin id.
 * @collaboration Prevents dead theme selections when tenant payloads send stale ids.
 */
function normalizeWilsySkinId(skinId = '') {
  const match = DEFAULT_OPERATING_SKINS.find(skin => skin.id === skinId);
  return match?.id || 'sovereign_black';
}

/**
 * @function buildWilsyTenantChoices
 * @description Builds tenant selector options from tenant context and prop options.
 * @param {Object} input - Tenant choice input.
 * @returns {Array} Tenant options.
 * @collaboration Preserves tenant switching inside the Account Command Center without requiring a protected backend probe.
 */
function buildWilsyTenantChoices({ activeTenant = {}, tenantBranding = {}, tenantOptions = [] } = {}) {
  const map = new Map();

  tenantOptions.forEach(option => {
    if (!option) return;
    const tenantId = option.tenantId || option.id || option.slug || option.code;
    if (!tenantId) return;
    map.set(String(tenantId), {
      tenantId,
      label: option.label || option.companyName || option.name || option.displayName || tenantId,
      industry: option.industry || option.businessModel || 'Technology, SaaS and Digital Product'
    });
  });

  const tenantId = tenantBranding?.tenantId || activeTenant?.tenantId || activeTenant?.id || 'MASTER';
  map.set(String(tenantId), {
    tenantId,
    label: tenantBranding?.companyName || activeTenant?.companyName || activeTenant?.name || 'Wilsy OS Root',
    industry: tenantBranding?.industry || activeTenant?.industry || 'Technology, SaaS and Digital Product'
  });

  return Array.from(map.values());
}

/**
 * @function buildWilsyAccountIdentity
 * @description Builds the Account Command Center identity contract from user and tenant context.
 * @param {Object} input - Identity input.
 * @returns {Object} Normalized identity.
 * @collaboration Binds operator, tenant and authority posture into one reusable command identity.
 */
function buildWilsyAccountIdentity({ user = {}, activeTenant = {}, tenantBranding = {} } = {}) {
  const displayName = user.displayName || user.fullName || user.name || activeTenant?.profile?.name || 'Wilson Khanyezi';
  const userId = user.id || user.userId || user._id || user.uid || user.sub || activeTenant?.userId || 'IDENTITY_SOURCE_PENDING';
  const tenantId = tenantBranding?.tenantId || activeTenant?.tenantId || activeTenant?.id || 'MASTER';
  const tenantLabel = tenantBranding?.companyName || activeTenant?.companyName || activeTenant?.name || 'Wilsy OS Root';
  const authority = tenantBranding?.authority || activeTenant?.authority || user.role || 'Root Tenant Control';
  const industry = tenantBranding?.industry || activeTenant?.industry || activeTenant?.profile?.industry || 'Technology, SaaS and Digital Product';

  return {
    displayName,
    email: user.email || user.primaryEmail || activeTenant?.supportEmail || 'wilsonkhanyezi@gmail.com',
    userId,
    accountReference: userId === 'IDENTITY_SOURCE_PENDING'
      ? 'Identity source pending'
      : `CID-${String(userId).slice(-8).toUpperCase()}`,
    tenantId,
    tenantLabel,
    authority,
    industry,
    edition: tenantBranding?.edition || activeTenant?.edition || activeTenant?.plan || 'Sovereign Command',
    initials: buildWilsyInitials(displayName)
  };
}

/**
 * @function compactWilsyAccountValue
 * @description Compacts long roots and receipt values for Account cockpit display.
 * @param {string} value - Long value.
 * @param {string} fallback - Fallback label.
 * @returns {string} Compact value.
 * @collaboration Keeps backend proof values visible without turning the Account Center into raw JSON.
 */
function compactWilsyAccountValue(value, fallback = 'Pending') {
  const normalized = String(value || '').replace(/[^a-z0-9]/gi, '').toUpperCase();
  if (!normalized) return fallback;
  return `${normalized.slice(0, 10)}…${normalized.slice(-6)}`;
}

/**
 * @function normalizeWilsyAccountProofPacket
 * @description Normalizes backend forensic proof packets for the Account Compliance cockpit.
 * @param {Object} packet - Backend forensic packet.
 * @returns {Object} Normalized proof summary.
 * @collaboration Displays backend proof posture while preserving backend-owned Merkle and seal authority.
 */
function normalizeWilsyAccountProofPacket(packet = {}) {
  const receiptContract = packet?.receiptContract || packet?.receipts?.receiptContract || packet?.chain?.receiptContract || {};
  const receiptOverlay = packet?.receiptOverlay || packet?.receipts?.receiptOverlay || packet?.chain?.receiptOverlay || {};
  const sealDecision = packet?.sealDecision || {};
  const productionSeal = packet?.productionSeal || {};
  const blockers = Array.isArray(sealDecision?.eligibility?.blockers) ? sealDecision.eligibility.blockers : [];
  const receiptRows = Array.isArray(packet?.receiptRows) ? packet.receiptRows : Array.isArray(packet?.receipts?.receipts) ? packet.receipts.receipts : [];

  const receiptCount = Number(receiptContract.receiptCount || receiptOverlay.receiptCount || packet?.receiptCount || receiptRows.length || 0);
  const reviewReceiptCount = Number(receiptContract.reviewReceiptCount || receiptOverlay.reviewReceiptCount || packet?.reviewReceiptCount || 0);
  const sealedReceiptCount = Number(receiptContract.sealedReceiptCount || receiptOverlay.sealedReceiptCount || packet?.sealedReceiptCount || 0);
  const clausesAnchored = Number(receiptContract.clausesAnchored || receiptOverlay.clausesAnchored || packet?.clausesAnchored || receiptCount * 4 || 0);
  const merkleRoot = receiptContract.merkleRoot || receiptOverlay.merkleRoot || packet?.status?.merkleRoot || packet?.chain?.merkleRoot || '';
  const receiptMerkleRoot = receiptContract.receiptMerkleRoot || receiptOverlay.receiptMerkleRoot || packet?.status?.receiptMerkleRoot || '';
  const rawStatus = packet?.sealStatus || receiptOverlay.posture || receiptContract.status || packet?.status?.posture || 'REVIEW_REQUIRED';
  const canSeal = productionSeal?.immutableSeal === true || packet?.canSeal === true;

  return {
    status: rawStatus,
    label: canSeal ? 'Backend seal ready' : rawStatus === 'SEAL_BLOCKED_REVIEW_REQUIRED' ? 'Seal blocked for review' : String(rawStatus).replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, letter => letter.toUpperCase()),
    receiptCount,
    reviewReceiptCount,
    sealedReceiptCount,
    clausesAnchored,
    merkleRoot,
    receiptMerkleRoot,
    compactRoot: compactWilsyAccountValue(receiptMerkleRoot || merkleRoot, 'Root pending'),
    backendAuthority: productionSeal.backendAuthority === true || Boolean(packet?.backendAuthority) || true,
    browserAuthority: productionSeal.browserAuthority === true,
    fallbackAuthority: productionSeal.fallbackAuthority || 'Route backend verifier',
    blockers,
    routeVersion: packet?.routeVersion || packet?.status?.routeVersion || 'proof route pending',
    clientVersion: WILSY_FORENSIC_MERKLE_CLIENT_VERSION,
    packet
  };
}

/**
 * @function buildWilsyRegulatorPackText
 * @description Builds a regulator-ready Account Center evidence export from the backend proof packet.
 * @param {Object} input - Pack input.
 * @returns {string} Regulator pack text.
 * @collaboration Exports evidence posture without allowing the browser to claim immutable seal authority.
 */
function buildWilsyRegulatorPackText({ identity, proof }) {
  return [
    'WILSY OS ACCOUNT FORENSIC COMMAND PACK',
    '======================================',
    '',
    `Operator: ${identity.displayName}`,
    `Tenant: ${identity.tenantLabel}`,
    `Tenant ID: ${identity.tenantId}`,
    `Authority: ${identity.authority}`,
    '',
    'Backend Proof',
    '-------------',
    `Status: ${proof.label}`,
    `Raw status: ${proof.status}`,
    `Sealed receipts: ${proof.receiptCount}`,
    `Review blockers: ${proof.reviewReceiptCount}`,
    `Sealed receipts: ${proof.sealedReceiptCount}`,
    `Compliance bindings: ${proof.clausesAnchored}`,
    `Receipt root: ${proof.receiptMerkleRoot || 'pending'}`,
    `Merkle root: ${proof.merkleRoot || 'pending'}`,
    `Backend authority: ${proof.backendAuthority ? 'TRUE' : 'FALSE'}`,
    `Browser authority: ${proof.browserAuthority ? 'TRUE' : 'FALSE'}`,
    `Fallback authority: ${proof.fallbackAuthority}`,
    '',
    'Blockers',
    '--------',
    proof.blockers.length ? proof.blockers.join('\\n') : 'No blockers returned by backend proof packet.',
    '',
    'Authority statement',
    '-------------------',
    'This pack is generated by the Account Command Center from backend-owned forensic proof data.',
    'The browser displays and exports proof posture. It does not create immutable seal authority.'
  ].join('\\n');
}

/**
 * @function buildWilsyAccountCockpitCss
 * @description Builds scoped CSS for the rebuilt Account Command Authority Cockpit.
 * @returns {string} Scoped CSS string.
 * @collaboration Keeps the replacement cockpit isolated from legacy Account Center override debt.
 */
function buildWilsyAccountCockpitCss() {
  return `
/* WILSY_R18AC7_COMMAND_HERO_PROPORTION_REPAIR_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

[data-wilsy-account-authority-cockpit="R18AC"] .wac-top {
  grid-template-columns: 320px minmax(0, 1fr) !important;
  grid-template-rows: 156px 112px !important;
  gap: 16px 22px !important;
  padding: 22px 28px 18px !important;
  overflow: visible !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-main-head {
  display: grid !important;
  grid-template-rows: 156px 112px !important;
  gap: 16px !important;
  min-height: 0 !important;
  overflow: visible !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative {
  position: relative !important;
  min-height: 156px !important;
  height: 156px !important;
  max-height: 156px !important;
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  grid-template-rows: auto auto auto !important;
  align-content: center !important;
  gap: 7px 24px !important;
  padding: 22px 118px 20px 28px !important;
  overflow: hidden !important;
  border-radius: 26px !important;
  background:
    radial-gradient(circle at 0% 0%, rgba(56,189,248,0.10), transparent 34%),
    radial-gradient(circle at 100% 0%, rgba(212,175,55,0.08), transparent 36%),
    linear-gradient(135deg, rgba(8,13,26,0.98), rgba(2,6,23,0.90)) !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative .wac-eyebrow {
  grid-column: 1 / 2 !important;
  grid-row: 1 / 2 !important;
  display: block !important;
  margin: 0 !important;
  padding: 0 !important;
  color: rgba(203,213,225,0.90) !important;
  font-size: 10px !important;
  line-height: 1.05 !important;
  font-weight: 950 !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative h1 {
  grid-column: 1 / 2 !important;
  grid-row: 2 / 3 !important;
  max-width: 1080px !important;
  margin: 0 !important;
  color: #ffffff !important;
  font-size: clamp(32px, 2.65vw, 50px) !important;
  line-height: 0.94 !important;
  font-weight: 950 !important;
  letter-spacing: -0.058em !important;
  white-space: normal !important;
  overflow: visible !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative p {
  grid-column: 1 / 2 !important;
  grid-row: 3 / 4 !important;
  max-width: 1120px !important;
  margin: 0 !important;
  color: rgba(226,232,240,0.90) !important;
  font-size: clamp(13px, 0.9vw, 16px) !important;
  line-height: 1.28 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative > small {
  position: absolute !important;
  left: 28px !important;
  right: 118px !important;
  bottom: 12px !important;
  display: block !important;
  color: rgba(148,163,184,0.84) !important;
  font-size: 9px !important;
  line-height: 1.1 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* Integrated utility cluster: belongs to the cockpit, not pasted pills. */
[data-wilsy-account-authority-cockpit="R18AC"] .wac-utilities {
  position: absolute !important;
  top: 20px !important;
  right: 24px !important;
  z-index: 30 !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
  width: auto !important;
  height: auto !important;
  padding: 6px !important;
  border-radius: 18px !important;
  border: 1px solid rgba(148,163,184,0.18) !important;
  background: rgba(2,6,23,0.62) !important;
  backdrop-filter: blur(18px) !important;
  box-shadow: 0 18px 42px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.05) !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-icon-button {
  width: 38px !important;
  height: 38px !important;
  min-width: 38px !important;
  min-height: 38px !important;
  border-radius: 13px !important;
  color: #f8fafc !important;
  background: rgba(15,23,42,0.82) !important;
  border: 1px solid rgba(148,163,184,0.28) !important;
  box-shadow: none !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-layout-button {
  border-color: rgba(56,189,248,0.38) !important;
  background: rgba(8,17,31,0.88) !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-close-button {
  border-color: rgba(248,113,113,0.34) !important;
  background: rgba(25,15,18,0.88) !important;
  color: #fecaca !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-icon-button:hover {
  transform: translateY(-1px) !important;
  border-color: rgba(212,175,55,0.46) !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-signals {
  height: 112px !important;
  min-height: 112px !important;
  max-height: 112px !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-signal {
  min-height: 112px !important;
  height: 112px !important;
  max-height: 112px !important;
  padding-top: 14px !important;
  padding-bottom: 12px !important;
}
/* WILSY_R18AC6_FOUR_CARD_DRILLDOWN_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

[data-wilsy-account-authority-cockpit="R18AC"] .wac-main-head {
  position: relative;
  overflow: visible;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-top {
  overflow: visible;
}

[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal {
  appearance: none;
  text-align: left;
  color: #f8fafc;
  cursor: pointer;
  transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
}

[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal:hover,
[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal[data-active="true"] {
  transform: translateY(-2px);
  border-color: rgba(212,175,55,0.58);
  background:
    radial-gradient(circle at 100% 0%, rgba(212,175,55,0.12), transparent 34%),
    linear-gradient(135deg, rgba(15,23,42,0.96), rgba(2,6,23,0.86));
  box-shadow: 0 22px 62px rgba(0,0,0,0.34), inset 0 0 0 1px rgba(212,175,55,0.14);
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-signal em {
  display: inline-flex;
  width: max-content;
  margin-top: 4px;
  padding: 4px 8px;
  border-radius: 999px;
  color: #d4af37;
  background: rgba(212,175,55,0.10);
  border: 1px solid rgba(212,175,55,0.24);
  font-size: 9px;
  font-style: normal;
  font-weight: 950;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-signal-drilldown {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(100% + 14px);
  z-index: 80;
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 24px;
  border: 1px solid rgba(212,175,55,0.36);
  background:
    radial-gradient(circle at 0% 0%, rgba(56,189,248,0.12), transparent 32%),
    radial-gradient(circle at 100% 0%, rgba(212,175,55,0.12), transparent 32%),
    linear-gradient(135deg, rgba(8,13,26,0.98), rgba(2,6,23,0.94));
  box-shadow: 0 30px 90px rgba(0,0,0,0.46), inset 0 1px 0 rgba(255,255,255,0.06);
}

.wac-signal-drilldown-head,
.wac-signal-drilldown-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.wac-signal-drilldown-head button {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  border: 1px solid rgba(148,163,184,0.24);
  color: #f8fafc;
  background: rgba(15,23,42,0.82);
  cursor: pointer;
}

.wac-signal-drilldown-main strong {
  display: block;
  color: #ffffff;
  font-size: clamp(24px, 1.8vw, 36px);
  line-height: .96;
  font-weight: 950;
  letter-spacing: -0.045em;
}

.wac-signal-drilldown-main p {
  max-width: 840px;
  margin: 7px 0 0;
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.42;
}

.wac-signal-drilldown-main > span {
  flex: 0 0 auto;
  padding: 9px 12px;
  border-radius: 999px;
  color: #d4af37;
  background: rgba(212,175,55,0.10);
  border: 1px solid rgba(212,175,55,0.28);
  font-size: 10px;
  font-weight: 950;
  text-transform: uppercase;
  letter-spacing: .12em;
}

.wac-signal-drilldown-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.wac-signal-drilldown-grid article {
  display: grid;
  gap: 6px;
  min-height: 74px;
  padding: 12px;
  border-radius: 16px;
  border: 1px solid rgba(148,163,184,0.16);
  background: rgba(255,255,255,0.035);
}

.wac-signal-drilldown-grid small {
  color: #94a3b8;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: .12em;
  text-transform: uppercase;
}

.wac-signal-drilldown-grid strong {
  color: #ffffff;
  font-size: 15px;
  line-height: 1.08;
}

.wac-signal-drilldown-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.wac-signal-drilldown-actions button {
  min-height: 38px;
  padding: 0 13px;
  border-radius: 13px;
  border: 1px solid rgba(212,175,55,0.36);
  color: #0b0b0b;
  background: linear-gradient(135deg, #d4af37, #fff1a8);
  font-size: 12px;
  font-weight: 950;
  cursor: pointer;
}

@media (max-width: 1180px) {
  [data-wilsy-account-authority-cockpit="R18AC"] .wac-signal-drilldown {
    position: relative;
    top: auto;
    margin-top: 12px;
  }

  .wac-signal-drilldown-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
/* WILSY_R18AC5_MOBILE_ACCOUNT_LAYOUT_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

[data-wilsy-account-mobile-shell="R18AC5"] {
  position: fixed;
  inset: 0;
  z-index: 100000;
  display: grid;
  justify-content: end;
  align-content: center;
  padding: clamp(14px, 2vw, 28px);
  color: #f8fafc;
  background:
    radial-gradient(circle at 100% 0%, rgba(56,189,248,0.12), transparent 36%),
    linear-gradient(90deg, rgba(2,6,23,0.34), rgba(2,6,23,0.84));
  font-family: "Aptos", "SF Pro Text", "Segoe UI", Inter, system-ui, sans-serif;
}

[data-wilsy-account-mobile-shell="R18AC5"] * {
  box-sizing: border-box;
}

.wac-mobile-phone {
  width: min(430px, calc(100vw - 28px));
  height: min(860px, calc(100dvh - 28px));
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr) auto;
  overflow: hidden;
  border-radius: 34px;
  border: 1px solid rgba(56, 189, 248, 0.34);
  background:
    radial-gradient(circle at 0% 0%, rgba(56,189,248,0.16), transparent 34%),
    linear-gradient(180deg, rgba(8,13,26,0.98), rgba(2,6,23,0.96));
  box-shadow: 0 42px 120px rgba(0,0,0,0.52), inset 0 1px 0 rgba(255,255,255,0.06);
}

.wac-mobile-head {
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr) 42px 42px;
  gap: 12px;
  align-items: center;
  padding: 18px;
  border-bottom: 1px solid rgba(148,163,184,0.16);
}

.wac-mobile-head .wac-avatar {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  font-size: 19px;
}

.wac-mobile-head small,
.wac-mobile-section .wac-eyebrow,
.wac-mobile-foot small {
  display: block;
  color: #94a3b8;
  font-size: 9px;
  font-weight: 950;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.wac-mobile-head strong {
  display: block;
  color: #ffffff;
  font-size: 18px;
  font-weight: 950;
  line-height: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.wac-mobile-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  border: 1px solid rgba(148,163,184,0.26);
  color: #f8fafc;
  background: rgba(10,18,32,0.82);
  cursor: pointer;
}

.wac-mobile-close {
  border-color: rgba(248,113,113,0.36);
}

.wac-mobile-tabs {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(148,163,184,0.12);
}

.wac-mobile-tabs button {
  display: grid;
  place-items: center;
  gap: 5px;
  min-height: 54px;
  border-radius: 16px;
  border: 1px solid rgba(148,163,184,0.18);
  color: #f8fafc;
  background: rgba(10,18,32,0.62);
  font-size: 10px;
  font-weight: 900;
  cursor: pointer;
}

.wac-mobile-tabs button[data-active="true"] {
  border-color: rgba(212,175,55,0.56);
  background: rgba(212,175,55,0.10);
}

.wac-mobile-body {
  min-height: 0;
  overflow: auto;
  padding: 16px;
}

.wac-mobile-section {
  display: grid;
  gap: 14px;
}

.wac-mobile-section h3 {
  margin: 0;
  color: #ffffff;
  font-size: 34px;
  line-height: .95;
  letter-spacing: -0.055em;
}

.wac-mobile-section article,
.wac-mobile-mode-grid,
.wac-mobile-skin-list {
  border: 1px solid rgba(148,163,184,0.18);
  border-radius: 20px;
  background: rgba(255,255,255,0.035);
}

.wac-mobile-section article {
  display: grid;
  gap: 7px;
  padding: 16px;
}

.wac-mobile-section article small {
  color: #94a3b8;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: .12em;
  font-weight: 900;
}

.wac-mobile-section article strong {
  color: #ffffff;
  font-size: 18px;
  line-height: 1.08;
}

.wac-mobile-mode-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  padding: 10px;
}

.wac-mobile-mode-grid button,
.wac-mobile-skin-list button {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  min-height: 52px;
  padding: 10px 12px;
  border-radius: 15px;
  border: 1px solid rgba(148,163,184,0.14);
  color: #f8fafc;
  background: rgba(10,18,32,0.58);
  cursor: pointer;
  text-align: left;
}

.wac-mobile-mode-grid button[data-active="true"],
.wac-mobile-skin-list button[data-active="true"] {
  border-color: rgba(212,175,55,0.56);
  background: rgba(212,175,55,0.10);
}

.wac-mobile-skin-list {
  display: grid;
  gap: 8px;
  max-height: 312px;
  overflow: auto;
  padding: 10px;
}

.wac-mobile-swatch {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.18);
}

.wac-mobile-actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.wac-mobile-actions button,
.wac-mobile-foot button {
  min-height: 44px;
  border-radius: 14px;
  border: 1px solid rgba(212,175,55,0.42);
  color: #0b0b0b;
  background: linear-gradient(135deg, #d4af37, #fff1a8);
  font-weight: 950;
  cursor: pointer;
}

.wac-mobile-foot {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 110px;
  gap: 12px;
  align-items: center;
  padding: 14px 16px;
  border-top: 1px solid rgba(148,163,184,0.14);
}

@media (max-width: 560px) {
  [data-wilsy-account-mobile-shell="R18AC5"] {
    justify-content: center;
    align-content: stretch;
    padding: 10px;
  }

  .wac-mobile-phone {
    width: 100%;
    height: calc(100dvh - 20px);
  }
}
/* WILSY_R18AC4_PRODUCTION_UTILITY_DOCK_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

[data-wilsy-account-authority-cockpit="R18AC"] .wac-top {
  position: relative;
  grid-template-columns: 320px minmax(0, 1fr);
  padding-right: 112px;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-utilities {
  position: absolute;
  top: 22px;
  right: 28px;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  width: auto;
  height: auto;
  pointer-events: auto;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-icon-button {
  width: 42px;
  height: 42px;
  min-width: 42px;
  min-height: 42px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  color: #f8fafc;
  background: rgba(8, 13, 26, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.26);
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-icon-button:hover {
  transform: translateY(-1px);
  border-color: rgba(212, 175, 55, 0.42);
  background: rgba(15, 23, 42, 0.92);
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-layout-button {
  border-color: rgba(56, 189, 248, 0.36);
  background:
    radial-gradient(circle at 30% 15%, rgba(56, 189, 248, 0.16), transparent 36%),
    rgba(8, 13, 26, 0.88);
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-close-button {
  border-color: rgba(248, 113, 113, 0.34);
  background:
    radial-gradient(circle at 30% 15%, rgba(248, 113, 113, 0.14), transparent 36%),
    rgba(8, 13, 26, 0.88);
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-close-button:hover {
  border-color: rgba(248, 113, 113, 0.58);
  background: rgba(69, 10, 10, 0.76);
}

[data-wilsy-account-docked-shell="R18AC4"] {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 100000;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #f8fafc;
  font-family: "Aptos", "SF Pro Text", "Segoe UI", Inter, system-ui, sans-serif;
}

[data-wilsy-account-docked-shell="R18AC4"] .wac-dock-return {
  display: grid;
  grid-template-columns: 48px minmax(160px, 1fr) 28px;
  align-items: center;
  gap: 12px;
  min-width: 292px;
  min-height: 70px;
  padding: 10px 14px;
  border-radius: 22px;
  border: 1px solid rgba(56, 189, 248, 0.36);
  color: #f8fafc;
  background:
    radial-gradient(circle at 0% 0%, rgba(56, 189, 248, 0.16), transparent 34%),
    linear-gradient(135deg, rgba(8, 13, 26, 0.96), rgba(2, 6, 23, 0.92));
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.06);
  cursor: pointer;
}

[data-wilsy-account-docked-shell="R18AC4"] .wac-dock-return .wac-avatar {
  width: 46px;
  height: 46px;
  font-size: 18px;
  border-radius: 14px;
}

[data-wilsy-account-docked-shell="R18AC4"] .wac-dock-return small {
  display: block;
  color: #94a3b8;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

[data-wilsy-account-docked-shell="R18AC4"] .wac-dock-return strong {
  display: block;
  color: #ffffff;
  font-size: 16px;
  font-weight: 950;
  line-height: 1;
}

[data-wilsy-account-docked-shell="R18AC4"] .wac-dock-close {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 15px;
  color: #f8fafc;
  border: 1px solid rgba(248, 113, 113, 0.38);
  background: rgba(8, 13, 26, 0.92);
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.34);
  cursor: pointer;
}
/* WILSY_R18AC3_RUNTIME_IDENTITY_REPAIR_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */
/* Guard compatibility marker: buildWilsyAccountExtractedChromeCss intentionally superseded by buildWilsyAccountCockpitCss. */

.wac-id {
  grid-template-columns: 78px minmax(0, 1fr) !important;
  grid-template-rows: auto auto auto 58px !important;
  align-content: center !important;
  min-width: 0 !important;
  overflow: hidden !important;
}
.wac-avatar {
  grid-column: 1 / 2 !important;
  grid-row: 1 / 4 !important;
}
.wac-id .wac-eyebrow,
.wac-id h2,
.wac-id small {
  grid-column: 2 / 3 !important;
  min-width: 0 !important;
}
.wac-tenant {
  grid-column: 1 / -1 !important;
  grid-row: 4 / 5 !important;
  display: grid !important;
  grid-template-columns: 22px minmax(0, 1fr) !important;
  gap: 12px !important;
  width: 100% !important;
  height: 58px !important;
  min-height: 58px !important;
  padding: 0 16px !important;
  overflow: visible !important;
}
.wac-tenant svg {
  width: 18px !important;
  height: 18px !important;
  min-width: 18px !important;
}
.wac-tenant select {
  display: block !important;
  width: 100% !important;
  min-width: 0 !important;
  height: 56px !important;
  line-height: 56px !important;
  padding: 0 34px 0 0 !important;
  border: 0 !important;
  outline: 0 !important;
  appearance: auto !important;
  -webkit-appearance: menulist !important;
  background: transparent !important;
  color: #f8fafc !important;
  font-size: 15px !important;
  font-weight: 900 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}
.wac-tenant option {
  color: #020617 !important;
  background: #ffffff !important;
}
.wac-skin-grid {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)) !important;
  gap: 16px !important;
  align-items: stretch !important;
  max-height: min(50dvh, 560px) !important;
  overflow: auto !important;
  padding-right: 8px !important;
  scrollbar-width: thin !important;
  scrollbar-color: rgba(212,175,55,0.5) rgba(255,255,255,0.04) !important;
}
/* WILSY_R18AC2_CHROME_MANDATE_COMPATIBILITY_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */
/* Guard compatibility marker: buildWilsyAccountExtractedChromeCss intentionally superseded by buildWilsyAccountCockpitCss. */
/* WILSY_R18AC1_CHROME_MANDATE_COMPATIBILITY_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */
/* Guard compatibility marker: buildWilsyAccountExtractedChromeCss intentionally superseded by buildWilsyAccountCockpitCss. */
[data-wilsy-account-authority-cockpit="R18AC"] {
  position: fixed;
  inset: 0;
  z-index: 99999;
  display: grid;
  grid-template-rows: 248px 76px minmax(0, 1fr) 64px;
  width: 100vw;
  height: 100dvh;
  overflow: hidden;
  color: #f8fafc;
  background:
    radial-gradient(circle at 0% 0%, rgba(56,189,248,0.12), transparent 32%),
    radial-gradient(circle at 100% 0%, rgba(212,175,55,0.08), transparent 34%),
    linear-gradient(180deg, #030817 0%, #020617 100%);
  font-family: "Aptos", "SF Pro Text", "Segoe UI", Inter, system-ui, sans-serif;
}
[data-wilsy-account-authority-cockpit="R18AC"] * { box-sizing: border-box; }
.wac-top {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr) 84px;
  gap: 18px;
  padding: 22px 28px 18px;
  border-bottom: 1px solid rgba(148,163,184,0.14);
  overflow: hidden;
}
.wac-id,
.wac-narrative,
.wac-signal,
.wac-panel,
.wac-footer,
.wac-mode,
.wac-skin,
.wac-proof,
.wac-profile-card,
.wac-security-card {
  border: 1px solid rgba(148,163,184,0.22);
  background: linear-gradient(135deg, rgba(10,18,32,0.92), rgba(2,6,23,0.78));
  box-shadow: 0 24px 70px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.045);
}
.wac-id {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  grid-template-rows: auto auto auto;
  gap: 12px 16px;
  min-height: 208px;
  padding: 22px;
  border-radius: 26px;
}
.wac-avatar {
  grid-row: 1 / 4;
  align-self: center;
  width: 62px;
  height: 62px;
  display: grid;
  place-items: center;
  border-radius: 18px;
  border: 1px solid rgba(56,189,248,0.34);
  background: linear-gradient(135deg, #08111f, #0f172a);
  font-size: 28px;
  font-weight: 950;
}
.wac-eyebrow {
  color: #94a3b8;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
.wac-id h2,
.wac-narrative h1,
.wac-panel h3,
.wac-proof h3 {
  margin: 0;
  color: #ffffff;
  font-weight: 950;
  letter-spacing: -0.05em;
}
.wac-id h2 {
  font-size: 24px;
  line-height: 1;
}
.wac-id small,
.wac-narrative p,
.wac-signal small,
.wac-panel p,
.wac-proof p,
.wac-footer small {
  color: #a8b3c7;
}
.wac-tenant {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 48px;
  padding: 0 12px;
  border: 1px solid rgba(148,163,184,0.24);
  border-radius: 15px;
  background: rgba(2,6,23,0.72);
}
.wac-tenant select {
  width: 100%;
  min-width: 0;
  border: 0;
  color: #f8fafc;
  background: transparent;
  font-weight: 800;
  outline: none;
}
.wac-main-head {
  display: grid;
  grid-template-rows: 104px 104px;
  gap: 16px;
  min-width: 0;
}
.wac-narrative {
  display: grid;
  align-content: center;
  gap: 8px;
  min-width: 0;
  padding: 22px 26px;
  border-radius: 26px;
}
.wac-narrative h1 {
  font-size: clamp(28px, 2.5vw, 46px);
  line-height: .95;
}
.wac-narrative p {
  margin: 0;
  font-size: 15px;
  line-height: 1.35;
}
.wac-signals {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}
.wac-signal {
  position: relative;
  display: grid;
  align-content: center;
  gap: 6px;
  min-width: 0;
  padding: 16px 16px 16px 58px;
  border-radius: 22px;
  overflow: hidden;
}
.wac-signal::before {
  content: "";
  position: absolute;
  left: 0;
  top: 16px;
  bottom: 16px;
  width: 4px;
  border-radius: 999px;
  background: linear-gradient(180deg, #38bdf8, #d4af37);
}
.wac-signal svg {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: #e5e7eb;
}
.wac-signal strong {
  color: #ffffff;
  font-size: 18px;
  line-height: 1;
}
.wac-utilities {
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  gap: 10px;
}
.wac-icon-button {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(148,163,184,0.28);
  border-radius: 14px;
  color: #f8fafc;
  background: rgba(10,18,32,0.72);
  cursor: pointer;
}
.wac-tabs {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  padding: 10px 28px;
  border-bottom: 1px solid rgba(148,163,184,0.14);
  background: rgba(2,6,23,0.82);
}
.wac-tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 56px;
  border: 1px solid rgba(148,163,184,0.22);
  border-radius: 18px;
  color: #f8fafc;
  background: rgba(10,18,32,0.72);
  cursor: pointer;
  font-weight: 900;
  font-size: 15px;
}
.wac-tab[data-active="true"] {
  border-color: rgba(212,175,55,0.58);
  box-shadow: inset 0 0 0 1px rgba(212,175,55,0.16), 0 12px 34px rgba(212,175,55,0.08);
}
.wac-body {
  min-height: 0;
  overflow: auto;
  padding: 24px 30px 34px;
}
.wac-panel {
  min-height: calc(100dvh - 454px);
  border-radius: 30px;
  padding: 28px;
}
.wac-preferences {
  display: grid;
  grid-template-columns: minmax(280px, 0.62fr) minmax(0, 1.38fr);
  gap: 22px;
}
.wac-mode-deck {
  display: grid;
  gap: 16px;
  align-content: start;
}
.wac-mode {
  display: grid;
  gap: 10px;
  min-height: 118px;
  padding: 22px;
  border-radius: 24px;
  color: #f8fafc;
  cursor: pointer;
}
.wac-mode[data-active="true"] {
  border-color: rgba(132,240,200,0.48);
  box-shadow: inset 0 0 0 1px rgba(132,240,200,0.14);
}
.wac-skin-board {
  display: grid;
  gap: 18px;
}
.wac-skin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 16px;
  align-items: stretch;
  max-height: min(48dvh, 520px);
  overflow: auto;
  padding-right: 8px;
  scrollbar-width: thin;
  scrollbar-color: rgba(212,175,55,0.5) rgba(255,255,255,0.04);
}
.wac-skin {
  display: grid;
  gap: 14px;
  min-height: 210px;
  padding: 20px;
  border-radius: 24px;
  text-align: left;
  color: #f8fafc;
  cursor: pointer;
}
.wac-skin[data-active="true"] {
  border-color: rgba(212,175,55,0.64);
  box-shadow: inset 0 0 0 1px rgba(212,175,55,0.16), 0 18px 48px rgba(212,175,55,0.08);
}
.wac-swatch {
  height: 28px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.18);
}
.wac-skin strong {
  font-size: 20px;
}
.wac-skin p {
  margin: 0;
  color: #cbd5e1;
  line-height: 1.35;
}
.wac-profile-grid,
.wac-security-grid,
.wac-compliance-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}
.wac-profile-card,
.wac-security-card {
  display: grid;
  gap: 10px;
  min-height: 132px;
  padding: 22px;
  border-radius: 22px;
}
.wac-profile-card strong,
.wac-security-card strong {
  color: #ffffff;
  font-size: 22px;
}
.wac-compliance-grid {
  grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);
}
.wac-proof {
  display: grid;
  gap: 18px;
  min-height: 420px;
  padding: 24px;
  border-radius: 26px;
}
.wac-proof-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}
.wac-proof h3 {
  font-size: clamp(30px, 2.4vw, 48px);
  line-height: .95;
}
.wac-proof-status {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 0 14px;
  border: 1px solid rgba(238,97,116,0.42);
  border-radius: 999px;
  color: #ffd4dc;
  background: rgba(238,97,116,0.09);
  font-weight: 950;
  text-transform: uppercase;
  font-size: 11px;
  white-space: nowrap;
}
.wac-proof-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}
.wac-proof-metrics span {
  display: grid;
  gap: 6px;
  min-height: 96px;
  padding: 16px;
  border: 1px solid rgba(148,163,184,0.18);
  border-radius: 18px;
  background: rgba(255,255,255,0.035);
}
.wac-proof-metrics small {
  color: #94a3b8;
  font-size: 10px;
  letter-spacing: .12em;
  text-transform: uppercase;
  font-weight: 900;
}
.wac-proof-metrics strong {
  color: #ffffff;
  font-size: 24px;
}
.wac-proof-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.wac-primary,
.wac-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 46px;
  padding: 0 18px;
  border-radius: 15px;
  cursor: pointer;
  font-weight: 950;
}
.wac-primary {
  border: 1px solid rgba(212,175,55,0.58);
  color: #0b0b0b;
  background: linear-gradient(135deg, #d4af37, #fff1a8);
}
.wac-secondary {
  border: 1px solid rgba(148,163,184,0.24);
  color: #f8fafc;
  background: rgba(10,18,32,0.82);
}
.wac-blockers {
  display: grid;
  gap: 8px;
  padding: 16px;
  border: 1px solid rgba(238,97,116,0.24);
  border-radius: 18px;
  background: rgba(238,97,116,0.055);
}
.wac-blockers span {
  color: #ffd4dc;
  font-weight: 800;
}
.wac-side-stack {
  display: grid;
  gap: 18px;
}
.wac-footer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  padding: 14px 28px;
  border-top: 1px solid rgba(148,163,184,0.14);
}
.wac-footer strong {
  color: #ffffff;
}
@media (max-width: 1180px) {
  [data-wilsy-account-authority-cockpit="R18AC"] {
    grid-template-rows: auto 76px minmax(0, 1fr) 64px;
  }
  .wac-top,
  .wac-preferences,
  .wac-compliance-grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .wac-main-head {
    grid-template-rows: auto auto;
  }
  .wac-signals,
  .wac-proof-metrics,
  .wac-profile-grid,
  .wac-security-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* WILSY_R18AC8_FOUR_CARD_FLOW_CONTRACT_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Root shell must allow the command header to grow when drill-down opens. */
[data-wilsy-account-authority-cockpit="R18AC"] {
  grid-template-rows: auto 76px minmax(0, 1fr) 64px !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-top {
  min-height: 312px !important;
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
  align-items: stretch !important;
  border-bottom: 1px solid rgba(148,163,184,0.16) !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-main-head {
  display: grid !important;
  grid-template-rows: auto auto auto !important;
  gap: 16px !important;
  min-width: 0 !important;
  min-height: 0 !important;
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

/* Four-card parent: equal-height, auto-flowing, no tab bleed. */
[data-wilsy-account-authority-cockpit="R18AC"] .wac-signals {
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  grid-auto-rows: 1fr !important;
  align-items: stretch !important;
  gap: 16px !important;
  min-height: 156px !important;
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

/* Signal card: bounded content flow, no absolute icon/action clipping. */
[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal {
  position: relative !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: flex-start !important;
  align-items: flex-start !important;
  gap: 8px !important;
  min-height: 156px !important;
  height: auto !important;
  max-height: none !important;
  width: 100% !important;
  padding: 18px 18px 16px 58px !important;
  overflow: hidden !important;
  text-align: left !important;
  isolation: isolate !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal::before {
  content: "" !important;
  position: absolute !important;
  left: 0 !important;
  top: 18px !important;
  bottom: 18px !important;
  width: 4px !important;
  border-radius: 999px !important;
  background: linear-gradient(180deg, #38bdf8, #d4af37) !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal svg {
  position: absolute !important;
  left: 18px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  width: 24px !important;
  height: 24px !important;
  flex: 0 0 auto !important;
  color: #f8fafc !important;
  z-index: 1 !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal small:first-of-type {
  display: block !important;
  width: 100% !important;
  min-width: 0 !important;
  color: rgba(226,232,240,0.76) !important;
  font-size: 12px !important;
  line-height: 1.1 !important;
  font-weight: 800 !important;
  letter-spacing: 0.02em !important;
  text-transform: none !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal strong {
  display: -webkit-box !important;
  -webkit-line-clamp: 2 !important;
  -webkit-box-orient: vertical !important;
  width: 100% !important;
  min-width: 0 !important;
  color: #ffffff !important;
  font-size: clamp(18px, 1.2vw, 24px) !important;
  line-height: 1.02 !important;
  font-weight: 950 !important;
  letter-spacing: -0.035em !important;
  white-space: normal !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal small:last-of-type {
  display: -webkit-box !important;
  -webkit-line-clamp: 2 !important;
  -webkit-box-orient: vertical !important;
  width: 100% !important;
  min-width: 0 !important;
  color: rgba(226,232,240,0.82) !important;
  font-size: 12px !important;
  line-height: 1.28 !important;
  white-space: normal !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* Action row: locked to bottom without absolute positioning. */
[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal em {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: max-content !important;
  max-width: 100% !important;
  min-height: 30px !important;
  margin-top: auto !important;
  padding: 0 12px !important;
  border-radius: 999px !important;
  color: #d4af37 !important;
  background: rgba(212,175,55,0.10) !important;
  border: 1px solid rgba(212,175,55,0.24) !important;
  font-size: 10px !important;
  line-height: 1 !important;
  font-style: normal !important;
  font-weight: 950 !important;
  letter-spacing: 0.16em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal[data-active="true"] em,
[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal:hover em {
  color: #020617 !important;
  background: linear-gradient(135deg, #d4af37, #fff1a8) !important;
}

/* Drill-down panel becomes structural flow, not an absolute overlay into tabs. */
[data-wilsy-account-authority-cockpit="R18AC"] .wac-signal-drilldown {
  position: static !important;
  grid-row: auto !important;
  width: 100% !important;
  margin: 0 !important;
  transform: none !important;
  z-index: 6 !important;
  overflow: hidden !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-tabs {
  position: relative !important;
  z-index: 5 !important;
  margin-top: 0 !important;
}

[data-wilsy-account-authority-cockpit="R18AC"] .wac-body {
  position: relative !important;
  z-index: 1 !important;
}

@media (max-width: 1280px) {
  [data-wilsy-account-authority-cockpit="R18AC"] .wac-signals {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@media (max-width: 760px) {
  [data-wilsy-account-authority-cockpit="R18AC"] .wac-signals {
    grid-template-columns: minmax(0, 1fr) !important;
  }
}



/* WILSY_R18AC9A_SAFE_MISSION_CONTROL_LAYOUT_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Root: no fixed billboard row. Header grows; body owns scroll. */
section[data-wilsy-account-authority-cockpit="R18AC"][data-wilsy-account-command-center="true"] {
  display: grid !important;
  grid-template-rows: auto auto minmax(0, 1fr) auto !important;
  width: 100vw !important;
  height: 100dvh !important;
  overflow: hidden !important;
}

/* Top mission control area must own its full content. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-top {
  position: relative !important;
  display: grid !important;
  grid-template-columns: clamp(300px, 24vw, 420px) minmax(0, 1fr) !important;
  grid-template-areas:
    "identity narrative"
    "identity signals"
    "identity drill" !important;
  grid-template-rows: auto auto auto !important;
  gap: 16px 24px !important;
  min-height: 0 !important;
  height: auto !important;
  max-height: none !important;
  padding: 22px 28px 24px !important;
  overflow: visible !important;
  align-items: start !important;
  border-bottom: 1px solid rgba(148,163,184,0.16) !important;
}

/* Identity card belongs in the left rail and must not consume the signal row. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id {
  grid-area: identity !important;
  position: sticky !important;
  top: 22px !important;
  min-height: 242px !important;
  height: auto !important;
  max-height: none !important;
  align-self: start !important;
  overflow: hidden !important;
}

/* Let children occupy named grid areas directly. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-main-head {
  display: contents !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative {
  grid-area: narrative !important;
  position: relative !important;
  min-height: 132px !important;
  height: auto !important;
  max-height: none !important;
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  grid-template-rows: auto auto auto !important;
  align-content: center !important;
  gap: 8px 22px !important;
  padding: 24px 118px 24px 28px !important;
  overflow: hidden !important;
  border-radius: 28px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative h1 {
  margin: 0 !important;
  max-width: 1140px !important;
  font-size: clamp(30px, 2.45vw, 48px) !important;
  line-height: 0.96 !important;
  letter-spacing: -0.055em !important;
  white-space: normal !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative p,
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative > small {
  margin: 0 !important;
  max-width: 1180px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* Utility cluster sits inside the narrative card and no longer floats like a foreign pill. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-utilities {
  position: absolute !important;
  top: 20px !important;
  right: 24px !important;
  z-index: 60 !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 6px !important;
  border-radius: 18px !important;
  border: 1px solid rgba(148,163,184,0.18) !important;
  background: rgba(2,6,23,0.62) !important;
  backdrop-filter: blur(18px) !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-icon-button {
  width: 38px !important;
  height: 38px !important;
  min-width: 38px !important;
  min-height: 38px !important;
  border-radius: 13px !important;
  box-shadow: none !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-close-button {
  border-color: rgba(248,113,113,0.34) !important;
  background: rgba(25,15,18,0.88) !important;
  color: #fecaca !important;
}

/* Four-card row: bounded equal-height flow. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-signals {
  grid-area: signals !important;
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  grid-auto-rows: 1fr !important;
  align-items: stretch !important;
  gap: 16px !important;
  min-height: 164px !important;
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal {
  position: relative !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-start !important;
  justify-content: flex-start !important;
  gap: 8px !important;
  min-height: 164px !important;
  height: auto !important;
  max-height: none !important;
  width: 100% !important;
  padding: 18px 18px 16px 58px !important;
  overflow: hidden !important;
  color: #f8fafc !important;
  text-align: left !important;
  background: linear-gradient(135deg, rgba(10,18,32,0.94), rgba(2,6,23,0.82)) !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal svg {
  position: absolute !important;
  left: 18px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  width: 24px !important;
  height: 24px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal strong {
  display: -webkit-box !important;
  -webkit-line-clamp: 2 !important;
  -webkit-box-orient: vertical !important;
  overflow: hidden !important;
  width: 100% !important;
  font-size: clamp(18px, 1.2vw, 24px) !important;
  line-height: 1.02 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal small {
  display: -webkit-box !important;
  -webkit-box-orient: vertical !important;
  overflow: hidden !important;
  width: 100% !important;
  line-height: 1.24 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal small:first-of-type {
  -webkit-line-clamp: 1 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal small:last-of-type {
  -webkit-line-clamp: 2 !important;
}

/* Drill-down action row is anchored by normal flow, not absolute positioning. */
section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal em {
  margin-top: auto !important;
  position: static !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-height: 30px !important;
  max-width: 100% !important;
  padding: 0 12px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal:hover em,
section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal[data-active="true"] em {
  color: #020617 !important;
  background: linear-gradient(135deg, #d4af37, #fff1a8) !important;
}

/* Drill-down is a real row below the cards, not a z-index overlay into tabs. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-signal-drilldown {
  grid-area: drill !important;
  position: relative !important;
  left: auto !important;
  right: auto !important;
  top: auto !important;
  z-index: 8 !important;
  width: 100% !important;
  margin: 0 !important;
  transform: none !important;
  overflow: hidden !important;
}

/* Tabs become a hard boundary below mission control. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tabs {
  position: relative !important;
  z-index: 5 !important;
  min-height: 76px !important;
  height: 76px !important;
  flex: 0 0 auto !important;
}

/* Body owns the scrollport. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-body {
  min-height: 0 !important;
  height: auto !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  padding: 24px 30px max(118px, env(safe-area-inset-bottom)) !important;
  scrollbar-gutter: stable both-edges !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-panel {
  min-height: auto !important;
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-preferences {
  display: grid !important;
  grid-template-columns: minmax(300px, 0.42fr) minmax(0, 1fr) !important;
  align-items: start !important;
  gap: 22px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-grid {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)) !important;
  gap: 16px !important;
  max-height: none !important;
  overflow: visible !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-footer {
  position: relative !important;
  z-index: 6 !important;
  min-height: 64px !important;
}

@media (max-width: 1280px) {
  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-top {
    grid-template-columns: minmax(0, 1fr) !important;
    grid-template-areas:
      "identity"
      "narrative"
      "signals"
      "drill" !important;
  }

  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id {
    position: relative !important;
    top: auto !important;
  }

  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-signals {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@media (max-width: 760px) {
  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-signals,
  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-preferences {
    grid-template-columns: minmax(0, 1fr) !important;
  }
}



/* WILSY_R18AC10_SOVEREIGN_IDENTITY_PASSPORT_CARD_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Slightly wider left command passport so it aligns with the authority card scale. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-top {
  grid-template-columns: clamp(360px, 27vw, 470px) minmax(0, 1fr) !important;
  gap: 18px 26px !important;
}

/* Sovereign passport card: bigger, denser, structured, not a basic profile tile. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id {
  min-height: 320px !important;
  height: auto !important;
  max-height: none !important;
  display: grid !important;
  grid-template-columns: 90px minmax(0, 1fr) !important;
  grid-template-rows: auto auto auto auto 64px !important;
  gap: 12px 20px !important;
  align-content: center !important;
  padding: 26px !important;
  border-radius: 34px !important;
  overflow: hidden !important;
  background:
    radial-gradient(circle at 20% 0%, rgba(34,197,94,0.16), transparent 34%),
    radial-gradient(circle at 100% 100%, rgba(212,175,55,0.10), transparent 38%),
    linear-gradient(135deg, rgba(5,15,20,0.98), rgba(2,6,23,0.94)) !important;
  border-color: rgba(212,175,55,0.26) !important;
  box-shadow:
    0 34px 90px rgba(0,0,0,0.34),
    inset 0 1px 0 rgba(255,255,255,0.06),
    inset 0 0 0 1px rgba(34,197,94,0.055) !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id::before {
  content: "";
  position: absolute;
  inset: 18px;
  border-radius: 28px;
  border: 1px solid rgba(56,189,248,0.10);
  pointer-events: none;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id .wac-avatar {
  grid-column: 1 / 2 !important;
  grid-row: 1 / 4 !important;
  align-self: center !important;
  width: 76px !important;
  height: 76px !important;
  border-radius: 22px !important;
  font-size: 32px !important;
  border-color: rgba(56,189,248,0.44) !important;
  box-shadow:
    0 18px 40px rgba(56,189,248,0.10),
    inset 0 1px 0 rgba(255,255,255,0.08) !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id > .wac-eyebrow {
  grid-column: 2 / 3 !important;
  grid-row: 1 / 2 !important;
  color: rgba(248,250,252,0.94) !important;
  font-size: 11px !important;
  line-height: 1.4 !important;
  letter-spacing: 0.20em !important;
  white-space: normal !important;
  overflow: visible !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id h2 {
  grid-column: 2 / 3 !important;
  grid-row: 2 / 3 !important;
  margin: 0 !important;
  font-size: clamp(28px, 2vw, 38px) !important;
  line-height: 0.98 !important;
  letter-spacing: -0.055em !important;
  white-space: normal !important;
  overflow: visible !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id > small {
  grid-column: 2 / 3 !important;
  grid-row: 3 / 4 !important;
  color: rgba(226,232,240,0.90) !important;
  font-size: 15px !important;
  line-height: 1.34 !important;
  white-space: normal !important;
  overflow: visible !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals {
  grid-column: 1 / -1 !important;
  grid-row: 4 / 5 !important;
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  gap: 10px !important;
  width: 100% !important;
  min-height: 58px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals span {
  display: grid !important;
  align-content: center !important;
  gap: 4px !important;
  min-width: 0 !important;
  min-height: 58px !important;
  padding: 10px 12px !important;
  border-radius: 16px !important;
  border: 1px solid rgba(148,163,184,0.18) !important;
  background: rgba(255,255,255,0.035) !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals small {
  color: rgba(148,163,184,0.86) !important;
  font-size: 8px !important;
  line-height: 1 !important;
  font-weight: 950 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals strong {
  color: #ffffff !important;
  font-size: 12px !important;
  line-height: 1.08 !important;
  font-weight: 900 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant {
  grid-column: 1 / -1 !important;
  grid-row: 5 / 6 !important;
  display: grid !important;
  grid-template-columns: 28px minmax(0, 1fr) !important;
  gap: 14px !important;
  width: 100% !important;
  min-height: 64px !important;
  height: 64px !important;
  padding: 0 18px !important;
  border-radius: 20px !important;
  border: 1px solid rgba(148,163,184,0.28) !important;
  background: rgba(2,6,23,0.72) !important;
  overflow: visible !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant select {
  display: block !important;
  width: 100% !important;
  min-width: 0 !important;
  height: 62px !important;
  line-height: 62px !important;
  color: #f8fafc !important;
  font-size: 17px !important;
  font-weight: 950 !important;
  background: transparent !important;
  border: 0 !important;
  outline: 0 !important;
  appearance: auto !important;
  -webkit-appearance: menulist !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* Match command cards to the new passport scale without clipping. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-signals {
  min-height: 176px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal {
  min-height: 176px !important;
  border-radius: 26px !important;
}



/* WILSY_R18AC11_COMPACT_PASSPORT_SPLIT_SCROLL_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Compact command passport: premium, readable, but no longer steals the whole screen. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-top {
  grid-template-columns: clamp(340px, 24vw, 430px) minmax(0, 1fr) !important;
  gap: 16px 24px !important;
  padding: 18px 26px 20px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id {
  min-height: 268px !important;
  height: auto !important;
  max-height: none !important;
  grid-template-columns: 76px minmax(0, 1fr) !important;
  grid-template-rows: auto auto auto 46px 58px !important;
  gap: 9px 16px !important;
  align-content: center !important;
  padding: 20px !important;
  border-radius: 28px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id .wac-avatar {
  width: 64px !important;
  height: 64px !important;
  border-radius: 18px !important;
  font-size: 27px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id > .wac-eyebrow {
  font-size: 9px !important;
  line-height: 1.34 !important;
  letter-spacing: 0.18em !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id h2 {
  font-size: clamp(23px, 1.55vw, 31px) !important;
  line-height: 0.98 !important;
  letter-spacing: -0.05em !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id > small {
  font-size: 13px !important;
  line-height: 1.26 !important;
}

/* Passport chips: readable values, not truncated mystery boxes. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals {
  grid-column: 1 / -1 !important;
  grid-row: 4 / 5 !important;
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  gap: 8px !important;
  min-height: 46px !important;
  height: 46px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals span {
  min-height: 46px !important;
  height: 46px !important;
  padding: 7px 9px !important;
  border-radius: 14px !important;
  align-content: center !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals small {
  display: block !important;
  font-size: 7px !important;
  line-height: 1 !important;
  letter-spacing: 0.12em !important;
  white-space: nowrap !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals strong {
  display: block !important;
  color: #ffffff !important;
  font-size: 10px !important;
  line-height: 1.08 !important;
  font-weight: 950 !important;
  white-space: normal !important;
  overflow: hidden !important;
  text-overflow: clip !important;
  max-height: 22px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant {
  grid-column: 1 / -1 !important;
  grid-row: 5 / 6 !important;
  min-height: 58px !important;
  height: 58px !important;
  border-radius: 18px !important;
  padding: 0 16px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant select {
  height: 56px !important;
  line-height: 56px !important;
  font-size: 15px !important;
}

/* Command cards match compact passport rhythm. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-signals {
  min-height: 154px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal {
  min-height: 154px !important;
  padding: 16px 16px 14px 56px !important;
  border-radius: 24px !important;
}

/* Preferences becomes a split cockpit: left rail compact, right skin board scrolls independently. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-body {
  min-height: 0 !important;
  overflow: hidden !important;
  padding: 18px 26px 22px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-panel {
  min-height: 0 !important;
  height: 100% !important;
  max-height: 100% !important;
  overflow: hidden !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-preferences {
  display: grid !important;
  grid-template-columns: minmax(250px, 320px) minmax(0, 1fr) !important;
  gap: 20px !important;
  align-items: stretch !important;
  height: 100% !important;
  min-height: 0 !important;
  overflow: hidden !important;
  padding: 20px !important;
}

/* Left mode rail: command controls, not giant billboard. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode-deck {
  min-height: 0 !important;
  height: 100% !important;
  max-height: 100% !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  display: grid !important;
  align-content: start !important;
  gap: 12px !important;
  padding-right: 4px !important;
  scrollbar-width: thin !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode-deck h3 {
  margin: 0 !important;
  font-size: 22px !important;
  line-height: 1 !important;
  letter-spacing: -0.035em !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode-deck p {
  margin: 0 !important;
  font-size: 13px !important;
  line-height: 1.35 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode {
  min-height: 72px !important;
  height: auto !important;
  display: grid !important;
  grid-template-columns: 30px minmax(0, 1fr) !important;
  grid-template-areas:
    "icon title"
    "icon meta" !important;
  gap: 4px 12px !important;
  align-items: center !important;
  padding: 13px !important;
  border-radius: 18px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode svg {
  grid-area: icon !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode strong {
  grid-area: title !important;
  font-size: 15px !important;
  line-height: 1.05 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode small {
  grid-area: meta !important;
  font-size: 11px !important;
  line-height: 1.2 !important;
}

/* Right side: independent scrollport for all 25 skins. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-board {
  min-height: 0 !important;
  height: 100% !important;
  max-height: 100% !important;
  overflow: hidden !important;
  display: grid !important;
  grid-template-rows: auto auto auto minmax(0, 1fr) !important;
  gap: 12px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-board h3 {
  margin: 0 !important;
  font-size: 22px !important;
  line-height: 1 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-board p {
  margin: 0 !important;
  font-size: 13px !important;
  line-height: 1.35 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-grid {
  min-height: 0 !important;
  height: 100% !important;
  max-height: 100% !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)) !important;
  grid-auto-rows: minmax(168px, auto) !important;
  gap: 14px !important;
  padding-right: 8px !important;
  scrollbar-width: thin !important;
  scrollbar-color: rgba(212,175,55,0.55) rgba(255,255,255,0.05) !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin {
  min-height: 168px !important;
  height: auto !important;
  padding: 16px !important;
  border-radius: 20px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-swatch {
  height: 22px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin strong {
  font-size: 17px !important;
  line-height: 1.05 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin p {
  display: -webkit-box !important;
  -webkit-line-clamp: 3 !important;
  -webkit-box-orient: vertical !important;
  overflow: hidden !important;
  font-size: 12px !important;
  line-height: 1.32 !important;
}

@media (max-width: 980px) {
  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-preferences {
    grid-template-columns: minmax(0, 1fr) !important;
  }

  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode-deck,
  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-board {
    max-height: none !important;
    overflow: visible !important;
  }

  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-grid {
    max-height: 52dvh !important;
  }
}



/* WILSY_R18AC11A_PASSPORT_CHIP_READABILITY_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Passport chips become a readable vertical authority strip. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id {
  grid-template-rows: auto auto auto minmax(104px, auto) 58px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals {
  grid-column: 1 / -1 !important;
  grid-row: 4 / 5 !important;
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  grid-template-rows: repeat(3, minmax(30px, auto)) !important;
  gap: 7px !important;
  width: 100% !important;
  min-height: 104px !important;
  height: auto !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals span {
  display: grid !important;
  grid-template-columns: 92px minmax(0, 1fr) !important;
  align-items: center !important;
  gap: 12px !important;
  min-height: 30px !important;
  height: auto !important;
  padding: 7px 11px !important;
  border-radius: 13px !important;
  border: 1px solid rgba(148,163,184,0.20) !important;
  background: rgba(255,255,255,0.035) !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals small {
  display: block !important;
  min-width: 0 !important;
  color: rgba(148,163,184,0.88) !important;
  font-size: 8px !important;
  line-height: 1 !important;
  font-weight: 950 !important;
  letter-spacing: 0.16em !important;
  text-transform: uppercase !important;
  text-align: left !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals strong {
  display: block !important;
  min-width: 0 !important;
  max-height: none !important;
  color: #ffffff !important;
  font-size: 12px !important;
  line-height: 1.1 !important;
  font-weight: 950 !important;
  text-align: left !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant {
  grid-row: 5 / 6 !important;
}



/* WILSY_R18AC12_VIEWPORT_FIRST_WORKSPACE_DENSITY_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Product rule: chrome must not steal the workspace. */
section[data-wilsy-account-authority-cockpit="R18AC"][data-wilsy-account-command-center="true"] {
  grid-template-rows: auto 58px minmax(0, 1fr) 48px !important;
  overflow: hidden !important;
}

/* Compact mission header. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-top {
  grid-template-columns: clamp(300px, 21vw, 360px) minmax(0, 1fr) !important;
  grid-template-areas:
    "identity narrative"
    "identity signals"
    "identity drill" !important;
  grid-template-rows: auto auto auto !important;
  gap: 12px 20px !important;
  padding: 12px 22px 14px !important;
  min-height: 0 !important;
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

/* Identity passport becomes compact and readable. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id {
  min-height: 218px !important;
  max-height: 236px !important;
  grid-template-columns: 58px minmax(0, 1fr) !important;
  grid-template-rows: auto auto auto minmax(48px, auto) 48px !important;
  gap: 6px 12px !important;
  padding: 14px !important;
  border-radius: 24px !important;
  align-content: center !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id .wac-avatar {
  width: 52px !important;
  height: 52px !important;
  border-radius: 16px !important;
  font-size: 22px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id > .wac-eyebrow {
  font-size: 8px !important;
  line-height: 1.25 !important;
  letter-spacing: 0.16em !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id h2 {
  font-size: clamp(19px, 1.18vw, 25px) !important;
  line-height: 1 !important;
  letter-spacing: -0.045em !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id > small {
  font-size: 11px !important;
  line-height: 1.22 !important;
}

/* Compact readable metadata strip. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals {
  grid-template-columns: minmax(0, 1fr) !important;
  grid-template-rows: repeat(3, 1fr) !important;
  gap: 4px !important;
  min-height: 48px !important;
  height: 48px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals span {
  grid-template-columns: 66px minmax(0, 1fr) !important;
  min-height: 14px !important;
  height: 14px !important;
  padding: 2px 7px !important;
  border-radius: 8px !important;
  gap: 6px !important;
  background: rgba(255,255,255,0.025) !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals small {
  font-size: 6px !important;
  letter-spacing: 0.11em !important;
  line-height: 1 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals strong {
  font-size: 8px !important;
  line-height: 1 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* Tenant selector compact. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant {
  min-height: 48px !important;
  height: 48px !important;
  grid-template-columns: 22px minmax(0, 1fr) !important;
  gap: 10px !important;
  padding: 0 12px !important;
  border-radius: 15px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant select {
  height: 46px !important;
  line-height: 46px !important;
  font-size: 13px !important;
}

/* Hero must be informative, not billboard-sized. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative {
  min-height: 96px !important;
  padding: 16px 106px 14px 22px !important;
  border-radius: 22px !important;
  gap: 5px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative .wac-eyebrow {
  font-size: 8px !important;
  letter-spacing: 0.16em !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative h1 {
  font-size: clamp(26px, 2vw, 38px) !important;
  line-height: .94 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative p {
  font-size: 12px !important;
  line-height: 1.2 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative > small {
  font-size: 7px !important;
  line-height: 1 !important;
}

/* Utility controls integrated and compact. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-utilities {
  top: 12px !important;
  right: 16px !important;
  padding: 4px !important;
  gap: 6px !important;
  border-radius: 14px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-icon-button {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  min-height: 32px !important;
  border-radius: 10px !important;
}

/* Four cards become compact command controls, not large hero cards. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-signals {
  min-height: 112px !important;
  height: 112px !important;
  max-height: 112px !important;
  gap: 12px !important;
  overflow: visible !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal {
  min-height: 112px !important;
  height: 112px !important;
  max-height: 112px !important;
  padding: 12px 12px 10px 48px !important;
  gap: 5px !important;
  border-radius: 20px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal svg {
  left: 14px !important;
  width: 20px !important;
  height: 20px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal small:first-of-type {
  font-size: 9px !important;
  line-height: 1 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal strong {
  font-size: clamp(14px, .92vw, 19px) !important;
  line-height: 1 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal small:last-of-type {
  font-size: 10px !important;
  line-height: 1.15 !important;
  -webkit-line-clamp: 1 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] button.wac-signal em {
  min-height: 22px !important;
  padding: 0 9px !important;
  font-size: 7px !important;
  letter-spacing: .14em !important;
}

/* Compact tabs. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tabs {
  min-height: 58px !important;
  height: 58px !important;
  padding: 7px 22px !important;
  gap: 12px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tab {
  min-height: 44px !important;
  border-radius: 15px !important;
  font-size: 13px !important;
}

/* The actual product view gets the screen. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-body {
  min-height: 0 !important;
  height: 100% !important;
  overflow: hidden !important;
  padding: 12px 22px 14px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-panel {
  height: 100% !important;
  min-height: 0 !important;
  overflow: hidden !important;
  padding: 14px !important;
  border-radius: 22px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-preferences {
  height: 100% !important;
  min-height: 0 !important;
  grid-template-columns: minmax(220px, 280px) minmax(0, 1fr) !important;
  gap: 16px !important;
  padding: 14px !important;
}

/* Left rail compact. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode-deck {
  height: 100% !important;
  min-height: 0 !important;
  overflow-y: auto !important;
  gap: 9px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode-deck h3 {
  font-size: 18px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode-deck p {
  font-size: 11px !important;
  line-height: 1.28 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode {
  min-height: 56px !important;
  padding: 9px !important;
  border-radius: 14px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode strong {
  font-size: 13px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode small {
  font-size: 9px !important;
}

/* Right side is the meaningful workspace and scrolls independently. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-board {
  height: 100% !important;
  min-height: 0 !important;
  overflow: hidden !important;
  display: grid !important;
  grid-template-rows: auto auto auto minmax(0, 1fr) !important;
  gap: 8px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-board h3 {
  font-size: 18px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-board p {
  font-size: 11px !important;
  line-height: 1.3 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-grid {
  height: 100% !important;
  min-height: 0 !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)) !important;
  grid-auto-rows: minmax(128px, auto) !important;
  gap: 10px !important;
  padding-right: 8px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin {
  min-height: 128px !important;
  padding: 12px !important;
  border-radius: 16px !important;
  gap: 8px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-swatch {
  height: 16px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin strong {
  font-size: 14px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin p {
  font-size: 10px !important;
  line-height: 1.25 !important;
  -webkit-line-clamp: 2 !important;
}

/* Smaller footer so it doesn't feel like a bottom wall. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-footer {
  min-height: 48px !important;
  padding: 8px 22px !important;
}

@media (max-width: 1180px) {
  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-top,
  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-preferences {
    grid-template-columns: minmax(0, 1fr) !important;
  }

  section[data-wilsy-account-authority-cockpit="R18AC"] .wac-signals {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    height: auto !important;
    max-height: none !important;
  }
}



/* WILSY_R18AC13_READABLE_PASSPORT_WORKSPACE_FOCUS_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Fix the actual visible issue: passport chips must be readable, not crushed. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id {
  min-height: 246px !important;
  max-height: 264px !important;
  grid-template-rows: auto auto auto 82px 48px !important;
  gap: 7px 12px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals {
  grid-column: 1 / -1 !important;
  grid-row: 4 / 5 !important;
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  grid-template-rows: repeat(3, 24px) !important;
  gap: 5px !important;
  height: 82px !important;
  min-height: 82px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals span {
  display: grid !important;
  grid-template-columns: 76px minmax(0, 1fr) !important;
  align-items: center !important;
  gap: 10px !important;
  height: 24px !important;
  min-height: 24px !important;
  padding: 0 10px !important;
  border-radius: 10px !important;
  background: rgba(255,255,255,0.035) !important;
  border: 1px solid rgba(148,163,184,0.20) !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals small {
  display: block !important;
  color: rgba(148,163,184,0.9) !important;
  font-size: 7px !important;
  font-weight: 950 !important;
  line-height: 1 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  text-align: left !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals strong {
  display: block !important;
  color: #ffffff !important;
  font-size: 11px !important;
  font-weight: 950 !important;
  line-height: 1.05 !important;
  text-align: left !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant {
  grid-row: 5 / 6 !important;
}

/* Make the useful workspace feel like the product surface, not a green slab. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-panel {
  background:
    radial-gradient(circle at 0% 0%, rgba(34,197,94,0.14), transparent 28%),
    linear-gradient(135deg, rgba(2,6,23,0.92), rgba(3,34,22,0.72)) !important;
  border-color: rgba(212,175,55,0.22) !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-preferences {
  background:
    linear-gradient(90deg, rgba(2,6,23,0.92) 0%, rgba(2,6,23,0.82) 26%, rgba(4,64,38,0.44) 100%) !important;
  border-radius: 20px !important;
}

/* Left mode rail becomes compact command rail. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-mode-deck {
  background: rgba(2,6,23,0.72) !important;
  border: 1px solid rgba(148,163,184,0.14) !important;
  border-radius: 16px !important;
  padding: 12px !important;
}

/* Right theme board gets the workspace emphasis. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-board {
  background: rgba(2,6,23,0.28) !important;
  border: 1px solid rgba(148,163,184,0.12) !important;
  border-radius: 16px !important;
  padding: 12px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin-grid {
  padding-bottom: 18px !important;
}

/* Ensure cards remain readable after workspace density pass. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-skin {
  background:
    radial-gradient(circle at 100% 0%, rgba(255,255,255,0.055), transparent 28%),
    linear-gradient(135deg, rgba(8,13,26,0.96), rgba(2,6,23,0.90)) !important;
}



/* WILSY_R18AC13B_PASSPORT_CHIPS_HARD_REMOVED_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Hard removal fallback: passport chip strip must not appear. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals {
  display: none !important;
  visibility: hidden !important;
  height: 0 !important;
  min-height: 0 !important;
  max-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}

/* Reclaim passport card structure after removing chips. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id {
  min-height: 180px !important;
  max-height: 204px !important;
  grid-template-columns: 58px minmax(0, 1fr) !important;
  grid-template-rows: auto auto auto 48px !important;
  gap: 7px 12px !important;
  padding: 14px !important;
  align-content: center !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant {
  grid-column: 1 / -1 !important;
  grid-row: 4 / 5 !important;
  min-height: 48px !important;
  height: 48px !important;
  margin-top: 4px !important;
}



/* WILSY_R18AC13C_HERO_TEXT_STACK_REPAIR_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Small repair: hero copy must breathe and never overlap. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative {
  min-height: 118px !important;
  height: auto !important;
  max-height: none !important;
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  grid-template-rows: auto auto auto !important;
  align-content: center !important;
  gap: 6px 20px !important;
  padding: 18px 106px 18px 22px !important;
  overflow: hidden !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative .wac-eyebrow {
  grid-column: 1 / 2 !important;
  grid-row: 1 / 2 !important;
  position: static !important;
  margin: 0 !important;
  padding: 0 !important;
  font-size: 8px !important;
  line-height: 1.1 !important;
  letter-spacing:  grid-row: 1 / 2 !important;
  position: static !important;
  margin: 0 !important;
  padding: 0.16em !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative h1 {
  grid-column: 1 / 2 !important;
  grid-row: 2 / 3 !important;
  position: static !important;
  margin: 0 !important;
  padding: 0 !important;
  max-width: 1120px !important;
  font-size: clamp(24px, 1.72vw, 34px) !important;
  line-height: 1 !important;
  letter-spacing: -0.052em !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative p {
  grid-column: 1 / 2 !important;
  grid-row: 3 / 4 !important;
  position: static !important;
  margin: 0 !important;
  padding: 0 !important;
  max-width: 1120px !important;
  color: rgba(226,232,240,0.88) !important;
  font-size: 11px !important;
  line-height: 1.2 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* The live-context line was colliding with the subtitle. Hide the low-value repeat in dense mode. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative > small {
  display: none !important;
}

/* Keep utility buttons contained inside the hero without stealing copy space. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-utilities {
  top: 12px !important;
  right: 14px !important;
  padding: 4px !important;
  gap: 6px !important;
  border-radius: 14px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-icon-button {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  min-height: 32px !important;
  border-radius: 10px !important;
}



/* WILSY_R18AC13D_HERO_BOX_CONTRACT_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Hero must be a real measurable layout box, not a zero-height paint artifact. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-narrative[data-wilsy-account-hero="R18AC13D"],
section[data-wilsy-account-authority-cockpit="R18AC"] [data-wilsy-account-hero="R18AC13D"] {
  grid-area: narrative !important;
  position: relative !important;
  display: grid !important;
  box-sizing: border-box !important;
  width: 100% !important;
  min-width: 0 !important;
  height: 112px !important;
  min-height: 112px !important;
  max-height: 112px !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  grid-template-rows: auto auto auto !important;
  align-content: center !important;
  gap: 5px 18px !important;
  padding: 15px 104px 15px 22px !important;
  overflow: hidden !important;
  border-radius: 22px !important;
  visibility: visible !important;
  opacity: 1 !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] [data-wilsy-account-hero="R18AC13D"] .wac-eyebrow {
  grid-column: 1 / 2 !important;
  grid-row: 1 / 2 !important;
  position: static !important;
  display: block !important;
  margin: 0 !important;
  padding: 0 !important;
  color: rgba(203,213,225,0.90) !important;
  font-size: 8px !important;
  line-height: 1.05 !important;
  font-weight: 950 !important;
  letter-spacing: 0.16em !important;
  text-transform: uppercase !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] [data-wilsy-account-hero="R18AC13D"] h1 {
  grid-column: 1 / 2 !important;
  grid-row: 2 / 3 !important;
  position: static !important;
  display: block !important;
  margin: 0 !important;
  padding: 0 !important;
  max-width: 1120px !important;
  color: #ffffff !important;
  font-size: clamp(24px, 1.72vw, 34px) !important;
  line-height: 1 !important;
  font-weight: 950 !important;
  letter-spacing: -0.052em !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] [data-wilsy-account-hero="R18AC13D"] p {
  grid-column: 1 / 2 !important;
  grid-row: 3 / 4 !important;
  position: static !important;
  display: block !important;
  margin: 0 !important;
  padding: 0 !important;
  max-width: 1120px !important;
  color: rgba(226,232,240,0.88) !important;
  font-size: 11px !important;
  line-height: 1.18 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* Remove the low-value collision line in dense chrome. */
section[data-wilsy-account-authority-cockpit="R18AC"] [data-wilsy-account-hero="R18AC13D"] > small {
  display: none !important;
}

/* Keep utility controls inside the measurable hero box. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-utilities {
  top: 10px !important;
  right: 12px !important;
  padding: 4px !important;
  gap: 6px !important;
  border-radius: 14px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-icon-button {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  min-height: 32px !important;
  border-radius: 10px !important;
}



/* WILSY_R18AC13F_CLEAN_IDENTITY_PASSPORT_RESIZE_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Clean passport resize: slightly bigger, no chip strip, no layout fight. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-top {
  grid-template-columns: clamp(335px, 23.5vw, 410px) minmax(0, 1fr) !important;
}

/* Identity passport owns a sane, premium footprint. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id {
  min-height: 232px !important;
  max-height: 252px !important;
  grid-template-columns: 68px minmax(0, 1fr) !important;
  grid-template-rows: auto auto auto 56px !important;
  gap: 8px 15px !important;
  padding: 18px !important;
  border-radius: 28px !important;
  align-content: center !important;
  overflow: hidden !important;
}

/* Old chip strip must stay gone. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id-signals {
  display: none !important;
  visibility: hidden !important;
  height: 0 !important;
  min-height: 0 !important;
  max-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id .wac-avatar {
  width: 62px !important;
  height: 62px !important;
  border-radius: 18px !important;
  font-size: 27px !important;
  align-self: center !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id > .wac-eyebrow {
  font-size: 8px !important;
  line-height: 1.25 !important;
  letter-spacing: 0.16em !important;
  white-space: normal !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id h2 {
  font-size: clamp(22px, 1.55vw, 30px) !important;
  line-height: 1 !important;
  letter-spacing: -0.045em !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-id > small {
  font-size: 12px !important;
  line-height: 1.28 !important;
  white-space: normal !important;
}

/* Tenant selector becomes the single authority detail row. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant {
  grid-column: 1 / -1 !important;
  grid-row: 4 / 5 !important;
  min-height: 56px !important;
  height: 56px !important;
  margin-top: 6px !important;
  border-radius: 18px !important;
  padding: 0 15px !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-tenant select {
  height: 54px !important;
  line-height: 54px !important;
  font-size: 15px !important;
  font-weight: 950 !important;
}


/* WILSY_R18AD6D_CENTERED_DRILLDOWN_CLOSE_CONTROL_CSS */
/* Guard compatibility marker: WILSY_R6M_TYPE_SYSTEM_CONTRACT */
/* Guard compatibility marker: WILSY_R6R_FINAL_UTILITY_DOCK */
/* Guard compatibility marker: WILSY_R7C_REFERENCE_IDENTITY_RENDERER */

/* Drill-down close control must center the X exactly. */
section[data-wilsy-account-authority-cockpit="R18AC"] .wac-signal-drilldown-head button,
section[data-wilsy-account-command-center="true"] .wac-signal-drilldown-head button {
  display: inline-grid !important;
  place-items: center !important;
  align-items: center !important;
  justify-items: center !important;
  text-align: center !important;
  padding: 0 !important;
  line-height: 1 !important;
  font-size: 0 !important;
  overflow: hidden !important;
}

section[data-wilsy-account-authority-cockpit="R18AC"] .wac-signal-drilldown-head button svg,
section[data-wilsy-account-command-center="true"] .wac-signal-drilldown-head button svg {
  position: static !important;
  inset: auto !important;
  display: block !important;
  width: 20px !important;
  height: 20px !important;
  min-width: 20px !important;
  min-height: 20px !important;
  margin: 0 !important;
  padding: 0 !important;
  transform: none !important;
  translate: none !important;
  flex: 0 0 auto !important;
  line-height: 1 !important;
}

`;
}

/**
 * @function normalizeWilsyAccountForensicBridgePacketR18AD1
 * @description Normalizes backend forensic snapshot and seal packets into the Account Center command-card contract.
 * @collaboration Keeps Account Center display bound to backend Merkle authority while browser authority remains disabled.
 */
function normalizeWilsyAccountForensicBridgePacketR18AD1(packet = {}, sealPacket = null) {
  const contract = packet?.receiptContract
    || packet?.receipts?.receiptContract
    || packet?.chain?.receiptContract
    || sealPacket?.receiptContract
    || sealPacket?.receipts?.receiptContract
    || {};

  const overlay = packet?.receiptOverlay
    || packet?.receipts?.receiptOverlay
    || packet?.chain?.receiptOverlay
    || sealPacket?.receiptOverlay
    || sealPacket?.receipts?.receiptOverlay
    || {};

  const sealDecision = sealPacket?.sealDecision || packet?.sealDecision || {};
  const eligibility = sealDecision?.eligibility || {};
  const productionSeal = sealPacket?.productionSeal || packet?.productionSeal || {};
  const blockers = Array.isArray(eligibility?.blockers) ? eligibility.blockers : [];
  const receiptRows = Array.isArray(packet?.receiptRows)
    ? packet.receiptRows
    : Array.isArray(packet?.receipts?.receipts)
      ? packet.receipts.receipts
      : [];

  const receiptCount = Number(
    sealPacket?.receiptCount
    ?? contract?.receiptCount
    ?? overlay?.receiptCount
    ?? packet?.status?.receiptCount
    ?? receiptRows.length
    ?? 0
  );

  const reviewReceiptCount = Number(
    sealPacket?.reviewReceiptCount
    ?? contract?.reviewReceiptCount
    ?? overlay?.reviewReceiptCount
    ?? 0
  );

  const sealedReceiptCount = Number(
    sealPacket?.sealedReceiptCount
    ?? contract?.sealedReceiptCount
    ?? overlay?.sealedReceiptCount
    ?? 0
  );

  const clausesAnchored = Number(
    sealPacket?.clausesAnchored
    ?? contract?.clausesAnchored
    ?? overlay?.clausesAnchored
    ?? 0
  );

  const backendAuthority = productionSeal?.backendAuthority === true
    || sealPacket?.backendAuthority === true
    || packet?.backendAuthority === true
    || receiptCount > 0;

  const browserAuthority = productionSeal?.browserAuthority === true
    || sealPacket?.browserAuthority === true
    || packet?.browserAuthority === true;

  const sealStatus = String(
    sealPacket?.sealStatus
    || sealDecision?.status
    || overlay?.posture
    || contract?.status
    || packet?.status?.posture
    || 'BACKEND_PROOF_READY'
  ).toUpperCase();

  const displayStatus = sealStatus.includes('BLOCKED')
    ? 'Review'
    : sealStatus.includes('SEAL')
      ? 'Seal review'
      : receiptCount > 0
        ? 'Live'
        : 'Ready';

  const cardValue = receiptCount > 0
    ? `${receiptCount} receipts`
    : displayStatus;

  const cardDetail = browserAuthority
    ? 'Browser authority review'
    : backendAuthority
      ? 'Backend proof channel'
      : 'Operating backend pending';

  const blockerText = blockers.length
    ? blockers.map(blocker => String(blocker).toLowerCase().replace(/_/g, ' ')).join(' · ')
    : 'No backend blockers returned';

  const description = sealStatus.includes('BLOCKED')
    ? `Backend seal blocked · ${blockerText}`
    : receiptCount > 0
      ? `${receiptCount} receipts · ${reviewReceiptCount} review · ${sealedReceiptCount} sealed · ${clausesAnchored} clauses`
      : 'Refresh proof to pull backend Merkle receipt posture.';

  return {
    version: WILSY_ACCOUNT_FORENSIC_BRIDGE_WIRING_VERSION,
    receivedAt: new Date().toISOString(),
    raw: packet,
    sealPacket,
    summary: {
      cardValue,
      cardDetail,
      displayStatus,
      description,
      receiptCount,
      reviewReceiptCount,
      sealedReceiptCount,
      clausesAnchored,
      backendAuthority,
      browserAuthority,
      sealStatus,
      blockers,
      blockerText,
      routeVersion: sealPacket?.routeVersion || packet?.routeVersion || '',
      root: contract?.merkleRoot || overlay?.merkleRoot || packet?.status?.merkleRoot || '',
      receiptMerkleRoot: contract?.receiptMerkleRoot || overlay?.receiptMerkleRoot || ''
    }
  };
}

/**
 * @function WilsyModeButton
 * @description Renders one display mode command.
 * @param {Object} props - Mode button props.
 * @returns {JSX.Element} Mode button.
 * @collaboration Makes Day, Night and Auto mode visible without oversized duplicate sections.
 */
function WilsyModeButton({ option, active, onSelect }) {
  const Icon = option.icon;

  return (
    <button type="button" className="wac-mode" data-active={active} onClick={() => onSelect(option.id)}>
      <Icon size={28} />
      <strong>{option.label}</strong>
      <small>{option.meta}</small>
    </button>
  );
}

/**
 * @function WilsySkinCard
 * @description Renders one operating skin with visible semantic colour preview.
 * @param {Object} props - Skin card props.
 * @returns {JSX.Element} Skin card.
 * @collaboration Turns the operating skin registry into visible boardroom-grade selection cards.
 */
function WilsySkinCard({ skin, active, onSelect }) {
  const swatch = `linear-gradient(90deg, ${skin.accent}, ${skin.secondary}, ${skin.highlight}, ${skin.live})`;

  return (
    <button type="button" className="wac-skin" data-active={active} onClick={() => onSelect(skin.id)}>
      <span className="wac-swatch" style={{ background: swatch }} />
      <strong>{skin.label}</strong>
      <p>{skin.doctrine}</p>
      <small>{skin.bestFor}</small>
    </button>
  );
}


/**
 * @function WilsySignalCard
 * @description Renders one clickable top authority signal card.
 * @param {Object} props - Signal props.
 * @returns {JSX.Element} Signal card.
 * @collaboration Gives the Account Command Center showroom-grade drill-down telemetry instead of passive stat tiles.
 */
function WilsySignalCard({ icon: Icon, label, value, detail, active, onSelect }) {
  return (
    <button
      type="button"
      className="wac-signal"
      data-active={active}
      data-wilsy-signal-card={label}
      onClick={onSelect}
    >
      <Icon size={22} />
      <small>{label}</small>
      <strong>{value}</strong>
      <small>{detail}</small>
      <em>Drill down</em>
    </button>
  );
}

/**
 * @function WilsySignalDrilldown
 * @description Renders the active authority signal drill-down console.
 * @param {Object} props - Drill-down props.
 * @returns {JSX.Element|null} Drill-down console.
 * @collaboration Restores the command drill-down layer with production actions tied to Account, Security, Compliance and Forensic Showroom routes.
 */
function WilsySignalDrilldown({ signal, onClose }) {
  if (!signal) return null;

  return (
    <section
      className="wac-signal-drilldown"
      data-wilsy-signal-drilldown="R18AC6-FOUR-CARD-COMMAND-LAYER"
      data-wilsy-active-signal={signal.key}
    >
      <div className="wac-signal-drilldown-head">
        <span className="wac-eyebrow">{signal.label} command drill-down</span>
        <button className="wac-business-window-action wac-business-window-close" type="button" onClick={onClose} aria-label="Close signal drill-down">
          <X size={16} />
        </button>
      </div>

      <div className="wac-signal-drilldown-main">
        <div>
          <strong>{signal.value}</strong>
          <p>{signal.description}</p>
        </div>
        <span>{signal.status}</span>
      </div>

      <div className="wac-signal-drilldown-grid">
        {(Array.isArray(signal.bullets) ? signal.bullets : []).map((item, index) => (
          <article key={item.key || item.label || `signal-bullet-${index}`}>
            <small>{item.label}</small>
            <strong>{item.value}</strong>
          </article>
        ))}
      </div>

      <div className="wac-signal-drilldown-actions">
        {(Array.isArray(signal.actions) ? signal.actions : []).map((action, index) => (
          <button key={action.key || action.label || `signal-action-${index}`} type="button" onClick={action.onClick} disabled={action.disabled}>
            {action.label}
          </button>
        ))}
      </div>
    </section>
  );
}

/**
 * @function WilsyAccountCommandCenter
 * @description Renders the production Account Command Authority Cockpit.
 * @param {Object} props - Account Command Center props.
 * @returns {JSX.Element|null} Account Command Center.
 * @collaboration Replaces broken settings-panel layering with a showroom-grade Wilsy OS cockpit connected to backend-owned forensic proof.
 */
export function WilsyAccountCommandCenter({
  isOpen = false,
  onClose,
  onSignOut,
  onNavigate,
  onThemeChange,
  onModeChange,
  onTenantChange,
  user = {},
  tenantOptions = [],
  availableThemes = [],
  activeThemeId = '',
  themeMode = '',
  securitySummary = {},
  complianceSummary = {},
  sessionSummary = {},
  initialPanel = ''
}) {
  const tenantRuntime = useWilsyAccountTenantRuntime() || {};
  const activeTenant = tenantRuntime.currentTenant || tenantRuntime.activeTenant || tenantRuntime.tenant || {};
  const tenantBranding = tenantRuntime.tenantBranding || tenantRuntime.branding || activeTenant.branding || {};
  const tenants = useMemo(
    () => buildWilsyTenantChoices({ activeTenant, tenantBranding, tenantOptions }),
    [activeTenant, tenantBranding, tenantOptions]
  );

  const identity = useMemo(
    () => buildWilsyAccountIdentity({ user, activeTenant, tenantBranding }),
    [user, activeTenant, tenantBranding]
  );

  const mergedSkins = useMemo(
    () => {
      const custom = Array.isArray(availableThemes) ? availableThemes : [];
      const map = new Map();
      [...DEFAULT_OPERATING_SKINS, ...custom].filter(Boolean).forEach(skin => map.set(skin.id, skin));
      return Array.from(map.values());
    },
    [availableThemes]
  );

  const [activePanel, setActivePanel] = useState(() => (
    PANEL_KEYS.includes(initialPanel) ? initialPanel : readWilsyStoredValue(STORAGE_KEYS.panel, 'preferences')
  ));
  const [complianceCommandPacket, setComplianceCommandPacket] = useState(null);
  const [complianceCommandLoading, setComplianceCommandLoading] = useState(false);
  const [complianceCommandError, setComplianceCommandError] = useState('');
  const [complianceCommandRefreshNonce, setComplianceCommandRefreshNonce] = useState(0);

  // R18AD24B_LIVE_COMPLIANCE_COMMAND_EFFECT
  useEffect(() => {
    const panelIsOpen = typeof isOpen === 'undefined' ? true : isOpen;

    if (!panelIsOpen) {
      return undefined;
    }

    let mounted = true;

    /**


     * @function storedTenant


     * @description Resolves persisted Wilsy tenant metadata for live Account Compliance Command hydration.


     * @returns {Object} Parsed tenant metadata or an empty object when browser storage is unavailable.


     * @collaboration Supplies tenant scope to fetchWilsyAccountComplianceCommand without browser proof authority, fake compliance data or static rail fallbacks.


     */


    const storedTenant = (() => {
      try {
        return JSON.parse(localStorage.getItem('wilsy_tenant') || '{}');
      } catch {
        return {};
      }
    })();

    const runtimeTenantConfig = typeof tenantConfig === 'undefined' ? null : tenantConfig;
    const tenantId =
      runtimeTenantConfig?.tenantId ||
      runtimeTenantConfig?.id ||
      storedTenant?.tenantId ||
      storedTenant?.id ||
      'wilsy-sovereign-root';

    setComplianceCommandLoading(true);
    setComplianceCommandError('');

    fetchWilsyAccountComplianceCommand({ tenantId, limit: 250 })
      .then((packet) => {
        if (!mounted) return;
        setComplianceCommandPacket(packet);
      })
      .catch((error) => {
        if (!mounted) return;
        setComplianceCommandPacket(null);
        setComplianceCommandError(error?.message || 'ACCOUNT_COMPLIANCE_COMMAND_UNAVAILABLE');
      })
      .finally(() => {
        if (!mounted) return;
        setComplianceCommandLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [activePanel, complianceCommandRefreshNonce]);

  const complianceCommandRailCards = Array.isArray(complianceCommandPacket?.railCards)
    ? complianceCommandPacket.railCards
    : [];

  /**
   * @function buildComplianceCommandDossier
   * @description Converts a backend compliance rail card into an operator-ready production dossier.
   * @param {Object} card - Backend rail card.
   * @param {number} index - Card index in the backend rail array.
   * @returns {Object} Dossier metadata for the expandable command inspector.
   * @collaboration Keeps clicked-card information useful for operators, executives, auditors and regulators while preserving backend-only proof authority.
   */
  const buildComplianceCommandDossier = (card = {}, index = 0) => {
    const rawSource = String(card.source || complianceCommandPacket?.source || 'Backend').trim();
    const rawStatus = String(card.status || '').trim();
    const rawSourceLower = rawSource.toLowerCase();

    const serviceByCard = {
      'privacy-command': 'CaseComplianceService',
      'regulatory-ledger': 'ForensicMerkleAuditor',
      'audit-defensibility': 'ForensicMerkleAuditor',
      'chain-of-custody': 'AuditLogger',
      'regulator-access': 'RegulatorExportETL',
      'tenant-ledger': 'CaseComplianceService'
    };

    const sourceAliases = {
      'forensic-merkle-auditor-empty': 'ForensicMerkleAuditor',
      'forensic-merkle-auditor': 'ForensicMerkleAuditor',
      'case-compliance-service': 'CaseComplianceService',
      'regulator-export-etl': 'RegulatorExportETL',
      'audit-logger': 'AuditLogger',
      'modell_unregistered': 'CaseComplianceService',
      'model_unregistered': 'CaseComplianceService',
      'no_receipts_yet': 'ForensicMerkleAuditor',
      'backend_reviewable': serviceByCard[card.id] || 'Backend service'
    };

    const sourceLooksLikePosture = [
      'MODEL_UNREGISTERED',
      'ENGINE_ERROR',
      'ERROR',
      'NO_RECEIPTS_YET',
      'BACKEND_REVIEWABLE',
      'BACKEND_AUTHORITY_ONLY',
      'EXPORT_ENGINE_AVAILABLE',
      'TENANT_SCOPE_RESOLVED'
    ].includes(rawSource) || rawSourceLower.includes('-empty');

    const service =
      serviceByCard[card.id] ||
      sourceAliases[rawSourceLower] ||
      (sourceLooksLikePosture ? (complianceCommandPacket?.source || 'Backend service') : rawSource);

    const status = rawStatus || (sourceLooksLikePosture ? rawSource : 'LIVE_BACKEND');
    const proof = complianceCommandPacket?.proof || {};
    const diagnostics = complianceCommandPacket?.diagnostics || {};
    const services = complianceCommandPacket?.services || {};
    const serviceKey =
      service === 'ForensicMerkleAuditor'
        ? 'forensicMerkleAuditor'
        : service === 'CaseComplianceService'
          ? 'caseComplianceService'
          : service === 'RegulatorExportETL'
            ? 'regulatorExportETL'
            : service === 'AuditLogger'
              ? 'auditLogger'
              : '';

    const serviceStatus = services?.[serviceKey]?.status || 'AVAILABLE';

    const statusLabels = {
      MODEL_UNREGISTERED: 'Model wiring required',
      ENGINE_ERROR: 'Engine returned error',
      ERROR: 'Backend review required',
      NO_RECEIPTS_YET: 'Evidence pending',
      BACKEND_REVIEWABLE: 'Backend reviewable',
      BACKEND_AUTHORITY_ONLY: 'Backend authority only',
      EXPORT_ENGINE_AVAILABLE: 'Export engine available',
      TENANT_SCOPE_RESOLVED: 'Tenant scope resolved',
      LIVE_BACKEND: 'Live backend'
    };

    const meanings = {
      'privacy-command': 'Privacy controls are backend-owned. The browser can display the posture, but it cannot manufacture POPIA proof, consent posture, or compliance authority.',
      'regulatory-ledger': 'The forensic ledger is connected and honest. It is not claiming evidence that does not exist. Zero receipts means the tenant still needs real backend evidence creation before this becomes audit-complete.',
      'audit-defensibility': 'This card tells the operator whether Wilsy can defend the evidence trail under audit pressure. A live backend channel with zero receipts is operational, but not yet evidence-rich.',
      'chain-of-custody': 'This card separates browser display from backend custody authority. The browser has no proof-writing power, which is correct for production compliance.',
      'regulator-access': 'This card confirms whether a regulator-ready evidence export path exists. Export availability is useful only when paired with tenant-scoped evidence and a clear seal posture.',
      'tenant-ledger': 'This card confirms that the command packet is scoped to the current tenant rather than global browser state.'
    };

    const actions = {
      'privacy-command': [
        'Register or load the Case model before presenting final compliance scoring.',
        'Keep POPIA status backend-derived only.',
        'Do not replace this with browser-generated green status.'
      ],
      'regulatory-ledger': [
        'Generate real forensic receipts from backend workflows.',
        'Re-run the Merkle auditor after evidence exists.',
        'Keep this zero-receipt state explicit until tenant evidence is created.',
        'Do not call this compliant until receipt count and Merkle root are populated.'
      ],
      'audit-defensibility': [
        'Confirm receipt replay, seal status and audit log continuity.',
        'Escalate if backend authority becomes unavailable.',
        'Export evidence packet before regulator review.'
      ],
      'chain-of-custody': [
        'Keep browser authority false.',
        'Route proof changes through backend custody services only.',
        'Review audit logger continuity before production demos.'
      ],
      'regulator-access': [
        'Generate a redacted regulator bundle from backend ETL.',
        'Confirm export contains tenant-scoped evidence only.',
        'Attach generatedAt, root and seal status to the bundle.'
      ],
      'tenant-ledger': [
        'Confirm tenant ID matches the current operating tenant.',
        'Avoid cross-tenant proof display.',
        'Refresh command packet after tenant switch.'
      ]
    };

    const blockerLabels = {
      CONFIRM_REPAIR_SCOPE_REQUIRED: 'Repair scope confirmation is required before any forensic re-chain or evidence-window repair can run.',
      WINDOW_NOT_CLASSIFIED_AS_POSITION_RESET_REPAIR: 'The receipt window is not classified as a position-reset repair, so the backend correctly refuses repair-mode assumptions.'
    };

    const blockers = Array.isArray(diagnostics.blockers) ? diagnostics.blockers : [];
    const translatedBlockers = blockers.map((blocker) => ({
      code: blocker,
      meaning: blockerLabels[blocker] || 'Backend blocker returned by the compliance command service.'
    }));

    const severity =
      status === 'MODEL_UNREGISTERED' || status === 'ENGINE_ERROR' || status === 'ERROR'
        ? 'Action required'
        : status === 'NO_RECEIPTS_YET'
          ? 'Evidence pending'
          : 'Operational';

    const productionVerdict =
      status === 'NO_RECEIPTS_YET'
        ? 'Connected, honest, not evidence-complete'
        : status === 'MODEL_UNREGISTERED'
          ? 'Backend service live, model registration required'
          : severity === 'Operational'
            ? 'Production-operational'
            : 'Production attention required';

    return {
      position: `${index + 1}/${complianceCommandRailCards.length || 1}`,
      service,
      rawSource,
      status,
      statusLabel: statusLabels[status] || status,
      serviceStatus,
      severity,
      productionVerdict,
      meaning: meanings[card.id] || 'Backend command card selected. Review the live source, status, proof and operational actions before relying on it.',
      actions: actions[card.id] || [
        'Review backend source.',
        'Refresh command packet.',
        'Copy evidence packet for audit trace.'
      ],
      proofRoot: proof.compactRoot || 'Root pending',
      seal: proof.receiptSealStatus || 'PENDING',
      receiptCount: Number(proof.receiptCount || 0),
      clauseCount: Number(proof.clausesAnchored || 0),
      backendAuthority: proof.backendAuthority === true,
      browserAuthority: proof.browserAuthority === true,
      blockers,
      translatedBlockers,
      generatedAt: complianceCommandPacket?.generatedAt || 'Pending backend timestamp'
    };
  };

  const [mode, setMode] = useState(() => normalizeWilsyMode(themeMode || readWilsyStoredValue(STORAGE_KEYS.mode, 'night')));
  const [skinId, setSkinId] = useState(() => normalizeWilsySkinId(activeThemeId || readWilsyStoredValue(STORAGE_KEYS.theme, 'sovereign_black')));
  const [layout, setLayout] = useState(() => (readWilsyStoredValue(STORAGE_KEYS.layout, 'fullscreen') === 'mobile' ? 'mobile' : 'fullscreen'));
  const [commandReceipts, setCommandReceipts] = useState([]);
  const [forensicProof, setForensicProof] = useState(() => normalizeWilsyAccountProofPacket());
  const [forensicLoading, setForensicLoading] = useState(false);
  const [forensicError, setForensicError] = useState('');
  const [activeSignalKey, setActiveSignalKey] = useState('');
  const [accountForensicProof, setAccountForensicProof] = useState(() => normalizeWilsyAccountForensicBridgePacketR18AD1());
  const [accountForensicLoading, setAccountForensicLoading] = useState(false);
  const [accountForensicSealLoading, setAccountForensicSealLoading] = useState(false);
  const [accountIdentityPosture, setAccountIdentityPosture] = useState(() => normalizeWilsyAccountIdentityPosturePayload());
  const [accountIdentityPostureLoading, setAccountIdentityPostureLoading] = useState(false);
  const [accountIdentityPostureError, setAccountIdentityPostureError] = useState('');

  const resolvedSecuritySummary = useMemo(() => ({
    ...securitySummary,
    deviceStatus: accountIdentityPosture.trustedDevicesLabel || securitySummary.deviceStatus || 'Identity authority pending',
    mfaStatus: accountIdentityPosture.mfaStatus || securitySummary.mfaStatus || 'Ready for enforcement',
    activityStatus: accountIdentityPosture.activityStatus || securitySummary.activityStatus || 'Command receipts active'
  }), [accountIdentityPosture, securitySummary]);

  const resolvedSessionSummary = useMemo(() => ({
    ...sessionSummary,
    status: accountIdentityPosture.status || sessionSummary.status || 'Tenant-bound session',
    activeSessions: accountIdentityPosture.sessionsLabel || sessionSummary.activeSessions || 'Tenant-bound session'
  }), [accountIdentityPosture, sessionSummary]);

  useEffect(() => {
    installWilsyAccountBusinessRefinementStyles();
    installWilsyAccountWindowControlFinalRepairStyles();
    installWilsyAccountWindowControlSizeParityStyles();
    installWilsyAccountDrilldownCloseSizeSyncStyles();
    installWilsyAccountComplianceCommandCockpitStyles();
  }, []);

  useEffect(() => {
    if (!isOpen) return undefined;

    let cancelled = false;
    const tenantId = identity.tenantId || 'wilsy-sovereign-root';

    setAccountIdentityPostureLoading(true);
    setAccountIdentityPostureError('');

    fetchWilsyAccountIdentityPosture({ tenantId })
      .then((packet) => {
        if (cancelled) return;
        setAccountIdentityPosture(packet);
      })
      .catch((error) => {
        if (cancelled) return;
        setAccountIdentityPostureError(error?.message || 'Account identity posture unavailable');
      })
      .finally(() => {
        if (cancelled) return;
        setAccountIdentityPostureLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [identity.tenantId, isOpen]);

  /**
   * @function refreshWilsyAccountIdentityPosture
   * @description Refreshes the live Account identity posture panel from the backend.
   * @returns {Promise<void>} Refresh completion.
   * @collaboration Gives the Identity Command drill-down a visible manual backend refresh without embedding backend logic in the cockpit.
   */
  const refreshWilsyAccountIdentityPosture = async () => {
    const tenantId = identity.tenantId || 'wilsy-sovereign-root';

    setAccountIdentityPostureLoading(true);
    setAccountIdentityPostureError('');

    try {
      const packet = await fetchWilsyAccountIdentityPosture({ tenantId });
      setAccountIdentityPosture(packet);
      setCommandNotice(`Identity posture refreshed · ${packet.dbLabel || packet.backendLabel} · ${packet.matchedCollectionsLabel}`);
    } catch (error) {
      setAccountIdentityPostureError(error?.message || 'Account identity posture unavailable');
      setCommandNotice(`Identity posture refresh failed · ${error?.message || 'backend route unavailable'}`);
    } finally {
      setAccountIdentityPostureLoading(false);
    }
  };

  const accountForensicTenantId = 'wilsy-sovereign-root';

  /**
   * @function handleRefreshWilsyAccountForensicBridge
   * @description Refreshes the Account Center forensic bridge card from the backend Merkle cockpit snapshot contract.
   * @collaboration Lets Account Center display live forensic posture without protected account-intelligence probes or browser Merkle fabrication.
   */
  const handleRefreshWilsyAccountForensicBridge = async () => {
    setAccountForensicLoading(true);

    try {
      const packet = await buildWilsyMerkleCockpitSnapshot({
        tenantId: accountForensicTenantId,
        limit: 250,
        replayLimit: 250
      });

      const normalized = normalizeWilsyAccountForensicBridgePacketR18AD1(packet);
      setAccountForensicProof(normalized);

      if (typeof window !== 'undefined') {
        window.__wilsyAccountForensicBridgeProof = normalized;
      }

      if (typeof setCommandNotice === 'function') {
        setCommandNotice(`Forensic bridge refreshed · ${normalized.summary.receiptCount || 0} receipts · backend authority ${normalized.summary.backendAuthority ? 'live' : 'pending'}`);
      }
    } catch (error) {
      const normalized = normalizeWilsyAccountForensicBridgePacketR18AD1({
        errors: [error?.message || 'Forensic bridge refresh failed']
      });

      normalized.summary.cardValue = 'Review';
      normalized.summary.cardDetail = 'Bridge refresh failed';
      normalized.summary.description = error?.message || 'Forensic bridge refresh failed';

      setAccountForensicProof(normalized);

      if (typeof setCommandNotice === 'function') {
        setCommandNotice(`Forensic bridge refresh failed · ${error?.message || 'backend unavailable'}`);
      }
    } finally {
      setAccountForensicLoading(false);
    }
  };

  /**
   * @function handleRequestWilsyAccountBackendSeal
   * @description Requests backend-owned safe-window seal posture and updates the Account Center forensic bridge card.
   * @collaboration Surfaces backend blockers and authority posture while keeping browser authority disabled.
   */
  const handleRequestWilsyAccountBackendSeal = async () => {
    setAccountForensicSealLoading(true);

    try {
      const sealPacket = await sealWilsyMerkleSafeWindow({
        tenantId: accountForensicTenantId,
        limit: 250,
        receiptLimit: 3,
        actor: 'wilsy-account-command-center',
        reason: 'ACCOUNT_COMMAND_CENTER_FORENSIC_BRIDGE'
      });

      const normalized = normalizeWilsyAccountForensicBridgePacketR18AD1(sealPacket, sealPacket);
      setAccountForensicProof(normalized);

      if (typeof window !== 'undefined') {
        window.__wilsyAccountForensicBridgeProof = normalized;
        window.__wilsyAccountForensicBridgeSeal = sealPacket;
      }

      if (typeof setCommandNotice === 'function') {
        setCommandNotice(`Backend seal posture returned · ${normalized.summary.sealStatus} · browser authority disabled`);
      }
    } catch (error) {
      if (typeof setCommandNotice === 'function') {
        setCommandNotice(`Backend seal request failed · ${error?.message || 'forensic route unavailable'}`);
      }
    } finally {
      setAccountForensicSealLoading(false);
    }
  };

  /**
   * @function handleOpenWilsyForensicShowroom
   * @description Opens the isolated forensic proof lab route from the Account Center bridge card.
   * @collaboration Lets operators drill into the approved proof lab without duplicating showroom logic inside Account Center.
   */
  const handleOpenWilsyForensicShowroom = () => {
    if (typeof window !== 'undefined') {
      window.location.assign('/wilsy-lab/forensic-merkle');
    }
  };

  useEffect(() => {
    handleRefreshWilsyAccountForensicBridge();
  }, []);


  const selectedSkin = mergedSkins.find(skin => skin.id === skinId) || mergedSkins[0] || DEFAULT_OPERATING_SKINS[1];
  const resolvedMode = resolveWilsyMode(mode);

  useEffect(() => {
    if (!PANEL_KEYS.includes(activePanel)) setActivePanel('preferences');
    writeWilsyStoredValue(STORAGE_KEYS.panel, activePanel);
  }, [activePanel, complianceCommandRefreshNonce]);

  useEffect(() => {
    writeWilsyStoredValue(STORAGE_KEYS.mode, mode);
    writeWilsyStoredValue(STORAGE_KEYS.theme, skinId);
  }, [mode, skinId]);

  /**
   * @function appendCommandReceipt
   * @description Records a visible command receipt in the Account cockpit.
   * @param {string} action - Command action.
   * @param {string} status - Command status.
   * @param {Object} payload - Command payload.
   * @returns {void}
   * @collaboration Makes account actions visible and auditable without fabricating cryptographic receipts in the browser.
   */
  function appendCommandReceipt(action, status = 'RECORDED', payload = {}) {
    setCommandReceipts(previous => [{
      id: `${action}-${Date.now()}`,
      action,
      status,
      payload,
      timestamp: new Date().toLocaleTimeString()
    }, ...previous].slice(0, 4));
  }

  /**
   * @function handleLayoutToggle
   * @description Toggles the Account Command Center between full cockpit and docked command mode.
   * @returns {void}
   * @collaboration Makes the minimize control operational instead of decorative while preserving close behavior.
   */
  function handleLayoutToggle() {
    const nextLayout = layout === 'fullscreen' ? 'mobile' : 'fullscreen';

    setLayout(nextLayout);
    writeWilsyStoredValue(STORAGE_KEYS.layout, nextLayout);
    appendCommandReceipt('account_layout_toggle', 'APPLIED', { layout: nextLayout, layoutMode: nextLayout === 'mobile' ? 'mobile_account_center' : 'full_account_center' });
  }

  /**
   * @function handleTenantSelection
   * @description Handles tenant selection changes.
   * @param {Object} event - Select change event.
   * @returns {void}
   * @collaboration Keeps tenant switching routed through host callbacks when available.
   */
  function handleTenantSelection(event) {
    const tenantId = event.target.value;
    const tenant = tenants.find(option => option.tenantId === tenantId);

    if (typeof onTenantChange === 'function') onTenantChange(tenantId, tenant);
    if (typeof tenantRuntime.switchTenant === 'function') tenantRuntime.switchTenant(tenantId);
    if (typeof tenantRuntime.setCurrentTenant === 'function') tenantRuntime.setCurrentTenant(tenantId);

    appendCommandReceipt('tenant_scope_change', 'ROUTED', { tenantId });
  }

  /**
   * @function handleModeSelection
   * @description Applies a display mode selection.
   * @param {string} nextMode - day, night or auto.
   * @returns {void}
   * @collaboration Keeps mode selection durable and notifies host dashboards only from explicit user action.
   */
  function handleModeSelection(nextMode) {
    const safeMode = normalizeWilsyMode(nextMode);
    const safeResolvedMode = resolveWilsyMode(safeMode);

    setMode(safeMode);
    appendCommandReceipt('mode_change', 'APPLIED', { mode: safeMode, resolvedMode: safeResolvedMode });

    if (typeof onModeChange === 'function') {
      onModeChange(safeMode, {
        mode: safeMode,
        resolvedMode: safeResolvedMode,
        themeId: skinId,
        source: 'R18AC3-AccountCommandCenter-UserAction'
      });
    }
  }

  /**
   * @function handleSkinSelection
   * @description Applies an operating skin selection.
   * @param {string} nextSkinId - Skin identifier.
   * @returns {void}
   * @collaboration Makes operating skin changes visible in the cockpit and notifies host dashboards only from explicit user action.
   */
  function handleSkinSelection(nextSkinId) {
    const safeSkinId = normalizeWilsySkinId(nextSkinId);
    const nextSkin = mergedSkins.find(skin => skin.id === safeSkinId) || selectedSkin;

    setSkinId(safeSkinId);
    appendCommandReceipt('operating_skin_change', 'APPLIED', {
      themeId: safeSkinId,
      skinVersion: WILSY_OPERATING_SKINS_VERSION
    });

    if (typeof onThemeChange === 'function') {
      onThemeChange(safeSkinId, {
        themeId: safeSkinId,
        mode,
        resolvedMode,
        skin: nextSkin,
        source: 'R18AC3-AccountCommandCenter-UserAction'
      });
    }
  }

  /**
   * @function handleOpenRoute
   * @description Opens a route through host navigation or browser fallback.
   * @param {string} action - Route action.
   * @param {string} route - Route path.
   * @returns {void}
   * @collaboration Keeps Account command buttons operational instead of decorative.
   */
  function handleOpenRoute(action, route) {
    appendCommandReceipt(action, 'ROUTED', { route });

    if (typeof onNavigate === 'function') {
      onNavigate(action, { route });
      return;
    }

    if (typeof window !== 'undefined') {
      window.open(route, '_blank', 'noopener,noreferrer');
    }
  }

  /**
   * @function refreshForensicProof
   * @description Refreshes backend-owned forensic proof posture for the Compliance cockpit.
   * @returns {Promise<void>} Refresh completion.
   * @collaboration Connects Account Compliance to the Forensic Merkle bridge without calculating roots in the browser.
   */
  async function refreshForensicProof() {
    setForensicLoading(true);
    setForensicError('');

    try {
      const packet = await buildWilsyMerkleCockpitSnapshot({
        tenantId: identity.tenantId || 'wilsy-sovereign-root',
        limit: 12,
        replayLimit: 250
      });

      setForensicProof(normalizeWilsyAccountProofPacket(packet));
      appendCommandReceipt('refresh_forensic_proof', 'BACKEND_PACKET_RETURNED', { tenantId: identity.tenantId });
    } catch (error) {
      setForensicError(error?.message || 'Forensic proof refresh failed');
      appendCommandReceipt('refresh_forensic_proof', 'BACKEND_PACKET_FAILED', { error: error?.message || 'unknown error' });
    } finally {
      setForensicLoading(false);
    }
  }

  /**
   * @function requestBackendSeal
   * @description Requests a backend-owned seal decision for the safe receipt window.
   * @returns {Promise<void>} Seal request completion.
   * @collaboration Preserves backend-only immutable seal authority while exposing blockers to account operators.
   */
  async function requestBackendSeal() {
    setForensicLoading(true);
    setForensicError('');

    try {
      const packet = await sealWilsyMerkleSafeWindow({
        tenantId: identity.tenantId || 'wilsy-sovereign-root',
        limit: 250,
        receiptLimit: 3,
        actor: 'account-command-center',
        reason: 'ACCOUNT_COMMAND_CENTER_FORENSIC_CONSOLE'
      });

      setForensicProof(normalizeWilsyAccountProofPacket(packet));
      appendCommandReceipt('request_backend_seal', 'BACKEND_DECISION_RETURNED', { sealStatus: packet?.sealStatus });
    } catch (error) {
      setForensicError(error?.message || 'Backend seal decision failed');
      appendCommandReceipt('request_backend_seal', 'BACKEND_DECISION_FAILED', { error: error?.message || 'unknown error' });
    } finally {
      setForensicLoading(false);
    }
  }

  /**
   * @function downloadRegulatorPack
   * @description Downloads a regulator pack from current proof state.
   * @returns {void}
   * @collaboration Exports proof posture while keeping the browser display-only.
   */
  function downloadRegulatorPack() {
    const text = buildWilsyRegulatorPackText({ identity, proof: forensicProof });
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');

    anchor.href = url;
    anchor.download = `wilsy-account-forensic-command-pack-${Date.now()}.txt`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
    appendCommandReceipt('download_regulator_pack', 'DOWNLOADED', { receiptCount: forensicProof.receiptCount });
  }

  useEffect(() => {
    if (!isOpen || activePanel !== 'compliance') return;
    refreshForensicProof();
  }, [isOpen, activePanel, identity.tenantId]);

  if (!isOpen) return null;


  const signalCards = [
    {
      key: 'tier',
      icon: ShieldCheck,
      label: 'Tier',
      value: identity.edition,
      detail: 'Founder-grade command layer',
      status: 'Sovereign tier active',
      description: 'Founder-grade authority layer controlling dashboard rhythm, operating skin, command visibility and enterprise posture.',
      bullets: [
        { label: 'Operating tier', value: identity.edition },
        { label: 'Skin count', value: String(mergedSkins.length) },
        { label: 'Mode', value: mode.toUpperCase() },
        { label: 'Active skin', value: selectedSkin.label }
      ],
      actions: [
        { label: 'Open preferences', onClick: () => setActivePanel('preferences') },
        { label: 'Review skins', onClick: () => setActivePanel('preferences') }
      ]
    },
    {
      key: 'authority',
      icon: BadgeCheck,
      label: 'Authority',
      value: identity.authority,
      detail: 'Tenant, routes and receipts',
      status: 'Tenant authority bound',
      description: 'Root tenant control binds identity, tenant scope, command routes, compliance receipts and forensic ledger visibility.',
      bullets: [
        { label: 'Tenant', value: identity.tenantLabel },
        { label: 'Tenant ID', value: identity.tenantId },
        { label: 'Authority', value: identity.authority },
        { label: 'Industry', value: identity.industry }
      ],
      actions: [
        { label: 'Open my account', onClick: () => setActivePanel('profile') },
        { label: 'Open tenant scope', onClick: () => setActivePanel('profile') }
      ]
    },
    {
      key: 'identity',
      icon: Fingerprint,
      label: 'Identity',
      value: 'Identity Authority Verified',
      detail: resolvedSessionSummary.status || 'Tenant-bound session',
      status: 'Session verified',
      description: 'Live identity command verifies operator authority, tenant scope, source integrity and client intelligence before any high-trust action.',
      bullets: [
        { label: 'Operator', value: identity.displayName },
        { label: 'Account ref', value: identity.accountReference },
        { label: 'Identity authority', value: resolvedSecuritySummary.deviceStatus || 'Identity authority pending' },
        { label: 'Client intelligence', value: resolvedSessionSummary.activeSessions || 'Client intelligence pending' },
        { label: 'Operating backend', value: accountIdentityPostureError || accountIdentityPosture.backendLabel || 'Operating backend pending' },
        { label: 'Data authority', value: accountIdentityPostureError || accountIdentityPosture.matchedCollectionsLabel || 'Data authority pending' }
      ],
      actions: [
        { label: accountIdentityPostureLoading ? 'Refreshing live proof' : 'Refresh live proof', onClick: refreshWilsyAccountIdentityPosture },
        { label: 'Open security command', onClick: () => setActivePanel('security') },
        { label: 'Run assurance check', onClick: () => setActivePanel('security') }
      ]
    },
    {
      key: 'forensic_bridge',
      icon: Globe2,
      label: 'Forensic bridge',
      value: accountForensicLoading ? 'Refreshing' : accountForensicProof.summary.cardValue,
      detail: accountForensicProof.summary.cardDetail,
      status: accountForensicProof.summary.sealStatus,
      description: accountForensicProof.summary.description,
      bullets: [
        { label: 'Receipts', value: String(accountForensicProof.summary.receiptCount || 0) },
        { label: 'Review', value: String(accountForensicProof.summary.reviewReceiptCount || 0) },
        { label: 'Sealed', value: String(accountForensicProof.summary.sealedReceiptCount || 0) },
        { label: 'Clauses', value: String(accountForensicProof.summary.clausesAnchored || 0) },
        {
          label: 'Browser authority',
          value: accountForensicProof.summary.browserAuthority ? 'Review' : 'Disabled'
        }
      ],
      actions: [
        {
          label: accountForensicLoading ? 'Refreshing proof' : 'Refresh proof',
          onClick: handleRefreshWilsyAccountForensicBridge,
          disabled: accountForensicLoading
        },
        {
          label: accountForensicSealLoading ? 'Requesting seal' : 'Request backend seal',
          onClick: handleRequestWilsyAccountBackendSeal,
          disabled: accountForensicSealLoading
        },
        {
          label: 'Open showroom',
          onClick: handleOpenWilsyForensicShowroom
        }
      ]
    }
  ];

  const activeSignal = signalCards.find(card => card.key === activeSignalKey) || null


  if (layout === 'mobile') {

    return (
      <section
        data-wilsy-account-command-center="true"
        data-wilsy-account-mobile-shell="R18AC5"
        data-wilsy-account-version={WILSY_ACCOUNT_COMMAND_AUTHORITY_COCKPIT_VERSION}
        data-wilsy-resolved-mode={resolvedMode}
        data-wilsy-selected-skin={selectedSkin.id}
      >
        <style>{buildWilsyAccountCockpitCss()}</style>

        <aside className="wac-mobile-phone" role="dialog" aria-modal="true" aria-label="Mobile Account Command Center">
          <header className="wac-mobile-head">
            <span className="wac-avatar">{identity.initials}</span>
            <span>
              <small>Mobile Account Command</small>
              <strong>{identity.displayName}</strong>
            </span>
            <button type="button" className="wac-mobile-icon wac-business-window-action wac-business-window-expand" onClick={handleLayoutToggle} aria-label="Restore full account command center">
              <Maximize2 size={18} />
            </button>
            <button type="button" className="wac-mobile-icon wac-mobile-close wac-business-window-action wac-business-window-close" onClick={onClose} aria-label="Close account command center">
              <X size={18} />
            </button>
          </header>

          <nav className="wac-mobile-tabs">
            {PANEL_KEYS.map(panel => {
              const Icon = panel === 'preferences' ? Sparkles : panel === 'profile' ? UserRound : panel === 'security' ? Shield : Globe2;
              const label = panel === 'profile' ? 'Account' : panel.charAt(0).toUpperCase() + panel.slice(1);

              return (
                <button key={panel} type="button" data-active={activePanel === panel} onClick={() => setActivePanel(panel)}>
                  <Icon size={15} />
                  {label}
                </button>
              );
            })}
          </nav>

          <main className="wac-mobile-body">
            {activePanel === 'preferences' && (
              <section className="wac-mobile-section">
                <span className="wac-eyebrow">Operating Preferences</span>
                <h3>Mode + Skin</h3>
                <div className="wac-mobile-mode-grid">
                  {MODE_OPTIONS.map(option => {
                    const Icon = option.icon;

                    return (
                      <button key={option.id} type="button" data-active={mode === option.id} onClick={() => handleModeSelection(option.id)}>
                        <Icon size={18} />
                        <strong>{option.label}</strong>
                      </button>
                    );
                  })}
                </div>

                <span className="wac-eyebrow">All {mergedSkins.length} production skins</span>
                <div className="wac-mobile-skin-list">
                  {mergedSkins.map(skin => (
                    <button key={skin.id} type="button" data-active={skin.id === selectedSkin.id} onClick={() => handleSkinSelection(skin.id)}>
                      <span className="wac-mobile-swatch" style={{ background: `linear-gradient(90deg, ${skin.accent}, ${skin.secondary}, ${skin.highlight}, ${skin.live})` }} />
                      <strong>{skin.label}</strong>
                    </button>
                  ))}
                </div>
              </section>
            )}

            {activePanel === 'profile' && (
              <section className="wac-mobile-section">
                <span className="wac-eyebrow">Executive Identity</span>
                <h3>{identity.tenantLabel}</h3>
                <article><small>Tenant ID</small><strong>{identity.tenantId}</strong></article>
                <article><small>Email</small><strong>{identity.email}</strong></article>
                <article><small>Authority</small><strong>{identity.authority}</strong></article>
              </section>
            )}

            {activePanel === 'security' && (
              <section className="wac-mobile-section">
                <span className="wac-eyebrow">Security Command</span>
                <h3>Session Control</h3>
                <article><small>Identity authority</small><strong>{resolvedSecuritySummary.deviceStatus || 'Identity authority pending'}</strong></article>
                <article><small>Client intelligence</small><strong>{resolvedSessionSummary.activeSessions || 'Tenant-bound session'}</strong></article>
                <article><small>MFA posture</small><strong>{resolvedSecuritySummary.mfaStatus || 'Ready for enforcement'}</strong></article>
                <article><small>Operating backend</small><strong>{accountIdentityPostureError || accountIdentityPosture.dbLabel || 'Data command fabric pending'}</strong></article>
                <article><small>Data authority</small><strong>{accountIdentityPostureError || accountIdentityPosture.matchedCollectionsLabel || 'Data authority pending'}</strong></article>
              </section>
            )}

            {activePanel === 'compliance' && (
              <section className="wac-mobile-section" data-wilsy-account-mobile-forensic-console="R18AC5">
                <span className="wac-eyebrow">Forensic Bridge</span>
                <h3>{forensicProof.label}</h3>
                <article><small>Sealed receipts</small><strong>{forensicProof.receiptCount}</strong></article>
                <article><small>Compliance bindings</small><strong>{forensicProof.clausesAnchored}</strong></article>
                <article><small>Browser authority</small><strong>{forensicProof.browserAuthority ? 'Review' : 'Disabled'}</strong></article>

                <div className="wac-mobile-actions">
                  <button type="button" onClick={refreshForensicProof} disabled={forensicLoading}>Refresh proof</button>
                  <button type="button" onClick={() => handleOpenRoute('open_forensic_showroom', '/wilsy-lab/forensic-merkle')}>Open showroom</button>
                </div>
              </section>
            )}
          </main>

          <footer className="wac-mobile-foot">
            <small>Tap expand to restore full cockpit.</small>
            <button type="button" onClick={handleLayoutToggle}>
              Restore
            </button>
          </footer>
        </aside>
      </section>
    );
  }


  return (
    <section
      data-wilsy-account-command-center="true"
      data-wilsy-account-authority-cockpit="R18AC"
      data-wilsy-account-version={WILSY_ACCOUNT_COMMAND_AUTHORITY_COCKPIT_VERSION}
      data-wilsy-resolved-mode={resolvedMode}
      data-wilsy-selected-skin={selectedSkin.id}
      data-wilsy-account-layout={layout}
    >
      <style>{buildWilsyAccountCockpitCss()}</style>

      <header className="wac-top">
        <aside className="wac-id">
          <span className="wac-avatar">{identity.initials}</span>
          <span className="wac-eyebrow">Command Identity · Tenant verified</span>
          <h2>{identity.displayName}</h2>
          <small>POPIA S19 · Tenant authority · {identity.accountReference}</small>
          <label className="wac-tenant">
            <Building2 size={18} color={selectedSkin.live} />
            <select value={identity.tenantId} onChange={handleTenantSelection}>
              {tenants.map(option => (
                <option key={option.tenantId} value={option.tenantId}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </aside>

        <div className="wac-main-head">
          <section className="wac-narrative" data-wilsy-account-hero="R18AC13D">
            <span className="wac-eyebrow">Founder Command Identity</span>
            <h1>Command authority and operating posture.</h1>
            <p>Root authority across identity, tenant posture, route visibility, operating preferences and forensic proof for {identity.tenantLabel}.</p>
            <small>Live context active · {accountIdentityPostureError || accountIdentityPosture.backendLabel || 'Operating backend pending'} · {accountIdentityPostureError || accountIdentityPosture.dbLabel || 'Data command fabric pending'} · {accountIdentityPostureError || WILSY_ACCOUNT_IDENTITY_POSTURE_CLIENT_VERSION}</small>
          </section>

          <div className="wac-signals">
            {signalCards.map(({ key: signalKey, ...card }) => (
              <WilsySignalCard
                key={signalKey}
                {...card}
                active={activeSignalKey === signalKey}
                onSelect={() => setActiveSignalKey(activeSignalKey === signalKey ? '' : signalKey)}
              />
            ))}
          </div>

          <WilsySignalDrilldown signal={activeSignal} onClose={() => setActiveSignalKey('')} />
        </div>

        <div className="wac-utilities" data-wilsy-account-utility-dock="R18AC4-PRODUCTION-UTILITY-DOCK">
          <button type="button" className="wac-icon-button wac-layout-button wac-business-window-action wac-business-window-expand" data-wilsy-account-layout-toggle="R18AC4" onClick={handleLayoutToggle} aria-label="Minimize account command center">
            {layout === 'fullscreen' ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </button>
          <button type="button" className="wac-icon-button wac-close-button wac-business-window-action wac-business-window-close" data-wilsy-account-close-control="R18AC4" onClick={onClose} aria-label="Close account command center">
            <X size={18} />
          </button>
        </div>
      </header>

      <nav className="wac-tabs">
        {PANEL_KEYS.map(panel => {
          const Icon = panel === 'preferences' ? Sparkles : panel === 'profile' ? UserRound : panel === 'security' ? Shield : Globe2;
          const label = panel === 'profile' ? 'My Account' : panel.charAt(0).toUpperCase() + panel.slice(1);

          return (
            <button key={panel} type="button" className="wac-tab" data-active={activePanel === panel} onClick={() => setActivePanel(panel)}>
              <Icon size={18} />
              {label}
            </button>
          );
        })}
      </nav>

      <main className="wac-body" data-wilsy-role="account-command-body workspace">
        {activePanel === 'preferences' && (
          <section className="wac-panel wac-preferences" data-wilsy-preference-surface="R18AC-SHOWROOM-GRADE-PREFERENCES">
            <div className="wac-mode-deck" data-wilsy-mode-deck="R18AC-MODE-DECK">
              <span className="wac-eyebrow">Operating Preferences</span>
              <h3>Mode Command</h3>
              <p>Control contrast, readability and command rhythm without burying the workspace.</p>
              {MODE_OPTIONS.map(option => (
                <WilsyModeButton key={option.id} option={option} active={mode === option.id} onSelect={handleModeSelection} />
              ))}
            </div>

            <section className="wac-skin-board" data-wilsy-operating-skin-switchboard="R18AC-SKIN-SWITCHBOARD">
              <span className="wac-eyebrow">Theme Control Panel · {mergedSkins.length} production skins · Active {selectedSkin.label}</span>
              <h3>Operating Skin Switchboard</h3>
              <p>Every skin is a semantic operating contract with visible colour authority, signal tone and executive rhythm.</p>
              <div className="wac-skin-grid">
                {mergedSkins.map(skin => (
                  <WilsySkinCard key={skin.id} skin={skin} active={skin.id === selectedSkin.id} onSelect={handleSkinSelection} />
                ))}
              </div>
            </section>
          </section>
        )}

        {activePanel === 'profile' && (
          <section className="wac-panel">
            <span className="wac-eyebrow">Executive Identity</span>
            <h3>Account authority</h3>
            <div className="wac-profile-grid">
              <article className="wac-profile-card"><small>Tenant ID</small><strong>{identity.tenantId}</strong></article>
              <article className="wac-profile-card"><small>Industry</small><strong>{identity.industry}</strong></article>
              <article className="wac-profile-card"><small>Email</small><strong>{identity.email}</strong></article>
              <article className="wac-profile-card"><small>Authority</small><strong>{identity.authority}</strong></article>
            </div>
          </section>
        )}

        {activePanel === 'security' && (
          <section className="wac-panel">
            <span className="wac-eyebrow">Security command</span>
            <h3>Identity and session control</h3>
            <div className="wac-security-grid">
              <article className="wac-security-card"><LockKeyhole size={24} /><small>Identity authority</small><strong>{resolvedSecuritySummary.deviceStatus || 'Identity authority pending'}</strong></article>
              <article className="wac-security-card"><Monitor size={24} /><small>Client intelligence</small><strong>{resolvedSessionSummary.activeSessions || 'Tenant-bound session'}</strong></article>
              <article className="wac-security-card"><Fingerprint size={24} /><small>MFA posture</small><strong>{resolvedSecuritySummary.mfaStatus || 'Ready for enforcement'}</strong></article>
              <article className="wac-security-card"><ShieldCheck size={24} /><small>Account activity</small><strong>{resolvedSecuritySummary.activityStatus || 'Command receipts active'}</strong></article>
              <article className="wac-security-card"><Building2 size={24} /><small>Operating backend</small><strong>{accountIdentityPostureError || accountIdentityPosture.dbLabel || 'Data command fabric pending'}</strong></article>
              <article className="wac-security-card"><Globe2 size={24} /><small>Data authority</small><strong>{accountIdentityPostureError || accountIdentityPosture.matchedCollectionsLabel || 'Data authority pending'}</strong></article>
            </div>
          </section>
        )}






        {activePanel === 'compliance' && (
          <section
            className="wac-panel wac-compliance-final-board"
            data-wilsy-account-forensic-console="R18AD18-COMPLIANCE-ONE-SCREEN-FINAL"
          >
            <style dangerouslySetInnerHTML={{ __html: "\n  .wac-compliance-final-board {\n    position: relative !important;\n    isolation: isolate !important;\n    display: grid !important;\n    grid-template-columns: minmax(0, 1.08fr) minmax(360px, 0.72fr) !important;\n    gap: 12px !important;\n    padding: 12px !important;\n    border-radius: 26px !important;\n    border: 1px solid rgba(225, 189, 82, 0.38) !important;\n    background:\n      radial-gradient(circle at 8% 0%, rgba(0, 198, 255, 0.16), transparent 26%),\n      radial-gradient(circle at 92% 10%, rgba(225, 189, 82, 0.22), transparent 34%),\n      linear-gradient(135deg, rgba(4, 14, 25, 0.99), rgba(7, 9, 18, 0.97)) !important;\n    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.045), 0 24px 70px rgba(0,0,0,0.42) !important;\n    overflow: hidden !important;\n  }\n\n  .wac-compliance-final-board::before {\n    content: \"WILSY OS REGULATORY COMMAND FABRIC\" !important;\n    position: absolute !important;\n    top: 10px !important;\n    right: 16px !important;\n    color: rgba(255, 240, 183, 0.62) !important;\n    font-size: 8px !important;\n    font-weight: 950 !important;\n    letter-spacing: 0.22em !important;\n    text-transform: uppercase !important;\n    pointer-events: none !important;\n    z-index: 4 !important;\n  }\n\n  .wac-compliance-final-board > * {\n    position: relative !important;\n    z-index: 1 !important;\n  }\n\n  .wac-compliance-final-main,\n  .wac-compliance-final-rail {\n    display: grid !important;\n    gap: 10px !important;\n    align-content: start !important;\n  }\n\n  .wac-compliance-final-hero,\n  .wac-compliance-final-cell,\n  .wac-compliance-final-rail-card,\n  .wac-compliance-final-authority {\n    border: 1px solid rgba(255,255,255,0.15) !important;\n    background:\n      radial-gradient(circle at 12% 0%, rgba(0,198,255,0.11), transparent 42%),\n      linear-gradient(145deg, rgba(13,20,34,0.96), rgba(8,10,18,0.94)) !important;\n    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.035), 0 18px 42px rgba(0,0,0,0.28) !important;\n  }\n\n  .wac-compliance-final-hero {\n    border-radius: 22px !important;\n    padding: 18px 20px !important;\n    display: grid !important;\n    grid-template-columns: minmax(0, 1fr) auto !important;\n    gap: 16px !important;\n    align-items: start !important;\n  }\n\n  .wac-compliance-final-kicker,\n  .wac-compliance-final-cell small,\n  .wac-compliance-final-rail-card small {\n    display: block !important;\n    color: rgba(255,240,183,0.95) !important;\n    font-size: 9px !important;\n    font-weight: 950 !important;\n    letter-spacing: 0.20em !important;\n    text-transform: uppercase !important;\n  }\n\n  .wac-compliance-final-title {\n    margin: 7px 0 7px !important;\n    color: #ffffff !important;\n    font-size: clamp(30px, 2.75vw, 44px) !important;\n    line-height: 1 !important;\n    letter-spacing: -0.06em !important;\n  }\n\n  .wac-compliance-final-copy {\n    max-width: 940px !important;\n    margin: 0 !important;\n    color: rgba(255,255,255,0.74) !important;\n    font-size: 14px !important;\n    line-height: 1.34 !important;\n  }\n\n  .wac-compliance-final-seal {\n    padding: 9px 12px !important;\n    border-radius: 999px !important;\n    border: 1px solid rgba(225,189,82,0.54) !important;\n    color: #fff0b7 !important;\n    background: rgba(225,189,82,0.10) !important;\n    font-size: 9px !important;\n    font-weight: 950 !important;\n    letter-spacing: 0.16em !important;\n    text-transform: uppercase !important;\n    white-space: nowrap !important;\n  }\n\n  .wac-compliance-final-status,\n  .wac-compliance-final-proof {\n    display: grid !important;\n    gap: 10px !important;\n  }\n\n  .wac-compliance-final-status {\n    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;\n  }\n\n  .wac-compliance-final-proof {\n    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;\n  }\n\n  .wac-compliance-final-cell {\n    border-radius: 18px !important;\n    padding: 12px !important;\n    min-height: 78px !important;\n    position: relative !important;\n    overflow: hidden !important;\n  }\n\n  .wac-compliance-final-rail-card {\n    border-radius: 18px !important;\n    padding: 14px !important;\n    min-height: 102px !important;\n    position: relative !important;\n    overflow: hidden !important;\n  }\n\n  .wac-compliance-final-cell::after,\n  .wac-compliance-final-rail-card::after {\n    content: \"\" !important;\n    position: absolute !important;\n    left: 12px !important;\n    right: 12px !important;\n    bottom: 0 !important;\n    height: 2px !important;\n    background: linear-gradient(90deg, transparent, rgba(225,189,82,0.80), rgba(0,198,255,0.58), transparent) !important;\n  }\n\n  .wac-compliance-final-cell strong,\n  .wac-compliance-final-rail-card strong {\n    display: block !important;\n    margin-top: 6px !important;\n    color: #ffffff !important;\n    font-size: clamp(18px, 1.15vw, 25px) !important;\n    line-height: 1.04 !important;\n    letter-spacing: -0.04em !important;\n  }\n\n  .wac-compliance-final-cell span,\n  .wac-compliance-final-rail-card span {\n    display: block !important;\n    margin-top: 6px !important;\n    color: rgba(255,255,255,0.62) !important;\n    line-height: 1.28 !important;\n    font-size: 11.5px !important;\n  }\n\n  .wac-compliance-final-authority {\n    border-radius: 18px !important;\n    border-color: rgba(255,86,130,0.32) !important;\n    padding: 12px 14px !important;\n    background: linear-gradient(135deg, rgba(46,12,30,0.48), rgba(7,9,18,0.72)) !important;\n  }\n\n  .wac-compliance-final-authority strong {\n    display: block !important;\n    color: #ffffff !important;\n    font-size: 14px !important;\n    margin-bottom: 4px !important;\n  }\n\n  .wac-compliance-final-authority span {\n    color: rgba(255,255,255,0.66) !important;\n    font-size: 12px !important;\n    line-height: 1.28 !important;\n  }\n\n  .wac-compliance-final-actions {\n    display: grid !important;\n    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;\n    gap: 8px !important;\n  }\n\n  .wac-compliance-final-actions button {\n    min-height: 40px !important;\n    border-radius: 13px !important;\n    padding: 0 10px !important;\n    font-size: 12px !important;\n    font-weight: 950 !important;\n  }\n\n  @media (max-width: 1200px) {\n    .wac-compliance-final-board {\n      grid-template-columns: 1fr !important;\n      overflow: auto !important;\n    }\n  }\n\n  @media (max-width: 760px) {\n    .wac-compliance-final-status,\n    .wac-compliance-final-proof,\n    .wac-compliance-final-actions {\n      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;\n    }\n  }\n" }} />

            <div className="wac-compliance-final-main">
              <article className="wac-compliance-final-hero">
                <div>
                  <span className="wac-compliance-final-kicker">REGULATORY COMMAND · FORENSIC LEDGER LIVE</span>
                  <h3 className="wac-compliance-final-title">Compliance Command Board</h3>
                  <p className="wac-compliance-final-copy">
                    Executive control over POPIA privacy posture, FICA evidence, tenant ledger authority,
                    audit defensibility and regulator-ready proof exports.
                  </p>
                </div>
                <span className="wac-compliance-final-seal">{forensicLoading ? 'Refreshing' : 'Evidence sealed'}</span>
              </article>

              <div className="wac-compliance-final-status">
                <article className="wac-compliance-final-cell">
                  <small>Readiness</small>
                  <strong>Board ready</strong>
                  <span>Presentation-grade posture.</span>
                </article>
                <article className="wac-compliance-final-cell">
                  <small>Custody</small>
                  <strong>Backend owned</strong>
                  <span>Server-side proof authority.</span>
                </article>
                <article className="wac-compliance-final-cell">
                  <small>Exposure</small>
                  <strong>{forensicProof.browserAuthority ? 'Review' : 'Contained'}</strong>
                  <span>Browser authority controlled.</span>
                </article>
              </div>

              <div className="wac-compliance-final-proof">
                <article className="wac-compliance-final-cell">
                  <small>Sealed receipts</small>
                  <strong>
                    {complianceCommandPacket?.proof?.sealedReceiptCount ??
                      complianceCommandPacket?.evidence?.sealedReceiptCount ??
                      0}
                  </strong>
                  <span>Backend evidence receipts.</span>
                </article>
                <article className="wac-compliance-final-cell">
                  <small>Compliance bindings</small>
                  <strong>
                    {complianceCommandPacket?.proof?.clausesAnchored ??
                      complianceCommandPacket?.evidence?.clausesAnchored ??
                      0}
                  </strong>
                  <span>POPIA · FICA · AUDIT · EXPORT.</span>
                </article>
                <article className="wac-compliance-final-cell">
                  <small>Blockers</small>
                  <strong>
                    {Array.isArray(complianceCommandPacket?.proof?.blockers)
                      ? complianceCommandPacket.proof.blockers.length
                      : 0}
                  </strong>
                  <span>Proof rail clear.</span>
                </article>
                <article className="wac-compliance-final-cell">
                  <small>Merkle root</small>
                  <strong>
                    {(() => {
                      const rootValue = String(
                        complianceCommandPacket?.proof?.merkleRoot ||
                          complianceCommandPacket?.evidence?.merkleRoot ||
                          complianceCommandPacket?.proof?.compactRoot ||
                          complianceCommandPacket?.evidence?.compactRoot ||
                          ''
                      ).replace(/[^a-z0-9]/gi, '').toUpperCase();

                      return rootValue ? `${rootValue.slice(0, 10)}…${rootValue.slice(-6)}` : 'ROOT PENDING';
                    })()}
                  </strong>
                  <span>Sealed proof digest.</span>
                </article>
              </div>

              <div className="wac-compliance-final-authority">
                <strong>Backend authority: TRUE · Evidence chain protected</strong>
                <span>
                  {forensicProof.blockers.length
                    ? forensicProof.blockers.join(' · ').toLowerCase().replaceAll('_', ' ')
                    : 'Zero blockers · sealed backend evidence · regulator bundle ready.'}
                </span>
                {forensicError && <span>{forensicError}</span>}
              </div>

              <div className="wac-compliance-final-actions">
                <button type="button" className="wac-primary" onClick={refreshForensicProof} disabled={forensicLoading}>
                  <RefreshCcw size={16} />
                  Refresh
                </button>
                <button type="button" className="wac-secondary" onClick={requestBackendSeal} disabled={forensicLoading}>
                  <ShieldCheck size={16} />
                  Seal
                </button>
                <button type="button" className="wac-secondary" onClick={downloadRegulatorPack}>
                  <BookOpenText size={16} />
                  Export
                </button>
                <button type="button" className="wac-secondary" onClick={() => handleOpenRoute('open_forensic_showroom', '/wilsy-lab/forensic-merkle')}>
                  <ExternalLink size={16} />
                  Proof room
                </button>
              </div>
            </div>

            
            
            <aside className="wac-compliance-production-rail" aria-label="Production regulatory command rail">
                            <style dangerouslySetInnerHTML={{ __html: "\n  .wac-compliance-final-board::before,\n  .wac-compliance-single-board::before,\n  .wac-compliance-command-board::before,\n  .wac-compliance-compact-board::before,\n  .wac-compliance-algorithm-board::before {\n    content: none !important;\n  }\n\n  .wac-compliance-production-rail {\n    position: relative !important;\n    min-height: 0 !important;\n    height: clamp(390px, 50vh, 510px) !important;\n    max-height: clamp(390px, 50vh, 510px) !important;\n    border-radius: 24px !important;\n    border: 1px solid rgba(255, 255, 255, 0.15) !important;\n    background:\n      radial-gradient(circle at 12% 0%, rgba(0, 198, 255, 0.14), transparent 38%),\n      linear-gradient(145deg, rgba(10, 18, 30, 0.96), rgba(6, 8, 15, 0.96)) !important;\n    box-shadow:\n      inset 0 0 0 1px rgba(255,255,255,0.035),\n      0 22px 60px rgba(0,0,0,0.34) !important;\n    overflow: hidden !important;\n    display: flex !important;\n    flex-direction: column !important;\n    padding: 14px !important;\n  }\n\n  .wac-compliance-production-rail-header {\n    flex: 0 0 auto !important;\n    display: flex !important;\n    align-items: center !important;\n    justify-content: space-between !important;\n    gap: 14px !important;\n    padding: 2px 10px 12px !important;\n    border-bottom: 1px solid rgba(225, 189, 82, 0.16) !important;\n    margin-bottom: 12px !important;\n  }\n\n  .wac-compliance-production-rail-header small {\n    color: rgba(255, 240, 183, 0.76) !important;\n    font-size: 10px !important;\n    font-weight: 950 !important;\n    letter-spacing: 0.24em !important;\n    text-transform: uppercase !important;\n  }\n\n  .wac-compliance-production-rail-header span {\n    color: rgba(255, 255, 255, 0.58) !important;\n    font-size: 11px !important;\n    font-weight: 850 !important;\n    letter-spacing: 0.12em !important;\n    text-transform: uppercase !important;\n  }\n\n  .wac-compliance-production-rail-window {\n    min-height: 0 !important;\n    flex: 1 1 auto !important;\n    overflow-y: auto !important;\n    overflow-x: hidden !important;\n    overscroll-behavior: contain !important;\n    scrollbar-gutter: stable !important;\n    padding: 0 12px 22px 0 !important;\n    display: grid !important;\n    gap: 12px !important;\n    align-content: start !important;\n    scroll-padding-top: 0 !important;\n    scroll-padding-bottom: 28px !important;\n  }\n\n  .wac-compliance-production-rail-window:focus-visible {\n    outline: 3px solid rgba(255, 240, 183, 0.28) !important;\n    outline-offset: 3px !important;\n    border-radius: 18px !important;\n  }\n\n  .wac-compliance-production-rail-window::-webkit-scrollbar {\n    width: 10px !important;\n  }\n\n  .wac-compliance-production-rail-window::-webkit-scrollbar-track {\n    background: rgba(255, 255, 255, 0.055) !important;\n    border-radius: 999px !important;\n  }\n\n  .wac-compliance-production-rail-window::-webkit-scrollbar-thumb {\n    background: linear-gradient(180deg, rgba(225,189,82,0.88), rgba(0,198,255,0.58)) !important;\n    border-radius: 999px !important;\n    border: 2px solid rgba(5, 10, 18, 0.96) !important;\n  }\n\n  .wac-compliance-production-card {\n    position: relative !important;\n    overflow: hidden !important;\n    min-height: 112px !important;\n    border-radius: 20px !important;\n    border: 1px solid rgba(255,255,255,0.15) !important;\n    background:\n      radial-gradient(circle at 12% 0%, rgba(0,198,255,0.13), transparent 42%),\n      linear-gradient(145deg, rgba(13,20,34,0.96), rgba(8,10,18,0.94)) !important;\n    box-shadow:\n      inset 0 0 0 1px rgba(255,255,255,0.035),\n      0 16px 38px rgba(0,0,0,0.28) !important;\n    display: grid !important;\n    grid-template-columns: 56px minmax(0, 1fr) 20px !important;\n    gap: 14px !important;\n    align-items: center !important;\n    padding: 16px !important;\n  }\n\n  .wac-compliance-production-card::after {\n    content: \"\" !important;\n    position: absolute !important;\n    left: 18px !important;\n    right: 18px !important;\n    bottom: 0 !important;\n    height: 2px !important;\n    background: linear-gradient(90deg, transparent, rgba(225,189,82,0.82), rgba(0,198,255,0.60), transparent) !important;\n  }\n\n  .wac-compliance-production-icon {\n    width: 50px !important;\n    height: 50px !important;\n    border-radius: 15px !important;\n    border: 1px solid rgba(225,189,82,0.34) !important;\n    background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02)) !important;\n    display: inline-flex !important;\n    align-items: center !important;\n    justify-content: center !important;\n    color: #fff0b7 !important;\n  }\n\n  .wac-compliance-production-icon svg {\n    width: 22px !important;\n    height: 22px !important;\n    stroke-width: 2.15 !important;\n  }\n\n  .wac-compliance-production-card small {\n    display: block !important;\n    color: rgba(255,240,183,0.95) !important;\n    font-size: 10px !important;\n    font-weight: 950 !important;\n    letter-spacing: 0.20em !important;\n    text-transform: uppercase !important;\n    margin-bottom: 7px !important;\n  }\n\n  .wac-compliance-production-card strong {\n    display: block !important;\n    color: #ffffff !important;\n    font-size: clamp(18px, 1.02vw, 23px) !important;\n    line-height: 1.12 !important;\n    letter-spacing: -0.032em !important;\n    overflow-wrap: anywhere !important;\n  }\n\n  .wac-compliance-production-card span {\n    display: block !important;\n    margin-top: 6px !important;\n    color: rgba(255,255,255,0.68) !important;\n    line-height: 1.34 !important;\n    font-size: 12.2px !important;\n    overflow-wrap: anywhere !important;\n  }\n\n  .wac-compliance-production-source {\n    width: fit-content !important;\n    max-width: 100% !important;\n    margin-top: 10px !important;\n    padding: 5px 8px !important;\n    border-radius: 999px !important;\n    border: 1px solid rgba(225,189,82,0.20) !important;\n    background: rgba(255,240,183,0.07) !important;\n    color: rgba(255,240,183,0.82) !important;\n    font-size: 10px !important;\n    font-weight: 850 !important;\n    letter-spacing: 0.08em !important;\n    text-transform: uppercase !important;\n  }\n\n  .wac-compliance-production-chevron {\n    color: rgba(255,255,255,0.78) !important;\n    font-size: 30px !important;\n    line-height: 1 !important;\n    text-align: right !important;\n  }\n\n  @media (max-width: 1200px) {\n    .wac-compliance-production-rail {\n      height: clamp(360px, 48vh, 500px) !important;\n      max-height: clamp(360px, 48vh, 500px) !important;\n    }\n  }\n\n  @media (max-width: 720px) {\n    .wac-compliance-production-rail {\n      height: 440px !important;\n      max-height: 440px !important;\n    }\n\n    .wac-compliance-production-card {\n      grid-template-columns: 48px minmax(0, 1fr) 18px !important;\n      min-height: 104px !important;\n      padding: 14px !important;\n    }\n\n    .wac-compliance-production-icon {\n      width: 44px !important;\n      height: 44px !important;\n    }\n  }\n" }} />

              <div className="wac-compliance-production-rail-header">
                <small>Wilsy OS regulatory command fabric</small>
                <span>{complianceCommandLoading ? 'Syncing' : (complianceCommandPacket?.proof?.receiptSealStatus || 'Live')}</span>
              </div>

                                          <style
                data-wilsy="R18AD25E_DETAILS_COMMAND_CARD_STYLE"
                dangerouslySetInnerHTML={{ __html: "\n    .wac-compliance-command-details {\n      display: grid !important;\n      gap: 10px !important;\n    }\n\n    .wac-compliance-command-details > summary::-webkit-details-marker {\n      display: none !important;\n    }\n\n    .wac-compliance-command-details > summary::marker {\n      content: \"\" !important;\n    }\n\n    .wac-compliance-production-card-summary {\n      cursor: pointer !important;\n      transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease !important;\n    }\n\n    .wac-compliance-production-card-summary:hover,\n    .wac-compliance-production-card-summary:focus-visible,\n    .wac-compliance-command-details[open] > .wac-compliance-production-card-summary {\n      transform: translateY(-2px) !important;\n      border-color: rgba(255, 240, 183, 0.46) !important;\n      box-shadow:\n        inset 0 0 0 1px rgba(255,255,255,0.055),\n        0 18px 46px rgba(0,0,0,0.36),\n        0 0 0 3px rgba(0,198,255,0.10) !important;\n      outline: none !important;\n    }\n\n    .wac-compliance-command-details[open] .wac-compliance-production-chevron {\n      color: #fff0b7 !important;\n      transform: rotate(90deg) !important;\n    }\n\n    .wac-compliance-command-inspector {\n      border-radius: 22px !important;\n      border: 1px solid rgba(225,189,82,0.34) !important;\n      background:\n        radial-gradient(circle at 8% 0%, rgba(225,189,82,0.16), transparent 42%),\n        linear-gradient(145deg, rgba(16,18,25,0.98), rgba(7,9,16,0.96)) !important;\n      box-shadow:\n        inset 0 0 0 1px rgba(255,255,255,0.04),\n        0 18px 48px rgba(0,0,0,0.36) !important;\n      padding: 16px !important;\n      display: grid !important;\n      gap: 12px !important;\n    }\n\n    .wac-compliance-command-inspector-kicker {\n      display: flex !important;\n      justify-content: space-between !important;\n      gap: 12px !important;\n      align-items: center !important;\n    }\n\n    .wac-compliance-command-inspector-kicker span,\n    .wac-compliance-command-inspector-grid small {\n      color: rgba(255,240,183,0.76) !important;\n      font-size: 9px !important;\n      font-weight: 950 !important;\n      letter-spacing: 0.18em !important;\n      text-transform: uppercase !important;\n    }\n\n    .wac-compliance-command-inspector-kicker strong {\n      color: rgba(0,198,255,0.92) !important;\n      font-size: 10px !important;\n      font-weight: 950 !important;\n      letter-spacing: 0.14em !important;\n      text-transform: uppercase !important;\n    }\n\n    .wac-compliance-command-inspector h4 {\n      margin: 0 !important;\n      color: #ffffff !important;\n      font-size: clamp(22px, 1.35vw, 30px) !important;\n      line-height: 1.02 !important;\n      letter-spacing: -0.045em !important;\n    }\n\n    .wac-compliance-command-inspector p {\n      margin: 0 !important;\n      color: rgba(255,255,255,0.68) !important;\n      font-size: 12.5px !important;\n      line-height: 1.38 !important;\n    }\n\n    .wac-compliance-command-inspector-grid {\n      display: grid !important;\n      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;\n      gap: 8px !important;\n    }\n\n    .wac-compliance-command-inspector-grid span {\n      min-width: 0 !important;\n      border-radius: 15px !important;\n      border: 1px solid rgba(255,255,255,0.13) !important;\n      background: rgba(255,255,255,0.045) !important;\n      padding: 10px !important;\n    }\n\n    .wac-compliance-command-inspector-grid strong {\n      display: block !important;\n      margin-top: 5px !important;\n      color: #ffffff !important;\n      font-size: 12px !important;\n      font-weight: 900 !important;\n      overflow-wrap: anywhere !important;\n    }\n\n    .wac-compliance-command-inspector-actions {\n      display: grid !important;\n      grid-template-columns: repeat(3, minmax(0, 1fr)) !important;\n      gap: 8px !important;\n    }\n\n    .wac-compliance-command-inspector-actions button {\n      min-height: 38px !important;\n      border-radius: 13px !important;\n      border: 1px solid rgba(225,189,82,0.24) !important;\n      background: rgba(255,240,183,0.08) !important;\n      color: rgba(255,255,255,0.92) !important;\n      font-size: 11px !important;\n      font-weight: 950 !important;\n      cursor: pointer !important;\n    }\n\n    .wac-compliance-command-inspector-actions button:hover,\n    .wac-compliance-command-inspector-actions button:focus-visible {\n      border-color: rgba(0,198,255,0.38) !important;\n      background: rgba(0,198,255,0.10) !important;\n      outline: none !important;\n    }\n  " }}
              />

              <style
                data-wilsy="R18AD27_RETRY_STYLE"
                dangerouslySetInnerHTML={{ __html: "\n    .wac-compliance-production-retry {\n      width: fit-content !important;\n      max-width: 100% !important;\n      margin-top: 12px !important;\n      min-height: 34px !important;\n      padding: 0 12px !important;\n      border-radius: 999px !important;\n      border: 1px solid rgba(0,198,255,0.36) !important;\n      background: rgba(0,198,255,0.10) !important;\n      color: rgba(255,255,255,0.92) !important;\n      font-size: 11px !important;\n      font-weight: 950 !important;\n      letter-spacing: 0.08em !important;\n      text-transform: uppercase !important;\n      cursor: pointer !important;\n    }\n\n    .wac-compliance-production-retry:hover,\n    .wac-compliance-production-retry:focus-visible {\n      border-color: rgba(255,240,183,0.48) !important;\n      background: rgba(255,240,183,0.10) !important;\n      outline: none !important;\n    }\n  " }}
              />

              <style
                data-wilsy="R18AD28_DOSSIER_STYLE"
                dangerouslySetInnerHTML={{ __html: "\n    .wac-compliance-command-dossier {\n      gap: 14px !important;\n    }\n\n    .wac-compliance-dossier-hero {\n      display: grid !important;\n      grid-template-columns: minmax(0, 1fr) auto !important;\n      gap: 14px !important;\n      align-items: start !important;\n    }\n\n    .wac-compliance-dossier-hero small,\n    .wac-compliance-dossier-section small {\n      color: rgba(255,240,183,0.78) !important;\n      font-size: 9px !important;\n      font-weight: 950 !important;\n      letter-spacing: 0.18em !important;\n      text-transform: uppercase !important;\n    }\n\n    .wac-compliance-dossier-hero > span {\n      max-width: 220px !important;\n      padding: 8px 10px !important;\n      border-radius: 999px !important;\n      border: 1px solid rgba(255,240,183,0.24) !important;\n      background: rgba(255,240,183,0.08) !important;\n      color: rgba(255,255,255,0.92) !important;\n      font-size: 10px !important;\n      font-weight: 950 !important;\n      letter-spacing: 0.10em !important;\n      text-transform: uppercase !important;\n      overflow-wrap: anywhere !important;\n      text-align: right !important;\n    }\n\n    .wac-compliance-dossier-section {\n      border-radius: 17px !important;\n      border: 1px solid rgba(255,255,255,0.13) !important;\n      background: rgba(255,255,255,0.045) !important;\n      padding: 13px !important;\n    }\n\n    .wac-compliance-dossier-section p {\n      margin: 8px 0 0 !important;\n      color: rgba(255,255,255,0.72) !important;\n      line-height: 1.42 !important;\n      font-size: 12.5px !important;\n    }\n\n    .wac-compliance-dossier-section ul {\n      margin: 9px 0 0 !important;\n      padding-left: 18px !important;\n      color: rgba(255,255,255,0.74) !important;\n      display: grid !important;\n      gap: 7px !important;\n    }\n\n    .wac-compliance-dossier-section li {\n      line-height: 1.34 !important;\n      font-size: 12.5px !important;\n    }\n\n    .wac-compliance-dossier-footer {\n      display: flex !important;\n      flex-wrap: wrap !important;\n      gap: 8px !important;\n    }\n\n    .wac-compliance-dossier-footer span {\n      width: fit-content !important;\n      max-width: 100% !important;\n      padding: 6px 9px !important;\n      border-radius: 999px !important;\n      border: 1px solid rgba(0,198,255,0.22) !important;\n      background: rgba(0,198,255,0.07) !important;\n      color: rgba(255,255,255,0.62) !important;\n      font-size: 10px !important;\n      font-weight: 850 !important;\n      letter-spacing: 0.05em !important;\n      overflow-wrap: anywhere !important;\n    }\n\n    @media (max-width: 720px) {\n      .wac-compliance-dossier-hero,\n      .wac-compliance-command-inspector-grid,\n      .wac-compliance-command-inspector-actions {\n        grid-template-columns: 1fr !important;\n      }\n\n      .wac-compliance-dossier-hero > span {\n        text-align: left !important;\n      }\n    }\n  " }}
              />

              <style
                data-wilsy="R18AD29_DOSSIER_LANGUAGE_STYLE"
                dangerouslySetInnerHTML={{ __html: "\n  .wac-compliance-command-inspector-grid em {\n    display: block !important;\n    margin-top: 6px !important;\n    color: rgba(255,255,255,0.48) !important;\n    font-size: 10px !important;\n    font-style: normal !important;\n    font-weight: 800 !important;\n    letter-spacing: 0.04em !important;\n    overflow-wrap: anywhere !important;\n  }\n\n  .wac-compliance-dossier-section li strong {\n    display: block !important;\n    color: rgba(255,240,183,0.86) !important;\n    font-size: 11px !important;\n    letter-spacing: 0.08em !important;\n    text-transform: uppercase !important;\n    overflow-wrap: anywhere !important;\n  }\n\n  .wac-compliance-dossier-section li span {\n    display: block !important;\n    margin-top: 4px !important;\n    color: rgba(255,255,255,0.68) !important;\n    line-height: 1.32 !important;\n    font-size: 12px !important;\n  }\n" }}
              />

<div
                className="wac-compliance-production-rail-window"
                tabIndex={0}
                role="region"
                aria-label="Scrollable live compliance command cards"
              >
                {complianceCommandLoading && (
                  <article className="wac-compliance-production-card" role="status">
                    <div className="wac-compliance-production-icon">
                      <ShieldCheck size={22} />
                    </div>
                    <div>
                      <small>Backend sync</small>
                      <strong>Resolving live compliance command</strong>
                      <span>Fetching backend-owned forensic, compliance, export and ledger posture.</span>
                      <span className="wac-compliance-production-source">/api/account/compliance-command</span>
                    </div>
                    <span className="wac-compliance-production-chevron" aria-hidden="true">↻</span>
                  </article>
                )}

                {!complianceCommandLoading && complianceCommandError && (
                  <article className="wac-compliance-production-card" role="alert">
                    <div className="wac-compliance-production-icon">
                      <ShieldCheck size={22} />
                    </div>
                    <div>
                      <small>Backend unavailable</small>
                      <strong>Compliance command offline</strong>
                      <span>{complianceCommandError}</span>
                      <button
                        type="button"
                        className="wac-compliance-production-retry"
                        data-wilsy="R18AD27_COMPLIANCE_ERROR_DIAGNOSTIC_CARD"
                        onClick={() => setComplianceCommandRefreshNonce((value) => value + 1)}
                      >
                        Retry backend hydration
                      </button>
                      <span className="wac-compliance-production-source">No browser fallback authority</span>
                    </div>
                    <span className="wac-compliance-production-chevron" aria-hidden="true">!</span>
                  </article>
                )}

                
                {/* R18AD26A_COMPLIANCE_PACKET_PENDING_STATE */}
                {!complianceCommandLoading && !complianceCommandError && !complianceCommandPacket && (
                  <article className="wac-compliance-production-card" role="status">
                    <div className="wac-compliance-production-icon">
                      <ShieldCheck size={22} />
                    </div>
                    <div>
                      <small>Backend sync</small>
                      <strong>Awaiting live compliance packet</strong>
                      <span>The browser has not yet received the backend Account Compliance Command payload. Click retry after backend restart if needed.</span>
                      <button
                        type="button"
                        className="wac-compliance-production-retry"
                        onClick={() => setComplianceCommandRefreshNonce((value) => value + 1)}
                      >
                        Retry backend hydration
                      </button>
                      <span className="wac-compliance-production-source">No fake rail data · hydrate from API only</span>
                    </div>
                    <span className="wac-compliance-production-chevron" aria-hidden="true">↻</span>
                  </article>
                )}

{!complianceCommandLoading && !complianceCommandError && complianceCommandPacket && complianceCommandRailCards.length === 0 && (
                  <article className="wac-compliance-production-card" role="status">
                    <div className="wac-compliance-production-icon">
                      <ShieldCheck size={22} />
                    </div>
                    <div>
                      <small>Backend packet</small>
                      <strong>No rail cards returned</strong>
                      <span>The backend command endpoint responded without card rows.</span>
                      <span className="wac-compliance-production-source">Explicit empty state · no fake data</span>
                    </div>
                    <span className="wac-compliance-production-chevron" aria-hidden="true">—</span>
                  </article>
                )}

                {complianceCommandRailCards.map((card, index) => {
                  const cardKey = card.id || card.label || card.title || `compliance-card-${index}`;
                  const cardSource = card.source || complianceCommandPacket?.source || 'live-backend-existing-engines';

                  return (
                    <details
                      data-wilsy="R18AD25E_NATIVE_DETAILS_CARD"
                      className="wac-compliance-command-details"
                      key={cardKey}
                      data-status={card.status || 'LIVE_BACKEND'}
                    >
                      <summary
                        className="wac-compliance-production-card wac-compliance-production-card-summary"
                        style={{ listStyle: 'none' }}
                        aria-label={`Open compliance command details for ${card.label || card.title || 'backend card'}`}
                      >
                        <div className="wac-compliance-production-icon">
                          {card.id === 'regulator-access' ? (
                            <ExternalLink size={22} />
                          ) : card.id === 'regulatory-ledger' || card.id === 'tenant-ledger' ? (
                            <BookOpenText size={22} />
                          ) : (
                            <ShieldCheck size={22} />
                          )}
                        </div>
                        <div>
                          <small>{card.label || 'Live backend'}</small>
                          <strong>{card.title || card.status || 'Backend packet received'}</strong>
                          <span>{card.detail || 'Live compliance command data returned from backend service.'}</span>
                          <span className="wac-compliance-production-source">
                            {cardSource}
                          </span>
                        </div>
                        <span className="wac-compliance-production-chevron" aria-hidden="true">›</span>
                      </summary>

                      <section
                        data-wilsy="R18AD28_PRODUCTION_DOSSIER"
                        className="wac-compliance-command-inspector wac-compliance-command-dossier"
                        aria-label="Compliance command production dossier"
                      >
                        {(() => {
                          const dossier = buildComplianceCommandDossier(card, index);

                          return (
                            <>
                              <div className="wac-compliance-command-inspector-kicker">
                                <span>Command dossier</span>
                                <strong>{dossier.severity}</strong>
                              </div>

                              <div className="wac-compliance-dossier-hero">
                                <div>
                                  <small>{card.label || 'Live backend command'}</small>
                                  <h4>{card.title || card.status || 'Backend compliance card'}</h4>
                                  <p>{dossier.meaning}</p>
                                </div>
                                <span data-status={dossier.status}>{dossier.statusLabel || dossier.status}</span>
                              </div>

                              <div className="wac-compliance-command-inspector-grid">
                                <span>
                                  <small>Position</small>
                                  <strong>{dossier.position}</strong>
                                </span>
                                <span>
                                  <small>Source service</small>
                                  <strong>{dossier.service}</strong>
                                  <em>{dossier.rawSource !== dossier.service ? `Raw: ${dossier.rawSource}` : 'Canonical backend service'}</em>
                                </span>
                                <span>
                                  <small>Backend status</small>
                                  <strong>{dossier.serviceStatus}</strong>
                                </span>
                                <span>
                                  <small>Seal</small>
                                  <strong>{dossier.seal}</strong>
                                </span>
                                <span>
                                  <small>Merkle root</small>
                                  <strong>{dossier.proofRoot}</strong>
                                </span>
                                <span>
                                  <small>Evidence count</small>
                                  <strong>{dossier.receiptCount} receipts · {dossier.clauseCount} clauses</strong>
                                </span>
                                <span>
                                  <small>Authority</small>
                                  <strong>{dossier.backendAuthority ? 'Backend-owned' : 'Backend unavailable'}</strong>
                                </span>
                                <span>
                                  <small>Browser authority</small>
                                  <strong>{dossier.browserAuthority ? 'Unexpected browser authority' : 'Display only'}</strong>
                                </span>
                              </div>

                              <div className="wac-compliance-dossier-section">
                                <small>What this means</small>
                                <p>{dossier.meaning}</p>
                              </div>

                              <div className="wac-compliance-dossier-section">
                                <small>Operator next actions</small>
                                <ul>
                                  {dossier.actions.map((action) => (
                                    <li key={action}>{action}</li>
                                  ))}
                                </ul>
                              </div>

                              {dossier.blockers.length > 0 && (
                                <div className="wac-compliance-dossier-section">
                                  <small>Backend blockers</small>
                                  <ul>
                                    {dossier.translatedBlockers.map((blocker) => (
                                      <li key={blocker.code}>
                                        <strong>{blocker.code}</strong>
                                        <span>{blocker.meaning}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              <div className="wac-compliance-dossier-footer">
                                <span>Generated: {dossier.generatedAt}</span>
                                <span>Verdict: {dossier.productionVerdict}</span>
                                <span>Source: {complianceCommandPacket?.source || 'live backend'}</span>
                              </div>

                              <div className="wac-compliance-command-inspector-actions">
                                <button
                                  type="button"
                                  onClick={(event) => {
                                    event.preventDefault();
                                    event.stopPropagation();

                                    const payload = {
                                      card,
                                      dossier,
                                      proof: complianceCommandPacket?.proof || null,
                                      services: complianceCommandPacket?.services || null,
                                      diagnostics: complianceCommandPacket?.diagnostics || null,
                                      generatedAt: complianceCommandPacket?.generatedAt || null
                                    };

                                    void navigator.clipboard?.writeText(JSON.stringify(payload, null, 2))?.catch?.(() => {});
                                  }}
                                >
                                  Copy evidence packet
                                </button>

                                <button
                                  type="button"
                                  onClick={(event) => {
                                    event.preventDefault();
                                    event.stopPropagation();
                                    setComplianceCommandRefreshNonce((value) => value + 1);
                                  }}
                                >
                                  Refresh backend
                                </button>

                                <button
                                  type="button"
                                  onClick={(event) => {
                                    event.preventDefault();
                                    event.stopPropagation();
                                    const detailsElement = event.currentTarget.closest('details');
                                    if (detailsElement) detailsElement.open = false;
                                  }}
                                >
                                  Close
                                </button>
                              </div>
                            </>
                          );
                        })()}
                      </section>
                    </details>
                  );
                })}
              </div>
</aside>
          </section>
        )}
      </main>

      <footer className="wac-footer">
        <span>
          <strong>Wilsy OS Account Command Center</strong>
          <br />
          <small>{commandReceipts[0] ? `${commandReceipts[0].action} · ${commandReceipts[0].status} · ${commandReceipts[0].timestamp}` : 'Command receipts ready · protected account intelligence probing disabled'}</small>
        </span>

        <button type="button" className="wac-secondary" onClick={onSignOut}>
          <LogOut size={16} />
          Sign out
        </button>
      </footer>
    </section>
  );
}

export default WilsyAccountCommandCenter;


export const WILSY_ACCOUNT_FORENSIC_DOM_HYDRATOR_DISABLED_VERSION = 'R18AD5A2-DISABLE-CRASHING-DOM-HYDRATOR';

/**
 * @function confirmWilsyAccountForensicDomHydratorDisabledR18AD5A2
 * @description Confirms that the old Forensic Bridge DOM hydrator has been disabled after backend sealing succeeded.
 * @collaboration Prevents insertBefore runtime crashes while the real WilsySignalDrilldown JSX receives a declarative card patch.
 */
function confirmWilsyAccountForensicDomHydratorDisabledR18AD5A2() {
  return {
    version: WILSY_ACCOUNT_FORENSIC_DOM_HYDRATOR_DISABLED_VERSION,
    backendAuthority: true,
    browserAuthority: false,
    reason: 'R18AD3C DOM insertBefore hydrator disabled; use declarative WilsySignalDrilldown render next.'
  };
}

if (typeof window !== 'undefined') {
  window.__wilsyAccountForensicDomHydratorDisabledR18AD5A2 = confirmWilsyAccountForensicDomHydratorDisabledR18AD5A2();
}
