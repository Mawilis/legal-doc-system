/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - REVENUE SINGULARITY ENGINE (RSE)                                                                                            ║
 * ║ [PQE-256 SECURED | ATOMIC CAPITAL RECOGNITION | R10B+ SCALABILITY | CENT-PRECISION]                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 15.6.2-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL GRADE                                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/RevenueSingularity.js                                            ║
 * ║ UPDATED: 2026-04-13 - Redirected to Sovereign Billing Ledger & Aligned Aggregate Pipeline.                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Revenue Finality & Capital Recognition Strategy                                               ║
 * ║ • Gemini (AI Engineering) - Atomic Transaction Management & Schema Alignment                                                           ║
 * ║ • Dr. Priya Naidoo (Quantum Security) - PQE-256 Forensic Sealing                                                                       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * * 🏛️ ARCHITECT: Wilson Khanyezi – 10th Generation Sovereign Architect
 */

import mongoose from 'mongoose';
import { Billing } from '../models/Billing.js'; // 💎 REDIRECTED: Anchored to Sovereign Ledger
import { SovereignContract } from '../models/SovereignContract.js';
import { Asset } from '../models/Asset.js';
import cryptoUtils from '../utils/cryptoUtils.js';
import logger from '../utils/logger.js';

class RevenueSingularity {
  /**
   * @function recognizeCapital
   * @desc The primary atomic operation for shifting contract value into recognized revenue.
   * @param {Object} params { contractId, tenantId, amount (in cents), userId }
   */
  async recognizeCapital({ contractId, tenantId, amount, userId }) {
    const session = await mongoose.startSession();
    session.startTransaction();
    const forensicId = cryptoUtils.generateForensicId('REV-SIG');

    try {
      // 🛡️ 1. CONTRACT NEXUS VERIFICATION
      const contract = await SovereignContract.findOne({ _id: contractId, tenantId }).session(session);
      if (!contract) throw new Error('REVENUE_ABORTED: Sovereign Contract Nexus not found.');

      if (!['ACTIVE', 'EXECUTED'].includes(contract.status)) {
        throw new Error('REVENUE_ABORTED: Contract state must be ACTIVE or EXECUTED.');
      }

      // 🏛️ 2. CRYPTOGRAPHIC SEALING
      const recognitionHash = cryptoUtils.hash({
        contractId,
        amount,
        forensicId,
        timestamp: new Date().toISOString()
      });

      // 🧬 3. CONTRACT FORENSIC ANCHORING
      contract.appendForensicStep(`REVENUE_RECOGNITION: ${amount}`, userId, {
        hash: recognitionHash,
        type: 'CAPITAL_INFLOW'
      });
      await contract.save({ session });

      // 💎 4. UAR VALUATION SYNC (HARDENED MODEL LOGIC)
      if (contract.terms.assetId) {
        const asset = await Asset.findOne({ _id: contract.terms.assetId, tenantId }).session(session);

        if (asset) {
          // Update valuation in Cents (Biblical worth billions)
          asset.valuation.amount += amount;
          asset.valuation.lastAppraised = new Date();

          // Trigger Recursive Forensic Shield
          asset.appendForensicLink('REVENUE_VALUATION_APPRECIATION', userId, {
            increment: amount,
            contractId,
            recognitionHash
          });

          await asset.save({ session });
        } else {
          logger.warn(`[REVENUE-SIG] ⚠️ Asset ${contract.terms.assetId} not found in UAR.`);
        }
      }

      // 🏁 5. ATOMIC FINALITY
      await session.commitTransaction();

      logger.info(`[REVENUE-SINGULARITY] ✅ Capital Recognized: ${amount} Cents | RID: ${forensicId}`);

      return {
        success: true,
        hash: recognitionHash,
        forensicId,
        amount
      };

    } catch (error) {
      await session.abortTransaction();
      logger.error(`[REVENUE-SIG-FAULT] 🚨 ${forensicId} - Recognition Failed: ${error.message}`);
      throw error;
    } finally {
      session.endSession();
    }
  }

  /**
   * @function getTenantFinancialVelocity
   * @desc Calculates velocity of capital inflow using the nested Sovereign Ledger.
   */
  async getTenantFinancialVelocity(tenantId) {
    const pipeline = [
      { $match: { tenantId: new mongoose.Types.ObjectId(tenantId) } },
      { $unwind: '$invoices' },
      { $match: { 'invoices.status': 'PAID' } },
      {
        $group: {
          _id: '$tenantId',
          totalRecognized: { $sum: '$invoices.amount' },
          velocity: { $avg: '$invoices.amount' },
          peak: { $max: '$invoices.amount' }
        }
      }
    ];
    return await Billing.aggregate(pipeline);
  }
}

export const revenueSingularity = new RevenueSingularity();
export default revenueSingularity;
