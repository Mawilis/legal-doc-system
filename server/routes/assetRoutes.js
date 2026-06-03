/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - UNIVERSAL ASSET REGISTRY (UAR) ROUTES                                                #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/assetRoutes.js               #
 * ####################################################################################################
 * # VERSION: 46.1.0-SINGULARITY | PRODUCTION READY | BILLION DOLLAR SPEC                            #
 * # EPITOME: BIBLICAL WORTH BILLIONS | GLOBAL ASSET ACCESS | NO CHILD'S PLACE                        #
 * ####################################################################################################
 * * 👥 COLLABORATION & SOVEREIGN SIGN-OFF:
 * • Wilson Khanyezi (Lead Architect) - Asset Routing Strategy & Global Revenue Logic. [2026-05-06]
 * • AI Engineering (Gemini) - RE-ANCHORED: Shifted from authMiddleware to auth.middleware shield. [2026-05-06]
 *
 * * 🔬 FORENSIC PROOF:
 * 1. PROTECTED ENDPOINTS: Guarded by requireSovereignAuth for SHA3-512 seal validation.
 * 2. TENANT BOUNDARIES: Enforces context-aware isolation via Nucleus Sharding.
 */

import express from 'express';
import { registerAsset, getSovereignAssets } from '../controllers/assetController.js';
import { requireSovereignAuth } from '../middleware/auth.middleware.js'; // 🏛️ RE-ANCHORED TO SHIELD

const router = express.Router();

/**
 * @route   POST /api/assets/register
 * @desc    Tokenize a new high-value asset in the Wilsy OS Sovereign Ledger
 * @access  Private (Forensic Seal + Bearer Token Required)
 */
router.post('/register', requireSovereignAuth, registerAsset);

/**
 * @route   GET /api/assets
 * @desc    Retrieve the full forensic ledger of assets for the current Tenant
 * @access  Private (Forensic Seal + Bearer Token Required)
 */
router.get('/', requireSovereignAuth, getSovereignAssets);

export default router;
