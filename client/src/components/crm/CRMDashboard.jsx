/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM COMMAND CENTER [R18AD67-CRM-DASHBOARD-CATALOG-COMMAND-WIRE]                                                                         ║
 * ║ [EXECUTIVE DASHBOARD PARITY | ZOHO-CLEAN MODULE RAIL | SOURCE-TRUTH CRM | TENANT BRANDING RUNTIME | WILSY AI COMMAND ENGINE]        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: R18AD67-CRM-DASHBOARD-CATALOG-COMMAND-WIRE | PRODUCTION READY | CRM OPERATING SYSTEM SURFACE                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/crm/CRMDashboard.jsx                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                   ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated ExecutiveDashboard as the Wilsy OS benchmark and rejected endless scroll CRM layouts.     ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Rebuilt CRM as a clean operating shell with real service routes and no fabricated records.   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useCallback, useEffect, useMemo, useRef, useState, Suspense } from 'react';
import {
  Activity,
  AlertCircle,
  BarChart3,
  Briefcase,
  Building2,
  Calendar,
  CheckCircle,
  Clock,
  Database,
  Download,
  FileText,
  Folder,
  Home,
  LayoutGrid,
  Loader2,
  MapPin,
  Megaphone,
  MessageSquare,
  PhoneCall,
  Plus,
  RefreshCw,
  Search,
  Shield,
  Sparkles,
  Target,
  TrendingUp,
  UploadCloud,
  UserCog,
  Users,
  Wand2,
  X
} from 'lucide-react';
import * as crmService from '../../services/crmService';
import {
  WILSY_CRM_CATALOG_READINESS,
  WILSY_CRM_IMPORT_VENDOR_CATALOG,
  WILSY_CRM_MODULE_CATALOG,
  WILSY_CRM_MODULE_CATALOG_VERSION,
  WILSY_CRM_ROUTE_POSTURE,
  WILSY_CRM_WORKSPACE_CATALOG,
  buildWilsyCrmModuleEnvelope
} from '../../data/wilsyCrmModuleCatalog.js';
import {
  WILSY_CRM_COMMAND_CLIENT_HEALTH,
  WILSY_CRM_COMMAND_CLIENT_VERSION,
  createWilsyCrmRecord,
  deleteWilsyCrmRecord,
  exportWilsyCrmRecords,
  getWilsyCrmCommandCenter,
  getWilsyCrmSourceRegistryEvidence,
  importWilsyCrmRecords,
  listWilsyCrmRecords,
  previewWilsyCrmImportRecords,
  updateWilsyCrmRecord
} from '../../services/wilsyCrmCommandClient.js';
import wilsyOfficialLogo from '../../assets/logo/wilsy.jpeg';
import WilsyAccountCommandCenter from '../account/WilsyAccountCommandCenter';
import WilsyOSDashboardTopRail from '../os/WilsyOSDashboardTopRail';
import styles from './CRMDashboard.module.css';



const WILSY_R18AD67_CRM_DASHBOARD_CATALOG_COMMAND_WIRE = 'R18AD67-CRM-DASHBOARD-CATALOG-COMMAND-WIRE';

const WILSY_R18AD69_CRM_CATALOG_RENDER_GUARD = 'R18AD69-CRM-CATALOG-RENDER-GUARD';


const WILSY_R9U_CRM_LIVE_OVERLAY_INLINE_IDENTITY_FIX = 'WILSY_R9U_CRM_LIVE_OVERLAY_INLINE_IDENTITY_FIX_ACTIVE';

/**
 * @function applyWilsyR9UInlineStyle
 * @description Applies important inline styles to the active CRM overlay Command Identity nodes when CSS module cascade is insufficient.
 * @collaboration Repairs the CRM Account Command Center identity surface without changing auth, tenant state, or Account Center source data.
 */
const applyWilsyR9UInlineStyle = (node, styles = {}) => {
  if (!node || !node.style) return;

  Object.entries(styles).forEach(([property, value]) => {
    const cssProperty = String(property).replace(/[A-Z]/g, match => `-${match.toLowerCase()}`);
    node.style.setProperty(cssProperty, value, 'important');
  });
};

/**
 * @function repairWilsyR9UCrmOverlayIdentity
 * @description Finds the live CRM account settings overlay and unclips the restored R7C Command Identity hierarchy.
 * @collaboration Preserves the restored R7C identity shell while making command labels, evidence seals, and tenant scope readable.
 */
const repairWilsyR9UCrmOverlayIdentity = () => {
  if (typeof document === 'undefined') return;

  const overlays = Array.from(document.querySelectorAll('[class*="accountSettingsOverlay"]'));

  overlays.forEach((overlay) => {
    overlay.setAttribute('data-wilsy-r9u-crm-overlay-identity-fixed', 'true');

    const identityCards = overlay.querySelectorAll('[data-wilsy-identity-chrome], [data-wilsy-r7c-identity-card="true"]');
    const identityShells = overlay.querySelectorAll('[data-wilsy-r7c-identity-ui="true"]');
    const identityContent = overlay.querySelectorAll('.wilsy-r7c-identity-content');
    const eyebrowRows = overlay.querySelectorAll('.wilsy-r7c-identity-eyebrow');
    const commandLabels = overlay.querySelectorAll('.wilsy-r7c-command-label');
    const verifiedLabels = overlay.querySelectorAll('.wilsy-r7c-verified-label');
    const identityNames = overlay.querySelectorAll('.wilsy-r7c-identity-name');
    const accountRows = overlay.querySelectorAll('.wilsy-r7c-identity-account');
    const evidenceRows = overlay.querySelectorAll('.wilsy-r7f-identity-evidence');
    const evidenceItems = overlay.querySelectorAll('.wilsy-r7f-identity-evidence span, .wilsy-r7f-clause-anchor, .wilsy-r7f-identity-seal');
    const tenantPills = overlay.querySelectorAll('.wilsy-r7c-tenant-pill');
    const tenantTexts = overlay.querySelectorAll('.wilsy-r7c-tenant-text');

    identityCards.forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        width: '100%',
        maxWidth: '100%',
        minWidth: '0',
        maxHeight: 'none',
        overflow: 'visible',
        boxSizing: 'border-box'
      });
    });

    identityShells.forEach((node) => {
      node.setAttribute('data-wilsy-r9u-active-identity-shell', 'true');
      applyWilsyR9UInlineStyle(node, {
        width: '100%',
        maxWidth: '100%',
        minWidth: '0',
        display: 'grid',
        gridTemplateColumns: 'clamp(104px, 7vw, 132px) minmax(0, 1fr)',
        gap: 'clamp(28px, 3vw, 44px)',
        alignItems: 'start',
        overflow: 'visible',
        boxSizing: 'border-box'
      });
    });

    identityContent.forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        display: 'grid',
        gridTemplateRows: 'auto auto auto auto auto',
        alignContent: 'start',
        gap: '14px',
        width: '100%',
        maxWidth: '100%',
        minWidth: '0',
        overflow: 'visible',
        boxSizing: 'border-box'
      });
    });

    eyebrowRows.forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1fr)',
        gridAutoRows: 'auto',
        justifyItems: 'start',
        alignItems: 'start',
        gap: '8px',
        width: '100%',
        maxWidth: '100%',
        minWidth: '0',
        overflow: 'visible',
        whiteSpace: 'normal'
      });
    });

    [...commandLabels, ...verifiedLabels].forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        display: 'inline-flex',
        width: 'max-content',
        minWidth: 'max-content',
        maxWidth: 'none',
        flex: '0 0 auto',
        overflow: 'visible',
        textOverflow: 'clip',
        whiteSpace: 'nowrap',
        overflowWrap: 'normal',
        letterSpacing: '0.12em',
        fontSize: 'clamp(9px, 0.62vw, 11px)',
        lineHeight: '1.15'
      });
    });

    identityNames.forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        width: '100%',
        maxWidth: '100%',
        minWidth: '0',
        overflow: 'visible',
        textOverflow: 'clip',
        whiteSpace: 'normal',
        overflowWrap: 'anywhere'
      });
    });

    accountRows.forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        width: '100%',
        maxWidth: '100%',
        minWidth: '0',
        overflow: 'visible',
        textOverflow: 'clip',
        whiteSpace: 'normal',
        overflowWrap: 'anywhere'
      });
    });

    evidenceRows.forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'flex-start',
        alignItems: 'center',
        gap: '8px 14px',
        width: '100%',
        maxWidth: '100%',
        minWidth: '100%',
        overflow: 'visible',
        whiteSpace: 'normal'
      });
    });

    evidenceItems.forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        display: 'inline-flex',
        width: 'max-content',
        minWidth: 'max-content',
        maxWidth: 'none',
        flex: '0 0 auto',
        overflow: 'visible',
        textOverflow: 'clip',
        whiteSpace: 'nowrap',
        overflowWrap: 'normal',
        letterSpacing: '0.10em',
        fontSize: 'clamp(8px, 0.54vw, 10px)',
        lineHeight: '1.18'
      });
    });


    /* WILSY_R9U_C_ZERO_WIDTH_COLLAPSE_HARDENING */
    [...eyebrowRows, ...evidenceRows].forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        position: 'relative',
        display: 'flex',
        flexWrap: 'wrap',
        width: '100%',
        minWidth: '100%',
        maxWidth: '100%',
        inlineSize: '100%',
        minInlineSize: '100%',
        maxInlineSize: '100%',
        blockSize: 'auto',
        contain: 'none',
        clipPath: 'none',
        overflow: 'visible',
        textOverflow: 'clip',
        whiteSpace: 'normal',
        transform: 'none'
      });
    });

    [...commandLabels, ...verifiedLabels, ...evidenceItems].forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        position: 'relative',
        display: 'inline-flex',
        flex: '0 0 auto',
        flexShrink: '0',
        flexGrow: '0',
        width: 'max-content',
        minWidth: 'max-content',
        maxWidth: 'none',
        inlineSize: 'max-content',
        minInlineSize: 'max-content',
        maxInlineSize: 'none',
        blockSize: 'auto',
        minBlockSize: 'auto',
        contain: 'none',
        clipPath: 'none',
        overflow: 'visible',
        textOverflow: 'clip',
        whiteSpace: 'nowrap',
        overflowWrap: 'normal',
        wordBreak: 'normal',
        transform: 'none'
      });
    });


    /* WILSY_R9V_CRM_READABLE_COMMAND_IDENTITY_RAIL */
    identityContent.forEach((contentNode) => {
      const originalEyebrow = contentNode.querySelector('.wilsy-r7c-identity-eyebrow');
      const originalEvidence = contentNode.querySelector('.wilsy-r7f-identity-evidence');

      const commandText = originalEyebrow?.querySelector('.wilsy-r7c-command-label')?.textContent?.trim() || 'Command Identity';
      const verifiedText = originalEyebrow?.querySelector('.wilsy-r7c-verified-label')?.textContent?.trim() || 'Tenant Verified';
      const evidenceText = originalEvidence?.textContent?.replace(/\s+/g, ' ')?.trim() || 'POPIA S19 • TENANT AUTHORITY CID';

      let readableHeader = contentNode.querySelector('[data-wilsy-r9v-readable-identity-header="true"]');

      if (!readableHeader) {
        readableHeader = document.createElement('div');
        readableHeader.setAttribute('data-wilsy-r9v-readable-identity-header', 'true');

        if (originalEyebrow?.parentNode) {
          originalEyebrow.parentNode.insertBefore(readableHeader, originalEyebrow);
        } else {
          contentNode.prepend(readableHeader);
        }
      }

      readableHeader.textContent = '';

      [commandText, verifiedText].forEach((labelText) => {
        const label = document.createElement('span');
        label.textContent = labelText;
        readableHeader.appendChild(label);

        applyWilsyR9UInlineStyle(label, {
          display: 'inline-flex',
          width: 'max-content',
          minWidth: 'max-content',
          maxWidth: '100%',
          overflow: 'visible',
          textOverflow: 'clip',
          whiteSpace: 'nowrap',
          letterSpacing: '0.14em',
          fontSize: 'clamp(10px, 0.72vw, 13px)',
          lineHeight: '1.15',
          fontWeight: '900',
          textTransform: 'uppercase'
        });
      });

      applyWilsyR9UInlineStyle(readableHeader, {
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'flex-start',
        gap: '8px 22px',
        width: '100%',
        minWidth: '100%',
        maxWidth: '100%',
        overflow: 'visible',
        whiteSpace: 'normal',
        contain: 'none',
        clipPath: 'none'
      });

      let readableEvidence = contentNode.querySelector('[data-wilsy-r9v-readable-identity-evidence="true"]');

      if (!readableEvidence) {
        readableEvidence = document.createElement('div');
        readableEvidence.setAttribute('data-wilsy-r9v-readable-identity-evidence', 'true');

        if (originalEvidence?.parentNode) {
          originalEvidence.parentNode.insertBefore(readableEvidence, originalEvidence);
        } else {
          contentNode.appendChild(readableEvidence);
        }
      }

      readableEvidence.textContent = '';

      const normalizedEvidence = evidenceText
        .replace(/(CID-[A-Z0-9]+)/g, ' $1')
        .replace(/(TENANT AUTHORITY)/gi, ' $1 ')
        .split(/\s{2,}|(?=CID-)|(?=TENANT AUTHORITY)/i)
        .map(item => item.trim())
        .filter(Boolean);

      normalizedEvidence.forEach((itemText) => {
        const item = document.createElement('span');
        item.textContent = itemText;
        readableEvidence.appendChild(item);

        applyWilsyR9UInlineStyle(item, {
          display: 'inline-flex',
          width: 'max-content',
          minWidth: 'max-content',
          maxWidth: '100%',
          overflow: 'visible',
          textOverflow: 'clip',
          whiteSpace: 'nowrap',
          letterSpacing: '0.10em',
          fontSize: 'clamp(8px, 0.54vw, 10px)',
          lineHeight: '1.18',
          fontWeight: '850',
          textTransform: 'uppercase'
        });
      });

      applyWilsyR9UInlineStyle(readableEvidence, {
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'flex-start',
        gap: '8px 14px',
        width: '100%',
        minWidth: '100%',
        maxWidth: '100%',
        overflow: 'visible',
        whiteSpace: 'normal',
        contain: 'none',
        clipPath: 'none'
      });

      if (originalEyebrow) {
        originalEyebrow.setAttribute('data-wilsy-r9v-superseded-zero-width-rail', 'true');
        applyWilsyR9UInlineStyle(originalEyebrow, {
          display: 'none',
          visibility: 'hidden',
          pointerEvents: 'none'
        });
      }

      if (originalEvidence) {
        originalEvidence.setAttribute('data-wilsy-r9v-superseded-zero-width-rail', 'true');
        applyWilsyR9UInlineStyle(originalEvidence, {
          display: 'none',
          visibility: 'hidden',
          pointerEvents: 'none'
        });
      }
    });

    tenantPills.forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        width: 'min(100%, 620px)',
        maxWidth: '100%',
        minWidth: '0',
        overflow: 'visible'
      });
    });

    tenantTexts.forEach((node) => {
      applyWilsyR9UInlineStyle(node, {
        minWidth: '0',
        maxWidth: '100%',
        overflow: 'visible',
        textOverflow: 'clip',
        whiteSpace: 'normal'
      });
    });
  });
};

/**
 * @function scheduleWilsyR9UCrmOverlayIdentityFix
 * @description Schedules bounded CRM overlay identity repair passes after route render, click-open, and animation frames.
 * @collaboration Avoids observers while ensuring the Account Command Center overlay is repaired when it appears.
 */
const scheduleWilsyR9UCrmOverlayIdentityFix = () => {
  if (typeof window === 'undefined') return;

  [0, 50, 150, 350, 700, 1200, 2200].forEach((delay) => {
    window.setTimeout(repairWilsyR9UCrmOverlayIdentity, delay);
  });
};

/**
 * @function bootWilsyR9UCrmOverlayIdentityFix
 * @description Boots the CRM overlay identity repair with bounded event scheduling and no document-level observer.
 * @collaboration Targets only the active CRM overlay that hosts the Account Command Center card.
 */
const bootWilsyR9UCrmOverlayIdentityFix = () => {
  if (typeof window === 'undefined' || window.__wilsyR9UCrmOverlayIdentityFixBooted) return;

  window.__wilsyR9UCrmOverlayIdentityFixBooted = true;
  scheduleWilsyR9UCrmOverlayIdentityFix();

  window.addEventListener('click', scheduleWilsyR9UCrmOverlayIdentityFix, { passive: true });
  window.addEventListener('focusin', scheduleWilsyR9UCrmOverlayIdentityFix, { passive: true });
  window.addEventListener('resize', scheduleWilsyR9UCrmOverlayIdentityFix, { passive: true });
};

bootWilsyR9UCrmOverlayIdentityFix();

const WILSY_R9W_BODY_MOUNTED_COMMAND_IDENTITY_RAIL = 'WILSY_R9W_BODY_MOUNTED_COMMAND_IDENTITY_RAIL_ACTIVE';

/**
 * @function applyWilsyR9WBodyRailStyle
 * @description Applies important inline styles to the body-mounted CRM Command Identity rail.
 * @collaboration Bypasses the zero-width CRM identity content region without changing tenant/auth data.
 */
const applyWilsyR9WBodyRailStyle = (node, styles = {}) => {
  if (!node || !node.style) return;

  Object.entries(styles).forEach(([property, value]) => {
    const cssProperty = String(property).replace(/[A-Z]/g, match => `-${match.toLowerCase()}`);
    node.style.setProperty(cssProperty, value, 'important');
  });
};

/**
 * @function ensureWilsyR9WBodyRail
 * @description Creates or returns the body-mounted readable identity rail for the active CRM overlay.
 * @collaboration Preserves the restored R7C identity source while rendering readable command/evidence copy outside the poisoned layout node.
 */
const ensureWilsyR9WBodyRail = () => {
  if (typeof document === 'undefined') return null;

  let rail = document.querySelector('[data-wilsy-r9w-body-mounted-identity-rail="true"]');

  if (!rail) {
    rail = document.createElement('div');
    rail.setAttribute('data-wilsy-r9w-body-mounted-identity-rail', 'true');

    const header = document.createElement('div');
    header.setAttribute('data-wilsy-r9w-body-mounted-identity-header', 'true');

    const command = document.createElement('span');
    command.setAttribute('data-wilsy-r9w-command-label', 'true');
    command.textContent = 'COMMAND IDENTITY';

    const verified = document.createElement('span');
    verified.setAttribute('data-wilsy-r9w-verified-label', 'true');
    verified.textContent = '● TENANT VERIFIED';

    header.append(command, verified);

    const evidence = document.createElement('div');
    evidence.setAttribute('data-wilsy-r9w-body-mounted-identity-evidence', 'true');

    const clause = document.createElement('span');
    clause.textContent = 'POPIA S19';

    const authority = document.createElement('span');
    authority.textContent = 'TENANT AUTHORITY';

    const cid = document.createElement('span');
    cid.setAttribute('data-wilsy-r9w-cid-label', 'true');
    cid.textContent = 'CID';

    evidence.append(clause, authority, cid);
    rail.append(header, evidence);
    document.body.appendChild(rail);
  }

  return rail;
};

/**
 * @function repairWilsyR9WBodyMountedIdentityRail
 * @description Positions a readable body-mounted command identity rail over the active CRM identity card.
 * @collaboration Solves the zero-width label failure proven by DevTools while keeping the CRM overlay and Account Command Center intact.
 */
