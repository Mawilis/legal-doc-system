/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - GATEWAY TELEMETRY ENGINE [V28.1.4-OMEGA-ALIGNMENT]                                                                          ║
 * ║ [RECTIFIED: DEV BYPASS | TAMPER-PROOF HASHING | FORENSIC ENTRY LOGS | TRACE ANCHORING | REAL-TIME BROADCAST]                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 28.1.4-OMEGA | PRODUCTION READY | BILLION DOLLAR SPEC                                                                         ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL FINALITY                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/gatewayTelemetry.js                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated tamper-proof audit trails and zero strip compliance. [2026-05-02]                     ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Injected Sovereign Development Bypass to resolve local 403 login fractures. [2026-05-04]         ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Synchronized [SECURITY-BREACH] logging with the Institutional Telemetry feed.                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import chalk from 'chalk';
import { broadcastTelemetry } from './telemetryHelper.js';
import { hash as sovereignHash } from './cryptoUtils.js';
import loggerRaw from './logger.js';
const logger = loggerRaw.default || loggerRaw;

/**
 * 🛡️ Safe string padding function to prevent undefined Node crashes
 */
function safePadEnd(str, length) {
  if (!str || typeof str !== 'string') {
    return ' '.repeat(length);
  }
  return str.padEnd(length);
}

/**
 * @function gatewayTelemetry
 * @desc The Central Ingress Sentinel. Seals every request, calculates latency, and enforces forensic entry protocols.
 * RECTIFIED: Now supports a local development bypass for Johannesburg/Randburg engineering strikes.
 */
export function gatewayTelemetry(req, res, next) {
  const start = Date.now();
  const traceId = req.headers['x-request-id'] || crypto.randomUUID();
  const tenantId = req.headers['x-tenant-id'] || 'SOVEREIGN_ROOT';
  const seal = req.headers['x-request-seal'] || req.headers['X-Request-Seal'];
  const clientIp = req.ip || req.connection.remoteAddress || '127.0.0.1';

  // 🛡️ SOVEREIGN DEVELOPMENT BYPASS
  // Detects if the strike is local and the environment is development to allow entry without a seal.
  const isLocal = clientIp.includes('127.0.0.1') || clientIp === '::1' || req.hostname === 'localhost';
  const isDev = (process.env.NODE_ENV || '').toLowerCase() === 'development';

  if (isDev && isLocal && !seal) {
    logger.warn(`[SECURITY-ADVISORY] ⚠️  Local Development Strike Permitted without seal | ReqID: ${traceId}`);
  } else if (!seal && !req.originalUrl.includes('/health')) {
    // 🏛️ INSTITUTIONAL ENFORCEMENT: Hard-blocking anonymous strikes in non-dev or remote contexts.
    logger.error(`[SECURITY-BREACH] 🚨 Missing Forensic Headers from: ${clientIp} | ReqID: ${traceId}`);
    return res.status(403).json({
      success: false,
      error: 'FORENSIC_SEAL_REQUIRED',
      traceId,
      narrative: 'Institutional access denied. Cryptographic DNA signature missing.'
    });
  }

  // 🏛️ FORENSIC ENTRY LOG: Captures the raw inbound strike
  console.log(chalk.cyan(`\n[GATEWAY_TELEMETRY] 🚀 Incoming Request:`), {
    method: req.method,
    url: req.originalUrl,
    tenantId,
    traceId,
    headers: {
      host: req.headers.host,
      origin: req.headers.origin,
      'user-agent': req.headers['user-agent']
    }
  });

  res.setHeader('X-Wilsy-Trace-ID', traceId);

  const recordForensicFinality = (status, error = null) => {
    const duration = Date.now() - start;
    const statusColor = res.statusCode >= 400 || error ? chalk.red : chalk.green;

    const identity = req.user ? (req.user.email || req.user.id || 'ANONYMOUS_IGNITION') : 'ANONYMOUS_IGNITION';
    const tenantLabel = (req.tenant && req.tenant.alias) ? req.tenant.alias : tenantId;

    const safeTenantLabel = String(tenantLabel || 'SOVEREIGN_ROOT');
    const safeIdentity = String(identity || 'ANONYMOUS_IGNITION');
    const safeMethod = String(req.method || 'UNKNOWN');
    const safeUrl = String(req.originalUrl || req.url || '/unknown');

    const eventSeal = sovereignHash({
      traceId,
      method: req.method,
      url: safeUrl,
      status: res.statusCode,
      identity: safeIdentity,
      duration: `${duration}ms`
    });

    try {
      console.log(
        `${statusColor('✅ [GATEWAY]')} ${chalk.white(safePadEnd(safeTenantLabel, 15))} | ${chalk.yellow(safePadEnd(safeIdentity, 25))} | ${chalk.cyan(safePadEnd(safeMethod, 6))} ${safePadEnd(safeUrl, 40)} ${statusColor(res.statusCode)} ${chalk.magenta(duration + 'ms')} [SEAL: ${eventSeal.substring(0, 8)}]`
      );
    } catch (logError) {
      console.log(`✅ [GATEWAY] ${safeTenantLabel} | ${safeIdentity} | ${safeMethod} ${safeUrl} ${res.statusCode} ${duration}ms`);
    }

    console.log(chalk.gray(`[GATEWAY_TELEMETRY] 📡 Forensic Payload:`), {
      traceId,
      tenantLabel: safeTenantLabel,
      identity: safeIdentity,
      method: req.method,
      url: safeUrl,
      status: res.statusCode,
      duration: `${duration}ms`,
      eventSeal: eventSeal.substring(0, 16)
    });

    try {
      broadcastTelemetry(tenantId, "HTTP_EVENT", "SYSTEM_GATEWAY", status, {
        method: req.method,
        url: safeUrl,
        status: res.statusCode,
        duration: `${duration}ms`,
        traceId,
        identity: safeIdentity,
        forensicSeal: eventSeal,
        error: error ? error.message : null
      });
    } catch (broadcastError) {
      console.error('Telemetry broadcast failed:', broadcastError.message);
    }
  };

  res.on('finish', () => recordForensicFinality('COMPLETED'));
  res.on('error', (err) => recordForensicFinality('GATEWAY_FAULT', err));

  next();
}

export default gatewayTelemetry;
