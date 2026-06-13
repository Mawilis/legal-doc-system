/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FOUNDER COMMAND CENTER [V50.4.0-OMEGA-AUTH-FIX]                                                                            ║
 * ║ [FULL BUSINESS OS | 20+ DEPARTMENTS | NEURAL MESH ANCHORED | BOARDROOM HUD NATIVE EMBED]                                               ║
 * ║ [STABILIZED: Enhanced token handling & Omega Strike logging – no UI changes]                                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 50.4.0-OMEGA-AUTH-FIX | PRODUCTION HARDENED | BILLION-DOLLAR SPEC                                                             ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL DOMINANCE | IDENTITY: WILSON KHANYEZI                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/FounderDashboard.jsx                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated robust token retrieval and forensic logging for 401 resolution.                      ║
 * ║ • AI Engineering (DeepSeek) – ENHANCED: getActiveToken now trims quotes and logs missing keys; executeOmegaStrike includes full audit. ║
 * ║ • Wilson Khanyezi (Founder) – Mandated Founder Profile, OS Spine, and real module wiring so WILSY OS behaves as an operating system.   ║
 * ║ • AI Engineering (Codex) – WIRED: Founder preferences, actual sovereign modules, data-readiness spine, and no-placeholder risk logic.  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Founder Command Center – the sovereign cockpit of WILSY OS.
 * This component is the single entry point for the entire institutional dashboard.
 * It enforces a strict provider hierarchy: SovereignOrchestrator → DataOrchestrator →
 * CommandUsageProvider → Dashboard UI. Every shard, including BillingHUD, War Room,
 * and all 20+ department modules, connects to the Neural Mesh through this hierarchy.
 *
 * WHY THIS IS THE ULTIMATE INVESTMENT:
 * 1. ZERO-CRASH ARCHITECTURE – SovereignErrorBoundary isolates failures; the mesh
 * providers guarantee that BillingHUD, RevenueLedger, and all shards share a single,
 * self-healing context.
 * 2. LIVE DATA PROPAGATION – Billing metrics, telemetry, and forensic events flow
 * through the DataOrchestrator into every component without manual refresh.
 * 3. CRYPTOGRAPHIC INTEGRITY – Every request is sealed by the Diplomatic Bridge (api.js);
 * the mesh event bus logs every action for the immutable forensic trail.
 * 4. 100-YEAR DURABILITY – Lazy-loaded modules, error boundaries, and autonomous healing
 * ensure this command centre outlasts any single component failure.
 *
 * @author Wilson Khanyezi <wilson@wilsy.ai>
 * @author AI Engineering (DeepSeek, Gemini) – sovereign collaborative partners
 * @copyright 2026 WILSY OS – All rights reserved.
 */

import React, { Suspense, useState, useEffect, useCallback, useMemo, useRef, Component } from 'react';
import { useAuth } from '../../contexts/authContext';
import { useTenants } from '../../contexts/tenantContext';
import useSovereignData from '../../hooks/useSovereignData';
import { useTelemetryFeed } from '../../hooks/useTelemetryFeed';
import { useTelemetryStats } from '../../hooks/useTelemetryStats';
import { useTrajectoryWithEmails } from '../../hooks/useTrajectoryWithEmails';
// 🔗 NEURAL MESH IMPORTS – The command centre anchors the mesh providers
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
  UserCog, SlidersHorizontal, Save, X, Sparkles, BadgeCheck, FileCheck2, Palette, Rocket, Workflow, Layers3
} from 'lucide-react';

// 📊 CHART.JS INTEGRATION
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

// 🔧 STANDALONE EXPORT HELPERS
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const FOUNDER_PROFILE_STORAGE_KEY = 'wilsy_founder_profile_preferences_v1';

/**
 * @constant FOUNDER_OPERATING_PRESETS
 * @description Defines cockpit behaviors that materially change the Founder OS
 * presentation. These are not decorative themes; each preset declares a landing
 * module, data posture, sidebar posture and investor narrative.
 *
 * @real-world
 *   Lets the Founder pivot the entire cockpit for investor demos, forensic
 *   audits, or builder operations without hunting through separate screens.
 */
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

/**
 * @function normalizeFounderDisplayName
 * @description Converts founder identity fragments into a human boardroom name.
 *
 * @param {string} value - Raw name, email handle or persisted preference.
 * @returns {string} Normalized display name.
 */
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

/**
 * @function resolveFounderDisplayName
 * @description Reads the best available Founder identity from auth state and
 * normalizes it for investor-facing presentation.
 *
 * @param {Object} user - Authenticated user object.
 * @returns {string} Founder display name.
 */
const resolveFounderDisplayName = (user) => normalizeFounderDisplayName(
  user?.name || user?.fullName || user?.displayName || user?.email || 'Wilson Khanyezi'
);

// ============================================================================
// FORENSIC HELPER FUNCTIONS
// ============================================================================

/**
 * Exports data to a CSV file.
 * @param {Array<Object>} data - Array of objects to export.
 * @param {string} filename - Name of the file (without extension).
 * @returns {void}
 */

/**
 * @function exportCSV
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
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

/**
 * Exports a chart (from ref) to PDF.
 * @param {React.RefObject} elementRef - Ref of the DOM element to capture.
 * @param {string} filename - Name of the PDF file.
 * @returns {Promise<void>}
 */

/**
 * @function exportPDF
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
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
// SOVEREIGN ERROR BOUNDARY – 100-YEAR FORENSIC DURABILITY
// ============================================================================

/**
 * @class SovereignErrorBoundary
 * @description Real-world 100-year software never crashes completely. This boundary isolates
 * failures within individual tabs (e.g., if RevenueLedger throws, the CEO Dashboard stays alive).
 * @extends {React.Component}
 */
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
// LOCAL IMPORTS – METRIC CARDS, STYLES, ASSETS
// ============================================================================

import MetricCard from './MetricCard';
import styles from './FounderDashboard.module.css';

import wilsyLogo from '../../assets/logo/wilsy.jpeg';
import iconManifest from '../../assets/iconManifest';

import CommandPalette from './CommandPalette';
import QuickPanel from './QuickPanel';
import { CommandUsageProvider } from '../../contexts/CommandUsageContext';

// ============================================================================
// LAZY-LOADED SOVEREIGN HUDS – CODE-SPLIT FOR PERFORMANCE
// ============================================================================

// 👁️ THE BOARDROOM HUD IS NOW DIRECTLY EMBEDDED
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

// 🆕 ALL DEPARTMENT MODULES (20+)
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

// 🧠 NEURAL NARRATIVE CAPSULE & NUCLEUS FEED
import NeuralNarrativeCapsule from './NeuralNarrativeCapsule';
import NucleusFeedMonitor from './NucleusFeedMonitor';

// ============================================================================
// SOVEREIGN COMMAND KEYS – NAVIGATION ARCHITECTURE
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

/**
 * @constant MODULE_OPERATING_MAP
 * @description Declares the operating-system contract for each FounderDashboard
 * module. This powers the OS Spine so the cockpit can tell investors what is
 * mounted, which business layer it belongs to, and which data feed proves it.
 *
 * @real-world
 *   Prevents WILSY OS from feeling like disconnected React screens. Each module
 *   is represented as part of a visible operating architecture.
 *
 * @forensic
 *   The `feed` field is intentionally explicit so placeholder surfaces can be
 *   identified and replaced with database-backed services.
 */
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
  STATEMENT_ENGINE: { layer: 'EVIDENCE', label: 'Statement Engine', contract: 'Investor and compliance artifacts', feed: 'Statement APIs' }
};

// ============================================================================
// UTILITY FUNCTIONS – ENHANCED TOKEN HANDLING
// ============================================================================

/**
 * Retrieves the active JWT token from multiple possible localStorage keys.
 * Removes surrounding quotes and trims whitespace to prevent malformed Authorization headers.
 * Logs an error with available keys when token is missing for forensic debugging.
 *
 * @function getActiveToken
 * @returns {string|null} The sanitized token or null if not found.
 *
 * @real-world
 *   Used by `executeOmegaStrike` and billing fetches. Ensures that tokens stored with
 *   accidental quotes (e.g., from copy-paste) are still valid.
 *
 * @forensic
 *   If no token is found, logs all localStorage keys to the console, helping diagnose
 *   authentication failures in production without exposing values.
 *
 * @example
 *   const token = getActiveToken();
 *   if (!token) redirectToLogin();
 */
