/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DASHBOARD TOP RAIL                                           ║
 * ║ Slot-based Executive-grade top rail for every Wilsy OS dashboard.        ║
 * ╠════════════════════════════════════════════════════════════════════════════╣
 * ║ PURPOSE                                                                  ║
 * ║ • Provide the Wilsy OS Chrome top-rail standard without wrapping a full   ║
 * ║   dashboard shell.                                                       ║
 * ║ • Let CRM, HR, Finance, Legal and future dashboards keep their own        ║
 * ║   workspaces, rails and domain CSS.                                      ║
 * ║ • Expose explicit slots and handlers for search, account, sync and        ║
 * ║   primary actions.                                                       ║
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
import {
  buildWilsyDashboardOperatorIdentity,
  buildWilsyDashboardTenantIdentity,
  compactWilsyDashboardSignal,
  normalizeWilsyDashboardText
} from './wilsyDashboardChromeConfig';
import './WilsyOSDashboardChrome.module.css';

const WILSY_OS_DASHBOARD_TOP_RAIL_VERSION = 'V1.0.0-SLOT-BASED-EXECUTIVE-TOPRAIL';
const WILSY_OS_DEFAULT_MARK = new URL('../../assets/logo/wilsy.jpeg', import.meta.url).href;

/**
 * @function normalizeWilsyTopRailStory
 * @description Normalizes top rail story messages without fabricating operational data.
 * @param {Array<string>|string|undefined} storyMessages - Candidate story messages.
 * @param {Object} fallbackContext - Tenant, operator and posture fallback context.
 * @returns {Array<string>} Display-safe story messages.
 * @collaboration Gives every dashboard a consistent Wilsy OS story rail while preserving source-truth language.
 */
const normalizeWilsyTopRailStory = (storyMessages = [], fallbackContext = {}) => {
  if (Array.isArray(storyMessages) && storyMessages.filter(Boolean).length) {
    return storyMessages.filter(Boolean).map(message => normalizeWilsyDashboardText(message, 'Source required'));
  }

  if (typeof storyMessages === 'string' && storyMessages.trim()) {
    return [storyMessages.trim()];
  }

  const tenantLabel = normalizeWilsyDashboardText(fallbackContext.tenant?.displayName, 'Wilsy OS Tenant');
  const operatorLabel = normalizeWilsyDashboardText(fallbackContext.operator?.displayName, 'Wilsy OS Operator');
  const operatorRole = normalizeWilsyDashboardText(fallbackContext.operator?.roleLabel, 'Operator');
  const posture = compactWilsyDashboardSignal(fallbackContext.posture || 'SOURCE_REQUIRED');

  return [
    `${tenantLabel} operating system active`,
    `${operatorLabel} operating as ${operatorRole}`,
    `Operating posture: ${posture}`
  ];
};

/**
 * @function buildWilsyTopRailPayload
 * @description Builds the normalized payload consumed by the slot-based Wilsy OS top rail.
 * @param {Object} params - Top rail input props.
 * @returns {Object} Normalized top rail payload.
 * @collaboration Lets dashboards reuse the Executive-grade top rail contract without surrendering their layout ownership.
 */
const buildWilsyTopRailPayload = ({
  commandLabel = 'Wilsy OS Command',
  title = 'WILSY OS DASHBOARD',
  dashboardKey = 'dashboard',
  posture = 'SOURCE_REQUIRED',
  tenant = {},
  operator = {},
  storyMessages = [],
  search = {},
  account = {},
  actions = {}
} = {}) => {
  const tenantIdentity = buildWilsyDashboardTenantIdentity(tenant);
  tenantIdentity.logo = !tenantIdentity.logo || String(tenantIdentity.logo).startsWith('/src/assets/')
    ? WILSY_OS_DEFAULT_MARK
    : tenantIdentity.logo;
  const operatorIdentity = buildWilsyDashboardOperatorIdentity(operator, operator.role || 'OPERATOR');
  const normalizedStory = normalizeWilsyTopRailStory(storyMessages, {
    tenant: tenantIdentity,
    operator: operatorIdentity,
    posture
  });

  return {
    dashboardKey: normalizeWilsyDashboardText(dashboardKey, 'dashboard'),
    commandLabel: normalizeWilsyDashboardText(commandLabel, 'Wilsy OS Command'),
    title: normalizeWilsyDashboardText(title, 'WILSY OS DASHBOARD'),
    posture: compactWilsyDashboardSignal(posture),
    tenant: tenantIdentity,
    operator: operatorIdentity,
    storyMessages: normalizedStory,
    search: {
      value: search.value || '',
      placeholder: normalizeWilsyDashboardText(search.placeholder, 'Search Wilsy OS or press ⌘K'),
      onChange: search.onChange,
      onFocus: search.onFocus
    },
    account: {
      label: normalizeWilsyDashboardText(account.label, 'COMMAND CENTER'),
      onOpen: account.onOpen
    },
    actions: {
      liveSyncLabel: normalizeWilsyDashboardText(actions.liveSyncLabel, 'LIVE SYNC'),
      primaryActionLabel: normalizeWilsyDashboardText(actions.primaryActionLabel, 'NEW COMMAND'),
      isRefreshing: Boolean(actions.isRefreshing),
      primaryDisabled: Boolean(actions.primaryDisabled),
      onLiveSync: actions.onLiveSync,
      onPrimaryAction: actions.onPrimaryAction
    }
  };
};

