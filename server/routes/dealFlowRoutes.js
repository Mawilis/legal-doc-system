import express from 'express';
import {
  identifyTargets,
  createDeal,
  calculateSynergy,
  assessRegulatory,
  simulateIntegration,
  getDeal,
  listDeals,
  updateDealStage,
  getPipelineAnalytics,
  getTargets,
  getDealStats
} from '../controllers/dealFlowController.js';
import { authenticate } from '../middleware/auth.js';
import { extractTenant } from '../middleware/tenantContext.js';
import { rateLimiter } from '../middleware/rateLimiter.js';

const router = express.Router();

// Apply common middleware to all routes
router.use(extractTenant);
router.use(authenticate({ required: true }));

// Rate limiting
const standardLimiter = rateLimiter({ mode: 'standard' });
const strictLimiter = rateLimiter({ mode: 'strict' });

// Target identification
router.post('/targets/identify', standardLimiter, identifyTargets);
router.get('/targets', standardLimiter, getTargets);

// Deal management
router.post('/', standardLimiter, createDeal);
router.get('/', standardLimiter, listDeals);
router.get('/:dealId', standardLimiter, getDeal);
router.patch('/:dealId/stage', standardLimiter, updateDealStage);

// Synergy & analysis
router.post('/synergy/:acquirerId/:targetId', strictLimiter, calculateSynergy);
router.post('/:dealId/regulatory-assessment', strictLimiter, assessRegulatory);
router.post('/:dealId/simulate-integration', strictLimiter, simulateIntegration);

// Analytics
router.get('/analytics', standardLimiter, getPipelineAnalytics);
router.get('/stats', standardLimiter, getDealStats);

export default router;