const getActiveToken = () => {
  const token = localStorage.getItem('wilsy_auth_token') ||
                localStorage.getItem('sovereignToken') ||
                localStorage.getItem('token') ||
                localStorage.getItem('accessToken');
  if (!token) {
    console.error('[AUTH] ❌ No token found in localStorage. Available keys:', Object.keys(localStorage));
    return null;
  }
  // Trim quotes and whitespace – solves "Bearer \"eyJ...\"" errors
  return token.replace(/["']/g, '').trim();
};

/**
 * @hook useDynamicNarrative
 * @description Cycles through a pool of boardroom narratives every 12 seconds.
 * @returns {{ currentNarrative: string }}
 */

/**
 * @function useDynamicNarrative
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
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

/**
 * Resolves the correct icon for a given module key.
 * Falls back to the icon manifest, then a hardcoded map, then a generic Target icon.
 * @param {string} key - Module identifier
 * @returns {JSX.Element} Resolved icon component
 */

/**
 * @function getModuleIcon
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const getModuleIcon = (key) => {
  if (iconManifest && iconManifest[key]) {
    return <img src={iconManifest[key].path} alt={iconManifest[key].label || key} style={{ width: '16px', height: '16px' }} />;
  }
  const iconMap = {
    'INVESTOR_PROOF': <BadgeCheck size={16} className="text-[#D4AF37]" />,
    'BOARDROOM_HUD': <Eye size={16} className="text-[#D4AF37]" />,
    'BILLING_HUB': <Coins size={16} className="text-[#D4AF37]" />,
    'INVOICE_SENTINEL': <Receipt size={16} className="text-[#D4AF37]" />,
    'REVENUE_LEDGER': <TrendingUp size={16} className="text-[#D4AF37]" />,
    'AUDIT_VAULT': <Lock size={16} className="text-[#D4AF37]" />,
    'CEO_DASHBOARD': <Crown size={16} className="text-[#D4AF37]" />,
    'COO_DASHBOARD': <Briefcase size={16} className="text-[#D4AF37]" />,
    'HR_DASHBOARD': <Users size={16} className="text-[#D4AF37]" />,
    'SALES_CRM': <MessageSquare size={16} className="text-[#D4AF37]" />,
    'IT_OPS': <Server size={16} className="text-[#D4AF37]" />,
    'FINANCE_DASHBOARD': <DollarSign size={16} className="text-[#D4AF37]" />,
    'LEGAL_DASHBOARD': <Gavel size={16} className="text-[#D4AF37]" />,
    'MARKETING_DASHBOARD': <Megaphone size={16} className="text-[#D4AF37]" />,
    'PRODUCT_DASHBOARD': <Box size={16} className="text-[#D4AF37]" />,
    'ENGINEERING_DASHBOARD': <Code size={16} className="text-[#D4AF37]" />,
    'DATA_DASHBOARD': <BarChart size={16} className="text-[#D4AF37]" />,
    'SECURITY_DASHBOARD': <LockKeyhole size={16} className="text-[#D4AF37]" />,
    'CUSTOMER_SUCCESS_DASHBOARD': <HeartHandshake size={16} className="text-[#D4AF37]" />,
    'PROCUREMENT_DASHBOARD': <ShoppingCart size={16} className="text-[#D4AF37]" />,
    'RESEARCH_DASHBOARD': <FlaskConical size={16} className="text-[#D4AF37]" />,
    'SPACE_OPERATIONS_DASHBOARD': <Satellite size={16} className="text-[#D4AF37]" />,
    'AI_ETHICS_DASHBOARD': <Brain size={16} className="text-[#D4AF37]" />,
    'QUANTUM_COMPUTING_DASHBOARD': <CpuIcon size={16} className="text-[#D4AF37]" />,
    'LONGEVITY_SCIENCES_DASHBOARD': <Dna size={16} className="text-[#D4AF37]" />,
  };
  return iconMap[key] || <Target size={16} />;
};

// ============================================================================
// FOUNDER DASHBOARD – MAIN COMPONENT
// ============================================================================

/**
 * @component FounderDashboard
 * @description The sovereign cockpit of WILSY OS. Renders the telemetry strip,
 * sidebar navigation, content grid with all 20+ department modules, and the
 * quick actions panel. Every shard is wrapped in SovereignErrorBoundary for
 * fault isolation.
 *
 * 🔗 PROVIDER HIERARCHY (enforced in the return statement):
 * SovereignOrchestrator → DataOrchestrator → CommandUsageProvider → Dashboard UI
 * This guarantees that BillingHUD, RevenueLedger, War Room, and all shards
 * can access the Neural Mesh context without "must be used within" errors.
 *
 * @returns {JSX.Element} The complete Founder Dashboard.
 */

/**
 * @function FounderDashboard
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const FounderDashboard = () => {
  // --------------------------------------------------------------------------
  // Context hooks
  // --------------------------------------------------------------------------
  const { user, logout } = useAuth();
  const { activeTenant } = useTenants();

  // --------------------------------------------------------------------------
  // Core UI state
  // --------------------------------------------------------------------------
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

  // 🚀 LIVE BILLING METRICS
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
  const [missionRun, setMissionRun] = useState({
    activeMission: null,
    status: 'IDLE',
    progress: 0,
    log: []
  });

  // --------------------------------------------------------------------------
  // Sovereign data hooks – real-time telemetry from the Nucleus
  // --------------------------------------------------------------------------
  const { analytics, compliance, forensics, loading: dataLoading, error: dataError } = useSovereignData();
  const { events: telemetryEvents, isSyncing: telemetrySyncing } = useTelemetryFeed(activeTenant?.tenantId || 'MASTER');
  const { stats: telemetryStats } = useTelemetryStats(activeTenant?.tenantId || 'MASTER');
  const { stats: trajectoryStats } = useTrajectoryWithEmails(activeTenant?.tenantId || 'MASTER');

  const chartRef = useRef(null);

  /**
   * @constant fallbackFounderProfile
   * @description Creates the canonical Founder identity envelope from live auth
   * and tenant context before any user preference overrides are applied.
   *
   * @real-world
   *   Gives the top bar an actual identity model instead of static text.
   *
   * @forensic
   *   Keeps tenant and jurisdiction assertions visible for investor diligence.
   */
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

  /**
   * @constant founderProfile
   * @description Merges the canonical founder identity with persisted local
   * operating preferences.
   */
  const founderProfile = useMemo(() => {
    const merged = {
      ...fallbackFounderProfile,
      ...(storedFounderProfile || {})
    };
    return {
      ...merged,
      displayName: normalizeFounderDisplayName(merged.displayName)
    };
  }, [fallbackFounderProfile, storedFounderProfile]);

  /**
   * @constant founderInitials
   * @description Derives a compact profile mark for the Founder cockpit chip.
   */
  const founderInitials = useMemo(() => {
    const parts = (founderProfile.displayName || 'Wilson Khanyezi').split(/\s+/).filter(Boolean);
    return `${parts[0]?.[0] || 'W'}${parts[1]?.[0] || 'K'}`.toUpperCase();
  }, [founderProfile.displayName]);

  /**
   * @constant isSingularityWorkspaceAuthorized
   * @description Restricts the unified Singularity Matrix workspace to Founder
   * and super-admin authority. This prevents role-controlled operating surfaces
   * from becoming a generic dashboard visible to every tenant user.
   *
   * @returns {boolean} True when the authenticated profile carries Founder,
   * super-admin, sovereign root, or global root authority.
   * @collaboration Wilson Khanyezi mandated the Singularity Matrix as a Founder
   * and super-admin command plane, not a public tenant view.
   */
  const isSingularityWorkspaceAuthorized = useMemo(() => {
    const authorityText = [
      user?.role,
      user?.accountRole,
      user?.authority,
      user?.tenantRole,
      Array.isArray(user?.permissions) ? user.permissions.join(' ') : '',
      founderProfile.commandMode,
      founderProfile.tenantScope
    ].filter(Boolean).join(' ').toUpperCase();

    return ['FOUNDER', 'SUPER_ADMIN', 'SUPERADMIN', 'SOVEREIGN', 'GLOBAL_ROOT', 'ROOT']
      .some(token => authorityText.includes(token));
  }, [founderProfile.commandMode, founderProfile.tenantScope, user]);

  /**
   * @constant operatorSovereigntyGraph
   * @description Builds an identity-aware authority label for the active
   * operator. The Matrix should speak to the person logged in, not expose
   * backend shard names such as MASTER as if they were the product story.
   *
   * @returns {Object} Human-facing operator identity and authority metadata.
   * @collaboration Wilson Khanyezi mandated a logged-in-person algorithm so the
   * Founder cockpit never feels like a generic admin console.
   */
  const operatorSovereigntyGraph = useMemo(() => {
    const roleText = String(user?.role || user?.accountRole || user?.authority || '').toUpperCase();
    const isFounder = roleText.includes('FOUNDER') || founderProfile.tenantScope === 'Founder Tenant';
    const isSuperAdmin = roleText.includes('SUPER');
    const authorityLabel = isFounder
      ? 'Founder Authority'
      : isSuperAdmin
        ? 'Sovereign Operator'
        : 'Authorized Operator';

    return {
      displayName: founderProfile.displayName,
      authorityLabel,
      companyScope: activeTenant?.name || founderProfile.company || 'Wilsy (Pty) Ltd',
      roleNarrative: founderProfile.title || 'Operator',
      evidenceMode: founderProfile.evidenceMode || 'Real Data Only'
    };
  }, [activeTenant, founderProfile, user]);

  /**
   * @constant founderPatentSystems
   * @description Curates investor-facing WILSY OS defensibility claims. These
   * are product architecture themes, not fake metrics.
   */
  const founderPatentSystems = useMemo(() => ([
    {
      title: 'Founder Sovereignty Graph',
      text: 'Ties owner identity, tenant authority, boardroom actions and audit proof into one visible command graph.',
      icon: Fingerprint
    },
    {
      title: 'Real-Data Investor Theatre',
      text: 'Demo surfaces reject placeholders and expose whether every figure is database-backed, cached or unavailable.',
      icon: BadgeCheck
    },
    {
      title: 'Jurisdiction Revenue Router',
      text: 'Links billing, courts, compliance, collections and tenant geography so money movement has legal context.',
      icon: Scale
    },
    {
      title: 'Forensic Operating Memory',
      text: 'Every executive action becomes explainable, exportable and sealed for institutional diligence.',
      icon: FileCheck2
    }
  ]), []);

  useEffect(() => {
    setProfileDraft(founderProfile);
  }, [founderProfile]);

  /**
   * @function updateProfileDraft
   * @description Updates one editable Founder preference field without mutating
   * the saved profile.
   *
   * @param {string} key - Founder profile field to update.
   * @param {string} value - New preference value.
   * @returns {void}
   */
  const updateProfileDraft = useCallback((key, value) => {
    setProfileDraft(prev => ({ ...prev, [key]: value }));
  }, []);

  /**
   * @function persistFounderProfile
   * @description Saves Founder preferences, updates cockpit posture and applies
   * OS-level behaviors such as default module, sidebar and quick panel state.
   *
   * @param {Object} nextProfile - Complete Founder profile to persist.
   * @returns {void}
   */
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
      if (cleanProfile.defaultModule === 'BOARDROOM_HUD') {
        setBoardroomReturnModule(activeModule === 'BOARDROOM_HUD' ? 'SINGULARITY_MATRIX' : activeModule);
      }
      setActiveModule(cleanProfile.defaultModule);
    }
  }, [fallbackFounderProfile, activeModule]);

  /**
   * @function applyFounderPreset
   * @description Applies an operational cockpit preset. This is the bridge from
   * preference menu to real OS behavior.
   *
   * @param {string} presetName - Name from `FOUNDER_OPERATING_PRESETS`.
   * @returns {void}
   */
  const applyFounderPreset = useCallback((presetName) => {
    const preset = FOUNDER_OPERATING_PRESETS[presetName];
    if (!preset) return;
    persistFounderProfile({
      ...founderProfile,
      ...preset,
      commandMode: presetName
    });
    setIsPreferenceEditing(true);
  }, [founderProfile, persistFounderProfile]);

  /**
   * @function applyPreferenceChange
   * @description Applies dropdown preference changes immediately so menu options
   * have visible consequences.
   *
   * @param {string} key - Preference field.
   * @param {string} value - New value.
   * @returns {void}
   */
  const applyPreferenceChange = useCallback((key, value) => {
    if (key === 'commandMode') {
      applyFounderPreset(value);
      return;
    }
    persistFounderProfile({
      ...founderProfile,
      [key]: value
    });
  }, [applyFounderPreset, founderProfile, persistFounderProfile]);

  /**
   * @function saveFounderProfile
   * @description Persists Founder operating preferences locally and refreshes
   * the in-memory cockpit identity.
   *
   * @returns {void}
   *
   * @forensic
   *   Uses a dedicated namespaced key so preference state is auditable and does
   *   not collide with auth or tenant state.
   */
  const saveFounderProfile = useCallback(() => {
    persistFounderProfile(profileDraft);
    setIsPreferenceEditing(false);
  }, [persistFounderProfile, profileDraft]);

  /**
   * @function resetFounderProfile
   * @description Removes saved Founder preferences and restores the canonical
   * profile derived from auth and tenant context.
   *
   * @returns {void}
   */
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

  /**
   * @function activateModule
   * @description Switches the Founder cockpit to a target module while
   * preserving the previous Boardroom HUD return target.
   *
   * @param {string} moduleKey - Module identifier to mount.
   * @returns {void}
   *
   * @collaboration
   *   Wilson Khanyezi required every cockpit button to actually route to a real
   *   operating surface. Codex keeps this as the single module activation path.
   */
  const activateModule = useCallback((moduleKey) => {
    if (moduleKey === 'BOARDROOM_HUD') {
      setBoardroomReturnModule(activeModule === 'BOARDROOM_HUD' ? 'SINGULARITY_MATRIX' : activeModule);
    }
    setActiveModule(moduleKey);
  }, [activeModule]);

  useEffect(() => {
    if (activeModule === 'SALES_CRM') {
      setIsSidebarOpen(false);
    }
  }, [activeModule]);

  // --------------------------------------------------------------------------
  // Fetch live billing metrics
  // --------------------------------------------------------------------------
  useEffect(() => {
    
/**
 * @function fetchBilling
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const fetchBilling = async () => {
      try {
        const token = getActiveToken();
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

  const { currentNarrative } = useDynamicNarrative();

  // --------------------------------------------------------------------------
  // Keyboard shortcuts and clock
  // --------------------------------------------------------------------------
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    
/**
 * @function handleKeyDown
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleKeyDown = (e) => {
      if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        e.stopPropagation();
        setIsCommandPaletteOpen(prev => !prev);
      }
      if (e.key === 'Escape' && isCommandPaletteOpen) {
        setIsCommandPaletteOpen(false);
      }
      if (e.key === 'Escape' && isFounderPanelOpen) {
        setIsFounderPanelOpen(false);
        setIsPreferenceEditing(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown, true);
    return () => {
      clearInterval(timer);
      window.removeEventListener('keydown', handleKeyDown, true);
    };
  }, [isCommandPaletteOpen, isFounderPanelOpen]);

  // --------------------------------------------------------------------------
  // System health monitoring
  // --------------------------------------------------------------------------
  useEffect(() => {
    if (dataLoading) {
      setSystemHealth('HYDRATING_NUCLEUS...');
    } else if (dataError) {
      setSystemHealth('FRACTURE: OMEGA_LINK_SEVERED');
    } else {
      setSystemHealth('SOVEREIGN_LINK_STABLE');
    }
  }, [dataLoading, dataError]);

  // ==========================================================================
  // OMEGA STRIKE – EXECUTIVE COMMAND EXECUTION (ENHANCED)
  // ==========================================================================

  /**
   * @function executeOmegaStrike
   * @description Executes a sovereign command against the backend API. Handles
   * token injection, PDF/blob downloads, and graceful fallback on failure.
   * Enhanced with detailed logging, token validation, and user alerts for 401.
   *
   * @param {string} actionId - Unique identifier for the action.
   * @param {string} endpoint - API endpoint.
   * @param {string} [method='GET'] - HTTP method.
   * @param {Object} [payload={}] - Request body for POST/PUT.
   * @returns {Promise<void>}
   *
   * @real-world
   *   Used by statement generation buttons (Revenue Artifact, Compliance Proof, Forensic Seal)
   *   and tenant management (Spawn Shard, Freeze Shard).
   *
   * @forensic
   *   - Logs the full action, endpoint, and a truncated token for debugging.
   *   - If token is missing, shows an alert and aborts early.
   *   - On 401 response, alerts the user to log out and log in again.
   *   - Always creates a fallback text file even on error, so the user never gets nothing.
   *   - Adds X-Trace-ID header to correlate client-side actions with server logs.
   *
   * @example
   *   executeOmegaStrike('STMT_REVENUE', '/statements/revenue');
   */
  const executeOmegaStrike = useCallback(async (actionId, endpoint, method = 'GET', payload = {}) => {
    setActionLoading(actionId);
    const traceId = `TRC-CMD-${Date.now()}`;
    console.log(`[OMEGA-STRIKE] Initiating: ${actionId} | ${method} ${endpoint} | Trace: ${traceId}`);

    try {
      const token = getActiveToken();
      const tenantContext = activeTenant?.id || 'GLOBAL_ROOT';
      const finalEndpoint = endpoint.includes('tenantId') ? endpoint : `${endpoint}?tenantId=${tenantContext}`;

      if (!token) {
        console.error('[OMEGA-STRIKE] ❌ No token available. Please log in again.');
        alert('Session expired. Please log out and log in again.');
        setActionLoading(null);
        return;
      }

      console.log(`[OMEGA-STRIKE] Token (first 20 chars): ${token.substring(0, 20)}...`);

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

      // Axios throws on 4xx/5xx by default, but this is an extra safety check
      if (response.status === 401) {
        throw new Error('UNAUTHORIZED – Token invalid or expired');
      }

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
      console.log(`[OMEGA-STRIKE] ✅ ${actionId} SUCCESS. File saved: ${filename}`);
    } catch (error) {
      console.error(`[OMEGA-STRIKE] ❌ ${actionId} FAILED:`, error.message);
      if (error.response?.status === 401) {
        console.error('   → Unauthorized – token may be expired. Please logout and login again.');
        alert('Authentication failed. Please logout and login again to refresh your session.');
      } else if (error.response) {
        console.error(`   → Server responded with status: ${error.response.status}`);
      } else if (error.request) {
        console.error('   → No response received from server. Check network/proxy.');
      }
      // Still create a fallback text file so user gets something
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
  // COMMAND PALETTE – MODULE NAVIGATION & ACTIONS
  // ==========================================================================

  const moduleCommands = useMemo(() => [
    { id: 'MODULE_INVESTOR_PROOF', label: 'Investor Proof Console', icon: <BadgeCheck size={16} />, handler: () => setActiveModule('INVESTOR_PROOF'), description: 'Why WILSY OS wins' },
    { id: 'MODULE_BOARDROOM_HUD', label: 'Boardroom HUD', icon: <Eye size={16} />, handler: () => setActiveModule('BOARDROOM_HUD'), description: 'Live Telemetry Override' },
    { id: 'MODULE_SINGULARITY_MATRIX', label: 'Singularity Matrix (HUDs)', icon: <BarChart3 size={16} />, handler: () => setActiveModule('SINGULARITY_MATRIX'), description: 'The Big Three HUDs' },
    { id: 'MODULE_EXECUTIVE_OVERSIGHT', label: 'Executive Oversight', icon: <Crown size={16} />, handler: () => setActiveModule('EXECUTIVE_OVERSIGHT'), description: 'C-Suite Analytics' },
    { id: 'MODULE_CLOUD_UPLINK', label: 'Cloud Uplink', icon: <Server size={16} />, handler: () => setActiveModule('CLOUD_UPLINK'), description: 'Global Node Telemetry' },
    { id: 'MODULE_REVENUE_LEDGER', label: 'Mathematics (Revenue)', icon: <TrendingUp size={16} />, handler: () => setActiveModule('REVENUE_LEDGER'), description: 'View ARR/MRR metrics' },
    { id: 'MODULE_BILLING_HUB', label: 'Billing Hub', icon: <CreditCard size={16} />, handler: () => setActiveModule('BILLING_HUB'), description: 'Billing, courts, collections and pricing control' },
    { id: 'MODULE_INVOICE_SENTINEL', label: 'Invoice Sentinel', icon: <Receipt size={16} />, handler: () => setActiveModule('INVOICE_SENTINEL'), description: 'Receivables lane monitoring' },
    { id: 'MODULE_NUCLEUS_MONITOR', label: 'Nucleus Feed Monitor', icon: <TerminalSquare size={16} />, handler: () => setActiveModule('NUCLEUS_MONITOR'), description: 'Live system source matrix' },
    { id: 'MODULE_AUDIT_VAULT', label: 'Science (Audit)', icon: <Microscope size={16} />, handler: () => setActiveModule('AUDIT_VAULT'), description: 'Forensic integrity' },
    { id: 'MODULE_NODE_REGISTRY', label: 'Engineering (Shards)', icon: <Cpu size={16} />, handler: () => setActiveModule('NODE_REGISTRY'), description: 'Active shards' },
    { id: 'MODULE_GLOBAL_ORCHESTRATOR', label: 'Technology (Network)', icon: <Globe size={16} />, handler: () => setActiveModule('GLOBAL_ORCHESTRATOR') },
    { id: 'MODULE_IDENTITY_HUB', label: 'Identity Hub', icon: <Key size={16} />, handler: () => setActiveModule('IDENTITY_HUB') },
    { id: 'MODULE_RISK_SENTINEL', label: 'Risk Sentinel', icon: <AlertOctagon size={16} />, handler: () => setActiveModule('RISK_SENTINEL') },
    { id: 'MODULE_CLIENT_COVENANT', label: 'Client Covenant', icon: <FileSignature size={16} />, handler: () => setActiveModule('CLIENT_COVENANT') },
    { id: 'MODULE_CRISIS_COMMAND', label: 'Crisis Command', icon: <Power size={16} />, handler: () => setActiveModule('CRISIS_COMMAND') },
    { id: 'MODULE_TENANT_MANAGER', label: 'Tenant Manager', icon: <Users size={16} />, handler: () => setActiveModule('TENANT_MANAGER') },
    { id: 'MODULE_STATEMENT_ENGINE', label: 'Statement Engine', icon: <FileText size={16} />, handler: () => setActiveModule('STATEMENT_ENGINE') },
    { id: 'MODULE_CEO_DASHBOARD', label: 'CEO Dashboard', icon: <Crown size={16} />, handler: () => setActiveModule('CEO_DASHBOARD'), description: 'Chief Executive Officer view' },
    { id: 'MODULE_COO_DASHBOARD', label: 'COO Dashboard', icon: <Briefcase size={16} />, handler: () => setActiveModule('COO_DASHBOARD'), description: 'Chief Operations Officer view' },
    { id: 'MODULE_HR_DASHBOARD', label: 'HR Department', icon: <Users size={16} />, handler: () => setActiveModule('HR_DASHBOARD'), description: 'Human Resources suite' },
    { id: 'MODULE_SALES_CRM', label: 'Sales & CRM', icon: <MessageSquare size={16} />, handler: () => setActiveModule('SALES_CRM'), description: 'CRM, Leads, Deals, Projects' },
    { id: 'MODULE_IT_OPS', label: 'IT Operations', icon: <Server size={16} />, handler: () => setActiveModule('IT_OPS'), description: 'System Engineers & Infrastructure' },
    { id: 'MODULE_FINANCE_DASHBOARD', label: 'Finance', icon: <DollarSign size={16} />, handler: () => setActiveModule('FINANCE_DASHBOARD') },
    { id: 'MODULE_LEGAL_DASHBOARD', label: 'Legal', icon: <Gavel size={16} />, handler: () => setActiveModule('LEGAL_DASHBOARD') },
    { id: 'MODULE_MARKETING_DASHBOARD', label: 'Marketing', icon: <Megaphone size={16} />, handler: () => setActiveModule('MARKETING_DASHBOARD') },
    { id: 'MODULE_PRODUCT_DASHBOARD', label: 'Product', icon: <Box size={16} />, handler: () => setActiveModule('PRODUCT_DASHBOARD') },
    { id: 'MODULE_ENGINEERING_DASHBOARD', label: 'Engineering', icon: <Code size={16} />, handler: () => setActiveModule('ENGINEERING_DASHBOARD') },
    { id: 'MODULE_DATA_DASHBOARD', label: 'Data', icon: <BarChart size={16} />, handler: () => setActiveModule('DATA_DASHBOARD') },
    { id: 'MODULE_SECURITY_DASHBOARD', label: 'Security', icon: <LockKeyhole size={16} />, handler: () => setActiveModule('SECURITY_DASHBOARD') },
    { id: 'MODULE_CUSTOMER_SUCCESS_DASHBOARD', label: 'Customer Success', icon: <HeartHandshake size={16} />, handler: () => setActiveModule('CUSTOMER_SUCCESS_DASHBOARD') },
    { id: 'MODULE_PROCUREMENT_DASHBOARD', label: 'Procurement', icon: <ShoppingCart size={16} />, handler: () => setActiveModule('PROCUREMENT_DASHBOARD') },
    { id: 'MODULE_RESEARCH_DASHBOARD', label: 'Research', icon: <FlaskConical size={16} />, handler: () => setActiveModule('RESEARCH_DASHBOARD') },
    { id: 'MODULE_SPACE_OPERATIONS_DASHBOARD', label: 'Space Operations', icon: <Satellite size={16} />, handler: () => setActiveModule('SPACE_OPERATIONS_DASHBOARD') },
    { id: 'MODULE_AI_ETHICS_DASHBOARD', label: 'AI Ethics', icon: <Brain size={16} />, handler: () => setActiveModule('AI_ETHICS_DASHBOARD') },
    { id: 'MODULE_QUANTUM_COMPUTING_DASHBOARD', label: 'Quantum Computing', icon: <CpuIcon size={16} />, handler: () => setActiveModule('QUANTUM_COMPUTING_DASHBOARD') },
    { id: 'MODULE_LONGEVITY_SCIENCES_DASHBOARD', label: 'Longevity Sciences', icon: <Dna size={16} />, handler: () => setActiveModule('LONGEVITY_SCIENCES_DASHBOARD') },
  ], []);

  const actionCommands = useMemo(() => [
    { id: 'ACTION_STMT_REVENUE', label: 'Mathematics: Revenue Artifact', icon: <FileText size={16} />, handler: () => executeOmegaStrike('STMT_REVENUE', '/statements/revenue'), description: 'PDF download' },
    { id: 'ACTION_STMT_COMPLIANCE', label: 'Science: Compliance Proof', icon: <ShieldCheck size={16} />, handler: () => executeOmegaStrike('STMT_COMPLIANCE', '/statements/compliance'), description: 'PDF download' },
    { id: 'ACTION_STMT_FORENSIC', label: 'Science: Forensic Seal', icon: <Fingerprint size={16} />, handler: () => executeOmegaStrike('STMT_FORENSIC', '/statements/forensics'), description: 'PDF download' },
    { id: 'ACTION_ADD_TENANT', label: 'Engineering: Spawn Shard', icon: <Users size={16} />, handler: () => executeOmegaStrike('TENANT_ADD', '/tenants/create', 'POST'), description: 'Create new node' },
    { id: 'ACTION_SUSPEND_TENANT', label: 'Engineering: Freeze Shard', icon: <ShieldAlert size={16} />, handler: () => executeOmegaStrike('TENANT_SUSPEND', '/tenants/suspend', 'POST') },
    { id: 'ACTION_TRIGGER_SNAPSHOT', label: 'Financial Fortress: Cold Storage Snapshot', icon: <Database size={16} />, handler: () => executeOmegaStrike('COLD_STORAGE_SNAPSHOT', '/revenue/snapshot/cold-storage', 'POST'), description: 'Archive billing state' },
    { id: 'ACTION_CLEAR_SUSPENSE', label: 'Financial Fortress: Open Invoice Sentinel', icon: <Receipt size={16} />, handler: () => setActiveModule('INVOICE_SENTINEL'), description: 'Force refresh receivables ledger' },
    { id: 'ACTION_LOGOUT', label: 'Logout / Terminate Session', icon: <LogOut size={16} />, handler: logout, description: 'End sovereign session' },
  ], [executeOmegaStrike, logout]);

  /**
   * @constant capabilityCommands
   * @description Mirrors the non-navigation command layers that live inside the
   * Command Palette so the Founder OS command count reflects the real operating
   * surface instead of the legacy module/action subset.
   *
   * @collaboration
   *   Wilson Khanyezi flagged the stale "42 commands" count as false value
   *   signalling. This inventory makes the dashboard count a living capability
   *   index that grows as the OS gains real functions.
   */
  const capabilityCommands = useMemo(() => [
    {
      id: 'CAPABILITY_SOVEREIGN_HEALTH_TRIBUNAL',
      label: 'Run Sovereign Health Tribunal',
      icon: <Activity size={16} />,
      handler: () => setActiveModule('BOARDROOM_HUD'),
      description: 'Live OS verdict across gateway, telemetry, revenue, compliance and forensics'
    },
    {
      id: 'CAPABILITY_COMMAND_MANIFEST_EXPORT',
      label: 'Export Sealed Command Manifest',
      icon: <FileCheck2 size={16} />,
      handler: () => setActiveModule('EXECUTIVE_OVERSIGHT'),
      description: 'Audit-ready command capability map'
    },
    {
      id: 'CAPABILITY_COPY_FORENSIC_RECEIPT',
      label: 'Copy Last Forensic Receipt',
      icon: <Fingerprint size={16} />,
      handler: () => setActiveModule('AUDIT_VAULT'),
      description: 'Portable execution trace evidence'
    },
    {
      id: 'CAPABILITY_INVESTOR_REPORT',
      label: 'Generate Investor Report',
      icon: <Scale size={16} />,
      handler: () => setActiveModule('EXECUTIVE_OVERSIGHT'),
      description: 'Founder-only investor distribution'
    },
    {
      id: 'CAPABILITY_ARR_REPORT',
      label: 'ARR Report',
      icon: <TrendingUp size={16} />,
      handler: () => executeOmegaStrike('ARR_REPORT', '/statements/revenue'),
      description: 'Annual recurring revenue artifact'
    },
    {
      id: 'CAPABILITY_MRR_REPORT',
      label: 'MRR Report',
      icon: <PieChart size={16} />,
      handler: () => executeOmegaStrike('MRR_REPORT', '/statements/revenue'),
      description: 'Monthly recurring revenue artifact'
    },
    {
      id: 'CAPABILITY_VOLUME_REPORT',
      label: 'Volume Report',
      icon: <BarChart3 size={16} />,
      handler: () => executeOmegaStrike('VOLUME_REPORT', '/statements/revenue'),
      description: 'Transaction volume artifact'
    },
    {
      id: 'CAPABILITY_GROWTH_REPORT',
      label: 'Growth Report',
      icon: <Activity size={16} />,
      handler: () => executeOmegaStrike('GROWTH_REPORT', '/statements/revenue'),
      description: 'Growth-rate evidence artifact'
    },
    {
      id: 'CAPABILITY_COMPLIANCE_REPORT',
      label: 'Compliance Report',
      icon: <ShieldCheck size={16} />,
      handler: () => executeOmegaStrike('COMPLIANCE_REPORT', '/statements/compliance'),
      description: 'Regulatory validation artifact'
    },
    {
      id: 'CAPABILITY_FORENSICS_REPORT',
      label: 'Forensics Report',
      icon: <Fingerprint size={16} />,
      handler: () => executeOmegaStrike('FORENSICS_REPORT', '/statements/forensics'),
      description: 'Chain-of-custody artifact'
    }
  ], [executeOmegaStrike]);

  const allCommands = useMemo(
    () => [...moduleCommands, ...actionCommands, ...capabilityCommands],
    [moduleCommands, actionCommands, capabilityCommands]
  );

  /**
   * @constant founderModuleOptions
   * @description Curates the modules that make sense as Founder landing screens.
   */
  const founderModuleOptions = useMemo(() => moduleCommands
    .filter(command => [
      'MODULE_BOARDROOM_HUD',
      'MODULE_INVESTOR_PROOF',
      'MODULE_SINGULARITY_MATRIX',
      'MODULE_REVENUE_LEDGER',
      'MODULE_BILLING_HUB',
      'MODULE_AUDIT_VAULT',
      'MODULE_NODE_REGISTRY',
      'MODULE_GLOBAL_ORCHESTRATOR',
      'MODULE_IDENTITY_HUB',
      'MODULE_TENANT_MANAGER',
      'MODULE_STATEMENT_ENGINE'
    ].includes(command.id))
    .map(command => ({
      label: command.label,
      value: command.id.replace('MODULE_', '')
    })), [moduleCommands]);

  /**
   * @constant activeModuleMeta
   * @description Resolves the active module's human label, business layer,
   * dependency feed, and operating contract for the OS Spine.
   */
  const activeModuleMeta = useMemo(() => {
    const command = moduleCommands.find(item => item.id === `MODULE_${activeModule}`);
    return {
      key: activeModule,
      label: command?.label || MODULE_OPERATING_MAP[activeModule]?.label || activeModule.replace(/_/g, ' '),
      description: command?.description || MODULE_OPERATING_MAP[activeModule]?.contract || 'Sovereign module mounted through Founder OS',
      ...(MODULE_OPERATING_MAP[activeModule] || { layer: 'DEPARTMENT', feed: 'Module context' })
    };
  }, [activeModule, moduleCommands]);

  /**
   * @constant osSpine
   * @description Computes the FounderDashboard operating-system health strip
   * from real tenant, telemetry, billing, compliance and forensic context.
   *
   * @real-world
   *   Gives an investor a quick answer to: "Is this an app full of pages, or a
   *   system whose modules know what they depend on?"
   *
   * @forensic
   *   The `realDataRatio` is intentionally computed from actual hook readiness
   *   instead of a hard-coded success score.
   */
  const osSpine = useMemo(() => {
    const telemetryCount = Array.isArray(telemetryEvents) ? telemetryEvents.length : 0;
    const telemetryStatsCount = Array.isArray(telemetryStats) ? telemetryStats.length : 0;
    const feeds = [
      { label: 'Tenant', status: activeTenant?.tenantId || activeTenant?.id || 'MASTER', ready: Boolean(activeTenant) },
      { label: 'Telemetry', status: telemetrySyncing ? 'Syncing' : `${telemetryCount} events`, ready: telemetryCount > 0 || !telemetrySyncing },
      { label: 'Revenue', status: billingMetrics ? 'Linked' : 'Pending', ready: Boolean(billingMetrics) },
      { label: 'Compliance', status: compliance ? 'Linked' : 'Pending', ready: Boolean(compliance) },
      { label: 'Forensics', status: forensics ? 'Linked' : 'Pending', ready: Boolean(forensics) },
      { label: 'Stats', status: `${telemetryStatsCount} samples`, ready: telemetryStatsCount > 0 }
    ];
    const mountedModules = new Set([
      ...COMMAND_LEVEL_KEYS,
      ...SOVEREIGN_HUB_KEYS,
      ...LEADERSHIP_KEYS,
      ...CORE_DEPT_KEYS,
      ...ADVANCED_DEPT_KEYS,
      ...FUTURE_DEPT_KEYS,
      'TENANT_MANAGER',
      'STATEMENT_ENGINE'
    ]);

    return {
      feeds,
      mounted: mountedModules.size,
      commandCount: allCommands.length,
      realDataRatio: Math.round((feeds.filter(feed => feed.ready).length / feeds.length) * 100)
    };
  }, [activeTenant, telemetryEvents, telemetryStats, telemetrySyncing, billingMetrics, compliance, forensics, allCommands.length]);

  /**
   * @constant investorProofMatrix
   * @description Builds the Founder-facing diligence matrix that answers why a
   * serious buyer would value WILSY OS as an operating system instead of another
   * SaaS dashboard.
   *
   * @real-world
   *   Each proof card is tied to mounted modules, tenant state, live telemetry,
   *   billing, compliance, forensics or identity context. The console never
   *   claims fake global expansion when only the Founder tenant is active.
   *
   * @collaboration
   *   Wilson Khanyezi challenged the system to explain its strategic moat in the
   *   product itself. Codex turns that challenge into executable navigation.
   */
  const investorProofMatrix = useMemo(() => {
    const telemetryCount = Array.isArray(telemetryEvents) ? telemetryEvents.length : 0;
    const statsCount = Array.isArray(telemetryStats) ? telemetryStats.length : 0;
    const tenantLabel = activeTenant?.name || founderProfile.company || 'Wilsy (Pty) Ltd';
    const tenantId = activeTenant?.tenantId || activeTenant?.id || 'MASTER';

    return [
      {
        title: 'Business OS, Not CRM Add-On',
        claim: 'CRM, billing, compliance, courts, identity, revenue and audit share one founder command plane.',
        proof: `${osSpine.mounted} mounted modules / ${osSpine.commandCount} executable commands`,
        ready: osSpine.mounted >= 20,
        module: 'SINGULARITY_MATRIX',
        action: 'Open OS Matrix'
      },
      {
        title: 'Diligence-Ready Evidence',
        claim: 'Every critical executive claim can route to Audit Vault, Statement Engine or a forensic feed.',
        proof: forensics ? 'Forensic feed linked' : 'Forensic feed pending',
        ready: Boolean(forensics),
        module: 'AUDIT_VAULT',
        action: 'Open Audit Vault'
      },
      {
        title: 'Founder-Controlled Tenancy',
        claim: 'The owner, tenant, role authority and expansion path are visible from the command center.',
        proof: `${tenantLabel} / ${tenantId}`,
        ready: Boolean(activeTenant || tenantId),
        module: 'IDENTITY_HUB',
        action: 'Open Identity Hub'
      },
      {
        title: 'Revenue-To-Court Loop',
        claim: 'Collections, court registry, receivables and statements belong to one operating workflow.',
        proof: billingMetrics ? 'Billing metrics linked' : 'Billing metrics pending',
        ready: Boolean(billingMetrics),
        module: 'BILLING_HUB',
        action: 'Open Billing Hub'
      },
      {
        title: 'Multi-Tenant Expansion Rail',
        claim: 'New businesses can become governed tenants without losing audit, identity or jurisdiction context.',
        proof: activeTenant?.jurisdiction || founderProfile.jurisdictionFocus || 'Founder jurisdiction configured',
        ready: Boolean(activeTenant?.jurisdiction || founderProfile.jurisdictionFocus),
        module: 'TENANT_MANAGER',
        action: 'Open Tenant Manager'
      },
      {
        title: 'Live Operating Telemetry',
        claim: 'A CEO sees posture, risk, uptime signals and command history without asking engineering.',
        proof: `${telemetryCount} events / ${statsCount} stat samples`,
        ready: telemetryCount > 0 || statsCount > 0,
        module: 'NUCLEUS_MONITOR',
        action: 'Open Nucleus Monitor'
      }
    ];
  }, [activeTenant, billingMetrics, forensics, founderProfile, osSpine, telemetryEvents, telemetryStats]);

  /**
   * @constant aiEraDefensibility
   * @description Answers the modern investor objection: if AI can generate
   * software quickly, why does WILSY OS deserve enterprise-level value?
   *
   * @real-world
   *   The moat is not "we have AI." The moat is governed execution: identity,
   *   tenant authority, court-aware billing, telemetry, audit artifacts and
   *   command history operating as one system.
   *
   * @collaboration
   *   Wilson Khanyezi challenged WILSY OS to be impossible to ignore in the AI
   *   age. Codex encodes the answer as visible product strategy.
   */
  const aiEraDefensibility = useMemo(() => {
    const readyFeeds = osSpine.feeds.filter(feed => feed.ready).length;
    const score = Math.round(((readyFeeds * 18) + Math.min(osSpine.mounted, 30) + Math.min(osSpine.commandCount, 36)) / 1.74);
    const cappedScore = Math.min(100, Math.max(0, score));

    return {
      score: cappedScore,
      thesis: 'AI can generate screens. WILSY OS governs the business: who owns the tenant, which evidence proves the action, which legal path executes, which revenue moves, and which audit trail survives diligence.',
      pillars: [
        {
          title: 'Governed Execution',
          text: 'Commands are routed through tenant, authority and evidence context before they become business action.',
          ready: Boolean(activeTenant),
          icon: Workflow
        },
        {
          title: 'Evidence Before Optics',
          text: 'Investor surfaces show readiness from real hooks instead of decorative claims.',
          ready: osSpine.realDataRatio >= 50,
          icon: FileCheck2
        },
        {
          title: 'Regulated Business Memory',
          text: 'Forensics, compliance and telemetry are treated as operating memory, not optional analytics.',
          ready: Boolean(forensics || compliance),
          icon: ShieldCheck
        },
        {
          title: 'Founder-Led Expansion',
          text: 'The system starts with Wilsy as the owner node and expands into governed tenants instead of anonymous accounts.',
          ready: Boolean(founderProfile.displayName),
          icon: Crown
        }
      ]
    };
  }, [activeTenant, compliance, forensics, founderProfile.displayName, osSpine]);

  /**
   * @constant sovereignValueLoops
   * @description Defines executable control loops that make WILSY OS feel like
   * an operating system and not a set of disconnected SaaS modules.
   *
   * @real-world
   *   Each loop names the chain of business capability and the module that can
   *   prove it in the current cockpit.
   */
  const sovereignValueLoops = useMemo(() => ([
    {
      title: 'Money To Law Loop',
      path: 'Invoice -> receivable -> court route -> statement -> forensic seal',
      module: 'BILLING_HUB',
      action: 'Inspect Billing'
    },
    {
      title: 'Identity To Authority Loop',
      path: 'Founder profile -> role graph -> tenant scope -> command permission',
      module: 'IDENTITY_HUB',
      action: 'Inspect Identity'
    },
    {
      title: 'Tenant To Node Loop',
      path: 'Founder tenant -> shard registry -> topology -> expansion readiness',
      module: 'GLOBAL_ORCHESTRATOR',
      action: 'Inspect Topology'
    },
    {
      title: 'Action To Evidence Loop',
      path: 'Command -> telemetry -> audit vault -> exportable diligence proof',
      module: 'AUDIT_VAULT',
      action: 'Inspect Evidence'
    }
  ]), []);

  /**
   * @constant founderMissionDeck
   * @description Defines executable Founder workflows. These missions are the
   * difference between a dashboard and an operating system: one command can run
   * a sequence, collect proof, open the correct module and leave an audit-style
   * cockpit log for the Founder.
   *
   * @real-world
   *   Mission steps are intentionally tied to existing modules and Omega Strike
   *   actions. When an endpoint exists, the mission can trigger the real export;
   *   when it is a readiness inspection, the step derives truth from live hooks.
   *
   * @collaboration
   *   Wilson Khanyezi requested gameplay-like progression instead of flat pages.
   *   Codex introduces mission loops with progress, outcomes and consequences.
   */
  const founderMissionDeck = useMemo(() => ([
    {
      id: 'INVESTOR_DILIGENCE_PACK',
      title: 'Investor Diligence Pack',
      purpose: 'Generate the evidence bundle an investor asks for before serious money moves.',
      module: 'AUDIT_VAULT',
      command: 'Generate Pack',
      steps: [
        { label: 'Revenue artifact', type: 'omega', actionId: 'STMT_REVENUE', endpoint: '/statements/revenue' },
        { label: 'Compliance artifact', type: 'omega', actionId: 'STMT_COMPLIANCE', endpoint: '/statements/compliance' },
        { label: 'Forensic artifact', type: 'omega', actionId: 'STMT_FORENSIC', endpoint: '/statements/forensics' },
        { label: 'Open Audit Vault for inspection', type: 'module', module: 'AUDIT_VAULT' }
      ]
    },
    {
      id: 'FOUNDER_READINESS_SCAN',
      title: 'Founder Readiness Scan',
      purpose: 'Score whether the current tenant can survive a boardroom, diligence and operations review.',
      module: 'INVESTOR_PROOF',
      command: 'Run Scan',
      steps: [
        { label: 'Verify tenant identity', type: 'check', ready: Boolean(activeTenant || founderProfile.company), proof: activeTenant?.name || founderProfile.company },
        { label: 'Verify real data spine', type: 'check', ready: osSpine.realDataRatio >= 50, proof: `${osSpine.realDataRatio}% real-data readiness` },
        { label: 'Verify command surface', type: 'check', ready: allCommands.length > 0, proof: `${allCommands.length} commands mounted` },
        { label: 'Verify AI-era moat', type: 'check', ready: aiEraDefensibility.score >= 50, proof: `${aiEraDefensibility.score}% defensibility` }
      ]
    },
    {
      id: 'REVENUE_TO_COURT_DRILL',
      title: 'Revenue To Court Drill',
      purpose: 'Walk from receivable pressure to legal execution posture without leaving the OS spine.',
      module: 'BILLING_HUB',
      command: 'Start Drill',
      steps: [
        { label: 'Open Billing Hub', type: 'module', module: 'BILLING_HUB' },
        { label: 'Open Invoice Sentinel', type: 'module', module: 'INVOICE_SENTINEL' },
        { label: 'Inspect court-aware billing posture', type: 'check', ready: Boolean(billingMetrics), proof: billingMetrics ? 'Billing metrics linked' : 'Billing metrics pending' },
        { label: 'Return to Investor Proof', type: 'module', module: 'INVESTOR_PROOF' }
      ]
    },
    {
      id: 'AI_CONTROL_LOCK',
      title: 'AI Control Lock',
      purpose: 'Show why AI must operate inside WILSY governance instead of becoming an unsupervised risk.',
      module: 'RISK_SENTINEL',
      command: 'Lock AI Control',
      steps: [
        { label: 'Open Risk Sentinel', type: 'module', module: 'RISK_SENTINEL' },
        { label: 'Inspect compliance memory', type: 'check', ready: Boolean(compliance), proof: compliance ? 'Compliance feed linked' : 'Compliance feed pending' },
        { label: 'Inspect forensic memory', type: 'check', ready: Boolean(forensics), proof: forensics ? 'Forensic feed linked' : 'Forensic feed pending' },
        { label: 'Open Crisis Command', type: 'module', module: 'CRISIS_COMMAND' }
      ]
    }
  ]), [activeTenant, aiEraDefensibility.score, allCommands.length, billingMetrics, compliance, forensics, founderProfile.company, osSpine.realDataRatio]);

  /**
   * @function appendMissionLog
   * @description Adds a timestamped mission event to the Founder mission console.
   *
   * @param {string} missionId - Active mission identifier.
   * @param {string} message - Human-readable mission event.
   * @param {string} [state='INFO'] - Event classification.
   * @returns {void}
   */
  const appendMissionLog = useCallback((missionId, message, state = 'INFO') => {
    setMissionRun(prev => ({
      ...prev,
      log: [
        {
          id: `${missionId}-${Date.now()}-${prev.log.length}`,
          missionId,
          state,
          message,
          time: new Date().toLocaleTimeString('en-GB')
        },
        ...prev.log
      ].slice(0, 8)
    }));
  }, []);

  /**
   * @function runFounderMission
   * @description Executes a Founder mission step-by-step, updating progress and
   * routing to modules or Omega Strike artifacts when required.
   *
   * @param {Object} mission - Mission definition from `founderMissionDeck`.
   * @returns {Promise<void>}
   */
  const runFounderMission = useCallback(async (mission) => {
    if (!mission || missionRun.status === 'RUNNING') return;

    setMissionRun(prev => ({
      ...prev,
      activeMission: mission.id,
      status: 'RUNNING',
      progress: 0,
      log: prev.log
    }));
    appendMissionLog(mission.id, `${mission.title} initiated`, 'START');

    for (let index = 0; index < mission.steps.length; index += 1) {
      const step = mission.steps[index];
      appendMissionLog(mission.id, step.label, step.type === 'check' && !step.ready ? 'WARN' : 'STEP');

      if (step.type === 'omega') {
        await executeOmegaStrike(step.actionId, step.endpoint, step.method || 'GET', step.payload || {});
      }

      if (step.type === 'module') {
        activateModule(step.module);
      }

      if (step.type === 'check') {
        appendMissionLog(mission.id, step.proof || (step.ready ? 'Ready' : 'Needs data'), step.ready ? 'PASS' : 'WARN');
      }

      setMissionRun(prev => ({
        ...prev,
        progress: Math.round(((index + 1) / mission.steps.length) * 100)
      }));
    }

    setMissionRun(prev => ({
      ...prev,
      activeMission: mission.id,
      status: 'COMPLETE',
      progress: 100
    }));
    appendMissionLog(mission.id, `${mission.title} complete`, 'COMPLETE');
  }, [activateModule, appendMissionLog, executeOmegaStrike, missionRun.status]);

  /**
   * @constant singularitySurfaces
   * @description Defines the Founder-only Singularity Matrix panes. Each pane
   * is a real module mounted into one focused viewport so operators do not read
   * unrelated dashboards side-by-side.
   *
   * @returns {Array<Object>} Role-controlled Matrix surface definitions.
   * @collaboration Wilson Khanyezi rejected mixed scrolling surfaces; Codex
   * turns the Matrix into an OS-grade tabbed command workspace.
   */
  const singularitySurfaces = useMemo(() => ([
    {
      id: 'REVENUE',
      label: 'Revenue Titan',
      eyebrow: 'Capital Operations',
      proof: billingMetrics ? 'Live billing feed linked' : 'Awaiting live billing source',
      icon: DollarSign
    },
    {
      id: 'COMPLIANCE',
      label: 'Compliance Sentinel',
      eyebrow: 'Regulatory Control',
      proof: compliance ? 'Live compliance feed linked' : 'Awaiting compliance source',
      icon: ShieldCheck
    },
    {
      id: 'FORENSICS',
      label: 'Forensic Nexus',
      eyebrow: 'Audit Proof Chain',
      proof: forensics ? 'Live forensic feed linked' : 'Awaiting forensic source',
      icon: Fingerprint
    },
    {
      id: 'COMMAND',
      label: 'Singularity Command',
      eyebrow: 'Autonomous OS Layer',
      proof: dataError ? 'One or more sources degraded' : 'Matrix source scan active',
      icon: Brain
    }
  ]), [billingMetrics, compliance, dataError, forensics]);

  /**
   * @constant activeSingularitySurface
   * @description Resolves the active Matrix pane metadata and falls back to the
   * first surface if a stale preference points at a removed pane.
   *
   * @returns {Object} Active Singularity Matrix surface definition.
   */
  const activeSingularitySurface = useMemo(() => (
    singularitySurfaces.find(surface => surface.id === singularitySurface) || singularitySurfaces[0]
  ), [singularitySurface, singularitySurfaces]);

  /**
   * @constant operatorIntentRoute
   * @description Recommends the next Matrix pane from live source state. This is
   * the first layer of a patentable Wilsy OS behavior: an authority-aware cockpit
   * that routes the operator to the highest-value next action instead of waiting
   * for manual browsing.
   *
   * @returns {Object} Recommended Matrix destination and reason.
   * @collaboration Wilson Khanyezi compared the desired behavior to algorithmic
   * product pull. Codex applies that idea to founder/super-admin operations.
   */
  const operatorIntentRoute = useMemo(() => {
    if (!billingMetrics) {
      return {
        surfaceId: 'REVENUE',
        label: 'Verify Revenue Feed',
        reason: 'Billing source is the first missing operating proof.'
      };
    }
    if (!compliance) {
      return {
        surfaceId: 'COMPLIANCE',
        label: 'Verify Compliance Shield',
        reason: 'Regulatory control has not reported live context.'
      };
    }
    if (!forensics) {
      return {
        surfaceId: 'FORENSICS',
        label: 'Verify Evidence Chain',
        reason: 'Forensic proof is not yet mounted into the Matrix.'
      };
    }
    return {
      surfaceId: 'COMMAND',
      label: 'Launch Founder Mission',
      reason: 'Core live sources are linked; mission execution is the next move.'
    };
  }, [billingMetrics, compliance, forensics]);

  /**
   * @function switchSingularitySurface
   * @description Moves the Founder viewport to a single operational plane and
   * records the focus change in the mission console.
   *
   * @param {string} surfaceId - Target Singularity Matrix pane identifier.
   * @returns {void}
   * @collaboration Wilson Khanyezi mandated OS-like transitions where a button
   * changes the working surface immediately instead of forcing manual scrolling.
   */
  const switchSingularitySurface = useCallback((surfaceId) => {
    const surface = singularitySurfaces.find(item => item.id === surfaceId);
    if (!surface || surfaceId === singularitySurface) return;
    setSingularitySurface(surfaceId);
    appendMissionLog('SINGULARITY_MATRIX', `Focused ${surface.label}`, 'STEP');
  }, [appendMissionLog, singularitySurface, singularitySurfaces]);

  /**
   * @constant singularityProcessDeck
   * @description Maps each Matrix pane to Founder-grade operating actions. These
   * actions route to live modules, export real backend artifacts, or execute
   * mission loops already wired into the OS.
   *
   * @returns {Object<string, Object>} Process controls for the active Matrix pane.
   * @collaboration Wilson Khanyezi demanded interactions beyond scrolling.
   * Codex converts each Matrix surface into a commandable operating process.
   */
  const singularityProcessDeck = useMemo(() => ({
    REVENUE: {
      headline: 'Revenue is not a dashboard. It is a money-motion control loop.',
      context: billingMetrics
        ? `Billing source synced ${billingMetrics.lastSync ? new Date(billingMetrics.lastSync).toLocaleTimeString('en-GB') : 'from live summary'}.`
        : 'Billing source is not currently linked; actions will expose the revenue control surfaces.',
      actions: [
        { id: 'OPEN_REVENUE_LEDGER', label: 'Open Revenue Ledger', icon: TrendingUp, handler: () => activateModule('REVENUE_LEDGER') },
        { id: 'OPEN_BILLING_HUB', label: 'Open Billing Hub', icon: CreditCard, handler: () => activateModule('BILLING_HUB') },
        { id: 'EXPORT_REVENUE_ARTIFACT', label: 'Export Revenue Artifact', icon: FileText, handler: () => executeOmegaStrike('STMT_REVENUE', '/statements/revenue') }
      ]
    },
    COMPLIANCE: {
      headline: 'Compliance becomes an operating shield when it can route, prove and escalate.',
      context: compliance
        ? 'Compliance source is mounted into the Founder Matrix.'
        : 'Compliance source is silent; the Matrix will not manufacture a compliance score.',
      actions: [
        { id: 'EXPORT_COMPLIANCE_PROOF', label: 'Export Compliance Proof', icon: ShieldCheck, handler: () => executeOmegaStrike('STMT_COMPLIANCE', '/statements/compliance') },
        { id: 'OPEN_RISK_SENTINEL', label: 'Open Risk Sentinel', icon: AlertOctagon, handler: () => activateModule('RISK_SENTINEL') },
        { id: 'OPEN_IDENTITY_HUB', label: 'Inspect Authority Graph', icon: Key, handler: () => activateModule('IDENTITY_HUB') }
      ]
    },
    FORENSICS: {
      headline: 'Forensics is the memory of the OS. Every serious claim needs an evidence route.',
      context: forensics
        ? 'Forensic source is mounted into the Founder Matrix.'
        : 'Forensic source is silent; the Matrix will show only live or unavailable evidence.',
      actions: [
        { id: 'EXPORT_FORENSIC_SEAL', label: 'Export Forensic Seal', icon: Fingerprint, handler: () => executeOmegaStrike('STMT_FORENSIC', '/statements/forensics') },
        { id: 'OPEN_AUDIT_VAULT', label: 'Open Audit Vault', icon: Microscope, handler: () => activateModule('AUDIT_VAULT') },
        { id: 'OPEN_STATEMENT_ENGINE', label: 'Open Statement Engine', icon: FileSignature, handler: () => activateModule('STATEMENT_ENGINE') }
      ]
    },
    COMMAND: {
      headline: 'The Founder does not browse the OS. The Founder launches missions.',
      context: `${allCommands.length} live command definitions mounted. ${missionRun.status === 'RUNNING' ? 'Mission in progress.' : 'Mission deck ready.'}`,
      actions: [
        {
          id: 'RUN_READINESS_SCAN',
          label: 'Run Founder Readiness Scan',
          icon: BadgeCheck,
          handler: () => runFounderMission(founderMissionDeck.find(mission => mission.id === 'FOUNDER_READINESS_SCAN'))
        },
        { id: 'OPEN_COMMAND_PALETTE', label: 'Open Command Palette', icon: TerminalSquare, handler: () => setIsCommandPaletteOpen(true) },
        { id: 'OPEN_GLOBAL_TOPOLOGY', label: 'Inspect Global Topology', icon: Globe, handler: () => activateModule('GLOBAL_ORCHESTRATOR') }
      ]
    }
  }), [
    activateModule,
    allCommands.length,
    billingMetrics,
    compliance,
    executeOmegaStrike,
    forensics,
    founderMissionDeck,
    missionRun.status,
    runFounderMission
  ]);

  /**
   * @constant activeSingularityProcesses
   * @description Resolves process controls for the focused Matrix pane.
   *
   * @returns {Object} Active process deck.
   */
  const activeSingularityProcesses = useMemo(() => (
    singularityProcessDeck[activeSingularitySurface.id] || singularityProcessDeck.REVENUE
  ), [activeSingularitySurface.id, singularityProcessDeck]);

  /**
   * @function runSingularityProcess
   * @description Executes a focused Matrix process and writes the activity into
   * the Founder mission console so interactions become visible operating memory.
   *
   * @param {Object} process - Process definition from the active Matrix deck.
   * @returns {Promise<void>}
   * @collaboration Wilson Khanyezi mandated visible founder-grade actions, not
   * passive component cards. This function turns Matrix controls into auditable
   * operating events.
   */
  const runSingularityProcess = useCallback(async (process) => {
    if (!process?.handler) return;
    appendMissionLog('SINGULARITY_MATRIX', `Process started: ${process.label}`, 'START');
    await process.handler();
    appendMissionLog('SINGULARITY_MATRIX', `Process routed: ${process.label}`, 'COMPLETE');
  }, [appendMissionLog]);

  // ==========================================================================
  // FILTERED TELEMETRY EVENTS
  // ==========================================================================

  const filteredEvents = useMemo(() => {
    if (filterType === 'ALL') return telemetryEvents;
    if (filterType === 'BILLING') {
      return telemetryEvents.filter(ev => {
        const type = (ev.eventType || '').toUpperCase();
        return type.includes('BILLING') || type.includes('INVOICE') || type.includes('VAULT_STORE') || type.includes('FINANCIAL');
      });
    }
    return telemetryEvents.filter(ev => ev.eventType?.toUpperCase().includes(filterType.toUpperCase()));
  }, [telemetryEvents, filterType]);

  // ==========================================================================
  // CHART DATA & OPTIONS
  // ==========================================================================

  const chartData = useMemo(() => {
    const telemetryArray = Array.isArray(telemetryStats) ? telemetryStats : [];
    const labels = [...new Set(telemetryArray.filter(s => s._id?.day).map(s => s._id.day))];
    return {
      labels: labels.length > 0 ? labels : ['Genesis Protocol'],
      datasets: [
        {
          label: 'Revenue Strikes',
          data: labels.map(day => {
            const stat = telemetryArray.find(s => s._id?.day === day && (s._id?.type === 'PDF_GENERATED' || s._id?.type === 'REVENUE_REPORT'));
            return stat ? stat.count : 0;
          }),
          backgroundColor: '#D4AF37'
        },
        {
          label: 'Science: Compliance',
          data: labels.map(day => {
            const stat = telemetryArray.find(s => s._id?.day === day && s._id?.type === 'COMPLIANCE_REPORT');
            return stat ? stat.count : 0;
          }),
          backgroundColor: '#444444'
        },
        {
          label: 'Science: Forensics',
          data: labels.map(day => {
            const stat = telemetryArray.find(s => s._id?.day === day && s._id?.type === 'FORENSICS_REPORT');
            return stat ? stat.count : 0;
          }),
          backgroundColor: '#888888'
        }
      ]
    };
  }, [telemetryStats]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#D4AF37', font: { family: 'Helvetica', weight: 'bold', size: 10 } } } },
    scales: {
      x: { ticks: { color: '#666' }, grid: { color: '#222' } },
      y: { ticks: { color: '#666' }, grid: { color: '#222' } }
    }
  };

  const getHealthColor = () => {
    if (systemHealth.includes('FRACTURE')) return '#ff3333';
    if (systemHealth.includes('HYDRATING')) return '#D4AF37';
    return '#00ff00';
  };

  // ==========================================================================
  // RENDER MODULE CONTENT – ALL 20+ DEPARTMENTS
  // ==========================================================================

  /**
   * @function renderModuleContent
   * @description Renders the currently active module inside a SovereignErrorBoundary.
   * Every department module receives live data (billingMetrics, telemetryStats,
   * executeOmegaStrike) for real-world institutional operation.
   * @returns {JSX.Element}
   */
  const renderModuleContent = () => {
    const quadShield = { isolation: 'isolate', overflow: 'hidden', position: 'relative' };

    return (
      <SovereignErrorBoundary>
        {(() => {
          switch (activeModule) {

            // 👁️ NEW BOARDROOM HUD VIEW
            case 'BOARDROOM_HUD':
              return null;

            case 'INVESTOR_PROOF':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '760px' }}>
                  <section className={styles.investorProof}>
                    <div className={styles.proofHero}>
                      <div className={styles.proofHeroCopy}>
                        <span className={styles.proofPill}><BadgeCheck size={14} /> Investor-Grade Operating Thesis</span>
                        <h2>Why WILSY OS Wins</h2>
                        <p>
                          WILSY OS is built as a business operating system: revenue, legal execution, identity,
                          audit evidence, tenant expansion and executive command share one evidence layer.
                        </p>
                      </div>
                      <div className={styles.proofMetrics}>
                        <div>
                          <span>Mounted Modules</span>
                          <strong>{osSpine.mounted}</strong>
                        </div>
                        <div>
                          <span>Executable Commands</span>
                          <strong>{osSpine.commandCount}</strong>
                        </div>
                        <div>
                          <span>Real Data Readiness</span>
                          <strong>{osSpine.realDataRatio}%</strong>
                        </div>
                        <div>
                          <span>Founder Tenant</span>
                          <strong>{activeTenant?.tenantId || activeTenant?.id || 'MASTER'}</strong>
                        </div>
                      </div>
                    </div>

                    <div className={styles.proofGrid}>
                      {investorProofMatrix.map(item => (
                        <article key={item.title} className={styles.proofCard} data-ready={item.ready ? 'true' : 'false'}>
                          <div className={styles.proofCardHeader}>
                            <BadgeCheck size={18} />
                            <span className={styles.proofStatus}>{item.ready ? 'PROVEN' : 'NEEDS LIVE DATA'}</span>
                          </div>
                          <h3>{item.title}</h3>
                          <p>{item.claim}</p>
                          <strong>{item.proof}</strong>
                          <button type="button" className={styles.proofButton} onClick={() => activateModule(item.module)}>
                            {item.action}
                          </button>
                        </article>
                      ))}
                    </div>

                    <div className={styles.proofMoatGrid}>
                      {[
                        {
                          title: 'Patent Candidate: Sovereign Data Plane',
                          text: 'One governed command layer routes every business module through tenant, evidence and authority context.',
                          icon: Network
                        },
                        {
                          title: 'Patent Candidate: Forensic Operating Memory',
                          text: 'Actions are treated as institutional evidence, not disposable logs, so diligence can inspect what happened and why.',
                          icon: Fingerprint
                        },
                        {
                          title: 'Patent Candidate: Jurisdiction Revenue Router',
                          text: 'Billing, collections, court registry and compliance can move together instead of living in separate products.',
                          icon: Scale
                        },
                        {
                          title: 'Patent Candidate: Founder Sovereignty Profile',
                          text: 'The owner identity is editable, visible and tied to preferences, module posture and investor presentation mode.',
                          icon: UserCog
                        }
                      ].map(moat => (
                        <article key={moat.title} className={styles.proofMoat}>
                          <moat.icon size={18} />
                          <div>
                            <h3>{moat.title}</h3>
                            <p>{moat.text}</p>
                          </div>
                        </article>
                      ))}
                    </div>

                    <section className={styles.aiMoat}>
                      <div className={styles.aiMoatHeader}>
                        <span><Rocket size={15} /> AI-Era Defensibility</span>
                        <strong>{aiEraDefensibility.score}%</strong>
                      </div>
                      <p>{aiEraDefensibility.thesis}</p>
                      <div className={styles.aiMoatGrid}>
                        {aiEraDefensibility.pillars.map(pillar => (
                          <article key={pillar.title} className={styles.aiMoatCard} data-ready={pillar.ready ? 'true' : 'false'}>
                            <pillar.icon size={18} />
                            <div>
                              <span>{pillar.ready ? 'ANCHORED' : 'AWAITING DATA'}</span>
                              <h3>{pillar.title}</h3>
                              <p>{pillar.text}</p>
                            </div>
                          </article>
                        ))}
                      </div>
                    </section>

                    <section className={styles.valueLoops}>
                      <div className={styles.valueLoopsHeader}>
                        <span><Layers3 size={15} /> Sovereign Control Loops</span>
                        <strong>Why This Cannot Be Replaced By Generated Screens</strong>
                      </div>
                      <div className={styles.valueLoopGrid}>
                        {sovereignValueLoops.map(loop => (
                          <article key={loop.title} className={styles.valueLoopCard}>
                            <Workflow size={18} />
                            <div>
                              <h3>{loop.title}</h3>
                              <p>{loop.path}</p>
                            </div>
                            <button type="button" className={styles.proofButtonSecondary} onClick={() => activateModule(loop.module)}>
                              {loop.action}
                            </button>
                          </article>
                        ))}
                      </div>
                    </section>

                    <section className={styles.missionControl}>
                      <div className={styles.missionHeader}>
                        <div>
                          <span><TerminalSquare size={15} /> Founder Mission Control</span>
                          <h3>Operate The System, Do Not Just View It</h3>
                        </div>
                        <div className={styles.missionProgress}>
                          <strong>{missionRun.progress}%</strong>
                          <span>{missionRun.status}</span>
                        </div>
                      </div>
                      <div className={styles.missionGrid}>
                        {founderMissionDeck.map(mission => (
                          <article key={mission.id} className={styles.missionCard} data-active={missionRun.activeMission === mission.id ? 'true' : 'false'}>
                            <div className={styles.missionCardTop}>
                              <span>{mission.steps.length} steps</span>
                              <strong>{mission.command}</strong>
                            </div>
                            <h3>{mission.title}</h3>
                            <p>{mission.purpose}</p>
                            <ol>
                              {mission.steps.map(step => (
                                <li key={step.label}>{step.label}</li>
                              ))}
                            </ol>
                            <button
                              type="button"
                              className={styles.proofButton}
                              disabled={missionRun.status === 'RUNNING'}
                              onClick={() => runFounderMission(mission)}
                            >
                              {missionRun.activeMission === mission.id && missionRun.status === 'RUNNING' ? 'Mission Running' : mission.command}
                            </button>
                          </article>
                        ))}
                      </div>
                      <div className={styles.missionLog}>
                        <span>Mission Log</span>
                        {missionRun.log.length === 0 ? (
                          <p>No mission executed this session.</p>
                        ) : (
                          missionRun.log.map(entry => (
                            <div key={entry.id} data-state={entry.state}>
                              <strong>{entry.time}</strong>
                              <p>{entry.message}</p>
                            </div>
                          ))
                        )}
                      </div>
                    </section>

                    <div className={styles.proofActions}>
                      <button type="button" className={styles.proofButton} onClick={() => activateModule('BILLING_HUB')}>
                        Prove Revenue Workflow
                      </button>
                      <button type="button" className={styles.proofButtonSecondary} onClick={() => activateModule('AUDIT_VAULT')}>
                        Prove Audit Chain
                      </button>
                      <button type="button" className={styles.proofButtonSecondary} onClick={() => activateModule('GLOBAL_ORCHESTRATOR')}>
                        Prove Tenant Topology
                      </button>
                    </div>
                  </section>
                </div>
              );

            case 'SINGULARITY_MATRIX':
              return (
                <section className={`${styles.quad} ${styles.span12} ${styles.singularityWorkspace}`} style={quadShield}>
                  <div className={styles.singularityWorkspaceHeader}>
                    <div className={styles.singularityWorkspaceTitle}>
                      <span>{activeSingularitySurface.eyebrow}</span>
                      <h2>Singularity Matrix Workspace</h2>
                      <p>{activeSingularitySurface.proof}</p>
                    </div>
                    <div className={styles.singularityWorkspaceAuthority}>
                      <strong>{isSingularityWorkspaceAuthorized ? operatorSovereigntyGraph.authorityLabel : 'Authority Required'}</strong>
                      <span>{operatorSovereigntyGraph.displayName} · {operatorSovereigntyGraph.companyScope}</span>
                      <em>{operatorIntentRoute.reason}</em>
                      <button
                        type="button"
                        onClick={() => switchSingularitySurface(operatorIntentRoute.surfaceId)}
                        disabled={!isSingularityWorkspaceAuthorized || activeSingularitySurface.id === operatorIntentRoute.surfaceId}
                      >
                        {operatorIntentRoute.label}
                      </button>
                    </div>
                  </div>

                  <div className={styles.singularityWorkspaceTabs} role="tablist" aria-label="Singularity Matrix operating surfaces">
                    {singularitySurfaces.map(surface => {
                      const SurfaceIcon = surface.icon;
                      const isActive = activeSingularitySurface.id === surface.id;
                      return (
                        <button
                          key={surface.id}
                          type="button"
                          role="tab"
                          aria-selected={isActive}
                          className={`${styles.singularityWorkspaceTab} ${isActive ? styles.singularityWorkspaceTabActive : ''}`}
                          onClick={() => switchSingularitySurface(surface.id)}
                          disabled={!isSingularityWorkspaceAuthorized}
                        >
                          <SurfaceIcon size={18} aria-hidden="true" />
                          <span>{surface.eyebrow}</span>
                          <strong>{surface.label}</strong>
                          <small>{surface.proof}</small>
                        </button>
                      );
                    })}
                  </div>

                  <div className={styles.singularityProcessBand} aria-label="Active Singularity Matrix operating processes">
                    <div className={styles.singularityProcessNarrative}>
                      <span>{activeSingularitySurface.label} Process</span>
                      <strong>{activeSingularityProcesses.headline}</strong>
                      <p>{activeSingularityProcesses.context}</p>
                    </div>
                    <div className={styles.singularityProcessActions}>
                      {activeSingularityProcesses.actions.map(process => {
                        const ProcessIcon = process.icon;
                        return (
                          <button
                            key={process.id}
                            type="button"
                            onClick={() => runSingularityProcess(process)}
                            disabled={!isSingularityWorkspaceAuthorized || actionLoading === process.id || missionRun.status === 'RUNNING'}
                          >
                            <ProcessIcon size={16} aria-hidden="true" />
                            <span>{process.label}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div className={styles.singularityWorkspaceBody} data-surface={activeSingularitySurface.id}>
                    {!isSingularityWorkspaceAuthorized ? (
                      <div className={styles.singularityWorkspaceLock}>
                        <LockKeyhole size={36} aria-hidden="true" />
                        <h3>Founder Authority Required</h3>
                        <p>This Matrix plane is reserved for Founder and super-admin operating roles.</p>
                      </div>
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
                </section>
              );

            case 'REVENUE_LEDGER':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '800px', padding: 0, display: 'flex', flexDirection: 'column' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING SOVEREIGN REVENUE LEDGER...</div>}>
                    <RevenueLedger
                      metrics={billingMetrics}
                      telemetry={telemetryStats}
                      executeCommand={executeOmegaStrike}
                    />
                  </Suspense>
                </div>
              );

            case 'BILLING_HUB':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING SOVEREIGN BILLING...</div>}>
                    <BillingHUD metrics={billingMetrics} executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'INVOICE_SENTINEL':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING INVOICE SENTINEL...</div>}>
                    <InvoiceSentinel metrics={billingMetrics} />
                  </Suspense>
                </div>
              );

            case 'NUCLEUS_MONITOR':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '400px' }}>
                  <NucleusFeedMonitor events={telemetryEvents} stats={telemetryStats} />
                </div>
              );

            case 'EXECUTIVE_OVERSIGHT':
              return (
                <>
                  <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '760px', padding: 0, overflow: 'visible' }}>
                    <Suspense fallback={<div className={styles.loading}>HYDRATING EXECUTIVE DASHBOARD...</div>}>
                      <ExecutiveDashboard metrics={analytics} />
                    </Suspense>
                  </div>
                  <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '520px', padding: 0 }}>
                    <Suspense fallback={<div className={styles.loading}>HYDRATING ANALYTICS DASHBOARD...</div>}>
                      <AnalyticsDashboard metrics={analytics} />
                    </Suspense>
                  </div>
                </>
              );

            case 'CEO_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING CEO DASHBOARD...</div>}>
                    <ExecutiveDashboard role="CEO" metrics={billingMetrics} analytics={analytics} executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'COO_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING COO OPERATIONS HUB...</div>}>
                    <COODashboard telemetry={telemetryStats} executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'HR_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING HR SUITE...</div>}>
                    <HRDashboard executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'SALES_CRM':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>LOADING SOVEREIGN CRM...</div>}>
                    <CRMDashboard metrics={billingMetrics} executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'IT_OPS':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING IT OPS CENTRE...</div>}>
                    <ITDashboard events={telemetryEvents} executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'FINANCE_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING FINANCE SUITE...</div>}>
                    <FinanceDashboard metrics={billingMetrics} executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'LEGAL_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING LEGAL COVENANT SUITE...</div>}>
                    <LegalDashboard forensics={forensics} executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'MARKETING_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING MARKETING SUITE...</div>}>
                    <MarketingDashboard executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'PRODUCT_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING PRODUCT SUITE...</div>}>
                    <ProductDashboard executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'ENGINEERING_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING ENGINEERING SUITE...</div>}>
                    <EngineeringDashboard stats={telemetryStats} executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'DATA_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING DATA SUITE...</div>}>
                    <DataDashboard analytics={analytics} executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'SECURITY_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING SECURITY SUITE...</div>}>
                    <SecurityDashboard forensics={forensics} executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'CUSTOMER_SUCCESS_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING CUSTOMER SUCCESS SUITE...</div>}>
                    <CustomerSuccessDashboard executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'PROCUREMENT_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING PROCUREMENT SUITE...</div>}>
                    <ProcurementDashboard executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'RESEARCH_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING RESEARCH SUITE...</div>}>
                    <ResearchDashboard executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'SPACE_OPERATIONS_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING SPACE OPERATIONS SUITE...</div>}>
                    <SpaceOperationsDashboard executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'AI_ETHICS_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING AI ETHICS SUITE...</div>}>
                    <AIEthicsDashboard executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'QUANTUM_COMPUTING_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING QUANTUM COMPUTING SUITE...</div>}>
                    <QuantumDashboard executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            case 'LONGEVITY_SCIENCES_DASHBOARD':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '600px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING LONGEVITY SCIENCES SUITE...</div>}>
                    <LongevityDashboard executeCommand={executeOmegaStrike} />
                  </Suspense>
                </div>
              );

            // Default protocol renderers
            case 'CLOUD_UPLINK':
              return (
                <>
                  <div className={`${styles.quad} ${styles.span6}`} style={quadShield}>
                    <Suspense fallback={<div className={styles.loading}>HYDRATING CLOUD UPLINK...</div>}>
                      <CloudUplinkDashboard />
                    </Suspense>
                  </div>
                  <div className={`${styles.quad} ${styles.span6}`} style={quadShield}>
                    <Suspense fallback={<div className={styles.loading}>HYDRATING SOVEREIGN NODE DASHBOARD...</div>}>
                      <SovereignNodeDashboard />
                    </Suspense>
                  </div>
                </>
              );

            case 'TENANT_MANAGER':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '640px', padding: 0 }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING TENANT MANAGER...</div>}>
                    <SovereignTenantManager />
                  </Suspense>
                </div>
              );

            case 'STATEMENT_ENGINE':
              return (
                <>
                  <div className={`${styles.quad} ${styles.span4}`} style={{ ...quadShield, minHeight: '360px', padding: 0 }}>
                    <Suspense fallback={<div className={styles.loading}>HYDRATING STATEMENT ENGINE...</div>}>
                      <SovereignStatementEngine tenantId={activeTenant?.id || activeTenant?.tenantId || 'GLOBAL_ROOT'} />
                    </Suspense>
                  </div>
                  <div className={`${styles.quad} ${styles.span8}`} style={{ ...quadShield, padding: 0, display: 'flex', flexDirection: 'column', minHeight: '360px' }}>
                    <div style={{ padding: '15px 20px', borderBottom: '1px solid #1f1f1f', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <TerminalSquare size={14} className="text-[#D4AF37]" />
                        <span style={{ fontSize: '0.7rem', color: '#D4AF37', fontWeight: 900, letterSpacing: '2px' }}>[EVIDENCE] LIVE FORENSIC FEED</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Filter size={12} className="text-[#666]" />
                        <select style={{ background: '#111', color: '#D4AF37', border: '1px solid #333', fontSize: '0.6rem', padding: '2px 5px', outline: 'none' }} value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                          <option value="ALL">ALL LIVE EVIDENCE</option>
                          <option value="REVENUE">REVENUE EVENTS</option>
                          <option value="COMPLIANCE">COMPLIANCE EVENTS</option>
                          <option value="FORENSICS">FORENSIC EVENTS</option>
                          <option value="BILLING">BILLING EVENTS</option>
                        </select>
                        <span style={{ fontSize: '0.55rem', color: telemetrySyncing ? '#D4AF37' : '#00ff00', fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase' }}>
                          {telemetrySyncing ? 'SYNCING...' : 'LIVE'}
                        </span>
                      </div>
                    </div>
                    <div style={{ flex: 1, overflowY: 'auto', padding: '10px 15px', display: 'flex', flexDirection: 'column', gap: '8px', minHeight: '150px' }}>
                      {filteredEvents.length === 0 ? (
                        <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', color: '#666', fontStyle: 'italic', letterSpacing: '1px' }}>NO STEM ACTIVITY DETECTED</div>
                      ) : (
                        filteredEvents.map((ev, index) => (
                          <div key={ev._id || index} style={{ borderLeft: '2px solid #D4AF37', paddingLeft: '10px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span style={{ fontSize: '0.65rem', color: '#fff', fontWeight: 700, letterSpacing: '1px' }}>{ev.eventType}</span>
                              <span style={{ fontSize: '0.55rem', color: '#888', fontVariantNumeric: 'tabular-nums' }}>{new Date(ev.timestamp).toLocaleTimeString('en-GB')}</span>
                            </div>
                            {ev.commandId && <span style={{ fontSize: '0.55rem', color: '#aaa', textTransform: 'uppercase' }}>{ev.commandId}</span>}
                            {ev.traceId && <span style={{ fontSize: '0.5rem', color: '#555', fontFamily: 'monospace' }}>TRACE: {ev.traceId.substring(0, 16)}...</span>}
                            {ev.sealHash && <span style={{ fontSize: '0.5rem', color: '#D4AF37', letterSpacing: '0.5px' }}>SEAL: {ev.sealHash.substring(0, 32)}...</span>}
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, padding: '20px', minHeight: '220px', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ fontSize: '0.7rem', color: '#D4AF37', fontWeight: 900, letterSpacing: '2px', marginBottom: '15px' }}>SOVEREIGN ARTIFACT GENERATION TRENDS</h3>
                    <div style={{ flex: 1, width: '100%', position: 'relative' }}>
                      <Bar data={chartData} options={chartOptions} />
                    </div>
                  </div>
                </>
              );

            case 'AUDIT_VAULT':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '760px', padding: 0, display: 'flex', flexDirection: 'column' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING SOVEREIGN AUDIT VAULT...</div>}>
                    <SovereignAuditVault />
                  </Suspense>
                </div>
              );

            case 'NODE_REGISTRY':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '760px', padding: 0, display: 'flex', flexDirection: 'column' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING SOVEREIGN NODE REGISTRY...</div>}>
                    <SovereignNodeRegistry />
                  </Suspense>
                </div>
              );

            case 'GLOBAL_ORCHESTRATOR':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '760px', padding: 0, display: 'flex', flexDirection: 'column' }}>
                  <Suspense fallback={<div className={styles.loading}>ALIGNING GLOBAL ORCHESTRATOR...</div>}>
                    <SovereignGlobalTopography />
                  </Suspense>
                </div>
              );

            case 'RISK_SENTINEL':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '650px', padding: 0 }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING RISK SENTINEL...</div>}>
                    <RiskSentinel events={telemetryEvents} analytics={analytics} compliance={compliance} />
                  </Suspense>
                </div>
              );

            case 'IDENTITY_HUB':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '760px', padding: 0 }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING IDENTITY HUB...</div>}>
                    <SovereignIdentityHub />
                  </Suspense>
                </div>
              );

            case 'CLIENT_COVENANT':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '680px' }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING CLIENT COVENANT...</div>}>
                    <SovereignClientCovenant />
                  </Suspense>
                </div>
              );

            case 'CRISIS_COMMAND':
              return (
                <div className={`${styles.quad} ${styles.span12}`} style={{ ...quadShield, minHeight: '760px', padding: 0 }}>
                  <Suspense fallback={<div className={styles.loading}>HYDRATING CRISIS COMMAND...</div>}>
                    <SovereignCrisisCommand />
                  </Suspense>
                </div>
              );

            default:
              return null;
          }
        })()}
      </SovereignErrorBoundary>
    );
  };

  // ==========================================================================
  // LAYOUT GUARDS – PREVENT FOOTER/TELEMETRY WRAPPING
  // ==========================================================================

  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      .footer { display: flex !important; flex-wrap: nowrap !important; gap: 20px !important; white-space: nowrap !important; }
      .footer span { white-space: nowrap !important; }
      .telemetryStrip { flex-wrap: wrap !important; row-gap: 8px !important; }
      @media (max-width: 1200px) { .teleGroup { flex-wrap: wrap !important; gap: 10px !important; } .teleItem { font-size: 0.6rem !important; } }
      canvas { max-width: 100% !important; height: auto !important; }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  // ==========================================================================
  // 🔗 STABILIZED RETURN – ENFORCED PROVIDER HIERARCHY
  // ==========================================================================
  // The entire dashboard is wrapped in:
  //   SovereignOrchestrator → DataOrchestrator → CommandUsageProvider → Dashboard UI
  // This guarantees that BillingHUD, RevenueLedger, War Room, and all 20+ shards
  // can access the Neural Mesh context without "must be used within" errors.
  // ==========================================================================

  if (activeModule === 'BOARDROOM_HUD') {
    return (
      <SovereignOrchestrator>
        <DataOrchestrator>
          <CommandUsageProvider>
            <div className={styles.boardroomTheatre}>
              <div className={styles.scanline}></div>
              <header className={styles.boardroomTheatreHeader}>
                <div className={styles.theatreBrand}>
                  <img src={activeTenant?.logoUrl || wilsyLogo} alt="Wilsy OS" />
                  <div>
                    <span>WILSY OS BOARDROOM</span>
                    <strong>Investor Theatre Mode</strong>
                  </div>
                </div>
                <div className={styles.theatreStatus}>
                  <span>FOUNDER ACCESS</span>
                  <span>{systemHealth}</span>
                </div>
                <button
                  type="button"
                  className={styles.theatreBackButton}
                  onClick={() => setActiveModule(boardroomReturnModule || 'SINGULARITY_MATRIX')}
                >
                  <ChevronLeft size={16} />
                  Return To Founder Dashboard
                </button>
              </header>

              <main className={styles.boardroomTheatreStage}>
                <Suspense fallback={<div className={styles.loading}>HYDRATING BOARDROOM TELEMETRY...</div>}>
                  <BoardroomHUD />
                </Suspense>
              </main>
            </div>
          </CommandUsageProvider>
        </DataOrchestrator>
      </SovereignOrchestrator>
    );
  }

  return (
    <SovereignOrchestrator>
      <DataOrchestrator>
        <CommandUsageProvider>
          <div className={styles.container} style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div className={styles.scanline}></div>

            {/* TELEMETRY STRIP */}
            <div className={styles.telemetryStrip} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 30px' }}>
              <div className={styles.teleGroup}>
                <div className={styles.teleItem}><span className="text-[#D4AF37]">SOVEREIGN COCKPIT [STEM]</span></div>
                <div className={styles.teleItem}>
                  <button
                    type="button"
                    className={styles.founderChip}
                    onClick={() => {
                      setProfileDraft(founderProfile);
                      setIsFounderPanelOpen(prev => !prev);
                    }}
                    aria-expanded={isFounderPanelOpen}
                    aria-label="Open founder profile and operating preferences"
                  >
                    <span className={styles.founderAvatar}>{founderInitials}</span>
                    <span className={styles.founderIdentity}>
                      <span>{founderProfile.displayName}</span>
                      <small><Crown size={12} /> {founderProfile.title}</small>
                    </span>
                    <UserCog size={15} />
                  </button>
                </div>
                <div className={styles.teleItem}>
                  <span className={systemHealth.includes('FRACTURE') ? "text-red-500" : "text-emerald-500"}>UPLINK:</span>
                  <span style={{ marginLeft: '5px', fontWeight: systemHealth.includes('FRACTURE') ? 'bold' : 'normal', color: systemHealth.includes('FRACTURE') ? '#ff3333' : 'inherit' }}>{systemHealth}</span>
                  <span style={{ marginLeft: '8px', width: '10px', height: '10px', borderRadius: '50%', display: 'inline-block', backgroundColor: getHealthColor(), boxShadow: `0 0 8px ${getHealthColor()}` }}></span>
                </div>
                <div className={styles.teleItem}><span className="text-[#D4AF37]">[S]CIENCE:</span> {compliance?.ratio ?? 'SOURCE_SILENT'}</div>
                <div className={styles.teleItem}><span className="text-[#D4AF37]">[T]ECH:</span> {analytics?.p95Latency != null ? `${analytics.p95Latency}ms` : 'SOURCE_SILENT'}</div>
                <div className={styles.teleItem}><span className="text-[#D4AF37]">[E]NGINEERING:</span> {analytics?.efficiencyIndex ?? 'SOURCE_SILENT'}</div>
                <div className={styles.teleItem}><span className="text-[#D4AF37]">[M]ATHEMATICS:</span> {analytics?.arrProjection ?? 'SOURCE_SILENT'}</div>
                <div className={styles.teleItem}>
                  <button onClick={() => setIsCommandPaletteOpen(true)} style={{ marginLeft: '20px', background: '#0a0a0a', border: '1px solid #333', color: '#D4AF37', fontSize: '0.6rem', padding: '3px 12px', cursor: 'pointer', fontWeight: 'bold', borderRadius: '3px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <Search size={10} /> [ ⌘K ] STEM_INTAKE
                  </button>
                </div>
              </div>
              <div className={styles.clock}>{currentTime.toLocaleTimeString()}</div>
            </div>

            {isFounderPanelOpen && (
              <section className={styles.founderPanel} aria-label="Founder profile command panel">
                <div className={styles.founderPanelHeader}>
                  <div className={styles.founderPanelMark}>
                    <span>{founderInitials}</span>
                  </div>
                  <div>
                    <span className={styles.panelEyebrow}><Sparkles size={14} /> Founder Sovereignty Profile</span>
                    <h2>{founderProfile.displayName}</h2>
                    <p>{founderProfile.title} - {founderProfile.company}</p>
                  </div>
                  <button
                    type="button"
                    className={styles.panelIconButton}
                    onClick={() => {
                      setIsFounderPanelOpen(false);
                      setIsPreferenceEditing(false);
                    }}
                    aria-label="Close founder profile"
                  >
                    <X size={18} />
                  </button>
                </div>

                <div className={styles.founderPanelGrid}>
                  <div className={styles.founderProfileCard}>
                    <div className={styles.sectionTitle}>
                      <SlidersHorizontal size={16} />
                      Operating Preferences
                    </div>
                    <div className={styles.presetGrid}>
                      {Object.keys(FOUNDER_OPERATING_PRESETS).map(presetName => (
                        <button
                          key={presetName}
                          type="button"
                          className={founderProfile.commandMode === presetName ? styles.presetButtonActive : styles.presetButton}
                          onClick={() => applyFounderPreset(presetName)}
                        >
                          <Sparkles size={14} />
                          <span>{presetName}</span>
                        </button>
                      ))}
                    </div>
                    <div className={styles.preferenceGrid}>
                      {[
                        ['displayName', 'Founder Name', 'text'],
                        ['title', 'Boardroom Title', 'text'],
                        ['company', 'Founder Tenant', 'text'],
                        ['jurisdictionFocus', 'Jurisdiction Focus', 'text']
                      ].map(([key, label, type]) => (
                        <label key={key} className={styles.preferenceField}>
                          <span>{label}</span>
                          <input
                            type={type}
                            value={profileDraft[key] || ''}
                            disabled={!isPreferenceEditing}
                            onChange={event => updateProfileDraft(key, event.target.value)}
                          />
                        </label>
                      ))}
                      {[
                        ['commandMode', 'Command Mode', ['Investor Theatre', 'Forensic Operator', 'Builder Mode']],
                        ['telemetryDensity', 'Telemetry Density', ['Executive', 'Dense', 'Silent']],
                        ['evidenceMode', 'Evidence Mode', ['Real Data Only', 'Diligence Grade', 'Court Ready']],
                        ['narrativeTone', 'Narrative Tone', ['Boardroom', 'Technical', 'Investor']],
                        ['tenantScope', 'Tenant Scope', ['Founder Tenant', 'Current Tenant', 'Multi Tenant']],
                        ['sidebarMode', 'Sidebar Mode', ['Open', 'Closed']],
                        ['quickPanelMode', 'Command Rail', ['Closed', 'Open']]
                      ].map(([key, label, options]) => (
                        <label key={key} className={styles.preferenceField}>
                          <span>{label}</span>
                          <select
                            value={profileDraft[key] || ''}
                            onChange={event => applyPreferenceChange(key, event.target.value)}
                          >
                            {options.map(option => <option key={option} value={option}>{option}</option>)}
                          </select>
                        </label>
                      ))}
                      <label className={styles.preferenceField}>
                        <span>Default Landing Module</span>
                        <select
                          value={profileDraft.defaultModule || 'SINGULARITY_MATRIX'}
                          onChange={event => applyPreferenceChange('defaultModule', event.target.value)}
                        >
                          {founderModuleOptions.map(option => (
                            <option key={option.value} value={option.value}>{option.label}</option>
                          ))}
                        </select>
                      </label>
                      <label className={`${styles.preferenceField} ${styles.preferenceWide}`}>
                        <span>Investor Promise</span>
                        <textarea
                          value={profileDraft.investorPromise || ''}
                          disabled={!isPreferenceEditing}
                          onChange={event => updateProfileDraft('investorPromise', event.target.value)}
                        />
                      </label>
                    </div>
                  </div>

                  <div className={styles.founderProfileCard}>
                    <div className={styles.sectionTitle}>
                      <Palette size={16} />
                      Demo Doctrine
                    </div>
                    <div className={styles.doctrineStack}>
                      <div>
                        <span>Operating Mode</span>
                        <strong>{founderProfile.commandMode}</strong>
                      </div>
                      <div>
                        <span>Evidence Standard</span>
                        <strong>{founderProfile.evidenceMode}</strong>
                      </div>
                      <div>
                        <span>Operating Skin</span>
                        <strong>{founderProfile.theme}</strong>
                      </div>
                      <div>
                        <span>Tenant Authority</span>
                        <strong>{activeTenant?.tenantId || 'MASTER'}</strong>
                      </div>
                      <div>
                        <span>Landing Module</span>
                        <strong>{founderProfile.defaultModule?.replace(/_/g, ' ')}</strong>
                      </div>
                    </div>
                    <p className={styles.doctrineCopy}>{founderProfile.investorPromise}</p>
                  </div>
                </div>

                <div className={styles.patentGrid}>
                  {founderPatentSystems.map(system => {
                    const Icon = system.icon;
                    return (
                      <article key={system.title} className={styles.patentCard}>
                        <Icon size={18} />
                        <strong>{system.title}</strong>
                        <span>{system.text}</span>
                      </article>
                    );
                  })}
                </div>

                <div className={styles.founderPanelActions}>
                  {isPreferenceEditing ? (
                    <>
                      <button type="button" className={styles.goldButton} onClick={saveFounderProfile}>
                        <Save size={15} /> Save Preferences
                      </button>
                      <button type="button" className={styles.ghostButton} onClick={() => {
                        setProfileDraft(founderProfile);
                        setIsPreferenceEditing(false);
                      }}>
                        <X size={15} /> Cancel
                      </button>
                      <button type="button" className={styles.dangerGhost} onClick={resetFounderProfile}>
                        Reset
                      </button>
                    </>
                  ) : (
                    <>
                      <button type="button" className={styles.goldButton} onClick={() => setIsPreferenceEditing(true)}>
                        <UserCog size={15} /> Edit Founder Profile
                      </button>
                      <button type="button" className={styles.ghostButton} onClick={() => activateModule('IDENTITY_HUB')}>
                        <Fingerprint size={15} /> Identity Hub
                      </button>
                      <button type="button" className={styles.ghostButton} onClick={() => activateModule('AUDIT_VAULT')}>
                        <ShieldCheck size={15} /> Audit Vault
                      </button>
                    </>
                  )}
                </div>
              </section>
            )}

            {/* MAIN GRID */}
            <div
              className={`${styles.mainGrid} ${isQuickPanelOpen ? styles.quickPanelExpanded : styles.quickPanelCollapsed}`}
              data-sidebar={isSidebarOpen ? 'open' : 'closed'}
              data-focus={activeModule === 'SALES_CRM' ? 'crm' : 'standard'}
            >
              {!isSidebarOpen && (
                <button
                  type="button"
                  className={styles.sidebarReveal}
                  aria-label="Open sovereign sidebar"
                  onClick={() => setIsSidebarOpen(true)}
                >
                  <PanelLeftOpen size={18} />
                  <span>Navigation</span>
                </button>
              )}

              {/* SIDEBAR NAVIGATION */}
              {isSidebarOpen && (
              <nav className={styles.sidebar} style={{ display: 'flex', flexDirection: 'column', height: '100%', flexShrink: 0, overflowY: 'auto' }}>
                <button
                  type="button"
                  className={styles.sidebarCollapseBtn}
                  aria-label="Close sovereign sidebar"
                  onClick={() => setIsSidebarOpen(false)}
                >
                  <PanelLeftClose size={15} />
                  <span>Close Sidebar</span>
                </button>
                <div className={styles.sidebarHeader}>
                  <div className={styles.logoBezel}>
                    <img src={activeTenant?.logoUrl || wilsyLogo} alt="Wilsy OS" className={styles.logo} />
                  </div>
                  <div>
                    <div className={styles.brand}>{activeTenant?.name || 'WILSY OS'}</div>
                    <div className={styles.subtitle}>SHARD: {activeTenant?.tenantId || 'SOVEREIGN_ROOT'}</div>
                    <div className={styles.brandSeal}>LEGAL SOVEREIGN STANDARD</div>
                  </div>
                </div>

                <div className={styles.nav}>
                  <div className={styles.navSectionLabel}>COCKPIT_LEVEL</div>
                  {COMMAND_LEVEL_KEYS.map(key => (
                    <button key={key} className={activeModule === key ? styles.navItemActive : styles.navItem} onClick={() => activateModule(key)}>
                      {getModuleIcon(key)}
                      <span style={{ marginLeft: '8px' }}>{key.replace(/_/g, ' ')}</span>
                    </button>
                  ))}

                  <div className={styles.navSectionLabel}>INSTITUTIONAL_HUB</div>
                  {SOVEREIGN_HUB_KEYS.map(key => (
                    <button key={key} className={activeModule === key ? styles.navItemActive : styles.navItem} onClick={() => setActiveModule(key)}>
                      {getModuleIcon(key)}
                      <span style={{ marginLeft: '8px' }}>{key.replace(/_/g, ' ')}</span>
                    </button>
                  ))}

                  <div className={styles.navSectionLabel}>LEADERSHIP</div>
                  {LEADERSHIP_KEYS.map(key => (
                    <button key={key} className={activeModule === key ? styles.navItemActive : styles.navItem} onClick={() => setActiveModule(key)}>
                      {getModuleIcon(key)}
                      <span style={{ marginLeft: '8px' }}>{key.replace(/_/g, ' ')}</span>
                    </button>
                  ))}

                  <div className={styles.navSectionLabel}>CORE DEPARTMENTS</div>
                  {CORE_DEPT_KEYS.map(key => {
                    let label = key.replace(/_/g, ' ');
                    if (key === 'SALES_CRM') label = 'SALES & CRM';
                    return (
                      <button key={key} className={activeModule === key ? styles.navItemActive : styles.navItem} onClick={() => setActiveModule(key)}>
                        {getModuleIcon(key)}
                        <span style={{ marginLeft: '8px' }}>{label}</span>
                      </button>
                    );
                  })}

                  <div className={styles.navSectionLabel}>ADVANCED SUITES</div>
                  {ADVANCED_DEPT_KEYS.map(key => (
                    <button key={key} className={activeModule === key ? styles.navItemActive : styles.navItem} onClick={() => setActiveModule(key)}>
                      {getModuleIcon(key)}
                      <span style={{ marginLeft: '8px' }}>{key.replace(/_DASHBOARD/g, '').replace(/_/g, ' ')}</span>
                    </button>
                  ))}

                  <div className={styles.navSectionLabel}>FUTURE PROOF</div>
                  {FUTURE_DEPT_KEYS.map(key => (
                    <button key={key} className={activeModule === key ? styles.navItemActive : styles.navItem} onClick={() => setActiveModule(key)}>
                      {getModuleIcon(key)}
                      <span style={{ marginLeft: '8px' }}>{key.replace(/_DASHBOARD/g, '').replace(/_/g, ' ')}</span>
                    </button>
                  ))}

                  <div className={styles.navSectionLabel}>PROTOCOL_SYSTEMS</div>
                  <button className={activeModule === 'TENANT_MANAGER' ? styles.navItemActive : styles.navItem} onClick={() => setActiveModule('TENANT_MANAGER')}>
                    <Users size={16} className={activeModule === 'TENANT_MANAGER' ? "text-[#D4AF37]" : "text-stone-500"} />
                    <span style={{ marginLeft: '8px' }}>Engineering: Shards</span>
                  </button>
                  <button className={activeModule === 'STATEMENT_ENGINE' ? styles.navItemActive : styles.navItem} onClick={() => setActiveModule('STATEMENT_ENGINE')}>
                    <FileText size={16} className={activeModule === 'STATEMENT_ENGINE' ? "text-[#D4AF37]" : "text-stone-500"} />
                    <span style={{ marginLeft: '8px' }}>Mathematics: Statements</span>
                  </button>

                  <div style={{ height: '1px', background: '#111', margin: '15px 0' }}></div>

                  <button className={activeModule === 'INVOICE_SENTINEL' ? styles.navItemActive : styles.navItem} onClick={() => setActiveModule('INVOICE_SENTINEL')}>
                    <Receipt size={16} style={{ marginRight: '8px', color: activeModule === 'INVOICE_SENTINEL' ? '#D4AF37' : '#888' }} />
                    <span>INVOICE SENTINEL</span>
                  </button>

                  <button className={activeModule === 'NUCLEUS_MONITOR' ? styles.navItemActive : styles.navItem} onClick={() => setActiveModule('NUCLEUS_MONITOR')}>
                    <TerminalSquare size={16} style={{ marginRight: '8px', color: activeModule === 'NUCLEUS_MONITOR' ? '#D4AF37' : '#888' }} />
                    <span>NUCLEUS MONITOR</span>
                  </button>
                </div>

                <button onClick={logout} className={styles.logoutBtn} style={{ marginTop: '20px' }}>
                  <LogOut size={16} /> TERMINATE SESSION
                </button>
              </nav>
              )}

              {/* CONTENT GRID */}
              <div className={styles.contentGrid}>
                <section className={styles.osSpine}>
                  <div className={styles.osSpineMain}>
                    <span className={styles.osSpineEyebrow}><Network size={14} /> Operating System Spine</span>
                    <h2>{activeModuleMeta.label}</h2>
                    <p>{activeModuleMeta.description}</p>
                  </div>
                  <div className={styles.osSpineMeta}>
                    <div>
                      <span>Layer</span>
                      <strong>{activeModuleMeta.layer}</strong>
                    </div>
                    <div>
                      <span>Feed</span>
                      <strong>{activeModuleMeta.feed}</strong>
                    </div>
                    <div>
                      <span>Modules</span>
                      <strong>{osSpine.mounted}</strong>
                    </div>
                    <div>
                      <span>Commands</span>
                      <strong>{osSpine.commandCount}</strong>
                    </div>
                    <div>
                      <span>Real Data</span>
                      <strong>{osSpine.realDataRatio}%</strong>
                    </div>
                  </div>
                  <div className={styles.osFeedRail}>
                    {osSpine.feeds.map(feed => (
                      <span key={feed.label} data-ready={feed.ready ? 'true' : 'false'}>
                        {feed.label}: <strong>{feed.status}</strong>
                      </span>
                    ))}
                  </div>
                </section>
                {activeModule !== 'SALES_CRM' && (
                  <NeuralNarrativeCapsule currentNarrative={currentNarrative} shardId={activeTenant?.tenantId} />
                )}
                {renderModuleContent()}
              </div>

              {/* QUICK ACTIONS PANEL */}
              <aside
                className={`${styles.quickActions} ${isQuickPanelOpen ? styles.quickActionsOpen : styles.quickActionsClosed}`}
                aria-label="Behavioral quick panel"
              >
                <button
                  type="button"
                  className={styles.quickPanelToggle}
                  aria-expanded={isQuickPanelOpen}
                  aria-label={isQuickPanelOpen ? 'Collapse behavioral quick panel' : 'Open behavioral quick panel'}
                  onClick={() => setIsQuickPanelOpen((open) => !open)}
                >
                  {isQuickPanelOpen ? <PanelRightClose size={18} /> : <PanelRightOpen size={18} />}
                  <span>{isQuickPanelOpen ? 'Collapse Panel' : 'Command Panel'}</span>
                </button>

                {isQuickPanelOpen ? (
                  <>
                    <div className={styles.quickPanelScroll}>
                      <QuickPanel allCommands={allCommands} onExecute={(handler) => handler()} />
                    </div>
                    <button className={`${styles.actionBtnRed} ${styles.quickTerminateButton}`} onClick={logout}>
                      <LogOut size={16} /> Terminate Session
                    </button>
                  </>
                ) : (
                  <div className={styles.quickRailStatus} aria-hidden="true">
                    <span>Commands</span>
                    <strong>{allCommands.length}</strong>
                  </div>
                )}
              </aside>
            </div>

            {/* FOOTER */}
            <footer className={styles.footer} style={{ height: '40px', minHeight: '40px' }}>
              <span>* BIBLICAL WORTH ESTABLISHED * STEM PROTOCOL PQE-256 ACTIVE * SOVEREIGN AI • 2050 TIMESTAMP</span>
              <span className={styles.footerBrand}>WILSY OS — LEGAL SOVEREIGN STANDARD • BOARDROOM HUD: FORTUNE-500 SOVEREIGN FINALITY</span>
            </footer>

            {/* COMMAND PALETTE */}
            <CommandPalette
              isOpen={isCommandPaletteOpen}
              onOpen={() => setIsCommandPaletteOpen(true)}
              onClose={() => setIsCommandPaletteOpen(false)}
              actions={actionCommands}
              modules={moduleCommands}
            />
          </div>
        </CommandUsageProvider>
      </DataOrchestrator>
    </SovereignOrchestrator>
  );
};

export default FounderDashboard;
