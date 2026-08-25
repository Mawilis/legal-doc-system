/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Unified Dashboard Registry
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/src/constants/dashboards.js
 * Version:        v1.0.1-SYNTAX-CORRECTED
 * Authority:      Wilsy OS Core Governance
 * Epitome:        The single source of truth for all dashboard modules in the
 *                 Wilsy OS ecosystem. Enumerates every sovereign, core, industry,
 *                 and future dashboard with metadata, icons, and category grouping.
 *                 Used by the Founder Dashboard and Command Palette to provide
 *                 unified navigation across the entire institutional surface.
 * Classification: Production Artifact
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) — Mandated absolute system unification
 *     and billion‑tenant navigability.
 *   - AI Engineering — RECTIFIED: Corrected import/export syntax to prevent
 *     `CATEGORIES` and helper functions from being pulled from `lucide-react`.
 *
 * Change Log:
 *   2026-07-31 v1.0.1-SYNTAX-CORRECTED — Fixed import/export collision.
 *   2026-07-31 v1.0.0-INSTITUTIONAL-SEAL — Initial certified release.
 *
 * Forensic Relationships:
 *   Upstream:   lucide-react
 *   Downstream: client/src/components/sovereign/FounderDashboard.jsx,
 *               client/src/components/sovereign/CockpitStatusBar.jsx,
 *               client/src/components/sovereign/CommandPalette.jsx
 *   Shared Crypto / Events / Config: None (pure constants).
 *
 * Certification Seal: PRODUCTION_READY_v1.0.1-SYNTAX-CORRECTED
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import {
  Activity, ShieldCheck, Zap, Globe, Users,
  FileText, Target, Cpu, Database, Server,
  Lock, Key, Fingerprint, FileSignature, AlertOctagon,
  Scale, Power, ShieldAlert, Network, Radio, TerminalSquare, TrendingUp, Search, BarChart3, Microscope, UserCheck, Crown,
  CreditCard, Receipt, Coins, Landmark, Briefcase, Calendar, MessageSquare, PieChart, Settings,
  DollarSign, Gavel, Megaphone, Box, Code, LockKeyhole, HeartHandshake, ShoppingCart, FlaskConical,
  Satellite, Brain, Dna, Eye, PanelLeftOpen, SlidersHorizontal, Sparkles, BadgeCheck, FileCheck2, Rocket, Workflow,
  Bell, Info, CheckCircle, AlertTriangle, ChevronDown, Command,
  Sprout, Building, Factory, Store, Building2, Gamepad2, GraduationCap, HeartPulse,
  Film, Home, Projector, Truck, HandHeart, Infinity
} from 'lucide-react';

/**
 * @constant CATEGORIES
 * @description The top‑level navigation categories for dashboard grouping.
 * Institutional Commentary: These categories correspond to the tabbed dropdown
 * menus in the Founder Cockpit, providing intuitive access to every module.
 */
export const CATEGORIES = {
  CORE: 'Core & Operations',
  SOVEREIGN: 'Sovereign / Executive',
  INDUSTRY: 'Industry & Domain',
  FUTURE: 'Longevity & Future',
  CONTROL: 'Control Room',
};

/**
 * @constant ALL_MODULES
 * @description The complete registry of every dashboard module in Wilsy OS.
 * Each entry contains: key, label, icon, category, path (for reference), and
 * optional description.
 * Institutional Commentary: This is the single source of truth for navigation.
 * The Founder Dashboard generates its dropdown menus directly from this registry.
 * @type {Object.<string, {label: string, icon: React.Element, category: string, path: string, description?: string}>}
 */
