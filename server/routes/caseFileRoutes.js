/**
 * File: server/routes/caseFileRoutes.js
 * PATH: server/routes/caseFileRoutes.js
 * STATUS: PRODUCTION-READY | SOVEREIGN GATEWAY | EPITOME
 * VERSION: 1.0.0 (The Genesis)
 * -----------------------------------------------------------------------------
 * PURPOSE
 * - The Definitive Routing Layer for Legal Case Assets in Wilsy OS.
 * - Orchestrates the flow between Identity, Isolation, and Business Logic.
 * - Engineered to handle High-Performance Discovery Streaming and Case Governance.
 *
 * ARCHITECTURAL SUPREMACY
 * 1. TRIPLE-LOCK SECURITY: Protect -> requireTenantActive -> tenantScope.
 * 2. DISCOVERY STREAMING: Specialized endpoints for Rule 35 bundle generation.
 * 3. AUDIT INTEGRITY: Every route hit is logged within the security middleware stack.
 * 4. POPIA COMPLIANT: Strict RBAC ensuring only authorized ranks access PII.
 *
 * COLLABORATION
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @api-team
 * - SECURITY: @security-ops (Enforces the "Iron Wall" per request)
 * -----------------------------------------------------------------------------
 * EPITOME:
 * Biblical worth billions no child's place. Wilsy OS to the World.
 */

'use strict';

const express = require('express');
const router = express.Router();

// --- CONTROLLER INJECTION ---
const caseFileController = require('../controllers/caseFileController');

// --- SOVEREIGN MIDDLEWARE STACK ---
const { protect, requireRole, requireTenantActive } = require('../middleware/authMiddleware');
const { tenantScope } = require('../middleware/tenantScope');

/* ---------------------------------------------------------------------------
   GLOBAL MIDDLEWARE BINDING
   All Case routes require an authenticated user within an active Law Firm.
   --------------------------------------------------------------------------- */
router.use(protect);
router.use(requireTenantActive);
router.use(tenantScope); // The "Iron Wall" starts here for all sub-routes

/* ---------------------------------------------------------------------------
   1. CASE MANAGEMENT (Sovereign CRUD)
   --------------------------------------------------------------------------- */

/**
 * @route   POST /api/v1/cases
 * @desc    Initialize a new Legal Case File
 * @access  Private (Legal Staff / Admin / Owner)
 */
router.post(
    '/',
    requireRole('LEGAL_STAFF', 'ADMIN', 'OWNER'),
    caseFileController.createCase
);

/**
 * @route   GET /api/v1/cases
 * @desc    Retrieve all cases within the Law Firm's sovereign boundary
 * @access  Private (All Firm Members)
 */
router.get(
    '/',
    caseFileController.getCases
);

/**
 * @route   GET /api/v1/cases/:id
 * @desc    Deep-dive into a specific Case File's discovery and timeline
 * @access  Private (All Firm Members)
 */
router.get(
    '/:id',
    caseFileController.getCaseDetails
);

/* ---------------------------------------------------------------------------
   2. HIGH COURT DISCOVERY (Rule 35 Engine)
   --------------------------------------------------------------------------- */

/**
 * @route   GET /api/v1/cases/:id/discovery-bundle
 * @desc    Stream a Court-Ready Discovery Bundle (Zip)
 * @access  Private (Legal Professionals / Admin)
 */
router.get(
    '/:id/discovery-bundle',
    requireRole('LAWYER', 'ADMIN', 'OWNER'),
    caseFileController.generateDiscoveryBundle
);

/* ---------------------------------------------------------------------------
   3. LIFECYCLE GOVERNANCE
   --------------------------------------------------------------------------- */

/**
 * @route   PATCH /api/v1/cases/:id/status
 * @desc    Transition case through legal lifecycle (e.g., Litigated -> Settled)
 * @access  Private (Lawyer / Admin / Owner)
 */
router.patch(
    '/:id/status',
    requireRole('LAWYER', 'ADMIN', 'OWNER'),
    caseFileController.transitionCaseStatus
);

/**
 * @route   POST /api/v1/cases/:id/archive
 * @desc    Move case to Cold Storage for 7-year Law Society compliance
 * @access  Private (Admin / Owner)
 */
router.post(
    '/:id/archive',
    requireRole('ADMIN', 'OWNER'),
    caseFileController.archiveCase
);

/**
 * @route   DELETE /api/v1/cases/:id
 * @desc    Permanent expungement of a case node (POPIA Right to Erasure)
 * @access  Private (Owner / SuperAdmin)
 */
router.delete(
    '/:id',
    requireRole('OWNER', 'SUPER_ADMIN'),
    caseFileController.deleteCase
);

/* ---------------------------------------------------------------------------
   EXPORTS
   --------------------------------------------------------------------------- */
module.exports = router;