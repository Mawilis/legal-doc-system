/* eslint-disable */

import {
  WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_MODEL_VERSION,
  buildTerminalEvidenceCockpitModel,
  fetchTerminalEvidenceCockpitModel,
} from './wilsyCrmTerminalEvidenceCockpitModel.js';

export const WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_MOUNT_CONTRACT_VERSION =
  'R72C-CRM-TERMINAL-EVIDENCE-DASHBOARD-MOUNT-CONTRACT-AUTHORITY';

export const WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_SLOT_ID =
  'crm-terminal-evidence-launch-cockpit-slot';

export const WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_PANEL_ID =
  'crm-terminal-evidence-launch-cockpit-panel';

/**
 * @function normalizeMountLabel
 * @description Converts terminal evidence contract labels into clean dashboard-facing text.
 * @collaboration CRM terminal evidence cockpit model, dashboard mount contract, future CRM dashboard wiring.
 */
export const normalizeMountLabel = (value = '') =>
  String(value || '')
    .replace(/_/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

/**
 * @function buildDashboardMetricTiles
 * @description Converts R72B cockpit KPIs into dashboard metric tile contracts.
 * @collaboration R72B cockpit model, CRM dashboard mount contract, terminal evidence KPI surface.
 */
export const buildDashboardMetricTiles = (cockpitModel = {}) => {
  const kpis = Array.isArray(cockpitModel.kpis) ? cockpitModel.kpis : [];

  return kpis.map((kpi, index) => ({
    id: `terminal-evidence-metric-${kpi.key || index + 1}`,
    key: kpi.key || `metric_${index + 1}`,
    label: kpi.label || normalizeMountLabel(kpi.key || `metric_${index + 1}`),
    value: kpi.value,
    status: kpi.status || (kpi.ready ? 'READY' : 'REVIEW'),
    ready: kpi.ready === true,
    priority: index + 1,
  }));
};

/**
 * @function buildDashboardAudiencePanels
 * @description Converts R72B audience cards into dashboard panel contracts.
 * @collaboration R72B audience cards, CRM dashboard mount contract, buyer/regulator/investor launch surfaces.
 */
export const buildDashboardAudiencePanels = (cockpitModel = {}) => {
  const cards = Array.isArray(cockpitModel.audienceCards)
    ? cockpitModel.audienceCards
    : [];

  return cards.map((card, index) => ({
    id: `terminal-evidence-audience-${card.audience || index + 1}`,
    audience: card.audience,
    title: card.title || normalizeMountLabel(`${card.audience || 'audience'} evidence`),
    artifact: card.artifact,
    proof: card.proof,
    status: card.status || (card.ready ? 'READY' : 'REVIEW'),
    ready: card.ready === true,
    priority: index + 1,
  }));
};

/**
 * @function buildDashboardActionButtons
 * @description Converts R72B cockpit actions into dashboard button contracts.
 * @collaboration R72B cockpit actions, CRM terminal evidence API endpoints, future CRM dashboard commands.
 */
export const buildDashboardActionButtons = (cockpitModel = {}) => {
  const actions = Array.isArray(cockpitModel.actions)
    ? cockpitModel.actions
    : [];

  return actions.map((action, index) => ({
    id: `terminal-evidence-action-${action.action || index + 1}`,
    action: action.action,
    label: action.label || normalizeMountLabel(action.action || `action_${index + 1}`),
    route: action.route,
    ready: action.ready === true,
    variant: index === 0 ? 'primary' : 'secondary',
    priority: index + 1,
  }));
};

/**
 * @function buildDashboardReadinessRail
 * @description Converts R72B readiness rail rows into dashboard checklist contracts.
 * @collaboration R72B readiness rail, CRM dashboard mount contract, terminal evidence launch readiness.
 */
export const buildDashboardReadinessRail = (cockpitModel = {}) => {
  const rail = Array.isArray(cockpitModel.readinessRail)
    ? cockpitModel.readinessRail
    : [];

  return rail.map((item, index) => ({
    id: `terminal-evidence-readiness-${item.id || index + 1}`,
    key: item.id || `readiness_${index + 1}`,
    label: item.label || normalizeMountLabel(item.id || `readiness_${index + 1}`),
    status: item.status || (item.ready ? 'READY' : 'REVIEW'),
    ready: item.ready === true,
    priority: index + 1,
  }));
};

/**
 * @function buildDashboardHeroContract
 * @description Builds the top hero contract for the terminal evidence cockpit panel.
 * @collaboration R72B cockpit model, R71M launch packet, CRM dashboard mount surface.
 */
export const buildDashboardHeroContract = (cockpitModel = {}) => ({
  id: 'terminal-evidence-hero',
  eyebrow: 'WILSY CRM TERMINAL EVIDENCE',
  title: 'Verified Launch Packet',
  topKpi: cockpitModel.topKpi || 'VERIFIED_TERMINAL_EVIDENCE',
  releaseDecision: cockpitModel.releaseDecision || 'HOLD',
  releaseScore:
    typeof cockpitModel.releaseScore === 'number' ? cockpitModel.releaseScore : 0,
  status: cockpitModel.ready === true ? 'READY' : 'REVIEW',
  ready: cockpitModel.ready === true,
  narrative:
    'Buyer, board, regulator, investor, auditor, and engineering launch surfaces are ready from the verified terminal evidence packet.',
});

/**
 * @function buildTerminalEvidenceDashboardMountContract
 * @description Builds the full dashboard mount contract from a raw launch packet payload or R72B cockpit model.
 * @collaboration R72B cockpit model, R72A client adapter, future CRM dashboard integration.
 */
export const buildTerminalEvidenceDashboardMountContract = (payloadOrModel = {}) => {
  const cockpitModel =
    payloadOrModel.cockpitType === 'CRM_TERMINAL_EVIDENCE_LAUNCH_COCKPIT_MODEL'
      ? payloadOrModel
      : buildTerminalEvidenceCockpitModel(payloadOrModel);

  const hero = buildDashboardHeroContract(cockpitModel);
  const metricTiles = buildDashboardMetricTiles(cockpitModel);
  const audiencePanels = buildDashboardAudiencePanels(cockpitModel);
  const actionButtons = buildDashboardActionButtons(cockpitModel);
  const readinessRail = buildDashboardReadinessRail(cockpitModel);

  const mountContract = {
    mountVersion: WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_MOUNT_CONTRACT_VERSION,
    sourceModelVersion: WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_MODEL_VERSION,
    mountType: 'CRM_TERMINAL_EVIDENCE_DASHBOARD_MOUNT_CONTRACT',
    slotId: WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_SLOT_ID,
    panelId: WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_PANEL_ID,
    ready: cockpitModel.ready === true,
    productizationSurface: true,
    terminalStop: cockpitModel.terminalStop === true,
    noR70F: cockpitModel.noR70F === true,
    recursiveLoopFrozen: cockpitModel.recursiveLoopFrozen === true,
    jsonResponseOnly: cockpitModel.jsonResponseOnly === true,
    noFilesystemWrite: cockpitModel.noFilesystemWrite === true,
    persistenceMode: cockpitModel.persistenceMode || 'JSON_RESPONSE_ONLY',
    hero,
    metricTiles,
    audiencePanels,
    actionButtons,
    readinessRail,
    counts: {
      metricTiles: metricTiles.length,
      audiencePanels: audiencePanels.length,
      actionButtons: actionButtons.length,
      readinessRail: readinessRail.length,
    },
    mountAssertions: {
      sourceModelReady: cockpitModel.ready === true,
      heroReady: hero.ready === true,
      allMetricTilesReady: metricTiles.every((tile) => tile.ready === true),
      allAudiencePanelsReady: audiencePanels.every((panel) => panel.ready === true),
      allActionButtonsReady: actionButtons.every((button) => button.ready === true),
      allReadinessRailReady: readinessRail.every((item) => item.ready === true),
      releaseDecisionGo: cockpitModel.releaseDecision === 'GO',
      releaseScorePerfect: cockpitModel.releaseScore === 100,
      terminalStop: cockpitModel.terminalStop === true,
      noR70F: cockpitModel.noR70F === true,
      recursiveLoopFrozen: cockpitModel.recursiveLoopFrozen === true,
      jsonResponseOnly: cockpitModel.jsonResponseOnly === true,
      noFilesystemWrite: cockpitModel.noFilesystemWrite === true,
    },
    sourceCockpitModel: cockpitModel,
  };

  return {
    ...mountContract,
    ready:
      mountContract.ready === true &&
      Object.values(mountContract.mountAssertions).every(Boolean),
  };
};

/**
 * @function fetchTerminalEvidenceDashboardMountContract
 * @description Fetches the terminal evidence cockpit model and returns a dashboard mount contract.
 * @collaboration R72A adapter, R72B cockpit model, CRM dashboard mount contract.
 */
export const fetchTerminalEvidenceDashboardMountContract = async (options = {}) => {
  const cockpitModel = await fetchTerminalEvidenceCockpitModel(options);

  return buildTerminalEvidenceDashboardMountContract(cockpitModel);
};

export default {
  WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_MOUNT_CONTRACT_VERSION,
  WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_SLOT_ID,
  WILSY_CRM_TERMINAL_EVIDENCE_DASHBOARD_PANEL_ID,
  normalizeMountLabel,
  buildDashboardMetricTiles,
  buildDashboardAudiencePanels,
  buildDashboardActionButtons,
  buildDashboardReadinessRail,
  buildDashboardHeroContract,
  buildTerminalEvidenceDashboardMountContract,
  fetchTerminalEvidenceDashboardMountContract,
};