const repairWilsyR9WBodyMountedIdentityRail = () => {
  if (typeof document === 'undefined' || typeof window === 'undefined') return;

  const overlay = document.querySelector('[class*="accountSettingsOverlay"]');
  if (!overlay) return;

  const shellCandidates = Array.from(
    overlay.querySelectorAll('[data-wilsy-r9u-active-identity-shell="true"], [data-wilsy-r7c-identity-ui="true"], [data-wilsy-identity-chrome], [data-wilsy-r7c-identity-card="true"]')
  );

  const visibleShellFrames = shellCandidates
    .map(node => {
      const candidateRect = node.getBoundingClientRect();
      return {
        node,
        rect: candidateRect,
        area: Math.max(0, candidateRect.width) * Math.max(0, candidateRect.height)
      };
    })
    .filter(item => item.rect.width >= 120 && item.rect.height >= 80)
    .sort((a, b) => b.area - a.area);

  const overlayRect = overlay.getBoundingClientRect();
  const selectedFrame = visibleShellFrames[0] || {
    node: overlay,
    rect: {
      left: overlayRect.left + 24,
      top: overlayRect.top + 24,
      width: Math.min(460, Math.max(320, overlayRect.width * 0.30)),
      height: 156
    },
    area: 1
  };

  const rect = selectedFrame.rect;
  overlay.setAttribute('data-wilsy-r9w-frame-source', visibleShellFrames[0] ? 'visible-shell' : 'overlay-fallback');
  overlay.setAttribute('data-wilsy-r9w-frame-candidates', String(shellCandidates.length));

  const rail = ensureWilsyR9WBodyRail();
  if (!rail) return;

  const sourceEvidenceText = overlay
    .querySelector('[data-wilsy-r9v-readable-identity-evidence="true"], .wilsy-r7f-identity-evidence')
    ?.textContent
    ?.replace(/\s+/g, ' ')
    ?.trim();

  const cidMatch = sourceEvidenceText?.match(/CID[-A-Z0-9]+/i);
  const cidNode = rail.querySelector('[data-wilsy-r9w-cid-label="true"]');
  if (cidNode && cidMatch?.[0]) cidNode.textContent = cidMatch[0].toUpperCase();

  const leftOffset = Math.min(132, Math.max(112, rect.width * 0.30));
  const railLeft = rect.left + leftOffset;
  const railTop = rect.top + 23;
  const railWidth = Math.max(240, rect.width - leftOffset - 26);

  applyWilsyR9WBodyRailStyle(rail, {
    position: 'fixed',
    zIndex: '2147483646',
    left: `${railLeft}px`,
    top: `${railTop}px`,
    width: `${railWidth}px`,
    maxWidth: `${railWidth}px`,
    minWidth: `${railWidth}px`,
    pointerEvents: 'none',
    display: 'grid',
    gridTemplateRows: 'auto auto',
    gap: '52px',
    overflow: 'visible',
    contain: 'none',
    clipPath: 'none',
    background: 'transparent',
    transform: 'translateZ(0)'
  });

  const header = rail.querySelector('[data-wilsy-r9w-body-mounted-identity-header="true"]');
  applyWilsyR9WBodyRailStyle(header, {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    justifyContent: 'flex-start',
    gap: '8px 22px',
    width: '100%',
    minWidth: '100%',
    overflow: 'visible',
    whiteSpace: 'normal'
  });

  rail.querySelectorAll('[data-wilsy-r9w-body-mounted-identity-header="true"] span').forEach((node) => {
    applyWilsyR9WBodyRailStyle(node, {
      display: 'inline-flex',
      flex: '0 0 auto',
      width: 'max-content',
      minWidth: 'max-content',
      maxWidth: 'none',
      overflow: 'visible',
      textOverflow: 'clip',
      whiteSpace: 'nowrap',
      letterSpacing: '0.18em',
      fontSize: '11px',
      lineHeight: '1',
      fontWeight: '950',
      textTransform: 'uppercase',
      color: node.textContent.includes('TENANT') ? '#31f59b' : '#d7deef',
      textShadow: '0 0 18px rgba(0, 209, 255, 0.25)'
    });
  });

  const evidence = rail.querySelector('[data-wilsy-r9w-body-mounted-identity-evidence="true"]');
  applyWilsyR9WBodyRailStyle(evidence, {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    justifyContent: 'flex-start',
    gap: '8px 14px',
    width: '100%',
    minWidth: '100%',
    overflow: 'visible',
    whiteSpace: 'normal'
  });

  rail.querySelectorAll('[data-wilsy-r9w-body-mounted-identity-evidence="true"] span').forEach((node) => {
    applyWilsyR9WBodyRailStyle(node, {
      display: 'inline-flex',
      flex: '0 0 auto',
      width: 'max-content',
      minWidth: 'max-content',
      maxWidth: 'none',
      overflow: 'visible',
      textOverflow: 'clip',
      whiteSpace: 'nowrap',
      letterSpacing: '0.12em',
      fontSize: '10px',
      lineHeight: '1',
      fontWeight: '900',
      textTransform: 'uppercase',
      color: node.textContent.startsWith('CID') ? '#e0c45c' : '#31f59b',
      textShadow: '0 0 14px rgba(49, 245, 155, 0.22)'
    });
  });

  overlay
    .querySelectorAll('.wilsy-r7c-identity-eyebrow, .wilsy-r7f-identity-evidence, [data-wilsy-r9v-readable-identity-header="true"], [data-wilsy-r9v-readable-identity-evidence="true"]')
    .forEach((node) => {
      node.setAttribute('data-wilsy-r9w-hidden-dead-identity-rail', 'true');
      applyWilsyR9WBodyRailStyle(node, {
        opacity: '0',
        visibility: 'hidden',
        pointerEvents: 'none'
      });
    });
};

/**
 * @function scheduleWilsyR9WBodyMountedIdentityRail
 * @description Schedules body rail repair after CRM overlay render and interaction frames.
 * @collaboration Keeps the readable identity rail aligned to the live card during account overlay usage.
 */
const scheduleWilsyR9WBodyMountedIdentityRail = () => {
  if (typeof window === 'undefined') return;

  [0, 40, 120, 260, 520, 900, 1500, 2400].forEach((delay) => {
    window.setTimeout(repairWilsyR9WBodyMountedIdentityRail, delay);
  });
};

/**
 * @function bootWilsyR9WBodyMountedIdentityRail
 * @description Boots the body-mounted CRM identity rail with bounded event scheduling.
 * @collaboration Provides the final readable overlay path after the live card region proved zero-width.
 */
const bootWilsyR9WBodyMountedIdentityRail = () => {
  if (typeof window === 'undefined' || window.__wilsyR9WBodyMountedIdentityRailBooted) return;

  window.__wilsyR9WBodyMountedIdentityRailBooted = true;
  scheduleWilsyR9WBodyMountedIdentityRail();

  window.addEventListener('click', scheduleWilsyR9WBodyMountedIdentityRail, { passive: true });
  window.addEventListener('focusin', scheduleWilsyR9WBodyMountedIdentityRail, { passive: true });
  window.addEventListener('resize', scheduleWilsyR9WBodyMountedIdentityRail, { passive: true });
  window.addEventListener('scroll', scheduleWilsyR9WBodyMountedIdentityRail, { passive: true });
};

bootWilsyR9WBodyMountedIdentityRail();





const CRM_VERSION = 'R18AD67-CRM-DASHBOARD-CATALOG-COMMAND-WIRE';
const DEFAULT_TENANT_ID = 'MASTER';
const DEFAULT_PAGE_LIMIT = 25;
const MAX_RECEIPTS = 14;

const WILSY_CRM_THEME_STORAGE_KEYS = Object.freeze({
  theme: 'wilsy:account-command-center:theme',
  mode: 'wilsy:account-command-center:mode'
});

const WILSY_CRM_THEME_SKINS = Object.freeze({
  wilsy_aurora: {
    accent: '#B66DFF',
    secondary: '#17BDF2',
    authority: '#D4AF37',
    live: '#84F0C8',
    risk: '#FF8AA4',
    surface: '#060B18',
    panel: '#0B1024',
    rail: '#080C18',
    bg: '#020306',
    text: '#FFFAF0',
    muted: '#C5CCE5',
    border: 'rgba(182,109,255,0.34)'
  },
  sovereign_black: {
    accent: '#D4AF37',
    secondary: '#56D69B',
    authority: '#F6D76B',
    live: '#56D69B',
    risk: '#FF6673',
    surface: '#050505',
    panel: '#0B0B0B',
    rail: '#030303',
    bg: '#000000',
    text: '#FFFFFF',
    muted: '#A7A7A7',
    border: 'rgba(212,175,55,0.32)'
  },
  cobalt_glass: {
    accent: '#17BDF2',
    secondary: '#8DBBFF',
    authority: '#D4AF37',
    live: '#54F0D1',
    risk: '#FF7C98',
    surface: '#06142E',
    panel: '#0A1D3D',
    rail: '#07132B',
    bg: '#020817',
    text: '#F3F8FF',
    muted: '#AFC7F6',
    border: 'rgba(23,189,242,0.34)'
  },
  pearl_command: {
    accent: '#7C68FF',
    secondary: '#0F9F6E',
    authority: '#C49A18',
    live: '#0F9F6E',
    risk: '#D33F62',
    surface: '#FFFFFF',
    panel: '#EEF2FF',
    rail: '#FFFFFF',
    bg: '#F6F8FF',
    text: '#111827',
    muted: '#53617F',
    border: 'rgba(124,104,255,0.26)'
  },
  legacy_gold: {
    accent: '#D4AF37',
    secondary: '#8FE6B1',
    authority: '#F6D76B',
    live: '#8FE6B1',
    risk: '#FF8A8A',
    surface: '#0D0A03',
    panel: '#141006',
    rail: '#090702',
    bg: '#070602',
    text: '#FFF8DC',
    muted: '#B9A56D',
    border: 'rgba(246,215,107,0.32)'
  },
  forensic_violet: {
    accent: '#B66DFF',
    secondary: '#E7B7FF',
    authority: '#D4AF37',
    live: '#84F0C8',
    risk: '#FF8AA4',
    surface: '#0D0718',
    panel: '#140B26',
    rail: '#090412',
    bg: '#05020A',
    text: '#FFF7FF',
    muted: '#CAB8EA',
    border: 'rgba(182,109,255,0.36)'
  },
  quantum: {
    accent: '#17F2D1',
    secondary: '#B6F6FF',
    authority: '#D4AF37',
    live: '#84F0C8',
    risk: '#FF789A',
    surface: '#06111A',
    panel: '#071C25',
    rail: '#031018',
    bg: '#01050A',
    text: '#F5FFFF',
    muted: '#9FD7E7',
    border: 'rgba(23,242,209,0.34)'
  }
});

const CRM_ICON_MAP = Object.freeze({
  home: Home,
  command: Home,
  database: Database,
  records: Database,
  leads: Users,
  contacts: Users,
  accounts: Building2,
  deals: Target,
  tasks: CheckCircle,
  meetings: Calendar,
  calls: PhoneCall,
  campaigns: Megaphone,
  documents: Folder,
  visits: MapPin,
  projects: Activity,
  quotes: FileText,
  invoices: FileText,
  cases: Shield,
  tickets: MessageSquare,
  contracts: FileText,
  authorities: Shield,
  risks: AlertCircle,
  opportunities: TrendingUp,
  suppliers: Briefcase,
  partners: Users,
  success: Users,
  support: MessageSquare,
  conversations: MessageSquare,
  forecast: TrendingUp,
  workflows: Wand2,
  automation: Wand2,
  connectors: Database,
  audit: Shield,
  evidence: Shield,
  shield: Shield,
  upload: UploadCloud,
  sparkles: Sparkles,
  wand: Wand2,
  messageSquare: MessageSquare,
  target: Target
});

const CRM_MODULES = Object.freeze(WILSY_CRM_MODULE_CATALOG.map(moduleConfig => ({
  ...moduleConfig,
  sourceStatus: moduleConfig?.sourceContract?.minimumStatus || 'SOURCE_REQUIRED',
  routePosture: moduleConfig?.routePosture || WILSY_CRM_ROUTE_POSTURE.required,
  catalogVersion: WILSY_CRM_MODULE_CATALOG_VERSION,
  commandEnvelope: buildWilsyCrmModuleEnvelope(moduleConfig.id)
})));

const CRM_WORKSPACES = Object.freeze(WILSY_CRM_WORKSPACE_CATALOG.map(workspace => ({
  ...workspace,
  id: workspace.id === 'command' ? 'home' : workspace.id,
  sourceWorkspaceId: workspace.id,
  icon: CRM_ICON_MAP[workspace.icon] || Home
})));

/**
 * @function resolveCrmCatalogModuleConfig
 * @description Resolves a CRM module from the governed catalog with a safe fallback so legacy dashboard rails cannot crash render.
 * @param {string} moduleId - Candidate CRM module id.
 * @param {string} fallbackId - Fallback CRM module id.
 * @returns {Object} Safe CRM module config.
 * @collaboration Keeps the catalog-driven CRM shell stable while older UI rails are being migrated one file at a time.
 */
const resolveCrmCatalogModuleConfig = (moduleId = 'leads', fallbackId = 'leads') => {
  const normalizedId = String(moduleId || '').trim().toLowerCase();
  const normalizedFallback = String(fallbackId || 'leads').trim().toLowerCase();

  return (
    CRM_MODULES.find(item => item?.id === normalizedId)
    || CRM_MODULES.find(item => item?.id === normalizedFallback)
    || CRM_MODULES[0]
    || {
      id: 'source_required',
      label: 'Source Required',
      singular: 'Record',
      icon: 'database',
      route: 'records',
      primary: 'name',
      secondary: 'status',
      money: null,
      boardBy: 'status',
      lanes: ['source_required'],
      fields: ['name', 'status'],
      sourceStatus: 'SOURCE_REQUIRED',
      routePosture: 'ROUTE_REQUIRED'
    }
  );
};

/**
 * @function resolveCrmCatalogIcon
 * @description Resolves a CRM icon component from the icon map with a safe fallback.
 * @param {string} iconKey - Catalog icon key.
 * @param {React.ComponentType} fallbackIcon - Fallback icon component.
 * @returns {React.ComponentType} Icon component.
 * @collaboration Prevents catalog growth from breaking CRM module, workspace and task rails.
 */
const resolveCrmCatalogIcon = (iconKey = 'database', fallbackIcon = Database) => (
  CRM_ICON_MAP[String(iconKey || '').trim()] || fallbackIcon || Database
);


const FIELD_LABELS = Object.freeze({
  accountName: 'Account',
  annualRevenue: 'Annual Revenue',
  authorityStatus: 'Authority',
  budget: 'Budget',
  channel: 'Channel',
  closingDate: 'Close Date',
  company: 'Company',
  completedAt: 'Completed',
  contactName: 'Contact',
  contractStatus: 'Contract',
  documentType: 'Document Type',
  dueDate: 'Due Date',
  effectiveDate: 'Effective Date',
  email: 'Email',
  evidenceType: 'Evidence Type',
  fileName: 'File Name',
  industry: 'Industry',
  leadsGenerated: 'Leads',
  location: 'Location',
  name: 'Name',
  number: 'Number',
  outcome: 'Outcome',
  owner: 'Owner',
  percentComplete: 'Complete',
  phone: 'Phone',
  priority: 'Priority',
  probability: 'Probability',
  scheduledAt: 'Scheduled',
  score: 'Score',
  severity: 'Severity',
  stage: 'Stage',
  startsAt: 'Start',
  status: 'Status',
  subject: 'Subject',
  title: 'Title',
  validUntil: 'Valid Until',
  value: 'Value',
  verifiedAt: 'Verified',
  healthScore: 'Health Score',
  healthStatus: 'Health',
  renewalDate: 'Renewal Date',
  renewalValue: 'Renewal Value',
  slaStatus: 'SLA',
  channel: 'Channel',
  lastMessageAt: 'Last Message',
  trigger: 'Trigger',
  targetModule: 'Target Module',
  lastRunAt: 'Last Run',
  vendor: 'Vendor',
  lastSyncAt: 'Last Sync',
  recordsSynced: 'Records Synced',
  receiptId: 'Receipt',
  operatorId: 'Operator',
  moduleId: 'Module',
  action: 'Action',
  period: 'Period',
  forecastValue: 'Forecast',
  pipelineValue: 'Pipeline',
  confidence: 'Confidence'
});

const FIELD_TYPES = Object.freeze({
  amount: 'number',
  annualRevenue: 'number',
  budget: 'number',
  closingDate: 'date',
  completedAt: 'date',
  dueDate: 'date',
  effectiveDate: 'date',
  email: 'email',
  leadsGenerated: 'number',
  percentComplete: 'number',
  phone: 'tel',
  probability: 'number',
  scheduledAt: 'date',
  score: 'number',
  startsAt: 'datetime-local',
  validUntil: 'date',
  value: 'number',
  verifiedAt: 'date',
  healthScore: 'number',
  renewalDate: 'date',
  renewalValue: 'number',
  lastMessageAt: 'datetime-local',
  lastRunAt: 'datetime-local',
  lastSyncAt: 'datetime-local',
  recordsSynced: 'number',
  forecastValue: 'number',
  pipelineValue: 'number',
  confidence: 'number'
});

/**
 * @function normalizeWilsyCrmThemeId
 * @description Normalizes Account Command Center theme ids for CRM.
 * @param {string} themeId - Candidate theme id.
 * @returns {string} Supported CRM theme id.
 * @collaboration Keeps CRM visual skin aligned with ExecutiveDashboard and Account Command Center.
 */
const normalizeWilsyCrmThemeId = (themeId = '') => {
  const aliases = {
    forensic: 'forensic_violet',
    cobalt: 'cobalt_glass',
    wilsy_daybreak: 'pearl_command',
    dark_ops: 'sovereign_black'
  };
  const normalized = aliases[themeId] || themeId || 'wilsy_aurora';
  return WILSY_CRM_THEME_SKINS[normalized] ? normalized : 'wilsy_aurora';
};

/**
 * @function normalizeWilsyCrmMode
 * @description Normalizes Account Command Center mode values for CRM.
 * @param {string} mode - Candidate mode.
 * @returns {string} Safe mode value.
 * @collaboration Protects CRM from invalid theme receipts.
 */
const normalizeWilsyCrmMode = (mode = '') => (
  ['day', 'night', 'auto'].includes(mode) ? mode : 'night'
);

/**
 * @function resolveWilsyCrmMode
 * @description Resolves automatic day or night mode.
 * @param {string} mode - Candidate mode.
 * @returns {string} Resolved mode.
 * @collaboration Mirrors ExecutiveDashboard theme behavior for CRM.
 */
const resolveWilsyCrmMode = (mode = 'night') => {
  const safeMode = normalizeWilsyCrmMode(mode);
  if (safeMode !== 'auto') return safeMode;
  const hour = new Date().getHours();
  return hour >= 7 && hour < 18 ? 'day' : 'night';
};

/**
 * @function readWilsyCrmThemePreference
 * @description Reads persisted Account Command Center theme settings.
 * @returns {{themeId:string,mode:string,resolvedMode:string,skin:Object}} Theme packet.
 * @collaboration Gives CRM the same operating theme source as ExecutiveDashboard.
 */
const readWilsyCrmThemePreference = () => {
  const themeId = normalizeWilsyCrmThemeId(
    typeof window === 'undefined'
      ? 'wilsy_aurora'
      : window.localStorage.getItem(WILSY_CRM_THEME_STORAGE_KEYS.theme)
  );
  const mode = normalizeWilsyCrmMode(
    typeof window === 'undefined'
      ? 'night'
      : window.localStorage.getItem(WILSY_CRM_THEME_STORAGE_KEYS.mode)
  );
  return {
    themeId,
    mode,
    resolvedMode: resolveWilsyCrmMode(mode),
    skin: WILSY_CRM_THEME_SKINS[themeId] || WILSY_CRM_THEME_SKINS.wilsy_aurora
  };
};

/**
 * @function buildWilsyCrmThemeVars
 * @description Builds CSS variable payload consumed by the CRM shell.
 * @param {string} themeId - Theme id.
 * @param {string} mode - Theme mode.
 * @returns {Object} CSS variable map.
 * @collaboration Keeps CRM theme behavior equal to ExecutiveDashboard.
 */
