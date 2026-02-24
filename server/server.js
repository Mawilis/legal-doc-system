/* eslint-disable */
/**
 * WILSY OS - Complete Working Server
 */

import express from 'express';
import fs from 'fs';
import path from 'path';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import mongoose from 'mongoose';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// ============================================================================
// MIDDLEWARE
// ============================================================================
app.use(cors());
app.use(helmet());
app.use(compression());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

console.log('✅ Middleware loaded');

// ============================================================================
// DATABASE CONNECTION
// ============================================================================
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/wilsy-os';

mongoose.connect(MONGODB_URI)
  .then(() => console.log('✅ MongoDB connected'))
  .catch(err => console.error('❌ MongoDB connection error:', err));

// ============================================================================
// ROUTES
// ============================================================================
// Import routes dynamically to avoid errors if files don't exist yet
try {
  const apiRoutes = await import('./routes/api.js').then(module => module.default);
  app.use('/api', apiRoutes);
  console.log('✅ API routes loaded');
} catch (err) {
  console.log('⚠️ API routes not yet available:', err.message);
}

try {
  const healthRoutes = await import('./routes/health.js').then(module => module.default);
  app.use('/health', healthRoutes);
  console.log('✅ Health routes loaded');
} catch (err) {
  console.log('⚠️ Health routes not yet available, using default');
  
  // Default health endpoint
  app.get('/health', (req, res) => {
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      module: 'ESM',
      __dirname: __dirname,
      mongodb: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
      middleware: {
        cors: true,
        helmet: true,
        compression: true,
        json: true
      }
    });
  });
}

// ============================================================================
// ERROR HANDLING
// ============================================================================
app.use((err, req, res, next) => {
  console.error('❌ Error:', err.message);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message,
    timestamp: new Date().toISOString()
  });
});

// ============================================================================
// START SERVER
// ============================================================================
app.listen(PORT, () => {
  console.log(`\n🚀 WILSY OS server running on port ${PORT}`);
  console.log(`   Health check: http://localhost:${PORT}/health`);
  console.log(`   API: http://localhost:${PORT}/api`);
  console.log(`   Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`   MongoDB: ${mongoose.connection.readyState === 1 ? '✅ Connected' : '❌ Disconnected'}\n`);
});

export default app;
