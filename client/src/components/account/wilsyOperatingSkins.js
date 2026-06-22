/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - OPERATING SKIN REGISTRY [V2.1.0-FORTUNE-500-CONTROL-PLANE]                                                       ║
 * ║ EXECUTIVE | CRM | LEGAL | FINANCE | HR | CONSTRUCTION | SECURITY | DOCUMENTS | INDUSTRIES | ACCESSIBILITY             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/account/wilsyOperatingSkins.js             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION                                                                                                          ║
 * ║ 1. Wilson Khanyezi - Mandated an operating-system-grade theme registry that can scale to millions of tenants.          ║
 * ║ 2. AI Engineering - Extracted skins from the Account Command Center into governed semantic registry contracts.          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Production operating skin registry for Wilsy OS.
 * Each skin is a semantic operating contract, not a decorative color preset.
 */

export const WILSY_OPERATING_SKINS_VERSION = 'V2.1.0-FORTUNE-500-CONTROL-PLANE';

export const WILSY_OPERATING_SKIN_CATEGORIES = Object.freeze({
  core: 'Core Executive',
  department: 'Operational Department',
  industry: 'Industry Tenant',
  accessibility: 'Accessibility and Environment'
});

export const DEFAULT_OPERATING_SKINS = Object.freeze([
  {
    id: 'wilsy_aurora',
    label: 'Wilsy Sovereign Aurora',
    shortLabel: 'Aurora',
    category: 'core',
    doctrine: 'Flagship command skin. Black authority, cobalt trust, cyan intelligence, mint live-state and gold command.',
    bestFor: 'Executive cockpit',
    accent: '#d4af37',
    secondary: '#2436a4',
    highlight: '#17bdf2',
    live: '#84f0c8',
    textOnAccent: '#020306',
    background: '#020306',
    modes: {
      day: { canvas: '#f6f8ff', panel: '#ffffff', card: '#eef3ff', rail: 'rgba(255,255,255,0.92)', brightText: '#10182b', softText: '#53617f', mutedText: '#6f7a96', overlay: 'rgba(222,227,244,0.58)' },
      night: { canvas: '#020306', panel: '#05070d', card: '#080c18', rail: 'rgba(3,5,10,0.96)', brightText: '#fffaf0', softText: '#c5cce5', mutedText: '#7c86a8', overlay: 'rgba(2,3,6,0.78)' }
    }
  },
  {
    id: 'sovereign_black',
    label: 'Sovereign Black',
    shortLabel: 'Black',
    category: 'core',
    doctrine: 'Boardroom authority. Minimal black, white and gold for investor-grade executive control.',
    bestFor: 'Boardroom mode',
    accent: '#d4af37',
    secondary: '#050505',
    highlight: '#fffaf0',
    live: '#d4af37',
    textOnAccent: '#020306',
    background: '#000000',
    modes: {
      day: { canvas: '#f3f1ea', panel: '#fffaf0', card: '#f7f2e6', rail: 'rgba(255,250,240,0.92)', brightText: '#16120a', softText: '#5f5643', mutedText: '#80735b', overlay: 'rgba(235,229,214,0.62)' },
      night: { canvas: '#000000', panel: '#050505', card: '#0b0b0b', rail: 'rgba(0,0,0,0.94)', brightText: '#ffffff', softText: '#cfc6a9', mutedText: '#8d846d', overlay: 'rgba(0,0,0,0.82)' }
    }
  },
  {
    id: 'cobalt_glass',
    label: 'Cobalt Glass',
    shortLabel: 'Cobalt',
    category: 'core',
    doctrine: 'Executive SaaS trust. Cobalt glass, ice blue and clean command depth without ordinary SaaS softness.',
    bestFor: 'Daily operations',
    accent: '#17bdf2',
    secondary: '#3957ff',
    highlight: '#d8f7ff',
    live: '#7ff0c8',
    textOnAccent: '#020306',
    background: '#061026',
    modes: {
      day: { canvas: '#edf5ff', panel: '#ffffff', card: '#e7f1ff', rail: 'rgba(255,255,255,0.9)', brightText: '#07142c', softText: '#385070', mutedText: '#62718a', overlay: 'rgba(219,236,255,0.62)' },
      night: { canvas: '#020817', panel: '#061026', card: '#0b1a38', rail: 'rgba(3,10,27,0.94)', brightText: '#f3f8ff', softText: '#afc7f6', mutedText: '#7891c2', overlay: 'rgba(2,8,23,0.82)' }
    }
  },
  {
    id: 'pearl_command',
    label: 'Pearl Command',
    shortLabel: 'Pearl',
    category: 'core',
    doctrine: 'Pearl clarity, cobalt structure and gold authority actions. Mode is controlled by Day/Night, never forced by skin.',
    bestFor: 'Day mode and presentations',
    accent: '#c49a18',
    secondary: '#2436a4',
    highlight: '#17bdf2',
    live: '#0f9f6e',
    textOnAccent: '#020306',
    background: '#f7f8fb',
    modes: {
      day: { canvas: '#f7f8fb', panel: '#ffffff', card: '#f1f4fb', rail: 'rgba(255,255,255,0.94)', brightText: '#111827', softText: '#53617f', mutedText: '#74809a', overlay: 'rgba(235,240,250,0.64)' },
      night: { canvas: '#080a12', panel: '#0f1420', card: '#151b2a', rail: 'rgba(8,10,18,0.94)', brightText: '#f7f8fb', softText: '#c6d0e8', mutedText: '#8a96b3', overlay: 'rgba(5,7,12,0.8)' }
    }
  },
  {
    id: 'legacy_gold',
    label: 'Legacy Gold',
    shortLabel: 'Gold',
    category: 'core',
    doctrine: 'Founder wealth skin. Black, ivory and gold for high-trust governance moments.',
    bestFor: 'Founder review',
    accent: '#d4af37',
    secondary: '#080604',
    highlight: '#fff1a8',
    live: '#f6d76b',
    textOnAccent: '#020306',
    background: '#080604',
    modes: {
      day: { canvas: '#f6efda', panel: '#fffaf0', card: '#f2e6bf', rail: 'rgba(255,250,240,0.92)', brightText: '#1d1608', softText: '#6a5a2c', mutedText: '#88794a', overlay: 'rgba(241,229,197,0.62)' },
      night: { canvas: '#070602', panel: '#0d0a03', card: '#141006', rail: 'rgba(7,6,2,0.95)', brightText: '#fff8dc', softText: '#b9a56d', mutedText: '#867545', overlay: 'rgba(7,6,2,0.82)' }
    }
  },
  {
    id: 'forensic_violet',
    label: 'Forensic Violet',
    shortLabel: 'Forensic',
    category: 'department',
    doctrine: 'Audit and investigation skin. Violet traceability for compliance, security and evidence workflows.',
    bestFor: 'Security review',
    accent: '#a85bff',
    secondary: '#09040f',
    highlight: '#f39dff',
    live: '#d8b4fe',
    textOnAccent: '#fffaf0',
    background: '#09040f',
    modes: {
      day: { canvas: '#faf5ff', panel: '#ffffff', card: '#f2e8ff', rail: 'rgba(255,255,255,0.92)', brightText: '#21122f', softText: '#604a77', mutedText: '#806a96', overlay: 'rgba(240,228,255,0.62)' },
      night: { canvas: '#05020a', panel: '#0d0718', card: '#140b26', rail: 'rgba(9,4,18,0.94)', brightText: '#fff7ff', softText: '#cab8ea', mutedText: '#917aae', overlay: 'rgba(5,2,10,0.82)' }
    }
  },
  {
    id: 'quantum_blue',
    label: 'Quantum Blue',
    shortLabel: 'Quantum',
    category: 'department',
    doctrine: 'Data intelligence skin. Blue and cyan signals for analytics, forecasting and intelligence surfaces.',
    bestFor: 'Analytics',
    accent: '#61a8ff',
    secondary: '#020817',
    highlight: '#16c7f3',
    live: '#a9e8ff',
    textOnAccent: '#020306',
    background: '#020817',
    modes: {
      day: { canvas: '#eff8ff', panel: '#ffffff', card: '#e4f4ff', rail: 'rgba(255,255,255,0.92)', brightText: '#071427', softText: '#426079', mutedText: '#6a8196', overlay: 'rgba(223,242,255,0.62)' },
      night: { canvas: '#01050a', panel: '#06111a', card: '#071c25', rail: 'rgba(3,16,24,0.95)', brightText: '#f5ffff', softText: '#9fd7e7', mutedText: '#6ca7b7', overlay: 'rgba(1,5,10,0.82)' }
    }
  },
  {
    id: 'crm_revenue_pulse',
    label: 'CRM Revenue Pulse',
    shortLabel: 'Revenue',
    category: 'department',
    doctrine: 'Customer command skin for pipeline, account growth, leads, retention and revenue movement.',
    bestFor: 'CRM vertical',
    accent: '#22c55e',
    secondary: '#0f172a',
    highlight: '#38bdf8',
    live: '#86efac',
    textOnAccent: '#03120a',
    background: '#030712',
    modes: {
      day: { canvas: '#f0fdf4', panel: '#ffffff', card: '#e9fbeF', rail: 'rgba(255,255,255,0.92)', brightText: '#092013', softText: '#3f6b4e', mutedText: '#60806a', overlay: 'rgba(225,248,232,0.62)' },
      night: { canvas: '#020805', panel: '#04130b', card: '#092416', rail: 'rgba(2,8,5,0.94)', brightText: '#f0fff4', softText: '#a7f3c4', mutedText: '#76b98f', overlay: 'rgba(2,8,5,0.82)' }
    }
  },
  {
    id: 'legal_evidence_noir',
    label: 'Legal Evidence Noir',
    shortLabel: 'Legal',
    category: 'department',
    doctrine: 'Legal and compliance authority with evidence contrast, case-grade hierarchy and proof readability.',
    bestFor: 'Legal vertical',
    accent: '#eab308',
    secondary: '#111827',
    highlight: '#f97316',
    live: '#fde68a',
    textOnAccent: '#140b02',
    background: '#030303',
    modes: {
      day: { canvas: '#fffbeb', panel: '#ffffff', card: '#fff7d6', rail: 'rgba(255,255,255,0.93)', brightText: '#241a06', softText: '#6b5a28', mutedText: '#8b7a4d', overlay: 'rgba(251,243,212,0.62)' },
      night: { canvas: '#030303', panel: '#0a0a0a', card: '#12100b', rail: 'rgba(3,3,3,0.95)', brightText: '#fff7db', softText: '#d8c58b', mutedText: '#998b66', overlay: 'rgba(3,3,3,0.84)' }
    }
  },
  {
    id: 'finance_ledger_green',
    label: 'Finance Ledger Green',
    shortLabel: 'Ledger',
    category: 'department',
    doctrine: 'Finance command skin for ledger truth, cash flow, controls, invoice proof and auditability.',
    bestFor: 'Finance and billing',
    accent: '#10b981',
    secondary: '#052e1b',
    highlight: '#facc15',
    live: '#34d399',
    textOnAccent: '#00140c',
    background: '#02130b',
    modes: {
      day: { canvas: '#ecfdf5', panel: '#ffffff', card: '#dcfce7', rail: 'rgba(255,255,255,0.92)', brightText: '#052e1b', softText: '#3b6f54', mutedText: '#5e826e', overlay: 'rgba(221,252,231,0.62)' },
      night: { canvas: '#01130a', panel: '#052e1b', card: '#064e2c', rail: 'rgba(1,19,10,0.94)', brightText: '#ecfdf5', softText: '#a7f3d0', mutedText: '#6bbf95', overlay: 'rgba(1,19,10,0.82)' }
    }
  },
  {
    id: 'hr_people_graph',
    label: 'HR People Graph',
    shortLabel: 'People',
    category: 'department',
    doctrine: 'Human capital skin for teams, onboarding, wellbeing, performance and employee operations.',
    bestFor: 'HR vertical',
    accent: '#ec4899',
    secondary: '#4c1d95',
    highlight: '#f9a8d4',
    live: '#c4b5fd',
    textOnAccent: '#fffaf0',
    background: '#12071c',
    modes: {
      day: { canvas: '#fdf2f8', panel: '#ffffff', card: '#fce7f3', rail: 'rgba(255,255,255,0.92)', brightText: '#321225', softText: '#7a3d62', mutedText: '#9a6580', overlay: 'rgba(251,231,243,0.62)' },
      night: { canvas: '#0b0410', panel: '#12071c', card: '#241032', rail: 'rgba(11,4,16,0.94)', brightText: '#fff7fb', softText: '#fbcfe8', mutedText: '#c084a7', overlay: 'rgba(11,4,16,0.82)' }
    }
  },
  {
    id: 'construction_command',
    label: 'Construction Command',
    shortLabel: 'Build',
    category: 'department',
    doctrine: 'Field command skin for project controls, EVM, crews, plant, milestones and site risk.',
    bestFor: 'Construction intelligence',
    accent: '#f59e0b',
    secondary: '#1f2937',
    highlight: '#f97316',
    live: '#fde68a',
    textOnAccent: '#140b02',
    background: '#111827',
    modes: {
      day: { canvas: '#fffbeb', panel: '#ffffff', card: '#fff4d6', rail: 'rgba(255,255,255,0.92)', brightText: '#251506', softText: '#70502a', mutedText: '#90704a', overlay: 'rgba(253,239,200,0.62)' },
      night: { canvas: '#080b10', panel: '#111827', card: '#1f2937', rail: 'rgba(8,11,16,0.95)', brightText: '#fff7e6', softText: '#fcd58f', mutedText: '#b8955d', overlay: 'rgba(8,11,16,0.82)' }
    }
  },
  {
    id: 'security_red_team',
    label: 'Security Red Team',
    shortLabel: 'Red Team',
    category: 'department',
    doctrine: 'Security operations skin for incidents, threats, sessions, privileged access and containment.',
    bestFor: 'Security operations',
    accent: '#ef4444',
    secondary: '#111827',
    highlight: '#fb7185',
    live: '#fca5a5',
    textOnAccent: '#fffafa',
    background: '#090909',
    modes: {
      day: { canvas: '#fff1f2', panel: '#ffffff', card: '#ffe4e6', rail: 'rgba(255,255,255,0.92)', brightText: '#3a0b0b', softText: '#7f3a3a', mutedText: '#9f6666', overlay: 'rgba(255,228,230,0.62)' },
      night: { canvas: '#090909', panel: '#130707', card: '#260b0b', rail: 'rgba(9,9,9,0.95)', brightText: '#fff5f5', softText: '#fecaca', mutedText: '#c68080', overlay: 'rgba(9,9,9,0.84)' }
    }
  },
  {
    id: 'document_vault_steel',
    label: 'Document Vault Steel',
    shortLabel: 'Vault',
    category: 'department',
    doctrine: 'Document intelligence skin for contracts, evidence, versions, signatures, vaults and retention.',
    bestFor: 'Document vault',
    accent: '#94a3b8',
    secondary: '#0f172a',
    highlight: '#38bdf8',
    live: '#cbd5e1',
    textOnAccent: '#020306',
    background: '#020617',
    modes: {
      day: { canvas: '#f8fafc', panel: '#ffffff', card: '#edf2f7', rail: 'rgba(255,255,255,0.92)', brightText: '#0f172a', softText: '#475569', mutedText: '#64748b', overlay: 'rgba(226,232,240,0.62)' },
      night: { canvas: '#020617', panel: '#0f172a', card: '#111c32', rail: 'rgba(2,6,23,0.95)', brightText: '#f8fafc', softText: '#cbd5e1', mutedText: '#94a3b8', overlay: 'rgba(2,6,23,0.84)' }
    }
  },
  {
    id: 'banking_trust',
    label: 'Banking Trust',
    shortLabel: 'Banking',
    category: 'industry',
    doctrine: 'Regulated financial trust skin for banking, wealth, lending, risk, treasury and board control.',
    bestFor: 'Financial services tenants',
    accent: '#0ea5e9',
    secondary: '#082f49',
    highlight: '#fbbf24',
    live: '#67e8f9',
    textOnAccent: '#00111a',
    background: '#03121f',
    modes: {
      day: { canvas: '#f0f9ff', panel: '#ffffff', card: '#e0f2fe', rail: 'rgba(255,255,255,0.92)', brightText: '#082f49', softText: '#315d76', mutedText: '#5e7c91', overlay: 'rgba(224,242,254,0.62)' },
      night: { canvas: '#03121f', panel: '#082f49', card: '#0b3d5e', rail: 'rgba(3,18,31,0.95)', brightText: '#f0f9ff', softText: '#bae6fd', mutedText: '#7fb8d6', overlay: 'rgba(3,18,31,0.84)' }
    }
  },
  {
    id: 'law_firm_authority',
    label: 'Law Firm Authority',
    shortLabel: 'Law',
    category: 'industry',
    doctrine: 'Prestige legal skin for matters, clients, evidence, litigation, opinions and compliance proof.',
    bestFor: 'Legal services tenants',
    accent: '#b45309',
    secondary: '#1c1917',
    highlight: '#fcd34d',
    live: '#fed7aa',
    textOnAccent: '#120805',
    background: '#0c0a09',
    modes: {
      day: { canvas: '#fffbeb', panel: '#ffffff', card: '#fef3c7', rail: 'rgba(255,255,255,0.92)', brightText: '#23160a', softText: '#6b4d2c', mutedText: '#8a6a47', overlay: 'rgba(254,243,199,0.62)' },
      night: { canvas: '#0c0a09', panel: '#1c1917', card: '#292524', rail: 'rgba(12,10,9,0.95)', brightText: '#fff7ed', softText: '#fed7aa', mutedText: '#caa37b', overlay: 'rgba(12,10,9,0.84)' }
    }
  },
  {
    id: 'healthcare_calm',
    label: 'Healthcare Calm',
    shortLabel: 'Health',
    category: 'industry',
    doctrine: 'Clinical clarity skin for healthcare records, care operations, privacy, safety and service confidence.',
    bestFor: 'Healthcare tenants',
    accent: '#14b8a6',
    secondary: '#134e4a',
    highlight: '#99f6e4',
    live: '#5eead4',
    textOnAccent: '#00201c',
    background: '#042f2e',
    modes: {
      day: { canvas: '#f0fdfa', panel: '#ffffff', card: '#ccfbf1', rail: 'rgba(255,255,255,0.92)', brightText: '#12312f', softText: '#3e6863', mutedText: '#64847f', overlay: 'rgba(204,251,241,0.62)' },
      night: { canvas: '#021817', panel: '#042f2e', card: '#134e4a', rail: 'rgba(2,24,23,0.95)', brightText: '#f0fdfa', softText: '#99f6e4', mutedText: '#68b8ad', overlay: 'rgba(2,24,23,0.84)' }
    }
  },
  {
    id: 'logistics_command',
    label: 'Logistics Command',
    shortLabel: 'Logistics',
    category: 'industry',
    doctrine: 'Movement and control skin for fleet, routes, delivery, warehouse, procurement and SLA execution.',
    bestFor: 'Logistics tenants',
    accent: '#f97316',
    secondary: '#1e293b',
    highlight: '#38bdf8',
    live: '#fb923c',
    textOnAccent: '#140802',
    background: '#0f172a',
    modes: {
      day: { canvas: '#fff7ed', panel: '#ffffff', card: '#ffedd5', rail: 'rgba(255,255,255,0.92)', brightText: '#251206', softText: '#755238', mutedText: '#95745c', overlay: 'rgba(255,237,213,0.62)' },
      night: { canvas: '#070d18', panel: '#0f172a', card: '#1e293b', rail: 'rgba(7,13,24,0.95)', brightText: '#fff7ed', softText: '#fed7aa', mutedText: '#c18b68', overlay: 'rgba(7,13,24,0.84)' }
    }
  },
  {
    id: 'real_estate_prestige',
    label: 'Real Estate Prestige',
    shortLabel: 'Estate',
    category: 'industry',
    doctrine: 'Portfolio-grade prestige skin for properties, tenants, leases, valuations and investor trust.',
    bestFor: 'Real estate tenants',
    accent: '#a16207',
    secondary: '#312e81',
    highlight: '#fde68a',
    live: '#d9f99d',
    textOnAccent: '#160d02',
    background: '#111827',
    modes: {
      day: { canvas: '#fefce8', panel: '#ffffff', card: '#fef3c7', rail: 'rgba(255,255,255,0.92)', brightText: '#252008', softText: '#6e6135', mutedText: '#8a7b55', overlay: 'rgba(254,243,199,0.62)' },
      night: { canvas: '#080b16', panel: '#111827', card: '#1f2550', rail: 'rgba(8,11,22,0.95)', brightText: '#fff8dc', softText: '#fde68a', mutedText: '#c7ae63', overlay: 'rgba(8,11,22,0.84)' }
    }
  },
  {
    id: 'government_civic',
    label: 'Government Civic',
    shortLabel: 'Civic',
    category: 'industry',
    doctrine: 'Public-sector skin for civic services, compliance, transparency, service delivery and institutional trust.',
    bestFor: 'Government tenants',
    accent: '#2563eb',
    secondary: '#1e3a8a',
    highlight: '#facc15',
    live: '#93c5fd',
    textOnAccent: '#ffffff',
    background: '#0f172a',
    modes: {
      day: { canvas: '#eff6ff', panel: '#ffffff', card: '#dbeafe', rail: 'rgba(255,255,255,0.92)', brightText: '#10213f', softText: '#405b86', mutedText: '#6680a3', overlay: 'rgba(219,234,254,0.62)' },
      night: { canvas: '#071022', panel: '#0f172a', card: '#1e3a8a', rail: 'rgba(7,16,34,0.95)', brightText: '#eff6ff', softText: '#bfdbfe', mutedText: '#86a6d4', overlay: 'rgba(7,16,34,0.84)' }
    }
  },
  {
    id: 'startup_velocity',
    label: 'Startup Velocity',
    shortLabel: 'Velocity',
    category: 'industry',
    doctrine: 'Fast-growth skin for product velocity, growth, funding, burn, customers and daily execution.',
    bestFor: 'Startup tenants',
    accent: '#8b5cf6',
    secondary: '#0f172a',
    highlight: '#22d3ee',
    live: '#a7f3d0',
    textOnAccent: '#fffaf0',
    background: '#020617',
    modes: {
      day: { canvas: '#f5f3ff', panel: '#ffffff', card: '#ede9fe', rail: 'rgba(255,255,255,0.92)', brightText: '#21133f', softText: '#594a80', mutedText: '#766a96', overlay: 'rgba(237,233,254,0.62)' },
      night: { canvas: '#020617', panel: '#0f172a', card: '#1e1b4b', rail: 'rgba(2,6,23,0.95)', brightText: '#f5f3ff', softText: '#c4b5fd', mutedText: '#8f80c6', overlay: 'rgba(2,6,23,0.84)' }
    }
  },
  {
    id: 'high_contrast_sovereign',
    label: 'High Contrast Sovereign',
    shortLabel: 'Contrast',
    category: 'accessibility',
    doctrine: 'Accessibility-first high contrast skin for maximum readability, clarity and low ambiguity.',
    bestFor: 'Accessibility',
    accent: '#ffff00',
    secondary: '#000000',
    highlight: '#ffffff',
    live: '#00ff99',
    textOnAccent: '#000000',
    background: '#000000',
    modes: {
      day: { canvas: '#ffffff', panel: '#ffffff', card: '#f2f2f2', rail: '#ffffff', brightText: '#000000', softText: '#111111', mutedText: '#333333', overlay: 'rgba(255,255,255,0.72)' },
      night: { canvas: '#000000', panel: '#000000', card: '#080808', rail: '#000000', brightText: '#ffffff', softText: '#ffffff', mutedText: '#cccccc', overlay: 'rgba(0,0,0,0.88)' }
    }
  },
  {
    id: 'low_light_ops',
    label: 'Low Light Ops',
    shortLabel: 'Low Light',
    category: 'accessibility',
    doctrine: 'Reduced glare skin for night operators, control rooms and long-session command work.',
    bestFor: 'Low light environments',
    accent: '#84f0c8',
    secondary: '#111827',
    highlight: '#60a5fa',
    live: '#86efac',
    textOnAccent: '#00120d',
    background: '#010409',
    modes: {
      day: { canvas: '#eef6f3', panel: '#f9fffc', card: '#e7f4ef', rail: 'rgba(249,255,252,0.92)', brightText: '#0e241c', softText: '#3f6156', mutedText: '#648177', overlay: 'rgba(231,244,239,0.62)' },
      night: { canvas: '#010409', panel: '#030812', card: '#07111f', rail: 'rgba(1,4,9,0.96)', brightText: '#eafff8', softText: '#9ee8d1', mutedText: '#78b49f', overlay: 'rgba(1,4,9,0.86)' }
    }
  },
  {
    id: 'presentation_boardroom',
    label: 'Presentation Boardroom',
    shortLabel: 'Boardroom',
    category: 'accessibility',
    doctrine: 'Projection-safe skin for investor presentations, boardrooms, screenshots and executive demos.',
    bestFor: 'Presentation mode',
    accent: '#d4af37',
    secondary: '#1f2937',
    highlight: '#f8fafc',
    live: '#84f0c8',
    textOnAccent: '#020306',
    background: '#111827',
    modes: {
      day: { canvas: '#f8fafc', panel: '#ffffff', card: '#f1f5f9', rail: 'rgba(255,255,255,0.94)', brightText: '#0f172a', softText: '#475569', mutedText: '#64748b', overlay: 'rgba(241,245,249,0.66)' },
      night: { canvas: '#0b1020', panel: '#111827', card: '#1f2937', rail: 'rgba(11,16,32,0.95)', brightText: '#f8fafc', softText: '#cbd5e1', mutedText: '#94a3b8', overlay: 'rgba(11,16,32,0.84)' }
    }
  },
  {
    id: 'outdoor_field_mode',
    label: 'Outdoor Field Mode',
    shortLabel: 'Field',
    category: 'accessibility',
    doctrine: 'High-legibility field skin for tablets, bright light, site operations and mobile-first command.',
    bestFor: 'Field operations',
    accent: '#f97316',
    secondary: '#0f172a',
    highlight: '#facc15',
    live: '#22c55e',
    textOnAccent: '#160802',
    background: '#fefce8',
    modes: {
      day: { canvas: '#fefce8', panel: '#ffffff', card: '#fef3c7', rail: 'rgba(255,255,255,0.95)', brightText: '#1c1604', softText: '#5e4d1a', mutedText: '#7d6c38', overlay: 'rgba(254,243,199,0.68)' },
      night: { canvas: '#120d03', panel: '#1c1604', card: '#302408', rail: 'rgba(18,13,3,0.95)', brightText: '#fff7d6', softText: '#fde68a', mutedText: '#c4a95c', overlay: 'rgba(18,13,3,0.84)' }
    }
  }
]);



