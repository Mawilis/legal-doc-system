/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SHARED DASHBOARD CHROME                                      ║
 * ║ Executive-standard operating shell for Wilsy OS dashboards.              ║
 * ╠════════════════════════════════════════════════════════════════════════════╣
 * ║ PURPOSE                                                                  ║
 * ║ • Standardize top rail, tenant identity, operator identity, search,       ║
 * ║   Account Command Center, live sync and context actions across dashboards.║
 * ║ • Keep each dashboard focused on its domain modules and data only.        ║
 * ║ • Reuse the existing WilsyAccountCommandCenter.                           ║
 * ╚════════════════════════════════════════════════════════════════════════════╝
 */

import React from 'react';
import {
  Briefcase,
  Plus,
  RefreshCw,
  Search,
  UserCog
} from 'lucide-react';
import WilsyAccountCommandCenter from '../account/WilsyAccountCommandCenter';
import './WilsyOSDashboardChrome.module.css';

const WILSY_OS_DASHBOARD_CHROME_VERSION = 'V1.0.0-EXECUTIVE-STANDARD-CHROME';

/**
 * @function normalizeWilsyChromeText
 * @description Normalizes operating shell text without inventing fake dashboard copy.
 * @param {unknown} value - Candidate display value.
 * @param {string} fallback - Truthful fallback when the candidate is empty.
 * @returns {string} Display-safe text.
 * @collaboration Keeps all Wilsy OS dashboards readable while preserving the no-placeholder doctrine.
 */
const normalizeWilsyChromeText = (value, fallback = '') => {
  const normalized = String(value ?? '').trim();
  return normalized || fallback;
};

/**
 * @function compactWilsyChromeSignal
 * @description Converts source and posture states into dashboard-safe operating language.
 * @param {unknown} value - Candidate source, account, session or readiness state.
 * @returns {string} Human-readable Wilsy OS signal.
 * @collaboration Gives every dashboard the Executive-style source truth language without duplicating helper logic.
 */
const compactWilsyChromeSignal = (value = 'SOURCE_REQUIRED') => {
  const raw = String(value || 'SOURCE_REQUIRED').trim().toUpperCase();

  const aliases = {
    READY: 'Ready',
    LIVE: 'Live',
    COMMAND_READY: 'Ready for decisions',
    SOURCE_GAPS: 'Source gaps',
    SOURCE_REQUIRED: 'Source required',
    SOURCE_SILENT: 'Source awaiting connection',
    SOURCE_PENDING: 'Source pending',
    SOURCE_LIVE: 'Source live',
    TELEMETRY_SYNCING: 'Telemetry syncing',
    TELEMETRY_LIVE: 'Telemetry live',
    ACCOUNT_VERIFIED: 'Account verified',
    ACCESS_GATED: 'Access gated',
    POPIA_SAFE: 'POPIA display safe',
    TENANT_LEDGER_READY: 'Tenant ledger ready'
  };

  if (aliases[raw]) return aliases[raw];

  return raw
    .replace(/^WILSY_/, '')
    .replace(/^EXECUTIVE_/, '')
    .replace(/^CRM_/, '')
    .replace(/^HR_/, '')
    .replace(/_+/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, letter => letter.toUpperCase());
};

/**
 * @function buildWilsyChromeIdentity
 * @description Builds tenant and operator identity packets for the shared dashboard chrome.
 * @param {Object} params - Tenant, operator and dashboard identity inputs.
 * @returns {{tenant:Object,operator:Object,storyMessages:Array<string>}} Normalized chrome identity.
 * @collaboration Lets CRM, HR, Finance and other dashboards use one Executive-grade identity story without hardcoding Wilson or MASTER.
 */
