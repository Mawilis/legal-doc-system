/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TELEMETRY VALIDATION SCHEMA [V1.3.0-FORTRESS-HUD]                                                                           ║
 * ║ [SEVERITY GRADING | TRACE ANCHORS | TIMESTAMP NORMALIZATION | ELASTIC METADATA]                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.3.0-FORTRESS-HUD | PRODUCTION READY | BILLION DOLLAR SPEC                                                                   ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/validators/telemetryValidator.js                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated severity grading and forensic trace normalization.                                   ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Injected trace anchors and timestamp normalization to prevent forensic gaps. [2026-05-11]        ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Locked eventType and severity valid sets for consistent HUD visualization. [2026-05-11]          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import Joi from 'joi';

export const pulseSchema = Joi.object({
  tenantId: Joi.string().default('GLOBAL_ROOT'),
  userId: Joi.string().allow('ANONYMOUS', null),
  sessionId: Joi.string().allow('', null),
  event: Joi.string().required(),
  eventType: Joi.string()
    .valid('HEARTBEAT', 'SYSTEM_EVENT', 'SECURITY_EVENT', 'PERFORMANCE_METRIC', 'BINARY_STRIKE')
    .default('HEARTBEAT'),
  severity: Joi.string()
    .valid('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
    .default('LOW'),
  traceId: Joi.string().optional(),
  timestamp: Joi.date().default(() => new Date(), 'current time'),
  metrics: Joi.object().unknown(true).default({}),
  metadata: Joi.object().unknown(true).default({})
}).unknown(true); // 🏛️ ANCHOR: .unknown(true) allows high-velocity ingestion without 400 fractures
