/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN STATEMENT ROUTER [V44.2.0-PROD-CONSOLIDATED]                                                                      ║
 * ║ [DIRECTORY REALIGNMENT | CRYPTOGRAPHIC GATEWAY | ES MODULE ALIGNMENT | STATEMENT-ONLY ROUTES]                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 44.2.0-PROD-CONSOLIDATED | PRODUCTION READY | BILLION DOLLAR SPEC                                                             ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL SECURITY                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/statements.routes.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated absolute path finality and Biblical comment standards. [2026-05-02]                  ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Aligned router with V45.0.0 Forensic Authentication Shield.                                     ║
 * ║ • Forensic Audit - Verified route registration for Revenue, Compliance, and Forensics strikes.                                         ║
 * ║ • Architecture Update - [2026-05-27] CONSOLIDATED: Removed PDF generation route – statements only.                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 📜 DESCRIPTION:                                                                                                                        ║
 * ║ Central gateway for institutional document generation. Enforces Zero-Trust through requireSovereignAuth and verifyTenantScope.         ║
 * ║ This router handles ONLY institutional statements (Revenue, Compliance, Forensics).                                                    ║
 * ║ PDF artifact generation (court‑sealed reports) is handled by the dedicated artifact router or pdfController.                          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';

/**
 * 🛡️ INSTITUTIONAL IMPORT ALIGNMENT
 * RECTIFIED: Importing the forensic shield and tenant validator at absolute paths.
 * These middlewares ensure that no unsigned or cross-tenant requests bypass the gate.
 */
import * as StatementController from '../controllers/statements.controller.js';
import { requireSovereignAuth } from '../middleware/auth.middleware.js';
import { verifyTenantScope } from '../middleware/tenant.middleware.js';

const router = express.Router();

/**
 * 🛰️ STRATEGIC ROUTING: STATEMENT ENGINE
 * requireSovereignAuth: Validates the JWT token and basic quantum compliance headers.
 */
router.use(requireSovereignAuth);

/**
 * @route   GET /api/statements/revenue
 * @desc    Generates a sealed Revenue Singularity Statement (PDF) for the tenant scope.
 *          Includes branding, live ARR/MRR metrics, and forensic seal.
 * @access  requires valid JWT and tenant scope verification
 * @example curl -H "Authorization: Bearer <token>" http://localhost:5050/api/statements/revenue
 */
router.get('/revenue', verifyTenantScope, StatementController.generateRevenueStatement);

/**
 * @route   GET /api/statements/compliance
 * @desc    Generates a regulatory compliance audit statement (PDF) covering GDPR, POPIA, SOC2.
 * @access  requires valid JWT and tenant scope verification
 * @example curl -H "Authorization: Bearer <token>" http://localhost:5050/api/statements/compliance
 */
router.get('/compliance', verifyTenantScope, StatementController.generateComplianceStatement);

/**
 * @route   GET /api/statements/forensics
 * @desc    Initiates a forensic chain-of-custody statement (PDF) for all system events.
 * @access  requires valid JWT and tenant scope verification
 * @example curl -H "Authorization: Bearer <token>" http://localhost:5050/api/statements/forensics
 */
router.get('/forensics', verifyTenantScope, StatementController.generateForensicsStatement);

/**
 * @route   GET /api/statements/:hud
 * @desc    Compatibility export for Revenue Ledger HUD modes such as predictive,
 *          collections and metering. These modes compile into the revenue
 *          statement engine with the requesting HUD preserved in metadata.
 * @access  requires valid JWT and tenant scope verification
 */
router.get('/:hud', verifyTenantScope, StatementController.generateRevenueStatement);

export default router;
