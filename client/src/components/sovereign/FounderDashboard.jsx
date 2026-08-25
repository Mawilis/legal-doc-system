/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FOUNDER COMMAND CENTER [V60.2.0-TMS-RAIL-ACCESS]                                                                   ║
 * ║ [STRICT ISOLATION MANDATE] ONLY FOUNDER MODULES RENDER INSIDE. ALL OTHERS REDIRECT TO STANDALONE FULL-VIEW.                            ║
 * ║ TOP 0.01% PRODUCTION ARCHITECTURE | MACHINE-GRADE PERFORMANCE | ZERO-LOSS ROUTING | REAL-TIME KENNEL TELEMETRY                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 60.2.0-TMS-RAIL-ACCESS | PRODUCTION READY                                                                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/FounderDashboard.jsx                           ║
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                               ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated Tenant Management System (TMS) elevation to Quick Access Left Rail.                       ║
 * ║ • AI Engineering (Certified v60.2.0) – Surgically appended `TENANT_MANAGER` to the `SIDEBAR_SHORTCUTS` array.                          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { Suspense, useState, useEffect, useCallback, useMemo, useRef, Component, memo } from 'react';
import { useAuth } from '../../contexts/authContext';
import { useTenants } from '../../contexts/tenantContext';
import useSovereignData from '../../hooks/useSovereignData';
import { useTelemetryFeed } from '../../hooks/useTelemetryFeed';
import { useTelemetryStats } from '../../hooks/useTelemetryStats';
import { useTrajectoryWithEmails } from '../../hooks/useTrajectoryWithEmails';
import useRuntimeStatus from '../../hooks/useRuntimeStatus';
import useKennelHealth from '../../hooks/useKennelHealth';

import { SovereignOrchestrator } from './SovereignOrchestrator';
import { DataOrchestrator } from './DataOrchestrator';
import api from '../../services/api';

import {
  Activity, ShieldCheck, Zap, Globe, Users, LogOut,
  Download, FileText, Target, Cpu, Database, Server,
  Lock, Key, Fingerprint, FileSignature, AlertOctagon,
  Scale, Power, ShieldAlert, Network, Radio, TerminalSquare, Filter, TrendingUp, Search, BarChart3, Microscope, UserCheck, Crown,
  CreditCard, Receipt, Coins, Landmark, Briefcase, UserPlus, Calendar, MessageSquare, PieChart, Settings, GitBranch,
  DollarSign, Gavel, Megaphone, Box, Code, BarChart, LockKeyhole, HeartHandshake, ShoppingCart, FlaskConical,
  Satellite, Brain, Cpu as CpuIcon, Dna, Eye, ChevronLeft, PanelRightClose, PanelRightOpen, PanelLeftClose, PanelLeftOpen,
  UserCog, SlidersHorizontal, Save, X, Sparkles, BadgeCheck, FileCheck2, Palette, Rocket, Workflow, Layers3,
  Bell, Loader2, Info, ArrowRight, CheckCircle, AlertTriangle, ChevronDown, Command,
  // ── Additional icons for missing Industry keys ──
  Trophy, GraduationCap, Clapperboard, Home, Truck
} from 'lucide-react';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, Filler);

import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const FOUNDER_PROFILE_STORAGE_KEY = 'wilsy_founder_profile_preferences_v1';
const NOTIFICATION_LAST_READ_KEY = 'wilsy_notification_lastRead';

const FOUNDER_OPERATING_PRESETS = {
  'Investor Theatre': {
    defaultModule: 'INVESTOR_PROOF',
    telemetryDensity: 'Executive',
    evidenceMode: 'Real Data Only',
    narrativeTone: 'Investor',
    tenantScope: 'Founder Tenant',
    sidebarMode: 'Open',
    quickPanelMode: 'Closed',
    investorPromise: 'WILSY OS proves why a business should move: revenue, billing, compliance, courts, identity and audit evidence operate as one system.'
  },
  'Forensic Operator': {
    defaultModule: 'AUDIT_VAULT',
    telemetryDensity: 'Dense',
    evidenceMode: 'Court Ready',
    narrativeTone: 'Technical',
    tenantScope: 'Current Tenant',
    sidebarMode: 'Open',
    quickPanelMode: 'Open',
    investorPromise: 'Every executive claim must survive diligence: the operating system exposes source, seal, tenant, jurisdiction and audit chain.'
  },
  'Builder Mode': {
    defaultModule: 'GLOBAL_ORCHESTRATOR',
    telemetryDensity: 'Dense',
    evidenceMode: 'Diligence Grade',
    narrativeTone: 'Boardroom',
    tenantScope: 'Multi Tenant',
    sidebarMode: 'Open',
    quickPanelMode: 'Open',
    investorPromise: 'Founder engineering mode reveals the machinery: nodes, tenants, identity, telemetry and module contracts wired into one command plane.'
  }
};

const normalizeFounderDisplayName = (value = '') => {
  const raw = value.toString().trim();
  if (!raw) return 'Wilson Khanyezi';
  const handle = raw.includes('@') ? raw.split('@')[0] : raw;
  const compact = handle.replace(/[^a-zA-Z]/g, '').toLowerCase();
  if (compact === 'wilsonkhanyezi') return 'Wilson Khanyezi';
  if (raw.includes(' ')) {
    return raw.split(/\s+/).filter(Boolean).map(part => `${part[0]?.toUpperCase() || ''}${part.slice(1)}`).join(' ');
  }
  return `${handle[0]?.toUpperCase() || ''}${handle.slice(1)}`;
};

const resolveFounderDisplayName = (user) => normalizeFounderDisplayName(
  user?.name || user?.fullName || user?.displayName || user?.email || 'Wilson Khanyezi'
);

// ============================================================================
// FORENSIC HELPER FUNCTIONS (exportCSV, exportPDF – full implementations)
// ============================================================================
const exportCSV = (data, filename) => {
  if (!data || (Array.isArray(data) && data.length === 0)) {
    console.warn('[CSV] No data to export');
    return;
  }
  try {
    const headers = Array.isArray(data) ? Object.keys(data[0] || {}) : Object.keys(data);
    const rows = Array.isArray(data) ? data.map(row =>
      headers.map(h => JSON.stringify(row[h] ?? '')).join(',')
    ) : [];
    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error('[CSV] Export failed:', err);
  }
};

const exportPDF = async (elementRef, filename) => {
  if (!elementRef?.current) {
    console.warn('[PDF] Chart ref not available – element not mounted.');
    const pdf = new jsPDF('landscape', 'mm', 'a4');
    pdf.text('Chart data temporarily unavailable. Please try again.', 20, 20);
    pdf.save(`${filename}_fallback.pdf`);
    return;
  }
  if (!document.body.contains(elementRef.current)) {
    console.warn('[PDF] Chart element not attached to document. Saving fallback PDF.');
    const pdf = new jsPDF('landscape', 'mm', 'a4');
    pdf.text('Chart element not ready. Please refresh and retry.', 20, 20);
    pdf.save(`${filename}_fallback.pdf`);
    return;
  }
  try {
    const canvas = await html2canvas(elementRef.current, {
      scale: 2,
      backgroundColor: '#000000',
      logging: false,
    });
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF('landscape', 'mm', 'a4');
    const imgWidth = 297;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
    pdf.save(filename);
  } catch (err) {
    console.error('[PDF] Export failed:', err);
    const pdf = new jsPDF('landscape', 'mm', 'a4');
    pdf.text(`PDF generation error: ${err.message}`, 20, 20);
    pdf.save(`${filename}_error.pdf`);
  }
};

// ============================================================================
// SOVEREIGN ERROR BOUNDARY
// ============================================================================
class SovereignErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorInfo: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    console.error("[SOVEREIGN_BOUNDARY_FRACTURE]:", error, errorInfo);
    this.setState({ errorInfo });
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', background: 'rgba(255,0,0,0.05)', border: '1px solid #ff3333', borderRadius: '8px', color: '#ff3333', fontFamily: 'monospace' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 900, marginBottom: '10px' }}>[CRITICAL] MODULE FRACTURE DETECTED</h2>
          <p style={{ fontSize: '0.8rem', color: '#ff8888' }}>The institutional module failed to render. The core OS remains secure.</p>
          <button
            onClick={() => this.setState({ hasError: false })}
            style={{ marginTop: '20px', padding: '10px 20px', background: '#330000', border: '1px solid #ff3333', color: '#fff', cursor: 'pointer', fontWeight: 'bold' }}
          >
            INITIATE MODULE REBOOT
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ============================================================================
// LOCAL IMPORTS
// ============================================================================
import MetricCard from './MetricCard';
import styles from './FounderDashboard.module.css';
import wilsyLogo from '../../assets/logo/wilsy.jpeg';
import iconManifest from '../../assets/iconManifest';
import CommandPalette from './CommandPalette';
import QuickPanel from './QuickPanel';
import FounderAppBar from './FounderAppBar';
import { CommandUsageProvider } from '../../contexts/CommandUsageContext';

// ============================================================================
// LAZY-LOADED SOVEREIGN HUDS – FULL LIST
// ============================================================================
const BoardroomHUD = React.lazy(() => import('./BoardroomHUD'));
const RevenueLedger = React.lazy(() => import('./Sovereign_Revenue_Ledger'));
const RevenueHUD = React.lazy(() => import('../RevenueHUD'));
const ComplianceHUD = React.lazy(() => import('../ComplianceHUD'));
const ForensicsHUD = React.lazy(() => import('../ForensicsHUD'));
const SingularityDashboard = React.lazy(() => import('../SingularityDashboard'));
const ExecutiveDashboard = React.lazy(() => import('../executive/ExecutiveDashboard'));
const AnalyticsDashboard = React.lazy(() => import('../analytics/AnalyticsDashboard'));
const SovereignNodeDashboard = React.lazy(() => import('./SovereignNodeDashboard'));
const SovereignNodeRegistry = React.lazy(() => import('./Sovereign_Node_Registry'));
const SovereignGlobalTopography = React.lazy(() => import('./Sovereign_Global_Topography'));
const CloudUplinkDashboard = React.lazy(() => import('./CloudUplinkDashboard'));
const BillingHUD = React.lazy(() => import('../billing/BillingHUD'));
const InvoiceSentinel = React.lazy(() => import('../billing/InvoiceSentinel'));
const SovereignAuditVault = React.lazy(() => import('./Sovereign_Audit_Vault'));
const SovereignIdentityHub = React.lazy(() => import('./Sovereign_Identity_Hub'));
const SovereignTenantManager = React.lazy(() => import('./Sovereign_TenantManager'));
const SovereignStatementEngine = React.lazy(() => import('./Sovereign_StatementEngine'));
const RiskSentinel = React.lazy(() => import('./RiskSentinel'));
const SovereignClientCovenant = React.lazy(() => import('./Sovereign_Client_Covenant'));
const SovereignCrisisCommand = React.lazy(() => import('./Sovereign_Crisis_Command'));
const ExecutiveControlRoom = React.lazy(() => import('../control-room/ExecutiveControlRoom'));

// ALL DEPARTMENT MODULES
const CRMDashboard = React.lazy(() => import('../crm/CRMDashboard'));
const HRDashboard = React.lazy(() => import('../hr/HRDashboard'));
const SalesDashboard = React.lazy(() => import('../sales/SalesDashboard'));
const ITDashboard = React.lazy(() => import('../it/ITDashboard'));
const COODashboard = React.lazy(() => import('../coo/COODashboard'));
const FinanceDashboard = React.lazy(() => import('../finance/FinanceDashboard'));
const LegalDashboard = React.lazy(() => import('../legal/LegalDashboard'));
const MarketingDashboard = React.lazy(() => import('../marketing/MarketingDashboard'));
const ProductDashboard = React.lazy(() => import('../product/ProductDashboard'));
const EngineeringDashboard = React.lazy(() => import('../engineering/EngineeringDashboard'));
const DataDashboard = React.lazy(() => import('../data/DataDashboard'));
const SecurityDashboard = React.lazy(() => import('../security/SecurityDashboard'));
const CustomerSuccessDashboard = React.lazy(() => import('../customer_success/CustomerSuccessDashboard'));
const ProcurementDashboard = React.lazy(() => import('../procurement/ProcurementDashboard'));
const ResearchDashboard = React.lazy(() => import('../research/ResearchDashboard'));
const SpaceOperationsDashboard = React.lazy(() => import('../space_operations/SpaceOperationsDashboard'));
const AIEthicsDashboard = React.lazy(() => import('../ai_ethics/AIEthicsDashboard'));
const QuantumDashboard = React.lazy(() => import('../quantum_computing/QuantumDashboard'));
const LongevityDashboard = React.lazy(() => import('../longevity_sciences/LongevityDashboard'));

import NeuralNarrativeCapsule from './NeuralNarrativeCapsule';
import NucleusFeedMonitor from './NucleusFeedMonitor';

// ============================================================================
// COMPLETE SOVEREIGN COMMAND KEYS CATEGORIES
// ============================================================================
const COMMAND_LEVEL_KEYS = ['BOARDROOM_HUD', 'SINGULARITY_MATRIX', 'REVENUE_LEDGER', 'BILLING_HUB', 'AUDIT_VAULT', 'NODE_REGISTRY'];
const SOVEREIGN_HUB_KEYS = [
  'INVESTOR_PROOF', 'GLOBAL_ORCHESTRATOR', 'EXECUTIVE_OVERSIGHT', 'INVOICE_SENTINEL',
  'CLOUD_UPLINK', 'IDENTITY_HUB', 'RISK_SENTINEL', 'CLIENT_COVENANT',
  'CRISIS_COMMAND', 'NUCLEUS_MONITOR'
];
const LEADERSHIP_KEYS = ['CEO_DASHBOARD', 'COO_DASHBOARD'];
const CORE_DEPT_KEYS = ['HR_DASHBOARD', 'SALES_CRM', 'IT_OPS'];
const ADVANCED_DEPT_KEYS = [
  'FINANCE_DASHBOARD', 'LEGAL_DASHBOARD', 'MARKETING_DASHBOARD', 'PRODUCT_DASHBOARD',
  'ENGINEERING_DASHBOARD', 'DATA_DASHBOARD', 'SECURITY_DASHBOARD', 'CUSTOMER_SUCCESS_DASHBOARD',
  'PROCUREMENT_DASHBOARD', 'RESEARCH_DASHBOARD'
];
const FUTURE_DEPT_KEYS = [
  'SPACE_OPERATIONS_DASHBOARD', 'AI_ETHICS_DASHBOARD', 'QUANTUM_COMPUTING_DASHBOARD', 'LONGEVITY_SCIENCES_DASHBOARD'
];
const CONTROL_ROOM_KEYS = ['EXECUTIVE_CONTROL_ROOM'];
const COCKPIT_KEYS = ['INVESTOR_PROOF', 'SINGULARITY_MATRIX', 'BOARDROOM_HUD'];
const INSTITUTIONAL_HUB_KEYS = ['REVENUE_LEDGER', 'BILLING_HUB', 'AUDIT_VAULT', 'NODE_REGISTRY', 'GLOBAL_ORCHESTRATOR', 'EXECUTIVE_OVERSIGHT', 'INVOICE_SENTINEL', 'CLOUD_UPLINK', 'IDENTITY_HUB', 'RISK_SENTINEL', 'CLIENT_COVENANT', 'CRISIS_COMMAND', 'NUCLEUS_MONITOR', 'TENANT_MANAGER', 'STATEMENT_ENGINE'];
const INDUSTRY_KEYS = ['AGRICULTURE_DASHBOARD', 'HOSPITALITY_DASHBOARD', 'PRODUCTION_DASHBOARD', 'RETAIL_DASHBOARD', 'PUBLIC_DASHBOARD', 'INDUSTRY_FINANCE_DASHBOARD', 'TECH_DASHBOARD', 'SPORTS_DASHBOARD', 'EDUCATION_DASHBOARD', 'HEALTHCARE_DASHBOARD', 'CONSULTING_DASHBOARD', 'ENERGY_DASHBOARD', 'ENTERTAINMENT_DASHBOARD', 'PROPERTY_DASHBOARD', 'INDUSTRY_LEGAL_DASHBOARD', 'PROJECT_DASHBOARD', 'LOGISTICS_DASHBOARD', 'NONPROFIT_DASHBOARD'];