const buildWilsyChromeIdentity = ({
  tenant = {},
  operator = {},
  dashboard = {},
  storyMessages = []
} = {}) => {
  const tenantName = normalizeWilsyChromeText(
    tenant.displayName || tenant.name || tenant.companyName || tenant.tenantName,
    'Wilsy OS Tenant'
  );
  const tenantId = normalizeWilsyChromeText(
    tenant.tenantId || tenant.id,
    'TENANT'
  );
  const operatorName = normalizeWilsyChromeText(
    operator.displayName || operator.fullName || operator.name || operator.email,
    'Wilsy OS Operator'
  );
  const operatorRole = normalizeWilsyChromeText(
    operator.roleLabel || operator.role || operator.userRole || dashboard.role,
    'Operator'
  );

  const resolvedStoryMessages = Array.isArray(storyMessages) && storyMessages.length
    ? storyMessages.filter(Boolean)
    : [
      `${tenantName} operating system active`,
      `${operatorName} operating as ${operatorRole}`,
      compactWilsyChromeSignal(dashboard.posture || 'SOURCE_REQUIRED')
    ];

  return {
    tenant: {
      ...tenant,
      tenantId,
      displayName: tenantName,
      initials: normalizeWilsyChromeText(tenant.initials, tenantName.slice(0, 2).toUpperCase())
    },
    operator: {
      ...operator,
      displayName: operatorName,
      roleLabel: operatorRole
    },
    storyMessages: resolvedStoryMessages
  };
};

/**
 * @function WilsyOSDashboardChrome
 * @description Renders the reusable Executive-standard Wilsy OS dashboard shell.
 * @param {Object} props - Dashboard chrome props.
 * @returns {React.ReactElement} Shared Wilsy OS dashboard chrome.
 * @collaboration Establishes one top app bar, one tenant identity plate, one Account Command Center pattern and context-specific dashboard slots.
 */
