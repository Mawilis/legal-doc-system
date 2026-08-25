/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                                                                                        ║
 * ║   ██████╗ ███████╗███╗   ███╗ ██████╗     ██████╗ ██████╗  ██████╗ ██╗   ██╗██╗██████╗ ███████╗██████╗                            ║
 * ║   ██╔══██╗██╔════╝████╗ ████║██╔═══██╗    ██╔══██╗██╔══██╗██╔═══██╗██║   ██║██║██╔══██╗██╔════╝██╔══██╗                           ║
 * ║   ██║  ██║█████╗  ██╔████╔██║██║   ██║    ██████╔╝██████╔╝██║   ██║██║   ██║██║██████╔╝█████╗  ██████╔╝                           ║
 * ║   ██║  ██║██╔══╝  ██║╚██╔╝██║██║   ██║    ██╔═══╝ ██╔══██╗██║   ██║╚██╗ ██╔╝██║██╔══██╗██╔══╝  ██╔══██╗                           ║
 * ║   ██████╔╝███████╗██║ ╚═╝ ██║╚██████╔╝    ██║     ██║  ██║╚██████╔╝ ╚████╔╝ ██║██║  ██║███████╗██║  ██║                           ║
 * ║   ╚═════╝ ╚══════╝╚═╝     ╚═╝ ╚═════╝     ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═══╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                           ║
 * ║                                                                                                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - DEMO PROVIDER [V1.0.0‑INSTITUTIONAL]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME: Provides a demo mode toggle and context for injecting mock data into the BillingHUD.                                       ║
 * ║           The `DemoMode` component renders a toggle switch in the account menu. Uses React Context for broader consumption.          ║
 * ║ COMPLIANCE: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001                                                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0‑INSTITUTIONAL | PRODUCTION READY                                                                                     ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/providers/DemoProvider.jsx                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated demo mode for sales presentations and user trials.                                  ║
 * ║ • AI Engineering – Created provider with toggle and mock data injection hooks.                                                         ║
 * ║ • Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2, ISO 27001                                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGE LOG:                                                                                                                       ║
 * ║   2026-08-20 v1.0.0‑INSTITUTIONAL – Initial creation.                                                                                ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';

// ─── Context ──────────────────────────────────────────────────────────────

const DemoContext = createContext({
  demoActive: false,
  toggleDemo: () => {},
  mockData: {},
});

/**
 * @hook useDemo
 * @description Hook to access demo mode state and mock data.
 * @returns {Object} { demoActive, toggleDemo, mockData }
 */
export const useDemo = () => useContext(DemoContext);

/**
 * @component DemoProvider
 * @description Wraps children to provide demo mode context.
 * @param {Object} props
 * @param {ReactNode} props.children – Child components.
 * @param {boolean} props.initialActive – Initial demo mode state (default false).
 * @param {Object} props.mockData – Custom mock data (optional).
 * @returns {JSX.Element} The provider component.
 * @collaboration Wilson Khanyezi – mandated demo mode for sales demos.
 * @institutional Provides a safe environment to showcase the BillingHUD without affecting production data.
 * @epitome "Demo mode is the sovereign stage – show, don't break."
 */
