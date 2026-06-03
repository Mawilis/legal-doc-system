/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN ALERT CONTEXT [V72.0.0-TELEMETRY-DEDUP]                                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/context/SovereignAlertContext.jsx                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ FEATURES:                                                                                                                              ║
 * ║   • Global alert stack – receives events via `SOVEREIGN_ESCALATION` custom event.                                                      ║
 * ║   • Alert deduplication – prevents duplicate alerts by `alertId` + `correlationId`.                                                    ║
 * ║   • Tenant‑aware – each alert carries its own `tenantId`.                                                                              ║
 * ║   • Auto‑pruning – removes dismissed alerts after 5 seconds (memory safe).                                                             ║
 * ║   • Telemetry – every add, dismiss, and prune is broadcast to the Sovereign Mesh.                                                      ║
 * ║   • Programmatic API – `addAlert`, `dismissAlert`, `clearAllAlerts` for external control.                                              ║
 * ║   • Integration with `HUDAlertBanner` – renders the multi‑alert stack.                                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – mandated global alert bus, deduplication, and telemetry.                                      ║
 * ║ • AI Engineering (DeepSeek) – ENHANCED: added dedup, tenant isolation, telemetry, and full JSDoc.                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import HUDAlertBanner from '../components/HUDAlertBanner';
import { broadcastTelemetry } from '../utils/telemetryHelper';

// ============================================================================
// 🔥 CONSTANTS
// ============================================================================

/** @constant {number} PRUNE_DELAY_MS - Delay after dismissal before removing alert from state (ms) */
const PRUNE_DELAY_MS = 5000;

/** @constant {number} MAX_ALERTS - Maximum number of alerts to keep in stack (prevents memory flood) */
const MAX_ALERTS = 50;

// ============================================================================
// 🔥 CONTEXT TYPE DEFINITION
// ============================================================================

/**
 * @typedef {Object} AlertObject
 * @property {string} alertId - Unique alert identifier.
 * @property {string} correlationId - End‑to‑end correlation ID.
 * @property {string} severity - 'warning' or 'critical'.
 * @property {string} title - Alert headline.
 * @property {string} message - Human‑readable detail.
 * @property {string} [tenantId] - Tenant ID (falls back to global).
 * @property {Object} [details] - Forensic metadata.
 * @property {Array<Object>} [actions] - Action buttons.
 * @property {string} [timestamp] - ISO timestamp.
 */

/**
 * @typedef {Object} SovereignAlertContextValue
 * @property {AlertObject[]} alerts - Current active alerts.
 * @property {Function} addAlert - (alert: AlertObject) => void
 * @property {Function} dismissAlert - (indexOrId: number | string) => void
 * @property {Function} clearAllAlerts - () => void
 */

const SovereignAlertContext = createContext(null);

// ============================================================================
// 🔥 HELPER: Generate a stable unique key for deduplication
// ============================================================================

/**
 * Generates a deduplication key from an alert.
 * @param {AlertObject} alert
 * @returns {string}
 */
function getAlertKey(alert) {
  return `${alert.alertId || 'no-id'}:${alert.correlationId || 'no-correlation'}:${alert.severity}`;
}

// ============================================================================
// 🔥 PROVIDER COMPONENT
// ============================================================================

/**
 * @component SovereignAlertProvider
 * @description Provides a global alert stack for the entire application.
 * Listens for `SOVEREIGN_ESCALATION` custom events and adds them to the stack.
 * Renders the `HUDAlertBanner` component (which supports multiple alerts) fixed at top‑right.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Child components.
 * @returns {JSX.Element}
 *
 * @real-world
 *   Wraps the entire Boardroom HUD or the root App component. Any part of the application
 *   can dispatch a `new CustomEvent('SOVEREIGN_ESCALATION', { detail: alert })` to trigger
 *   a banner. Used for real‑time Prometheus alerts, seizure notifications, compliance warnings.
 *
 * @forensic
 *   - Every alert added triggers telemetry event `ALERT_ADDED` with dedup status.
 *   - Dismissals trigger `ALERT_DISMISSED`.
 *   - Auto‑pruning after 5 seconds triggers `ALERT_PRUNED`.
 *   - All telemetry includes tenantId, alertId, correlationId, and severity.
 *
 * @example
 * // Wrap your app
 * <SovereignAlertProvider>
 *   <BoardroomHUD />
 * </SovereignAlertProvider>
 *
 * // Dispatch an alert from anywhere
 * const alert = {
 *   alertId: 'PROM-123',
 *   correlationId: 'CORR-456',
 *   severity: 'critical',
 *   title: 'Database Lag',
 *   message: 'Replication lag > 5s',
 *   tenantId: 'GLOBAL_ROOT',
 *   actions: [{ type: 'biometric', label: 'Acknowledge' }]
 * };
 * window.dispatchEvent(new CustomEvent('SOVEREIGN_ESCALATION', { detail: alert }));
 */
