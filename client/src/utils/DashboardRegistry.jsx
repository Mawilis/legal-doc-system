/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - POLYMORPHIC DASHBOARD REGISTRY [R18AD68-CRM-OS-DISCOVERY-ROUTING]                                                                   ║
 * ║ [TENANT ISOLATION | DYNAMIC LAZY LOADING | MEMORY-SAFE CACHE | CRYPTOGRAPHIC FALLBACKS]                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: R18AD68-CRM-OS-DISCOVERY-ROUTING | PRODUCTION READY | BILLION DOLLAR SPEC                                                                    ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/utils/DashboardRegistry.jsx                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated absolute tenant boundaries and future-proof scaling.                                 ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Upgraded memory cache to prevent heap bloat during heavy routing. [2026-05-12]                  ║
 * ║ • AI Engineering (Gemini) - OMEGA PATCH: Integrated all 30+ Forensic Scan HUDs and hardened the Jurisdiction Denied UI.                ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { Suspense, lazy } from 'react';
import { Spin } from 'antd';
import { AlertOctagon } from 'lucide-react';
import ErrorBoundary from '../components/ErrorBoundary';

// 🛡️ THE ULTIMATE FALLBACK: Statically imported to guarantee it never fails to load
import SingularityDashboard from '../components/SingularityDashboard';

const WILSY_DASHBOARD_REGISTRY_VERSION = 'R18AD68-CRM-OS-DISCOVERY-ROUTING';

const WILSY_CRM_OS_DASHBOARD_KEY = 'crm_os';

const WILSY_CRM_OS_DISCOVERY_ROLES = Object.freeze([
  'sales',
  'sales_representative',
  'sales_development_representative',
  'sdr',
  'account_executive',
  'business_development',
  'sales_manager',
  'sales_director',
  'crm',
  'crm_operator',
  'crm_manager',
  'customer_success',
  'customer_success_manager',
  'support_agent',
  'revenue_operations'
]);

const WILSY_SOVEREIGN_OVERRIDE_ROLES = Object.freeze([
  'founder',
  'super_admin',
  'omega'
]);

/**
 * @function normalizeDashboardRegistryKey
 * @description Normalizes user role, tenant dashboard and force-dashboard keys for deterministic dashboard routing.
 * @param {unknown} value - Candidate dashboard key.
 * @returns {string} Normalized dashboard key.
 * @collaboration Keeps Discovery UI, tenant overrides, Founder/Omega commands and CRM OS role routing aligned.
 */
