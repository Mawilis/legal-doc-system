/* eslint-disable */

import React from 'react';
import styles from './WilsyOSIntelligenceDock.module.css';

/**
 * @function normalizeWilsyExecutionText
 * @description Normalizes execution canvas text without leaking raw backend or prototype terms.
 * @param {unknown} value - Candidate display value.
 * @param {string} fallback - Safe fallback value.
 * @returns {string} Safe visible text.
 * @collaboration Wilsy OS execution canvas, operator-facing language, sovereign AI display, and production UI restraint.
 */
function normalizeWilsyExecutionText(value, fallback = '') {
  const text = typeof value === 'string' ? value.trim() : '';

  return text || fallback;
}

/**
 * @function resolveWilsyRouteJudge
 * @description Resolves the route-judge object used by the execution canvas.
 * @param {Object} model - Current Wilsy operator model.
 * @returns {Object} Source route judge display object.
 * @collaboration Wilsy AI core engine, source route judge, authority boundary check, and evidence anchor policy.
 */
function resolveWilsyRouteJudge(model = {}) {
  if (model?.sourceRouteJudge) {
    return model.sourceRouteJudge;
  }

  return {
    status: 'READ_ONLY_ALLOWED',
    route: normalizeWilsyExecutionText(model?.domain, 'workspace_governance_lane'),
    decision: 'Prepare work only. Mutation requires governed approval.',
    reason: 'Authority, evidence, and human sign-off remain required before execution.',
  };
}

/**
 * @function resolveWilsyTelemetry
 * @description Resolves compact telemetry packs for the native execution canvas.
 * @param {Object} model - Current Wilsy operator model.
 * @returns {Array<Object>} Telemetry packs.
 * @collaboration Wilsy AI core engine, compliance HUD, authority boundary, evidence anchors, and native cockpit UI.
 */
function resolveWilsyTelemetry(model = {}) {
  const telemetry = Array.isArray(model?.telemetryPacks) ? model.telemetryPacks : [];

  if (telemetry.length > 0) {
    return telemetry;
  }

  return [
    {
      label: 'Authority Boundary',
      value: model?.missionState?.objective || 'Review, approval, release, and mutation powers remain separated.',
    },
    {
      label: 'Evidence Anchor',
      value: Array.isArray(model?.evidenceAnchors) && model.evidenceAnchors[0] ? model.evidenceAnchors[0] : 'Receipt proof required before execution.',
    },
    {
      label: 'Execution Mode',
      value: 'Read-only route preparation until human approval signs off.',
    },
    {
      label: 'Workspace Lens',
      value: normalizeWilsyExecutionText(model?.domain, 'Current workspace'),
    },
  ];
}

/**
 * @function resolveWilsyCommandToken
 * @description Builds a safe command-token display for an execution row.
 * @param {Object} action - Action row candidate.
 * @param {number} index - Row index.
 * @param {string} route - Route prefix.
 * @returns {string} Wilsy command token.
 * @collaboration Wilsy AI command pipeline, read-only execution tokens, and governed command routing.
 */
function resolveWilsyCommandToken(action = {}, index = 0, route = 'wilsy://workspace') {
  return normalizeWilsyExecutionText(
    action.token,
    `${route}/prepare/${String(action.intent || action.id || `move-${index + 1}`).replaceAll('_', '-')}`,
  );
}

/**
 * @function resolveWilsyExecutionRows
 * @description Resolves high-density execution rows from command tokens, playable actions, or mission moves.
 * @param {Object} model - Current Wilsy operator model.
 * @returns {Array<Object>} Execution rows.
 * @collaboration Wilsy AI execution canvas, action rail replacement, command tokens, mission progression, and evidence-aware workflow.
 */
