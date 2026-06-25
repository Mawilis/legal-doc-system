/* eslint-disable */

import React, { useEffect, useMemo, useState } from 'react';
import {
  buildTerminalEvidenceDashboardMountContract,
  fetchTerminalEvidenceDashboardMountContract,
} from '../../services/wilsyCrmTerminalEvidenceDashboardMountContract.js';

export const WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_PANEL_VERSION =
  'R72D-CRM-TERMINAL-EVIDENCE-COCKPIT-PANEL-AUTHORITY';

export const WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_PANEL_TEST_ID =
  'crm-terminal-evidence-cockpit-panel';

const panelStyles = {
  shell: {
    border: '1px solid rgba(148, 163, 184, 0.24)',
    borderRadius: 24,
    padding: 24,
    background:
      'linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(2, 6, 23, 0.96))',
    color: '#f8fafc',
    boxShadow: '0 28px 90px rgba(15, 23, 42, 0.42)',
  },
  eyebrow: {
    margin: 0,
    fontSize: 11,
    letterSpacing: '0.18em',
    textTransform: 'uppercase',
    color: '#38bdf8',
    fontWeight: 800,
  },
  titleRow: {
    display: 'flex',
    gap: 16,
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    marginTop: 10,
  },
  title: {
    margin: 0,
    fontSize: 28,
    lineHeight: 1.05,
    fontWeight: 900,
  },
  narrative: {
    margin: '10px 0 0',
    maxWidth: 780,
    color: '#cbd5e1',
    lineHeight: 1.65,
  },
  badge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    borderRadius: 999,
    padding: '8px 12px',
    border: '1px solid rgba(34, 197, 94, 0.32)',
    background: 'rgba(22, 163, 74, 0.14)',
    color: '#bbf7d0',
    fontSize: 12,
    fontWeight: 800,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: 12,
    marginTop: 22,
  },
  card: {
    border: '1px solid rgba(148, 163, 184, 0.18)',
    borderRadius: 18,
    padding: 16,
    background: 'rgba(15, 23, 42, 0.76)',
  },
  cardLabel: {
    margin: 0,
    color: '#94a3b8',
    fontSize: 12,
    fontWeight: 800,
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
  },
  cardValue: {
    margin: '8px 0 0',
    color: '#f8fafc',
    fontSize: 18,
    fontWeight: 900,
  },
  sectionTitle: {
    margin: '26px 0 12px',
    fontSize: 14,
    color: '#e2e8f0',
    textTransform: 'uppercase',
    letterSpacing: '0.12em',
  },
  audienceGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
    gap: 12,
  },
  actionRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 10,
    marginTop: 14,
  },
  action: {
    border: '1px solid rgba(56, 189, 248, 0.28)',
    borderRadius: 14,
    padding: '10px 12px',
    color: '#e0f2fe',
    background: 'rgba(14, 165, 233, 0.14)',
    fontWeight: 800,
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
  },
  rail: {
    display: 'grid',
    gap: 8,
    marginTop: 12,
  },
  railItem: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: 10,
    borderBottom: '1px solid rgba(148, 163, 184, 0.14)',
    padding: '8px 0',
    color: '#cbd5e1',
    fontSize: 13,
  },
  error: {
    border: '1px solid rgba(248, 113, 113, 0.35)',
    color: '#fecaca',
    background: 'rgba(127, 29, 29, 0.24)',
    borderRadius: 18,
    padding: 16,
  },
};

/**
 * @function resolvePanelMountContract
 * @description Resolves a usable dashboard mount contract from supplied mount, raw launch packet payload, or empty state.
 * @collaboration R72C dashboard mount contract, R72D cockpit panel, CRM dashboard integration.
 */
export const resolvePanelMountContract = ({
  mountContract,
  launchPacket,
} = {}) => {
  if (mountContract?.mountType === 'CRM_TERMINAL_EVIDENCE_DASHBOARD_MOUNT_CONTRACT') {
    return mountContract;
  }

  if (launchPacket?.ok === true) {
    return buildTerminalEvidenceDashboardMountContract(launchPacket);
  }

  return null;
};

/**
 * @function createTerminalEvidenceCockpitPanelViewState
 * @description Converts a dashboard mount contract into the panel state consumed by render helpers.
 * @collaboration R72C dashboard mount contract, terminal evidence cockpit panel, future CRMDashboard mount point.
 */
