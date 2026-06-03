/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN HUD ALERT BANNER [V72.0.0-MULTI-STACK-AUTO-DISMISS]                                                              ║
 * ║ [MULTI-ALERT QUEUE | AUTO-DISMISS TIMERS | AUDIO/VIBRATION | BIOMETRIC LOCKOUT MESSAGING | FULL JSDOC]                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 72.0.0-MULTI-STACK-AUTO-DISMISS | PRODUCTION READY | TRILLION DOLLAR SPEC                                                     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/HUDAlertBanner.jsx                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – MANDATE: Multi‑alert stacking, auto‑dismiss, and audio/vibration for critical events.        ║
 * ║ • AI Engineering (DeepSeek) – ENHANCED: added alert queue management, auto‑dismiss timers, lockout reason display, and telemetry.     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import './HUDAlertBanner.css';
import { handleBiometricAcknowledge } from '../utils/BiometricHandler';
import { broadcastTelemetry } from '../utils/telemetryHelper';

// ============================================================================
// 🔥 CONSTANTS
// ============================================================================

/** @constant {number} AUTO_DISMISS_WARNING_MS - 30 seconds for warning alerts */
const AUTO_DISMISS_WARNING_MS = 30 * 1000;

/** @constant {number|null} AUTO_DISMISS_CRITICAL_MS - Never auto‑dismiss critical alerts */
const AUTO_DISMISS_CRITICAL_MS = null;

// ============================================================================
// 🔥 HELPER: Play audio / vibrate for critical alerts
// ============================================================================

/**
 * Plays a short beep sound (if supported by browser) and vibrates for critical alerts.
 * @private
 */
function playCriticalAlertSoundAndVibrate() {
  try {
    if (navigator.vibrate) {
      navigator.vibrate(200);
    }
    if (window.AudioContext || window.webkitAudioContext) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const ctx = new AudioCtx();
      const oscillator = ctx.createOscillator();
      const gain = ctx.createGain();
      oscillator.connect(gain);
      gain.connect(ctx.destination);
      oscillator.frequency.value = 880;
      gain.gain.value = 0.2;
      oscillator.start();
      gain.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + 0.5);
      oscillator.stop(ctx.currentTime + 0.5);
      setTimeout(() => ctx.close(), 600);
    }
  } catch (e) {}
}

// ============================================================================
// 🔥 SUB-COMPONENT: Single Alert Banner (with its own dismiss logic)
// ============================================================================

/**
 * @component SingleAlert
 * @private
 * @description Renders a single alert banner with its own dismissal, biometric handling, and auto‑dismiss timer.
 * @param {Object} props
 * @param {Object} props.alert - Alert payload
 * @param {string} props.tenantId - Tenant ID
 * @param {Function} props.onDismiss - Callback when banner is dismissed (removed from stack)
 * @param {boolean} props.isAutoDismissEnabled - Whether auto‑dismiss is allowed for this severity
 * @returns {JSX.Element}
 */