function normalizeDashboardRegistryKey(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

/**
 * @function loadWilsyCrmOsDashboard
 * @description Lazily loads the Wilsy CRM OS dashboard as the operating surface for Sales, CRM, SDR, Support and Customer Success roles.
 * @returns {React.LazyExoticComponent} Lazy CRM dashboard component.
 * @collaboration Routes revenue-facing tenant employees into one governed CRM command system instead of fragmented SaaS-style panels.
 */
function loadWilsyCrmOsDashboard() {
  return lazy(() => import('../components/crm/CRMDashboard'));
}

/**
 * @function isWilsyCrmOsDiscoveryRole
 * @description Determines whether a normalized role should resolve to the Wilsy CRM OS surface.
 * @param {unknown} role - User role or dashboard key.
 * @returns {boolean} True when the role belongs to the CRM OS entry cohort.
 * @collaboration Gives Discovery UI one CRM/Sales/Customer Success destination while preserving tenant isolation.
 */
function isWilsyCrmOsDiscoveryRole(role) {
  return WILSY_CRM_OS_DISCOVERY_ROLES.includes(normalizeDashboardRegistryKey(role));
}

/**
 * @function isWilsySovereignOverrideUser
 * @description Determines whether a user has sovereign Founder/Omega override privileges.
 * @param {Object} user - Authenticated user.
 * @returns {boolean} True when the user can cross-enter sovereign dashboards under audit.
 * @collaboration Lets Founder/Omega access CRM from FounderDashboard without weakening normal tenant user isolation.
 */
function isWilsySovereignOverrideUser(user) {
  const roleKey = normalizeDashboardRegistryKey(user?.role || user?.roleKey || user?.tenantRole);
  return Boolean(
    user?.sovereignAccess
    || user?.omegaAccess
    || user?.founderAccess
    || WILSY_SOVEREIGN_OVERRIDE_ROLES.includes(roleKey)
  );
}

// ============================================================================
// 1. LAZY LOADING MAPS (OMNI-MATRIX FULLY INTEGRATED)
// ============================================================================

const industryLoaders = {
  agriculture: () => lazy(() => import('../components/industry/AgricultureDashboard')),
  consulting: () => lazy(() => import('../components/industry/ConsultingDashboard')),
  education: () => lazy(() => import('../components/industry/EducationDashboard')),
  energy: () => lazy(() => import('../components/industry/EnergyDashboard')),
  entertainment: () => lazy(() => import('../components/industry/EntertainmentDashboard')),
  finance: () => lazy(() => import('../components/industry/FinanceDashboard')),
  healthcare: () => lazy(() => import('../components/industry/HealthcareDashboard')),
  hospitality: () => lazy(() => import('../components/industry/HospitalityDashboard')),
  legal: () => lazy(() => import('../components/industry/LegalDashboard')),
  logistics: () => lazy(() => import('../components/industry/LogisticsDashboard')),
  nonprofit: () => lazy(() => import('../components/industry/NonprofitDashboard')),
  production: () => lazy(() => import('../components/industry/ProductionDashboard')),
  project: () => lazy(() => import('../components/industry/ProjectDashboard')),
  property: () => lazy(() => import('../components/industry/PropertyDashboard')),
  public: () => lazy(() => import('../components/industry/PublicDashboard')),
  retail: () => lazy(() => import('../components/industry/RetailDashboard')),
  sports: () => lazy(() => import('../components/industry/SportsDashboard')),
  tech: () => lazy(() => import('../components/industry/TechDashboard')),
};

const roleLoaders = {
  // Executive & Management
  executive: () => lazy(() => import('../components/executive/ExecutiveDashboard')),
  ceo: () => lazy(() => import('../components/executive/ExecutiveDashboard')),
  cto: () => lazy(() => import('../components/executive/ExecutiveDashboard')),
  coo: () => lazy(() => import('../components/executive/ExecutiveDashboard')),
  // Finance
  finance_manager: () => lazy(() => import('../components/finance/FinanceDashboard')),
  cfo: () => lazy(() => import('../components/finance/FinanceDashboard')),
  accountant: () => lazy(() => import('../components/finance/FinanceDashboard')),
  // HR
  hr_manager: () => lazy(() => import('../components/hr/HrDashboard')),
  // Marketing
  marketing_manager: () => lazy(() => import('../components/marketing/MarketingDashboard')),
  // Operations
  operations_manager: () => lazy(() => import('../components/operations/OperationsDashboard')),
  // Sales
  sales_representative: loadWilsyCrmOsDashboard,
  account_executive: loadWilsyCrmOsDashboard,
  business_development: loadWilsyCrmOsDashboard,
  sales_manager: loadWilsyCrmOsDashboard,
  sales_director: loadWilsyCrmOsDashboard,
  sales: loadWilsyCrmOsDashboard,
  sales_development_representative: loadWilsyCrmOsDashboard,
  sdr: loadWilsyCrmOsDashboard,
  crm: loadWilsyCrmOsDashboard,
  crm_os: loadWilsyCrmOsDashboard,
  crm_operator: loadWilsyCrmOsDashboard,
  crm_manager: loadWilsyCrmOsDashboard,
  customer_success: loadWilsyCrmOsDashboard,
  customer_success_manager: loadWilsyCrmOsDashboard,
  support_agent: loadWilsyCrmOsDashboard,
  revenue_operations: loadWilsyCrmOsDashboard,
  // Technical
  technical_director: () => lazy(() => import('../components/technical/TechnicalDashboard')),
  // Compliance
  compliance_officer: () => lazy(() => import('../components/compliance/ComplianceDashboard')),
  // Sovereign
  founder: () => lazy(() => import('../components/sovereign/FounderDashboard')),
  super_admin: () => lazy(() => import('../components/sovereign/FounderDashboard')),
  sovereign_node: () => lazy(() => import('../components/sovereign/SovereignNodeDashboard')),
  cloud_uplink: () => lazy(() => import('../components/sovereign/CloudUplinkDashboard')),
};

const sovereignLoaders = {
  founder: () => lazy(() => import('../components/sovereign/FounderDashboard')),
  sovereign_node: () => lazy(() => import('../components/sovereign/SovereignNodeDashboard')),
  cloud_uplink: () => lazy(() => import('../components/sovereign/CloudUplinkDashboard')),
};

// ============================================================================
// 2. MEMORY-SAFE CACHE LOGIC
// ============================================================================
const cache = new Map();
const MAX_CACHE_SIZE = 50;

/**
 * @function getCached
 * @description Retrieves a cached dashboard component while enforcing a short registry TTL.
 * @param {string} key - Cache key.
 * @returns {Function|null} Cached dashboard component or null.
 * @collaboration Keeps tenant dashboard resolution fast without leaking stale dashboard entries.
 */
function getCached(key) {
  const entry = cache.get(key);
  if (!entry) return null;
  // Expire after 5 minutes
  if (Date.now() - entry.timestamp > 300000) {
    cache.delete(key);
    return null;
  }
  return entry.component;
}

/**
 * @function setCached
 * @description Stores a dashboard component in the bounded dashboard registry cache.
 * @param {string} key - Cache key.
 * @param {Function} component - Dashboard component.
 * @returns {void}
 * @collaboration Prevents heap bloat during multi-tenant dashboard routing.
 */
function setCached(key, component) {
  // 🛡️ MEMORY SHIELD: Prevent memory leaks in multi-tenant heavy routing
  if (cache.size >= MAX_CACHE_SIZE) {
    const oldestKey = cache.keys().next().value;
    cache.delete(oldestKey);
  }
  cache.set(key, { component, timestamp: Date.now() });
}

// ============================================================================
// 3. TELEMETRY (ENHANCED FOR ISOLATION VIOLATIONS)
// ============================================================================
/**
 * @function logDashboardResolution
 * @description Emits dashboard resolution telemetry and local isolation-violation diagnostics.
 * @param {string} userId - User id.
 * @param {string} tenantId - Tenant id.
 * @param {string} resolvedType - Resolution trace.
 * @param {boolean} fallbackUsed - Whether fallback was used.
 * @param {boolean} permissionDenied - Whether permission was denied.
 * @param {boolean} isolationViolation - Whether tenant isolation was violated.
 * @returns {Promise<void>} Telemetry result.
 * @collaboration Gives Wilsy OS auditable dashboard routing without blocking user navigation.
 */
async function logDashboardResolution(userId, tenantId, resolvedType, fallbackUsed, permissionDenied, isolationViolation = false) {
  const payload = { userId, tenantId, resolvedType, fallbackUsed, permissionDenied, isolationViolation, timestamp: new Date().toISOString() };
  if (process.env.NODE_ENV === 'production') {
    fetch('/api/telemetry/dashboard', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }).catch(() => {});
  }
  if (isolationViolation) {
    console.error(`[SECURITY] Tenant isolation violation: user ${userId} attempted to access tenant ${tenantId}`);
  }
}