const buildWilsyCrmThemeVars = (themeId = 'wilsy_aurora', mode = 'night') => {
  const safeThemeId = normalizeWilsyCrmThemeId(themeId);
  const resolvedMode = resolveWilsyCrmMode(mode);
  const skin = WILSY_CRM_THEME_SKINS[safeThemeId] || WILSY_CRM_THEME_SKINS.wilsy_aurora;

  return {
    '--wilsy-bg': skin.bg,
    '--wilsy-surface': skin.surface,
    '--wilsy-panel': skin.panel,
    '--wilsy-rail': skin.rail,
    '--wilsy-text': skin.text,
    '--wilsy-muted': skin.muted,
    '--wilsy-accent': skin.accent,
    '--wilsy-accent-2': skin.secondary,
    '--wilsy-authority': skin.authority,
    '--wilsy-live': skin.live,
    '--wilsy-risk': skin.risk,
    '--wilsy-border': skin.border,
    colorScheme: resolvedMode === 'day' ? 'light' : 'dark'
  };
};

/**
 * @function applyWilsyCrmThemeToDocument
 * @description Applies current CRM theme to document root and body.
 * @param {string} themeId - Theme id.
 * @param {string} mode - Theme mode.
 * @returns {void}
 * @collaboration Keeps global chrome and CRM surface visually synchronized.
 */
const applyWilsyCrmThemeToDocument = (themeId = 'wilsy_aurora', mode = 'night') => {
  if (typeof document === 'undefined') return;

  const safeThemeId = normalizeWilsyCrmThemeId(themeId);
  const safeMode = normalizeWilsyCrmMode(mode);
  const resolvedMode = resolveWilsyCrmMode(safeMode);
  const vars = buildWilsyCrmThemeVars(safeThemeId, safeMode);

  document.documentElement.dataset.wilsyTheme = safeThemeId;
  document.documentElement.dataset.wilsyMode = safeMode;
  document.documentElement.dataset.wilsyResolvedMode = resolvedMode;
  document.body.dataset.wilsyTheme = safeThemeId;
  document.body.dataset.wilsyMode = safeMode;
  document.body.dataset.wilsyResolvedMode = resolvedMode;
  document.body.dataset.wilsyActiveDashboard = 'crm';

  Object.entries(vars).forEach(([key, value]) => {
    if (key.startsWith('--')) {
      document.documentElement.style.setProperty(key, value);
      document.body.style.setProperty(key, value);
    }
  });
};

/**
 * @function titleizeCrmText
 * @description Converts tokens into readable CRM labels.
 * @param {string} value - Candidate text.
 * @returns {string} Readable label.
 * @collaboration Prevents raw CRM route ids from weakening the operating system UI.
 */
const titleizeCrmText = (value = '') => (
  String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
    .replace(/\b\w/g, letter => letter.toUpperCase())
);

/**
 * @function compactCrmSignal
 * @description Converts source signals into compact CRM posture labels.
 * @param {string} value - Source signal.
 * @returns {string} Compact signal.
 * @collaboration Keeps CRM source posture visible without claiming false verification.
 */
const compactCrmSignal = (value = '') => (
  String(value || 'SOURCE_REQUIRED')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toUpperCase()
);

/**
 * @function numericCrmValue
 * @description Converts a value to a finite number.
 * @param {unknown} value - Candidate value.
 * @returns {number} Numeric value.
 * @collaboration Keeps CRM metrics derived from real records only.
 */
const numericCrmValue = (value = 0) => {
  const next = Number(value);
  return Number.isFinite(next) ? next : 0;
};

/**
 * @function formatCrmMoney
 * @description Formats money values for CRM cards and ledgers.
 * @param {unknown} value - Candidate amount.
 * @returns {string} Formatted money string.
 * @collaboration Keeps CRM commercial truth readable while preserving zero as zero.
 */
const formatCrmMoney = (value = 0) => `R ${Math.round(numericCrmValue(value)).toLocaleString()}`;

/**
 * @function formatCrmDate
 * @description Formats date-like values for CRM ledgers.
 * @param {unknown} value - Candidate date.
 * @returns {string} Formatted date or source required label.
 * @collaboration Prevents invalid dates from becoming misleading CRM evidence.
 */
const formatCrmDate = (value = '') => {
  if (!value) return 'SOURCE REQUIRED';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleDateString();
};

/**
 * @function normalizeCrmLogoCandidate
 * @description Normalizes a tenant logo candidate.
 * @param {unknown} value - Candidate logo value.
 * @returns {string} Safe logo URL or empty string.
 * @collaboration Keeps CRM multi-tenant without fixed local logo paths.
 */
const normalizeCrmLogoCandidate = (value = '') => {
  if (typeof value !== 'string') return '';
  const trimmed = value.trim();
  if (!trimmed) return '';
  if (/placeholder|example|dummy/i.test(trimmed)) return '';
  
  return trimmed;
};

/**
 * @function readStoredCrmBrandingCandidates
 * @description Reads tenant branding candidates from browser storage.
 * @returns {Array<string>} Logo candidates.
 * @collaboration Lets tenant discovery and Account Settings supply CRM tenant logos at runtime.
 */
const readStoredCrmBrandingCandidates = () => {
  if (typeof window === 'undefined') return [];

  return [
    'wilsy:tenant-branding',
    'wilsy:active-tenant',
    'wilsy_active_tenant',
    'activeTenant',
    'tenant',
    'tenantConfig',
    'wilsy_tenant',
    'wilsy:tenant-context',
    'wilsy:tenant-profile',
    'wilsy:tenant-discovery',
    'wilsy:account-command-center:tenant',
    'wilsy:account-command-center:profile',
    'wilsy:account-command-center:branding',
    'wilsy:account-command-center:user',
    'wilsy:user-profile',
    'wilsy:session',
    'wilsy:auth'
  ].flatMap(key => {
    try {
      const raw = window.localStorage.getItem(key);
      if (!raw) return [];

      const directLogo = normalizeCrmLogoCandidate(raw);
      let parsed = null;

      try {
        parsed = JSON.parse(raw);
      } catch {
        return directLogo ? [directLogo] : [];
      }

      return [
        directLogo,
        parsed?.branding?.logoUrl,
        parsed?.branding?.logo,
        parsed?.branding?.brandLogo,
        parsed?.branding?.logoSrc,
        parsed?.branding?.logoDataUrl,
        parsed?.branding?.logoDataUri,
        parsed?.branding?.image,
        parsed?.brand?.logoUrl,
        parsed?.brand?.logo,
        parsed?.assets?.logoUrl,
        parsed?.assets?.logo,
        parsed?.assets?.brandMark,
        parsed?.logoUrl,
        parsed?.logo,
        parsed?.brandLogo,
        parsed?.tenantLogo,
        parsed?.logoDataUrl,
        parsed?.logoDataUri,
        parsed?.avatar,
        parsed?.avatarUrl,
        parsed?.image,
        parsed?.tenant?.branding?.logoUrl,
        parsed?.tenant?.branding?.logo,
        parsed?.tenant?.branding?.brandLogo,
        parsed?.tenant?.logoUrl,
        parsed?.tenant?.logo,
        parsed?.profile?.branding?.logoUrl,
        parsed?.profile?.branding?.logo,
        parsed?.profile?.logoUrl,
        parsed?.profile?.logo,
        parsed?.user?.tenant?.branding?.logoUrl,
        parsed?.user?.tenant?.branding?.logo,
        parsed?.user?.tenant?.logoUrl,
        parsed?.user?.tenant?.logo
      ].map(normalizeCrmLogoCandidate).filter(Boolean);
    } catch {
      return [];
    }
  });
};

/**
 * @function createCrmInitialsSeal
 * @description Creates a tenant initials SVG seal when no logo exists.
 * @param {string} displayName - Tenant display name.
 * @returns {string} SVG data URI.
 * @collaboration Prevents broken tenant branding without borrowing Wilson's local logo.
 */
