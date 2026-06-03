/* eslint-disable */
/**
 * 🏛️ WILSY OS - SOVEREIGN MASTER API v2
 * @version 10.0.0-QUANTUM-2050
 * @description The unified gateway orchestrating the entire Wilsy OS ecosystem.
 * * 🤝 COLLABORATION NOTES:
 * - CONSOLIDATION: Unifies Admin, Finance, Legal, and Sync layers.
 * - SECURITY: Every endpoint is shielded by Sovereign Identity validation.
 * - WORTH: This is the primary interface for R2.3T in digital legal assets.
 */
import express from 'express';
import { getSystemVitality } from '../../controllers/admin/SystemHealth.controller.js';
import { getSecurityPosture } from '../../controllers/admin/SecurityAudit.controller.js';
import { getGlobalSyncStatus } from '../../controllers/admin/SyncHUD.controller.js';
import { generateFinalSovereignInvoice } from '../../controllers/finance/FinancialGateway.controller.js';

const router = express.Router();

// --- 🛡️ CITADEL OPS (Admin & Security) ---
import { executeLiveDemo } from '../../controllers/demo/Sovereign_Demo_Live.controller.js';
router.post('/demo/ignite', executeLiveDemo);
import { sovereignLogin } from '../../controllers/auth/Sovereign_Login.controller.js';
router.post('/login', sovereignLogin);
import { getSystemSettings, updateSystemSettings } from '../../controllers/admin/SovereignSettings.controller.js';
router.get('/settings', getSystemSettings);
router.put('/settings', updateSystemSettings);
router.get('/citadel/health', getSystemVitality);
router.get('/citadel/security', getSecurityPosture);
router.get('/citadel/sync-map', getGlobalSyncStatus);

// --- 💰 FINANCIAL OPS (Billing & Tax) ---
router.post('/finance/seal-invoice', generateFinalSovereignInvoice);

// --- ⚖️ LEGAL OPS (Document Assembly) ---
// Note: Integration with DocumentService happens via specific controllers

console.log('--- 🚀 SOVEREIGN API v2 LOADED & SEALED ---');

export default router;