export const WILSY_OPERATING_SKIN_REGISTRY_METADATA = Object.freeze({
  product: 'Wilsy OS',
  registry: 'Operating Skin Control Plane',
  version: WILSY_OPERATING_SKINS_VERSION,
  defaultSkinId: 'wilsy_aurora',
  defaultMode: 'night',
  tenantScaleClass: 'MULTI_TENANT_ENTERPRISE_OS',
  investorMandate: 'Fortune 500 boardroom-grade operating system experience',
  governance: Object.freeze({
    sourceOfTruth: 'client/src/components/account/wilsyOperatingSkins.js',
    tokenEngine: 'client/src/components/account/wilsyAccountThemeTokens.js',
    owner: 'Wilsy OS Account Command Center',
    principle: 'Skin identity and Day/Night mode must remain independent.',
    compatibility: 'Every skin must expose day and night mode palettes.'
  })
});

export const WILSY_OPERATING_SKIN_SURFACES = Object.freeze({
  executive: 'Executive cockpit',
  crm: 'CRM and revenue operations',
  legal: 'Legal, evidence and compliance',
  finance: 'Finance, billing and audit',
  people: 'HR and people operations',
  construction: 'Construction intelligence',
  security: 'Security operations',
  documents: 'Document vault',
  industry: 'Industry tenant defaults',
  accessibility: 'Accessibility and environment modes'
});

