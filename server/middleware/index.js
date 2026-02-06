/*
 * File: server/middleware/index.js
 * STATUS: PRODUCTION-READY | ARCHITECTURAL COMMAND CENTER
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Centralized export hub for the entire middleware fortress.
 * Allows for clean imports: const { protect, tenantScope } = require('./middleware');
 * -----------------------------------------------------------------------------
 */

'use strict';

// 1. Security & Identity
const { protect } = require('./authMiddleware');
const { authorize } = require('./authorize');
const { tenantScope } = require('./tenantScope');
const {
    headerSecurity,
    authLimiter,
    globalApiLimiter,
    requestId,
    tenantGuard,
    errorNormalizer
} = require('./security');

// 2. Access Control (RBAC)
const rbac = require('./rbacMiddleware');
const roles = require('./roleMiddleware');

// 3. Data Integrity & Validation
const validate = require('./validationMiddleware');
const { sanitizeBody } = require('./sanitizeMiddleware');
const validateObjectId = require('./validateObjectId');

// 4. Observability & Forensics
const { emitAudit } = require('./auditMiddleware');
const { metricsMiddleware, metricsEndpoint } = require('./metricsMiddleware');
const requestLogger = require('./requestLogger');
const { ipMetadata } = require('./ipMetadata');
const { userAgentRequired } = require('./userAgentMiddleware');
const correlationId = require('./correlationId');

// 5. Operational Safety
const { errorHandler } = require('./errorMiddleware');
const maintenanceMode = require('./maintenanceMode');
const { features, checkFeature } = require('./featureFlags');
const apiLimiter = require('./rateLimiter');

// 6. Specialized Utilities
const { uploadDocument } = require('./uploadMiddleware');
const responseHandler = require('./responseHandler');

module.exports = {
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
    ...responseHandler
};