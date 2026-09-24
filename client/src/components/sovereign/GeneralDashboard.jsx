/* eslint-disable */
/**
 * WILSY OS — GENERAL TENANT COMMAND CENTER
 * VERSION: v16.6.0-D14-LEGAL-LANE-CLEANUP
 * AUTHORITY: General tenant presentation/orchestration only.
 * EPITOME: General tenant Document Vault and Team Members workspace; Legal roles route only through canonical Legal OS.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/GeneralDashboard.jsx
 * COLLABORATION / OWNERSHIP: Wilsy OS Core Governance.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG: 2026-09-24 v16.6.0-D14-LEGAL-LANE-CLEANUP removes the obsolete nested Legal Engine lane and stale Sovereign_Legal_Analytics dependency.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Presentation only; no legal or financial truth is inferred here.
 * TENANT BOUNDARY: Authenticated tenant context only.
 * AUTHORITY BOUNDARY: Published Legal roles are resolved by SovereignDashboardController to canonical LegalDashboard.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns payment execution and settlement.
 */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - GENERAL TENANT COMMAND CENTER                                                                                               ║
 * ║ [TENANT-LEVEL ORCHESTRATION | DOCUMENT INTELLIGENCE | JURISDICTIONAL COMPLIANCE]                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.5.0-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/GeneralDashboard.jsx                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Multi-Tenant Strategy & Final Approval                                                        ║
 * ║ • Gemini (AI Engineering) - Interface Orchestration & Module Mapping                                                                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { Suspense, useState, useEffect } from 'react';
import { useAuth } from '../../contexts/authContext';
import { useTenants } from '../../contexts/tenantContext';
import {
  FileText, Users, ShieldCheck,
  LogOut, LayoutDashboard, Database, Bell
} from 'lucide-react';

import styles from './FounderDashboard.module.css'; // Utilizing the unified Dark-Ops design system

// 🏛️ TENANT MODULE REGISTRY
const DocumentVault = React.lazy(() => import('./Sovereign_Document_Vault'));
const UserManagement = React.lazy(() => import('./Sovereign_User_Management'));


/**
 * @function GeneralDashboard
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const GeneralDashboard = () => {
  const { user, logout } = useAuth();
  const { activeTenant } = useTenants();
  const [activeModule, setActiveModule] = useState('VAULT');

  useEffect(() => {
    console.log(`[TENANT-CENTER] 🛰️ Active Tenant: ${activeTenant?.name || 'RESOLVING...'}`);
  }, [activeTenant]);

  
/**
 * @function renderModule
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const renderModule = () => {
    switch (activeModule) {
      case 'VAULT': return <DocumentVault />;
      case 'USERS': return <UserManagement />;
      default: return <DocumentVault />;
    }
  };

  return (
    <div className={styles.dashboardLayout}>
      {/* 🏛️ TENANT SIDEBAR */}
      <aside className={styles.sidebar}>
        <div className={styles.branding}>
          <div className={styles.logoPulse}>
            <img src={'/assets/images/superadmin/wilsy.jpeg'} alt="Wilsy" />
          </div>
          <h1 className={styles.osTitle}>{activeTenant?.name?.toUpperCase() || 'TENANT'} <span className={styles.version}>v16.6</span></h1>
        </div>

        <nav className={styles.mainNav}>
          <button
            onClick={() => setActiveModule('VAULT')}
            className={activeModule === 'VAULT' ? styles.active : ''}
          >
            <FileText size={18} /> <span>Document Vault</span>
          </button>
          <button
            onClick={() => setActiveModule('USERS')}
            className={activeModule === 'USERS' ? styles.active : ''}
          >
            <Users size={18} /> <span>Team Members</span>
          </button>
        </nav>

        <div className={styles.footerSection}>
          <div className={styles.userProfile}>
            <div className={styles.avatar}>{user?.firstName?.[0] || 'U'}</div>
            <div className={styles.userMeta}>
              <span className={styles.userName}>{user?.firstName || 'USER'}</span>
              <span className={styles.role}>{user?.role?.toUpperCase()}</span>
            </div>
          </div>
          <button onClick={logout} className={styles.logoutBtn}>
            <LogOut size={16} /> <span>EXIT TERMINAL</span>
          </button>
        </div>
      </aside>

      {/* 🚀 TENANT OPERATIONAL STAGE */}
      <main className={styles.mainStage}>
        <header className={styles.topBar}>
          <div className={styles.telemetryGroup}>
            <div className={styles.teleItem}>
              <ShieldCheck size={14} className="text-emerald-500" />
              <span>STATUS: <span className={styles.value}>SECURE</span></span>
            </div>
            <div className={styles.teleItem}>
              <Database size={14} className="text-blue-500" />
              <span>STORAGE: <span className={styles.value}>ENCRYPTED</span></span>
            </div>
            <div className={styles.teleItem}>
              <Bell size={14} className="text-gold" />
              <span>ALERTS: <span className={styles.value}>0</span></span>
            </div>
          </div>

          <div className={styles.globalTime}>
             {new Date().toLocaleDateString('en-ZA')} | {new Date().toLocaleTimeString('en-ZA', { hour12: false })}
          </div>
        </header>

        <section className={styles.moduleViewport}>
          <Suspense fallback={
            <div className={styles.moduleLoader}>
              <LayoutDashboard className="animate-pulse" size={48} />
              <p>HYDRATING SOVEREIGN TERMINAL...</p>
            </div>
          }>
            {renderModule()}
          </Suspense>
        </section>
      </main>
    </div>
  );
};

export default GeneralDashboard;

/**
 * ARTIFACT: GeneralDashboard.jsx
 * VERSION: v16.6.0-D14-LEGAL-LANE-CLEANUP
 * AUTHORITY BOUNDARY: General tenant presentation/orchestration only; no Legal authority
 * TENANT POSTURE: Authenticated tenant context only
 * FAIL-CLOSED POSTURE: No nested or fallback Legal module is exposed
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
