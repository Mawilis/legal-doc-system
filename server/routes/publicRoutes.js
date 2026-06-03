/* eslint-disable */
import express from 'express';

const router = express.Router();

router.get('/ping', (req, res) => {
  res.json({
    success: true,
    message: 'WILSY OS is alive!',
    timestamp: new Date().toISOString(),
    version: '7.0.0-OMEGA'
  });
});

router.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'OPERATIONAL',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    timestamp: new Date().toISOString()
  });
});

export default router;