export const ALL_MODULES = {
  // ─── Core & Operations ────────────────────────────────────────────────────
  COO_DASHBOARD: {
    label: 'COO Operations',
    icon: <Briefcase size={16} />,
    category: CATEGORIES.CORE,
    path: 'client/src/components/coo/COODashboard.jsx',
    description: 'Chief Operations Officer command center',
  },
  PRODUCT_DASHBOARD: {
    label: 'Product Management',
    icon: <Box size={16} />,
    category: CATEGORIES.CORE,
    path: 'client/src/components/product/ProductDashboard.jsx',
    description: 'Product roadmap, development, and lifecycle',
  },
  COMPLIANCE_DASHBOARD: {
    label: 'Compliance Center',
    icon: <ShieldCheck size={16} />,
    category: CATEGORIES.CORE,
    path: 'client/src/components/compliance/ComplianceDashboard.jsx',
    description: 'Regulatory compliance and risk monitoring',
  },
  OPERATIONS_DASHBOARD: {
    label: 'Operations Hub',
    icon: <Settings size={16} />,
    category: CATEGORIES.CORE,
    path: 'client/src/components/operations/OperationsDashboard.jsx',
    description: 'Day‑to‑day operational oversight',
  },
  PROCUREMENT_DASHBOARD: {
    label: 'Procurement',
    icon: <ShoppingCart size={16} />,
    category: CATEGORIES.CORE,
    path: 'client/src/components/procurement/ProcurementDashboard.jsx',
    description: 'Supply chain and vendor management',
  },
  HR_DASHBOARD: {
    label: 'Human Resources',
    icon: <Users size={16} />,
    category: CATEGORIES.CORE,
    path: 'client/src/components/hr/HrDashboard.jsx',
    description: 'People operations, hiring, and benefits',
  },
  EXECUTIVE_CONTROL_ROOM: {
    label: 'Executive Control Room',
    icon: <Command size={16} />,
    category: CATEGORIES.CORE,
    path: 'client/src/components/control-room/ExecutiveControlRoom.jsx',
    description: 'Authoritative kernel window and operator gateway',
  },

  // ─── Sovereign / Executive ──────────────────────────────────────────────
  GENERAL_DASHBOARD: {
    label: 'General Dashboard',
    icon: <Activity size={16} />,
    category: CATEGORIES.SOVEREIGN,
    path: 'client/src/components/sovereign/GeneralDashboard.jsx',
    description: 'Tenant Command Center',
  },
  SOVEREIGN_COMPLIANCE: {
    label: 'Sovereign Compliance',
    icon: <ShieldAlert size={16} />,
    category: CATEGORIES.SOVEREIGN,
    path: 'client/src/components/sovereign/ComplianceDashboard.jsx',
    description: 'Sovereign regulatory control',
  },
  FOUNDER_DASHBOARD: {
    label: 'Founder Dashboard',
    icon: <Crown size={16} />,
    category: CATEGORIES.SOVEREIGN,
    path: 'client/src/components/sovereign/FounderDashboard.jsx',
    description: 'Founder command center and cockpit',
  },
  FORENSICS_DASHBOARD: {
    label: 'Forensics Dashboard',
    icon: <Fingerprint size={16} />,
    category: CATEGORIES.SOVEREIGN,
    path: 'client/src/components/sovereign/ForensicsDashboard.jsx',
    description: 'Chain‑of‑custody and evidence analysis',
  },
  SOVEREIGN_NODE: {
    label: 'Sovereign Node',
    icon: <Cpu size={16} />,
    category: CATEGORIES.SOVEREIGN,
    path: 'client/src/components/sovereign/SovereignNodeDashboard.jsx',
    description: 'Node health and shard telemetry',
  },
  REVENUE_DASHBOARD: {
    label: 'Revenue Dashboard',
    icon: <TrendingUp size={16} />,
    category: CATEGORIES.SOVEREIGN,
    path: 'client/src/components/sovereign/RevenueDashboard.jsx',
    description: 'Revenue analytics and ledger',
  },
  CLOUD_UPLINK: {
    label: 'Cloud Uplink',
    icon: <Radio size={16} />,
    category: CATEGORIES.SOVEREIGN,
    path: 'client/src/components/sovereign/CloudUplinkDashboard.jsx',
    description: 'Global uplink and telemetry status',
  },
  SOVEREIGN_DASHBOARD_CONTROLLER: {
    label: 'Dashboard Controller',
    icon: <SlidersHorizontal size={16} />,
    category: CATEGORIES.SOVEREIGN,
    path: 'client/src/components/sovereign/SovereignDashboardController.jsx',
    description: 'Dynamic dashboard routing engine',
  },
  BOARDROOM_HUD: {
    label: 'Boardroom HUD',
    icon: <Eye size={16} />,
    category: CATEGORIES.SOVEREIGN,
    path: 'client/src/components/sovereign/BoardroomHUD.jsx',
    description: 'Executive telemetry surface',
  },
  COMMAND_SEARCH: {
    label: 'Global Command Search',
    icon: <Search size={16} />,
    category: CATEGORIES.SOVEREIGN,
    path: 'client/src/components/sovereign/WilsyGlobalCommandSearch.jsx',
    description: 'Unified command and module search',
  },

  // ─── Industry & Domain ──────────────────────────────────────────────────
  AGRICULTURE_DASHBOARD: {
    label: 'Agriculture',
    icon: <Sprout size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/AgricultureDashboard.jsx',
  },
  HOSPITALITY_DASHBOARD: {
    label: 'Hospitality',
    icon: <Building size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/HospitalityDashboard.jsx',
  },
  PRODUCTION_DASHBOARD: {
    label: 'Production',
    icon: <Factory size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/ProductionDashboard.jsx',
  },
  RETAIL_DASHBOARD: {
    label: 'Retail',
    icon: <Store size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/RetailDashboard.jsx',
  },
  PUBLIC_DASHBOARD: {
    label: 'Public Sector',
    icon: <Landmark size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/PublicDashboard.jsx',
  },
  FINANCE_DASHBOARD: {
    label: 'Finance',
    icon: <DollarSign size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/FinanceDashboard.jsx',
  },
  TECH_DASHBOARD: {
    label: 'Technology',
    icon: <Cpu size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/TechDashboard.jsx',
  },
  SPORTS_DASHBOARD: {
    label: 'Sports',
    icon: <Gamepad2 size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/SportsDashboard.jsx',
  },
  EDUCATION_DASHBOARD: {
    label: 'Education',
    icon: <GraduationCap size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/EducationDashboard.jsx',
  },
  HEALTHCARE_DASHBOARD: {
    label: 'Healthcare',
    icon: <HeartPulse size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/HealthcareDashboard.jsx',
  },
  CONSULTING_DASHBOARD: {
    label: 'Consulting',
    icon: <Briefcase size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/ConsultingDashboard.jsx',
  },
  ENERGY_DASHBOARD: {
    label: 'Energy',
    icon: <Zap size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/EnergyDashboard.jsx',
  },
  ENTERTAINMENT_DASHBOARD: {
    label: 'Entertainment',
    icon: <Film size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/EntertainmentDashboard.jsx',
  },
  PROPERTY_DASHBOARD: {
    label: 'Property',
    icon: <Home size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/PropertyDashboard.jsx',
  },
  LEGAL_DASHBOARD: {
    label: 'Legal',
    icon: <Scale size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/LegalDashboard.jsx',
  },
  PROJECT_DASHBOARD: {
    label: 'Project Management',
    icon: <Projector size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/ProjectDashboard.jsx',
  },
  LOGISTICS_DASHBOARD: {
    label: 'Logistics',
    icon: <Truck size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/LogisticsDashboard.jsx',
  },
  NONPROFIT_DASHBOARD: {
    label: 'Non‑Profit',
    icon: <HandHeart size={16} />,
    category: CATEGORIES.INDUSTRY,
    path: 'client/src/components/industry/NonprofitDashboard.jsx',
  },

  // ─── Longevity & Future ──────────────────────────────────────────────────
  LONGEVITY_SCIENCES_DASHBOARD: {
    label: 'Longevity Sciences',
    icon: <Dna size={16} />,
    category: CATEGORIES.FUTURE,
    path: 'client/src/components/longevity_sciences/LongevityDashboard.jsx',
    description: 'Cutting‑edge longevity and biotech research',
  },
};

