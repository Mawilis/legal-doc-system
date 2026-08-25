import express from 'express';
import { invoicesCreated } from '../utils/metricsCollector.js';

const router = express.Router();

router.get('/test-metric', (req, res) => {
  try {
    invoicesCreated.inc({ tenantId: 'test', status: 'TEST', currency: 'ZAR' });
    res.json({ success: true, message: 'Counter incremented' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/test-metric-value', async (req, res) => {
  try {
    // Prometheus Counter doesn't have a get() method, but we can scrape /metrics
    // For simplicity, just return that we incremented
    res.json({ success: true, message: 'Check /metrics for value' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
