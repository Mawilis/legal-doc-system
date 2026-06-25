/* eslint-disable */

import {
  WILSY_CRM_TERMINAL_EVIDENCE_LAUNCH_ADAPTER_VERSION,
  WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS,
  buildTerminalEvidenceLaunchSnapshot,
  fetchTerminalEvidenceLaunchPacket,
} from './wilsyCrmTerminalEvidenceLaunchService.js';

export const WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_MODEL_VERSION =
  'R72B-CRM-TERMINAL-EVIDENCE-COCKPIT-MODEL-AUTHORITY';

export const WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_AUDIENCES = Object.freeze([
  'buyer',
  'board',
  'regulator',
  'investor',
  'auditor',
  'engineering',
]);

/**
 * @function boolReady
 * @description Normalizes readiness flags for terminal evidence cockpit card and action models.
 * @collaboration CRM terminal evidence cockpit model, launch snapshot adapter, cockpit status surfaces.
 */
export const boolReady = (value) => value === true;

/**
 * @function resolveLaunchArtifact
 * @description Finds a named launch artifact inside a terminal evidence launch snapshot.
 * @collaboration R71M launch packet, R72A client adapter, CRM cockpit model.
 */
export const resolveLaunchArtifact = (snapshot = {}, artifactName = '') => {
  const artifacts = Array.isArray(snapshot.launchArtifacts)
    ? snapshot.launchArtifacts
    : [];

  return (
    artifacts.find((artifact) => artifact.artifact === artifactName) || {
      artifact: artifactName,
      ready: false,
      proof: null,
    }
  );
};

/**
 * @function buildTerminalEvidenceCockpitKpis
 * @description Builds top-level cockpit KPI cards from a normalized terminal evidence launch snapshot.
 * @collaboration CRM cockpit model, release launch packet, buyer/regulator/investor evidence surfaces.
 */
export const buildTerminalEvidenceCockpitKpis = (snapshot = {}) => [
  {
    key: 'terminalEvidence',
    label: 'Terminal Evidence',
    value: snapshot.topKpi || 'VERIFIED_TERMINAL_EVIDENCE',
    status: boolReady(snapshot.ok) ? 'READY' : 'DEGRADED',
    ready: boolReady(snapshot.ok),
  },
  {
    key: 'releaseDecision',
    label: 'Release Decision',
    value: snapshot.releaseDecision || 'HOLD',
    status: snapshot.releaseDecision === 'GO' ? 'READY' : 'HOLD',
    ready: snapshot.releaseDecision === 'GO',
  },
  {
    key: 'releaseScore',
    label: 'Release Score',
    value: typeof snapshot.releaseScore === 'number' ? snapshot.releaseScore : 0,
    status: snapshot.releaseScore === 100 ? 'READY' : 'REVIEW',
    ready: snapshot.releaseScore === 100,
  },
  {
    key: 'runtimePosture',
    label: 'Runtime Posture',
    value: snapshot.persistenceMode || 'JSON_RESPONSE_ONLY',
    status:
      boolReady(snapshot.jsonResponseOnly) && boolReady(snapshot.noFilesystemWrite)
        ? 'CONTROLLED'
        : 'REVIEW',
    ready:
      boolReady(snapshot.jsonResponseOnly) && boolReady(snapshot.noFilesystemWrite),
  },
  {
    key: 'proofBoundary',
    label: 'Proof Boundary',
    value: boolReady(snapshot.noR70F) ? 'NO RECURSIVE EXPANSION' : 'REVIEW',
    status:
      boolReady(snapshot.noR70F) && boolReady(snapshot.recursiveLoopFrozen)
        ? 'FROZEN'
        : 'OPEN',
    ready:
      boolReady(snapshot.noR70F) && boolReady(snapshot.recursiveLoopFrozen),
  },
];

/**
 * @function buildTerminalEvidenceAudienceCards
 * @description Builds audience-specific cockpit cards for buyer, board, regulator, investor, auditor, and engineering.
 * @collaboration R71M launch artifacts, CRM cockpit model, terminal evidence launch packet.
 */
export const buildTerminalEvidenceAudienceCards = (snapshot = {}) => {
  const artifactMap = {
    buyer: 'buyer_demo_packet',
    board: 'board_approval_packet',
    regulator: 'regulator_inspection_packet',
    investor: 'investor_diligence_packet',
    auditor: 'audit_assurance_packet',
    engineering: 'engineering_handoff_packet',
  };

  const readinessMap = {
    buyer: snapshot.buyerDemoReady,
    board:
      resolveLaunchArtifact(snapshot, artifactMap.board).ready === true,
    regulator: snapshot.regulatorReady,
    investor: snapshot.investorReady,
    auditor: snapshot.auditorReady,
    engineering: snapshot.engineeringReady,
  };

  return WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_AUDIENCES.map((audience) => {
    const artifact = resolveLaunchArtifact(snapshot, artifactMap[audience]);

    return {
      audience,
      artifact: artifact.artifact,
      title: `${audience.charAt(0).toUpperCase()}${audience.slice(1)} Evidence`,
      proof: artifact.proof || 'VERIFIED_TERMINAL_EVIDENCE',
      ready: boolReady(readinessMap[audience]) && boolReady(artifact.ready),
      status:
        boolReady(readinessMap[audience]) && boolReady(artifact.ready)
          ? 'READY'
          : 'REVIEW',
    };
  });
};

/**
 * @function buildTerminalEvidenceCockpitActions
 * @description Builds UI action descriptors for the terminal evidence cockpit without mutating dashboard files.
 * @collaboration R72A endpoint registry, CRM cockpit model, future dashboard wiring.
 */