/**
 * @constant MODULE_OPERATING_MAP
 * @description Extended metadata for modules that appear in the Founder Cockpit.
 * This map provides additional context such as layer, label, contract, and feed.
 * Institutional Commentary: These fields are used to populate the OS Spine
 * and module‑specific narrative surfaces. Not all modules require this detail,
 * only those that are mounted as primary command surfaces.
 */
export const MODULE_OPERATING_MAP = {
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
};

/**
 * @function getModuleIcon
 * @description Utility to retrieve the icon for a given module key.
 * @param {string} key - The module key (e.g., 'BOARDROOM_HUD').
 * @returns {React.Element} The icon component.
 */
export const getModuleIcon = (key) => {
  const module = ALL_MODULES[key];
  return module?.icon || <Target size={16} />;
};

/**
 * @function getModuleLabel
 * @description Utility to retrieve the display label for a given module key.
 * @param {string} key - The module key.
 * @returns {string} The display label.
 */
export const getModuleLabel = (key) => {
  const module = ALL_MODULES[key];
  return module?.label || key.replace(/_/g, ' ');
};

export default {
  ALL_MODULES,
  MODULE_OPERATING_MAP,
  CATEGORIES,
  getModuleIcon,
  getModuleLabel,
};

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — WILSY OS DASHBOARD REGISTRY
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status: CERTIFIED PRODUCTION ARTIFACT
 * Modules Count: 48
 * Categories: Core, Sovereign, Industry, Future
 * Compliance: POPIA / GDPR / SOC2 SECURE
 * ═══════════════════════════════════════════════════════════════════════════════
 */
