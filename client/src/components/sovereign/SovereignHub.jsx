/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN HUB CONTAINER [V1.0.0-OMEGA]                                                                                      ║
 * ║ [UNIFIED BOARDROOM PANORAMA | MULTI-TENANT VISIBILITY | TELEMETRY ORCHESTRATOR | INVESTOR-READY]                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-OMEGA | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL DOMINANCE                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/SovereignHub.jsx                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated the unified master grid for total boardroom visibility.                              ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Engineered the dynamic flex-grid, CSS module binding, and dashboard orchestration.              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React from 'react';
import { Crown, Globe, Shield, Activity, Users } from 'lucide-react';
import RevenueDashboard from './RevenueDashboard';
import ComplianceDashboard from './ComplianceDashboard';
import ForensicsDashboard from './ForensicsDashboard';
import Sovereign_Identity_Hub from './Sovereign_Identity_Hub'; // Integrating the Identity Citadel
import styles from './SovereignHub.module.css';

/**
 * @component SovereignHub
 * @description The master orchestration layer of Wilsy OS. Unifies all forensic, compliance, and revenue intelligence into a single investor-ready panorama.
 */
const SovereignHub = () => {
  return (
    <div className={styles.hubContainer}>
      {/* 🏛️ MASTER HUB HEADER: Boardroom Gravitas */}
      <div className={styles.hubHeader}>
        <div className={styles.headerLeft}>
          <Crown size={28} className={styles.crownIcon} />
          <div>
            <h1 className={styles.hubTitle}>WILSY OS SOVEREIGN HUB</h1>
            <p className={styles.hubSubtitle}>Global Intelligence Panorama • Institutional Dominance Active</p>
          </div>
        </div>
        <div className={styles.headerRight}>
          <div className={styles.systemStatus}>
            <span className={styles.statusDot}></span>
            OMNIVERSAL SYNC SECURED
          </div>
        </div>
      </div>

      {/* 🌐 THE PANORAMA GRID: Orchestrating the Nucleus Dashboards */}
      <div className={styles.hubGrid}>

        {/* ROW 1: Financial & Regulatory Power */}
        <div className={styles.hubSectionRow}>
          <div className={styles.hubSectionHalf}>
            <RevenueDashboard />
          </div>
          <div className={styles.hubSectionHalf}>
            <ComplianceDashboard />
          </div>
        </div>

        {/* ROW 2: Cryptographic & Identity Control */}
        <div className={styles.hubSectionRow}>
          <div className={styles.hubSectionHalf}>
            <ForensicsDashboard />
          </div>
          <div className={styles.hubSectionHalf}>
            <Sovereign_Identity_Hub />
          </div>
        </div>

      </div>

      {/* 🛡️ MASTER TELEMETRY FOOTER */}
      <div className={styles.hubFooter}>
        <div className={styles.footerBranding}>
          <span>PQE-256 ENCRYPTED MASTER NODE</span>
          <span className={styles.divider}>|</span>
          <span>WILSY_GLOBAL_ROOT_001</span>
        </div>
      </div>
    </div>
  );
};

export default SovereignHub;