export const createTerminalEvidenceCockpitPanelViewState = (mountContract = {}) => ({
  ready: mountContract.ready === true,
  slotId: mountContract.slotId || 'crm-terminal-evidence-launch-cockpit-slot',
  panelId: mountContract.panelId || 'crm-terminal-evidence-launch-cockpit-panel',
  hero: mountContract.hero || {},
  metricTiles: Array.isArray(mountContract.metricTiles)
    ? mountContract.metricTiles
    : [],
  audiencePanels: Array.isArray(mountContract.audiencePanels)
    ? mountContract.audiencePanels
    : [],
  actionButtons: Array.isArray(mountContract.actionButtons)
    ? mountContract.actionButtons
    : [],
  readinessRail: Array.isArray(mountContract.readinessRail)
    ? mountContract.readinessRail
    : [],
  mountAssertions: mountContract.mountAssertions || {},
  terminalStop: mountContract.terminalStop === true,
  noR70F: mountContract.noR70F === true,
  recursiveLoopFrozen: mountContract.recursiveLoopFrozen === true,
  jsonResponseOnly: mountContract.jsonResponseOnly === true,
  noFilesystemWrite: mountContract.noFilesystemWrite === true,
  persistenceMode: mountContract.persistenceMode || 'JSON_RESPONSE_ONLY',
});

/**
 * @function renderTerminalEvidenceBadge
 * @description Renders a compact readiness badge for the terminal evidence cockpit panel.
 * @collaboration R72D cockpit panel, R72C mount contract, React dashboard composition.
 */
export const renderTerminalEvidenceBadge = (label, ready = true) =>
  React.createElement(
    'span',
    {
      style: {
        ...panelStyles.badge,
        borderColor: ready
          ? 'rgba(34, 197, 94, 0.32)'
          : 'rgba(251, 191, 36, 0.42)',
        background: ready
          ? 'rgba(22, 163, 74, 0.14)'
          : 'rgba(180, 83, 9, 0.18)',
        color: ready ? '#bbf7d0' : '#fde68a',
      },
    },
    ready ? '● ' : '▲ ',
    label
  );

/**
 * @function renderMetricTile
 * @description Renders a terminal evidence metric tile.
 * @collaboration R72D cockpit panel, R72C metric tile contract, CRM dashboard cards.
 */
export const renderMetricTile = (tile) =>
  React.createElement(
    'article',
    {
      key: tile.id || tile.key,
      style: panelStyles.card,
    },
    React.createElement('p', { style: panelStyles.cardLabel }, tile.label),
    React.createElement('p', { style: panelStyles.cardValue }, String(tile.value ?? '—')),
    renderTerminalEvidenceBadge(tile.status || 'READY', tile.ready === true)
  );

/**
 * @function renderAudiencePanel
 * @description Renders a buyer, board, regulator, investor, auditor, or engineering evidence card.
 * @collaboration R72D cockpit panel, R72C audience panel contract, launch artifact surfaces.
 */
export const renderAudiencePanel = (panel) =>
  React.createElement(
    'article',
    {
      key: panel.id || panel.audience,
      style: panelStyles.card,
    },
    React.createElement('p', { style: panelStyles.cardLabel }, panel.title),
    React.createElement('p', { style: panelStyles.cardValue }, panel.artifact),
    React.createElement(
      'p',
      {
        style: {
          margin: '8px 0 0',
          color: '#94a3b8',
          fontSize: 12,
          lineHeight: 1.5,
        },
      },
      panel.proof || 'VERIFIED_TERMINAL_EVIDENCE'
    ),
    renderTerminalEvidenceBadge(panel.status || 'READY', panel.ready === true)
  );

/**
 * @function renderActionButton
 * @description Renders a terminal evidence action descriptor as a safe non-navigating button contract display.
 * @collaboration R72D cockpit panel, R72C action button contract, future dashboard command wiring.
 */
export const renderActionButton = (action) =>
  React.createElement(
    'button',
    {
      key: action.id || action.action,
      type: 'button',
      style: {
        ...panelStyles.action,
        opacity: action.ready === true ? 1 : 0.64,
      },
      'data-route': action.route || '',
      'data-action': action.action || '',
    },
    action.label || action.action
  );

/**
 * @function renderReadinessRailItem
 * @description Renders one launch readiness rail item.
 * @collaboration R72D cockpit panel, R72C readiness rail, CRM evidence checklist surface.
 */
export const renderReadinessRailItem = (item) =>
  React.createElement(
    'div',
    {
      key: item.id || item.key,
      style: panelStyles.railItem,
    },
    React.createElement('span', null, item.label || item.key),
    renderTerminalEvidenceBadge(item.status || 'READY', item.ready === true)
  );