export const WILSY_OPERATING_SKIN_QUALITY_GATES = Object.freeze({
  requiredFields: Object.freeze([
    'id',
    'label',
    'shortLabel',
    'category',
    'doctrine',
    'bestFor',
    'accent',
    'secondary',
    'highlight',
    'live',
    'textOnAccent',
    'background',
    'modes'
  ]),
  requiredModes: Object.freeze(['day', 'night']),
  requiredModeFields: Object.freeze([
    'canvas',
    'panel',
    'card',
    'rail',
    'brightText',
    'softText',
    'mutedText',
    'overlay'
  ]),
  minimumRegistrySize: 20
});

export const WILSY_OPERATING_SKIN_ALIAS_MAP = Object.freeze({
  aurora: 'wilsy_aurora',
  sovereign: 'sovereign_black',
  black: 'sovereign_black',
  dark: 'sovereign_black',
  cobalt: 'cobalt_glass',
  pearl: 'pearl_command',
  daybreak: 'pearl_command',
  gold: 'legacy_gold',
  legacy: 'legacy_gold',
  forensic: 'forensic_violet',
  quantum: 'quantum_blue',
  analytics: 'quantum_blue',
  crm: 'crm_revenue_pulse',
  revenue: 'crm_revenue_pulse',
  sales: 'crm_revenue_pulse',
  legal: 'legal_evidence_noir',
  evidence: 'legal_evidence_noir',
  finance: 'finance_ledger_green',
  ledger: 'finance_ledger_green',
  billing: 'finance_ledger_green',
  hr: 'hr_people_graph',
  people: 'hr_people_graph',
  construction: 'construction_command',
  build: 'construction_command',
  security: 'security_red_team',
  redteam: 'security_red_team',
  vault: 'document_vault_steel',
  documents: 'document_vault_steel',
  banking: 'banking_trust',
  law: 'law_firm_authority',
  healthcare: 'healthcare_calm',
  health: 'healthcare_calm',
  logistics: 'logistics_command',
  estate: 'real_estate_prestige',
  realestate: 'real_estate_prestige',
  civic: 'government_civic',
  government: 'government_civic',
  startup: 'startup_velocity',
  velocity: 'startup_velocity',
  contrast: 'high_contrast_sovereign',
  highcontrast: 'high_contrast_sovereign',
  lowlight: 'low_light_ops',
  boardroom: 'presentation_boardroom',
  presentation: 'presentation_boardroom',
  field: 'outdoor_field_mode'
});

