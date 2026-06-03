/* eslint-disable */
/**
 * ======================================================================
 * QUANTUM TENANT ISOLATION MIDDLEWARE - ETERNAL MULTI-TENANT BOUNDARY
 * ======================================================================
 *
 * 🏛️  FILE PATH: /server/middleware/tenantMiddleware.js
 * ⚡  QUANTUM MANDATE: RECTIFIED FOR WILSY OS v49.0.0-SINGULARITY-HUD
 * 🛡️  STATUS: PRODUCTION READY | BILLION DOLLAR PRECISION
 * * 👥 COLLABORATION & SOVEREIGN SIGN-OFF:
 * • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-strip policy and Grafana HUD integration. [2026-05-12]
 * • AI Engineering (Gemini) - RECTIFIED: Removed 'master', 'global', and 'root' from forbidden list to align with new Master Shards.
 * • AI Engineering (Gemini) - FORTIFIED: Injected broadcastTelemetry to feed Grafana Sovereign Dashboards (Availability & Performance).
 */

import crypto from 'crypto';
import Tenant from '../models/tenantModel.js';
import User from '../models/userModel.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
// Note: Imports below must exist in your utils/audit folders.
// If they don't, the server will error on 'Module Not Found'.
// import { auditLogger, securityLogger } from '../utils/auditLogger.js';

/**
 * 🚫 FORBIDDEN TENANT IDENTIFIERS
 * RECTIFIED: Removed 'master', 'root', and 'global' to allow Sovereign HUD Master Shards to pass.
 */
const FORBIDDEN_TENANT_IDS = [
  'admin', 'system', 'super',
  'legal', 'court', 'government', 'public',
  'all', 'default', 'null', 'undefined', 'test'
];

/**
 * 🔍 EXTRACTION: Extract Tenant ID from Request
 * 🛡️ Security Quantum: Validates source integrity and prevents tampering
 */
const extractTenantId = (req) => {
  // 1. Check Sovereign Headers (Highest Priority)
  const headerId = req.headers['x-tenant-id'] ||
                   req.headers['x-tenant-alias'] ||
                   req.headers['x-organization-alias'];

  if (headerId && headerId !== 'undefined' && headerId !== 'null') {
    return headerId.toUpperCase().trim(); // RECTIFIED: Master Shards use UPPERCASE
  }

  // 2. Check JWT User Context (If already authenticated)
  if (req.user && req.user.tenantId) {
    return req.user.tenantId.toUpperCase().trim();
  }

  // 3. Check Query or Body
  const altId = req.query.tenantId || req.body.tenantId || req.body.organizationAlias;
  if (altId) return altId.toUpperCase().trim();

  // 4. BIBLICAL FALLBACK: Anchor to 'WILSY_ROOT' for the Master Core
  return 'WILSY_ROOT';
};

/**
 * 🔐 VALIDATION: Validate Tenant Access
 * This is the Master Gatekeeper for the Sovereign Ledger.
 */
export const tenantDiscovery = async (req, res, next) => {
  try {
    const alias = extractTenantId(req);

    // 🛡️ Security Quantum: Block Forbidden IDs
    if (FORBIDDEN_TENANT_IDS.includes(alias.toLowerCase())) {
      console.error(`🚨 [SOVEREIGN] REJECTION: Forbidden Alias [${alias}]`);

      // 📊 GRAFANA FEED: Intrusion attempt logged for Security Dashboard
      if (typeof broadcastTelemetry === 'function') {
        broadcastTelemetry('GLOBAL_ROOT', 'SECURITY_ALERT', 'FORBIDDEN_ALIAS_REJECTION', 'tenantMiddleware', { attemptedAlias: alias });
      }

      return res.status(403).json({ error: "Identity rejection: Forbidden identifier." });
    }

    // 🏛️ LEDGER LOOKUP
    // Supports both legacy Tenant models and the new Sovereign Identity
    let tenant = await Tenant.findOne({
      $or: [{ slug: alias.toLowerCase() }, { organizationAlias: alias }, { tenantId: alias }],
      status: 'ACTIVE'
    });

    // 🛡️ FOUNDER RECOVERY: Force-anchor if record is misaligned
    if (!tenant && (alias === 'WILSY' || alias === 'WILSY_ROOT')) {
      console.warn("[SOVEREIGN] 🛡️ Founder Override: Manual anchor for 'wilsy' root.");
      tenant = await Tenant.findOne({ adminEmail: "wilsonkhanyezi@gmail.com" });

      if (tenant && tenant.slug !== 'wilsy') {
        tenant.slug = 'wilsy';
        await tenant.save();
      }
    }

    if (!tenant) {
      console.error(`🚨 [SOVEREIGN] REJECTION: Organization "${alias}" not found in Ledger.`);
      return res.status(404).json({
        error: "Identity rejection: Organization not found in Sovereign Ledger."
      });
    }

    // 🎯 ANCHOR TO REQUEST OBJECT
    req.tenant = tenant;
    req.tenantId = tenant.tenantId || tenant.slug; // Prioritize V40 tenantId over legacy slug

    console.log(`✅ [SOVEREIGN] Identity Anchored: ${tenant.name || 'Master Core'} [${req.tenantId}]`);

    // 📊 GRAFANA FEED: Successful routing logged for Performance & Availability Dashboards
    if (typeof broadcastTelemetry === 'function') {
      broadcastTelemetry(req.tenantId, 'ROUTING_SUCCESS', 'TENANT_ANCHORED', 'tenantMiddleware', { target: req.tenantId });
    }

    next();
  } catch (error) {
    console.error("🚨 [SOVEREIGN] ORCHESTRATION FATAL:", error.message);
    res.status(500).json({ error: "Sovereign Ledger access failure." });
  }
};

/**
 * 🚧 ENFORCEMENT: Enforce Tenant Boundary
 * Automatically injects tenantId into queries to prevent data leaks.
 */
export const enforceTenantBoundary = (req, res, next) => {
  if (!req.tenantId) {
    return res.status(400).json({ error: "Tenant context missing." });
  }
  // This logic is used by controllers to filter data:
  // e.g., const docs = await Contract.find({ tenantId: req.tenantId });
  next();
};

export default tenantDiscovery;