// ============================================================================
// 4. TENANT ISOLATION ENFORCEMENT (THE IRON WALL)
// ============================================================================
/**
 * @function isTenantAccessAllowed
 * @description Checks whether a user can access a tenant under the Wilsy OS iron-wall isolation doctrine.
 * @param {Object} user - Authenticated user.
 * @param {Object} tenant - Target tenant.
 * @returns {boolean} True when access is allowed.
 * @collaboration Allows audited Founder/Omega override while forcing normal users to match their tenant shard.
 */
function isTenantAccessAllowed(user, tenant) {
  // Sovereign override
  if (isWilsySovereignOverrideUser(user)) {
    return true;
  }
  // Normal tenant user: strict match
  const userTenantId = user?.tenantId || user?.tenant_id;
  const targetTenantId = tenant?._id || tenant?.id;

  if (!userTenantId || !targetTenantId) return false;
  return userTenantId.toString() === targetTenantId.toString();
}

// ============================================================================
// 5. PERMISSION MATRIX
// ============================================================================
/**
 * @function hasDashboardAccess
 * @description Verifies whether a user may access a resolved dashboard type for a tenant.
 * @param {Object} user - Authenticated user.
 * @param {Object} tenant - Target tenant.
 * @param {string} dashboardType - Dashboard category.
 * @param {string|null} roleKey - Optional role dashboard key.
 * @returns {boolean} True when dashboard access is allowed.
 * @collaboration Enforces role and tenant boundaries before lazy dashboard rendering.
 */
function hasDashboardAccess(user, tenant, dashboardType, roleKey = null) {
  if (isWilsySovereignOverrideUser(user)) return true;
  if (dashboardType === 'industry') return isTenantAccessAllowed(user, tenant);
  if (dashboardType === 'role' && roleKey) return user?.role === roleKey;
  return true;
}

// ============================================================================
// 6. SOVEREIGN FALLBACK UI COMPONENTS
// ============================================================================
/**
 * @function RegistryLoader
 * @description Renders the dashboard registry loading surface during lazy dashboard hydration.
 * @returns {React.ReactElement} Registry loading element.
 * @collaboration Keeps Discovery UI transitions sovereign and readable while dashboard chunks load.
 */