export const WILSY_OPERATING_SKIN_ENTERPRISE_MANIFEST = Object.freeze({
  wilsy_aurora: { tier: 'flagship', surfaces: ['executive', 'industry'], buyerSignal: 'boardroom command', tenantDefault: true },
  sovereign_black: { tier: 'flagship', surfaces: ['executive', 'security'], buyerSignal: 'investor authority', tenantDefault: false },
  cobalt_glass: { tier: 'core', surfaces: ['executive', 'crm'], buyerSignal: 'enterprise SaaS trust', tenantDefault: false },
  pearl_command: { tier: 'core', surfaces: ['executive', 'accessibility'], buyerSignal: 'day-mode clarity', tenantDefault: false },
  legacy_gold: { tier: 'founder', surfaces: ['executive'], buyerSignal: 'founder governance', tenantDefault: false },
  forensic_violet: { tier: 'department', surfaces: ['legal', 'security'], buyerSignal: 'audit traceability', tenantDefault: false },
  quantum_blue: { tier: 'department', surfaces: ['executive'], buyerSignal: 'intelligence and analytics', tenantDefault: false },
  crm_revenue_pulse: { tier: 'department', surfaces: ['crm'], buyerSignal: 'revenue growth', tenantDefault: false },
  legal_evidence_noir: { tier: 'department', surfaces: ['legal'], buyerSignal: 'legal proof and compliance', tenantDefault: false },
  finance_ledger_green: { tier: 'department', surfaces: ['finance'], buyerSignal: 'ledger confidence', tenantDefault: false },
  hr_people_graph: { tier: 'department', surfaces: ['people'], buyerSignal: 'people operations', tenantDefault: false },
  construction_command: { tier: 'department', surfaces: ['construction'], buyerSignal: 'project control', tenantDefault: false },
  security_red_team: { tier: 'department', surfaces: ['security'], buyerSignal: 'security readiness', tenantDefault: false },
  document_vault_steel: { tier: 'department', surfaces: ['documents'], buyerSignal: 'document control', tenantDefault: false },
  banking_trust: { tier: 'industry', surfaces: ['finance', 'industry'], buyerSignal: 'regulated trust', tenantDefault: false },
  law_firm_authority: { tier: 'industry', surfaces: ['legal', 'industry'], buyerSignal: 'professional authority', tenantDefault: false },
  healthcare_calm: { tier: 'industry', surfaces: ['industry'], buyerSignal: 'clinical clarity', tenantDefault: false },
  logistics_command: { tier: 'industry', surfaces: ['industry'], buyerSignal: 'movement control', tenantDefault: false },
  real_estate_prestige: { tier: 'industry', surfaces: ['industry'], buyerSignal: 'portfolio prestige', tenantDefault: false },
  government_civic: { tier: 'industry', surfaces: ['industry'], buyerSignal: 'civic trust', tenantDefault: false },
  startup_velocity: { tier: 'industry', surfaces: ['industry'], buyerSignal: 'growth velocity', tenantDefault: false },
  high_contrast_sovereign: { tier: 'accessibility', surfaces: ['accessibility'], buyerSignal: 'readability and inclusion', tenantDefault: false },
  low_light_ops: { tier: 'accessibility', surfaces: ['accessibility', 'security'], buyerSignal: 'low-light endurance', tenantDefault: false },
  presentation_boardroom: { tier: 'accessibility', surfaces: ['executive', 'accessibility'], buyerSignal: 'board presentation', tenantDefault: false },
  outdoor_field_mode: { tier: 'accessibility', surfaces: ['accessibility', 'construction'], buyerSignal: 'field legibility', tenantDefault: false }
});

