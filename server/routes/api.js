import express from 'express';
import investorRoutes from './investorRoutes.js';
import dealFlowRoutes from './dealFlowRoutes.js';
import healthRoutes from './health.js';

const router = express.Router();

// Test route
router.get('/test', (req, res) => {
  res.json({
    success: true,
    message: 'API is working',
    timestamp: new Date().toISOString()
  });
});

// Mount routes
router.use('/investor', investorRoutes);
router.use('/deals', dealFlowRoutes);
router.use('/health', healthRoutes);

export default router;