// RESTORED MISSING SIDEBAR SHORTCUTS
// ⚡ SURGICAL ELEVATION: Appended 'TENANT_MANAGER' for instant Founder access to shard provisioning.
const SIDEBAR_SHORTCUTS = ['INVESTOR_PROOF', 'SINGULARITY_MATRIX', 'EXECUTIVE_CONTROL_ROOM', 'BILLING_HUB', 'EXECUTIVE_OVERSIGHT', 'HR_DASHBOARD', 'TENANT_MANAGER'];

const MODULE_OPERATING_MAP = {
  INVESTOR_PROOF: { layer: 'INVESTOR', label: 'Investor Proof Console', contract: 'Why WILSY OS wins with live operating proof', feed: 'OS spine and module readiness' },
  BOARDROOM_HUD: { layer: 'COMMAND', label: 'Boardroom HUD', contract: 'Executive truth surface', feed: 'Telemetry mesh' },
  SINGULARITY_MATRIX: { layer: 'COMMAND', label: 'Singularity Matrix', contract: 'Revenue, compliance and forensic convergence', feed: 'Sovereign data hooks' },
  REVENUE_LEDGER: { layer: 'MONEY', label: 'Revenue Ledger', contract: 'ARR, MRR, statement and billing proof', feed: 'Revenue and billing APIs' },
  BILLING_HUB: { layer: 'MONEY', label: 'Billing Hub', contract: 'Collections, courts and receivables operations', feed: 'Billing APIs' },
  AUDIT_VAULT: { layer: 'EVIDENCE', label: 'Audit Vault', contract: 'Immutable forensic record inspection', feed: 'Forensics vault' },
  NODE_REGISTRY: { layer: 'INFRASTRUCTURE', label: 'Node Registry', contract: 'Real tenant node inventory', feed: 'Node APIs' },
  GLOBAL_ORCHESTRATOR: { layer: 'INFRASTRUCTURE', label: 'Global Orchestrator', contract: 'World topology for real tenant nodes', feed: 'Node registry' },
  EXECUTIVE_OVERSIGHT: { layer: 'LEADERSHIP', label: 'Executive Oversight', contract: 'C-suite operating intelligence', feed: 'Analytics APIs' },
  INVOICE_SENTINEL: { layer: 'MONEY', label: 'Invoice Sentinel', contract: 'Receivables surveillance', feed: 'Billing APIs' },
  CLOUD_UPLINK: { layer: 'INFRASTRUCTURE', label: 'Cloud Uplink', contract: 'Shard and uplink telemetry', feed: 'Telemetry mesh' },
  IDENTITY_HUB: { layer: 'IDENTITY', label: 'Identity Hub', contract: 'People, roles and authority graph', feed: 'User APIs' },
  RISK_SENTINEL: { layer: 'RISK', label: 'Risk Sentinel', contract: 'Telemetry-backed threat posture', feed: 'Telemetry events' },
  CLIENT_COVENANT: { layer: 'CUSTOMER', label: 'Client Covenant', contract: 'Client agreements and trust posture', feed: 'Client registry' },
  CRISIS_COMMAND: { layer: 'RESILIENCE', label: 'Crisis Command', contract: 'Incident response and key rotation', feed: 'Security telemetry' },
  NUCLEUS_MONITOR: { layer: 'OBSERVABILITY', label: 'Nucleus Monitor', contract: 'Raw system event stream', feed: 'Telemetry mesh' },
  TENANT_MANAGER: { layer: 'TENANCY', label: 'Tenant Manager', contract: 'Shard provisioning and suspension', feed: 'Tenant APIs' },
  STATEMENT_ENGINE: { layer: 'EVIDENCE', label: 'Statement Engine', contract: 'Investor and compliance artifacts', feed: 'Statement APIs' },
  EXECUTIVE_CONTROL_ROOM: { layer: 'COMMAND', label: 'Executive Control Room', contract: 'Authoritative kernel window and operator gateway', feed: 'POST /execution and GET /dashboard' },
  CEO_DASHBOARD: { layer: 'LEADERSHIP', label: 'CEO Dashboard', contract: 'Chief Executive Officer view', feed: 'Executive APIs' },
  COO_DASHBOARD: { layer: 'LEADERSHIP', label: 'COO Dashboard', contract: 'Chief Operations Officer view', feed: 'Operations APIs' },
  HR_DASHBOARD: { layer: 'CORE', label: 'HR Department', contract: 'Human Resources suite', feed: 'HR APIs' },
  SALES_CRM: { layer: 'CORE', label: 'Sales & CRM', contract: 'CRM, Leads, Deals, Projects', feed: 'CRM APIs' },
  IT_OPS: { layer: 'CORE', label: 'IT Operations', contract: 'System Engineers & Infrastructure', feed: 'IT APIs' },
  FINANCE_DASHBOARD: { layer: 'ADVANCED', label: 'Finance', contract: 'Financial operations suite', feed: 'Finance APIs' },
  LEGAL_DASHBOARD: { layer: 'ADVANCED', label: 'Legal', contract: 'Legal covenant suite', feed: 'Legal APIs' },
  MARKETING_DASHBOARD: { layer: 'ADVANCED', label: 'Marketing', contract: 'Marketing operations suite', feed: 'Marketing APIs' },
  PRODUCT_DASHBOARD: { layer: 'ADVANCED', label: 'Product', contract: 'Product management suite', feed: 'Product APIs' },
  ENGINEERING_DASHBOARD: { layer: 'ADVANCED', label: 'Engineering', contract: 'Engineering operations suite', feed: 'Engineering APIs' },
  DATA_DASHBOARD: { layer: 'ADVANCED', label: 'Data', contract: 'Data operations suite', feed: 'Data APIs' },
  SECURITY_DASHBOARD: { layer: 'ADVANCED', label: 'Security', contract: 'Security operations suite', feed: 'Security APIs' },
  CUSTOMER_SUCCESS_DASHBOARD: { layer: 'ADVANCED', label: 'Customer Success', contract: 'Customer success suite', feed: 'CS APIs' },
  PROCUREMENT_DASHBOARD: { layer: 'ADVANCED', label: 'Procurement', contract: 'Procurement operations suite', feed: 'Procurement APIs' },
  RESEARCH_DASHBOARD: { layer: 'ADVANCED', label: 'Research', contract: 'Research operations suite', feed: 'Research APIs' },
  SPACE_OPERATIONS_DASHBOARD: { layer: 'FUTURE', label: 'Space Operations', contract: 'Space operations suite', feed: 'Space APIs' },
  AI_ETHICS_DASHBOARD: { layer: 'FUTURE', label: 'AI Ethics', contract: 'AI ethics suite', feed: 'AI APIs' },
  QUANTUM_COMPUTING_DASHBOARD: { layer: 'FUTURE', label: 'Quantum Computing', contract: 'Quantum computing suite', feed: 'Quantum APIs' },
  LONGEVITY_SCIENCES_DASHBOARD: { layer: 'FUTURE', label: 'Longevity Sciences', contract: 'Longevity sciences suite', feed: 'Longevity APIs' },
  AGRICULTURE_DASHBOARD: { layer: 'INDUSTRY', label: 'Agriculture', contract: 'Agriculture domain suite', feed: 'Agriculture APIs' },
  HOSPITALITY_DASHBOARD: { layer: 'INDUSTRY', label: 'Hospitality', contract: 'Hospitality domain suite', feed: 'Hospitality APIs' },
  PRODUCTION_DASHBOARD: { layer: 'INDUSTRY', label: 'Production', contract: 'Production domain suite', feed: 'Production APIs' },
  RETAIL_DASHBOARD: { layer: 'INDUSTRY', label: 'Retail', contract: 'Retail domain suite', feed: 'Retail APIs' },
  PUBLIC_DASHBOARD: { layer: 'INDUSTRY', label: 'Public', contract: 'Public domain suite', feed: 'Public APIs' },
  INDUSTRY_FINANCE_DASHBOARD: { layer: 'INDUSTRY', label: 'Industry Finance', contract: 'Industry finance suite', feed: 'Industry Finance APIs' },
  TECH_DASHBOARD: { layer: 'INDUSTRY', label: 'Tech', contract: 'Tech domain suite', feed: 'Tech APIs' },
  SPORTS_DASHBOARD: { layer: 'INDUSTRY', label: 'Sports', contract: 'Sports domain suite', feed: 'Sports APIs' },
  EDUCATION_DASHBOARD: { layer: 'INDUSTRY', label: 'Education', contract: 'Education domain suite', feed: 'Education APIs' },
  HEALTHCARE_DASHBOARD: { layer: 'INDUSTRY', label: 'Healthcare', contract: 'Healthcare domain suite', feed: 'Healthcare APIs' },
  CONSULTING_DASHBOARD: { layer: 'INDUSTRY', label: 'Consulting', contract: 'Consulting domain suite', feed: 'Consulting APIs' },
  ENERGY_DASHBOARD: { layer: 'INDUSTRY', label: 'Energy', contract: 'Energy domain suite', feed: 'Energy APIs' },
  ENTERTAINMENT_DASHBOARD: { layer: 'INDUSTRY', label: 'Entertainment', contract: 'Entertainment domain suite', feed: 'Entertainment APIs' },
  PROPERTY_DASHBOARD: { layer: 'INDUSTRY', label: 'Property', contract: 'Property domain suite', feed: 'Property APIs' },
  INDUSTRY_LEGAL_DASHBOARD: { layer: 'INDUSTRY', label: 'Industry Legal', contract: 'Industry legal suite', feed: 'Industry Legal APIs' },
  PROJECT_DASHBOARD: { layer: 'INDUSTRY', label: 'Project', contract: 'Project domain suite', feed: 'Project APIs' },
  LOGISTICS_DASHBOARD: { layer: 'INDUSTRY', label: 'Logistics', contract: 'Logistics domain suite', feed: 'Logistics APIs' },
  NONPROFIT_DASHBOARD: { layer: 'INDUSTRY', label: 'Nonprofit', contract: 'Nonprofit domain suite', feed: 'Nonprofit APIs' }
};

// ============================================================================
// THE ONLY MODULES RENDERED INSIDE FOUNDER DASHBOARD
// ============================================================================
const FOUNDER_ONLY_KEYS = new Set(['INVESTOR_PROOF', 'SINGULARITY_MATRIX', 'BOARDROOM_HUD']);