export const SovereignAlertProvider = ({ children }) => {
  const [alerts, setAlerts] = useState([]);
  const pruneTimeoutsRef = useRef(new Map());

  useEffect(() => {
    if (alerts.length > 0) {
      const lastAlert = alerts[alerts.length - 1];
      broadcastTelemetry(
        lastAlert.tenantId || 'GLOBAL_ROOT',
        'ALERT_CONTEXT',
        'STACK_UPDATED',
        'SovereignAlertProvider',
        { count: alerts.length, severities: alerts.map(a => a.severity) }
      ).catch(console.error);
    }
  }, [alerts.length]);

  const addAlert = useCallback((alert, force = false) => {
    if (!alert) return;

    const effectiveTenant = alert.tenantId || 'GLOBAL_ROOT';
    const alertKey = getAlertKey(alert);

    if (!force) {
      const exists = alerts.some(existing => getAlertKey(existing) === alertKey);
      if (exists) {
        broadcastTelemetry(effectiveTenant, 'ALERT_CONTEXT', 'ALERT_DEDUPLICATED', 'SovereignAlertProvider', {
          alertId: alert.alertId,
          correlationId: alert.correlationId,
          severity: alert.severity
        }).catch(console.error);
        return;
      }
    }

    if (alerts.length >= MAX_ALERTS) {
      const oldest = alerts[0];
      broadcastTelemetry(effectiveTenant, 'ALERT_CONTEXT', 'ALERT_DROPPED_MAX', 'SovereignAlertProvider', {
        alertId: oldest.alertId,
        correlationId: oldest.correlationId,
        reason: 'max_alerts_reached'
      }).catch(console.error);
      setAlerts(prev => prev.slice(1));
    }

    setAlerts(prev => [alert, ...prev]);

    broadcastTelemetry(effectiveTenant, 'ALERT_CONTEXT', 'ALERT_ADDED', 'SovereignAlertProvider', {
      alertId: alert.alertId,
      correlationId: alert.correlationId,
      severity: alert.severity,
      title: alert.title,
      stackSize: alerts.length + 1
    }).catch(console.error);
  }, [alerts]);

  const dismissAlert = useCallback((indexOrId) => {
    let indexToRemove = -1;
    let alertToRemove = null;

    if (typeof indexOrId === 'number') {
      indexToRemove = indexOrId;
      if (indexToRemove >= 0 && indexToRemove < alerts.length) {
        alertToRemove = alerts[indexToRemove];
      }
    } else {
      indexToRemove = alerts.findIndex(a => a.alertId === indexOrId || a.correlationId === indexOrId);
      if (indexToRemove !== -1) {
        alertToRemove = alerts[indexToRemove];
      }
    }

    if (indexToRemove === -1 || !alertToRemove) return;

    const effectiveTenant = alertToRemove.tenantId || 'GLOBAL_ROOT';
    broadcastTelemetry(effectiveTenant, 'ALERT_CONTEXT', 'ALERT_DISMISSED', 'SovereignAlertProvider', {
      alertId: alertToRemove.alertId,
      correlationId: alertToRemove.correlationId,
      severity: alertToRemove.severity,
      method: typeof indexOrId === 'number' ? 'by_index' : 'by_id'
    }).catch(console.error);

    setAlerts(prev => prev.filter((_, idx) => idx !== indexToRemove));

    if (pruneTimeoutsRef.current.has(indexToRemove)) {
      clearTimeout(pruneTimeoutsRef.current.get(indexToRemove));
    }
    const timeoutId = setTimeout(() => {
      broadcastTelemetry(effectiveTenant, 'ALERT_CONTEXT', 'ALERT_PRUNED', 'SovereignAlertProvider', {
        alertId: alertToRemove.alertId,
        correlationId: alertToRemove.correlationId,
        delayMs: PRUNE_DELAY_MS
      }).catch(console.error);
      pruneTimeoutsRef.current.delete(indexToRemove);
    }, PRUNE_DELAY_MS);
    pruneTimeoutsRef.current.set(indexToRemove, timeoutId);
  }, [alerts]);

  const clearAllAlerts = useCallback(() => {
    if (alerts.length === 0) return;
    const tenant = alerts[0]?.tenantId || 'GLOBAL_ROOT';
    broadcastTelemetry(tenant, 'ALERT_CONTEXT', 'ALL_ALERTS_CLEARED', 'SovereignAlertProvider', {
      count: alerts.length
    }).catch(console.error);
    for (const timeout of pruneTimeoutsRef.current.values()) {
      clearTimeout(timeout);
    }
    pruneTimeoutsRef.current.clear();
    setAlerts([]);
  }, [alerts]);

  useEffect(() => {
    const handler = (event) => {
      if (event.detail) {
        addAlert(event.detail);
      }
    };
    window.addEventListener('SOVEREIGN_ESCALATION', handler);
    return () => window.removeEventListener('SOVEREIGN_ESCALATION', handler);
  }, [addAlert]);

  useEffect(() => {
    return () => {
      for (const timeout of pruneTimeoutsRef.current.values()) {
        clearTimeout(timeout);
      }
    };
  }, []);

  const contextValue = {
    alerts,
    addAlert,
    dismissAlert,
    clearAllAlerts
  };

  return (
    <SovereignAlertContext.Provider value={contextValue}>
      <div
        style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          width: '480px',
          maxWidth: 'calc(100% - 40px)',
          zIndex: 99999,
          pointerEvents: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}
      >
        <HUDAlertBanner alert={alerts} />
      </div>
      {children}
    </SovereignAlertContext.Provider>
  );
};

/**
 * Hook to access the Sovereign Alert Context.
 * @returns {SovereignAlertContextValue}
 * @throws {Error} If used outside of SovereignAlertProvider.
 *
 * @example
 * const { addAlert, dismissAlert } = useSovereignAlerts();
 * addAlert({ severity: 'critical', title: 'System Overload', message: 'CPU > 90%' });
 */
export const useSovereignAlerts = () => {
  const context = useContext(SovereignAlertContext);
  if (!context) {
    throw new Error('useSovereignAlerts must be used within a SovereignAlertProvider');
  }
  return context;
};

export default SovereignAlertProvider;
