/* eslint-disable */
import express from 'express.js';

// Try to import investor routes, but don't fail if missing
let investorRoutes;
try {
  investorRoutes = (await import('./investorRoutes.js')).default;
  console.log('✅ investorRoutes loaded');
} catch (err) {
  console.log('⚠️ investorRoutes not available:', err.message);
  investorRoutes = express.Router();
  investorRoutes.get('/test', (req, res) => {
    res.json({ message: 'Investor routes placeholder', timestamp: new Date().toISOString() });
  });
}

// Try to import middleware, but provide fallbacks
let authenticate, extractTenant, rateLimiter, auditMiddleware, validateRequest, logger, auditLogger;

try {
  const authModule = await import('../middleware/auth.js');
  authenticate = authModule.authenticate || authModule.default;
} catch (err) {
  console.log('⚠️ auth middleware not available');
  authenticate = (req, res, next) => next();
}

try {
  const tenantModule = await import('../middleware/tenantContext.js');
  extractTenant = tenantModule.extractTenant || tenantModule.default;
} catch (err) {
  console.log('⚠️ tenant middleware not available');
  extractTenant = (req, res, next) => { req.tenantContext = { tenantId: 'public' }; next(); };
}

try {
  const rateLimiterModule = await import('../middleware/rateLimiter.js');
  rateLimiter = rateLimiterModule.rateLimiter || rateLimiterModule.default;
} catch (err) {
  console.log('⚠️ rateLimiter middleware not available');
  rateLimiter = () => (req, res, next) => next();
}

try {
  const auditModule = await import('../middleware/auditLogger.js');
  auditMiddleware = auditModule.auditMiddleware || auditModule.default;
} catch (err) {
  console.log('⚠️ audit middleware not available');
  auditMiddleware = () => (req, res, next) => next();
}

try {
  const validatorModule = await import('../middleware/requestValidator.js');
  validateRequest = validatorModule.validateRequest || validatorModule.default;
} catch (err) {
  console.log('⚠️ validator middleware not available');
  validateRequest = () => (req, res, next) => next();
}

try {
  const loggerModule = await import('../utils/logger.js');
  logger = loggerModule.default;
} catch (err) {
  console.log('⚠️ logger not available');
  logger = { info: console.log, error: console.error, warn: console.warn, debug: console.log };
}

try {
  const auditLoggerModule = await import('../utils/auditLogger.js');
  auditLogger = auditLoggerModule.default;
} catch (err) {
  console.log('⚠️ auditLogger not available');
  auditLogger = { log: () => Promise.resolve() };
}

const router = express.Router();
const API_VERSION = 'v1';
const SERVICE_NAME = 'WILSY-OS-API';
const BUILD_VERSION = process.env.BUILD_VERSION || '2.0.0-investor-grade';

// Helper functions
function generateRequestId() {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 10);
  return `req_${timestamp}_${random}`;
}

function formatSuccess(data, requestId) {
  return {
    success: true,
    data,
    timestamp: new Date().toISOString(),
    requestId,
    service: SERVICE_NAME,
    version: BUILD_VERSION
  };
}

// Request ID middleware
router.use((req, res, next) => {
  req.requestId = generateRequestId();
  res.setHeader('X-Request-ID', req.requestId);
  next();
});

// Apply middleware
router.use(extractTenant);
router.use(rateLimiter({ authenticated: 1000, unauthenticated: 100 }));
router.use(express.json({ limit: '10mb' }));
router.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Test endpoint
router.get('/test', (req, res) => {
  logger.info('Test endpoint accessed', { requestId: req.requestId });
  res.json(formatSuccess({
    message: 'WILSY OS API routes are operational',
    timestamp: new Date().toISOString(),
    version: BUILD_VERSION
  }, req.requestId));
});

// Health endpoint
router.get('/health', (req, res) => {
  res.json(formatSuccess({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: SERVICE_NAME
  }, req.requestId));
});

// Debug routes endpoint
router.get('/debug/routes', (req, res) => {
  const routes = [];
  router.stack.forEach(layer => {
    if (layer.route) {
      const methods = Object.keys(layer.route.methods).join(', ').toUpperCase();
      routes.push({
        path: layer.route.path,
        methods
      });
    }
  });
  res.json(formatSuccess({ routes }, req.requestId));
});

// Mount investor routes if available
if (investorRoutes) {
  router.use('/investor', 
    authenticate,
    validateRequest({ schema: 'investor' }),
    auditMiddleware({ action: 'INVESTOR_API_ACCESS' }),
    investorRoutes
  );
  console.log('✅ Investor routes mounted at /api/investor');
}

// 404 handler
router.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: {
      code: 'NOT_FOUND',
      message: `Cannot ${req.method} ${req.originalUrl}`,
      requestId: req.requestId,
      timestamp: new Date().toISOString()
    }
  });
});

// Error handler
router.use((err, req, res, next) => {
  logger.error('API error', { error: err.message, requestId: req.requestId });
  res.status(err.statusCode || 500).json({
    success: false,
    error: {
      code: err.code || 'INTERNAL_ERROR',
      message: err.message || 'Internal server error',
      requestId: req.requestId,
      timestamp: new Date().toISOString()
    }
  });
});

export default router;
