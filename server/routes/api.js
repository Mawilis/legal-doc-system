/**
 * WILSY OS - API Routes
 */

import express from 'express';
const router = express.Router();

// Health check within API
router.get('/health', (req, res) => {
  res.json({ 
    status: 'api-ok', 
    timestamp: new Date().toISOString() 
  });
});

// Version endpoint
router.get('/version', (req, res) => {
  res.json({
    version: '3.0.0',
    name: 'WILSY OS',
    environment: process.env.NODE_ENV || 'development'
  });
});

export default router;

// Import additional routes
import userRoutes from './users.js';
router.use('/users', userRoutes);
