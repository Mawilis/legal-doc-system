/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN SMART CONTRACT ROUTES                                                                                             ║
 * ║ [SSC EXECUTION | FORENSIC VERIFICATION | ATOMIC ASSET BINDING]                                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 46.2.0-SINGULARITY | PRODUCTION READY | BILLION DOLLAR SPEC                                                                   ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                                                                    ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/contractRoutes.js                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated atomic contract execution with forensic state sealing. [2026-05-06]                  ║
 * ║ • AI Engineering (Gemini) - RE-ANCHORED: Shifted from authMiddleware to consolidated auth.middleware shield. [2026-05-06]               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import { requireSovereignAuth } from '../middleware/auth.middleware.js'; // 🏛️ RE-ANCHORED TO SHIELD
import { integrityShield } from '../middleware/ProductionHardening.middleware.js';
import { initializeContract, executeContract } from '../controllers/contractController.js';

const router = express.Router();

/**
 * @route   POST /api/contracts/initialize
 * @desc    Create a new sovereign smart contract bound to an asset
 * @access  Private (Forensic Seal + Bearer Token Required)
 * @forensic Anchors the covenant into the Sovereign Ledger
 */
router.post('/initialize', requireSovereignAuth, initializeContract);

/**
 * @route   POST /api/contracts/execute/:contractId
 * @desc    Execute contract logic, update asset state atomically
 * @access  Private (Forensic Seal + Bearer Token + Integrity Shield Required)
 * @forensic Triggers SHA3-512 state sealing and vertical chaining
 */
router.post('/execute/:contractId', requireSovereignAuth, integrityShield, executeContract);

export default router;
