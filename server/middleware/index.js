import { createRequire as _createRequire } from 'module';
const require = _createRequire(import.meta.url);
/*
 * File: server/middleware/index.js
 * STATUS: PRODUCTION-READY | ARCHITECTURAL COMMAND CENTER
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Centralized export hub for the entire middleware fortress.
 * Allows for clean imports: const { protect, tenantScope } = require('./middleware');
 * -----------------------------------------------------------------------------
 */

// 1. Security & Identity

// 2. Access Control (RBAC)

// 3. Data Integrity & Validation

// 4. Observability & Forensics
const { emitAudit } = require('./auditMiddleware');
const { protect } = require('./authMiddleware');
const { authorize } = require('./authorize');
const correlationId = require('./correlationId');

// 5. Operational Safety
const { errorHandler } = require('./errorMiddleware');
const { features, checkFeature } = require('./featureFlags');
const { ipMetadata } = require('./ipMetadata');
const maintenanceMode = require('./maintenanceMode');
const { metricsMiddleware, metricsEndpoint } = require('./metricsMiddleware');
const apiLimiter = require('./rateLimiter');
const rbac = require('./rbacMiddleware');
const requestLogger = require('./requestLogger');

// 6. Specialized Utilities
const responseHandler = require('./responseHandler');
const roles = require('./roleMiddleware');
const { sanitizeBody } = require('./sanitizeMiddleware');
const {
  headerSecurity,
  authLimiter,
  globalApiLimiter,
  requestId,
  tenantGuard,
  errorNormalizer,
} = require('./security');
const { tenantScope } = require('./tenantScope');
const { uploadDocument } = require('./uploadMiddleware');
const { userAgentRequired } = require('./userAgentMiddleware');
const validateObjectId = require('./validateObjectId');
const validate = require('./validationMiddleware');

export default {
  // Identity & Protection
  protect,
  authorize,
  tenantScope,
  headerSecurity,
  authLimiter,
  globalApiLimiter,
  requestId,
  tenantGuard,
  errorNormalizer,

  // Access Control
  ...rbac,
  ...roles,

  // Validation
  validate,
  sanitizeBody,
  validateObjectId,

  // Monitoring
  emitAudit,
  metricsMiddleware,
  metricsEndpoint,
  requestLogger,
  ipMetadata,
  userAgentRequired,
  correlationId,

  // Operations
  errorHandler,
  maintenanceMode,
  features,
  checkFeature,
  apiLimiter,

  // Tools
  uploadDocument,
  ...responseHandler,
};