/**
 * @function normalizeWilsyOperatingSkinLookupKey
 * @description Normalizes theme ids, aliases and tenant-provided labels for registry lookup.
 * @param {string} value - Candidate skin id or alias.
 * @returns {string} Normalized lookup key.
 * @collaboration Allows dashboards, tenants and future backend services to resolve skins without duplicating alias logic.
 */
export const normalizeWilsyOperatingSkinLookupKey = value => String(value || '')
  .trim()
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '_')
  .replace(/^_+|_+$/g, '');

/**
 * @function resolveWilsyOperatingSkinId
 * @description Resolves a skin id or alias to a registered operating skin id.
 * @param {string} value - Candidate skin id or alias.
 * @param {string} fallback - Fallback skin id.
 * @returns {string} Resolved skin id.
 * @collaboration Gives Wilsy OS one tenant-scale theme resolution path across Account, Executive, CRM and future dashboards.
 */
export const resolveWilsyOperatingSkinId = (value, fallback = WILSY_OPERATING_SKIN_REGISTRY_METADATA.defaultSkinId) => {
  const lookupKey = normalizeWilsyOperatingSkinLookupKey(value);
  const directMatch = DEFAULT_OPERATING_SKINS.find(theme => theme.id === lookupKey);
  if (directMatch) return directMatch.id;

  const aliased = WILSY_OPERATING_SKIN_ALIAS_MAP[lookupKey];
  if (aliased && DEFAULT_OPERATING_SKINS.some(theme => theme.id === aliased)) return aliased;

  return DEFAULT_OPERATING_SKINS.some(theme => theme.id === fallback)
    ? fallback
    : WILSY_OPERATING_SKIN_REGISTRY_METADATA.defaultSkinId;
};

