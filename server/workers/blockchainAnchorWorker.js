/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ BLOCKCHAIN ANCHOR WORKER - INVESTOR-GRADE MODULE                          ║
  ║ Background processing | Hyperledger integration | Auto-retry             ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/workers/blockchainAnchorWorker.js
 * VERSION: 1.0.0-PRODUCTION
 * CREATED: 2026-03-02
 */

import { Worker } from 'bullmq';
import BlockchainAnchor, { BLOCKCHAIN_STATUS } from '../models/BlockchainAnchor.js';
import blockchainService from '../services/blockchainService.js';
import { redisConfig } from '../config/queue.js';
import logger from '../utils/logger.js';
import auditLogger from '../utils/auditLogger.js';

const ANCHOR_BATCH_SIZE = 50;
const MAX_RETRIES = 5;
const RETRY_DELAYS = [5000, 15000, 30000, 60000, 120000];

class BlockchainAnchorWorker {
  constructor() {
    this.worker = null;
    this.initialize();
  }

  initialize() {
    this.worker = new Worker('blockchain-anchor', async job => {
      const { type, data } = job.data;

      switch(type) {
        case 'anchor-document':
          return await this.anchorDocument(data);
        case 'anchor-batch':
          return await this.anchorBatch(data);
        case 'verify-anchor':
          return await this.verifyAnchor(data);
        case 'retry-failed':
          return await this.retryFailed(data);
        default:
          throw new Error(`Unknown job type: ${type}`);
      }
    }, {
      connection: redisConfig.connection,
      concurrency: 5,
      limiter: { max: 50, duration: 1000 }
    });

    this.setupEventHandlers();
    logger.info('✅ BlockchainAnchorWorker initialized');
  }

  setupEventHandlers() {
    this.worker.on('completed', job => {
      logger.info(`Anchor job ${job.id} completed`, {
        type: job.data.type,
        duration: job.finishedOn - job.processedOn
      });
    });

    this.worker.on('failed', (job, err) => {
      logger.error(`Anchor job ${job.id} failed`, {
        type: job.data.type,
        error: err.message
      });
    });
  }

  async anchorDocument(data) {
    const { anchorId, documentHash, metadata } = data;
    const startTime = Date.now();

    try {
      const anchor = await BlockchainAnchor.findOne({ anchorId });
      if (!anchor) throw new Error(`Anchor not found: ${anchorId}`);

      anchor.status = BLOCKCHAIN_STATUS.ANCHORING;
      await anchor.save();

      const result = await blockchainService.anchorDocument({
        documentHash,
        documentId: anchor.documentId,
        tenantId: anchor.tenantId,
        metadata
      });

      anchor.transactionId = result.transactionId;
      anchor.blockNumber = result.blockNumber;
      anchor.blockHash = result.blockHash;
      anchor.peerResponses = result.peerResponses;
      anchor.status = BLOCKCHAIN_STATUS.ANCHORED;
      anchor.audit.anchoredBy = 'worker';
      anchor.audit.anchoredAt = new Date();
      await anchor.save();

      await auditLogger.log({
        action: 'BLOCKCHAIN_ANCHORED',
        anchorId,
        transactionId: result.transactionId,
        blockNumber: result.blockNumber,
        duration: Date.now() - startTime
      });

      return result;
    } catch (error) {
      const anchor = await BlockchainAnchor.findOne({ anchorId });
      if (anchor) {
        anchor.retryCount += 1;
        anchor.lastRetryAt = new Date();
        anchor.errorMessage = error.message;

        if (anchor.retryCount >= MAX_RETRIES) {
          anchor.status = BLOCKCHAIN_STATUS.FAILED;
        }
        await anchor.save();
      }

      throw error;
    }
  }

  async anchorBatch(data) {
    const { anchorIds } = data;
    const results = [];

    for (const anchorId of anchorIds) {
      try {
        const result = await this.anchorDocument({ anchorId });
        results.push({ anchorId, success: true, result });
      } catch (error) {
        results.push({ anchorId, success: false, error: error.message });
      }
    }

    return {
      total: anchorIds.length,
      successful: results.filter(r => r.success).length,
      failed: results.filter(r => !r.success).length,
      results
    };
  }

  async verifyAnchor(data) {
    const { anchorId, transactionId } = data;
    const startTime = Date.now();

    try {
      const verification = await blockchainService.verifyTransaction(transactionId);
      
      const anchor = await BlockchainAnchor.findOne({ anchorId });
      if (anchor) {
        anchor.verificationChecks = [{
          check: 'blockchain-verification',
          passed: verification.verified,
          details: verification.details,
          timestamp: new Date()
        }];

        if (verification.verified) {
          anchor.status = BLOCKCHAIN_STATUS.VERIFIED;
          anchor.verifiedAt = new Date();
          anchor.verifiedBy = 'worker';
        }

        await anchor.save();
      }

      await auditLogger.log({
        action: 'BLOCKCHAIN_VERIFIED',
        anchorId,
        transactionId,
        verified: verification.verified,
        duration: Date.now() - startTime
      });

      return verification;
    } catch (error) {
      logger.error('Verification failed', { anchorId, transactionId, error: error.message });
      throw error;
    }
  }

  async retryFailed(data) {
    const { maxRetries = MAX_RETRIES } = data;

    const failedAnchors = await BlockchainAnchor.find({
      status: BLOCKCHAIN_STATUS.FAILED,
      retryCount: { $lt: maxRetries }
    }).limit(ANCHOR_BATCH_SIZE);

    const results = [];
    for (const anchor of failedAnchors) {
      try {
        anchor.status = BLOCKCHAIN_STATUS.PENDING;
        await anchor.save();

        const result = await this.anchorDocument({
          anchorId: anchor.anchorId,
          documentHash: anchor.documentHash,
          metadata: anchor.metadata
        });

        results.push({ anchorId: anchor.anchorId, success: true, result });
      } catch (error) {
        results.push({ 
          anchorId: anchor.anchorId, 
          success: false, 
          error: error.message 
        });
      }
    }

    return {
      processed: failedAnchors.length,
      successful: results.filter(r => r.success).length,
      results
    };
  }

  async getStats() {
    const jobCounts = await this.worker.getJobCounts();
    return {
      worker: { isRunning: this.worker.isRunning(), concurrency: this.worker.concurrency },
      jobs: jobCounts
    };
  }

  async close() {
    await this.worker.close();
    logger.info('BlockchainAnchorWorker closed');
  }
}

export const createAnchorWorker = () => new BlockchainAnchorWorker();
export default BlockchainAnchorWorker;
