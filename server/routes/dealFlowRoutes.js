/* ╔═══════════════════════════════════════════════════════════════════════════════════════╗
  ║ DEAL FLOW ROUTES - QUANTUM M&A PIPELINE API ENDPOINTS                                 ║
  ║ [R1.2B/year Deal Flow | JSE Compliant | Competition Act Ready]                        ║
  ╚═══════════════════════════════════════════════════════════════════════════════════════╝ */

import express from 'express.js';
import {
  identifyTargets,
  calculateSynergy,
  generateFairnessOpinion,
  simulateIntegration,
  generateCompetitionFiling,
  predictDealSuccess,
} from '../controllers/dealFlowController.js.js';
import { authenticate } from '../middleware/auth.js.js';
import { rateLimiter } from '../middleware/rateLimiter.js.js';
import { validateRequest } from '../middleware/requestValidator.js.js';
import { extractTenant } from '../middleware/tenantContext.js.js';

const router = express.Router();

router.use(extractTenant);

// Target identification (quantum matching)
router.post(
  '/targets/identify',
  authenticate({ required: true, roles: ['deal_team', 'admin'] }),
  rateLimiter({ mode: 'standard' }),
  validateRequest({ schema: 'target_identification' }),
  identifyTargets,
);

// Synergy calculation
router.post(
  '/synergy/:acquirerId/:targetId',
  authenticate({ required: true, roles: ['deal_team', 'analyst', 'admin'] }),
  rateLimiter({ mode: 'standard' }),
  validateRequest({ schema: 'synergy_calculation' }),
  calculateSynergy,
);

// Fairness opinion generation
router.post(
  '/fairness/:dealId',
  authenticate({ required: true, roles: ['admin', 'director'] }),
  rateLimiter({ mode: 'strict' }),
  generateFairnessOpinion,
);

// Integration simulation
router.post(
  '/simulate/:dealId',
  authenticate({ required: true, roles: ['deal_team', 'admin'] }),
  rateLimiter({ mode: 'standard' }),
  validateRequest({ schema: 'integration_simulation' }),
  simulateIntegration,
);

// Competition filing generation
router.post(
  '/filing/:dealId/:jurisdiction',
  authenticate({ required: true, roles: ['admin', 'legal'] }),
  rateLimiter({ mode: 'strict' }),
  generateCompetitionFiling,
);

// Deal success prediction
router.get(
  '/predict/:dealId',
  authenticate({ required: true, roles: ['deal_team', 'admin', 'investor'] }),
  rateLimiter({ mode: 'standard' }),
  predictDealSuccess,
);

export default router;