const SingleAlert = ({ alert, tenantId, onDismiss, isAutoDismissEnabled }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [lockoutMessage, setLockoutMessage] = useState(null);
  const dismissTimerRef = useRef(null);

  const effectiveTenantId = tenantId || alert?.tenantId || 'WILSY_GLOBAL_ROOT';
  const { severity, title, message, details = {}, actions = [], timestamp, alertId, correlationId } = alert || {};

  // Auto‑dismiss timer setup
  useEffect(() => {
    if (isAutoDismissEnabled && severity !== 'critical') {
      dismissTimerRef.current = setTimeout(() => {
        broadcastTelemetry(effectiveTenantId, 'ALERT_BANNER', 'AUTO_DISMISSED', 'HUDAlertBanner', {
          alertId,
          correlationId,
          severity,
          autoDismissMs: AUTO_DISMISS_WARNING_MS
        });
        onDismiss();
      }, AUTO_DISMISS_WARNING_MS);
    }
    return () => {
      if (dismissTimerRef.current) clearTimeout(dismissTimerRef.current);
    };
  }, [isAutoDismissEnabled, severity, alertId, correlationId, effectiveTenantId, onDismiss]);

  // Telemetry: Alert rendered (only once)
  useEffect(() => {
    broadcastTelemetry(effectiveTenantId, 'ALERT_BANNER', 'ALERT_RENDERED', 'HUDAlertBanner', {
      alertId,
      correlationId,
      severity,
      title,
      details: { ...details, timestamp: timestamp || new Date().toISOString() }
    });
    if (severity === 'critical') {
      playCriticalAlertSoundAndVibrate();
    }
  }, []);

  const executeAction = useCallback(async (action) => {
    if (!action) return;

    if (action.type === 'biometric') {
      if (isProcessing) return;
      setIsProcessing(true);
      setLockoutMessage(null);
      broadcastTelemetry(effectiveTenantId, 'ALERT_BANNER', 'BIOMETRIC_ATTEMPT', 'HUDAlertBanner', {
        alertId,
        correlationId,
        severity
      });
      try {
        await handleBiometricAcknowledge(alert, effectiveTenantId);
        broadcastTelemetry(effectiveTenantId, 'ALERT_BANNER', 'BIOMETRIC_SUCCESS', 'HUDAlertBanner', {
          alertId,
          correlationId,
          severity
        });
        if (dismissTimerRef.current) clearTimeout(dismissTimerRef.current);
        onDismiss();
      } catch (error) {
        console.error('[HUD_BANNER] Biometric verification failed:', error);
        let userMessage = error.message;
        if (userMessage.includes('locked')) {
          const match = userMessage.match(/locked until ([\d:]+ [APM]+)/);
          if (match) {
            userMessage = `Biometric locked until ${match[1]}. Contact support or use recovery token.`;
          } else {
            userMessage = 'Biometric verification locked due to repeated failures. Please wait or use override token.';
          }
          setLockoutMessage(userMessage);
        } else {
          setLockoutMessage(userMessage);
        }
        broadcastTelemetry(effectiveTenantId, 'ALERT_BANNER', 'BIOMETRIC_FAILURE', 'HUDAlertBanner', {
          alertId,
          correlationId,
          severity,
          error: error.message
        });
      } finally {
        setIsProcessing(false);
      }
    } else if (action.type === 'link' && action.href) {
      window.open(action.href, '_blank', 'noopener,noreferrer');
      broadcastTelemetry(effectiveTenantId, 'ALERT_BANNER', 'LINK_CLICKED', 'HUDAlertBanner', {
        alertId,
        correlationId,
        severity,
        href: action.href
      });
    } else {
      console.warn('[HUD_BANNER] Unknown action type:', action.type);
      if (action.dismissOnClick) {
        if (dismissTimerRef.current) clearTimeout(dismissTimerRef.current);
        onDismiss();
      }
    }
  }, [alert, effectiveTenantId, alertId, correlationId, severity, isProcessing, onDismiss]);

  const handleManualDismiss = useCallback(() => {
    if (dismissTimerRef.current) clearTimeout(dismissTimerRef.current);
    broadcastTelemetry(effectiveTenantId, 'ALERT_BANNER', 'ALERT_DISMISSED', 'HUDAlertBanner', {
      alertId,
      correlationId,
      severity,
      dismissedAt: new Date().toISOString(),
      method: 'manual'
    });
    onDismiss();
  }, [effectiveTenantId, alertId, correlationId, severity, onDismiss]);

  const bannerClass = severity === 'critical' ? 'hud-banner-critical' : 'hud-banner-warning';
  const displayTimestamp = timestamp ? new Date(timestamp).toLocaleString() : new Date().toLocaleString();

  return (
    <div className={`hud-banner ${bannerClass}`}>
      <button className="hud-banner-close" onClick={handleManualDismiss} aria-label="Dismiss alert">✕</button>
      <div className="hud-banner-header">
        <h4 className="hud-banner-title">{title}</h4>
        <span className="hud-banner-timestamp">{displayTimestamp}</span>
      </div>

      <div className="hud-banner-body">
        <p className="hud-banner-message">{message}</p>
        {Object.keys(details).length > 0 && (
          <div className="hud-banner-details">
            {details.traceId && <p><strong>Trace ID:</strong> {details.traceId}</p>}
            {details.retryCount !== undefined && <p><strong>Retry Count:</strong> {details.retryCount}</p>}
            {details.lastError && <p><strong>Last Error:</strong> {details.lastError}</p>}
            {details.failureCount !== undefined && <p><strong>Failure Count:</strong> {details.failureCount}</p>}
            {details.reason && <p><strong>Reason:</strong> {details.reason}</p>}
          </div>
        )}
        {lockoutMessage && (
          <div className="hud-banner-lockout-warning">
            ⚠️ {lockoutMessage}
          </div>
        )}
      </div>

      {actions.length > 0 && (
        <div className="hud-banner-actions">
          {actions.map((action, idx) => (
            action.type === 'link' ? (
              <a
                key={idx}
                href={action.href}
                className="hud-banner-link"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => executeAction(action)}
              >
                {action.label}
              </a>
            ) : (
              <button
                key={idx}
                className="hud-banner-btn"
                onClick={() => executeAction(action)}
                disabled={isProcessing && action.type === 'biometric'}
              >
                {isProcessing && action.type === 'biometric' ? (
                  <span className="hud-banner-spinner">⏳</span>
                ) : action.label}
              </button>
            )
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================================================
// 🔥 MAIN COMPONENT: HUDAlertBanner (supports multiple alerts)
// ============================================================================

/**
 * @component HUDAlertBanner
 * @description Renders a stack of sovereign alerts (supports single alert or array).
 * Each banner can be dismissed independently; critical alerts never auto‑dismiss,
 * warning alerts auto‑dismiss after 30 seconds (if not acknowledged).
 *
 * @param {Object} props - React props.
 * @param {Object|Array<Object>} props.alert - Single alert payload or array of alerts.
 * @param {string} [props.tenantId] - Tenant identifier (falls back to alert.tenantId or 'WILSY_GLOBAL_ROOT').
 * @returns {JSX.Element|null} Rendered stack of banners, or null if none.
 *
 * @real-world
 *   Embedded in the Boardroom HUD to display real‑time Prometheus alerts.
 *   Multiple alerts stack vertically; critical alerts remain until dismissed by a director.
 *   Auto‑dismiss reduces noise for transient warnings.
 *
 * @forensic
 *   - Every alert mount triggers `ALERT_RENDERED` telemetry.
 *   - Auto‑dismiss triggers `AUTO_DISMISSED` telemetry.
 *   - Manual dismiss triggers `ALERT_DISMISSED` telemetry.
 *   - Biometric attempts and failures are fully logged.
 *   - Stack changes (add/remove) are broadcast.
 *
 * @example
 * // Single alert
 * <HUDAlertBanner alert={singleAlert} tenantId="GLOBAL_ROOT" />
 *
 * // Multiple alerts
 * <HUDAlertBanner alert={[alert1, alert2]} />
 */
const HUDAlertBanner = ({ alert, tenantId }) => {
  const initialAlerts = Array.isArray(alert) ? alert : (alert ? [alert] : []);
  const [activeAlerts, setActiveAlerts] = useState(initialAlerts);

  useEffect(() => {
    const newAlerts = Array.isArray(alert) ? alert : (alert ? [alert] : []);
    if (newAlerts.length !== activeAlerts.length || JSON.stringify(newAlerts) !== JSON.stringify(activeAlerts)) {
      setActiveAlerts(newAlerts);
      const effectiveTenant = tenantId || newAlerts[0]?.tenantId || 'WILSY_GLOBAL_ROOT';
      broadcastTelemetry(effectiveTenant, 'ALERT_STACK', 'STACK_UPDATED', 'HUDAlertBanner', {
        count: newAlerts.length,
        severities: newAlerts.map(a => a.severity)
      });
    }
  }, [alert, activeAlerts, tenantId]);

  const removeAlert = useCallback((indexToRemove) => {
    setActiveAlerts(prev => prev.filter((_, idx) => idx !== indexToRemove));
  }, []);

  if (activeAlerts.length === 0) return null;

  return (
    <div className="hud-alert-stack">
      {activeAlerts.map((singleAlert, idx) => (
        <SingleAlert
          key={singleAlert.alertId || singleAlert.correlationId || idx}
          alert={singleAlert}
          tenantId={tenantId}
          onDismiss={() => removeAlert(idx)}
          isAutoDismissEnabled={singleAlert.severity !== 'critical'}
        />
      ))}
    </div>
  );
};

export default HUDAlertBanner;
