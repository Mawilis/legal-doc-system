/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN TENANT & SHARDING ROUTES [V46.7.0-SINGULARITY]                                                                    ║
 * ║ [DYNAMIC SHARD PROVISIONING | ISOLATION ENFORCEMENT | FORENSIC TENANT BINDING]                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 46.7.0-SINGULARITY | PRODUCTION READY | BILLION DOLLAR SPEC                                                                   ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/tenantRoutes.js                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-leak tenant isolation for institutional clients. [2026-05-06]                   ║
 * ║ • AI Engineering (Gemini) - RE-ANCHORED: Shifted from legacy cryptoUtils to sovereign cryptoCore nucleus. [2026-05-06]                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import {
  createTenant,
  getTenantDetails,
  updateTenantTier
} from '../controllers/tenantController.js';
import { requireSovereignAuth, admin } from '../middleware/auth.middleware.js'; // 🏛️ RE-ANCHORED TO SHIELD

const router = express.Router();

/**
 * @route   POST /api/tenants
 * @desc    Shard Genesis - Provision a new institutional tenant
 * @access  Private (Sovereign/Founder Only)
 */
router.post('/', requireSovereignAuth, admin, createTenant);

/**
 * @route   GET /api/tenants/:tenantId
 * @desc    Shard Echo - Retrieve institutional configuration
 * @access  Private (Sovereign/Founder Only)
 */
router.get('/:tenantId', requireSovereignAuth, admin, getTenantDetails);

/**
 * @route   PATCH /api/tenants/:tenantId/tier
 * @desc    Tier Escalation - Adjust institutional throughput
 * @access  Private (Sovereign/Founder Only)
 */
router.patch('/:tenantId/tier', requireSovereignAuth, admin, updateTenantTier);

export default router;
