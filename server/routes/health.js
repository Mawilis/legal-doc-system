/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS - HEALTH CHECK ENDPOINT                                          ║
  ║ Always accessible, no auth required                                       ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import express from 'express';
import mongoose from 'mongoose';

const router = express.Router();

// Simple health check - NO AUTH REQUIRED
router.get('/', (req, res) => {
    const healthcheck = {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        version: process.env.npm_package_version || '3.0.0',
        services: {
            database: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
            server: 'running'
        }
    };
    
    res.status(200).json(healthcheck);
});

// Detailed health for Kubernetes probes
router.get('/detailed', (req, res) => {
    const healthcheck = {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        version: process.env.npm_package_version || '3.0.0',
        memory: process.memoryUsage(),
        cpu: process.cpuUsage(),
        services: {
            database: {
                status: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
                state: mongoose.STATES[mongoose.connection.readyState]
            },
            redis: global.redisClient ? 'connected' : 'not configured'
        }
    };
    
    res.status(200).json(healthcheck);
});

export default router;
