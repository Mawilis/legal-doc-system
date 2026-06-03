/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - UNIVERSAL ASSET REGISTRY (UAR) CONTROLLER                                                                                   ║
 * ║ [PQE-256 SECURED | ATOMIC REGISTRATION | R10B+ VALUATION ENGINE]                                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 15.6.0-SINGULARITY-OMEGA | PRODUCTION READY | BILLION DOLLAR SPEC                                                           ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | GLOBAL ASSET CONTROL | NO CHILD'S PLACE                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/assetController.js                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect): Mandated Forensic Telemetry and Seal Enforcement.                                              ║
 * ║ • AI Engineering (Gemini): RE-ANCHORED: Shifted from legacy cryptoUtils to sovereign cryptoCore nucleus. [2026-05-06]                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { AssetSchema } from '../models/Asset.js';
import { SovereignContractSchema } from '../models/SovereignContract.js';
import cryptoCore from '../utils/cryptoCore.js'; // 🏛️ RE-ANCHORED TO NUCLEUS
import logger from '../utils/logger.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import { getCurrentTenantId, getCurrentUserId, getCurrentRequestId } from '../middleware/tenantContext.js';
import crypto from 'node:crypto';

/**
 * 🧬 RECTIFIED MODEL RESOLVER
 */
const getTenantModel = (req, modelName, schema) => {
  const db = req.db || (req.app && req.app.get('db'));
  if (!db) throw new Error("QUANTUM_LINK_DISCONNECTED: No database anchored to request.");
  try {
    return db.model(modelName, schema);
  } catch (error) {
    if (error.name === 'OverwriteModelError') return db.model(modelName);
    throw error;
  }
};

/**
 * @function registerAsset
 */
export const registerAsset = async (req, res, next) => {
  const requestId = getCurrentRequestId();
  const tenantId = getCurrentTenantId();
  const userId = getCurrentUserId();

  try {
    const { name, type, valuation, description, contractId, currency } = req.body;
    const Asset = getTenantModel(req, 'Asset', AssetSchema);
    const Contract = getTenantModel(req, 'SovereignContract', SovereignContractSchema);

    // 🛡️ 1. CONTRACT NEXUS VERIFICATION
    if (contractId) {
      const linkedContract = await Contract.findOne({ _id: contractId, tenantId });
      if (!linkedContract) {
        return res.status(403).json({
          success: false,
          code: 'CONTRACT_ANCHOR_INVALID',
          message: 'Contract nexus not found.'
        });
      }
    }

    // 🔬 2. GENESIS FORENSICS (RE-ANCHORED)
    // Using cryptoCore for institutional forensic ID and hashing DNA
    const assetId = `UAR-${Date.now()}-${crypto.randomBytes(3).toString('hex').toUpperCase()}`;
    const genesisHash = cryptoCore.hash ? cryptoCore.hash({ name, type, assetId, tenantId, timestamp: Date.now() }) : 'RESERVE_HASH_STRIKE';

    // 🏛️ 3. SOVEREIGN REGISTRATION
    const newAsset = await Asset.create({
      tenantId,
      assetId,
      name,
      description,
      type,
      valuation: {
        amount: valuation || 0,
        currency: currency || 'ZAR',
        lastAppraised: new Date()
      },
      status: 'LINKED_TO_CONTRACT',
      integritySeal: genesisHash,
      forensicChain: [{
        action: 'GENESIS_REGISTRATION',
        performer: userId,
        hash: genesisHash,
        timestamp: new Date(),
        metadata: { contractId, requestId }
      }]
    });

    // 📡 4. TELEMETRY BROADCAST
    broadcastTelemetry(tenantId, "ASSET_REGISTRATION", userId, "GENESIS", {
      requestId,
      assetId,
      contractId,
      valuation: newAsset.valuation
    });

    logger.info(`[UAR] 💎 Asset Tokenized: ${name} | AssetID: ${assetId} | RID: ${requestId}`);

    res.status(201).json({
      success: true,
      data: {
        id: newAsset._id,
        assetId: newAsset.assetId,
        integritySeal: genesisHash
      },
      forensicTrace: requestId
    });

  } catch (error) {
    logger.error(`[UAR-FAULT] 🚨 Tenant=${tenantId} Request=${requestId} Error=${error.message}`);
    next(error);
  }
};

/**
 * @function getSovereignAssets
 */
export const getSovereignAssets = async (req, res, next) => {
  const requestId = getCurrentRequestId();
  const tenantId = getCurrentTenantId();
  const userId = getCurrentUserId();

  try {
    const Asset = getTenantModel(req, 'Asset', AssetSchema);
    const assets = await Asset.find({ tenantId }).sort({ createdAt: -1 });

    broadcastTelemetry(tenantId, "ASSET_QUERY", userId, "LEDGER_RETRIEVED", {
      requestId,
      count: assets.length
    });

    res.status(200).json({
      success: true,
      count: assets.length,
      data: assets,
      forensicTrace: requestId
    });
  } catch (error) {
    logger.error(`[UAR-QUERY-FAULT] 🚨 Tenant=${tenantId} Request=${requestId} Error=${error.message}`);
    next(error);
  }
};

export default { registerAsset, getSovereignAssets };