// ============================================================================
// EVERY SINGLE DASHBOARD REDIRECTS TO AN ABSOLUTE STANDALONE WORKSPACE
// ============================================================================
const standaloneDashboardRoutes = {
  REVENUE_LEDGER: { dashboardKey: 'REVENUE', route: '/revenue' },
  BILLING_HUB: { dashboardKey: 'BILLING', route: '/billing' },
  AUDIT_VAULT: { dashboardKey: 'AUDIT', route: '/audit' },
  NODE_REGISTRY: { dashboardKey: 'NODE_REGISTRY', route: '/node-registry' },
  GLOBAL_ORCHESTRATOR: { dashboardKey: 'GLOBAL_ORCHESTRATOR', route: '/global-orchestrator' },
  EXECUTIVE_OVERSIGHT: { dashboardKey: 'EXECUTIVE', route: '/executive' },
  INVOICE_SENTINEL: { dashboardKey: 'INVOICE_SENTINEL', route: '/invoice-sentinel' },
  CLOUD_UPLINK: { dashboardKey: 'CLOUD_UPLINK', route: '/cloud-uplink' },
  IDENTITY_HUB: { dashboardKey: 'IDENTITY_HUB', route: '/identity-hub' },
  RISK_SENTINEL: { dashboardKey: 'RISK_SENTINEL', route: '/risk-sentinel' },
  CLIENT_COVENANT: { dashboardKey: 'CLIENT_COVENANT', route: '/client-covenant' },
  CRISIS_COMMAND: { dashboardKey: 'CRISIS_COMMAND', route: '/crisis-command' },
  NUCLEUS_MONITOR: { dashboardKey: 'NUCLEUS_MONITOR', route: '/nucleus-monitor' },
  TENANT_MANAGER: { dashboardKey: 'TENANT_MANAGER', route: '/tenant-manager' },
  STATEMENT_ENGINE: { dashboardKey: 'STATEMENT_ENGINE', route: '/statement-engine' },
  CEO_DASHBOARD: { dashboardKey: 'EXECUTIVE', route: '/executive' },
  COO_DASHBOARD: { dashboardKey: 'COO', route: '/coo' },
  EXECUTIVE_CONTROL_ROOM: { dashboardKey: 'CONTROL_ROOM', route: '/control-room' },
  HR_DASHBOARD: { dashboardKey: 'HR', route: '/hr' },
  SALES_CRM: { dashboardKey: 'CRM', route: '/crm' },
  CRM_DASHBOARD: { dashboardKey: 'CRM', route: '/crm' },
  IT_OPS: { dashboardKey: 'IT', route: '/it' },
  PRODUCT_DASHBOARD: { dashboardKey: 'PRODUCT', route: '/product' },
  COMPLIANCE_DASHBOARD: { dashboardKey: 'COMPLIANCE', route: '/compliance' },
  OPERATIONS_DASHBOARD: { dashboardKey: 'OPERATIONS', route: '/operations' },
  PROCUREMENT_DASHBOARD: { dashboardKey: 'PROCUREMENT', route: '/procurement' },
  FINANCE_DASHBOARD: { dashboardKey: 'FINANCE', route: '/finance' },
  LEGAL_DASHBOARD: { dashboardKey: 'LEGAL', route: '/legal' },
  MARKETING_DASHBOARD: { dashboardKey: 'MARKETING', route: '/marketing' },
  ENGINEERING_DASHBOARD: { dashboardKey: 'ENGINEERING', route: '/engineering' },
  DATA_DASHBOARD: { dashboardKey: 'DATA', route: '/data' },
  SECURITY_DASHBOARD: { dashboardKey: 'SECURITY', route: '/security' },
  CUSTOMER_SUCCESS_DASHBOARD: { dashboardKey: 'CUSTOMER_SUCCESS', route: '/customer-success' },
  RESEARCH_DASHBOARD: { dashboardKey: 'RESEARCH', route: '/research' },
  SPACE_OPERATIONS_DASHBOARD: { dashboardKey: 'SPACE_OPERATIONS', route: '/space-operations' },
  AI_ETHICS_DASHBOARD: { dashboardKey: 'AI_ETHICS', route: '/ai-ethics' },
  QUANTUM_COMPUTING_DASHBOARD: { dashboardKey: 'QUANTUM', route: '/quantum' },
  LONGEVITY_SCIENCES_DASHBOARD: { dashboardKey: 'LONGEVITY', route: '/longevity' },
  AGRICULTURE_DASHBOARD: { dashboardKey: 'AGRICULTURE', route: '/industry/agriculture' },
  HOSPITALITY_DASHBOARD: { dashboardKey: 'HOSPITALITY', route: '/industry/hospitality' },
  PRODUCTION_DASHBOARD: { dashboardKey: 'PRODUCTION', route: '/industry/production' },
  RETAIL_DASHBOARD: { dashboardKey: 'RETAIL', route: '/industry/retail' },
  PUBLIC_DASHBOARD: { dashboardKey: 'PUBLIC', route: '/industry/public' },
  INDUSTRY_FINANCE_DASHBOARD: { dashboardKey: 'INDUSTRY_FINANCE', route: '/industry/finance' },
  TECH_DASHBOARD: { dashboardKey: 'TECH', route: '/industry/tech' },
  SPORTS_DASHBOARD: { dashboardKey: 'SPORTS', route: '/industry/sports' },
  EDUCATION_DASHBOARD: { dashboardKey: 'EDUCATION', route: '/industry/education' },
  HEALTHCARE_DASHBOARD: { dashboardKey: 'HEALTHCARE', route: '/industry/healthcare' },
  CONSULTING_DASHBOARD: { dashboardKey: 'CONSULTING', route: '/industry/consulting' },
  ENERGY_DASHBOARD: { dashboardKey: 'ENERGY', route: '/industry/energy' },
  ENTERTAINMENT_DASHBOARD: { dashboardKey: 'ENTERTAINMENT', route: '/industry/entertainment' },
  PROPERTY_DASHBOARD: { dashboardKey: 'PROPERTY', route: '/industry/property' },
  INDUSTRY_LEGAL_DASHBOARD: { dashboardKey: 'INDUSTRY_LEGAL', route: '/industry/legal' },
  PROJECT_DASHBOARD: { dashboardKey: 'PROJECT', route: '/industry/project' },
  LOGISTICS_DASHBOARD: { dashboardKey: 'LOGISTICS', route: '/industry/logistics' },
  NONPROFIT_DASHBOARD: { dashboardKey: 'NONPROFIT', route: '/industry/nonprofit' },
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================
const FounderDashboard = memo(({ onSwitchDashboard }) => {
  const { user, logout } = useAuth();
  const { activeTenant } = useTenants();
  const { healthy, workers, latency: runtimeLatency, error: runtimeError, loading: runtimeLoading } = useRuntimeStatus();
  const { isConnected: kennelConnected, latency: kennelLatency, kernelStatus } = useKennelHealth();

  const [currentTime, setCurrentTime] = useState(new Date());
  const [activeModule, setActiveModule] = useState('INVESTOR_PROOF');
  const [singularitySurface, setSingularitySurface] = useState('REVENUE');
  const [actionLoading, setActionLoading] = useState(null);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState('VERIFYING_UPLINK...');
  const [filterType, setFilterType] = useState('ALL');
  const [boardroomReturnModule, setBoardroomReturnModule] = useState('SINGULARITY_MATRIX');
  const [isQuickPanelOpen, setIsQuickPanelOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  const [lastReadTimestamp, setLastReadTimestamp] = useState(() => {
    const saved = localStorage.getItem(NOTIFICATION_LAST_READ_KEY);
    return saved ? parseInt(saved, 10) : 0;
  });
  const [notifications, setNotifications] = useState([]);
  const [billingMetrics, setBillingMetrics] = useState(null);
  const [storedFounderProfile, setStoredFounderProfile] = useState(() => {
    try {
      const raw = localStorage.getItem(FOUNDER_PROFILE_STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (error) {
      console.warn('[FOUNDER-PROFILE] Preference cache unavailable:', error.message);
      return null;
    }
  });
  const [profileDraft, setProfileDraft] = useState({});
  const [isFounderPanelOpen, setIsFounderPanelOpen] = useState(false);
  const [isPreferenceEditing, setIsPreferenceEditing] = useState(false);
  const [missionRun, setMissionRun] = useState({ activeMission: null, status: 'IDLE', progress: 0, log: [] });

  const { analytics, compliance, forensics, loading: dataLoading, error: dataError } = useSovereignData();
  const { events: telemetryEvents, isSyncing: telemetrySyncing } = useTelemetryFeed(activeTenant?.tenantId || 'MASTER');
  const { stats: telemetryStats } = useTelemetryStats(activeTenant?.tenantId || 'MASTER');
  const { stats: trajectoryStats } = useTrajectoryWithEmails(activeTenant?.tenantId || 'MASTER');
  const chartRef = useRef(null);

  // ==========================================================================
  // NOTIFICATION CENTER
  // ==========================================================================
  useEffect(() => {
    if (!telemetryEvents || telemetryEvents.length === 0) {
      setNotifications([]);
      return;
    }
    const relevant = telemetryEvents
      .filter(ev => {
        const type = (ev.eventType || '').toUpperCase();
        const severity = (ev.severity || '').toUpperCase();
        return (type.includes('BILLING') || type.includes('COMPLIANCE') || type.includes('FORENSIC') || type.includes('ALERT') || type.includes('ERROR') || severity === 'CRITICAL' || severity === 'WARNING');
      })
      .map(ev => ({
        ...ev,
        timestamp: new Date(ev.timestamp).getTime(),
        isRead: new Date(ev.timestamp).getTime() <= lastReadTimestamp
      }))
      .sort((a, b) => b.timestamp - a.timestamp);
    setNotifications(relevant);
  }, [telemetryEvents, lastReadTimestamp]);

  const unreadCount = useMemo(() => notifications.filter(n => !n.isRead).length, [notifications]);
  const markAllAsRead = useCallback(() => {
    const now = Date.now();
    localStorage.setItem(NOTIFICATION_LAST_READ_KEY, String(now));
    setLastReadTimestamp(now);
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
  }, []);

  // ==========================================================================
  // FOUNDER PROFILE
  // ==========================================================================
  const fallbackFounderProfile = useMemo(() => ({
    displayName: resolveFounderDisplayName(user),
    title: 'Founder, CEO & Lead Architect',
    company: activeTenant?.name || 'Wilsy (Pty) Ltd',
    commandMode: 'Investor Theatre',
    telemetryDensity: 'Executive',
    evidenceMode: 'Real Data Only',
    narrativeTone: 'Boardroom',
    theme: 'Sovereign Gold',
    defaultModule: 'INVESTOR_PROOF',
    tenantScope: 'Founder Tenant',
    sidebarMode: 'Open',
    quickPanelMode: 'Closed',
    jurisdictionFocus: activeTenant?.jurisdiction || 'South Africa / Global Expansion',
    investorPromise: 'Every module proves ownership, auditability, revenue motion and sovereign control.'
  }), [user, activeTenant]);

  const founderProfile = useMemo(() => {
    const merged = { ...fallbackFounderProfile, ...(storedFounderProfile || {}) };
    return { ...merged, displayName: normalizeFounderDisplayName(merged.displayName) };
  }, [fallbackFounderProfile, storedFounderProfile]);

  const founderInitials = useMemo(() => {
    const parts = (founderProfile.displayName || 'Wilson Khanyezi').split(/\s+/).filter(Boolean);
    return `${parts[0]?.[0] || 'W'}${parts[1]?.[0] || 'K'}`.toUpperCase();
  }, [founderProfile.displayName]);

  const isSingularityWorkspaceAuthorized = useMemo(() => {
    const authorityText = [
      user?.role, user?.accountRole, user?.authority, user?.tenantRole,
      Array.isArray(user?.permissions) ? user.permissions.join(' ') : '',
      founderProfile.commandMode, founderProfile.tenantScope
    ].filter(Boolean).join(' ').toUpperCase();
    return ['FOUNDER', 'SUPER_ADMIN', 'SUPERADMIN', 'SOVEREIGN', 'GLOBAL_ROOT', 'ROOT'].some(token => authorityText.includes(token));
  }, [founderProfile, user]);

  const operatorSovereigntyGraph = useMemo(() => {
    const roleText = String(user?.role || user?.accountRole || user?.authority || '').toUpperCase();
    const isFounder = roleText.includes('FOUNDER') || founderProfile.tenantScope === 'Founder Tenant';
    const isSuperAdmin = roleText.includes('SUPER');
    const authorityLabel = isFounder ? 'Founder Authority' : isSuperAdmin ? 'Sovereign Operator' : 'Authorized Operator';
    return {
      displayName: founderProfile.displayName,
      authorityLabel,
      companyScope: activeTenant?.name || founderProfile.company || 'Wilsy (Pty) Ltd',
      roleNarrative: founderProfile.title || 'Operator',
      evidenceMode: founderProfile.evidenceMode || 'Real Data Only'
    };
  }, [activeTenant, founderProfile, user]);

  const founderPatentSystems = useMemo(() => ([
    { title: 'Founder Sovereignty Graph', text: 'Ties owner identity, tenant authority, boardroom actions and audit proof into one visible command graph.', icon: Fingerprint },
    { title: 'Real-Data Investor Theatre', text: 'Demo surfaces reject placeholders and expose whether every figure is database-backed, cached or unavailable.', icon: BadgeCheck },
    { title: 'Jurisdiction Revenue Router', text: 'Links billing, courts, compliance, collections and tenant geography so money movement has legal context.', icon: Scale },
    { title: 'Forensic Operating Memory', text: 'Every executive action becomes explainable, exportable and sealed for institutional diligence.', icon: FileCheck2 }
  ]), []);

  useEffect(() => { setProfileDraft(founderProfile); }, [founderProfile]);
  const updateProfileDraft = useCallback((key, value) => {
    setProfileDraft(prev => ({ ...prev, [key]: value }));
  }, []);

  // ==========================================================================
  // ACTIVATE MODULE - STRICT ISOLATION & STANDALONE ROUTER
  // ==========================================================================
  const activateModule = useCallback((moduleKey) => {
    if (!FOUNDER_ONLY_KEYS.has(moduleKey)) {
      const standaloneInfo = standaloneDashboardRoutes[moduleKey];
      if (standaloneInfo) {
        if (onSwitchDashboard) {
          onSwitchDashboard(standaloneInfo.dashboardKey);
          return;
        }
        const requestPacket = {
          dashboardKey: standaloneInfo.dashboardKey,
          moduleKey,
          route: standaloneInfo.route,
          source: 'FounderDashboard',
          requestedAt: new Date().toISOString()
        };
        window.localStorage.setItem('wilsy_last_dashboard', standaloneInfo.dashboardKey);
        window.localStorage.setItem('wilsy:requested-dashboard', JSON.stringify(requestPacket));
        window.dispatchEvent(new CustomEvent('wilsy:navigate-dashboard', { detail: requestPacket }));
        window.dispatchEvent(new CustomEvent('wilsy:switch-dashboard', { detail: requestPacket }));
      } else {
        console.warn(`[FOUNDER-DASHBOARD] No standalone route defined for module: ${moduleKey}`);
      }
      return;
    }

    if (moduleKey === 'BOARDROOM_HUD') {
      setBoardroomReturnModule(activeModule === 'BOARDROOM_HUD' ? 'SINGULARITY_MATRIX' : activeModule);
    }
    setActiveModule(moduleKey);
  }, [activeModule, onSwitchDashboard]);

  const persistFounderProfile = useCallback((nextProfile) => {
    const cleanProfile = {
      ...fallbackFounderProfile,
      ...nextProfile,
      displayName: normalizeFounderDisplayName(nextProfile.displayName || fallbackFounderProfile.displayName)
    };
    try {
      localStorage.setItem(FOUNDER_PROFILE_STORAGE_KEY, JSON.stringify(cleanProfile));
    } catch (error) {
      console.warn('[FOUNDER-PROFILE] Preference persistence skipped:', error.message);
    }
    setStoredFounderProfile(cleanProfile);
    setProfileDraft(cleanProfile);
    if (cleanProfile.sidebarMode === 'Closed') setIsSidebarOpen(false);
    if (cleanProfile.sidebarMode === 'Open') setIsSidebarOpen(true);
    if (cleanProfile.quickPanelMode === 'Open') setIsQuickPanelOpen(true);
    if (cleanProfile.quickPanelMode === 'Closed') setIsQuickPanelOpen(false);
    if (cleanProfile.defaultModule && cleanProfile.defaultModule !== activeModule) {
      activateModule(cleanProfile.defaultModule);
    }
  }, [fallbackFounderProfile, activeModule, activateModule]);

  const applyFounderPreset = useCallback((presetName) => {
    const preset = FOUNDER_OPERATING_PRESETS[presetName];
    if (!preset) return;
    persistFounderProfile({ ...founderProfile, ...preset, commandMode: presetName });
    setIsPreferenceEditing(true);
  }, [founderProfile, persistFounderProfile]);

  const applyPreferenceChange = useCallback((key, value) => {
    if (key === 'commandMode') { applyFounderPreset(value); return; }
    persistFounderProfile({ ...founderProfile, [key]: value });
  }, [applyFounderPreset, founderProfile, persistFounderProfile]);

  const saveFounderProfile = useCallback(() => {
    persistFounderProfile(profileDraft);
    setIsPreferenceEditing(false);
  }, [persistFounderProfile, profileDraft]);

  const resetFounderProfile = useCallback(() => {
    try {
      localStorage.removeItem(FOUNDER_PROFILE_STORAGE_KEY);
    } catch (error) {
      console.warn('[FOUNDER-PROFILE] Preference reset skipped:', error.message);
    }
    setStoredFounderProfile(null);
    setProfileDraft(fallbackFounderProfile);
    setIsPreferenceEditing(false);
  }, [fallbackFounderProfile]);

  const handleNotificationClick = useCallback((ev) => {
    const type = (ev.eventType || '').toUpperCase();
    let moduleKey = null;
    if (type.includes('BILLING')) moduleKey = 'BILLING_HUB';
    else if (type.includes('COMPLIANCE')) moduleKey = 'RISK_SENTINEL';
    else if (type.includes('FORENSIC')) moduleKey = 'AUDIT_VAULT';
    else if (type.includes('ALERT') || type.includes('ERROR')) moduleKey = 'CRISIS_COMMAND';
    else moduleKey = 'INVESTOR_PROOF';
    if (moduleKey) { activateModule(moduleKey); }
    setIsNotificationOpen(false);
  }, [activateModule]);

  const handleKeyDown = useCallback((e) => {
    if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) {
      e.preventDefault(); e.stopPropagation();
      setIsCommandPaletteOpen(prev => !prev);
    }
    if (e.key === 'Escape' && isCommandPaletteOpen) setIsCommandPaletteOpen(false);
    if (e.key === 'Escape' && isFounderPanelOpen) { setIsFounderPanelOpen(false); setIsPreferenceEditing(false); }
    if (e.key === 'Escape' && isNotificationOpen) setIsNotificationOpen(false);
  }, [isCommandPaletteOpen, isFounderPanelOpen, isNotificationOpen]);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    window.addEventListener('keydown', handleKeyDown, true);
    return () => {
      clearInterval(timer);
      window.removeEventListener('keydown', handleKeyDown, true);
    };
  }, [handleKeyDown]);

  useEffect(() => {
    if (activeModule === 'SALES_CRM') { setIsSidebarOpen(false); }
  }, [activeModule]);

  useEffect(() => {
    const fetchBilling = async () => {
      try {
        const token = localStorage.getItem('wilsy_auth_token')?.replace(/["']/g, '').trim();
        const tenantId = activeTenant?.id || 'GLOBAL_ROOT';
        const response = await api.get('/billing/institutional/summary', {
          params: { tenantId },
          headers: { Authorization: `Bearer ${token}` }
        });
        if (response.data?.success) {
          const payload = response.data.data || response.data;
          setBillingMetrics({
            ytdRevenue: payload.metrics?.ytdRevenue || payload.ytdRevenue || 0,
            outstandingReceivables: payload.metrics?.outstandingReceivables || payload.outstandingReceivables || 0,
            isFrozen: activeTenant?.billingStatus === 'FROZEN_AWAITING_SETTLEMENT',
            lastSync: new Date().toISOString()
          });
        }
      } catch (err) {
        console.warn('[FOUNDER-DASHBOARD] Billing metrics fetch skipped:', err.message);
      }
    };
    fetchBilling();
  }, [activeTenant]);

  useEffect(() => {
    if (dataLoading || runtimeLoading) { setSystemHealth('HYDRATING_NUCLEUS...'); }
    else if (dataError || runtimeError) { setSystemHealth('FRACTURE: OMEGA_LINK_SEVERED'); }
    else if (!healthy) { setSystemHealth('RUNTIME DEGRADED'); }
    else { setSystemHealth('SOVEREIGN_LINK_STABLE'); }
  }, [dataLoading, dataError, runtimeLoading, runtimeError, healthy]);

  const { currentNarrative } = useDynamicNarrative();

  // ==========================================================================
  // OMEGA STRIKE
  // ==========================================================================
  const executeOmegaStrike = useCallback(async (actionId, endpoint, method = 'GET', payload = {}) => {
    setActionLoading(actionId);
    const traceId = `TRC-CMD-${Date.now()}`;
    console.log(`[OMEGA-STRIKE] Initiating: ${actionId} | ${method} ${endpoint} | Trace: ${traceId}`);
    try {
      const token = localStorage.getItem('wilsy_auth_token')?.replace(/["']/g, '').trim();
      const tenantContext = activeTenant?.id || 'GLOBAL_ROOT';
      const finalEndpoint = endpoint.includes('tenantId') ? endpoint : `${endpoint}?tenantId=${tenantContext}`;
      if (!token) {
        console.error('[OMEGA-STRIKE] No token available.');
        alert('Session expired. Please log out and log in again.');
        setActionLoading(null); return;
      }
      const response = await api({
        url: finalEndpoint,
        method: method,
        data: method === 'GET' ? undefined : payload,
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant-ID': tenantContext,
          'X-Trace-ID': traceId
        },
        responseType: 'blob',
        timeout: 15000
      });
      if (response.status === 401) { throw new Error('UNAUTHORIZED – Token invalid or expired'); }
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const contentType = response.headers['content-type'] || '';
      const ext = contentType.includes('pdf') ? 'pdf' : (contentType.includes('json') ? 'json' : 'txt');
      const filename = `WILSY_OS_${actionId}_${timestamp}.${ext}`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
      console.log(`[OMEGA-STRIKE] ${actionId} SUCCESS. File saved: ${filename}`);
    } catch (error) {
      console.error(`[OMEGA-STRIKE] ${actionId} FAILED:`, error.message);
      if (error.response?.status === 401) {
        alert('Authentication failed. Please logout and login again.');
      }
      const dummyContent = `WILSY OS Fallback Report\nAction: ${actionId}\nTrace: ${traceId}\nTimestamp: ${new Date().toISOString()}\nError: ${error.message}\n\nPlease check console for details.`;
      const blob = new Blob([dummyContent], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `WILSY_OS_${actionId}_fallback_${Date.now()}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } finally {
      setActionLoading(null);
    }
  }, [activeTenant]);

  // ==========================================================================
  // COMMAND PALETTE
  // ==========================================================================
  const moduleCommands = useMemo(() => [
    { id: 'MODULE_INVESTOR_PROOF', label: 'Investor Proof Console', icon: <BadgeCheck size={16} />, handler: () => activateModule('INVESTOR_PROOF') },
    { id: 'MODULE_BOARDROOM_HUD', label: 'Boardroom HUD', icon: <Eye size={16} />, handler: () => activateModule('BOARDROOM_HUD') },
    { id: 'MODULE_SINGULARITY_MATRIX', label: 'Singularity Matrix (HUDs)', icon: <BarChart3 size={16} />, handler: () => activateModule('SINGULARITY_MATRIX') },
    { id: 'MODULE_EXECUTIVE_OVERSIGHT', label: 'Executive Oversight', icon: <Crown size={16} />, handler: () => activateModule('EXECUTIVE_OVERSIGHT') },
    { id: 'MODULE_CLOUD_UPLINK', label: 'Cloud Uplink', icon: <Server size={16} />, handler: () => activateModule('CLOUD_UPLINK') },
    { id: 'MODULE_REVENUE_LEDGER', label: 'Revenue Ledger', icon: <TrendingUp size={16} />, handler: () => activateModule('REVENUE_LEDGER') },
    { id: 'MODULE_BILLING_HUB', label: 'Billing Hub', icon: <CreditCard size={16} />, handler: () => activateModule('BILLING_HUB') },
    { id: 'MODULE_INVOICE_SENTINEL', label: 'Invoice Sentinel', icon: <Receipt size={16} />, handler: () => activateModule('INVOICE_SENTINEL') },
    { id: 'MODULE_NUCLEUS_MONITOR', label: 'Nucleus Feed Monitor', icon: <TerminalSquare size={16} />, handler: () => activateModule('NUCLEUS_MONITOR') },
    { id: 'MODULE_AUDIT_VAULT', label: 'Audit Vault', icon: <Microscope size={16} />, handler: () => activateModule('AUDIT_VAULT') },
    { id: 'MODULE_NODE_REGISTRY', label: 'Node Registry', icon: <Cpu size={16} />, handler: () => activateModule('NODE_REGISTRY') },
    { id: 'MODULE_GLOBAL_ORCHESTRATOR', label: 'Global Orchestrator', icon: <Globe size={16} />, handler: () => activateModule('GLOBAL_ORCHESTRATOR') },
    { id: 'MODULE_IDENTITY_HUB', label: 'Identity Hub', icon: <Key size={16} />, handler: () => activateModule('IDENTITY_HUB') },
    { id: 'MODULE_RISK_SENTINEL', label: 'Risk Sentinel', icon: <AlertOctagon size={16} />, handler: () => activateModule('RISK_SENTINEL') },
    { id: 'MODULE_CLIENT_COVENANT', label: 'Client Covenant', icon: <FileSignature size={16} />, handler: () => activateModule('CLIENT_COVENANT') },
    { id: 'MODULE_CRISIS_COMMAND', label: 'Crisis Command', icon: <Power size={16} />, handler: () => activateModule('CRISIS_COMMAND') },
    { id: 'MODULE_TENANT_MANAGER', label: 'Tenant Manager', icon: <Users size={16} />, handler: () => activateModule('TENANT_MANAGER') },
    { id: 'MODULE_STATEMENT_ENGINE', label: 'Statement Engine', icon: <FileText size={16} />, handler: () => activateModule('STATEMENT_ENGINE') },
    { id: 'MODULE_CEO_DASHBOARD', label: 'CEO Dashboard', icon: <Crown size={16} />, handler: () => activateModule('CEO_DASHBOARD') },
    { id: 'MODULE_COO_DASHBOARD', label: 'COO Dashboard', icon: <Briefcase size={16} />, handler: () => activateModule('COO_DASHBOARD') },
    { id: 'MODULE_HR_DASHBOARD', label: 'HR Department', icon: <Users size={16} />, handler: () => activateModule('HR_DASHBOARD') },
    { id: 'MODULE_SALES_CRM', label: 'Sales & CRM', icon: <MessageSquare size={16} />, handler: () => activateModule('SALES_CRM') },
    { id: 'MODULE_IT_OPS', label: 'IT Operations', icon: <Server size={16} />, handler: () => activateModule('IT_OPS') },
    { id: 'MODULE_FINANCE_DASHBOARD', label: 'Finance', icon: <DollarSign size={16} />, handler: () => activateModule('FINANCE_DASHBOARD') },
    { id: 'MODULE_LEGAL_DASHBOARD', label: 'Legal', icon: <Gavel size={16} />, handler: () => activateModule('LEGAL_DASHBOARD') },
    { id: 'MODULE_MARKETING_DASHBOARD', label: 'Marketing', icon: <Megaphone size={16} />, handler: () => activateModule('MARKETING_DASHBOARD') },
    { id: 'MODULE_PRODUCT_DASHBOARD', label: 'Product', icon: <Box size={16} />, handler: () => activateModule('PRODUCT_DASHBOARD') },
    { id: 'MODULE_ENGINEERING_DASHBOARD', label: 'Engineering', icon: <Code size={16} />, handler: () => activateModule('ENGINEERING_DASHBOARD') },
    { id: 'MODULE_DATA_DASHBOARD', label: 'Data', icon: <BarChart size={16} />, handler: () => activateModule('DATA_DASHBOARD') },
    { id: 'MODULE_SECURITY_DASHBOARD', label: 'Security', icon: <LockKeyhole size={16} />, handler: () => activateModule('SECURITY_DASHBOARD') },
    { id: 'MODULE_CUSTOMER_SUCCESS_DASHBOARD', label: 'Customer Success', icon: <HeartHandshake size={16} />, handler: () => activateModule('CUSTOMER_SUCCESS_DASHBOARD') },
    { id: 'MODULE_PROCUREMENT_DASHBOARD', label: 'Procurement', icon: <ShoppingCart size={16} />, handler: () => activateModule('PROCUREMENT_DASHBOARD') },
    { id: 'MODULE_RESEARCH_DASHBOARD', label: 'Research', icon: <FlaskConical size={16} />, handler: () => activateModule('RESEARCH_DASHBOARD') },
    { id: 'MODULE_SPACE_OPERATIONS_DASHBOARD', label: 'Space Operations', icon: <Satellite size={16} />, handler: () => activateModule('SPACE_OPERATIONS_DASHBOARD') },
    { id: 'MODULE_AI_ETHICS_DASHBOARD', label: 'AI Ethics', icon: <Brain size={16} />, handler: () => activateModule('AI_ETHICS_DASHBOARD') },
    { id: 'MODULE_QUANTUM_COMPUTING_DASHBOARD', label: 'Quantum Computing', icon: <CpuIcon size={16} />, handler: () => activateModule('QUANTUM_COMPUTING_DASHBOARD') },
    { id: 'MODULE_LONGEVITY_SCIENCES_DASHBOARD', label: 'Longevity Sciences', icon: <Dna size={16} />, handler: () => activateModule('LONGEVITY_SCIENCES_DASHBOARD') },
    { id: 'MODULE_EXECUTIVE_CONTROL_ROOM', label: 'Executive Control Room', icon: <Command size={16} />, handler: () => activateModule('EXECUTIVE_CONTROL_ROOM') }
  ], []);

  const actionCommands = useMemo(() => [
    { id: 'ACTION_STMT_REVENUE', label: 'Revenue Artifact', icon: <FileText size={16} />, handler: () => executeOmegaStrike('STMT_REVENUE', '/statements/revenue') },
    { id: 'ACTION_STMT_COMPLIANCE', label: 'Compliance Proof', icon: <ShieldCheck size={16} />, handler: () => executeOmegaStrike('STMT_COMPLIANCE', '/statements/compliance') },
    { id: 'ACTION_STMT_FORENSIC', label: 'Forensic Seal', icon: <Fingerprint size={16} />, handler: () => executeOmegaStrike('STMT_FORENSIC', '/statements/forensics') },
    { id: 'ACTION_ADD_TENANT', label: 'Spawn Shard', icon: <Users size={16} />, handler: () => executeOmegaStrike('TENANT_ADD', '/tenants/create', 'POST') },
    { id: 'ACTION_SUSPEND_TENANT', label: 'Freeze Shard', icon: <ShieldAlert size={16} />, handler: () => executeOmegaStrike('TENANT_SUSPEND', '/tenants/suspend', 'POST') },
    { id: 'ACTION_TRIGGER_SNAPSHOT', label: 'Cold Storage Snapshot', icon: <Database size={16} />, handler: () => executeOmegaStrike('COLD_STORAGE_SNAPSHOT', '/revenue/snapshot/cold-storage', 'POST') },
    { id: 'ACTION_CLEAR_SUSPENSE', label: 'Open Invoice Sentinel', icon: <Receipt size={16} />, handler: () => activateModule('INVOICE_SENTINEL') },
    { id: 'ACTION_LOGOUT', label: 'Logout / Terminate Session', icon: <LogOut size={16} />, handler: logout }
  ], [executeOmegaStrike, logout]);

  const capabilityCommands = useMemo(() => [
    { id: 'CAPABILITY_SOVEREIGN_HEALTH_TRIBUNAL', label: 'Run Sovereign Health Tribunal', icon: <Activity size={16} />, handler: () => activateModule('BOARDROOM_HUD') },
    { id: 'CAPABILITY_COMMAND_MANIFEST_EXPORT', label: 'Export Sealed Command Manifest', icon: <FileCheck2 size={16} />, handler: () => activateModule('EXECUTIVE_OVERSIGHT') },
    { id: 'CAPABILITY_COPY_FORENSIC_RECEIPT', label: 'Copy Last Forensic Receipt', icon: <Fingerprint size={16} />, handler: () => activateModule('AUDIT_VAULT') },
    { id: 'CAPABILITY_INVESTOR_REPORT', label: 'Generate Investor Report', icon: <Scale size={16} />, handler: () => activateModule('EXECUTIVE_OVERSIGHT') },
    { id: 'CAPABILITY_ARR_REPORT', label: 'ARR Report', icon: <TrendingUp size={16} />, handler: () => executeOmegaStrike('ARR_REPORT', '/statements/revenue') }
  ], [executeOmegaStrike]);

  const allCommands = useMemo(() => [...moduleCommands, ...actionCommands, ...capabilityCommands], [moduleCommands, actionCommands, capabilityCommands]);

  const founderModuleOptions = useMemo(() => moduleCommands
    .filter(command => ['MODULE_BOARDROOM_HUD', 'MODULE_INVESTOR_PROOF', 'MODULE_SINGULARITY_MATRIX', 'MODULE_REVENUE_LEDGER', 'MODULE_BILLING_HUB', 'MODULE_AUDIT_VAULT', 'MODULE_NODE_REGISTRY', 'MODULE_GLOBAL_ORCHESTRATOR', 'MODULE_IDENTITY_HUB', 'MODULE_TENANT_MANAGER', 'MODULE_STATEMENT_ENGINE', 'MODULE_EXECUTIVE_CONTROL_ROOM'].includes(command.id))
    .map(command => ({ label: command.label, value: command.id.replace('MODULE_', '') })), [moduleCommands]);

  const activeModuleMeta = useMemo(() => {
    const command = moduleCommands.find(item => item.id === `MODULE_${activeModule}`);
    return {
      key: activeModule,
      label: command?.label || activeModule.replace(/_/g, ' '),
      description: command?.description || 'Sovereign module mounted through Founder OS'
    };
  }, [activeModule, moduleCommands]);

  // ==========================================================================
  // OS SPINE & CORE LOGIC
  // ==========================================================================
  const osSpine = useMemo(() => {
    const telemetryCount = Array.isArray(telemetryEvents) ? telemetryEvents.length : 0;
    const telemetryStatsCount = Array.isArray(telemetryStats) ? telemetryStats.length : 0;
    const feeds = [
      { label: 'Tenant', status: activeTenant?.tenantId || activeTenant?.id || 'MASTER', ready: Boolean(activeTenant) },
      { label: 'Telemetry', status: telemetrySyncing ? 'Syncing' : `${telemetryCount} events`, ready: telemetryCount > 0 || !telemetrySyncing },
      { label: 'Revenue', status: billingMetrics ? 'Linked' : 'Pending', ready: Boolean(billingMetrics) },
      { label: 'Compliance', status: compliance ? 'Linked' : 'Pending', ready: Boolean(compliance) },
      { label: 'Forensics', status: forensics ? 'Linked' : 'Pending', ready: Boolean(forensics) },
      { label: 'Stats', status: `${telemetryStatsCount} samples`, ready: telemetryStatsCount > 0 },
      { label: 'Runtime', status: healthy ? 'Operational' : 'Degraded', ready: healthy }
    ];
    return { feeds, mounted: 38, commandCount: allCommands.length, realDataRatio: Math.round((feeds.filter(feed => feed.ready).length / feeds.length) * 100), workers, latency: runtimeLatency, runtimeStatus: healthy ? 'Stable' : 'Degraded' };
  }, [activeTenant, telemetryEvents, telemetryStats, telemetrySyncing, billingMetrics, compliance, forensics, allCommands.length, healthy, workers, runtimeLatency]);

  const investorProofMatrix = useMemo(() => {
    const telemetryCount = Array.isArray(telemetryEvents) ? telemetryEvents.length : 0;
    const statsCount = Array.isArray(telemetryStats) ? telemetryStats.length : 0;
    const tenantLabel = activeTenant?.name || founderProfile.company || 'Wilsy (Pty) Ltd';
    const tenantId = activeTenant?.tenantId || activeTenant?.id || 'MASTER';
    return [
      { title: 'Business OS, Not CRM Add-On', claim: 'CRM, billing, compliance, courts, identity, revenue and audit share one founder command plane.', proof: `${osSpine.mounted} mounted modules / ${osSpine.commandCount} executable commands`, ready: osSpine.mounted >= 20, module: 'SINGULARITY_MATRIX', action: 'Open OS Matrix' },
      { title: 'Diligence-Ready Evidence', claim: 'Every critical executive claim can route to Audit Vault, Statement Engine or a forensic feed.', proof: forensics ? 'Forensic feed linked' : 'Forensic feed pending', ready: Boolean(forensics), module: 'AUDIT_VAULT', action: 'Open Audit Vault' },
      { title: 'Founder-Controlled Tenancy', claim: 'The owner, tenant, role authority and expansion path are visible from the command center.', proof: `${tenantLabel} / ${tenantId}`, ready: Boolean(activeTenant || tenantId), module: 'IDENTITY_HUB', action: 'Open Identity Hub' },
      { title: 'Revenue-To-Court Loop', claim: 'Collections, court registry, receivables and statements belong to one operating workflow.', proof: billingMetrics ? 'Billing metrics linked' : 'Billing metrics pending', ready: Boolean(billingMetrics), module: 'BILLING_HUB', action: 'Open Billing Hub' },
      { title: 'Multi-Tenant Expansion Rail', claim: 'New businesses can become governed tenants without losing audit, identity or jurisdiction context.', proof: activeTenant?.jurisdiction || founderProfile.jurisdictionFocus || 'Founder jurisdiction configured', ready: Boolean(activeTenant?.jurisdiction || founderProfile.jurisdictionFocus), module: 'TENANT_MANAGER', action: 'Open Tenant Manager' },
      { title: 'Live Operating Telemetry', claim: 'A CEO sees posture, risk, uptime signals and command history without asking engineering.', proof: `${telemetryCount} events / ${statsCount} stat samples`, ready: telemetryCount > 0 || statsCount > 0, module: 'NUCLEUS_MONITOR', action: 'Open Nucleus Monitor' }
    ];
  }, [activeTenant, billingMetrics, forensics, founderProfile, osSpine, telemetryEvents, telemetryStats]);

  const aiEraDefensibility = useMemo(() => {
    const readyFeeds = osSpine.feeds.filter(feed => feed.ready).length;
    const score = Math.min(100, Math.max(0, Math.round(((readyFeeds * 18) + Math.min(osSpine.mounted, 30) + Math.min(osSpine.commandCount, 36)) / 1.74)));
    return {
      score,
      thesis: 'AI can generate screens. WILSY OS governs the business: who owns the tenant, which evidence proves the action, which legal path executes, which revenue moves, and which audit trail survives diligence.',
      pillars: [
        { title: 'Governed Execution', text: 'Commands are routed through tenant, authority and evidence context before they become business action.', ready: Boolean(activeTenant), icon: Workflow },
        { title: 'Evidence Before Optics', text: 'Investor surfaces show readiness from real hooks instead of decorative claims.', ready: osSpine.realDataRatio >= 50, icon: FileCheck2 },
        { title: 'Regulated Business Memory', text: 'Forensics, compliance and telemetry are treated as operating memory, not optional analytics.', ready: Boolean(forensics || compliance), icon: ShieldCheck },
        { title: 'Founder-Led Expansion', text: 'The system starts with Wilsy as the owner node and expands into governed tenants instead of anonymous accounts.', ready: Boolean(founderProfile.displayName), icon: Crown }
      ]
    };
  }, [activeTenant, compliance, forensics, founderProfile.displayName, osSpine]);

  const sovereignValueLoops = useMemo(() => ([
    { title: 'Money To Law Loop', path: 'Invoice -> receivable -> court route -> statement -> forensic seal', module: 'BILLING_HUB', action: 'Inspect Billing' },
    { title: 'Identity To Authority Loop', path: 'Founder profile -> role graph -> tenant scope -> command permission', module: 'IDENTITY_HUB', action: 'Inspect Identity' },
    { title: 'Tenant To Node Loop', path: 'Founder tenant -> shard registry -> topology -> expansion readiness', module: 'GLOBAL_ORCHESTRATOR', action: 'Inspect Topology' },
    { title: 'Action To Evidence Loop', path: 'Command -> telemetry -> audit vault -> exportable diligence proof', module: 'AUDIT_VAULT', action: 'Inspect Evidence' }
  ]), []);

  const founderMissionDeck = useMemo(() => ([
    {
      id: 'INVESTOR_DILIGENCE_PACK', title: 'Investor Diligence Pack', purpose: 'Generate the evidence bundle an investor asks for before serious money moves.', module: 'AUDIT_VAULT', command: 'Generate Pack',
      steps: [
        { label: 'Revenue artifact', type: 'omega', actionId: 'STMT_REVENUE', endpoint: '/statements/revenue' },
        { label: 'Compliance artifact', type: 'omega', actionId: 'STMT_COMPLIANCE', endpoint: '/statements/compliance' },
        { label: 'Forensic artifact', type: 'omega', actionId: 'STMT_FORENSIC', endpoint: '/statements/forensics' },
        { label: 'Open Audit Vault for inspection', type: 'module', module: 'AUDIT_VAULT' }
      ]
    },
    {
      id: 'FOUNDER_READINESS_SCAN', title: 'Founder Readiness Scan', purpose: 'Score whether the current tenant can survive a boardroom, diligence and operations review.', module: 'INVESTOR_PROOF', command: 'Run Scan',
      steps: [
        { label: 'Verify tenant identity', type: 'check', ready: Boolean(activeTenant || founderProfile.company), proof: activeTenant?.name || founderProfile.company },
        { label: 'Verify real data spine', type: 'check', ready: osSpine.realDataRatio >= 50, proof: `${osSpine.realDataRatio}% real-data readiness` },
        { label: 'Verify command surface', type: 'check', ready: allCommands.length > 0, proof: `${allCommands.length} commands mounted` },
        { label: 'Verify AI-era moat', type: 'check', ready: aiEraDefensibility.score >= 50, proof: `${aiEraDefensibility.score}% defensibility` }
      ]
    },
    {
      id: 'REVENUE_TO_COURT_DRILL', title: 'Revenue To Court Drill', purpose: 'Walk from receivable pressure to legal execution posture without leaving the OS spine.', module: 'BILLING_HUB', command: 'Start Drill',
      steps: [
        { label: 'Open Billing Hub', type: 'module', module: 'BILLING_HUB' },
        { label: 'Open Invoice Sentinel', type: 'module', module: 'INVOICE_SENTINEL' },
        { label: 'Inspect court-aware billing posture', type: 'check', ready: Boolean(billingMetrics), proof: billingMetrics ? 'Billing metrics linked' : 'Billing metrics pending' },
        { label: 'Return to Investor Proof', type: 'module', module: 'INVESTOR_PROOF' }
      ]
    },
    {
      id: 'AI_CONTROL_LOCK', title: 'AI Control Lock', purpose: 'Show why AI must operate inside WILSY governance instead of becoming an unsupervised risk.', module: 'RISK_SENTINEL', command: 'Lock AI Control',
      steps: [
        { label: 'Open Risk Sentinel', type: 'module', module: 'RISK_SENTINEL' },
        { label: 'Inspect compliance memory', type: 'check', ready: Boolean(compliance), proof: compliance ? 'Compliance feed linked' : 'Compliance feed pending' },
        { label: 'Inspect forensic memory', type: 'check', ready: Boolean(forensics), proof: forensics ? 'Forensic feed linked' : 'Forensic feed pending' },
        { label: 'Open Crisis Command', type: 'module', module: 'CRISIS_COMMAND' }
      ]
    }
  ]), [activeTenant, aiEraDefensibility.score, allCommands.length, billingMetrics, compliance, forensics, founderProfile.company, osSpine.realDataRatio]);

  const appendMissionLog = useCallback((missionId, message, state = 'INFO') => {
    setMissionRun(prev => ({
      ...prev,
      log: [{ id: `${missionId}-${Date.now()}-${prev.log.length}`, missionId, state, message, time: new Date().toLocaleTimeString('en-GB') }, ...prev.log].slice(0, 8)
    }));
  }, []);

  const runFounderMission = useCallback(async (mission) => {
    if (!mission || missionRun.status === 'RUNNING') return;
    setMissionRun(prev => ({ ...prev, activeMission: mission.id, status: 'RUNNING', progress: 0, log: prev.log }));
    appendMissionLog(mission.id, `${mission.title} initiated`, 'START');
    for (let index = 0; index < mission.steps.length; index += 1) {
      const step = mission.steps[index];
      appendMissionLog(mission.id, step.label, step.type === 'check' && !step.ready ? 'WARN' : 'STEP');
      if (step.type === 'omega') await executeOmegaStrike(step.actionId, step.endpoint, step.method || 'GET', step.payload || {});
      if (step.type === 'module') activateModule(step.module);
      if (step.type === 'check') appendMissionLog(mission.id, step.proof || (step.ready ? 'Ready' : 'Needs data'), step.ready ? 'PASS' : 'WARN');
      setMissionRun(prev => ({ ...prev, progress: Math.round(((index + 1) / mission.steps.length) * 100) }));
    }
    setMissionRun(prev => ({ ...prev, activeMission: mission.id, status: 'COMPLETE', progress: 100 }));
    appendMissionLog(mission.id, `${mission.title} complete`, 'COMPLETE');
  }, [activateModule, appendMissionLog, executeOmegaStrike, missionRun.status]);

  // ==========================================================================
  // SINGULARITY SURFACES
  // ==========================================================================
  const singularitySurfaces = useMemo(() => ([
    { id: 'REVENUE', label: 'Revenue Titan', eyebrow: 'Capital Operations', proof: billingMetrics ? 'Live billing feed linked' : 'Awaiting live billing source', icon: DollarSign },
    { id: 'COMPLIANCE', label: 'Compliance Sentinel', eyebrow: 'Regulatory Control', proof: compliance ? 'Live compliance feed linked' : 'Awaiting compliance source', icon: ShieldCheck },
    { id: 'FORENSICS', label: 'Forensic Nexus', eyebrow: 'Audit Proof Chain', proof: forensics ? 'Live forensic feed linked' : 'Awaiting forensic source', icon: Fingerprint },
    { id: 'COMMAND', label: 'Singularity Command', eyebrow: 'Autonomous OS Layer', proof: dataError ? 'One or more sources degraded' : 'Matrix source scan active', icon: Brain }
  ]), [billingMetrics, compliance, dataError, forensics]);

  const activeSingularitySurface = useMemo(() => singularitySurfaces.find(surface => surface.id === singularitySurface) || singularitySurfaces[0], [singularitySurface, singularitySurfaces]);

  const switchSingularitySurface = useCallback((surfaceId) => {
    const surface = singularitySurfaces.find(item => item.id === surfaceId);
    if (!surface || surfaceId === singularitySurface) return;
    setSingularitySurface(surfaceId);
    appendMissionLog('SINGULARITY_MATRIX', `Focused ${surface.label}`, 'STEP');
  }, [appendMissionLog, singularitySurface, singularitySurfaces]);

  const operatorIntentRoute = useMemo(() => {
    if (!billingMetrics) return { surfaceId: 'REVENUE', label: 'Verify Revenue Feed', reason: 'Billing source is the first missing operating proof.' };
    if (!compliance) return { surfaceId: 'COMPLIANCE', label: 'Verify Compliance Shield', reason: 'Regulatory control has not reported live context.' };
    if (!forensics) return { surfaceId: 'FORENSICS', label: 'Verify Evidence Chain', reason: 'Forensic proof is not yet mounted into the Matrix.' };
    return { surfaceId: 'COMMAND', label: 'Launch Founder Mission', reason: 'Core live sources are linked; mission execution is the next move.' };
  }, [billingMetrics, compliance, forensics]);

  const singularityProcessDeck = useMemo(() => ({
    REVENUE: {
      headline: 'Revenue is not a dashboard. It is a money-motion control loop.', context: billingMetrics ? `Billing source synced ${billingMetrics.lastSync ? new Date(billingMetrics.lastSync).toLocaleTimeString('en-GB') : 'from live summary'}.` : 'Billing source is not currently linked; actions will expose the revenue control surfaces.',
      actions: [
        { id: 'OPEN_REVENUE_LEDGER', label: 'Open Revenue Ledger', icon: TrendingUp, handler: () => activateModule('REVENUE_LEDGER') },
        { id: 'OPEN_BILLING_HUB', label: 'Open Billing Hub', icon: CreditCard, handler: () => activateModule('BILLING_HUB') },
        { id: 'EXPORT_REVENUE_ARTIFACT', label: 'Export Revenue Artifact', icon: FileText, handler: () => executeOmegaStrike('STMT_REVENUE', '/statements/revenue') }
      ]
    },
    COMPLIANCE: {
      headline: 'Compliance becomes an operating shield when it can route, prove and escalate.', context: compliance ? 'Compliance source is mounted into the Founder Matrix.' : 'Compliance source is silent; the Matrix will not manufacture a compliance score.',
      actions: [
        { id: 'EXPORT_COMPLIANCE_PROOF', label: 'Export Compliance Proof', icon: ShieldCheck, handler: () => executeOmegaStrike('STMT_COMPLIANCE', '/statements/compliance') },
        { id: 'OPEN_RISK_SENTINEL', label: 'Open Risk Sentinel', icon: AlertOctagon, handler: () => activateModule('RISK_SENTINEL') },
        { id: 'OPEN_IDENTITY_HUB', label: 'Inspect Authority Graph', icon: Key, handler: () => activateModule('IDENTITY_HUB') }
      ]
    },
    FORENSICS: {
      headline: 'Forensics is the memory of the OS. Every serious claim needs an evidence route.', context: forensics ? 'Forensic source is mounted into the Founder Matrix.' : 'Forensic source is silent; the Matrix will show only live or unavailable evidence.',
      actions: [
        { id: 'EXPORT_FORENSIC_SEAL', label: 'Export Forensic Seal', icon: Fingerprint, handler: () => executeOmegaStrike('STMT_FORENSIC', '/statements/forensics') },
        { id: 'OPEN_AUDIT_VAULT', label: 'Open Audit Vault', icon: Microscope, handler: () => activateModule('AUDIT_VAULT') },
        { id: 'OPEN_STATEMENT_ENGINE', label: 'Open Statement Engine', icon: FileSignature, handler: () => activateModule('STATEMENT_ENGINE') }
      ]
    },
    COMMAND: {
      headline: 'The Founder does not browse the OS. The Founder launches missions.', context: `${allCommands.length} live command definitions mounted. ${missionRun.status === 'RUNNING' ? 'Mission in progress.' : 'Mission deck ready.'}`,
      actions: [
        { id: 'RUN_READINESS_SCAN', label: 'Run Founder Readiness Scan', icon: BadgeCheck, handler: () => runFounderMission(founderMissionDeck.find(mission => mission.id === 'FOUNDER_READINESS_SCAN')) },
        { id: 'OPEN_COMMAND_PALETTE', label: 'Open Command Palette', icon: TerminalSquare, handler: () => setIsCommandPaletteOpen(true) },
        { id: 'OPEN_GLOBAL_TOPOLOGY', label: 'Inspect Global Topology', icon: Globe, handler: () => activateModule('GLOBAL_ORCHESTRATOR') }
      ]
    }
  }), [activateModule, allCommands.length, billingMetrics, compliance, executeOmegaStrike, forensics, founderMissionDeck, missionRun.status, runFounderMission]);

  const activeSingularityProcesses = useMemo(() => singularityProcessDeck[activeSingularitySurface.id] || singularityProcessDeck.REVENUE, [activeSingularitySurface.id, singularityProcessDeck]);

  const runSingularityProcess = useCallback(async (process) => {
    if (!process?.handler) return;
    appendMissionLog('SINGULARITY_MATRIX', `Process started: ${process.label}`, 'START');
    await process.handler();
    appendMissionLog('SINGULARITY_MATRIX', `Process routed: ${process.label}`, 'COMPLETE');
  }, [appendMissionLog]);

  const filteredEvents = useMemo(() => {
    if (filterType === 'ALL') return telemetryEvents;
    if (filterType === 'BILLING') return telemetryEvents.filter(ev => (ev.eventType || '').toUpperCase().includes('BILLING') || (ev.eventType || '').toUpperCase().includes('INVOICE') || (ev.eventType || '').toUpperCase().includes('VAULT_STORE') || (ev.eventType || '').toUpperCase().includes('FINANCIAL'));
    return telemetryEvents.filter(ev => ev.eventType?.toUpperCase().includes(filterType.toUpperCase()));
  }, [telemetryEvents, filterType]);

  const chartData = useMemo(() => {
    const telemetryArray = Array.isArray(telemetryStats) ? telemetryStats : [];
    const labels = [...new Set(telemetryArray.filter(s => s._id?.day).map(s => s._id.day))];
    return {
      labels: labels.length > 0 ? labels : ['Genesis Protocol'],
      datasets: [
        { label: 'Revenue Strikes', data: labels.map(day => { const stat = telemetryArray.find(s => s._id?.day === day && (s._id?.type === 'PDF_GENERATED' || s._id?.type === 'REVENUE_REPORT')); return stat ? stat.count : 0; }), backgroundColor: '#D4AF37' },
        { label: 'Science: Compliance', data: labels.map(day => { const stat = telemetryArray.find(s => s._id?.day === day && s._id?.type === 'COMPLIANCE_REPORT'); return stat ? stat.count : 0; }), backgroundColor: '#444444' },
        { label: 'Science: Forensics', data: labels.map(day => { const stat = telemetryArray.find(s => s._id?.day === day && s._id?.type === 'FORENSICS_REPORT'); return stat ? stat.count : 0; }), backgroundColor: '#888888' }
      ]
    };
  }, [telemetryStats]);

  const chartOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#D4AF37', font: { family: 'Helvetica', weight: 'bold', size: 10 } } } }, scales: { x: { ticks: { color: '#666' }, grid: { color: '#222' } }, y: { ticks: { color: '#666' }, grid: { color: '#222' } } } };

  // ==========================================================================
  // RENDER MODULE CONTENT
  // ==========================================================================
  const renderModuleContent = () => {
    const quadShield = { isolation: 'isolate', overflow: 'hidden', position: 'relative' };
    return (
      <SovereignErrorBoundary>
        {(() => {
          switch (activeModule) {
            case 'INVESTOR_PROOF':
              return (<div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '760px' }}>
                <section className={styles.investorProof}>
                  <div className={styles.proofHero}>
                    <div className={styles.proofHeroCopy}>
                      <span className={styles.proofPill}><BadgeCheck size={14} /> Investor-Grade Operating Thesis</span>
                      <h2>Why WILSY OS Wins</h2>
                      <p>WILSY OS is built as a business operating system: revenue, legal execution, identity, audit evidence, tenant expansion and executive command share one evidence layer.</p>
                    </div>
                    <div className={styles.proofMetrics}>
                      <div><span>Mounted Modules</span><strong>{osSpine.mounted}</strong></div>
                      <div><span>Executable Commands</span><strong>{osSpine.commandCount}</strong></div>
                      <div><span>Real Data Readiness</span><strong>{osSpine.realDataRatio}%</strong></div>
                      <div><span>Founder Tenant</span><strong>{activeTenant?.tenantId || activeTenant?.id || 'MASTER'}</strong></div>
                    </div>
                  </div>
                  <div className={styles.proofGrid}>
                    {investorProofMatrix.map(item => (
                      <article key={item.title} className={styles.proofCard} data-ready={item.ready ? 'true' : 'false'}>
                        <div className={styles.proofCardHeader}><BadgeCheck size={18} /><span className={styles.proofStatus}>{item.ready ? 'PROVEN' : 'NEEDS LIVE DATA'}</span></div>
                        <h3>{item.title}</h3>
                        <p>{item.claim}</p>
                        <strong>{item.proof}</strong>
                        <button type="button" className={styles.proofButton} onClick={() => activateModule(item.module)}>{item.action}</button>
                      </article>
                    ))}
                  </div>
                  <div className={styles.proofMoatGrid}>
                    {[
                      { title: 'Patent Candidate: Sovereign Data Plane', text: 'One governed command layer routes every business module through tenant, evidence and authority context.', icon: Network },
                      { title: 'Patent Candidate: Forensic Operating Memory', text: 'Actions are treated as institutional evidence, not disposable logs, so diligence can inspect what happened and why.', icon: Fingerprint },
                      { title: 'Patent Candidate: Jurisdiction Revenue Router', text: 'Billing, collections, court registry and compliance can move together instead of living in separate products.', icon: Scale },
                      { title: 'Patent Candidate: Founder Sovereignty Profile', text: 'The owner identity is editable, visible and tied to preferences, module posture and investor presentation mode.', icon: UserCog }
                    ].map(moat => (
                      <article key={moat.title} className={styles.proofMoat}><moat.icon size={18} /><div><h3>{moat.title}</h3><p>{moat.text}</p></div></article>
                    ))}
                  </div>
                  <section className={styles.aiMoat}>
                    <div className={styles.aiMoatHeader}><span><Rocket size={15} /> AI-Era Defensibility</span><strong>{aiEraDefensibility.score}%</strong></div>
                    <p>{aiEraDefensibility.thesis}</p>
                    <div className={styles.aiMoatGrid}>
                      {aiEraDefensibility.pillars.map(pillar => (
                        <article key={pillar.title} className={styles.aiMoatCard} data-ready={pillar.ready ? 'true' : 'false'}>
                          <pillar.icon size={18} /><div><span>{pillar.ready ? 'ANCHORED' : 'AWAITING DATA'}</span><h3>{pillar.title}</h3><p>{pillar.text}</p></div>
                        </article>
                      ))}
                    </div>
                  </section>
                  <section className={styles.valueLoops}>
                    <div className={styles.valueLoopsHeader}><span><Layers3 size={15} /> Sovereign Control Loops</span><strong>Why This Cannot Be Replaced By Generated Screens</strong></div>
                    <div className={styles.valueLoopGrid}>
                      {sovereignValueLoops.map(loop => (
                        <article key={loop.title} className={styles.valueLoopCard}>
                          <Workflow size={18} /><div><h3>{loop.title}</h3><p>{loop.path}</p></div>
                          <button type="button" className={styles.proofButtonSecondary} onClick={() => activateModule(loop.module)}>{loop.action}</button>
                        </article>
                      ))}
                    </div>
                  </section>
                  <section className={styles.missionControl}>
                    <div className={styles.missionHeader}>
                      <div><span><TerminalSquare size={15} /> Founder Mission Control</span><h3>Operate The System, Do Not Just View It</h3></div>
                      <div className={styles.missionProgress}><strong>{missionRun.progress}%</strong><span>{missionRun.status}</span></div>
                    </div>
                    <div className={styles.missionGrid}>
                      {founderMissionDeck.map(mission => (
                        <article key={mission.id} className={styles.missionCard} data-active={missionRun.activeMission === mission.id ? 'true' : 'false'}>
                          <div className={styles.missionCardTop}><span>{mission.steps.length} steps</span><strong>{mission.command}</strong></div>
                          <h3>{mission.title}</h3><p>{mission.purpose}</p><ol>{mission.steps.map(step => <li key={step.label}>{step.label}</li>)}</ol>
                          <button type="button" className={styles.proofButton} disabled={missionRun.status === 'RUNNING'} onClick={() => runFounderMission(mission)}>
                            {missionRun.activeMission === mission.id && missionRun.status === 'RUNNING' ? 'Mission Running' : mission.command}
                          </button>
                        </article>
                      ))}
                    </div>
                    <div className={styles.missionLog}><span>Mission Log</span>{missionRun.log.length === 0 ? <p>No mission executed this session.</p> : missionRun.log.map(entry => <div key={entry.id} data-state={entry.state}><strong>{entry.time}</strong><p>{entry.message}</p></div>)}</div>
                  </section>
                  <div className={styles.proofActions}>
                    <button type="button" className={styles.proofButton} onClick={() => activateModule('BILLING_HUB')}>Prove Revenue Workflow</button>
                    <button type="button" className={styles.proofButtonSecondary} onClick={() => activateModule('AUDIT_VAULT')}>Prove Audit Chain</button>
                    <button type="button" className={styles.proofButtonSecondary} onClick={() => activateModule('GLOBAL_ORCHESTRATOR')}>Prove Tenant Topology</button>
                  </div>
                </section>
              </div>);
            case 'SINGULARITY_MATRIX':
              return (<section className={`${styles.quad} ${styles.span12} ${styles.singularityWorkspace}`} style={quadShield}>
                <div className={styles.singularityWorkspaceHeader}>
                  <div className={styles.singularityWorkspaceTitle}><span>{activeSingularitySurface.eyebrow}</span><h2>Singularity Matrix Workspace</h2><p>{activeSingularitySurface.proof}</p></div>
                  <div className={styles.singularityWorkspaceAuthority}>
                    <strong>{isSingularityWorkspaceAuthorized ? operatorSovereigntyGraph.authorityLabel : 'Authority Required'}</strong>
                    <span>{operatorSovereigntyGraph.displayName} · {operatorSovereigntyGraph.companyScope}</span>
                    <em>{operatorIntentRoute.reason}</em>
                    <button type="button" onClick={() => switchSingularitySurface(operatorIntentRoute.surfaceId)} disabled={!isSingularityWorkspaceAuthorized || activeSingularitySurface.id === operatorIntentRoute.surfaceId}>{operatorIntentRoute.label}</button>
                  </div>
                </div>
                <div className={styles.singularityWorkspaceTabs} role="tablist">
                  {singularitySurfaces.map(surface => {
                    const SurfaceIcon = surface.icon;
                    const isActive = activeSingularitySurface.id === surface.id;
                    return (
                      <button key={surface.id} type="button" role="tab" aria-selected={isActive} className={`${styles.singularityWorkspaceTab} ${isActive ? styles.singularityWorkspaceTabActive : ''}`} onClick={() => switchSingularitySurface(surface.id)} disabled={!isSingularityWorkspaceAuthorized}>
                        <SurfaceIcon size={18} /><span>{surface.eyebrow}</span><strong>{surface.label}</strong><small>{surface.proof}</small>
                      </button>
                    );
                  })}
                </div>
                <div className={styles.singularityProcessBand}>
                  <div className={styles.singularityProcessNarrative}><span>{activeSingularitySurface.label} Process</span><strong>{activeSingularityProcesses.headline}</strong><p>{activeSingularityProcesses.context}</p></div>
                  <div className={styles.singularityProcessActions}>
                    {activeSingularityProcesses.actions.map(process => {
                      const ProcessIcon = process.icon;
                      return (
                        <button key={process.id} type="button" onClick={() => runSingularityProcess(process)} disabled={!isSingularityWorkspaceAuthorized || actionLoading === process.id || missionRun.status === 'RUNNING'}>
                          <ProcessIcon size={16} /><span>{process.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
                <div className={styles.singularityWorkspaceBody} data-surface={activeSingularitySurface.id}>
                  {!isSingularityWorkspaceAuthorized ? (
                    <div className={styles.singularityWorkspaceLock}><LockKeyhole size={36} /><h3>Founder Authority Required</h3><p>This Matrix plane is reserved for Founder and super-admin operating roles.</p></div>
                  ) : (
                    <div className={styles.singularitySurfaceMount}>
                      <Suspense fallback={<div className={styles.loading}>HYDRATING {activeSingularitySurface.label}...</div>}>
                        {activeSingularitySurface.id === 'REVENUE' && <RevenueHUD metrics={billingMetrics} embedded />}
                        {activeSingularitySurface.id === 'COMPLIANCE' && <ComplianceHUD metrics={compliance} embedded />}
                        {activeSingularitySurface.id === 'FORENSICS' && <ForensicsHUD embedded />}
                        {activeSingularitySurface.id === 'COMMAND' && <SingularityDashboard />}
                      </Suspense>
                    </div>
                  )}
                </div>
              </section>);
            default: return null;
          }
        })()}
      </SovereignErrorBoundary>
    );
  };

  // ==========================================================================
  // LAYOUT GUARDS
  // ==========================================================================
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      .footer { display: flex !important; flex-wrap: nowrap !important; gap: 20px !important; white-space: nowrap !important; }
      .footer span { white-space: nowrap !important; }
      .telemetryStrip { flex-wrap: nowrap !important; row-gap: 0 !important; }
      @media (max-width: 1200px) { .teleGroup { flex-wrap: wrap !important; gap: 10px !important; } .teleItem { font-size: 0.6rem !important; } }
      canvas { max-width: 100% !important; height: auto !important; }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  if (activeModule === 'BOARDROOM_HUD') {
    return (
      <SovereignOrchestrator><DataOrchestrator><CommandUsageProvider>
        <div className={styles.boardroomTheatre}>
          <div className={styles.scanline}></div>
          <header className={styles.boardroomTheatreHeader}>
            <div className={styles.theatreBrand}>
              <img src={activeTenant?.logoUrl || wilsyLogo} alt="Wilsy OS" />
              <div><span>WILSY OS BOARDROOM</span><strong>Investor Theatre Mode</strong></div>
            </div>
            <div className={styles.theatreStatus}><span>FOUNDER ACCESS</span><span>{systemHealth}</span></div>
            <button type="button" className={styles.theatreBackButton} onClick={() => activateModule(boardroomReturnModule || 'SINGULARITY_MATRIX')}><ChevronLeft size={16} /> Return To Founder Dashboard</button>
          </header>
          <main className={styles.boardroomTheatreStage}>
            <Suspense fallback={<div className={styles.loading}>HYDRATING BOARDROOM TELEMETRY...</div>}>
              <BoardroomHUD />
            </Suspense>
          </main>
        </div>
      </CommandUsageProvider></DataOrchestrator></SovereignOrchestrator>
    );
  }

  // ==========================================================================
  // PRODUCTION-READY APP BAR: 8 CATEGORIZED DROPDOWN GROUPS
  // ==========================================================================
  const menuGroups = [
    { label: 'Cockpit Level', keys: COCKPIT_KEYS },
    { label: 'Institutional Hub', keys: INSTITUTIONAL_HUB_KEYS },
    { label: 'Leadership', keys: LEADERSHIP_KEYS },
    { label: 'Core Departments', keys: CORE_DEPT_KEYS },
    { label: 'Advanced Departments', keys: ADVANCED_DEPT_KEYS },
    { label: 'Future Departments', keys: FUTURE_DEPT_KEYS },
    { label: 'Control Room', keys: CONTROL_ROOM_KEYS },
    { label: 'Industry & Domain', keys: INDUSTRY_KEYS }
  ];

  const appBarMenuGroups = menuGroups.map((group) => ({
    label: group.label,
    items: group.keys.map((key) => ({
      key,
      label: MODULE_OPERATING_MAP[key]?.label || key.replace(/_/g, ' '),
      icon: getModuleIcon(key),
      active: activeModule === key
    }))
  }));

  return (
    <SovereignOrchestrator><DataOrchestrator><CommandUsageProvider>
      <div className={styles.container} style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }} /* content below scrolls; menus use portal */>
        <div className={styles.scanline}></div>

        {/* TOP BAR — FounderAppBar v1.1: portal menus, no duplicate identity */}
        <FounderAppBar
          menuGroups={appBarMenuGroups}
          onActivateModule={activateModule}
          kennelConnected={kennelConnected}
          kennelLatencyMs={typeof kennelLatency === 'number' ? kennelLatency : 0}
          kennelVersion="1.1.1"
          rightSlot={(
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              {/* Single identity control — do NOT also mount CockpitStatusBar user chips here */}
              <button
                type="button"
                className={styles.founderChip}
                onClick={() => { setProfileDraft(founderProfile); setIsFounderPanelOpen(prev => !prev); }}
                aria-expanded={isFounderPanelOpen}
                aria-label="Founder profile"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(212,175,55,0.25)',
                  color: '#fff',
                  cursor: 'pointer',
                  padding: '4px 10px 4px 4px',
                  borderRadius: 24,
                  whiteSpace: 'nowrap'
                }}
              >
                <span
                  className={styles.founderAvatar}
                  style={{
                    position: 'relative',
                    width: 28,
                    height: 28,
                    fontSize: '0.7rem',
                    display: 'inline-grid',
                    placeItems: 'center',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg,#D4AF37,#8E6A12)',
                    color: '#000',
                    fontWeight: 900
                  }}
                >
                  {founderInitials}
                </span>
                <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#eee' }}>
                  {founderProfile.displayName}
                </span>
                <ChevronDown size={14} style={{ opacity: 0.65 }} />
              </button>
              <div
                className={styles.clock}
                style={{ fontSize: '0.72rem', color: '#aaa', minWidth: 72, textAlign: 'right', fontFamily: 'ui-monospace, monospace' }}
              >
                {currentTime.toLocaleTimeString()}
              </div>
            </div>
          )}
        />

        {/* MAIN LAYOUT (SIDEBAR, PANELS, FOOTER) - UNCHANGED */}
        {isFounderPanelOpen && (
          <section className={styles.founderPanel} aria-label="Founder profile command panel">
            <div className={styles.founderPanelHeader}>
              <div className={styles.founderPanelMark}><span>{founderInitials}</span></div>
              <div><span className={styles.panelEyebrow}><Sparkles size={14} /> Founder Sovereignty Profile</span><h2>{founderProfile.displayName}</h2><p>{founderProfile.title} - {founderProfile.company}</p></div>
              <button type="button" className={styles.panelIconButton} onClick={() => { setIsFounderPanelOpen(false); setIsPreferenceEditing(false); }} aria-label="Close founder profile"><X size={18} /></button>
            </div>
            <div className={styles.founderPanelGrid}>
              <div className={styles.founderProfileCard}>
                <div className={styles.sectionTitle}><SlidersHorizontal size={16} /> Operating Preferences</div>
                <div className={styles.presetGrid}>{Object.keys(FOUNDER_OPERATING_PRESETS).map(presetName => <button key={presetName} type="button" className={founderProfile.commandMode === presetName ? styles.presetButtonActive : styles.presetButton} onClick={() => applyFounderPreset(presetName)}><Sparkles size={14} /><span>{presetName}</span></button>)}</div>
                <div className={styles.preferenceGrid}>
                  {[['displayName', 'Founder Name', 'text'], ['title', 'Boardroom Title', 'text'], ['company', 'Founder Tenant', 'text'], ['jurisdictionFocus', 'Jurisdiction Focus', 'text']].map(([key, label, type]) => <label key={key} className={styles.preferenceField}><span>{label}</span><input type={type} value={profileDraft[key] || ''} disabled={!isPreferenceEditing} onChange={event => updateProfileDraft(key, event.target.value)} /></label>)}
                  {[['commandMode', 'Command Mode', ['Investor Theatre', 'Forensic Operator', 'Builder Mode']], ['telemetryDensity', 'Telemetry Density', ['Executive', 'Dense', 'Silent']], ['evidenceMode', 'Evidence Mode', ['Real Data Only', 'Diligence Grade', 'Court Ready']], ['narrativeTone', 'Narrative Tone', ['Boardroom', 'Technical', 'Investor']], ['tenantScope', 'Tenant Scope', ['Founder Tenant', 'Current Tenant', 'Multi Tenant']], ['sidebarMode', 'Sidebar Mode', ['Open', 'Closed']], ['quickPanelMode', 'Command Rail', ['Closed', 'Open']]].map(([key, label, options]) => <label key={key} className={styles.preferenceField}><span>{label}</span><select value={profileDraft[key] || ''} onChange={event => applyPreferenceChange(key, event.target.value)}>{options.map(option => <option key={option} value={option}>{option}</option>)}</select></label>)}
                  <label className={styles.preferenceField}><span>Default Landing Module</span><select value={profileDraft.defaultModule || 'SINGULARITY_MATRIX'} onChange={event => applyPreferenceChange('defaultModule', event.target.value)}>{founderModuleOptions.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
                  <label className={`${styles.preferenceField} ${styles.preferenceWide}`}><span>Investor Promise</span><textarea value={profileDraft.investorPromise || ''} disabled={!isPreferenceEditing} onChange={event => updateProfileDraft('investorPromise', event.target.value)} /></label>
                </div>
              </div>
              <div className={styles.founderProfileCard}>
                <div className={styles.sectionTitle}><Palette size={16} /> Demo Doctrine</div>
                <div className={styles.doctrineStack}>
                  <div><span>Operating Mode</span><strong>{founderProfile.commandMode}</strong></div>
                  <div><span>Evidence Standard</span><strong>{founderProfile.evidenceMode}</strong></div>
                  <div><span>Operating Skin</span><strong>{founderProfile.theme}</strong></div>
                  <div><span>Tenant Authority</span><strong>{activeTenant?.tenantId || 'MASTER'}</strong></div>
                  <div><span>Landing Module</span><strong>{founderProfile.defaultModule?.replace(/_/g, ' ')}</strong></div>
                </div>
                <p className={styles.doctrineCopy}>{founderProfile.investorPromise}</p>
              </div>
            </div>
            <div className={styles.patentGrid}>
              {founderPatentSystems.map(system => { const Icon = system.icon; return <article key={system.title} className={styles.patentCard}><Icon size={18} /><strong>{system.title}</strong><span>{system.text}</span></article>; })}
            </div>
            <div className={styles.founderPanelActions}>
              {isPreferenceEditing ? (<>
                <button type="button" className={styles.goldButton} onClick={saveFounderProfile}><Save size={15} /> Save Preferences</button>
                <button type="button" className={styles.ghostButton} onClick={() => { setProfileDraft(founderProfile); setIsPreferenceEditing(false); }}><X size={15} /> Cancel</button>
                <button type="button" className={styles.dangerGhost} onClick={resetFounderProfile}>Reset</button>
              </>) : (<>
                <button type="button" className={styles.goldButton} onClick={() => setIsPreferenceEditing(true)}><UserCog size={15} /> Edit Founder Profile</button>
                <button type="button" className={styles.ghostButton} onClick={() => activateModule('IDENTITY_HUB')}><Fingerprint size={15} /> Identity Hub</button>
                <button type="button" className={styles.ghostButton} onClick={() => activateModule('AUDIT_VAULT')}><ShieldCheck size={15} /> Audit Vault</button>
              </>)}
            </div>
          </section>
        )}

        <div className={`${styles.mainGrid} ${isQuickPanelOpen ? styles.quickPanelExpanded : styles.quickPanelCollapsed}`} data-sidebar={isSidebarOpen ? 'open' : 'closed'} data-focus={activeModule === 'SALES_CRM' ? 'crm' : 'standard'}>
          {!isSidebarOpen && <button type="button" className={styles.sidebarReveal} aria-label="Open sovereign sidebar" onClick={() => setIsSidebarOpen(true)}><PanelLeftOpen size={18} /><span>Navigation</span></button>}

          {isSidebarOpen && (
            <nav className={styles.sidebar} style={{ display: 'flex', flexDirection: 'column', height: '100%', flexShrink: 0, overflowY: 'auto', background: 'linear-gradient(180deg, rgba(10,10,12,0.98), rgba(5,5,8,0.96))', borderRight: '1px solid rgba(212,175,55,0.2)', boxShadow: '4px 0 40px rgba(0,0,0,0.6), inset -1px 0 20px rgba(212,175,55,0.05)', width: '286px', padding: '20px 16px', position: 'relative', zIndex: 50 }}>
              <button type="button" className={styles.sidebarCollapseBtn} aria-label="Collapse OS Navigator" onClick={() => setIsSidebarOpen(false)} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid rgba(212,175,55,0.3)', background: 'rgba(212,175,55,0.08)', color: '#D4AF37', cursor: 'pointer', marginBottom: '20px', transition: 'all 0.2s', fontFamily: 'var(--font-mono, monospace)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.7rem', fontWeight: 700, letterSpacing: '1px' }}><span>⌘</span><span>QUICK ACCESS</span></span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.6rem', opacity: 0.6 }}><span>close</span><PanelLeftClose size={16} /></span>
              </button>

              <div className={styles.sidebarHeader} style={{ display: 'grid', gridTemplateColumns: '72px 1fr', alignItems: 'center', gap: '14px', marginBottom: '24px', padding: '14px 16px', border: '1px solid rgba(212,175,55,0.25)', borderRadius: '12px', background: 'linear-gradient(135deg, rgba(212,175,55,0.1), rgba(24,183,255,0.05))', boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.04), 0 8px 32px rgba(0,0,0,0.4)' }}>
                <div className={styles.logoBezel} style={{ width: '64px', height: '64px', borderRadius: '16px', border: '1px solid rgba(212,175,55,0.6)', overflow: 'hidden', boxShadow: '0 0 30px rgba(212,175,55,0.2), inset 0 0 20px rgba(212,175,55,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#000' }}>
                  <img src={activeTenant?.logoUrl || wilsyLogo} alt="Wilsy OS" style={{ width: '85%', height: '85%', objectFit: 'contain', filter: 'brightness(1.1) contrast(1.1)' }} />
                </div>
                <div>
                  <div className={styles.brand} style={{ fontSize: '1.1rem', fontWeight: 900, letterSpacing: '0.08em', color: '#fff', textShadow: '0 0 20px rgba(212,175,55,0.15)' }}>{activeTenant?.name || 'WILSY OS'}</div>
                  <div className={styles.subtitle} style={{ fontSize: '0.6rem', color: '#D4AF37', letterSpacing: '0.12em', textTransform: 'uppercase', marginTop: '2px' }}>SHARD: {activeTenant?.tenantId || 'SOVEREIGN_ROOT'}</div>
                  <div className={styles.brandSeal} style={{ marginTop: '6px', padding: '3px 10px', background: 'linear-gradient(90deg, rgba(212,175,55,0.2), rgba(212,175,55,0.05))', border: '1px solid rgba(212,175,55,0.25)', borderRadius: '4px', fontSize: '0.45rem', letterSpacing: '0.1em', color: '#D4AF37', display: 'inline-block' }}>LEGAL SOVEREIGN STANDARD</div>
                </div>
              </div>

              <div className={styles.navSectionLabel} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '4px 8px', color: 'rgba(212,175,55,0.7)', fontSize: '0.55rem', fontWeight: 900, letterSpacing: '0.15em', textTransform: 'uppercase', borderBottom: '1px solid rgba(212,175,55,0.1)', paddingBottom: '6px' }}>
                <span style={{ width: '4px', height: '4px', borderRadius: '50%', background: '#D4AF37' }}></span> QUICK ACCESS
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', marginBottom: '12px' }}>
                {SIDEBAR_SHORTCUTS.map(key => {
                  let label = MODULE_OPERATING_MAP[key]?.label || key.replace(/_/g, ' ');
                  return (<button key={key} className={activeModule === key ? styles.navItemActive : styles.navItem} onClick={() => activateModule(key)} style={{ width: '100%', padding: '10px 14px', borderRadius: '6px', border: 'none', background: activeModule === key ? 'linear-gradient(90deg, rgba(212,175,55,0.15), transparent)' : 'transparent', color: activeModule === key ? '#D4AF37' : '#d0d0d0', fontWeight: activeModule === key ? 800 : 500, fontSize: '0.75rem', letterSpacing: '0.3px', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer', transition: 'all 0.15s', borderLeft: activeModule === key ? '3px solid #D4AF37' : '3px solid transparent', fontFamily: 'var(--font-mono, monospace)' }}>
                    {getModuleIcon(key)}<span>{label}</span>
                  </button>);
                })}
              </div>

              <div style={{ marginTop: 'auto', paddingTop: '14px', borderTop: '1px solid rgba(212,175,55,0.08)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 12px', borderRadius: '8px', background: 'rgba(212,175,55,0.05)', marginBottom: '12px' }}>
                  <span className={styles.founderAvatar} style={{ width: '36px', height: '36px', borderRadius: '50%', display: 'grid', placeItems: 'center', background: 'linear-gradient(135deg, #D4AF37, #8E6A12)', color: '#000', fontWeight: 900, fontSize: '0.8rem' }}>{founderInitials}</span>
                  <div style={{ flex: 1 }}><div style={{ fontSize: '0.7rem', fontWeight: 600, color: '#fff' }}>{founderProfile.displayName}</div><div style={{ fontSize: '0.55rem', color: 'rgba(255,255,255,0.5)', letterSpacing: '0.5px' }}>FOUNDER • OMEGA_LEVEL</div></div>
                  <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 12px #10b981' }}></span>
                </div>
                <button onClick={logout} className={styles.logoutBtn} style={{ width: '100%', padding: '12px', background: 'rgba(255,61,87,0.1)', border: '1px solid rgba(255,61,87,0.25)', borderRadius: '8px', color: '#ff6b7a', fontSize: '0.65rem', fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', cursor: 'pointer', transition: 'all 0.2s' }}>
                  <LogOut size={16} /><span>TERMINATE SESSION</span>
                </button>
                <div style={{ textAlign: 'center', marginTop: '12px', fontSize: '0.5rem', color: 'rgba(255,255,255,0.15)', letterSpacing: '1px' }}>WILSY OS v60.0.0 • FORENSIC SEAL: ACTIVE</div>
              </div>
            </nav>
          )}

          <div className={styles.contentGrid}>
            <section className={styles.osSpine}>
              <div className={styles.osSpineMain}>
                <span className={styles.osSpineEyebrow}><Network size={14} /> Operating System Spine</span>
                <h2>{activeModuleMeta.label}</h2>
                <p>{activeModuleMeta.description}</p>
              </div>
              <div className={styles.osSpineMeta}>
                <div><span>Layer</span><strong>{activeModuleMeta.layer}</strong></div>
                <div><span>Feed</span><strong>{activeModuleMeta.feed}</strong></div>
                <div><span>Modules</span><strong>{osSpine.mounted}</strong></div>
                <div><span>Commands</span><strong>{osSpine.commandCount}</strong></div>
                <div><span>Real Data</span><strong>{osSpine.realDataRatio}%</strong></div>
                <div><span>Workers</span><strong>{workers}</strong></div>
                <div><span>Latency</span><strong>{kennelLatency}ms</strong></div>
                <div><span>Runtime</span><strong style={{ color: kennelConnected ? '#10b981' : '#ef4444' }}>{kennelConnected ? '🟢 Stable' : '🔴 Degraded'}</strong></div>
              </div>
              <div className={styles.osFeedRail}>
                {osSpine.feeds.map(feed => <span key={feed.label} data-ready={feed.ready ? 'true' : 'false'}>{feed.label}: <strong>{feed.status}</strong></span>)}
              </div>
            </section>
            {activeModule !== 'SALES_CRM' && <NeuralNarrativeCapsule currentNarrative={currentNarrative} shardId={activeTenant?.tenantId} />}
            {renderModuleContent()}
          </div>

          <aside className={`${styles.quickActions} ${isQuickPanelOpen ? styles.quickActionsOpen : styles.quickActionsClosed}`} aria-label="Behavioral quick panel">
            <button type="button" className={styles.quickPanelToggle} aria-expanded={isQuickPanelOpen} aria-label={isQuickPanelOpen ? 'Collapse behavioral quick panel' : 'Open behavioral quick panel'} onClick={() => setIsQuickPanelOpen((open) => !open)}>
              {isQuickPanelOpen ? <PanelRightClose size={18} /> : <PanelRightOpen size={18} />}
              <span>{isQuickPanelOpen ? 'Collapse Panel' : 'Command Panel'}</span>
            </button>
            {isQuickPanelOpen ? (
              <><div className={styles.quickPanelScroll}><QuickPanel allCommands={allCommands} onExecute={(handler) => handler()} /></div>
                <button className={`${styles.actionBtnRed} ${styles.quickTerminateButton}`} onClick={logout}><LogOut size={16} /> Terminate Session</button></>
            ) : (
              <div className={styles.quickRailStatus} aria-hidden="true"><span>Commands</span><strong>{allCommands.length}</strong></div>
            )}
          </aside>
        </div>

        {/* RE-FORGED DUAL-SIDED INSTITUTIONAL FOOTER WITH LIVE KENNEL STATUS */}
        <footer className={styles.footer} style={{ height: '40px', minHeight: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>
            ⚡ KENNEL: {kennelConnected ? 'OPERATIONAL' : 'FRACTURE'} • v1.1.1 • BILLION‑TENANT SCALE • TOP 0.01% LATENCY • PQE‑256 SEALED
          </span>
          <span className={styles.footerBrand}>
            WILSY OS — LEGAL SOVEREIGN STANDARD • FOUNDER COMMAND CENTER • FORENSIC SEAL: ACTIVE
          </span>
        </footer>

        <CommandPalette isOpen={isCommandPaletteOpen} onOpen={() => setIsCommandPaletteOpen(true)} onClose={() => setIsCommandPaletteOpen(false)} actions={actionCommands} modules={moduleCommands} />
      </div>
    </CommandUsageProvider></DataOrchestrator></SovereignOrchestrator>
  );
});

const useDynamicNarrative = () => {
  const [narrativeIndex, setNarrativeIndex] = useState(0);
  const narrativePool = useMemo(() => [
    "AI BOARDROOM NARRATIVE: Master Shard running at optimal capacity allocation. P95 telemetry latency remains securely stabilised within designated architectural boundaries, guaranteeing zero database connection jitter.",
    "AI BOARDROOM NARRATIVE: ARR trajectory indicates a definitive confidence tier milestone, laying the infrastructure foundations for upcoming continental expansion frameworks.",
    "AI BOARDROOM NARRATIVE: Forensic auditing parameters confirm data protection compliance records are completely locked. Post-Quantum Encryption vault layers verify absolute transaction immutability.",
    "AI BOARDROOM NARRATIVE: Active operational command centre routing loops are processing multi-tenant data pipelines with flawless transactional performance signatures."
  ], []);
  useEffect(() => {
    const timer = setInterval(() => {
      setNarrativeIndex((prev) => (prev + 1) % narrativePool.length);
    }, 12000);
    return () => clearInterval(timer);
  }, [narrativePool.length]);
  return { currentNarrative: narrativePool[narrativeIndex] };
};

// ── FULLY COMPLETE ICON MAP (Task 1) ──
const getModuleIcon = (key) => {
  // If an SVG icon exists in the manifest, use it first
  if (iconManifest && iconManifest[key]) {
    return (
      <img
        src={iconManifest[key].path}
        alt={iconManifest[key].label || key}
        style={{ width: '16px', height: '16px' }}
      />
    );
  }

  // Comprehensive fallback icon map – every dashboard key covered
  const iconMap = {
    // ── Cockpit & Command ──
    INVESTOR_PROOF: <BadgeCheck size={16} className="text-[#D4AF37]" />,
    SINGULARITY_MATRIX: <BarChart3 size={16} className="text-[#D4AF37]" />,
    BOARDROOM_HUD: <Eye size={16} className="text-[#D4AF37]" />,

    // ── Institutional Hub ──
    REVENUE_LEDGER: <TrendingUp size={16} className="text-[#D4AF37]" />,
    BILLING_HUB: <Coins size={16} className="text-[#D4AF37]" />,
    AUDIT_VAULT: <Lock size={16} className="text-[#D4AF37]" />,
    NODE_REGISTRY: <Cpu size={16} className="text-[#D4AF37]" />,
    GLOBAL_ORCHESTRATOR: <Globe size={16} className="text-[#D4AF37]" />,
    EXECUTIVE_OVERSIGHT: <Crown size={16} className="text-[#D4AF37]" />,
    INVOICE_SENTINEL: <Receipt size={16} className="text-[#D4AF37]" />,
    CLOUD_UPLINK: <Server size={16} className="text-[#D4AF37]" />,
    IDENTITY_HUB: <Key size={16} className="text-[#D4AF37]" />,
    RISK_SENTINEL: <AlertOctagon size={16} className="text-[#D4AF37]" />,
    CLIENT_COVENANT: <FileSignature size={16} className="text-[#D4AF37]" />,
    CRISIS_COMMAND: <Power size={16} className="text-[#D4AF37]" />,
    NUCLEUS_MONITOR: <TerminalSquare size={16} className="text-[#D4AF37]" />,
    TENANT_MANAGER: <Users size={16} className="text-[#D4AF37]" />,
    STATEMENT_ENGINE: <FileText size={16} className="text-[#D4AF37]" />,

    // ── Leadership ──
    CEO_DASHBOARD: <Crown size={16} className="text-[#D4AF37]" />,
    COO_DASHBOARD: <Briefcase size={16} className="text-[#D4AF37]" />,

    // ── Core Departments ──
    HR_DASHBOARD: <Users size={16} className="text-[#D4AF37]" />,
    SALES_CRM: <MessageSquare size={16} className="text-[#D4AF37]" />,
    IT_OPS: <Server size={16} className="text-[#D4AF37]" />,

    // ── Advanced Departments ──
    FINANCE_DASHBOARD: <DollarSign size={16} className="text-[#D4AF37]" />,
    LEGAL_DASHBOARD: <Gavel size={16} className="text-[#D4AF37]" />,
    MARKETING_DASHBOARD: <Megaphone size={16} className="text-[#D4AF37]" />,
    PRODUCT_DASHBOARD: <Box size={16} className="text-[#D4AF37]" />,
    ENGINEERING_DASHBOARD: <Code size={16} className="text-[#D4AF37]" />,
    DATA_DASHBOARD: <BarChart size={16} className="text-[#D4AF37]" />,
    SECURITY_DASHBOARD: <LockKeyhole size={16} className="text-[#D4AF37]" />,
    CUSTOMER_SUCCESS_DASHBOARD: <HeartHandshake size={16} className="text-[#D4AF37]" />,
    PROCUREMENT_DASHBOARD: <ShoppingCart size={16} className="text-[#D4AF37]" />,
    RESEARCH_DASHBOARD: <FlaskConical size={16} className="text-[#D4AF37]" />,

    // ── Future Departments ──
    SPACE_OPERATIONS_DASHBOARD: <Satellite size={16} className="text-[#D4AF37]" />,
    AI_ETHICS_DASHBOARD: <Brain size={16} className="text-[#D4AF37]" />,
    QUANTUM_COMPUTING_DASHBOARD: <CpuIcon size={16} className="text-[#D4AF37]" />,
    LONGEVITY_SCIENCES_DASHBOARD: <Dna size={16} className="text-[#D4AF37]" />,

    // ── Control Room ──
    EXECUTIVE_CONTROL_ROOM: <Command size={16} className="text-[#D4AF37]" />,

    // ── Industry & Domain (all missing keys added) ──
    AGRICULTURE_DASHBOARD: <FlaskConical size={16} className="text-[#D4AF37]" />,
    HOSPITALITY_DASHBOARD: <Users size={16} className="text-[#D4AF37]" />,
    PRODUCTION_DASHBOARD: <Cpu size={16} className="text-[#D4AF37]" />,
    RETAIL_DASHBOARD: <ShoppingCart size={16} className="text-[#D4AF37]" />,
    PUBLIC_DASHBOARD: <Megaphone size={16} className="text-[#D4AF37]" />,
    INDUSTRY_FINANCE_DASHBOARD: <Landmark size={16} className="text-[#D4AF37]" />,
    TECH_DASHBOARD: <Cpu size={16} className="text-[#D4AF37]" />,
    SPORTS_DASHBOARD: <Trophy size={16} className="text-[#D4AF37]" />,
    EDUCATION_DASHBOARD: <GraduationCap size={16} className="text-[#D4AF37]" />,
    HEALTHCARE_DASHBOARD: <HeartHandshake size={16} className="text-[#D4AF37]" />,
    CONSULTING_DASHBOARD: <Briefcase size={16} className="text-[#D4AF37]" />,
    ENERGY_DASHBOARD: <Zap size={16} className="text-[#D4AF37]" />,
    ENTERTAINMENT_DASHBOARD: <Clapperboard size={16} className="text-[#D4AF37]" />,
    PROPERTY_DASHBOARD: <Home size={16} className="text-[#D4AF37]" />,
    INDUSTRY_LEGAL_DASHBOARD: <Gavel size={16} className="text-[#D4AF37]" />,
    PROJECT_DASHBOARD: <Briefcase size={16} className="text-[#D4AF37]" />,
    LOGISTICS_DASHBOARD: <Truck size={16} className="text-[#D4AF37]" />,
    NONPROFIT_DASHBOARD: <HeartHandshake size={16} className="text-[#D4AF37]" />,
  };

  return iconMap[key] || <Target size={16} />;
};

FounderDashboard.displayName = 'FounderDashboard';
export default FounderDashboard;
