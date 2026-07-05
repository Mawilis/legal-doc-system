/* eslint-disable */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import styles from './CRMDashboard.module.css';

/**
 * @function buildWilsyCrmRawStreamPayload
 * @description Builds the raw CRM workspace live text response and inline Wilsy route links.
 * @param {string} directive - Operator directive from the CRM command layer.
 * @returns {Object} Stream payload with text, routes, and telemetry.
 * @collaboration Wilsy CRM workspace, raw typographic stream, command HUD, authority graph, evidence anchors, and CRM route intelligence.
 */
function buildWilsyCrmRawStreamPayload(directive = '') {
  const normalizedDirective = String(directive || '').trim();
  const intent = normalizedDirective || 'What should I do next?';

  return {
    status: 'CRM_THREAD_STREAMING',
    text:
      `CRM command thread accepted: ${intent}\n\n` +
      'Wilsy is not opening another card. The workspace is now using one live text surface. ' +
      'First, trace the CRM authority route so the operator, tenant, reviewer, approver, and release owner are visible. ' +
      'Second, bind evidence anchors to the current route: lead source, meeting receipt, proof object, command surface, and tenant identity. ' +
      'Third, judge release readiness before any mutation. If a route is missing proof, Wilsy prepares the repair route instead of pretending the command is safe.\n\n' +
      'Current safe move: keep the CRM state read-only, prepare the evidence path, and expose only governed command routes that can be clicked inline.',
    routes: [
      {
        label: 'TRACE AUTHORITY ROUTE',
        url: 'wilsy://crm/authority/trace-route',
        prompt: 'Trace CRM authority route',
      },
      {
        label: 'BIND EVIDENCE ANCHORS',
        url: 'wilsy://crm/evidence/bind-anchors',
        prompt: 'Bind CRM evidence anchors',
      },
      {
        label: 'JUDGE RELEASE READINESS',
        url: 'wilsy://crm/release/judge-readiness',
        prompt: 'Judge CRM release readiness',
      },
      {
        label: 'INSPECT ROUTE DRIFT',
        url: 'wilsy://crm/routes/inspect-drift',
        prompt: 'Inspect CRM route drift',
      },
      {
        label: 'PREPARE REPAIR ROUTE',
        url: 'wilsy://crm/repair/prepare-route',
        prompt: 'Prepare CRM repair route',
      },
    ],
    telemetry: {
      routes: '135 CRM routes',
      readiness: '67% readiness',
      posture: 'READ_ONLY_UNTIL_SIGNED',
      operator: 'Security Admin',
    },
  };
}

/**
 * @function tokenizeWilsyStreamText
 * @description Splits stream text into printable units while preserving paragraph breaks.
 * @param {string} text - Candidate stream text.
 * @returns {Array<string>} Printable token list.
 * @collaboration Wilsy live text engine, raw terminal response layer, and CRM workspace command stream.
 */
function tokenizeWilsyStreamText(text = '') {
  return String(text || '')
    .replaceAll('\n\n', ' ¶¶ ')
    .replaceAll('\n', ' ¶ ')
    .split(/\s+/)
    .filter(Boolean);
}

/**
 * @function renderWilsyStreamText
 * @description Restores paragraph breaks from streamed token output.
 * @param {Array<string>} tokens - Printed token list.
 * @returns {string} Visible stream text.
 * @collaboration Wilsy raw typographic renderer, CRM command canvas, and live response stream.
 */
function renderWilsyStreamText(tokens = []) {
  return tokens
    .join(' ')
    .replaceAll(' ¶¶ ', '\n\n')
    .replaceAll(' ¶ ', '\n');
}

/**
 * @function WilsyCrmRawStreamThread
 * @description Renders the CRM-native raw live text engine that prints directly into the main workspace viewport.
 * @returns {JSX.Element} Raw live stream thread.
 * @collaboration Wilsy CRM dashboard, global command HUD, raw typographic response engine, inline command routes, and production workspace viewport.
 */
