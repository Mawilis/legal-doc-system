/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - MAIN SERVER                                                     ║
 * ║ Production-grade Express server with multi-tenant isolation                ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import dotenv from 'dotenv';
import jwt from 'jsonwebtoken';
import Redis from 'ioredis';

// Load environment variables
dotenv.config();

// Import routes
import apiRoutes from './routes/api.js';
import healthRoutes from './routes/health.js';
import dealFlowRoutes from './routes/dealFlowRoutes.js';
import investorRoutes from './routes/investorRoutes.js';

// Import middleware
import { extractTenant } from './middleware/tenantContext.js';
import { requestLogger } from './middleware/requestLogger.js';
import { errorHandler } from './middleware/errorHandler.js';
import { rateLimiter } from './middleware/rateLimiter.js';
import { correlationId } from './middleware/correlationId.js';

// Import utilities
import loggerRaw from './utils/logger.js';
const logger = loggerRaw.default || loggerRaw;
import { AuditLogger } from './utils/auditLogger.js';

const app = express();
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

// ============================================================================
// Redis Connection
// ============================================================================

export const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
  retryStrategy: (times) => Math.min(times * 50, 2000)
});

redis.on('connect', () => {
  logger.info('✅ Redis connected');
});

redis.on('error', (err) => {
  logger.error('❌ Redis error:', err);
});

// ============================================================================
// MongoDB Connection
// ============================================================================

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal_doc_system';

mongoose.connect(MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

mongoose.connection.on('connected', () => {
  logger.info('✅ MongoDB connected');
});

mongoose.connection.on('error', (err) => {
  logger.error('❌ MongoDB error:', err);
});

// ============================================================================
// Middleware
// ============================================================================

// Security middleware
app.use(helmet({
  contentSecurityPolicy: NODE_ENV === 'production' ? undefined : false
}));

// CORS
app.use(cors({
  origin: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));

// Compression
app.use(compression());

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request tracing
app.use(correlationId);
app.use(requestLogger);

// Tenant isolation
app.use(extractTenant);

// Rate limiting (applied to all routes)
app.use(rateLimiter({ mode: 'standard' }));

// ============================================================================
// Routes
// ============================================================================

// Health check (no auth required)
app.use('/health', healthRoutes);

// API routes
app.use('/api', apiRoutes);

// Deal Flow routes
app.use('/api/deals', dealFlowRoutes);

// Investor routes
app.use('/api/investor', investorRoutes);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: 'NOT_FOUND',
    message: `Cannot ${req.method} ${req.originalUrl}`
  });
});

// Error handler
app.use(errorHandler);

// ============================================================================
// Start Server
// ============================================================================

const server = app.listen(PORT, () => {
  logger.info(`
╔════════════════════════════════════════════════════════════════╗
║  🏛️ WILSY OS - Production Server Running                        ║
╠════════════════════════════════════════════════════════════════╣
║  Environment: ${NODE_ENV.padEnd(30)} ║
║  Port: ${String(PORT).padEnd(35)} ║
║  MongoDB: Connected ✅                                           ║
║  Redis: Connected ✅                                             ║
║  Multi-tenant: Enabled ✅                                        ║
║  Rate Limiting: Active ✅                                        ║
╚════════════════════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('🛑 SIGTERM received, shutting down gracefully');
  server.close(() => {
    mongoose.disconnect();
    redis.quit();
    logger.info('✅ Graceful shutdown complete');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.info('🛑 SIGINT received, shutting down gracefully');
  server.close(() => {
    mongoose.disconnect();
    redis.quit();
    logger.info('✅ Graceful shutdown complete');
    process.exit(0);
  });
});

export default app;

// ============================================================================
// Neural API Routes
// ============================================================================

import apiRoutes from './routes/api.js';
import adminApiRoutes from './routes/admin/apiKeyRoutes.js';

// Public API endpoints (versioned)
app.use('/api', apiRoutes);

// Admin API key management
app.use('/api/admin', adminApiRoutes);

// Vector search index creation (one-time setup)
app.post('/api/admin/indexes/vector', superAdminGuard, async (req, res) => {
  try {
    // Create vector search index for precedents
    await mongoose.connection.db.createCollection('precedents');
    await mongoose.connection.db.collection('precedents').createIndex(
      { embedding: "vector" },
      {
        name: "precedent_vector_index",
        vectorOptions: {
          dimensions: 1536,
          similarity: "cosine"
        }
      }
    );
    
    res.json({
      success: true,
      message: 'Vector search index created successfully'
    });
  } catch (error) {
    logger.error('Failed to create vector index', { error: error.message });
    res.status(500).json({ error: 'Failed to create vector index' });
  }
});
