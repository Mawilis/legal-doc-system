/* eslint-disable */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { ChevronLeft, ChevronRight, Crown, Search } from 'lucide-react';
import wilsyLogo from '../../../assets/logo/wilsy.jpeg';
import styles from './CrmSovereignSideRail.module.css';

const WILSY_CRM_RAIL_ENGINE_VERSION = 'R65A-TRI-STATE-KINETIC-DOCKING-ENGINE';
const RAIL_STORAGE_KEY = 'wilsy_os_crm_rail_state_r65a';
const RAIL_STATES = Object.freeze({
  EXPANDED: 'EXPANDED',
  COLLAPSED: 'COLLAPSED',
  PEEKING: 'PEEKING'
});

/**
 * @function getInitialRailState
 * @description Resolves the persisted Wilsy CRM rail state.
 * @returns {string} Initial rail state.
 * @collaboration Keeps CRM navigation geometry stable across refreshes.
 */
function getInitialRailState() {
  if (typeof window === 'undefined') return RAIL_STATES.EXPANDED;

  const cached = window.localStorage.getItem(RAIL_STORAGE_KEY);
  return cached === RAIL_STATES.COLLAPSED ? RAIL_STATES.COLLAPSED : RAIL_STATES.EXPANDED;
}

/**
 * @function persistRailState
 * @description Persists durable rail states while ignoring transient peek state.
 * @param {string} nextState - Next rail state.
 * @returns {void}
 * @collaboration Separates workspace layout persistence from hover-peek overlays.
 */
function persistRailState(nextState) {
  if (typeof window === 'undefined') return;
  if (nextState === RAIL_STATES.PEEKING) return;

  window.localStorage.setItem(RAIL_STORAGE_KEY, nextState);
}

/**
 * @function getWorkspaceCount
 * @description Resolves a workspace badge count from a snapshot packet.
 * @param {Object} snapshot - CRM source snapshot.
 * @param {string} workspaceId - Workspace id.
 * @returns {number|string} Count value.
 * @collaboration Keeps rail badges connected to backend source arrays.
 */
function getWorkspaceCount(snapshot = {}, workspaceId = '') {
  if (workspaceId === 'home') return 'OS';

  const records = snapshot?.[workspaceId];
  return Array.isArray(records) ? records.length : 0;
}

/**
 * @function groupWorkspaces
 * @description Groups CRM workspaces by category for command rail rendering.
 * @param {Array} workspaces - Workspace registry.
 * @returns {Array} Grouped workspace entries.
 * @collaboration Preserves current CRM module structure while upgrading rail behavior.
 */
function groupWorkspaces(workspaces = []) {
  const order = ['Command', 'Records', 'Control', 'Evidence', 'Connectors'];
  const grouped = workspaces.reduce((accumulator, workspace) => {
    const group = workspace.group || 'Records';
    if (!accumulator[group]) accumulator[group] = [];
    accumulator[group].push(workspace);
    return accumulator;
  }, {});

  return Object.keys(grouped)
    .sort((left, right) => {
      const leftIndex = order.indexOf(left);
      const rightIndex = order.indexOf(right);

      if (leftIndex === -1 && rightIndex === -1) return left.localeCompare(right);
      if (leftIndex === -1) return 1;
      if (rightIndex === -1) return -1;

      return leftIndex - rightIndex;
    })
    .map(group => ({ group, items: grouped[group] }));
}

/**
 * @function resolveTenantName
 * @description Resolves the visible tenant name.
 * @param {Object} tenantConfig - Tenant config.
 * @returns {string} Tenant display name.
 * @collaboration Keeps rail identity tenant-aware.
 */
function resolveTenantName(tenantConfig = {}) {
  return String(
    tenantConfig?.name
      || tenantConfig?.tenantName
      || tenantConfig?.organizationName
      || tenantConfig?.displayName
      || 'Wilsy OS Root'
  );
}

/**
 * @function resolveTenantMode
 * @description Resolves tenant mode or tenant id for the rail badge.
 * @param {Object} tenantConfig - Tenant config.
 * @returns {string} Tenant mode.
 * @collaboration Keeps master tenant boundary visible without hardcoding local UI state.
 */
function resolveTenantMode(tenantConfig = {}) {
  const rawMode = String(
    tenantConfig?.tenantId
      || tenantConfig?.id
      || tenantConfig?.tenantKey
      || tenantConfig?.mode
      || 'Business Workspace'
  );

  return ['MASTER', 'ROOT', 'SUPER_ADMIN'].includes(rawMode.toUpperCase()) ? 'Business Workspace' : rawMode;
}

/**
 * @function resolveOperatorProfile
 * @description Resolves operator name, role and avatar.
 * @param {Object} user - User packet.
 * @returns {Object} Operator profile.
 * @collaboration Keeps footer identity sourced from auth context.
 */
function resolveOperatorProfile(user = {}) {
  return {
    name: String(user?.name || user?.fullName || user?.email || 'Wilson Khanyezi'),
    role: String(user?.role || user?.accountRole || user?.profile?.role || 'Workspace Admin').replace(/_/g, ' '),
    avatarUrl: user?.avatarUrl || user?.avatar || user?.photoUrl || ''
  };
}