/**
 * @function getWilsyOperatingSkinById
 * @description Retrieves a registered operating skin by id or alias.
 * @param {string} value - Candidate skin id or alias.
 * @param {Object} options - Lookup options.
 * @param {string} options.fallback - Fallback skin id.
 * @returns {Object} Registered operating skin.
 * @collaboration Prevents dashboards from hand-rolling their own theme fallback behaviour.
 */
export const getWilsyOperatingSkinById = (value, options = {}) => {
  const resolvedId = resolveWilsyOperatingSkinId(value, options.fallback);
  return DEFAULT_OPERATING_SKINS.find(theme => theme.id === resolvedId) || DEFAULT_OPERATING_SKINS[0];
};

/**
 * @function listWilsyOperatingSkinsByCategory
 * @description Lists operating skins by registry category.
 * @param {string} category - Registry category.
 * @returns {Array<Object>} Matching skins.
 * @collaboration Lets future Account UI, tenant admin and marketplace screens group skins without copying category logic.
 */
export const listWilsyOperatingSkinsByCategory = category => {
  const normalizedCategory = normalizeWilsyOperatingSkinLookupKey(category);
  return DEFAULT_OPERATING_SKINS.filter(theme => normalizeWilsyOperatingSkinLookupKey(theme.category) === normalizedCategory);
};