function resolveWilsyExecutionRows(model = {}) {
  const judge = resolveWilsyRouteJudge(model);
  const commandTokens = Array.isArray(model?.commandTokens) ? model.commandTokens : [];
  const playableActions = Array.isArray(model?.playableActions) ? model.playableActions : [];
  const actions = Array.isArray(model?.actions) ? model.actions : [];
  const missionMoves = Array.isArray(model?.missionNextMoves) ? model.missionNextMoves : [];
  const source = commandTokens.length > 0 ? commandTokens : playableActions.length > 0 ? playableActions : actions;

  if (source.length > 0) {
    return source.slice(0, 10).map((action, index) => ({
      id: action.id || action.label || action.title || `execution-${index}`,
      label: normalizeWilsyExecutionText(action.label || action.buttonLabel || action.title, `Execution route ${index + 1}`),
      intent: action.intent || action.id || 'what_next',
      prompt: action.prompt || action.label || action.title || 'What should I do next?',
      token: resolveWilsyCommandToken(action, index, `wilsy://${judge.route || 'workspace'}`),
      telemetry: normalizeWilsyExecutionText(action.telemetry || action.description || action.lockedReason, 'Prepare route with evidence and authority checks.'),
      mode: action.mode || 'read_only_execution_stream',
      evidenceRequired: action.evidenceRequired !== false,
    }));
  }

  return missionMoves.slice(0, 8).map((move, index) => ({
    id: `mission-${index}`,
    label: move,
    intent: 'what_next',
    prompt: move,
    token: `wilsy://${judge.route || 'workspace'}/mission/${String(index + 1).padStart(2, '0')}`,
    telemetry: `Mission next move: ${move}`,
    mode: 'read_only_execution_stream',
    evidenceRequired: true,
  }));
}

/**
 * @function resolveWilsyActionPayload
 * @description Converts an execution row into a quick-prompt payload understood by the Wilsy operator dock.
 * @param {Object} row - Execution row.
 * @returns {Object} Quick-prompt payload.
 * @collaboration Wilsy AI dock, execution canvas, quick prompt handler, command tokens, and native mission flow.
 */
function resolveWilsyActionPayload(row = {}) {
  return {
    id: row.intent || row.id || 'what_next',
    intent: row.intent || row.id || 'what_next',
    label: row.label || row.prompt || 'Continue',
    prompt: row.prompt || row.label || 'Continue',
    description: row.telemetry || row.token || 'Continue the governed route.',
  };
}

/**
 * @function WilsyOSExecutionCanvas
 * @description Renders the native Wilsy AI execution canvas as a sovereign system cockpit rather than a chat/card rail.
 * @param {Object} props - Component props.
 * @param {Object} props.model - Current Wilsy operator model.
 * @param {boolean} props.visible - Whether the canvas should render.
 * @param {Function} props.onSelect - Action selection callback.
 * @returns {JSX.Element|null} Native execution canvas.
 * @collaboration Wilsy OS AI core engine, operator dock, native execution stream, source route judge, telemetry packs, and evidence anchors.
 */
export default function WilsyOSExecutionCanvas({ model = {}, visible = false, onSelect = () => {} }) {
  if (!visible) {
    return null;
  }

  const rows = resolveWilsyExecutionRows(model);
  const telemetry = resolveWilsyTelemetry(model);
  const judge = resolveWilsyRouteJudge(model);

  if (rows.length === 0) {
    return null;
  }

  return (
    <section className={styles.sovereignExecutionCanvas} data-wilsy-native-execution-canvas="active">
      <div className={styles.sovereignExecutionHeader}>
        <span>SOVEREIGN EXECUTION CANVAS</span>
        <strong>{normalizeWilsyExecutionText(model?.executionCanvas?.summary || model?.missionState?.objective, 'Live state thread')}</strong>
      </div>

      <div className={styles.sovereignTelemetryStrip}>
        {telemetry.slice(0, 4).map((item, index) => (
          <span key={`${item.label || item.value}-${index}`}>
            <strong>{normalizeWilsyExecutionText(item.label, 'Telemetry')}</strong>
            <small>{normalizeWilsyExecutionText(item.value, 'Awaiting signal')}</small>
          </span>
        ))}
      </div>

      <div className={styles.sovereignRouteJudge}>
        <span>SOURCE ROUTE JUDGE</span>
        <strong>{normalizeWilsyExecutionText(judge.status, 'READ_ONLY_ALLOWED')}</strong>
        <small>{normalizeWilsyExecutionText(judge.decision || judge.reason, 'Prepare work only. Mutation requires approval.')}</small>
      </div>

      <div className={styles.sovereignCommandStream}>
        {rows.map((row, index) => (
          <button
            key={row.id || row.token || index}
            type="button"
            className={styles.sovereignCommandRow}
            onClick={() => onSelect(resolveWilsyActionPayload(row))}
          >
            <span>{String(index + 1).padStart(2, '0')}</span>
            <code>{row.token}</code>
            <strong>{row.label}</strong>
            <small>{row.telemetry}</small>
          </button>
        ))}
      </div>
    </section>
  );
}