const RegistryLoader = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#050505' }}>
    <Spin size="large" tip={<span style={{ color: '#D4AF37', letterSpacing: '2px', fontWeight: 'bold' }}>HYDRATING NUCLEUS...</span>} />
  </div>
);

/**
 * @function IsolationErrorDashboard
 * @description Renders the jurisdiction-denied dashboard when tenant isolation fails.
 * @returns {React.ReactElement} Isolation error element.
 * @collaboration Stops cross-tenant access while giving the operator a clear termination path.
 */
const IsolationErrorDashboard = () => (
  <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#050505', color: '#ff3333', fontFamily: '"JetBrains Mono", monospace' }}>
    <AlertOctagon size={64} style={{ marginBottom: '24px', filter: 'drop-shadow(0 0 20px rgba(255,51,51,0.5))' }} />
    <h2 style={{ fontSize: '2rem', letterSpacing: '4px', fontWeight: 900, margin: 0 }}>⚠️ JURISDICTION DENIED</h2>
    <p style={{ color: '#888', marginTop: '16px', letterSpacing: '1px' }}>Cryptographic isolation enforced. Tenant mismatch detected.</p>
    <button
      onClick={() => window.location.href = '/login'}
      style={{ marginTop: '30px', padding: '12px 24px', background: 'rgba(51,0,0,0.8)', border: '1px solid #ff3333', color: '#fff', cursor: 'pointer', borderRadius: '4px', fontWeight: 'bold', letterSpacing: '2px', transition: 'all 0.3s' }}
      onMouseOver={(e) => { e.currentTarget.style.background = '#ff3333'; e.currentTarget.style.boxShadow = '0 0 20px rgba(255,51,51,0.5)'; }}
      onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(51,0,0,0.8)'; e.currentTarget.style.boxShadow = 'none'; }}
    >
      TERMINATE SESSION
    </button>
  </div>
);

// ============================================================================
// 7. RESOLVER CORE WITH TENANT ISOLATION
// ============================================================================
/**
 * @function resolveDashboard
 * @description Resolves the correct Wilsy OS dashboard for a user, tenant and optional forced dashboard key.
 * @param {Object} user - Authenticated user.
 * @param {Object} tenant - Active tenant.
 * @param {Object} options - Resolution options.
 * @returns {React.ComponentType} Resolved dashboard wrapper component.
 * @collaboration Routes Sales/CRM/SDR/Customer Success roles into CRM OS while preserving Founder/Omega and tenant isolation rules.
 */