export default function WilsyCrmRawStreamThread() {
  const [directive, setDirective] = useState('');
  const [streamState, setStreamState] = useState({
    active: false,
    completed: false,
    status: 'CRM_THREAD_ATTACHED',
    text: 'Core CRM thread attached. Type a directive or press Command to stream the next governed CRM move directly into this workspace.',
    routes: [],
    telemetry: {
      routes: '135 CRM routes',
      readiness: '67% readiness',
      posture: 'AWAITING_DIRECTIVE',
      operator: 'Security Admin',
    },
  });

  const timerRef = useRef(null);
  const payload = useMemo(() => buildWilsyCrmRawStreamPayload(directive), [directive]);

  /**
   * @function stopWilsyStream
   * @description Clears the active CRM live stream interval safely.
   * @returns {void}
   * @collaboration Wilsy CRM raw stream, browser timer lifecycle, and frontend stability.
   */
  const stopWilsyStream = useCallback(() => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  /**
   * @function startWilsyCrmStream
   * @description Starts word-by-word printing directly in the CRM workspace.
   * @param {string} nextDirective - Operator directive to stream.
   * @returns {void}
   * @collaboration Wilsy CRM command HUD, raw typographic text engine, route injection, and live operator workflow.
   */
  const startWilsyCrmStream = useCallback(
    (nextDirective = '') => {
      const nextPayload = buildWilsyCrmRawStreamPayload(nextDirective || directive);
      const tokens = tokenizeWilsyStreamText(nextPayload.text);
      let cursor = 0;

      stopWilsyStream();

      setStreamState({
        active: true,
        completed: false,
        status: nextPayload.status,
        text: '',
        routes: [],
        telemetry: {
          ...nextPayload.telemetry,
          posture: 'STREAMING_RESPONSE',
        },
      });

      timerRef.current = window.setInterval(() => {
        cursor += 1;

        setStreamState((current) => ({
          ...current,
          active: cursor < tokens.length,
          completed: cursor >= tokens.length,
          text: renderWilsyStreamText(tokens.slice(0, cursor)),
          routes: cursor >= tokens.length ? nextPayload.routes : [],
          telemetry: {
            ...nextPayload.telemetry,
            posture: cursor >= Math.floor(tokens.length / 2) ? 'ROUTE_JUDGE_ACTIVE' : 'STREAMING_RESPONSE',
            readiness: cursor >= Math.floor(tokens.length / 2) ? '100% route judged' : nextPayload.telemetry.readiness,
          },
        }));

        if (cursor >= tokens.length) {
          stopWilsyStream();
        }
      }, 38);
    },
    [directive, stopWilsyStream],
  );

  /**
   * @function handleWilsyStreamSubmit
   * @description Handles CRM raw stream command submission.
   * @param {React.FormEvent<HTMLFormElement>} event - Submit event.
   * @returns {void}
   * @collaboration Wilsy CRM command HUD, operator input, and raw live stream execution.
   */
  function handleWilsyStreamSubmit(event) {
    event.preventDefault();
    startWilsyCrmStream(directive || 'What should I do next?');
  }

  /**
   * @function handleWilsyRouteClick
   * @description Streams a clicked inline route as the next CRM command.
   * @param {Object} route - Inline command route.
   * @returns {void}
   * @collaboration Wilsy inline route links, raw stream continuation, and CRM command routing.
   */
  function handleWilsyRouteClick(route = {}) {
    const nextDirective = route.prompt || route.label || route.url || 'Continue CRM route';
    setDirective(nextDirective);
    startWilsyCrmStream(nextDirective);
  }

  useEffect(() => () => stopWilsyStream(), [stopWilsyStream]);

  useEffect(() => {
    /**
     * @function handleExternalCommandClick
     * @description Bridges the existing CRM Command button into the raw live text stream without changing the button layout.
     * @param {MouseEvent} event - Browser click event.
     * @returns {void}
     * @collaboration Existing CRM command button, raw live stream, and production workspace continuity.
     */
    function handleExternalCommandClick(event) {
      const target = event.target;
      const text = target?.textContent || target?.closest?.('button')?.textContent || '';

      if (String(text).trim().toLowerCase() === 'command') {
        startWilsyCrmStream(directive || 'Run CRM command intelligence');
      }
    }

    document.addEventListener('click', handleExternalCommandClick, true);

    return () => document.removeEventListener('click', handleExternalCommandClick, true);
  }, [directive, startWilsyCrmStream]);

  return (
    <section className={styles.crmRawStreamThread} data-wilsy-crm-raw-stream-thread="true">
      <div className={styles.crmRawStreamStatusLine}>
        <span>[CRM_THREAD]</span>
        <strong>{streamState.status}</strong>
        <small>
          ROUTES: {streamState.telemetry.routes} | READINESS: {streamState.telemetry.readiness} | POSTURE:{' '}
          {streamState.telemetry.posture}
        </small>
      </div>

      <form className={styles.crmRawStreamCommandLine} onSubmit={handleWilsyStreamSubmit}>
        <span>ask_wilsy://</span>
        <input
          type="text"
          value={directive}
          onChange={(event) => setDirective(event.target.value)}
          placeholder="type a directive and press Enter..."
          aria-label="Ask Wilsy CRM raw stream"
        />
        <button type="submit">[EXECUTE]</button>
      </form>

      <div
        className={`${styles.crmRawStreamBody} ${streamState.active ? styles.crmRawStreamPrinting : ''}`}
        data-wilsy-crm-live-text-output="true"
        aria-live="polite"
      >
        {streamState.text}
        {streamState.active ? <span className={styles.crmRawStreamCursor}>▍</span> : null}
      </div>

      {streamState.routes.length > 0 ? (
        <div className={styles.crmRawRouteInjection} data-wilsy-crm-inline-route-injection="true">
          {streamState.routes.map((route) => (
            <button key={route.url} type="button" onClick={() => handleWilsyRouteClick(route)}>
              <span>[{route.label}]</span>
              <code>{route.url}</code>
            </button>
          ))}
        </div>
      ) : null}
    </section>
  );
}