/**
 * @function TerminalEvidenceCockpitPanel
 * @description Renders the isolated terminal evidence cockpit panel without mutating the CRM dashboard file.
 * @collaboration R72C dashboard mount contract, R72B cockpit model, R72A adapter, future CRMDashboard wiring.
 */
export function TerminalEvidenceCockpitPanel({
  apiBaseUrl = '',
  tenantId = 'MASTER',
  operator = 'SYSTEM',
  mountContract,
  launchPacket,
  autoFetch = false,
  onLoaded,
  onError,
} = {}) {
  const initialContract = useMemo(
    () =>
      resolvePanelMountContract({
        mountContract,
        launchPacket,
      }),
    [mountContract, launchPacket]
  );

  const [resolvedContract, setResolvedContract] = useState(initialContract);
  const [loading, setLoading] = useState(autoFetch && !initialContract);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    if (!autoFetch || initialContract) {
      return () => {
        cancelled = true;
      };
    }

    setLoading(true);
    setError(null);

    fetchTerminalEvidenceDashboardMountContract({
      apiBaseUrl,
      tenantId,
      operator,
    })
      .then((contract) => {
        if (cancelled) {
          return;
        }

        setResolvedContract(contract);
        setLoading(false);

        if (typeof onLoaded === 'function') {
          onLoaded(contract);
        }
      })
      .catch((fetchError) => {
        if (cancelled) {
          return;
        }

        setError(fetchError);
        setLoading(false);

        if (typeof onError === 'function') {
          onError(fetchError);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [apiBaseUrl, autoFetch, initialContract, onError, onLoaded, operator, tenantId]);

  if (loading) {
    return React.createElement(
      'section',
      {
        style: panelStyles.shell,
        'data-testid': WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_PANEL_TEST_ID,
      },
      React.createElement('p', { style: panelStyles.eyebrow }, 'WILSY CRM TERMINAL EVIDENCE'),
      React.createElement('h2', { style: panelStyles.title }, 'Loading launch packet…')
    );
  }

  if (error) {
    return React.createElement(
      'section',
      {
        style: panelStyles.error,
        'data-testid': WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_PANEL_TEST_ID,
      },
      React.createElement('strong', null, 'Terminal evidence cockpit unavailable'),
      React.createElement('p', null, error.message || 'Unable to load terminal evidence.')
    );
  }

  if (!resolvedContract) {
    return React.createElement(
      'section',
      {
        style: panelStyles.shell,
        'data-testid': WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_PANEL_TEST_ID,
      },
      React.createElement('p', { style: panelStyles.eyebrow }, 'WILSY CRM TERMINAL EVIDENCE'),
      React.createElement('h2', { style: panelStyles.title }, 'Launch packet not mounted'),
      React.createElement(
        'p',
        { style: panelStyles.narrative },
        'Provide a R72C dashboard mount contract or enable autoFetch to load the verified launch packet.'
      )
    );
  }

  const viewState = createTerminalEvidenceCockpitPanelViewState(resolvedContract);

  return React.createElement(
    'section',
    {
      id: viewState.panelId,
      style: panelStyles.shell,
      'data-testid': WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_PANEL_TEST_ID,
      'data-slot-id': viewState.slotId,
      'data-ready': String(viewState.ready),
    },
    React.createElement(
      'div',
      { style: panelStyles.titleRow },
      React.createElement(
        'div',
        null,
        React.createElement('p', { style: panelStyles.eyebrow }, viewState.hero.eyebrow),
        React.createElement('h2', { style: panelStyles.title }, viewState.hero.title),
        React.createElement('p', { style: panelStyles.narrative }, viewState.hero.narrative)
      ),
      renderTerminalEvidenceBadge(viewState.hero.status || 'READY', viewState.hero.ready === true)
    ),
    React.createElement('div', { style: panelStyles.grid }, viewState.metricTiles.map(renderMetricTile)),
    React.createElement('h3', { style: panelStyles.sectionTitle }, 'Launch Artifacts'),
    React.createElement(
      'div',
      { style: panelStyles.audienceGrid },
      viewState.audiencePanels.map(renderAudiencePanel)
    ),
    React.createElement('h3', { style: panelStyles.sectionTitle }, 'Evidence Actions'),
    React.createElement(
      'div',
      { style: panelStyles.actionRow },
      viewState.actionButtons.map(renderActionButton)
    ),
    React.createElement('h3', { style: panelStyles.sectionTitle }, 'Readiness Rail'),
    React.createElement(
      'div',
      { style: panelStyles.rail },
      viewState.readinessRail.map(renderReadinessRailItem)
    )
  );
}

export default TerminalEvidenceCockpitPanel;
