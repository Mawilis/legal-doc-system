import express from 'express';
import mongoose from 'mongoose';
import { redis } from '../server.js';

const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      mongodb: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
      redis: redis.status === 'ready' ? 'connected' : 'disconnected'
    },
    uptime: process.uptime()
  });
});

router.get('/detailed', async (req, res) => {
  const mongoStatus = mongoose.connection.readyState === 1;
  const redisStatus = redis.status === 'ready';
  
  let redisPing = null;
  if (redisStatus) {
    try {
      redisPing = await redis.ping();
    } catch (e) {
      redisPing = 'error';
    }
  }

  res.json({
    status: mongoStatus && redisStatus ? 'healthy' : 'degraded',
    timestamp: new Date().toISOString(),
    services: {
      mongodb: {
        status: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
        state: mongoose.connection.readyState
      },
      redis: {
        status: redis.status,
        ping: redisPing
      }
    },
    memory: process.memoryUsage(),
    uptime: process.uptime()
  });
});

export default router;
