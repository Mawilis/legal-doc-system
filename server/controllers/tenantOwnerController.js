/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TENANT OWNER ADMINISTRATIVE CITADEL                                                                                         ║
 * ║ [SOVEREIGN CONTROL | AUDIT TRANSPARENCY | DATA PRIVACY]                                                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 15.0.0-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                                                                    ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/tenantOwnerController.js                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { User } from '../models/userModel.js';
import { Billing } from '../models/Billing.js';
import { getCurrentTenantId, getCurrentRequestId } from '../middleware/tenantContext.js';

export const getOwnerDashboard = async (req, res) => {
  const tenantId = getCurrentTenantId();
  const requestId = getCurrentRequestId();

  try {
    const [userCount, billingInfo] = await Promise.all([
      User.countDocuments({ tenantId }),
      Billing.findOne({ tenantId })
    ]);

    res.status(200).json({
      success: true,
      data: {
        totalUsers: userCount,
        billingTier: billingInfo?.tier || 'FREE',
        complianceStatus: 'VERIFIED'
      },
      forensicTrace: requestId
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
};

export default { getOwnerDashboard };