/**
 * @function CrmSovereignSideRail
 * @description Renders the Wilsy CRM tri-state kinetic side rail.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} CRM side rail.
 * @collaboration Provides EXPANDED, COLLAPSED and PEEKING navigation without damaging the CRM workspace shell.
 */
export default function CrmSovereignSideRail({
  workspaces = [],
  activeWorkspace = 'home',
  snapshot = {},
  tenantConfig = {},
  user = {},
  onWorkspaceSelect,
  onRailStateChange
}) {
  const [railState, setRailState] = useState(getInitialRailState);
  const peekTimerRef = useRef(null);
  const groupedWorkspaces = useMemo(() => groupWorkspaces(workspaces), [workspaces]);
  const tenantName = resolveTenantName(tenantConfig);
  const tenantMode = resolveTenantMode(tenantConfig);
  const operator = resolveOperatorProfile(user);
  const isMini = railState === RAIL_STATES.COLLAPSED;
  const isOverlay = railState === RAIL_STATES.PEEKING;

  /**
   * @function commitRailState
   * @description Applies a rail state and notifies the dashboard shell.
   * @param {string} nextState - Next rail state.
   * @returns {void}
   * @collaboration Keeps component state, local storage and parent layout synchronized.
   */
  function commitRailState(nextState) {
    setRailState(nextState);
    persistRailState(nextState);

    if (typeof onRailStateChange === 'function') {
      onRailStateChange(nextState);
    }
  }

  /**
   * @function toggleExplicitState
   * @description Toggles between expanded and collapsed rail states.
   * @returns {void}
   * @collaboration Gives users a direct rail control without creating a large dead tile.
   */
  function toggleExplicitState() {
    commitRailState(railState === RAIL_STATES.EXPANDED ? RAIL_STATES.COLLAPSED : RAIL_STATES.EXPANDED);
  }

  /**
   * @function handleDockMouseEnter
   * @description Opens transient peek overlay when the rail is collapsed.
   * @returns {void}
   * @collaboration Allows fast context inspection without shifting the main workspace.
   */
  function handleDockMouseEnter() {
    if (railState !== RAIL_STATES.COLLAPSED) return;

    if (peekTimerRef.current) window.clearTimeout(peekTimerRef.current);
    peekTimerRef.current = window.setTimeout(() => commitRailState(RAIL_STATES.PEEKING), 120);
  }

  /**
   * @function handleDockMouseLeave
   * @description Returns a transient peek rail to collapsed state.
   * @returns {void}
   * @collaboration Preserves collapsed workspace width after hover inspection.
   */
  function handleDockMouseLeave() {
    if (railState !== RAIL_STATES.PEEKING) return;

    if (peekTimerRef.current) window.clearTimeout(peekTimerRef.current);
    peekTimerRef.current = window.setTimeout(() => commitRailState(RAIL_STATES.COLLAPSED), 220);
  }

  /**
   * @function handleWorkspaceClick
   * @description Selects a CRM workspace and closes transient peek state.
   * @param {string} workspaceId - Workspace id.
   * @returns {void}
   * @collaboration Keeps navigation behavior stable between expanded, collapsed and peeking states.
   */
  function handleWorkspaceClick(workspaceId) {
    if (typeof onWorkspaceSelect === 'function') {
      onWorkspaceSelect(workspaceId);
    }

    if (railState === RAIL_STATES.PEEKING) {
      commitRailState(RAIL_STATES.COLLAPSED);
    }
  }

  useEffect(() => {
    if (typeof onRailStateChange === 'function') {
      onRailStateChange(railState);
    }
  }, [onRailStateChange, railState]);

  useEffect(() => {
    /**
     * @function handleKeyboardToggle
     * @description Toggles rail state with Cmd+\ or Ctrl+\.
     * @param {KeyboardEvent} event - Keyboard event.
     * @returns {void}
     * @collaboration Gives Wilsy CRM IDE-grade keyboard orchestration.
     */
    function handleKeyboardToggle(event) {
      if (!(event.metaKey || event.ctrlKey) || event.key !== '\\') return;

      event.preventDefault();
      commitRailState(railState === RAIL_STATES.EXPANDED ? RAIL_STATES.COLLAPSED : RAIL_STATES.EXPANDED);
    }

    window.addEventListener('keydown', handleKeyboardToggle);
    return () => window.removeEventListener('keydown', handleKeyboardToggle);
  }, [railState]);

  useEffect(() => {
    return () => {
      if (peekTimerRef.current) window.clearTimeout(peekTimerRef.current);
    };
  }, []);

  /**
   * @function renderBrand
   * @description Renders rail brand block.
   * @returns {JSX.Element} Brand block.
   * @collaboration Preserves Wilsy CRM identity in expanded and peek states.
   */
  function renderBrand() {
    return (
      <section className={styles.brandBlock}>
        <img src={wilsyLogo} alt="Wilsy CRM" />
        {!isMini ? (
          <span>
            <strong>WILSY CRM</strong>
            <em>{tenantMode}</em>
          </span>
        ) : null}
      </section>
    );
  }

  /**
   * @function renderTenantCard
   * @description Renders tenant identity card.
   * @returns {JSX.Element|null} Tenant card or null.
   * @collaboration Keeps tenant identity visible in expanded and peek states.
   */
  function renderTenantCard() {
    if (isMini) return null;

    return (
      <section className={styles.tenantCard}>
        <span>
          <strong>{tenantName}</strong>
          <em>Tenant Identity Live</em>
        </span>
        <i aria-hidden="true" />
      </section>
    );
  }

  /**
   * @function renderSearch
   * @description Renders rail search affordance.
   * @returns {JSX.Element|null} Search control or null.
   * @collaboration Leaves search available in full rail while mini rail prioritizes icon density.
   */
  function renderSearch() {
    if (isMini) return null;

    return (
      <label className={styles.railSearch}>
        <Search size={20} />
        <input type="search" placeholder="Search CRM" aria-label="Search CRM navigation" />
      </label>
    );
  }

  /**
   * @function renderWorkspaceItem
   * @description Renders one workspace navigation item.
   * @param {Object} workspace - Workspace descriptor.
   * @returns {JSX.Element} Workspace button.
   * @collaboration Keeps current CRM module registry while changing only rail behavior.
   */
  function renderWorkspaceItem(workspace) {
    const Icon = workspace.icon;
    const count = getWorkspaceCount(snapshot, workspace.id);
    const selected = workspace.id === activeWorkspace;
    const label = workspace.label || workspace.id;

    return (
      <button
        key={workspace.id}
        type="button"
        className={selected ? styles.navItemActive : styles.navItem}
        onClick={() => handleWorkspaceClick(workspace.id)}
        title={isMini ? label : undefined}
        aria-label={label}
        aria-current={selected ? 'page' : undefined}
      >
        <span className={styles.navIcon}>{Icon ? <Icon size={22} /> : null}</span>
        {!isMini ? <strong>{label}</strong> : null}
        {!isMini ? <em>{count}</em> : null}
        {isMini && count ? <b>{count}</b> : null}
        {isMini ? <small>{label}</small> : null}
      </button>
    );
  }

  /**
   * @function renderWorkspaceGroup
   * @description Renders a grouped workspace section.
   * @param {Object} groupPacket - Group descriptor.
   * @returns {JSX.Element} Workspace group.
   * @collaboration Preserves COMMAND, RECORDS and CONTROL grouping from the CRM registry.
   */
  function renderWorkspaceGroup(groupPacket) {
    return (
      <section key={groupPacket.group} className={styles.navGroup}>
        {!isMini ? <h4>{groupPacket.group}</h4> : null}
        <div>{groupPacket.items.map(renderWorkspaceItem)}</div>
      </section>
    );
  }

  /**
   * @function renderFooter
   * @description Renders operator identity footer.
   * @returns {JSX.Element|null} Footer identity.
   * @collaboration Keeps operator authority visible in expanded and peek states.
   */
  function renderFooter() {
    if (isMini) return null;

    return (
      <footer className={styles.operatorCard}>
        <span>
          {operator.avatarUrl ? <img src={operator.avatarUrl} alt={operator.name} /> : <Crown size={20} />}
        </span>
        <strong>{operator.name}</strong>
        <em>{operator.role}</em>
      </footer>
    );
  }

  return (
    <aside
      className={styles.railShell}
      data-wilsy-crm-rail-engine={WILSY_CRM_RAIL_ENGINE_VERSION}
      data-rail-state={railState}
      onMouseEnter={handleDockMouseEnter}
      onMouseLeave={handleDockMouseLeave}
      aria-label="Wilsy CRM navigation rail"
    >
      <section className={styles.railPanel}>
        <button
          type="button"
          className={styles.kineticToggle}
          onClick={toggleExplicitState}
          aria-label={railState === RAIL_STATES.EXPANDED ? 'Collapse CRM navigation rail' : 'Expand CRM navigation rail'}
          title="Toggle CRM rail · Cmd+\\"
        >
          <span
            className={styles.togglePanelGlyph}
            data-expanded={railState === RAIL_STATES.EXPANDED ? 'true' : 'false'}
            aria-hidden="true"
          >
            <i />
            <b />
          </span>
          <span className={styles.toggleAssistive}>
            {railState === RAIL_STATES.EXPANDED ? 'Collapse navigation' : 'Expand navigation'}
          </span>
        </button>

        <div className={styles.railTop}>
          {renderBrand()}
          {renderTenantCard()}
          {renderSearch()}
        </div>

        <nav className={styles.navStack} aria-label="CRM workspaces">
          {groupedWorkspaces.map(renderWorkspaceGroup)}
        </nav>

        {renderFooter()}
      </section>

      {isMini ? <span className={styles.hoverZone} aria-hidden="true" /> : null}
      {isOverlay ? <span className={styles.peekScrim} aria-hidden="true" /> : null}
    </aside>
  );
}