export const buildTerminalEvidenceCockpitActions = () => [
  {
    action: 'open_launch_packet',
    label: 'Open Launch Packet',
    route: WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS.launchPacket,
    ready: true,
  },
  {
    action: 'open_release_brief',
    label: 'Open Release Brief',
    route: WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS.releaseBrief,
    ready: true,
  },
  {
    action: 'verify_release_passport',
    label: 'Verify Release Passport',
    route: WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS.releasePassportVerifier,
    ready: true,
  },
  {
    action: 'open_api_surface_registry',
    label: 'Open API Surface Registry',
    route: WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS.apiSurfaceRegistry,
    ready: true,
  },
  {
    action: 'open_cockpit_contract',
    label: 'Open Cockpit Contract',
    route: WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS.cockpitContract,
    ready: true,
  },
];

/**
 * @function buildTerminalEvidenceReadinessRail
 * @description Builds a compact readiness rail for cockpit rendering from launch readiness matrix rows.
 * @collaboration R71M launch readiness matrix, CRM cockpit model, future UI rail without current rail mutation.
 */
export const buildTerminalEvidenceReadinessRail = (snapshot = {}) => {
  const matrix = Array.isArray(snapshot.launchReadinessMatrix)
    ? snapshot.launchReadinessMatrix
    : [];

  return matrix.map((item, index) => ({
    id: item.check || `readiness_${index + 1}`,
    label: String(item.check || `readiness_${index + 1}`).replace(/_/g, ' '),
    ready: boolReady(item.ready),
    status: boolReady(item.ready) ? 'READY' : 'REVIEW',
  }));
};

/**
 * @function buildTerminalEvidenceCockpitModel
 * @description Converts a raw or normalized launch packet payload into a full cockpit-ready view model.
 * @collaboration R72A adapter, R71M launch packet, CRM dashboard future integration.
 */
export const buildTerminalEvidenceCockpitModel = (payload = {}) => {
  const snapshot = buildTerminalEvidenceLaunchSnapshot(payload);
  const kpis = buildTerminalEvidenceCockpitKpis(snapshot);
  const audienceCards = buildTerminalEvidenceAudienceCards(snapshot);
  const actions = buildTerminalEvidenceCockpitActions();
  const readinessRail = buildTerminalEvidenceReadinessRail(snapshot);

  const model = {
    modelVersion: WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_MODEL_VERSION,
    adapterVersion: WILSY_CRM_TERMINAL_EVIDENCE_LAUNCH_ADAPTER_VERSION,
    cockpitType: 'CRM_TERMINAL_EVIDENCE_LAUNCH_COCKPIT_MODEL',
    ok: snapshot.ok === true,
    topKpi: snapshot.topKpi,
    releaseDecision: snapshot.releaseDecision,
    releaseScore: snapshot.releaseScore,
    productizationSurface: true,
    terminalStop: snapshot.terminalStop === true,
    noR70F: snapshot.noR70F === true,
    recursiveLoopFrozen: snapshot.recursiveLoopFrozen === true,
    jsonResponseOnly: snapshot.jsonResponseOnly === true,
    noFilesystemWrite: snapshot.noFilesystemWrite === true,
    persistenceMode: snapshot.persistenceMode,
    kpis,
    audienceCards,
    actions,
    readinessRail,
    counts: {
      kpis: kpis.length,
      audienceCards: audienceCards.length,
      actions: actions.length,
      readinessRail: readinessRail.length,
      launchArtifacts: snapshot.launchArtifactCount,
      launchSequence: snapshot.launchSequenceCount,
      launchReadiness: snapshot.launchReadinessCount,
    },
    assertions: {
      allKpisReady: kpis.every((item) => item.ready === true),
      allAudienceCardsReady: audienceCards.every((item) => item.ready === true),
      allActionsReady: actions.every((item) => item.ready === true),
      allReadinessRailReady: readinessRail.every((item) => item.ready === true),
      releaseDecisionGo: snapshot.releaseDecision === 'GO',
      releaseScorePerfect: snapshot.releaseScore === 100,
      terminalStop: snapshot.terminalStop === true,
      noR70F: snapshot.noR70F === true,
      recursiveLoopFrozen: snapshot.recursiveLoopFrozen === true,
      jsonResponseOnly: snapshot.jsonResponseOnly === true,
      noFilesystemWrite: snapshot.noFilesystemWrite === true,
    },
  };

  return {
    ...model,
    ready:
      model.ok === true &&
      Object.values(model.assertions).every(Boolean),
  };
};

/**
 * @function fetchTerminalEvidenceCockpitModel
 * @description Fetches the launch packet through R72A and returns a cockpit-ready model.
 * @collaboration R72A client adapter, R72B cockpit model, future CRM dashboard surface.
 */
export const fetchTerminalEvidenceCockpitModel = async (options = {}) => {
  const envelope = await fetchTerminalEvidenceLaunchPacket(options);

  return buildTerminalEvidenceCockpitModel(envelope.raw || envelope);
};

export default {
  WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_MODEL_VERSION,
  WILSY_CRM_TERMINAL_EVIDENCE_COCKPIT_AUDIENCES,
  boolReady,
  resolveLaunchArtifact,
  buildTerminalEvidenceCockpitKpis,
  buildTerminalEvidenceAudienceCards,
  buildTerminalEvidenceCockpitActions,
  buildTerminalEvidenceReadinessRail,
  buildTerminalEvidenceCockpitModel,
  fetchTerminalEvidenceCockpitModel,
};