const createCrmInitialsSeal = (displayName = 'Tenant') => {
  const safeName = String(displayName || 'Tenant').replace(/[<>&"]/g, '');
  const initials = safeName
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(part => part[0])
    .join('')
    .toUpperCase() || 'TN';

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="180" height="180" viewBox="0 0 180 180" role="img" aria-label="${safeName}"><defs><linearGradient id="wilsyTenantSeal" x1="0" x2="1" y1="0" y2="1"><stop offset="0%" stop-color="#D4AF37"/><stop offset="55%" stop-color="#B66DFF"/><stop offset="100%" stop-color="#17BDF2"/></linearGradient></defs><rect width="180" height="180" rx="30" fill="#050505"/><rect x="10" y="10" width="160" height="160" rx="26" fill="url(#wilsyTenantSeal)"/><text x="90" y="104" text-anchor="middle" font-family="Arial, sans-serif" font-size="46" font-weight="900" fill="#050505">${initials}</text></svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
};

/**
 * @function buildCrmTenantIdentity
 * @description Builds tenant and operator identity for CRM.
 * @param {object} params - Identity inputs.
 * @returns {object} Tenant identity packet.
 * @collaboration Makes CRM tenant-branded at scale while keeping founder identity out of tenant logos.
 */
const buildCrmTenantIdentity = ({ tenantId, activeTenant = {}, tenantConfig = {}, user = {} } = {}) => {
  const displayName = (
    activeTenant?.branding?.companyName ||
    activeTenant?.companyName ||
    activeTenant?.name ||
    tenantConfig?.branding?.companyName ||
    tenantConfig?.companyName ||
    tenantConfig?.name ||
    user?.tenant?.name ||
    'Wilsy OS Tenant'
  );

  const operatorName = (
    user?.fullName ||
    user?.displayName ||
    user?.name ||
    [user?.firstName, user?.lastName].filter(Boolean).join(' ') ||
    'CRM Operator'
  );

  const logoCandidates = [
    activeTenant?.branding?.logoUrl,
    activeTenant?.branding?.logo,
    activeTenant?.branding?.brandLogo,
    activeTenant?.branding?.logoSrc,
    activeTenant?.brand?.logoUrl,
    activeTenant?.brand?.logo,
    activeTenant?.assets?.logoUrl,
    activeTenant?.assets?.logo,
    activeTenant?.logoUrl,
    activeTenant?.logo,
    activeTenant?.brandLogo,
    activeTenant?.tenantLogo,
    tenantConfig?.branding?.logoUrl,
    tenantConfig?.branding?.logo,
    tenantConfig?.logoUrl,
    tenantConfig?.logo,
    user?.tenant?.branding?.logoUrl,
    user?.tenant?.branding?.logo,
    user?.tenant?.branding?.brandLogo,
    user?.tenant?.branding?.logoDataUrl,
    user?.tenant?.branding?.logoDataUri,
    user?.tenant?.logoUrl,
    user?.tenant?.logo,
    user?.tenantLogo,
    user?.logoUrl,
    user?.logo,
    user?.avatar,
    user?.avatarUrl,
    tenantConfig?.branding?.logoDataUrl,
    tenantConfig?.branding?.logoDataUri,
    activeTenant?.branding?.logoDataUrl,
    activeTenant?.branding?.logoDataUri,
    import.meta?.env?.VITE_DEFAULT_TENANT_LOGO_URL,
    import.meta?.env?.VITE_TENANT_LOGO_URL,
    import.meta?.env?.VITE_WILSY_BRAND_LOGO_URL,
    ...readStoredCrmBrandingCandidates(),
    wilsyOfficialLogo
  ].map(normalizeCrmLogoCandidate).filter(Boolean);

  return {
    tenantId: tenantId || activeTenant?.tenantId || activeTenant?.id || activeTenant?._id || user?.tenantId || DEFAULT_TENANT_ID,
    displayName,
    operatorName,
    operatorRole: titleizeCrmText(user?.roleLabel || user?.title || user?.role || 'CRM Operator'),
    logo: logoCandidates[0] || createCrmInitialsSeal(displayName),
    story: `${displayName} customer graph live`
  };
};

/**
 * @function safeParseCrmJson
 * @description Parses JSON safely.
 * @param {string} value - JSON string.
 * @returns {object|null} Parsed payload.
 * @collaboration Keeps CRM import intake deterministic.
 */
const safeParseCrmJson = (value = '') => {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
};

/**
 * @function parseCrmCsv
 * @description Parses a simple CSV file into CRM records.
 * @param {string} text - CSV text.
 * @returns {Array<object>} Parsed rows.
 * @collaboration Allows governed competitor exports to enter CRM through preview routes.
 */
const parseCrmCsv = (text = '') => {
  const rows = String(text || '')
    .split(/\r?\n/)
    .filter(Boolean)
    .map(row => row.split(',').map(cell => cell.trim().replace(/^"|"$/g, '')));

  const headers = rows.shift() || [];
  return rows.map(values => headers.reduce((record, key, index) => ({
    ...record,
    [key]: values[index] || ''
  }), {}));
};

/**
 * @function escapeCrmCsvCell
 * @description Escapes a value for CSV export.
 * @param {unknown} value - Cell value.
 * @returns {string} CSV cell.
 * @collaboration Keeps CRM exports portable.
 */
const escapeCrmCsvCell = (value = '') => {
  const raw = value === null || value === undefined ? '' : String(value);
  return /[",\n\r]/.test(raw) ? `"${raw.replace(/"/g, '""')}"` : raw;
};

/**
 * @function downloadCrmCsv
 * @description Downloads CRM rows as CSV.
 * @param {Array<object>} rows - Rows to export.
 * @param {string} fileName - File name without extension.
 * @returns {void}
 * @collaboration Gives CRM portable evidence without changing source records.
 */
const downloadCrmCsv = (rows = [], fileName = 'wilsy-crm-export') => {
  const fields = Array.from(rows.reduce((set, row) => {
    Object.keys(row || {}).forEach(key => set.add(key));
    return set;
  }, new Set(['id', 'name', 'status', 'sourceStatus'])));

  const csv = [
    fields.join(','),
    ...rows.map(row => fields.map(field => escapeCrmCsvCell(row?.[field])).join(','))
  ].join('\n');

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `${fileName}.csv`;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
};

/**
 * @function normalizeCrmEnvelope
 * @description Normalizes CRM service envelopes.
 * @param {unknown} payload - Service payload.
 * @returns {{items:Array<object>,total:number,sourceStatus:string,raw:unknown}} Normalized envelope.
 * @collaboration Lets CRM read multiple backend envelope formats without fabricating records.
 */
const normalizeCrmEnvelope = (payload = {}) => {
  const source = payload?.data || payload?.result || payload?.summary || payload || {};
  const items = Array.isArray(payload)
    ? payload
    : (source.items || source.records || source.rows || source.data || []);
  const list = Array.isArray(items) ? items : [];

  return {
    items: list.map((item, index) => ({
      ...item,
      id: item?.id || item?._id || item?.recordId || item?.sourceId || `CRM_ROW_${index}`
    })),
    total: Number(source.total ?? source.count ?? list.length ?? 0),
    sourceStatus: source.sourceStatus || source.status || (list.length ? 'SOURCE_LIVE' : 'SOURCE_REQUIRED'),
    raw: payload
  };
};

/**
 * @function buildCrmMethodNames
 * @description Builds candidate CRM service method names for a module action.
 * @param {string} action - Action name.
 * @param {object} moduleConfig - CRM module config.
 * @returns {Array<string>} Candidate service names.
 * @collaboration Keeps CRM tied to existing services while allowing route growth.
 */
const buildCrmMethodNames = (action = 'get', moduleConfig = {}) => {
  const singular = moduleConfig.singular || titleizeCrmText(moduleConfig.id);
  const plural = titleizeCrmText(moduleConfig.id).replace(/\s+/g, '');
  const singularName = singular.replace(/\s+/g, '');

  if (action === 'get') return [`get${plural}`, `get${singularName}s`, 'getCrmRecords', 'getRecords'];
  if (action === 'create') return [`create${singularName}`, 'createCrmRecord', 'createRecord'];
  if (action === 'update') return [`update${singularName}`, 'updateCrmRecord', 'updateRecord'];
  if (action === 'delete') return [`delete${singularName}`, 'deleteCrmRecord', 'deleteRecord'];
  return [];
};

/**
 * @function callCrmServiceMethod
 * @description Attempts CRM service methods with supported argument signatures.
 * @param {Array<string>} methodNames - Candidate method names.
 * @param {Array<Array<unknown>>} argumentSets - Candidate argument sets.
 * @returns {Promise<unknown>} Service response.
 * @collaboration Uses real connector routes only and surfaces route gaps as source required.
 */
const callCrmServiceMethod = async (methodNames = [], argumentSets = []) => {
  let lastError = null;

  for (const name of methodNames) {
    const fn = crmService?.[name];
    if (typeof fn !== 'function') continue;

    for (const args of argumentSets) {
      try {
        return await fn(...args);
      } catch (error) {
        lastError = error;
      }
    }
  }

  if (lastError) throw lastError;
  return null;
};

/**
 * @function buildCrmReceiptHash
 * @description Builds a browser-safe deterministic receipt hash.
 * @param {object} payload - Receipt payload.
 * @returns {string} Receipt hash.
 * @collaboration Gives CRM visible command receipts without exposing secrets.
 */
const buildCrmReceiptHash = (payload = {}) => {
  const raw = JSON.stringify(payload, Object.keys(payload || {}).sort());
  let hash = 0x811c9dc5;
  for (let index = 0; index < raw.length; index += 1) {
    hash ^= raw.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return `CRM-${(hash >>> 0).toString(16).toUpperCase().padStart(8, '0')}`;
};

/**
 * @function buildCrmReadiness
 * @description Calculates CRM readiness from live source and record posture.
 * @param {object} params - Readiness inputs.
 * @returns {{score:number,posture:string,liveSources:number,totalSources:number}} Readiness packet.
 * @collaboration Makes readiness measurable without inventing verified data.
 */
const buildCrmReadiness = ({ collections = {}, sourceState = {} } = {}) => {
  const totalSources = CRM_MODULES.length;
  const liveSources = Object.values(sourceState).filter(source => (
    ['SOURCE_LIVE', 'LIVE', 'SOURCE_READY'].includes(String(source?.status || '').toUpperCase())
  )).length;
  const totalRecords = Object.values(collections).reduce((sum, envelope) => (
    sum + Number(envelope?.total || envelope?.items?.length || 0)
  ), 0);
  const catalogReady = Boolean(WILSY_CRM_CATALOG_READINESS?.ok);
  const commandReady = Boolean(WILSY_CRM_COMMAND_CLIENT_HEALTH?.ok);
  const liveRouteCount = Number(WILSY_CRM_CATALOG_READINESS?.liveRoutes || 0);
  const plannedRouteCount = Number(WILSY_CRM_CATALOG_READINESS?.plannedRoutes || 0);

  const score = Math.min(100, Math.round(
    (liveSources / Math.max(totalSources, 1)) * 54
    + (totalRecords > 0 ? 18 : 4)
    + (catalogReady ? 12 : 0)
    + (commandReady ? 10 : 0)
    + (liveRouteCount > 0 ? 6 : 0)
  ));

  return {
    score,
    posture: score >= 80 ? 'CRM_OS_READY_FOR_REVENUE_COMMAND' : score >= 55 ? 'CRM_OS_SOURCE_REPAIR_ACTIVE' : 'CRM_OS_SOURCE_ROUTES_REQUIRED',
    liveSources,
    totalSources,
    totalRecords,
    liveRouteCount,
    plannedRouteCount,
    catalogReady,
    commandReady,
    catalogVersion: WILSY_CRM_MODULE_CATALOG_VERSION,
    commandClientVersion: WILSY_CRM_COMMAND_CLIENT_VERSION,
    noFakeData: true
  };
};

/**
 * @function buildCrmAiMemo
 * @description Builds a Wilsy AI CRM memo from real source posture and visible records.
 * @param {object} params - Memo inputs.
 * @returns {{headline:string,detail:string,next:string}} Memo packet.
 * @collaboration Makes Wilsy AI a command engine layer without claiming model output or fake data.
 */
const buildCrmAiMemo = ({ readiness, activeModule, collections, evidenceTotal } = {}) => {
  const totalRecords = Object.values(collections || {}).reduce((sum, envelope) => (
    sum + Number(envelope?.total || envelope?.items?.length || 0)
  ), 0);

  if (readiness.score < 55) {
    return {
      headline: 'Repair source routes, then refresh the customer graph.',
      detail: `${readiness.liveSources}/${readiness.totalSources} CRM source rails are live. ${totalRecords} records are visible. Evidence rows: ${evidenceTotal}.`,
      next: 'Run Live Sync and inspect Source Registry evidence.'
    };
  }

  return {
    headline: 'Customer command graph is ready for action.',
    detail: `${totalRecords} CRM records are active across ${readiness.liveSources} live source rails. Active module: ${titleizeCrmText(activeModule)}.`,
    next: 'Open Pipeline, Evidence or AI to move customer work forward.'
  };
};

/**
 * @function getCrmDisplayValue
 * @description Extracts and formats a CRM field for display.
 * @param {object} row - CRM row.
 * @param {string} field - Field key.
 * @returns {string} Display value.
 * @collaboration Keeps missing CRM values marked as source required.
 */
const getCrmDisplayValue = (row = {}, field = '') => {
  const value = row?.[field];
  if (value === null || value === undefined || value === '') return 'SOURCE REQUIRED';
  if (['amount', 'annualRevenue', 'budget', 'value'].includes(field)) return formatCrmMoney(value);
  if (['probability', 'score', 'percentComplete'].includes(field)) return `${numericCrmValue(value)}%`;
  if (['closingDate', 'completedAt', 'dueDate', 'effectiveDate', 'scheduledAt', 'startsAt', 'validUntil', 'verifiedAt'].includes(field)) return formatCrmDate(value);
  return String(value);
};

/**
 * @function buildDefaultCrmDraft
 * @description Builds a draft record for the active CRM module.
 * @param {object} moduleConfig - Module config.
 * @returns {object} Draft record.
 * @collaboration Creates form state without fabricating persisted records.
 */
const buildDefaultCrmDraft = (moduleConfig = {}) => (
  (moduleConfig.fields || []).reduce((draft, field) => ({
    ...draft,
    [field]: FIELD_TYPES[field] === 'number' ? 0 : ''
  }), {
    sourceSystem: 'WILSY_OS_CRM',
    sourceStatus: 'SOURCE_PENDING'
  })
);

/**
 * @function CRMDashboard
 * @description Renders the clean Wilsy OS CRM command center.
 * @param {object} props - Component props.
 * @returns {React.ReactElement} CRM dashboard.
 * @collaboration Implements ExecutiveDashboard parity with a clean CRM operating shell and real service routes.
 */
/**
 * @function buildCrmLiveStatusLabel
 * @description Builds a truthful CRM status label from live readiness, sync and source inventory state.
 * @param {Object} params - CRM status inputs.
 * @returns {string} Human readable live CRM status label.
 * @collaboration Removes fake placeholder copy while keeping the dashboard honest when source routes are not connected.
 */
const buildCrmLiveStatusLabel = ({
  readiness = {},
  isRefreshing = false,
  error = null,
  lastUpdated = null
} = {}) => {
  const liveSources = Number(readiness.liveSources || 0);
  const totalSources = Number(readiness.totalSources || 0);
  const score = Number(readiness.score || 0);
  const posture = String(readiness.posture || '').replace(/_/g, ' ').toLowerCase();

  if (isRefreshing) return 'Syncing live CRM source graph';
  if (error) return 'Live CRM sync needs attention';
  if (liveSources > 0 && totalSources > 0) {
    return `${liveSources}/${totalSources} live sources // ${score}% readiness`;
  }
  if (totalSources > 0) {
    return `No connected live CRM sources // ${totalSources} routes checked`;
  }
  if (lastUpdated) return `CRM source inventory empty // last checked ${lastUpdated}`;
  if (posture) return `CRM source inventory empty // ${posture}`;
  return 'CRM source inventory empty';
};

/**
 * @function CRMDashboard
 * @description Renders the Wilsy OS CRM command surface with tenant branding, live CRM readiness, customer records, source posture, module navigation and command-center controls.
 * @returns {React.ReactElement} Wilsy OS CRM dashboard.
 * @collaboration Keeps the CRM dashboard guard-compliant while preserving the existing Executive Account Command Center integration path.
 */
const CRMDashboard = ({
  tenantId,
  activeTenant = {},
  tenantConfig = {},
  user = {},
  founderReturnEnabled = false,
  onFounderReturn,
  executeCommand
}) => {
  const importInputRef = useRef(null);
  const currentTenantId = tenantId || activeTenant?.tenantId || activeTenant?.id || activeTenant?._id || user?.tenantId || DEFAULT_TENANT_ID;

  const [activeWorkspace, setActiveWorkspace] = useState('home');
  const [sideRailOpen, setSideRailOpen] = useState(true);
  const [activeModule, setActiveModule] = useState('leads');
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('table');
  const [collections, setCollections] = useState(() => CRM_MODULES.reduce((all, moduleConfig) => ({
    ...all,
    [moduleConfig.id]: { items: [], total: 0, sourceStatus: 'SOURCE_REQUIRED' }
  }), {}));
  const [sourceState, setSourceState] = useState({});
  const [pageState, setPageState] = useState(() => CRM_MODULES.reduce((all, moduleConfig) => ({
    ...all,
    [moduleConfig.id]: { limit: DEFAULT_PAGE_LIMIT, offset: 0 }
  }), {}));
  const [commandCenter, setCommandCenter] = useState({});
  const [sourceRegistryEvidence, setSourceRegistryEvidence] = useState({ items: [], total: 0, sourceStatus: 'SOURCE_REQUIRED' });
  const [receipts, setReceipts] = useState([]);
  const [importVendor, setImportVendor] = useState('GENERIC_CRM');
  const [importReport, setImportReport] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [recordDraft, setRecordDraft] = useState({});
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [sourceFilter, setSourceFilter] = useState('ALL');
  const [boardFilter, setBoardFilter] = useState('ALL');
  const [themePreference, setThemePreference] = useState(() => readWilsyCrmThemePreference());
  const [accountSettingsOpen, setAccountSettingsOpen] = useState(false);

  /**
   * @function resolveInitialCrmAccountThemeId
   * @description Resolves the CRM Account Command Center theme id from local runtime storage.
   * @returns {string} Initial CRM account theme id.
   * @collaboration Prevents Account Command Center theme runtime references from crashing before the first render.
   */
  const resolveInitialCrmAccountThemeId = () => {
    if (typeof window === 'undefined') return 'sovereign_black';

    try {
      return (
        window.localStorage.getItem('wilsy:crm:theme')
        || window.localStorage.getItem('wilsy:account-command-center:theme')
        || window.localStorage.getItem('wilsy:dashboard-chrome:theme')
        || 'sovereign_black'
      );
    } catch (storageError) {
      return 'sovereign_black';
    }
  };

  /**
   * @function resolveInitialCrmAccountThemeMode
   * @description Resolves the CRM Account Command Center mode from local runtime storage.
   * @returns {string} Initial CRM account theme mode.
   * @collaboration Keeps CRM boot safe while the Account Command Center takes theme authority.
   */
  const resolveInitialCrmAccountThemeMode = () => {
    if (typeof window === 'undefined') return 'night';

    try {
      return (
        window.localStorage.getItem('wilsy:crm:mode')
        || window.localStorage.getItem('wilsy:account-command-center:mode')
        || window.localStorage.getItem('wilsy:dashboard-chrome:mode')
        || 'night'
      );
    } catch (storageError) {
      return 'night';
    }
  };

  const [accountThemeId, setAccountThemeId] = useState(() => String(resolveInitialCrmAccountThemeId() || 'sovereign_black').trim() || 'sovereign_black');
  const [accountThemeMode, setAccountThemeMode] = useState(() => ['day', 'night', 'auto'].includes(String(resolveInitialCrmAccountThemeMode() || 'night').toLowerCase()) ? String(resolveInitialCrmAccountThemeMode() || 'night').toLowerCase() : 'night');
  const [founderReturnOpen, setFounderReturnOpen] = useState(false);
  const [commandCentreOpen, setCommandCentreOpen] = useState(false);
  const [commandCentrePinned, setCommandCentrePinned] = useState(false);

  const crmThemeVars = useMemo(() => (
    buildWilsyCrmThemeVars(themePreference.themeId, themePreference.mode)
  ), [themePreference]);

  const tenantIdentity = useMemo(() => (
    buildCrmTenantIdentity({ tenantId: currentTenantId, activeTenant, tenantConfig, user })
  ), [activeTenant, currentTenantId, tenantConfig, user]);

  const moduleConfig = useMemo(() => (
    resolveCrmCatalogModuleConfig(activeModule)
  ), [activeModule]);

  const currentCollection = collections[activeModule] || { items: [], total: 0, sourceStatus: 'SOURCE_REQUIRED' };

  const readiness = useMemo(() => (
    buildCrmReadiness({ collections, sourceState })
  ), [collections, sourceState]);

  const pipelineValue = useMemo(() => (
    (collections.deals?.items || []).reduce((sum, deal) => (
      sum + numericCrmValue(deal.value || deal.amount) * (numericCrmValue(deal.probability) / 100)
    ), 0)
  ), [collections.deals]);

  const evidenceTotal = Number(sourceRegistryEvidence?.total || sourceRegistryEvidence?.items?.length || 0);

  const aiMemo = useMemo(() => (
    buildCrmAiMemo({ readiness, activeModule, collections, evidenceTotal })
  ), [activeModule, collections, evidenceTotal, readiness]);

  const visibleRows = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase();
    return (currentCollection.items || []).filter(row => {
      if (needle && !JSON.stringify(row).toLowerCase().includes(needle)) return false;
      if (sourceFilter !== 'ALL' && String(row.sourceStatus || row.sourcePosture || '').toUpperCase() !== sourceFilter) return false;
      if (boardFilter !== 'ALL' && String(row.boardStatus || '').toUpperCase() !== boardFilter) return false;
      return true;
    });
  }, [boardFilter, currentCollection.items, searchTerm, sourceFilter]);

  const tableFields = useMemo(() => (
    Array.from(new Set([moduleConfig.primary, moduleConfig.secondary, ...(moduleConfig.fields || []).slice(0, 4)]))
      .filter(Boolean)
      .slice(0, 6)
  ), [moduleConfig]);

  const addReceipt = useCallback((eventType, message, payload = {}) => {
    const receipt = {
      id: `${eventType}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`,
      eventType,
      message,
      timestamp: new Date().toISOString(),
      proofHash: buildCrmReceiptHash({
        eventType,
        message,
        payload,
        tenantId: currentTenantId,
        version: CRM_VERSION
      })
    };

    setReceipts(previous => [receipt, ...previous].slice(0, MAX_RECEIPTS));
    return receipt;
  }, [currentTenantId]);

  const updateSource = useCallback((moduleId, status, message = '') => {
    setSourceState(previous => ({
      ...previous,
      [moduleId]: {
        status,
        message: message || compactCrmSignal(status),
        updatedAt: new Date().toISOString()
      }
    }));
  }, []);

  const loadModuleRecords = useCallback(async (moduleId = activeModule, nextPage = pageState[moduleId]) => {
    const config = resolveCrmCatalogModuleConfig(moduleId, moduleConfig?.id);
    const page = nextPage || { limit: DEFAULT_PAGE_LIMIT, offset: 0 };

    try {
      const commandEnvelope = await listWilsyCrmRecords(config.id, {
        tenantId: currentTenantId,
        limit: page.limit || DEFAULT_PAGE_LIMIT,
        offset: page.offset || 0,
        search: searchTerm,
        sourceStatus: sourceFilter !== 'ALL' ? sourceFilter : undefined
      });

      const normalizedCommandEnvelope = normalizeCrmEnvelope(commandEnvelope);

      if (
        commandEnvelope?.sourceStatus === 'SOURCE_LIVE'
        || commandEnvelope?.routePosture !== 'ROUTE_REQUIRED'
        || normalizedCommandEnvelope.items.length > 0
      ) {
        setCollections(previous => ({
          ...previous,
          [moduleId]: normalizedCommandEnvelope
        }));
        updateSource(moduleId, commandEnvelope?.sourceStatus || normalizedCommandEnvelope.sourceStatus || 'SOURCE_REQUIRED', `${config.label} command client hydrated`);
        return;
      }

      const methodNames = buildCrmMethodNames('get', config);
      const argumentSets = [
        [currentTenantId, page],
        [config.route, currentTenantId, page],
        [config.id, currentTenantId, page],
        [config.id, page, currentTenantId],
        [{ tenantId: currentTenantId, resourceType: config.id, ...page }]
      ];

      const legacyResponse = await callCrmServiceMethod(methodNames, argumentSets);
      if (!legacyResponse) {
        updateSource(moduleId, 'SOURCE_REQUIRED', `${config.label} command route required`);
        setCollections(previous => ({
          ...previous,
          [moduleId]: {
            items: [],
            total: 0,
            sourceStatus: 'SOURCE_REQUIRED',
            routePosture: config.routePosture || 'ROUTE_REQUIRED',
            moduleEnvelope: buildWilsyCrmModuleEnvelope(config.id, { tenantId: currentTenantId })
          }
        }));
        return;
      }

      const envelope = normalizeCrmEnvelope(legacyResponse);
      setCollections(previous => ({
        ...previous,
        [moduleId]: envelope
      }));
      updateSource(moduleId, envelope.sourceStatus || 'SOURCE_LIVE', `${config.label} legacy service hydrated`);
    } catch (error) {
      updateSource(moduleId, 'SOURCE_ERROR', error?.message || `${config.label} source failed`);
      setCollections(previous => ({
        ...previous,
        [moduleId]: {
          ...(previous[moduleId] || {}),
          sourceStatus: 'SOURCE_ERROR',
          error: error?.message || 'Source error'
        }
      }));
    }
  }, [activeModule, currentTenantId, moduleConfig, pageState, searchTerm, sourceFilter, updateSource]);

  const loadCommandCenter = useCallback(async () => {
    try {
      const commandEnvelope = await getWilsyCrmCommandCenter({
        tenantId: currentTenantId,
        limit: 50
      });

      if (commandEnvelope?.ok || commandEnvelope?.sourceStatus !== 'SOURCE_ERROR') {
        setCommandCenter({
          ...(commandEnvelope.raw?.data || commandEnvelope.raw || {}),
          sourceStatus: commandEnvelope.sourceStatus || 'SOURCE_REQUIRED',
          commandClientVersion: WILSY_CRM_COMMAND_CLIENT_VERSION,
          catalogVersion: WILSY_CRM_MODULE_CATALOG_VERSION,
          noFakeData: true
        });
        return;
      }

      if (typeof crmService.getCrmCommandCenter !== 'function') {
        setCommandCenter({ sourceStatus: 'SOURCE_REQUIRED', commandClientVersion: WILSY_CRM_COMMAND_CLIENT_VERSION });
        return;
      }

      const envelope = normalizeCrmEnvelope(await crmService.getCrmCommandCenter(currentTenantId));
      setCommandCenter(envelope.raw?.data || envelope.raw || { sourceStatus: envelope.sourceStatus });
    } catch (error) {
      setCommandCenter({ sourceStatus: 'SOURCE_ERROR', error: error?.message });
    }
  }, [currentTenantId]);

  const loadEvidence = useCallback(async () => {
    try {
      const commandEnvelope = await getWilsyCrmSourceRegistryEvidence({
        tenantId: currentTenantId,
        limit: 25
      });

      if (commandEnvelope?.ok || commandEnvelope?.sourceStatus !== 'SOURCE_ERROR') {
        setSourceRegistryEvidence(commandEnvelope);
        return;
      }

      if (typeof crmService.getCrmSourceRegistryEvidence !== 'function') {
        setSourceRegistryEvidence({ items: [], total: 0, sourceStatus: 'SOURCE_REQUIRED' });
        return;
      }

      const envelope = normalizeCrmEnvelope(await crmService.getCrmSourceRegistryEvidence(currentTenantId, { limit: 20 }));
      setSourceRegistryEvidence(envelope);
    } catch (error) {
      setSourceRegistryEvidence({ items: [], total: 0, sourceStatus: 'SOURCE_ERROR', error: error?.message });
    }
  }, [currentTenantId]);

  const loadAllData = useCallback(async () => {
    setIsRefreshing(true);
    await Promise.allSettled([
      loadCommandCenter(),
      loadEvidence(),
      loadModuleRecords(activeModule, pageState[activeModule])
    ]);
    addReceipt('CRM_LIVE_SYNC', `CRM refreshed for ${tenantIdentity.displayName}`, { activeModule, receiptId: `CRM_LIVE_SYNC_${activeModule}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}` });
    setIsRefreshing(false);
  }, [activeModule, addReceipt, loadCommandCenter, loadEvidence, loadModuleRecords, pageState, tenantIdentity.displayName]);
  /**
   * @function openWilsyAccountSettings
   * @description Opens the Wilsy OS reusable account settings surface through the global operating event bridge.
   * @returns {void}
   * @collaboration Gives CRM the same Account command path used by the wider Wilsy OS shell without rendering a blank CRM modal.
   */
  const openWilsyAccountSettings = () => {
    setAccountSettingsOpen(true);
  };



  const openCreateRecord = useCallback(() => {
    setEditingRecord(null);
    setRecordDraft(buildDefaultCrmDraft(moduleConfig));
    setModalOpen(true);
  }, [moduleConfig]);

  const openEditRecord = useCallback((record = {}) => {
    setEditingRecord(record);
    setRecordDraft({ ...record });
    setModalOpen(true);
  }, []);

  const saveRecord = useCallback(async () => {
    const action = editingRecord ? 'update' : 'create';
    const methodNames = buildCrmMethodNames(action, moduleConfig);
    const id = editingRecord?.id || editingRecord?._id || recordDraft.id;
    const argumentSets = action === 'create'
      ? [
        [currentTenantId, recordDraft],
        [moduleConfig.route, currentTenantId, recordDraft],
        [moduleConfig.id, currentTenantId, recordDraft],
        [recordDraft, currentTenantId]
      ]
      : [
        [id, recordDraft, currentTenantId],
        [currentTenantId, id, recordDraft],
        [moduleConfig.route, id, recordDraft, currentTenantId],
        [moduleConfig.id, id, recordDraft, currentTenantId]
      ];

    setIsRefreshing(true);
    try {
      const response = await callCrmServiceMethod(methodNames, argumentSets);
      if (!response) {
        addReceipt('CRM_ROUTE_REQUIRED', `${moduleConfig.singular} ${action} route required`, { activeModule, action });
        setIsRefreshing(false);
        return;
      }

      addReceipt(`CRM_${action.toUpperCase()}`, `${moduleConfig.singular} ${action} committed`, { activeModule });
      setModalOpen(false);
      setEditingRecord(null);
      await loadModuleRecords(activeModule, pageState[activeModule]);
    } catch (error) {
      addReceipt('CRM_MUTATION_ERROR', error?.message || `${moduleConfig.singular} save failed`, { activeModule, action });
    }
    setIsRefreshing(false);
  }, [activeModule, addReceipt, currentTenantId, editingRecord, loadModuleRecords, moduleConfig, pageState, recordDraft]);

  const deleteRecord = useCallback(async (record = {}) => {
    const id = record?.id || record?._id;
    if (!id) return;

    const confirmed = window.confirm(`Delete ${moduleConfig.singular}?`);
    if (!confirmed) return;

    setIsRefreshing(true);
    try {
      const response = await callCrmServiceMethod(buildCrmMethodNames('delete', moduleConfig), [
        [id, currentTenantId],
        [currentTenantId, id],
        [moduleConfig.route, id, currentTenantId],
        [moduleConfig.id, id, currentTenantId]
      ]);

      if (!response) {
        addReceipt('CRM_DELETE_ROUTE_REQUIRED', `${moduleConfig.singular} delete route required`, { activeModule, id });
        setIsRefreshing(false);
        return;
      }

      addReceipt('CRM_DELETE', `${moduleConfig.singular} deleted`, { activeModule, id });
      await loadModuleRecords(activeModule, pageState[activeModule]);
    } catch (error) {
      addReceipt('CRM_DELETE_ERROR', error?.message || `${moduleConfig.singular} delete failed`, { activeModule, id });
    }
    setIsRefreshing(false);
  }, [activeModule, addReceipt, currentTenantId, loadModuleRecords, moduleConfig, pageState]);

  const exportCurrentModule = useCallback(async () => {
    try {
      const exportEnvelope = await exportWilsyCrmRecords(activeModule, {
        tenantId: currentTenantId,
        filters: { sourceFilter, boardFilter, searchTerm },
        format: 'csv'
      });

      if (exportEnvelope?.ok && exportEnvelope?.raw?.downloadUrl) {
        window.open(exportEnvelope.raw.downloadUrl, '_blank', 'noopener,noreferrer');
      } else {
        downloadCrmCsv(visibleRows, `wilsy_crm_${activeModule}_${Date.now()}`);
      }

      addReceipt('CRM_EXPORT', `${visibleRows.length} ${moduleConfig.label} rows exported`, {
        activeModule,
        routePosture: exportEnvelope?.routePosture || 'ROUTE_REQUIRED',
        sourceStatus: exportEnvelope?.sourceStatus || 'SOURCE_REQUIRED'
      });
    } catch (error) {
      downloadCrmCsv(visibleRows, `wilsy_crm_${activeModule}_${Date.now()}`);
      addReceipt('CRM_EXPORT_LOCAL_FALLBACK', `${visibleRows.length} ${moduleConfig.label} rows exported locally`, { activeModule });
    }
  }, [activeModule, addReceipt, boardFilter, currentTenantId, moduleConfig.label, searchTerm, sourceFilter, visibleRows]);

  const importFile = useCallback(async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsRefreshing(true);
    try {
      const text = await file.text();
      const parsed = file.name.toLowerCase().endsWith('.json')
        ? safeParseCrmJson(text)
        : parseCrmCsv(text);
      const records = Array.isArray(parsed) ? parsed : parsed?.records;

      if (!Array.isArray(records) || records.length === 0) {
        setImportReport({ status: 'SOURCE_REQUIRED', message: 'Import file had no records.' });
        setIsRefreshing(false);
        event.target.value = '';
        return;
      }

      if (typeof crmService.previewImportRecords !== 'function' || typeof crmService.importRecords !== 'function') {
        setImportReport({ status: 'ROUTE_REQUIRED', message: 'CRM import routes are required before records enter Wilsy OS.' });
        addReceipt('CRM_IMPORT_ROUTE_REQUIRED', 'Import route required', { activeModule, count: records.length });
        setIsRefreshing(false);
        event.target.value = '';
        return;
      }

      await crmService.previewImportRecords(activeModule, currentTenantId, records, {
        dedupeKey: activeModule === 'leads' || activeModule === 'contacts' ? 'email' : 'name',
        sourceSystem: importVendor
      });

      const report = await crmService.importRecords(activeModule, currentTenantId, records, {
        mode: 'upsert',
        dedupeKey: activeModule === 'leads' || activeModule === 'contacts' ? 'email' : 'name',
        sourceSystem: importVendor
      });

      setImportReport({ status: 'IMPORTED', message: `${records.length} records processed`, report });
      addReceipt('CRM_IMPORT', `${records.length} ${moduleConfig.label} records imported`, { activeModule, importVendor });
      await loadModuleRecords(activeModule, pageState[activeModule]);
    } catch (error) {
      setImportReport({ status: 'ERROR', message: error?.message || 'Import failed' });
      addReceipt('CRM_IMPORT_ERROR', error?.message || 'Import failed', { activeModule });
    }

    event.target.value = '';
    setIsRefreshing(false);
  }, [activeModule, addReceipt, currentTenantId, importVendor, loadModuleRecords, moduleConfig.label, pageState]);

  const routeArtifactCommand = useCallback((target = 'artifacts') => {
    const packet = {
      tenantId: currentTenantId,
      source: 'CRMDashboard',
      target,
      activeModule,
      proofHash: buildCrmReceiptHash({ target, activeModule, currentTenantId, version: CRM_VERSION })
    };

    window.dispatchEvent(new CustomEvent('wilsy:artifact-command', { detail: packet }));
    window.dispatchEvent(new CustomEvent('wilsy:navigate-dashboard', {
      detail: {
        dashboardKey: target === 'documents' ? 'DOCUMENTS_DASHBOARD' : 'ARTIFACTS_DASHBOARD',
        source: 'CRMDashboard',
        tenantId: currentTenantId
      }
    }));

    if (typeof executeCommand === 'function') {
      executeCommand('CRM_ARTIFACT_ROUTE', target, 'POST', packet).catch(() => null);
    }

    addReceipt('CRM_ARTIFACT_ROUTE', `Routed ${target}`, packet);
  }, [activeModule, addReceipt, currentTenantId, executeCommand]);

  useEffect(() => {
    // WILSY_CRM_OS_THEME_RUNTIME_SUBSCRIBER_STEP_R4A
    let unsubscribeWilsyCrmThemeRuntime = null
    let isWilsyCrmThemeRuntimeMounted = true

    if (typeof document !== 'undefined') {
      document.documentElement.dataset.wilsyCrmDashboardLive = 'true'
      document.body.dataset.wilsyCrmDashboardLive = 'true'
    }

    /**
     * @function synchronizeWilsyCrmThemeRuntime
     * @description Commits the shared Wilsy OS theme runtime packet so CRM repaints beyond the Account Command Center.
     * @param {Object} detail - Runtime theme detail emitted by the Account Command Center or persisted storage.
     * @returns {void}
     * @collaboration Makes CRM consume the same OS theme bus as Account, Executive and future tenant dashboards.
     */
    const synchronizeWilsyCrmThemeRuntime = detail => {
      import('../account/wilsyAccountThemeTokens').then(themeRuntime => {
        if (!isWilsyCrmThemeRuntimeMounted) return

        themeRuntime.commitWilsyThemeRuntime(
          {
            themeId: detail?.themeId,
            mode: detail?.mode,
            source: 'CRMDashboard.themeRuntimeSubscriber'
          },
          {
            dispatch: false,
            source: 'CRMDashboard.themeRuntimeSubscriber'
          }
        )
      }).catch(error => {
        console.warn('[WILSY-CRM-THEME-RUNTIME-SKIPPED]', error.message)
      })
    }

    /**
     * @function bootstrapWilsyCrmThemeRuntime
     * @description Loads the persisted Wilsy OS theme runtime on CRM mount and subscribes to future changes.
     * @returns {Promise<void>} Theme runtime bootstrap result.
     * @collaboration Ensures CRM opens already themed before the Account Command Center is opened.
     */
    const bootstrapWilsyCrmThemeRuntime = async () => {
      try {
        const themeRuntime = await import('../account/wilsyAccountThemeTokens')
        if (!isWilsyCrmThemeRuntimeMounted) return

        const storedRuntime = themeRuntime.readStoredWilsyThemeRuntime({
          themeId: 'wilsy_aurora',
          mode: 'night'
        })

        themeRuntime.commitWilsyThemeRuntime(
          {
            ...storedRuntime,
            source: 'CRMDashboard.themeRuntimeBootstrap'
          },
          {
            dispatch: false,
            source: 'CRMDashboard.themeRuntimeBootstrap'
          }
        )

        unsubscribeWilsyCrmThemeRuntime = themeRuntime.subscribeWilsyThemeRuntime(synchronizeWilsyCrmThemeRuntime)
      } catch (error) {
        console.warn('[WILSY-CRM-THEME-RUNTIME-BOOTSTRAP-SKIPPED]', error.message)
      }
    }

    bootstrapWilsyCrmThemeRuntime()

    return () => {
      isWilsyCrmThemeRuntimeMounted = false
      if (typeof unsubscribeWilsyCrmThemeRuntime === 'function') {
        unsubscribeWilsyCrmThemeRuntime()
      }

      if (typeof document !== 'undefined') {
        delete document.documentElement.dataset.wilsyCrmDashboardLive
        delete document.body.dataset.wilsyCrmDashboardLive
      }
    }
  }, [])

  useEffect(() => {
    const preference = readWilsyCrmThemePreference();
    setThemePreference(preference);
    applyWilsyCrmThemeToDocument(preference.themeId, preference.mode);

    /**
     * @function syncWilsyCrmThemeRuntime
     * @description Syncs CRM theme from Account Command Center events.
     * @returns {void}
     * @collaboration Keeps CRM live with the same theme runtime used by ExecutiveDashboard.
     */
    const syncWilsyCrmThemeRuntime = () => {
      const next = readWilsyCrmThemePreference();
      setThemePreference(next);
      applyWilsyCrmThemeToDocument(next.themeId, next.mode);
    };

    window.addEventListener('wilsy:theme-change', syncWilsyCrmThemeRuntime);
    window.addEventListener('storage', syncWilsyCrmThemeRuntime);

    return () => {
      window.removeEventListener('wilsy:theme-change', syncWilsyCrmThemeRuntime);
      window.removeEventListener('storage', syncWilsyCrmThemeRuntime);
      if (document.body.dataset.wilsyActiveDashboard === 'crm') {
        delete document.body.dataset.wilsyActiveDashboard;
      }
    };
  }, []);

  useEffect(() => {
    loadAllData();
  }, [currentTenantId]);

  useEffect(() => {
    loadModuleRecords(activeModule, pageState[activeModule]);
  }, [activeModule]);

  const sourceLabel = compactCrmSignal(currentCollection.sourceStatus || sourceState[activeModule]?.status || 'SOURCE_REQUIRED');
  const ActiveWorkspaceIcon = CRM_WORKSPACES.find(workspace => workspace.id === activeWorkspace)?.icon || Home;

  const moduleCards = CRM_MODULES.map(item => {
    const Icon = resolveCrmCatalogIcon(item?.icon, Database);
    const active = item.id === activeModule;
    return (
      <button
        key={item.id}
        type="button"
        className={active ? styles.moduleButtonActive : styles.moduleButton}
        onClick={() => {
          setActiveModule(item.id);
          setActiveWorkspace('records');
        }}
      >
        <Icon size={16} />
        <span>{item.label}</span>
        <em>{collections[item.id]?.total || 0}</em>
        <small>{compactCrmSignal(collections[item.id]?.sourceStatus || item.routePosture || 'SOURCE_REQUIRED')}</small>
      </button>
    );
  });

  const workspaceButtons = CRM_WORKSPACES.map(workspace => {
    const Icon = workspace.icon;
    const active = workspace.id === activeWorkspace;
    return (
      <button
        key={workspace.id}
        type="button"
        className={active ? styles.workspaceButtonActive : styles.workspaceButton}
        onClick={() => setActiveWorkspace(workspace.id)}
      >
        <Icon size={16} />
        <span>{workspace.label}</span>
        <small>{workspace.detail}</small>
      </button>
    );
  });

  /**
   * @function homeCards
   * @description Renders the clean CRM home workspace cards from real task, meeting, lead and deal collections.
   * @returns {React.ReactElement} CRM home workspace card grid.
   * @collaboration Keeps the CRM home screen Zoho-clean while preserving Wilsy OS source truth and no fabricated records.
   */
  const homeCards = (
    <div className={styles.homeGrid}>
      <section className={styles.widgetCard}>
        <header>
          <span><CheckCircle size={14} /> My Open Tasks</span>
          <button type="button" onClick={() => setActiveModule('tasks')}>Open</button>
        </header>
        <div className={styles.cleanTableShell}>
          <table>
            <thead><tr><th>Subject</th><th>Due Date</th><th>Status</th></tr></thead>
            <tbody>
              {(collections.tasks?.items || []).slice(0, 5).map(task => (
                <tr key={task.id}><td>{getCrmDisplayValue(task, 'subject')}</td><td>{getCrmDisplayValue(task, 'dueDate')}</td><td>{getCrmDisplayValue(task, 'status')}</td></tr>
              ))}
              {(collections.tasks?.items || []).length === 0 && <tr><td colSpan="3">No tasks found.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      <section className={styles.widgetCard}>
        <header>
          <span><Calendar size={14} /> My Meetings</span>
          <button type="button" onClick={() => setActiveModule('meetings')}>Open</button>
        </header>
        <div className={styles.cleanTableShell}>
          <table>
            <thead><tr><th>Title</th><th>From</th><th>Status</th></tr></thead>
            <tbody>
              {(collections.meetings?.items || []).slice(0, 5).map(meeting => (
                <tr key={meeting.id}><td>{getCrmDisplayValue(meeting, 'subject')}</td><td>{getCrmDisplayValue(meeting, 'startsAt')}</td><td>{getCrmDisplayValue(meeting, 'status')}</td></tr>
              ))}
              {(collections.meetings?.items || []).length === 0 && <tr><td colSpan="3">No meetings found.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      <section className={styles.widgetCard}>
        <header>
          <span><Users size={14} /> Today's Leads</span>
          <button type="button" onClick={() => setActiveModule('leads')}>Open</button>
        </header>
        <div className={styles.cleanTableShell}>
          <table>
            <thead><tr><th>Lead Name</th><th>Company</th><th>Stage</th></tr></thead>
            <tbody>
              {(collections.leads?.items || []).slice(0, 5).map(lead => (
                <tr key={lead.id}><td>{getCrmDisplayValue(lead, 'name')}</td><td>{getCrmDisplayValue(lead, 'company')}</td><td>{getCrmDisplayValue(lead, 'stage')}</td></tr>
              ))}
              {(collections.leads?.items || []).length === 0 && <tr><td colSpan="3">No leads found.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      <section className={styles.widgetCard}>
        <header>
          <span><Target size={14} /> Deals Closing This Month</span>
          <button type="button" onClick={() => setActiveModule('deals')}>Open</button>
        </header>
        <div className={styles.cleanTableShell}>
          <table>
            <thead><tr><th>Deal Name</th><th>Amount</th><th>Stage</th></tr></thead>
            <tbody>
              {(collections.deals?.items || []).slice(0, 5).map(deal => (
                <tr key={deal.id}><td>{getCrmDisplayValue(deal, 'name')}</td><td>{getCrmDisplayValue(deal, 'value')}</td><td>{getCrmDisplayValue(deal, 'stage')}</td></tr>
              ))}
              {(collections.deals?.items || []).length === 0 && <tr><td colSpan="3">No deals found.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );

  /**
   * @function recordsView
   * @description Renders the active CRM module ledger, filters, board mode and table mode.
   * @returns {React.ReactElement} CRM record ledger workspace.
   * @collaboration Gives every CRM module one clean operating ledger without endless scrolling or fake verified data.
   */
  const recordsView = (
    <section className={styles.ledgerCard}>
      <header className={styles.ledgerHeader}>
        <div>
          <span><Database size={14} /> CRM Ledger</span>
          <h3>{moduleConfig.label}</h3>
          <p>{sourceLabel} // {visibleRows.length} visible / {currentCollection.total || 0} total</p>
        </div>
        <div className={styles.ledgerActions}>
          <button type="button" onClick={() => setViewMode(viewMode === 'table' ? 'board' : 'table')}><LayoutGrid size={14} /> {viewMode === 'table' ? 'Board' : 'Table'}</button>
          <button type="button" onClick={() => loadModuleRecords(activeModule, pageState[activeModule])}><RefreshCw size={14} className={isRefreshing ? styles.spin : ''} /> Sync</button>
        </div>
      </header>

      <div className={styles.filterBar}>
        <label>
          <Search size={14} />
          <input value={searchTerm} onChange={event => setSearchTerm(event.target.value)} placeholder={`Search ${moduleConfig.label}`} />
        </label>
        <select value={sourceFilter} onChange={event => setSourceFilter(event.target.value)}>
          <option value="ALL">All source posture</option>
          <option value="SOURCE_LIVE">Source live</option>
          <option value="SOURCE_REQUIRED">Source required</option>
          <option value="SOURCE_ERROR">Source error</option>
        </select>
        <select value={boardFilter} onChange={event => setBoardFilter(event.target.value)}>
          <option value="ALL">All board readiness</option>
          <option value="READY_FOR_BOARDROOM">Board ready</option>
          <option value="NEEDS_EVIDENCE">Needs evidence</option>
          <option value="NEEDS_AUTHORITY">Needs authority</option>
        </select>
      </div>

      {viewMode === 'table' ? (
        <div className={styles.cleanTableShell}>
          <table>
            <thead>
              <tr>
                {tableFields.map(field => <th key={field}>{FIELD_LABELS[field] || titleizeCrmText(field)}</th>)}
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {visibleRows.map(row => (
                <tr key={row.id}>
                  {tableFields.map(field => <td key={field}>{getCrmDisplayValue(row, field)}</td>)}
                  <td>
                    <button type="button" onClick={() => openEditRecord(row)}>Edit</button>
                    <button type="button" onClick={() => deleteRecord(row)}>Delete</button>
                  </td>
                </tr>
              ))}
              {visibleRows.length === 0 && (
                <tr><td colSpan={tableFields.length + 1}>{sourceLabel === 'SOURCE REQUIRED' ? `${moduleConfig.label} route requires live records.` : 'No matching records.'}</td></tr>
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className={styles.boardGrid}>
          {moduleConfig.lanes.map(lane => (
            <section key={lane} className={styles.boardLane}>
              <header><span>{titleizeCrmText(lane)}</span><strong>{visibleRows.filter(row => String(row[moduleConfig.boardBy] || '').toLowerCase() === lane.toLowerCase()).length}</strong></header>
              {visibleRows.filter(row => String(row[moduleConfig.boardBy] || '').toLowerCase() === lane.toLowerCase()).map(row => (
                <article key={row.id}>
                  <strong>{getCrmDisplayValue(row, moduleConfig.primary)}</strong>
                  <small>{getCrmDisplayValue(row, moduleConfig.secondary)}</small>
                  {moduleConfig.money && <em>{getCrmDisplayValue(row, moduleConfig.money)}</em>}
                </article>
              ))}
            </section>
          ))}
        </div>
      )}
    </section>
  );

  const pipelineView = (
    <div className={styles.analyticsGrid}>
      <section className={styles.metricPanel}><span>Weighted Pipeline</span><strong>{formatCrmMoney(pipelineValue)}</strong><small>{collections.deals?.total || 0} deal records</small></section>
      <section className={styles.metricPanel}><span>Accounts</span><strong>{collections.accounts?.total || 0}</strong><small>Customer accounts</small></section>
      <section className={styles.metricPanel}><span>Opportunities</span><strong>{collections.opportunities?.total || 0}</strong><small>Expansion records</small></section>
      <section className={styles.metricPanel}><span>Contract Posture</span><strong>{collections.contracts?.total || 0}</strong><small>Contract records</small></section>
      <div className={styles.spanAll}>{recordsView}</div>
    </div>
  );

  const tasksView = (
    <div className={styles.homeGrid}>
      {['tasks', 'meetings', 'conversations', 'tickets'].map(moduleId => {
        const config = resolveCrmCatalogModuleConfig(moduleId, activeModule);
        const Icon = resolveCrmCatalogIcon(config?.icon, Activity);
        return (
          <section key={moduleId} className={styles.widgetCard}>
            <header><span><Icon size={14} /> {config.label}</span><button type="button" onClick={() => { setActiveModule(moduleId); setActiveWorkspace('records'); }}>Open</button></header>
            <div className={styles.cleanList}>
              {(collections[moduleId]?.items || []).slice(0, 6).map(item => (
                <article key={item.id}><strong>{getCrmDisplayValue(item, config.primary)}</strong><small>{getCrmDisplayValue(item, config.secondary)}</small></article>
              ))}
              {(collections[moduleId]?.items || []).length === 0 && <p>No {config.label.toLowerCase()} found.</p>}
            </div>
          </section>
        );
      })}
    </div>
  );

  const evidenceView = (
    <div className={styles.analyticsGrid}>
      <section className={styles.metricPanel}><span>Source Registry Evidence</span><strong>{evidenceTotal}</strong><small>{compactCrmSignal(sourceRegistryEvidence.sourceStatus)}</small></section>
      <section className={styles.metricPanel}><span>Authority</span><strong>{collections.authorities?.total || 0}</strong><small>Authority-to-bind records</small></section>
      <section className={styles.metricPanel}><span>Contracts</span><strong>{collections.contracts?.total || 0}</strong><small>Contract ledger records</small></section>
      <section className={styles.metricPanel}><span>Risks</span><strong>{collections.risks?.total || 0}</strong><small>Customer risk records</small></section>
      <section className={styles.artifactPanel}>
        <header><span><Shield size={14} /> Customer Artifact Studio</span><p>Route real customer proof into board, legal, billing and document engines.</p></header>
        <button type="button" onClick={() => routeArtifactCommand('evidence')}><FileText size={15} /> CRM Evidence Pack</button>
        <button type="button" onClick={() => routeArtifactCommand('documents')}><Folder size={15} /> Document Vault</button>
        <button type="button" onClick={exportCurrentModule}><Download size={15} /> Portable CSV</button>
      </section>
    </div>
  );

  const aiView = (
    <div className={styles.aiGrid}>
      <section className={styles.aiPanel}>
        <span><Sparkles size={15} /> Wilsy AI CRM Memo</span>
        <h3>{aiMemo.headline}</h3>
        <p>{aiMemo.detail}</p>
        <strong>{aiMemo.next}</strong>
      </section>
      <section className={styles.aiPanel}>
        <span><Wand2 size={15} /> Command Engine</span>
        <h3>{compactCrmSignal(readiness.posture)}</h3>
        <p>Wilsy AI reads source posture, customer records, pipeline value, authority, contract posture and evidence route status.</p>
        <button type="button" onClick={loadAllData}>Run Source Review</button>
      </section>
    </div>
  );

  const importView = (
    <section className={styles.importPanel}>
      <header>
        <span><UploadCloud size={14} /> Governed CRM Import</span>
        <h3>Import only through preview and import routes.</h3>
        <p>No imported row enters CRM state unless the service route accepts it.</p>
      </header>
      <div className={styles.importControls}>
        <label>
          <span>Vendor</span>
          <select value={importVendor} onChange={event => setImportVendor(event.target.value)}>
            {WILSY_CRM_IMPORT_VENDOR_CATALOG.map(vendor => (
              <option key={vendor.id} value={vendor.id}>{vendor.label}</option>
            ))}
          </select>
        </label>
        <label>
          <span>Module</span>
          <select value={activeModule} onChange={event => setActiveModule(event.target.value)}>
            {CRM_MODULES.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}
          </select>
        </label>
        <button type="button" onClick={() => importInputRef.current?.click()}><UploadCloud size={15} /> Select CSV or JSON</button>
      </div>
      {importReport && (
        <article className={styles.importReport}>
          <strong>{compactCrmSignal(importReport.status)}</strong>
          <p>{importReport.message}</p>
        </article>
      )}
    </section>
  );

  /**
   * @function handleCrmTopRailPrimaryAction
   * @description Routes the Wilsy OS CRM top rail primary action to the CRM leads workspace without creating fake records.
   * @returns {void}
   * @collaboration Lets the slot-based Wilsy OS top rail stay context-aware while CRM keeps ownership of its domain modules.
   */
  const handleCrmTopRailPrimaryAction = () => {
    if (typeof setActiveWorkspace === 'function') {
      setActiveWorkspace('leads');
    }

    if (typeof setCommandCentreOpen === 'function') {
      setCommandCentreOpen(true);
    }

    if (typeof setCommandCentrePinned === 'function') {
      setCommandCentrePinned(true);
    }

    if (typeof setCommandCenter === 'function') {
      setCommandCenter(previous => ({
        ...previous,
        activeCommand: 'NEW_LEAD_CAPTURE',
        resourceType: 'leads',
        intent: 'capture',
        source: 'toprail',
        openedAt: new Date().toISOString()
      }));
    }

    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('wilsy:crm-lead-capture-requested', {
        detail: {
          action: 'NEW_LEAD_CAPTURE',
          resourceType: 'leads',
          source: 'CRMDashboard',
          emittedAt: new Date().toISOString()
        }
      }));
    }
  };

  /**
   * @function normalizeCrmIdentityText
   * @description Normalizes CRM identity text while refusing to display emails as operator names.
   * @param {unknown} value - Candidate identity value.
   * @returns {string} Display-safe identity text.
   * @collaboration Keeps the Wilsy OS top rail honest by showing DB-backed names or source-required language.
   */
  const normalizeCrmIdentityText = value => String(value || '').trim();

  /**
   * @function isCrmEmailIdentity
   * @description Determines whether a candidate identity value is only an email address.
   * @param {unknown} value - Candidate identity value.
   * @returns {boolean} True when the value is an email address.
   * @collaboration Prevents CRM from using email addresses as the primary operator display name.
   */
  const isCrmEmailIdentity = value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizeCrmIdentityText(value));

  /**
   * @function resolveCrmDbOperatorIdentity
   * @description Resolves CRM operator identity from DB/auth/profile sources without falling back to email as a name.
   * @param {Object} params - Operator source payloads.
   * @returns {{displayName:string,roleLabel:string,email:string,sourceStatus:string}} Operator identity for WilsyOSDashboardTopRail.
   * @collaboration Makes the CRM top rail display real user name, surname and role when backend data is available.
   */
  const resolveCrmDbOperatorIdentity = ({ accountProfileSource = {}, userSource = {}, accessSource = {} } = {}) => {
    const firstName = normalizeCrmIdentityText(
      accountProfileSource.firstName
      || accountProfileSource.givenName
      || userSource.firstName
      || userSource.givenName
      || accessSource.firstName
      || accessSource.givenName
    );
    const lastName = normalizeCrmIdentityText(
      accountProfileSource.lastName
      || accountProfileSource.surname
      || accountProfileSource.familyName
      || userSource.lastName
      || userSource.surname
      || userSource.familyName
      || accessSource.lastName
      || accessSource.surname
      || accessSource.familyName
    );
    const composedName = normalizeCrmIdentityText([firstName, lastName].filter(Boolean).join(' '));
    const profileName = normalizeCrmIdentityText(
      accountProfileSource.fullName
      || accountProfileSource.displayName
      || accountProfileSource.name
      || userSource.fullName
      || userSource.displayName
      || userSource.name
      || accessSource.fullName
      || accessSource.displayName
      || accessSource.name
    );
    const displayName = composedName
      || (!isCrmEmailIdentity(profileName) ? profileName : '')
      || 'User profile source required';
    const roleLabel = normalizeCrmIdentityText(
      accountProfileSource.roleLabel
      || accountProfileSource.role
      || accountProfileSource.title
      || userSource.roleLabel
      || userSource.role
      || userSource.title
      || accessSource.roleLabel
      || accessSource.role
      || accessSource.tenantRole
      || 'Role source required'
    );

    return {
      ...accountProfileSource,
      displayName,
      name: displayName,
      roleLabel,
      role: roleLabel,
      email: normalizeCrmIdentityText(accountProfileSource.email || userSource.email || accessSource.email),
      sourceStatus: displayName === 'User profile source required' || roleLabel === 'Role source required'
        ? 'PROFILE_SOURCE_REQUIRED'
        : 'DB_PROFILE_RESOLVED'
    };
  };

  /**
   * @function resolveCrmTenantTopRailIdentity
   * @description Resolves tenant identity for the Wilsy OS CRM top rail without hardcoded tenant status theatre.
   * @param {Object} tenantSource - Tenant identity source.
   * @returns {Object} Tenant identity for WilsyOSDashboardTopRail.
   * @collaboration Keeps the tenant plate rooted in tenant data while preserving the official Wilsy logo fallback.
   */
  const resolveCrmTenantTopRailIdentity = (tenantSource = {}) => ({
    ...tenantSource,
    displayName: normalizeCrmIdentityText(tenantSource.displayName || tenantSource.companyName || tenantSource.name) || 'Tenant profile source required',
    tenantId: normalizeCrmIdentityText(tenantSource.tenantId || tenantSource.id) || 'wilsy-sovereign-root',
    logo: tenantSource.logo || tenantSource.branding?.logo || '/src/assets/logo/wilsy.jpeg',
    status: normalizeCrmIdentityText(tenantSource.status || tenantSource.sourceStatus || tenantSource.ledgerStatus)
      || (normalizeCrmIdentityText(tenantSource.displayName || tenantSource.companyName || tenantSource.name || tenantSource.tenantId || tenantSource.id)
        ? 'Tenant identity live'
        : 'Tenant profile source pending')
  });

  /**
   * @function buildCrmTopRailStoryMessages
   * @description Builds the CRM top rail story from live readiness and source posture only.
   * @param {Object} params - Story source params.
   * @returns {Array<string>} Source-backed story messages.
   * @collaboration Removes hardcoded placeholder slogans from the CRM top rail.
   */
  const buildCrmTopRailStoryMessages = ({ liveStatus = '', readinessSource = {} } = {}) => ([
    normalizeCrmIdentityText(liveStatus) || 'CRM source status required',
    `${Number(readinessSource.liveSources || 0)}/${Number(readinessSource.totalSources || 0)} live sources visible`,
    normalizeCrmIdentityText(readinessSource.posture || readinessSource.status) || 'Source posture required'
  ]);

  const crmResolvedOperatorIdentity = resolveCrmDbOperatorIdentity({
    accountProfileSource: typeof accountProfile === 'undefined' ? {} : accountProfile,
    userSource: typeof user === 'undefined' ? {} : user,
    accessSource: typeof access === 'undefined' ? {} : access
  });
  const crmResolvedTenantTopRailIdentity = resolveCrmTenantTopRailIdentity(typeof tenantIdentity === 'undefined' ? {} : tenantIdentity);
  /**
   * @function formatCrmSourcePosture
   * @description Converts raw CRM source constants into polished Wilsy OS interface language.
   * @param {unknown} value - Raw source posture value.
   * @returns {string} Human-readable source posture.
   * @collaboration Removes leaked constants such as SOURCE_GAPS from CRM while preserving source-truth honesty.
   */
  const formatCrmSourcePosture = value => {
    const raw = String(value || '').trim().toUpperCase();

    const phrases = {
      SOURCE_GAPS: 'CRM live records awaiting sync',
      SOURCE_REQUIRED: 'Source handshake pending',
      SOURCE_SILENT: 'Source awaiting connection',
      SOURCE_PENDING: 'Source pending',
      LIVE_SOURCE_REQUIRED: 'Live records awaiting sync',
      CRM_SOURCE_SILENT: 'CRM source handshake pending',
      CRM_SOURCE_LIVE: 'CRM source live',
      ZERO_RECORDS_FOUND_IN_SHARD: 'No records found in connected shard',
      TENANT_LEDGER_READY: 'Tenant ledger ready',
      PROFILE_SOURCE_REQUIRED: 'Profile source required',
      DB_PROFILE_RESOLVED: 'Database profile resolved'
    };

    if (phrases[raw]) return phrases[raw];

    return raw
      .replace(/^CRM_/, '')
      .replace(/^WILSY_/, '')
      .replace(/_+/g, ' ')
      .toLowerCase()
      .replace(/\b\w/g, letter => letter.toUpperCase()) || 'Source connection required';
  };

  /**
   * @function buildCrmPolishedTopRailStoryMessages
   * @description Builds polished CRM top rail story messages without exposing raw source constants.
   * @param {Object} params - CRM story sources.
   * @returns {Array<string>} Polished top rail story messages.
   * @collaboration Keeps Wilsy OS Chrome premium while refusing fake live-source claims.
   */
  const buildCrmPolishedTopRailStoryMessages = ({ readinessSource = {} } = {}) => {
    const liveSources = Number(readinessSource.liveSources || 0);
    const totalSources = Number(readinessSource.totalSources || 0);
    const routeMessage = totalSources > 0
      ? `${totalSources} CRM routes checked`
      : 'CRM route inventory loading';
    const sourceMessage = liveSources > 0
      ? `${liveSources}/${totalSources} CRM sources live`
      : 'Tenant identity loaded';
    const postureMessage = liveSources > 0
      ? formatCrmSourcePosture(readinessSource.posture || readinessSource.status || 'CRM_SOURCE_LIVE')
      : 'CRM live records awaiting sync';

    return [sourceMessage, routeMessage, postureMessage];
  };

  /**
   * @function pickCrmAccountValue
   * @description Picks the first non-empty value from CRM account identity candidates.
   * @param {...unknown} values - Candidate values.
   * @returns {string} First displayable value.
   * @collaboration Keeps WilsyAccountCommandCenter connected to real CRM/auth identity data without fake fallbacks.
   */
  const pickCrmAccountValue = (...values) => (
    values
      .map(value => String(value || '').trim())
      .find(Boolean) || ''
  );

  /**
   * @function readCrmNestedAccountValue
   * @description Reads nested account values from possible auth, access, profile and tenant payloads.
   * @param {Object} source - Source object.
   * @param {Array<string>} paths - Dot paths to inspect.
   * @returns {string} First discovered value.
   * @collaboration Mirrors ExecutiveDashboard's broad user/access payload tolerance for CRM.
   */
  const readCrmNestedAccountValue = (source = {}, paths = []) => {
    for (const path of paths) {
      const value = String(path)
        .split('.')
        .reduce((cursor, key) => (cursor && cursor[key] !== undefined ? cursor[key] : undefined), source);

      if (value !== undefined && value !== null && String(value).trim()) {
        return String(value).trim();
      }
    }

    return '';
  };

  /**
   * @function buildCrmAccountCommandCenterUser
   * @description Builds the exact user packet CRM should pass into WilsyAccountCommandCenter using auth/access/profile/tenant sources.
   * @param {Object} params - CRM account source packet.
   * @returns {Object} Account Command Center user payload.
   * @collaboration Fixes UNBOUND_USER by giving Account Command Center the same class of identity object ExecutiveDashboard supplies.
   */
  const buildCrmAccountCommandCenterUser = ({
    userSource = {},
    accessSource = {},
    accountProfileSource = {},
    operatorSource = {},
    tenantSource = {}
  } = {}) => {
    const id = pickCrmAccountValue(
      readCrmNestedAccountValue(userSource, ['id', '_id', 'userId', 'uid', 'sub', 'claims.sub', 'profile.id', 'profile._id', 'user.id', 'user._id']),
      readCrmNestedAccountValue(accessSource, ['id', '_id', 'userId', 'uid', 'sub', 'claims.sub', 'profile.id', 'profile._id', 'user.id', 'user._id']),
      readCrmNestedAccountValue(accountProfileSource, ['id', '_id', 'userId', 'uid', 'sub', 'profile.id', 'profile._id']),
      readCrmNestedAccountValue(operatorSource, ['id', '_id', 'userId', 'uid', 'sub']),
      readCrmNestedAccountValue(tenantSource, ['ownerId', 'createdBy', 'userId'])
    );

    const firstName = pickCrmAccountValue(
      userSource.firstName,
      userSource.givenName,
      userSource.profile?.firstName,
      accessSource.firstName,
      accessSource.givenName,
      accessSource.user?.firstName,
      accountProfileSource.firstName,
      operatorSource.firstName
    );
    const lastName = pickCrmAccountValue(
      userSource.lastName,
      userSource.surname,
      userSource.familyName,
      userSource.profile?.lastName,
      accessSource.lastName,
      accessSource.surname,
      accessSource.familyName,
      accessSource.user?.lastName,
      accountProfileSource.lastName,
      accountProfileSource.surname,
      operatorSource.lastName
    );
    const composedName = [firstName, lastName].filter(Boolean).join(' ').trim();
    const displayName = pickCrmAccountValue(
      composedName,
      userSource.fullName,
      userSource.displayName,
      userSource.name,
      userSource.profile?.displayName,
      accessSource.fullName,
      accessSource.displayName,
      accessSource.name,
      accessSource.user?.displayName,
      accessSource.user?.name,
      accountProfileSource.fullName,
      accountProfileSource.displayName,
      accountProfileSource.name,
      operatorSource.displayName,
      operatorSource.name,
      tenantSource.ownerName,
      tenantSource.founderName
    );

    const email = pickCrmAccountValue(
      userSource.email,
      userSource.username,
      userSource.profile?.email,
      accessSource.email,
      accessSource.userEmail,
      accessSource.username,
      accessSource.user?.email,
      accountProfileSource.email,
      operatorSource.email
    );

    const roleLabel = pickCrmAccountValue(
      userSource.roleLabel,
      userSource.role,
      userSource.tenantRole,
      userSource.title,
      accessSource.roleLabel,
      accessSource.userRole,
      accessSource.role,
      accessSource.tenantRole,
      accessSource.user?.role,
      accountProfileSource.roleLabel,
      accountProfileSource.role,
      operatorSource.roleLabel,
      operatorSource.role,
      'CRM Command'
    );

    return {
      ...accessSource,
      ...userSource,
      ...accountProfileSource,
      ...operatorSource,
      id: id || undefined,
      _id: id || userSource._id || accessSource._id || accountProfileSource._id,
      userId: id || userSource.userId || accessSource.userId || accountProfileSource.userId,
      uid: id || userSource.uid || accessSource.uid,
      sub: id || userSource.sub || accessSource.sub,
      firstName,
      lastName,
      fullName: displayName || email || 'Wilsy OS Operator',
      displayName: displayName || email || 'Wilsy OS Operator',
      name: displayName || email || 'Wilsy OS Operator',
      email,
      role: roleLabel,
      roleLabel,
      tenantId: pickCrmAccountValue(
        tenantSource.tenantId,
        tenantSource.id,
        accessSource.tenantId,
        userSource.tenantId,
        accountProfileSource.tenantId,
        'MASTER'
      ),
      tenantName: pickCrmAccountValue(
        tenantSource.displayName,
        tenantSource.companyName,
        tenantSource.name,
        'Wilsy OS Root'
      ),
      edition: pickCrmAccountValue(accountProfileSource.edition, accessSource.edition, 'SOVEREIGN_EDITION'),
      authority: pickCrmAccountValue(accountProfileSource.authority, accessSource.authority, roleLabel, 'TENANT_AUTHORITY')
    };
  };

  /**
   * @function buildCrmAccountSecuritySummary
   * @description Builds Account Command Center security summary from CRM/access readiness.
   * @param {Object} params - Security source params.
   * @returns {Object} Security summary for WilsyAccountCommandCenter.
   * @collaboration Connects the Account Command Center to CRM service state without inventing unavailable auth-discovery data.
   */
  const buildCrmAccountSecuritySummary = ({ accountUser = {}, readinessSource = {}, accessSource = {} } = {}) => ({
    identitySource: accountUser.id || accountUser.userId || accountUser._id ? 'CRM identity bound' : 'Auth identity source pending',
    mfaStatus: accessSource.mfaEnabled ? 'MFA enabled' : 'MFA source pending',
    trustedDevices: accessSource.trustedDevices?.length ? `${accessSource.trustedDevices.length} trusted devices` : 'Device source pending',
    accountActivity: `${Number(readinessSource.score || 0)}% CRM readiness`
  });

  /**
   * @function buildCrmAccountComplianceSummary
   * @description Builds Account Command Center compliance summary from tenant/readiness state.
   * @param {Object} params - Compliance source params.
   * @returns {Object} Compliance summary for WilsyAccountCommandCenter.
   * @collaboration Keeps POPIA, tenant ledger and CRM readiness visible inside the OS account surface.
   */
  const buildCrmAccountComplianceSummary = ({ readinessSource = {}, tenantSource = {} } = {}) => ({
    privacyStatus: 'POPIA display safe',
    complianceStatus: tenantSource.complianceStatus || tenantSource.status || 'Tenant ledger visible',
    auditConfidence: `${Number(readinessSource.score || 0)}% CRM readiness`,
    retentionStatus: tenantSource.retentionStatus || tenantSource.ledgerStatus || 'Tenant ledger visible'
  });

  /**
   * @function buildCrmAccountSessionSummary
   * @description Builds Account Command Center session summary from CRM telemetry and auth access data.
   * @param {Object} params - Session source params.
   * @returns {Object} Session summary for WilsyAccountCommandCenter.
   * @collaboration Separates live CRM command state from the still-pending auth discover route.
   */
  const buildCrmAccountSessionSummary = ({ accessSource = {}, readinessSource = {} } = {}) => ({
    activeSessions: accessSource.sessionId || accessSource.tokenPresent
      ? 'CRM auth session detected'
      : `${Number(readinessSource.liveSources || 0)}/${Number(readinessSource.totalSources || 0)} CRM sources live`
  });

  /**
   * @function resolveCrmAccountThemeChangePayload
   * @description Resolves operating skin changes emitted by WilsyAccountCommandCenter from strings, receipts, payloads or DOM events.
   * @param {unknown} packet - Theme change packet.
   * @returns {string} Normalized CRM theme id.
   * @collaboration Converts Account Command Center receipts into real CRM/Wilsy OS repaint commands.
   */
  const resolveCrmAccountThemeChangePayload = packet => {
    const aliases = {
      black: 'sovereign_black',
      sovereign: 'sovereign_black',
      sovereign_black: 'sovereign_black',
      aurora: 'wilsy_aurora',
      wilsy_aurora: 'wilsy_aurora',
      daybreak: 'wilsy_daybreak',
      wilsy_daybreak: 'wilsy_daybreak',
      pearl: 'pearl_command',
      pearl_command: 'pearl_command'
    };

    const raw = typeof packet === 'string'
      ? packet
      : (
        packet?.themeId
        || packet?.skinId
        || packet?.theme
        || packet?.skin
        || packet?.id
        || packet?.value
        || packet?.target?.value
        || packet?.detail?.themeId
        || packet?.detail?.skinId
        || packet?.detail?.value
        || ''
      );

    const cleaned = String(raw || '').trim();
    const aliasKey = cleaned.toLowerCase().replace(/\s+/g, '_');

    return aliases[aliasKey] || cleaned || accountThemeId;
  };

  /**
   * @function resolveCrmAccountModeChangePayload
   * @description Resolves mode changes emitted by WilsyAccountCommandCenter from strings, receipts, payloads or DOM events.
   * @param {unknown} packet - Mode change packet.
   * @returns {string} Normalized CRM mode.
   * @collaboration Keeps Account Command Center mode selection synchronized with the CRM runtime.
   */
  const resolveCrmAccountModeChangePayload = packet => {
    const raw = typeof packet === 'string'
      ? packet
      : (
        packet?.mode
        || packet?.themeMode
        || packet?.id
        || packet?.value
        || packet?.target?.value
        || packet?.detail?.mode
        || packet?.detail?.themeMode
        || packet?.detail?.value
        || ''
      );

    const mode = String(raw || accountThemeMode || 'night').trim().toLowerCase();
    return ['day', 'night', 'auto'].includes(mode) ? mode : 'night';
  };

  /**
   * @function normalizeCrmAccountThemeId
   * @description Normalizes Account Command Center skin ids into supported CRM/Wilsy OS theme ids.
   * @param {unknown} themeId - Candidate theme id.
   * @returns {string} Supported theme id.
   * @collaboration Prevents receipt-only skin changes by keeping theme ids compatible with CRM runtime variables.
   */
  const normalizeCrmAccountThemeId = themeId => {
    const aliases = {
      black: 'sovereign_black',
      sovereign: 'sovereign_black',
      sovereign_black: 'sovereign_black',
      aurora: 'wilsy_aurora',
      wilsy_aurora: 'wilsy_aurora',
      daybreak: 'wilsy_daybreak',
      wilsy_daybreak: 'wilsy_daybreak',
      pearl: 'pearl_command',
      pearl_command: 'pearl_command'
    };

    const cleaned = String(themeId || accountThemeId || 'sovereign_black').trim();
    const aliasKey = cleaned.toLowerCase().replace(/\s+/g, '_');

    return aliases[aliasKey] || cleaned || 'sovereign_black';
  };

  /**
   * @function buildCrmAccountThemeFallbackVars
   * @description Builds fallback CSS variables when the CRM theme builder does not provide a complete variable packet.
   * @param {string} themeId - Theme id.
   * @param {string} mode - Theme mode.
   * @returns {Object} CSS variable map.
   * @collaboration Guarantees that Account theme changes repaint the CRM shell even when theme helper coverage is partial.
   */
  const buildCrmAccountThemeFallbackVars = (themeId, mode) => {
    const palettes = {
      sovereign_black: {
        '--crm-bg': '#050505',
        '--crm-surface': '#090b10',
        '--crm-card': '#0d1017',
        '--crm-accent': '#d4af37',
        '--crm-accent-2': '#84f0c8',
        '--crm-accent-3': '#b66dff',
        '--crm-glow': 'rgba(212, 175, 55, 0.18)',
        '--crm-glow-2': 'rgba(132, 240, 200, 0.12)'
      },
      wilsy_aurora: {
        '--crm-bg': '#050711',
        '--crm-surface': '#0b1020',
        '--crm-card': '#0e1528',
        '--crm-accent': '#b66dff',
        '--crm-accent-2': '#17bdf2',
        '--crm-accent-3': '#84f0c8',
        '--crm-glow': 'rgba(182, 109, 255, 0.22)',
        '--crm-glow-2': 'rgba(23, 189, 242, 0.16)'
      },
      wilsy_daybreak: {
        '--crm-bg': '#f6f0df',
        '--crm-surface': '#fffaf0',
        '--crm-card': '#f4ead0',
        '--crm-accent': '#b8860b',
        '--crm-accent-2': '#0f8f8c',
        '--crm-accent-3': '#5f6df0',
        '--crm-glow': 'rgba(184, 134, 11, 0.2)',
        '--crm-glow-2': 'rgba(15, 143, 140, 0.14)'
      },
      pearl_command: {
        '--crm-bg': '#f4f6fb',
        '--crm-surface': '#ffffff',
        '--crm-card': '#edf1f8',
        '--crm-accent': '#5f6df0',
        '--crm-accent-2': '#0f8f8c',
        '--crm-accent-3': '#b8860b',
        '--crm-glow': 'rgba(95, 109, 240, 0.18)',
        '--crm-glow-2': 'rgba(15, 143, 140, 0.12)'
      }
    };

    return palettes[themeId] || palettes.sovereign_black;
  };

  /**
   * @function commitCrmAccountThemeRuntime
   * @description Commits Account Command Center theme/mode changes into CRM state, storage, document datasets and CSS variables.
   * @param {Object} params - Theme runtime params.
   * @returns {{themeId:string,mode:string}} Applied theme packet.
   * @collaboration Turns operating skin receipts into actual Wilsy OS runtime repaint.
   */
  const commitCrmAccountThemeRuntime = ({ themeId = accountThemeId, mode = accountThemeMode, source = 'crm_account_command_center' } = {}) => {
    const nextThemeId = normalizeCrmAccountThemeId(themeId);
    const nextMode = resolveCrmAccountModeChangePayload(mode);

    let helperVars = {};

    try {
      if (typeof buildWilsyCrmThemeVars === 'function') {
        helperVars = buildWilsyCrmThemeVars(nextThemeId, nextMode) || {};
      }
    } catch (themeError) {
      helperVars = {};
    }

    const nextVars = {
      ...buildCrmAccountThemeFallbackVars(nextThemeId, nextMode),
      ...helperVars
    };

    setAccountThemeId(nextThemeId);
    setAccountThemeMode(nextMode);

    if (typeof window !== 'undefined') {
      try {
        window.localStorage.setItem('wilsy:crm:theme', nextThemeId);
        window.localStorage.setItem('wilsy:crm:mode', nextMode);
        window.localStorage.setItem('wilsy:account-command-center:theme', nextThemeId);
        window.localStorage.setItem('wilsy:account-command-center:mode', nextMode);
        window.localStorage.setItem('wilsy:dashboard-chrome:theme', nextThemeId);
        window.localStorage.setItem('wilsy:dashboard-chrome:mode', nextMode);
      } catch (storageError) {
        // Storage can fail in restricted browser contexts; runtime repaint must still continue.
      }

      try {
        if (typeof applyWilsyCrmThemeToDocument === 'function') {
          applyWilsyCrmThemeToDocument(nextThemeId, nextMode);
        }
      } catch (documentThemeError) {
        // Continue with direct CSS variable application below.
      }

      if (typeof document !== 'undefined') {
        document.documentElement.dataset.wilsyTheme = nextThemeId;
        document.documentElement.dataset.wilsyMode = nextMode;

        if (document.body) {
          document.body.dataset.wilsyTheme = nextThemeId;
          document.body.dataset.wilsyMode = nextMode;
        }

        Object.entries(nextVars).forEach(([key, value]) => {
          document.documentElement.style.setProperty(key, value);

          if (document.body) {
            document.body.style.setProperty(key, value);
          }
        });
      }

      window.dispatchEvent(new CustomEvent('wilsy:theme-change', {
        detail: {
          themeId: nextThemeId,
          mode: nextMode,
          source,
          emittedAt: new Date().toISOString()
        }
      }));

      window.dispatchEvent(new CustomEvent('wilsy:crm-theme-change', {
        detail: {
          themeId: nextThemeId,
          mode: nextMode,
          source,
          emittedAt: new Date().toISOString()
        }
      }));
    }

    return { themeId: nextThemeId, mode: nextMode };
  };

  /**
   * @function handleCrmAccountThemeChange
   * @description Handles Account Command Center operating skin changes and repaints CRM immediately.
   * @param {unknown} packet - Theme change packet.
   * @returns {{themeId:string,mode:string}} Applied theme packet.
   * @collaboration Gives CRM the same account-driven theme authority as ExecutiveDashboard.
   */
  const handleCrmAccountThemeChange = packet => commitCrmAccountThemeRuntime({
    themeId: resolveCrmAccountThemeChangePayload(packet),
    mode: accountThemeMode,
    source: 'crm_account_theme_change'
  });

  /**
   * @function handleCrmAccountModeChange
   * @description Handles Account Command Center day/night/auto changes and repaints CRM immediately.
   * @param {unknown} packet - Mode change packet.
   * @returns {{themeId:string,mode:string}} Applied mode packet.
   * @collaboration Synchronizes CRM visual mode with the selected Account Command Center mode.
   */
  const handleCrmAccountModeChange = packet => commitCrmAccountThemeRuntime({
    themeId: accountThemeId,
    mode: resolveCrmAccountModeChangePayload(packet),
    source: 'crm_account_mode_change'
  });

  /**
   * @function handleCrmAccountCommandBridge
   * @description Routes Account Command Center commands while converting theme receipts into real CRM runtime changes.
   * @param {unknown} command - Account command.
   * @param {unknown} payload - Account command payload.
   * @returns {unknown} Downstream command result.
   * @collaboration Preserves existing CRM account navigation while activating saved skin/mode receipts.
   */
  const handleCrmAccountCommandBridge = (command, payload) => {
    const commandKey = String(
      typeof command === 'string'
        ? command
        : (command?.action || command?.type || command?.id || command?.command || '')
    ).toLowerCase();

    const commandPayload = payload || command || {};

    if (commandKey.includes('skin') || commandKey.includes('theme') || commandKey.includes('operating_skin')) {
      handleCrmAccountThemeChange(commandPayload);
    }

    if (commandKey.includes('mode')) {
      handleCrmAccountModeChange(commandPayload);
    }

    if (typeof handleCrmAccountCommand === 'function') {
      return handleCrmAccountCommand(command, payload);
    }

    return undefined;
  };

  useEffect(() => {
    commitCrmAccountThemeRuntime({
      themeId: accountThemeId,
      mode: accountThemeMode,
      source: 'crm_account_theme_state_effect'
    });
  }, [accountThemeId, accountThemeMode]);

const workspaceContent = {
    home: homeCards,
    command: homeCards,
    records: recordsView,
    pipeline: pipelineView,
    tasks: tasksView,
    work: tasksView,
    success: recordsView,
    support: tasksView,
    automation: aiView,
    intelligence: aiView,
    evidence: evidenceView,
    ai: aiView,
    import: importView
  };
  const liveCrmStatusLabel = buildCrmLiveStatusLabel({
    readiness,
    isRefreshing,
    error: null,
    lastUpdated: null
  });



  return (
    <div className={styles.crmShell} style={crmThemeVars} data-wilsy-crm-dashboard="clean-os" data-version={CRM_VERSION} data-wilsy-theme={accountThemeId} data-wilsy-mode={accountThemeMode}>
      <input ref={importInputRef} type="file" accept=".csv,.json,text/csv,application/json" className={styles.hiddenInput} onChange={importFile} />
      {(founderReturnEnabled || typeof onFounderReturn === 'function') && (
        founderReturnOpen ? (
          <div className={styles.founderReturnOpenPanel} data-wilsy-founder-return="open">
            <button type="button" className={styles.founderReturnAction} onClick={onFounderReturn}>
              ← Founder Dashboard
            </button>
            <button type="button" className={styles.founderReturnClose} onClick={() => setFounderReturnOpen(false)} aria-label="Close Founder return">
              ×
            </button>
          </div>
        ) : (
          <button
            type="button"
            className={styles.founderReturnClosedButton}
            onClick={() => setFounderReturnOpen(true)}
            aria-label="Open Founder return"
          >
            ♛
          </button>
        )
      )}

      <aside className={`${styles.moduleRail} ${sideRailOpen ? styles.moduleRailOpen : styles.moduleRailClosed}`} aria-label="CRM module navigation">
        <button
          type="button"
          className={styles.railDockToggle}
          onClick={() => setSideRailOpen(previous => !previous)}
          aria-expanded={sideRailOpen}
          aria-label={sideRailOpen ? 'Collapse CRM rail' : 'Expand CRM rail'}
        >
          {sideRailOpen ? '‹' : '›'}
        </button>

        <div className={styles.productMark}>
          <div className={styles.logoBox}>
            <img src={tenantIdentity.logo || wilsyOfficialLogo} alt={`${tenantIdentity.displayName} logo`} onError={(event) => { event.currentTarget.onerror = null; event.currentTarget.src = wilsyOfficialLogo || createCrmInitialsSeal(tenantIdentity.displayName); }} />
          </div>
          <div>
            <strong>Wilsy CRM</strong>
            <small>{tenantIdentity.tenantId}</small>
          </div>
        </div>

        <label className={styles.railSearch}>
          <Search size={14} />
          <input value={searchTerm} onChange={event => setSearchTerm(event.target.value)} placeholder="Search records" />
        </label>

        <nav className={styles.railNav}>
          <button type="button" className={activeWorkspace === 'home' ? styles.navButtonActive : styles.navButton} onClick={() => setActiveWorkspace('home')}>
            <Home size={16} /> Home
          </button>
          <button type="button" className={activeWorkspace === 'evidence' ? styles.navButtonActive : styles.navButton} onClick={() => setActiveWorkspace('evidence')}>
            <BarChart3 size={16} /> Reports
          </button>
        </nav>

        <div className={styles.moduleTitle}>Modules</div>
        <div className={styles.moduleList}>{moduleCards}</div>
      </aside>

      <section className={styles.appSurface}>
                                <WilsyOSDashboardTopRail
                  className={styles.crmSlotTopRail}
                  dashboardKey="crm"
                  commandLabel="Customer Intelligence"
                  title="WILSY OS CRM COMMAND CENTER"
                  posture={readiness?.posture || readiness?.status || 'SOURCE_REQUIRED'}
                  tenant={crmResolvedTenantTopRailIdentity}
                  operator={crmResolvedOperatorIdentity}
                  storyMessages={buildCrmPolishedTopRailStoryMessages({ readinessSource: readiness })}
                  search={{
                    value: searchTerm,
                    placeholder: 'Search customers, deals, contacts or press ⌘K',
                    onChange: event => setSearchTerm(event.target.value),
                    onFocus: () => {
                      if (typeof window !== 'undefined') {
                        window.dispatchEvent(new CustomEvent('wilsy:open-command-search'));
                      }
                    }
                  }}
                  account={{
                                    label: 'COMMAND CENTER',
                                    onOpen: openWilsyAccountSettings
                                  }}
                  actions={{
                    liveSyncLabel: 'LIVE SYNC',
                    primaryActionLabel: 'NEW LEAD',
                    isRefreshing,
                    onLiveSync: () => {
      if (typeof loadAllData === 'function') {
        loadAllData();
      }

      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('wilsy:crm-live-sync-requested', {
          detail: {
            action: 'LIVE_SYNC',
            source: 'CRMDashboard',
            emittedAt: new Date().toISOString()
          }
        }));
      }
    },
                    onPrimaryAction: handleCrmTopRailPrimaryAction
                  }}
                
                                  accountTrigger={
                                    <button
                                      type="button"
                                      className="wilsyOsChromeSecondaryButton"
                                      data-wilsy-crm-command-center-direct="executive-parity"
                                      title="Open Wilsy Account Command Center"
                                      onClick={() => setAccountSettingsOpen(true)}
                                    >
                                      <UserCog size={13} /> COMMAND CENTER
                                    </button>
                                  }/>

        <main className={styles.operatingGrid}>
          <nav className={styles.workspaceRail} aria-label="CRM workspace navigation">
            <label className={styles.workspaceSelect}>
              <span>Workspace</span>
              <select value={activeWorkspace} onChange={event => setActiveWorkspace(event.target.value)}>
                {CRM_WORKSPACES.map(workspace => <option key={workspace.id} value={workspace.id}>{workspace.label}</option>)}
              </select>
            </label>
            <div className={styles.workspaceButtons}>{workspaceButtons}</div>
          </nav>

          <section className={styles.workspaceViewport}>
            <header className={styles.workspaceHeader}>
              <div>
                <span><ActiveWorkspaceIcon size={14} /> {CRM_WORKSPACES.find(workspace => workspace.id === activeWorkspace)?.label || titleizeCrmText(activeWorkspace)}</span>
                <h2>{CRM_WORKSPACES.find(workspace => workspace.id === activeWorkspace)?.label || titleizeCrmText(activeWorkspace)}</h2>
                <p>{activeWorkspace === 'home' ? liveCrmStatusLabel : `${moduleConfig.label} // ${sourceLabel}`}</p>
              </div>
              <div className={styles.workspaceMetrics}>
                <article><small>Readiness</small><strong>{readiness.score}%</strong></article>
                <article><small>Sources</small><strong>{readiness.liveSources}/{readiness.totalSources}</strong></article>
                <article><small>Pipeline</small><strong>{formatCrmMoney(pipelineValue)}</strong></article>
              </div>
            </header>
            <div className={styles.workspaceContent}>{workspaceContent[activeWorkspace] || homeCards}</div>
          </section>

          <aside className={`${styles.contextRail} ${commandCentrePinned ? styles.contextRailPinned : styles.contextRailFloating} ${(commandCentreOpen || commandCentrePinned) ? styles.contextRailOpen : styles.contextRailClosed}`} aria-label="CRM command rail">
            <div className={styles.contextDockControls}>
              <button
                type="button"
                className={styles.contextRailHandle}
                onClick={() => setCommandCentreOpen(previous => commandCentrePinned ? true : !previous)}
                aria-expanded={commandCentreOpen || commandCentrePinned}
                aria-label={(commandCentreOpen || commandCentrePinned) ? 'Close Command Centre' : 'Open Command Centre'}
              >
                {(commandCentreOpen || commandCentrePinned) ? 'Close' : 'Command'}
              </button>
              <button
                type="button"
                className={styles.contextPinButton}
                onClick={() => {
                  setCommandCentrePinned(previous => !previous);
                  setCommandCentreOpen(true);
                }}
                aria-pressed={commandCentrePinned}
                aria-label={commandCentrePinned ? 'Unpin Command Centre' : 'Pin Command Centre'}
              >
                {commandCentrePinned ? 'Unpin' : 'Pin'}
              </button>
            </div>

            <div className={styles.contextRailInner}>
            <header>
              <span><Sparkles size={14} /> Command Centre</span>
              <strong>{compactCrmSignal(readiness.posture)}</strong>
              <p>{collections.leads?.total || 0} leads, {collections.accounts?.total || 0} accounts, {collections.deals?.total || 0} deals.</p>
            </header>

            <label>
              <span>Run Command</span>
              <select
                value=""
                onChange={event => {
                  if (event.target.value === 'sync') loadAllData();
                  if (event.target.value === 'create') openCreateRecord();
                  if (event.target.value === 'export') exportCurrentModule();
                  if (event.target.value === 'import') setActiveWorkspace('import');
                  if (event.target.value === 'ai') setActiveWorkspace('ai');
                }}
              >
                <option value="">Select command</option>
                <option value="sync">Live Sync</option>
                <option value="create">New Record</option>
                <option value="export">Export Current Module</option>
                <option value="import">Import Customers</option>
                <option value="ai">Wilsy AI Review</option>
              </select>
            </label>

            <label>
              <span>CRM Module</span>
              <select value={activeModule} onChange={event => { setActiveModule(event.target.value); setActiveWorkspace('records'); }}>
                {CRM_MODULES.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}
              </select>
            </label>

            <button type="button" className={styles.primaryButton} onClick={() => routeArtifactCommand('evidence')}>
              <Download size={14} /> Evidence Pack
            </button>

            <section className={styles.aiRailCard}>
              <span>Wilsy AI</span>
              <p>{aiMemo.headline}</p>
            </section>

            <section className={styles.receiptFeed}>
              <span>Command Receipts</span>
              {receipts.map(receipt => (
                <article key={receipt.id}>
                  <strong>{receipt.eventType}</strong>
                  <small>{receipt.message}</small>
                  <em>{receipt.proofHash}</em>
                </article>
              ))}
              {receipts.length === 0 && <p>No command executed yet.</p>}
            </section>
            </div>
          </aside>
        </main>
      </section>

      {modalOpen && (
        <div className={styles.modalOverlay}>
          <section className={styles.modalPanel}>
            <header>
              <div>
                <span>{editingRecord ? 'Update Record' : 'Create Record'}</span>
                <h2>{moduleConfig.singular}</h2>
              </div>
              <button type="button" onClick={() => setModalOpen(false)}><X size={16} /></button>
            </header>
            <div className={styles.formGrid}>
              {moduleConfig.fields.map(field => (
                <label key={field}>
                  <span>{FIELD_LABELS[field] || titleizeCrmText(field)}</span>
                  <input
                    type={FIELD_TYPES[field] || 'text'}
                    value={recordDraft[field] ?? ''}
                    onChange={event => setRecordDraft(previous => ({
                      ...previous,
                      [field]: FIELD_TYPES[field] === 'number' ? numericCrmValue(event.target.value) : event.target.value
                    }))}
                  />
                </label>
              ))}
            </div>
            <footer>
              <button type="button" onClick={() => setModalOpen(false)}>Cancel</button>
              <button type="button" onClick={saveRecord} className={styles.primaryButton}>{editingRecord ? 'Update' : 'Create'}</button>
            </footer>
          </section>
        </div>
      )}
    
      {/* WILSY CRM EXECUTIVE ROOT ACCOUNT MOUNT - STEP M */}
            <WilsyAccountCommandCenter
        isOpen={accountSettingsOpen}
        onClose={() => setAccountSettingsOpen(false)}
        onNavigate={handleCrmAccountCommandBridge}
        onSignOut={typeof handleCrmChromeSignOut === 'function' ? handleCrmChromeSignOut : undefined}
        user={buildCrmAccountCommandCenterUser({
          userSource: typeof user === 'undefined' ? {} : user,
          accessSource: typeof access === 'undefined' ? {} : access,
          accountProfileSource: typeof accountProfile === 'undefined' ? {} : accountProfile,
          operatorSource: typeof crmResolvedOperatorIdentity === 'undefined' ? {} : crmResolvedOperatorIdentity,
          tenantSource: typeof tenantIdentity === 'undefined' ? {} : tenantIdentity
        })}
        activeThemeId={accountThemeId}
        themeMode={accountThemeMode}
        onThemeChange={handleCrmAccountThemeChange}
        onModeChange={handleCrmAccountModeChange}
        securitySummary={buildCrmAccountSecuritySummary({
          accountUser: buildCrmAccountCommandCenterUser({
            userSource: typeof user === 'undefined' ? {} : user,
            accessSource: typeof access === 'undefined' ? {} : access,
            accountProfileSource: typeof accountProfile === 'undefined' ? {} : accountProfile,
            operatorSource: typeof crmResolvedOperatorIdentity === 'undefined' ? {} : crmResolvedOperatorIdentity,
            tenantSource: typeof tenantIdentity === 'undefined' ? {} : tenantIdentity
          }),
          readinessSource: typeof readiness === 'undefined' ? {} : readiness,
          accessSource: typeof access === 'undefined' ? {} : access
        })}
        complianceSummary={buildCrmAccountComplianceSummary({
          readinessSource: typeof readiness === 'undefined' ? {} : readiness,
          tenantSource: typeof tenantIdentity === 'undefined' ? {} : tenantIdentity
        })}
        sessionSummary={buildCrmAccountSessionSummary({
          accessSource: typeof access === 'undefined' ? {} : access,
          readinessSource: typeof readiness === 'undefined' ? {} : readiness
        })}/>
</div>
  );
};

export default CRMDashboard;


const WILSY_R9X_CLEAN_BODY_IDENTITY_RAIL = 'WILSY_R9X_CLEAN_BODY_IDENTITY_RAIL_ACTIVE';

/**
 * @function applyWilsyR9XStyle
 * @description Applies important inline styles for the final body-mounted CRM identity rail cleanup.
 * @collaboration Stabilizes R9W output without relying on earlier exact source blocks.
 */
const applyWilsyR9XStyle = (node, styles = {}) => {
  if (!node || !node.style) return;

  Object.entries(styles).forEach(([property, value]) => {
    const cssProperty = String(property).replace(/[A-Z]/g, match => `-${match.toLowerCase()}`);
    node.style.setProperty(cssProperty, value, 'important');
  });
};

/**
 * @function repairWilsyR9XCleanBodyIdentityRail
 * @description Removes duplicate dead rails and positions the body-mounted identity rail into non-overlapping header/evidence lanes.
 * @collaboration Keeps the readable R9W rail while preserving the restored account identity card, tenant selector, and operator name.
 */
const repairWilsyR9XCleanBodyIdentityRail = () => {
  if (typeof document === 'undefined' || typeof window === 'undefined') return;

  const overlay = document.querySelector('[class*="accountSettingsOverlay"]');
  const rail = document.querySelector('[data-wilsy-r9w-body-mounted-identity-rail="true"]');

  if (!overlay || !rail) return;

  const shellCandidates = Array.from(
    overlay.querySelectorAll('[data-wilsy-r9u-active-identity-shell="true"], [data-wilsy-r7c-identity-ui="true"], [data-wilsy-identity-chrome], [data-wilsy-r7c-identity-card="true"]')
  );

  const frames = shellCandidates
    .map(node => {
      const rect = node.getBoundingClientRect();
      return { node, rect, area: Math.max(0, rect.width) * Math.max(0, rect.height) };
    })
    .filter(item => item.rect.width >= 240 && item.rect.height >= 160)
    .sort((a, b) => b.area - a.area);

  const overlayRect = overlay.getBoundingClientRect();
  const rect = frames[0]?.rect || {
    left: overlayRect.left + 24,
    top: overlayRect.top + 24,
    width: Math.min(520, Math.max(380, overlayRect.width * 0.34)),
    height: 430
  };

  const contentLeft = rect.left + Math.min(230, Math.max(190, rect.width * 0.29));
  const contentWidth = Math.max(360, rect.right - contentLeft - 40);

  applyWilsyR9XStyle(rail, {
    position: 'fixed',
    zIndex: '2147483647',
    left: `${contentLeft}px`,
    top: `${rect.top + 38}px`,
    width: `${contentWidth}px`,
    minWidth: `${contentWidth}px`,
    maxWidth: `${contentWidth}px`,
    height: '260px',
    minHeight: '260px',
    maxHeight: '260px',
    display: 'block',
    pointerEvents: 'none',
    overflow: 'visible',
    background: 'transparent',
    contain: 'none',
    clipPath: 'none',
    transform: 'translateZ(0)'
  });

  const header = rail.querySelector('[data-wilsy-r9w-body-mounted-identity-header="true"]');
  const evidence = rail.querySelector('[data-wilsy-r9w-body-mounted-identity-evidence="true"]');

  applyWilsyR9XStyle(header, {
    position: 'absolute',
    left: '0',
    top: '0',
    width: '100%',
    minWidth: '100%',
    maxWidth: '100%',
    display: 'flex',
    flexWrap: 'nowrap',
    alignItems: 'center',
    justifyContent: 'flex-start',
    gap: '18px',
    overflow: 'visible',
    whiteSpace: 'nowrap'
  });

  header?.querySelectorAll('span').forEach((node) => {
    applyWilsyR9XStyle(node, {
      display: 'inline-flex',
      flex: '0 0 auto',
      width: 'max-content',
      minWidth: 'max-content',
      maxWidth: 'none',
      overflow: 'visible',
      textOverflow: 'clip',
      whiteSpace: 'nowrap',
      letterSpacing: '0.10em',
      fontSize: '10px',
      lineHeight: '1',
      fontWeight: '900',
      textTransform: 'uppercase'
    });
  });

  applyWilsyR9XStyle(evidence, {
    position: 'absolute',
    left: '0',
    top: '176px',
    width: '100%',
    minWidth: '100%',
    maxWidth: '100%',
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    justifyContent: 'flex-start',
    gap: '8px 14px',
    overflow: 'visible',
    whiteSpace: 'normal'
  });

  evidence?.querySelectorAll('span').forEach((node) => {
    applyWilsyR9XStyle(node, {
      display: 'inline-flex',
      flex: '0 0 auto',
      width: 'max-content',
      minWidth: 'max-content',
      maxWidth: 'none',
      overflow: 'visible',
      textOverflow: 'clip',
      whiteSpace: 'nowrap',
      letterSpacing: '0.08em',
      fontSize: '9px',
      lineHeight: '1',
      fontWeight: '900',
      textTransform: 'uppercase'
    });
  });

  overlay
    .querySelectorAll([
      '.wilsy-r7c-identity-eyebrow',
      '.wilsy-r7c-command-label',
      '.wilsy-r7c-verified-label',
      '.wilsy-r7f-identity-evidence',
      '.wilsy-r7f-clause-anchor',
      '.wilsy-r7f-identity-seal',
      '[data-wilsy-r9v-readable-identity-header="true"]',
      '[data-wilsy-r9v-readable-identity-evidence="true"]'
    ].join(', '))
    .forEach((node) => {
      node.setAttribute('data-wilsy-r9x-hidden-duplicate-identity-rail', 'true');
      applyWilsyR9XStyle(node, {
        display: 'none',
        opacity: '0',
        visibility: 'hidden',
        pointerEvents: 'none',
        width: '0',
        minWidth: '0',
        maxWidth: '0',
        height: '0',
        minHeight: '0',
        maxHeight: '0',
        overflow: 'hidden',
        color: 'transparent',
        textShadow: 'none'
      });
    });
};

/**
 * @function scheduleWilsyR9XCleanBodyIdentityRail
 * @description Schedules the final identity rail cleanup after CRM overlay paint and interaction frames.
 * @collaboration Ensures R9W remains readable without duplicating the original dead rails.
 */
const scheduleWilsyR9XCleanBodyIdentityRail = () => {
  if (typeof window === 'undefined') return;

  [0, 40, 120, 260, 520, 900, 1500, 2400].forEach((delay) => {
    window.setTimeout(repairWilsyR9XCleanBodyIdentityRail, delay);
  });
};

/**
 * @function bootWilsyR9XCleanBodyIdentityRail
 * @description Boots the resilient cleanup layer for the body-mounted CRM identity rail.
 * @collaboration Finalizes the Account Command Center CRM overlay after R9W mounted the readable rail.
 */
const bootWilsyR9XCleanBodyIdentityRail = () => {
  if (typeof window === 'undefined' || window.__wilsyR9XCleanBodyIdentityRailBooted) return;

  window.__wilsyR9XCleanBodyIdentityRailBooted = true;
  scheduleWilsyR9XCleanBodyIdentityRail();

  window.addEventListener('click', scheduleWilsyR9XCleanBodyIdentityRail, { passive: true });
  window.addEventListener('focusin', scheduleWilsyR9XCleanBodyIdentityRail, { passive: true });
  window.addEventListener('resize', scheduleWilsyR9XCleanBodyIdentityRail, { passive: true });
  window.addEventListener('scroll', scheduleWilsyR9XCleanBodyIdentityRail, { passive: true });
};

bootWilsyR9XCleanBodyIdentityRail();


const WILSY_R9Y_SINGLE_SOURCE_IDENTITY_RAIL = 'WILSY_R9Y_SINGLE_SOURCE_IDENTITY_RAIL_ACTIVE';

/**
 * @function applyWilsyR9YStyle
 * @description Applies important inline styles for the single-source CRM identity rail cleanup.
 * @collaboration Removes the duplicate body-mounted rail while preserving the restored Account Command Center card.
 */
const applyWilsyR9YStyle = (node, styles = {}) => {
  if (!node || !node.style) return;

  Object.entries(styles).forEach(([property, value]) => {
    const cssProperty = String(property).replace(/[A-Z]/g, match => `-${match.toLowerCase()}`);
    node.style.setProperty(cssProperty, value, 'important');
  });
};

/**
 * @function ensureWilsyR9YNoDuplicateStyleSheet
 * @description Installs a defensive stylesheet that prevents body-mounted identity duplicates from rendering.
 * @collaboration Guarantees R9W/R9X rails cannot visually duplicate the in-card identity source.
 */
const ensureWilsyR9YNoDuplicateStyleSheet = () => {
  if (typeof document === 'undefined') return;

  if (document.querySelector('[data-wilsy-r9y-no-duplicate-identity-style="true"]')) return;

  const style = document.createElement('style');
  style.setAttribute('data-wilsy-r9y-no-duplicate-identity-style', 'true');
  style.textContent = `
    [data-wilsy-r9w-body-mounted-identity-rail="true"],
    [data-wilsy-r9v-readable-identity-header="true"],
    [data-wilsy-r9v-readable-identity-evidence="true"] {
      display: none !important;
      opacity: 0 !important;
      visibility: hidden !important;
      pointer-events: none !important;
    }
  `;

  document.head.appendChild(style);
};

/**
 * @function repairWilsyR9YSingleSourceIdentityRail
 * @description Removes duplicate body-mounted identity rails and restores the in-card rails as the single visible identity source.
 * @collaboration Stabilizes the CRM Account Command Center card after the R9W body-mounted rail caused duplicated command/evidence text.
 */
const repairWilsyR9YSingleSourceIdentityRail = () => {
  if (typeof document === 'undefined') return;

  ensureWilsyR9YNoDuplicateStyleSheet();

  document
    .querySelectorAll('[data-wilsy-r9w-body-mounted-identity-rail="true"]')
    .forEach((node) => node.remove());

  const overlay = document.querySelector('[class*="accountSettingsOverlay"]');
  if (!overlay) return;

  overlay.setAttribute('data-wilsy-r9y-single-source-identity-fixed', 'true');

  overlay
    .querySelectorAll('[data-wilsy-r9v-readable-identity-header="true"], [data-wilsy-r9v-readable-identity-evidence="true"]')
    .forEach((node) => {
      node.setAttribute('data-wilsy-r9y-hidden-duplicate-generated-rail', 'true');
      applyWilsyR9YStyle(node, {
        display: 'none',
        opacity: '0',
        visibility: 'hidden',
        pointerEvents: 'none',
        width: '0',
        height: '0',
        overflow: 'hidden'
      });
    });

  overlay
    .querySelectorAll('.wilsy-r7c-identity-eyebrow')
    .forEach((node) => {
      node.setAttribute('data-wilsy-r9y-single-source-eyebrow', 'true');
      applyWilsyR9YStyle(node, {
        display: 'flex',
        flexWrap: 'nowrap',
        alignItems: 'center',
        justifyContent: 'flex-start',
        gap: '18px',
        opacity: '1',
        visibility: 'visible',
        width: '100%',
        minWidth: '100%',
        maxWidth: '100%',
        height: 'auto',
        overflow: 'visible',
        whiteSpace: 'nowrap'
      });
    });

  overlay
    .querySelectorAll('.wilsy-r7c-command-label, .wilsy-r7c-verified-label')
    .forEach((node) => {
      node.setAttribute('data-wilsy-r9y-single-source-label', 'true');
      applyWilsyR9YStyle(node, {
        display: 'inline-flex',
        flex: '0 0 auto',
        opacity: '1',
        visibility: 'visible',
        width: 'max-content',
        minWidth: 'max-content',
        maxWidth: 'none',
        height: 'auto',
        overflow: 'visible',
        textOverflow: 'clip',
        whiteSpace: 'nowrap',
        letterSpacing: '0.10em',
        fontSize: '10px',
        lineHeight: '1',
        fontWeight: '900',
        textTransform: 'uppercase'
      });
    });

  overlay
    .querySelectorAll('.wilsy-r7f-identity-evidence')
    .forEach((node) => {
      node.setAttribute('data-wilsy-r9y-single-source-evidence', 'true');
      applyWilsyR9YStyle(node, {
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'flex-start',
        gap: '8px 14px',
        opacity: '1',
        visibility: 'visible',
        width: '100%',
        minWidth: '100%',
        maxWidth: '100%',
        height: 'auto',
        overflow: 'visible',
        whiteSpace: 'normal'
      });
    });

  overlay
    .querySelectorAll('.wilsy-r7f-clause-anchor, .wilsy-r7f-identity-seal')
    .forEach((node) => {
      node.setAttribute('data-wilsy-r9y-single-source-evidence-label', 'true');
      applyWilsyR9YStyle(node, {
        display: 'inline-flex',
        flex: '0 0 auto',
        opacity: '1',
        visibility: 'visible',
        width: 'max-content',
        minWidth: 'max-content',
        maxWidth: 'none',
        height: 'auto',
        overflow: 'visible',
        textOverflow: 'clip',
        whiteSpace: 'nowrap',
        letterSpacing: '0.08em',
        fontSize: '9px',
        lineHeight: '1',
        fontWeight: '900',
        textTransform: 'uppercase'
      });
    });
};

/**
 * @function scheduleWilsyR9YSingleSourceIdentityRail
 * @description Schedules the no-duplicate identity cleanup after CRM overlay paint and interaction frames.
 * @collaboration Runs after R9W/R9X so the body-mounted duplicate is removed and the original in-card rails remain the only source.
 */
const scheduleWilsyR9YSingleSourceIdentityRail = () => {
  if (typeof window === 'undefined') return;

  [0, 40, 120, 260, 520, 900, 1500, 2400].forEach((delay) => {
    window.setTimeout(repairWilsyR9YSingleSourceIdentityRail, delay);
  });
};

/**
 * @function bootWilsyR9YSingleSourceIdentityRail
 * @description Boots the single-source CRM identity rail cleanup.
 * @collaboration Finalizes the CRM Account Command Center by preventing duplicate identity and evidence rails.
 */
const bootWilsyR9YSingleSourceIdentityRail = () => {
  if (typeof window === 'undefined' || window.__wilsyR9YSingleSourceIdentityRailBooted) return;

  window.__wilsyR9YSingleSourceIdentityRailBooted = true;
  scheduleWilsyR9YSingleSourceIdentityRail();

  window.addEventListener('click', scheduleWilsyR9YSingleSourceIdentityRail, { passive: true });
  window.addEventListener('focusin', scheduleWilsyR9YSingleSourceIdentityRail, { passive: true });
  window.addEventListener('resize', scheduleWilsyR9YSingleSourceIdentityRail, { passive: true });
  window.addEventListener('scroll', scheduleWilsyR9YSingleSourceIdentityRail, { passive: true });
};

bootWilsyR9YSingleSourceIdentityRail();


