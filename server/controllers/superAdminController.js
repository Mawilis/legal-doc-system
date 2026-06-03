/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SUPERADMIN SOVEREIGN HUB [V31.0.9-OMEGA]                                                                                    ║
 * ║ [REAL-DATA ENGINE | PATH RECONCILIATION | INSTITUTIONAL FINALITY]                                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 31.0.9-OMEGA | PRODUCTION READY | BILLION DOLLAR SPEC                                                                         ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/superAdminController.js                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated real-time HUD telemetry and forensic shard resolution.                                ║
 * ║ • Gemini (AI Engineering) - RECTIFIED: Aligned named import { SuperAdmin } with Model Shard V5.0.4.                                     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { performance } from 'node:perf_hooks';
import os from 'node:os';
import chalk from 'chalk';

// Sovereign Models
import { SuperAdmin } from '../models/SuperAdmin.js';
import Tenant from '../models/Tenant.js';
import User from '../models/userModel.js';

class SuperAdminController {
  /**
   * 🏛️ getDashboardOverview
   * @desc Provides high-fidelity metrics for the Founder Dashboard.
   */
  async getDashboardOverview(req, res, next) {
    const startTime = performance.now();
    try {
      console.log(chalk.blue("[SUPERADMIN_CONTROLLER] 🛰️ Aggregating Sovereign Metrics..."));

      const [tenantCount, activeUsers, adminStatus] = await Promise.all([
        Tenant.countDocuments({ status: 'ACTIVE' }).catch(() => 0),
        User.countDocuments({ isActive: true }).catch(() => 0),
        SuperAdmin.findOne({ 'identity.email': req.user?.email }).select('status').lean().catch(() => null)
      ]);

      const telemetry = {
        latency: `${(performance.now() - startTime).toFixed(4)}ms`,
        nodes: tenantCount,
        souls: activeUsers,
        valuation: "REVENUE_READY",
        systemState: adminStatus?.status === 'ACTIVE' ? "STABLE" : "DEGRADED"
      };

      console.log(chalk.green("[SUPERADMIN_CONTROLLER] ✅ HUD Telemetry Finalized."));

      return res.status(200).json({
        success: true,
        metrics: telemetry,
        system: {
          uptime: `${Math.round(os.uptime() / 3600)} Hours`,
          platform: "WILSY OS OMEGA",
          kernel: os.release()
        }
      });
    } catch (error) {
      console.error(chalk.red('🚨 [SUPERADMIN_CONTROLLER] 💥 HUD_IGNITION_FAILURE:'), error.message);
      return res.status(500).json({ success: false, message: "HUD_IGNITION_FAILURE" });
    }
  }

  async getGlobalHUD(req, res, next) {
    return this.getDashboardOverview(req, res, next);
  }
}

const superAdminController = new SuperAdminController();
export default superAdminController;