const WilsyOSDashboardChrome = ({
  dashboardKey = 'dashboard',
  commandLabel = 'Wilsy OS Command',
  title = 'Wilsy OS Dashboard',
  role = 'OPERATOR',
  posture = 'SOURCE_REQUIRED',
  tenant = {},
  operator = {},
  storyMessages = [],
  search = {},
  account = {},
  actions = {},
  metrics = [],
  leftRail = null,
  children = null,
  rightRail = null,
  className = '',
  style = {}
}) => {
  const identity = buildWilsyChromeIdentity({
    tenant,
    operator,
    dashboard: { dashboardKey, role, posture },
    storyMessages
  });

  const liveSyncLabel = normalizeWilsyChromeText(actions.liveSyncLabel, 'LIVE SYNC');
  const primaryActionLabel = normalizeWilsyChromeText(actions.primaryActionLabel, 'NEW COMMAND');
  const searchPlaceholder = normalizeWilsyChromeText(search.placeholder, 'Search Wilsy OS or press ⌘K');
  const accountLabel = normalizeWilsyChromeText(account.label, 'COMMAND CENTER');
  const accountUser = account.user || operator || {};
  const accountSecuritySummary = account.securitySummary || {
    identitySource: compactWilsyChromeSignal(account.identitySource || 'ACCOUNT_VERIFIED'),
    mfaStatus: compactWilsyChromeSignal(account.mfaStatus || 'SOURCE_REQUIRED'),
    trustedDevices: compactWilsyChromeSignal(account.trustedDevices || 'SOURCE_REQUIRED'),
    accountActivity: compactWilsyChromeSignal(posture)
  };
  const accountComplianceSummary = account.complianceSummary || {
    privacyStatus: compactWilsyChromeSignal(account.privacyStatus || 'POPIA_SAFE'),
    complianceStatus: compactWilsyChromeSignal(account.complianceStatus || 'SOURCE_REQUIRED'),
    auditConfidence: compactWilsyChromeSignal(account.auditConfidence || posture),
    retentionStatus: compactWilsyChromeSignal(account.retentionStatus || 'TENANT_LEDGER_READY')
  };
  const accountSessionSummary = account.sessionSummary || {
    activeSessions: compactWilsyChromeSignal(account.activeSessions || 'SOURCE_REQUIRED')
  };

  return (
    <div
      className={`wilsyOsDashboardChrome wilsyOsDashboardChrome-${dashboardKey} ${className}`.trim()}
      data-wilsy-os-dashboard-chrome="true"
      data-wilsy-dashboard-key={dashboardKey}
      data-wilsy-chrome-version={WILSY_OS_DASHBOARD_CHROME_VERSION}
      style={style}
    >
      <header className="wilsyOsChromeTopRail">
        <div className="wilsyOsChromeTitleBlock">
          <span className="wilsyOsChromeEyebrow">
            <Briefcase size={14} /> {commandLabel}
          </span>
          <h1>{title}</h1>
          <div className="wilsyOsChromeStoryRail" aria-label="Wilsy OS operating story">
            <span>{identity.storyMessages.join('     •     ')}</span>
          </div>
        </div>

        <section className="wilsyOsChromeTenantPlate" aria-label="Tenant identity">
          <div className="wilsyOsChromeTenantMark">
            {identity.tenant.logo ? (
              <img src={identity.tenant.logo} alt={`${identity.tenant.displayName} mark`} />
            ) : (
              <span>{identity.tenant.initials}</span>
            )}
          </div>
          <div>
            <small>TENANT IDENTITY</small>
            <strong>{identity.tenant.displayName}</strong>
            <em>{normalizeWilsyChromeText(identity.tenant.status, 'OPERATING BRAND VERIFIED')}</em>
          </div>
        </section>

        <section className="wilsyOsChromeToolbar" aria-label="Dashboard command toolbar">
          <div className="wilsyOsChromeOperatorCard" title={identity.operator.email || identity.operator.displayName}>
            <UserCog size={14} />
            <div>
              <strong>{identity.operator.displayName}</strong>
              <small>{identity.operator.roleLabel}</small>
            </div>
          </div>

          <label className="wilsyOsChromeSearchBox">
            <Search size={13} />
            <input
              value={search.value || ''}
              onChange={search.onChange}
              placeholder={searchPlaceholder}
              onFocus={search.onFocus}
            />
          </label>

          <button
            type="button"
            className="wilsyOsChromeSecondaryButton"
            onClick={account.onOpen}
            title="Open Wilsy Account Command Center"
          >
            <UserCog size={13} /> {accountLabel}
          </button>

          <button
            type="button"
            className="wilsyOsChromeSecondaryButton"
            onClick={actions.onLiveSync}
            disabled={Boolean(actions.isRefreshing)}
          >
            <RefreshCw size={13} className={actions.isRefreshing ? 'wilsyOsChromeSpin' : ''} /> {liveSyncLabel}
          </button>

          <button
            type="button"
            className="wilsyOsChromePrimaryButton"
            onClick={actions.onPrimaryAction}
            disabled={Boolean(actions.primaryDisabled)}
          >
            <Plus size={13} /> {primaryActionLabel}
          </button>
        </section>
      </header>

      <section className="wilsyOsChromeMetricStrip" aria-label="Dashboard operating metrics">
        {metrics.map(metric => (
          <article key={metric.id || metric.label}>
            <small>{metric.label}</small>
            <strong>{metric.value}</strong>
            {metric.detail && <span>{metric.detail}</span>}
          </article>
        ))}
      </section>

      <section className="wilsyOsChromeWorkspaceFrame">
        {leftRail && (
          <aside className="wilsyOsChromeLeftRail" aria-label="Dashboard navigation rail">
            {leftRail}
          </aside>
        )}

        <main className="wilsyOsChromeViewport">
          {children}
        </main>

        {rightRail && (
          <aside className="wilsyOsChromeRightRail" aria-label="Dashboard command rail">
            {rightRail}
          </aside>
        )}
      </section>

      <WilsyAccountCommandCenter
        isOpen={Boolean(account.isOpen)}
        onClose={account.onClose}
        onNavigate={account.onNavigate}
        onSignOut={account.onSignOut}
        user={accountUser}
        activeThemeId={account.activeThemeId}
        themeMode={account.themeMode}
        onThemeChange={account.onThemeChange}
        onModeChange={account.onModeChange}
        securitySummary={accountSecuritySummary}
        complianceSummary={accountComplianceSummary}
        sessionSummary={accountSessionSummary}
      />
    </div>
  );
};

export {
  WILSY_OS_DASHBOARD_CHROME_VERSION,
  buildWilsyChromeIdentity,
  compactWilsyChromeSignal,
  normalizeWilsyChromeText
};

export default WilsyOSDashboardChrome;