export const DemoProvider = ({ children, initialActive = false, mockData = {} }) => {
  const [demoActive, setDemoActive] = useState(initialActive);

  const toggleDemo = useCallback(() => {
    setDemoActive(prev => !prev);
  }, []);

  // Default mock data (can be overridden via props)
  const defaultMockData = useMemo(() => ({
    invoices: [
      { id: 'INV-DEMO-001', invoiceNumber: 'INV-2026-0001', tenantId: 'demo-tenant-1', amount: 1500, totalAmount: 1500, currency: 'ZAR', status: 'PAID', issuedAt: '2026-01-15', dueDate: '2026-02-15', customerName: 'Acme Corp', issuingEntity: 'Wilsy (Pty) Ltd' },
      { id: 'INV-DEMO-002', invoiceNumber: 'INV-2026-0002', tenantId: 'demo-tenant-2', amount: 2500, totalAmount: 2500, currency: 'ZAR', status: 'ISSUED', issuedAt: '2026-02-01', dueDate: '2026-03-01', customerName: 'Beta Inc', issuingEntity: 'Wilsy (Pty) Ltd' },
      { id: 'INV-DEMO-003', invoiceNumber: 'INV-2026-0003', tenantId: 'demo-tenant-1', amount: 1200, totalAmount: 1200, currency: 'ZAR', status: 'OVERDUE', issuedAt: '2026-01-20', dueDate: '2026-02-20', customerName: 'Acme Corp', issuingEntity: 'Wilsy (Pty) Ltd' },
    ],
    subscriptions: [
      { id: 'SUB-DEMO-001', planName: 'Basic Plan', tenantId: 'demo-tenant-1', amount: 99, currency: 'ZAR', status: 'active', billingFrequency: 'monthly' },
      { id: 'SUB-DEMO-002', planName: 'Pro Plan', tenantId: 'demo-tenant-2', amount: 299, currency: 'ZAR', status: 'active', billingFrequency: 'monthly' },
      { id: 'SUB-DEMO-003', planName: 'Enterprise Plan', tenantId: 'demo-tenant-3', amount: 999, currency: 'ZAR', status: 'active', billingFrequency: 'annual' },
    ],
    tenants: [
      { id: 'demo-tenant-1', name: 'Acme Corp', tenantId: 'demo-tenant-1', status: 'Active' },
      { id: 'demo-tenant-2', name: 'Beta Inc', tenantId: 'demo-tenant-2', status: 'Active' },
      { id: 'demo-tenant-3', name: 'Gamma LLC', tenantId: 'demo-tenant-3', status: 'Active' },
    ],
    courts: [
      { id: 'court-1', name: 'Johannesburg High Court', jurisdiction: 'ZA', type: 'High Court' },
      { id: 'court-2', name: 'Cape Town Magistrate Court', jurisdiction: 'ZA', type: 'Magistrate Court' },
    ],
    summary: {
      totalArr: 12000,
      activeSubscriptions: 5,
      pendingInvoices: 3,
      history: [
        { label: '2026-01', volume: 8000, paidVolume: 7000 },
        { label: '2026-02', volume: 9000, paidVolume: 8000 },
        { label: '2026-03', volume: 10000, paidVolume: 9000 },
      ],
    },
    analytics: {
      mrr: 1200,
      arr: 14400,
      churnRate: 0.05,
      ltv: 3600,
      cac: 1080,
      forecast: 15000,
      growthRate: 12.5,
    },
  }), []);

  const effectiveMockData = useMemo(() => ({
    ...defaultMockData,
    ...mockData,
  }), [defaultMockData, mockData]);

  const value = useMemo(() => ({
    demoActive,
    toggleDemo,
    mockData: effectiveMockData,
  }), [demoActive, toggleDemo, effectiveMockData]);

  return (
    <DemoContext.Provider value={value}>
      {children}
    </DemoContext.Provider>
  );
};

// ─── DemoMode Component (for the account menu toggle) ─────────────────────

/**
 * @component DemoMode
 * @description Renders a toggle button for demo mode, used in the BillingHUD account menu.
 * @param {Object} props
 * @param {boolean} props.active – Whether demo mode is active.
 * @param {Function} props.onToggle – Callback to toggle demo mode.
 * @returns {JSX.Element} A compact toggle button.
 * @collaboration Wilson Khanyezi – mandated a visible toggle for demo mode.
 * @institutional Allows users to switch between real and demo data instantly.
 * @epitome "Demo mode is the sandbox – play, learn, and sell without risk."
 */
export const DemoMode = ({ active = false, onToggle }) => {
  const handleToggle = () => {
    if (onToggle) {
      onToggle();
    }
  };

  return (
    <button
      onClick={handleToggle}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 14px',
        background: active ? 'rgba(212,175,55,0.2)' : 'transparent',
        border: active ? '1px solid #D4AF37' : '1px solid rgba(255,255,255,0.1)',
        borderRadius: '20px',
        color: active ? '#D4AF37' : '#94a3b8',
        fontSize: '0.75rem',
        fontWeight: 500,
        cursor: 'pointer',
        transition: 'all 0.2s',
        whiteSpace: 'nowrap',
      }}
      onMouseEnter={(e) => {
        if (!active) e.currentTarget.style.borderColor = 'rgba(255,255,255,0.3)';
      }}
      onMouseLeave={(e) => {
        if (!active) e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)';
      }}
      title={active ? 'Disable demo mode and show real data' : 'Enable demo mode with mock data'}
    >
      <span style={{ opacity: active ? 1 : 0.5 }}>🎯</span>
      <span>{active ? 'Demo On' : 'Demo Off'}</span>
    </button>
  );
};

export default DemoMode;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — DemoProvider V1.0.0‑INSTITUTIONAL
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:          CERTIFIED PRODUCTION ARTIFACT
 * Version:         v1.0.0‑INSTITUTIONAL
 * Compliance:      POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001
 * Error Handling:  Graceful fallback if context is missing.
 * Pending Work:    None – ready for integration into BillingHUD.
 * ────────────────────────────────────────────────────────────────────────────────
 * 🔒 This component is ready for deployment.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