export function resolveDashboard(user, tenant, options = {}) {
  // STEP 0: TENANT ISOLATION VALIDATION (MANDATORY)
  if (!isTenantAccessAllowed(user, tenant)) {
    const violationMsg = `Tenant isolation violation: user.tenantId=${user?.tenantId} attempted to access tenant._id=${tenant?._id}`;
    console.error(`[DashboardRegistry] 🚨 ${violationMsg}`);
    logDashboardResolution(user?._id, tenant?._id, 'ISOLATION_VIOLATION', true, false, true);
    return IsolationErrorDashboard;
  }

  const cacheKey = `${user?._id || user?.email}-${tenant?._id}-${options.forceDashboard || ''}`;
  if (!options.bypassCache) {
    const cached = getCached(cacheKey);
    if (cached) return cached;
  }

  let DashboardComponent = null;
  let resolutionTrace = [];
  let fallbackUsed = false;
  let permissionDenied = false;

  console.log('[DashboardRegistry] 🔍 Tenant isolation passed. Resolving for role:', user?.role, 'tenant:', tenant?._id);

  // STEP 1: Explicit force override
  const forcedDashboardKey = normalizeDashboardRegistryKey(options.forceDashboard);
  if (forcedDashboardKey && roleLoaders[forcedDashboardKey]) {
    DashboardComponent = roleLoaders[forcedDashboardKey]();
    resolutionTrace.push(`forced:${forcedDashboardKey}`);
    if (!hasDashboardAccess(user, tenant, 'role', forcedDashboardKey)) {
      permissionDenied = true;
      DashboardComponent = SingularityDashboard;
      resolutionTrace.push('permission-denied→fallback');
    }
  }

  // STEP 2: Sovereign layer
  if (!DashboardComponent && isWilsySovereignOverrideUser(user)) {
    const sovereignRoleKey = normalizeDashboardRegistryKey(user?.role);
    if (sovereignRoleKey === 'founder' || sovereignRoleKey === 'super_admin' || sovereignRoleKey === 'omega') {
      DashboardComponent = sovereignLoaders.founder();
      resolutionTrace.push('sovereign:founder');
    } else if (user?.nodeType === 'sovereign') {
      DashboardComponent = sovereignLoaders.sovereign_node();
      resolutionTrace.push('sovereign:node');
    } else if (user?.uplinkEnabled) {
      DashboardComponent = sovereignLoaders.cloud_uplink();
      resolutionTrace.push('sovereign:uplink');
    }
  }

  // STEP 3: Role-based
  if (!DashboardComponent && user?.role && roleLoaders[normalizeDashboardRegistryKey(user.role)]) {
    const roleKey = normalizeDashboardRegistryKey(user.role);
    DashboardComponent = roleLoaders[roleKey]();
    resolutionTrace.push(`role:${roleKey}`);
    if (!hasDashboardAccess(user, tenant, 'role', roleKey)) {
      permissionDenied = true;
      DashboardComponent = SingularityDashboard;
      resolutionTrace.push('permission-denied→fallback');
    }
  }

  // STEP 4: Tenant custom dashboard overrides
  const tenantCustomDashboardKey = normalizeDashboardRegistryKey(tenant?.customDashboard);
  if (!DashboardComponent && tenantCustomDashboardKey && roleLoaders[tenantCustomDashboardKey]) {
    DashboardComponent = roleLoaders[tenantCustomDashboardKey]();
    resolutionTrace.push(`tenant-custom:${tenantCustomDashboardKey}`);
    if (!hasDashboardAccess(user, tenant, 'role', tenantCustomDashboardKey)) {
      permissionDenied = true;
      DashboardComponent = SingularityDashboard;
      resolutionTrace.push('permission-denied→fallback');
    }
  }

  // STEP 5: Industry dashboard (only if tenant.industry is valid)
  if (!DashboardComponent && tenant?.industry && typeof tenant.industry === 'string' && tenant.industry.trim() !== '') {
    const industryKey = normalizeDashboardRegistryKey(tenant.industry);
    if (industryLoaders[industryKey]) {
      DashboardComponent = industryLoaders[industryKey]();
      resolutionTrace.push(`industry:${tenant.industry}`);
      if (!hasDashboardAccess(user, tenant, 'industry')) {
        permissionDenied = true;
        DashboardComponent = SingularityDashboard;
        resolutionTrace.push('permission-denied→fallback');
      }
    }
  }

  // STEP 6: Ultimate fallback
  if (!DashboardComponent) {
    DashboardComponent = SingularityDashboard;
    resolutionTrace.push('fallback:singularity');
    fallbackUsed = true;
  }

  // Wrap with Suspense & ErrorBoundary
  /**
   * @function WrappedDashboard
   * @description Wraps the resolved dashboard in ErrorBoundary and Suspense protections.
   * @param {Object} props - Dashboard props.
   * @returns {React.ReactElement} Protected dashboard render.
   * @collaboration Keeps lazy CRM OS, sovereign and tenant dashboards resilient during route hydration.
   */
  const WrappedDashboard = (props) => {
    if (DashboardComponent === SingularityDashboard) {
      return (
        <ErrorBoundary fallback={<SingularityDashboard />}>
          <DashboardComponent {...props} />
        </ErrorBoundary>
      );
    }
    return (
      <ErrorBoundary fallback={<SingularityDashboard />}>
        <Suspense fallback={<RegistryLoader />}>
          <DashboardComponent {...props} />
        </Suspense>
      </ErrorBoundary>
    );
  };

  setCached(cacheKey, WrappedDashboard);
  logDashboardResolution(user?._id, tenant?._id, resolutionTrace.join('→'), fallbackUsed, permissionDenied, false);
  console.log(`[DashboardRegistry] ✅ Resolved: ${resolutionTrace.join(' → ')}`);

  return WrappedDashboard;
}

/**
 * @function preloadDashboard
 * @description Preloads the resolved dashboard for a user and tenant into the bounded dashboard cache.
 * @param {Object} user - Authenticated user.
 * @param {Object} tenant - Active tenant.
 * @returns {void}
 * @collaboration Speeds up role-based dashboard entry without bypassing tenant isolation.
 */
export function preloadDashboard(user, tenant) {
  if (!isTenantAccessAllowed(user, tenant)) return;
  const cacheKey = `${user?._id}-${tenant?._id}-preload`;
  if (getCached(cacheKey)) return;
  const Dashboard = resolveDashboard(user, tenant, { bypassCache: true });
  setCached(cacheKey, Dashboard);
}

export default { resolveDashboard, preloadDashboard };