/**
 * @function listWilsyOperatingSkinsForSurface
 * @description Lists operating skins suitable for a Wilsy OS surface.
 * @param {string} surface - Surface key such as crm, executive or legal.
 * @returns {Array<Object>} Matching skins.
 * @collaboration Prepares Wilsy OS for dashboard-specific defaults while keeping one registry source of truth.
 */
export const listWilsyOperatingSkinsForSurface = surface => {
  const normalizedSurface = normalizeWilsyOperatingSkinLookupKey(surface);
  return DEFAULT_OPERATING_SKINS.filter(theme => (
    WILSY_OPERATING_SKIN_ENTERPRISE_MANIFEST[theme.id]?.surfaces || []
  ).some(candidate => normalizeWilsyOperatingSkinLookupKey(candidate) === normalizedSurface));
};

/**
 * @function buildWilsyOperatingSkinProfile
 * @description Builds the full enterprise profile for a registered operating skin.
 * @param {string} value - Candidate skin id or alias.
 * @returns {Object} Enterprise operating skin profile.
 * @collaboration Combines visual skin metadata, investor signal and tenant-scaling classification in one contract.
 */
export const buildWilsyOperatingSkinProfile = value => {
  const skin = getWilsyOperatingSkinById(value);
  const manifest = WILSY_OPERATING_SKIN_ENTERPRISE_MANIFEST[skin.id] || {};

  return Object.freeze({
    ...skin,
    enterprise: Object.freeze({
      tier: manifest.tier || 'core',
      surfaces: Object.freeze(manifest.surfaces || ['executive']),
      buyerSignal: manifest.buyerSignal || skin.bestFor,
      tenantDefault: Boolean(manifest.tenantDefault),
      registryVersion: WILSY_OPERATING_SKINS_VERSION
    })
  });
};

