#!import express from 'express';

const router = express.Router();

router.get('/dashboard', (req, res) => {
  res.json({
    success: true,
    message: 'Investor dashboard endpoint',
    data: {
      metrics: {
        totalDeals: 42,
        totalValue: 1500000000,
        activeDeals: 12,
      },
    },
  });
});

router.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
  });
});

export default router;