/**
 * @function WilsyOSDashboardTopRail
 * @description Renders the slot-based Executive-grade Wilsy OS top rail without owning dashboard layout.
 * @param {Object} props - Top rail props.
 * @returns {React.ReactElement} Wilsy OS dashboard top rail.
 * @collaboration Allows CRM to reach Wilsy OS Chrome quality by replacing only its top bar while preserving mature CRM workspace, rail and command systems.
 */
const WilsyOSDashboardTopRail = ({
  commandLabel = 'Wilsy OS Command',
  title = 'WILSY OS DASHBOARD',
  dashboardKey = 'dashboard',
  posture = 'SOURCE_REQUIRED',
  tenant = {},
  operator = {},
  storyMessages = [],
  search = {},
  account = {},
  actions = {},
  accountTrigger = null,
  className = '',
  style = {}
}) => {
  const payload = buildWilsyTopRailPayload({
    commandLabel,
    title,
    dashboardKey,
    posture,
    tenant,
    operator,
    storyMessages,
    search,
    account,
    actions
  });

  return (
    <header
      className={`wilsyOsChromeTopRail wilsyOsDashboardTopRail wilsyOsDashboardTopRail-${payload.dashboardKey} ${className}`.trim()}
      data-wilsy-os-toprail="slot-based"
      data-wilsy-dashboard-key={payload.dashboardKey}
      data-wilsy-toprail-version={WILSY_OS_DASHBOARD_TOP_RAIL_VERSION}
      style={style}
    >
      <div className="wilsyOsChromeTitleBlock">
        <span className="wilsyOsChromeEyebrow">
          <Briefcase size={14} /> {payload.commandLabel}
        </span>
        <h1>{payload.title}</h1>
        <div className="wilsyOsChromeStoryRail" aria-label="Wilsy OS operating story">
          <span>{payload.storyMessages.join('     •     ')}</span>
        </div>
      </div>

      <section className="wilsyOsChromeTenantPlate" aria-label="Tenant identity">
        <div className="wilsyOsChromeTenantMark">
          {payload.tenant.logo ? (
            <img
              src={payload.tenant.logo}
              alt={`${payload.tenant.displayName} mark`}
              onError={event => {
                event.currentTarget.onerror = null;
                event.currentTarget.src = WILSY_OS_DEFAULT_MARK;
              }}
            />
          ) : (
            <span>{payload.tenant.initials}</span>
          )}
        </div>
        <div>
          <small>TENANT IDENTITY</small>
          <strong>{payload.tenant.displayName}</strong>
          <em>{payload.tenant.status || 'TENANT LEDGER READY'}</em>
        </div>
      </section>

      <section className="wilsyOsChromeToolbar" aria-label="Dashboard command toolbar">
        <div className="wilsyOsChromeOperatorCard" title={payload.operator.email || payload.operator.displayName}>
          <UserCog size={14} />
          <div>
            <strong>{payload.operator.displayName}</strong>
            <small>{payload.operator.roleLabel}</small>
          </div>
        </div>

        <label className="wilsyOsChromeSearchBox">
          <Search size={13} />
          <input
            value={payload.search.value}
            onChange={payload.search.onChange}
            placeholder={payload.search.placeholder}
            onFocus={payload.search.onFocus}
          />
        </label>

                {accountTrigger || (
<button
          type="button"
          className="wilsyOsChromeSecondaryButton"
          data-wilsy-command-center-trigger="true"
          onMouseDown={event => {
            event.preventDefault();

            if (typeof payload.account.onOpen === 'function') {
              payload.account.onOpen(event);
            }
          }}
          onClick={event => {
            event.preventDefault();
            if (typeof payload.account.onOpen === 'function') {
              payload.account.onOpen(event);
            }
          }}
          title="Open Wilsy Account Command Center"
        >
          <UserCog size={13} /> {payload.account.label}
        </button>
        )}

        <button
          type="button"
          className="wilsyOsChromeSecondaryButton"
          onClick={payload.actions.onLiveSync}
          disabled={payload.actions.isRefreshing}
        >
          <RefreshCw size={13} className={payload.actions.isRefreshing ? 'wilsyOsChromeSpin' : ''} />
          {payload.actions.liveSyncLabel}
        </button>

        <button
          type="button"
          className="wilsyOsChromePrimaryButton"
          onClick={payload.actions.onPrimaryAction}
          disabled={payload.actions.primaryDisabled}
        >
          <Plus size={13} /> {payload.actions.primaryActionLabel}
        </button>
      </section>
    </header>
  );
};

export {
  WILSY_OS_DASHBOARD_TOP_RAIL_VERSION,
  buildWilsyTopRailPayload,
  normalizeWilsyTopRailStory
};

export default WilsyOSDashboardTopRail;