/**
 * @function validateWilsyOperatingSkin
 * @description Validates one operating skin against the Wilsy OS registry quality gates.
 * @param {Object} skin - Operating skin.
 * @returns {Array<string>} Validation issue list.
 * @collaboration Stops incomplete skins from entering a Fortune-500-grade operating skin registry.
 */
export const validateWilsyOperatingSkin = skin => {
  const issues = [];

  WILSY_OPERATING_SKIN_QUALITY_GATES.requiredFields.forEach(field => {
    if (skin?.[field] === undefined || skin?.[field] === null || skin?.[field] === '') {
      issues.push(`${skin?.id || 'UNKNOWN_SKIN'} missing field ${field}`);
    }
  });

  WILSY_OPERATING_SKIN_QUALITY_GATES.requiredModes.forEach(mode => {
    if (!skin?.modes?.[mode]) {
      issues.push(`${skin?.id || 'UNKNOWN_SKIN'} missing ${mode} mode`);
      return;
    }

    WILSY_OPERATING_SKIN_QUALITY_GATES.requiredModeFields.forEach(field => {
      if (!skin.modes[mode][field]) {
        issues.push(`${skin?.id || 'UNKNOWN_SKIN'} missing ${mode}.${field}`);
      }
    });
  });

  return issues;
};

/**
 * @function assertWilsyOperatingSkinRegistry
 * @description Validates the full operating skin registry.
 * @returns {Object} Registry health object.
 * @collaboration Gives build scripts and future tests a deterministic way to prove the registry is production-ready.
 */
export const assertWilsyOperatingSkinRegistry = () => {
  const ids = DEFAULT_OPERATING_SKINS.map(theme => theme.id);
  const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
  const issues = DEFAULT_OPERATING_SKINS.flatMap(validateWilsyOperatingSkin);

  if (DEFAULT_OPERATING_SKINS.length < WILSY_OPERATING_SKIN_QUALITY_GATES.minimumRegistrySize) {
    issues.push(`registry below minimum size ${WILSY_OPERATING_SKIN_QUALITY_GATES.minimumRegistrySize}`);
  }

  duplicates.forEach(id => issues.push(`duplicate skin id ${id}`));

  return Object.freeze({
    ok: issues.length === 0,
    version: WILSY_OPERATING_SKINS_VERSION,
    count: DEFAULT_OPERATING_SKINS.length,
    categories: Object.freeze(Object.keys(WILSY_OPERATING_SKIN_CATEGORIES)),
    issues: Object.freeze(issues)
  });
};

/**
 * @function buildWilsyTenantOperatingSkinRecommendation
 * @description Recommends an operating skin from tenant industry, module or surface context.
 * @param {Object} tenant - Tenant or dashboard context.
 * @returns {Object} Recommended operating skin profile.
 * @collaboration Prepares Wilsy OS for millions of tenants receiving intelligent defaults without hardcoded dashboard themes.
 */
export const buildWilsyTenantOperatingSkinRecommendation = (tenant = {}) => {
  const source = `${tenant.industry || ''} ${tenant.businessModel || ''} ${tenant.module || ''} ${tenant.surface || ''}`.toLowerCase();

  if (/bank|finance|wealth|treasury|lending/.test(source)) return buildWilsyOperatingSkinProfile('banking_trust');
  if (/law|legal|attorney|case|compliance/.test(source)) return buildWilsyOperatingSkinProfile('law_firm_authority');
  if (/health|clinic|medical|care/.test(source)) return buildWilsyOperatingSkinProfile('healthcare_calm');
  if (/logistics|fleet|warehouse|delivery|procurement/.test(source)) return buildWilsyOperatingSkinProfile('logistics_command');
  if (/real estate|property|lease|portfolio/.test(source)) return buildWilsyOperatingSkinProfile('real_estate_prestige');
  if (/government|civic|public/.test(source)) return buildWilsyOperatingSkinProfile('government_civic');
  if (/startup|saas|growth|venture/.test(source)) return buildWilsyOperatingSkinProfile('startup_velocity');
  if (/construction|project|site|evm/.test(source)) return buildWilsyOperatingSkinProfile('construction_command');
  if (/security|risk|incident|threat/.test(source)) return buildWilsyOperatingSkinProfile('security_red_team');
  if (/document|contract|vault|signature/.test(source)) return buildWilsyOperatingSkinProfile('document_vault_steel');
  if (/crm|sales|revenue|pipeline|customer/.test(source)) return buildWilsyOperatingSkinProfile('crm_revenue_pulse');

  return buildWilsyOperatingSkinProfile(WILSY_OPERATING_SKIN_REGISTRY_METADATA.defaultSkinId);
};

export const WILSY_OPERATING_SKIN_REGISTRY_HEALTH = assertWilsyOperatingSkinRegistry();

export const WILSY_OPERATING_SKIN_IDS = Object.freeze(DEFAULT_OPERATING_SKINS.map(theme => theme.id));

export default DEFAULT_OPERATING_SKINS;
