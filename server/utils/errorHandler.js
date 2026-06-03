/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN ERROR HANDLER UTILITY                                ║
 * ║ [CENTRALIZED ERROR HANDLING | LOGGING | NOTIFICATION | RECOVERY]         ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * @team Collaboration Notes:
 * - Centralized error handling for all services
 * - Error classification and severity levels
 * - Automatic retry mechanisms
 * - Error logging and alerting
 * - 101/10 reliability standard
 *
 * @last_updated: 2026-03-18
 * @lead_architect: Wilson Khanyezi
 */

// ============================================================================
// ERROR CLASSIFICATION
// ============================================================================

export const ErrorTypes = {
  // Validation errors
  VALIDATION: 'VALIDATION_ERROR',
  SCHEMA: 'SCHEMA_ERROR',
  TYPE: 'TYPE_ERROR',

  // Authentication errors
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  INVALID_TOKEN: 'INVALID_TOKEN',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  MFA_REQUIRED: 'MFA_REQUIRED',

  // Resource errors
  NOT_FOUND: 'NOT_FOUND',
  ALREADY_EXISTS: 'ALREADY_EXISTS',
  CONFLICT: 'CONFLICT',
  RESOURCE_LOCKED: 'RESOURCE_LOCKED',

  // Database errors
  DB_CONNECTION: 'DB_CONNECTION_ERROR',
  DB_QUERY: 'DB_QUERY_ERROR',
  DB_TIMEOUT: 'DB_TIMEOUT',
  DB_DUPLICATE: 'DB_DUPLICATE_KEY',

  // External service errors
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  SERVICE_TIMEOUT: 'SERVICE_TIMEOUT',
  SERVICE_RESPONSE: 'SERVICE_RESPONSE_ERROR',

  // Rate limiting
  RATE_LIMIT: 'RATE_LIMIT_EXCEEDED',
  QUOTA_EXCEEDED: 'QUOTA_EXCEEDED',

  // Business logic errors
  BUSINESS_RULE: 'BUSINESS_RULE_VIOLATION',
  INSUFFICIENT_FUNDS: 'INSUFFICIENT_FUNDS',
  INVALID_STATE: 'INVALID_STATE',

  // File errors
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  INVALID_FILE_TYPE: 'INVALID_FILE_TYPE',
  FILE_CORRUPT: 'FILE_CORRUPT',

  // Network errors
  NETWORK: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT_ERROR',

  // System errors
  SYSTEM: 'SYSTEM_ERROR',
  MEMORY: 'MEMORY_ERROR',
  DISK: 'DISK_ERROR',
  UNKNOWN: 'UNKNOWN_ERROR'
};

export const ErrorSeverity = {
  DEBUG: 0,
  INFO: 1,
  WARNING: 2,
  ERROR: 3,
  CRITICAL: 4,
  FATAL: 5
};

// ============================================================================
// ERROR MAPPINGS
// ============================================================================

const ErrorMappings = {
  // HTTP status code mapping
  httpStatus: {
    [ErrorTypes.VALIDATION]: 400,
    [ErrorTypes.SCHEMA]: 400,
    [ErrorTypes.TYPE]: 400,
    [ErrorTypes.UNAUTHORIZED]: 401,
    [ErrorTypes.INVALID_TOKEN]: 401,
    [ErrorTypes.TOKEN_EXPIRED]: 401,
    [ErrorTypes.FORBIDDEN]: 403,
    [ErrorTypes.MFA_REQUIRED]: 403,
    [ErrorTypes.NOT_FOUND]: 404,
    [ErrorTypes.ALREADY_EXISTS]: 409,
    [ErrorTypes.CONFLICT]: 409,
    [ErrorTypes.RESOURCE_LOCKED]: 423,
    [ErrorTypes.RATE_LIMIT]: 429,
    [ErrorTypes.QUOTA_EXCEEDED]: 429,
    [ErrorTypes.SERVICE_UNAVAILABLE]: 503,
    [ErrorTypes.SERVICE_TIMEOUT]: 504,
    [ErrorTypes.DB_CONNECTION]: 503,
    [ErrorTypes.DB_TIMEOUT]: 504
  },

  // Severity mapping
  severity: {
    [ErrorTypes.VALIDATION]: ErrorSeverity.INFO,
    [ErrorTypes.SCHEMA]: ErrorSeverity.INFO,
    [ErrorTypes.TYPE]: ErrorSeverity.INFO,
    [ErrorTypes.UNAUTHORIZED]: ErrorSeverity.WARNING,
    [ErrorTypes.INVALID_TOKEN]: ErrorSeverity.WARNING,
    [ErrorTypes.TOKEN_EXPIRED]: ErrorSeverity.INFO,
    [ErrorTypes.FORBIDDEN]: ErrorSeverity.WARNING,
    [ErrorTypes.MFA_REQUIRED]: ErrorSeverity.INFO,
    [ErrorTypes.NOT_FOUND]: ErrorSeverity.INFO,
    [ErrorTypes.ALREADY_EXISTS]: ErrorSeverity.INFO,
    [ErrorTypes.CONFLICT]: ErrorSeverity.WARNING,
    [ErrorTypes.RESOURCE_LOCKED]: ErrorSeverity.WARNING,
    [ErrorTypes.RATE_LIMIT]: ErrorSeverity.INFO,
    [ErrorTypes.QUOTA_EXCEEDED]: ErrorSeverity.WARNING,
    [ErrorTypes.SERVICE_UNAVAILABLE]: ErrorSeverity.ERROR,
    [ErrorTypes.SERVICE_TIMEOUT]: ErrorSeverity.ERROR,
    [ErrorTypes.SERVICE_RESPONSE]: ErrorSeverity.ERROR,
    [ErrorTypes.DB_CONNECTION]: ErrorSeverity.CRITICAL,
    [ErrorTypes.DB_QUERY]: ErrorSeverity.ERROR,
    [ErrorTypes.DB_TIMEOUT]: ErrorSeverity.ERROR,
    [ErrorTypes.DB_DUPLICATE]: ErrorSeverity.INFO,
    [ErrorTypes.BUSINESS_RULE]: ErrorSeverity.WARNING,
    [ErrorTypes.INSUFFICIENT_FUNDS]: ErrorSeverity.WARNING,
    [ErrorTypes.INVALID_STATE]: ErrorSeverity.ERROR,
    [ErrorTypes.FILE_TOO_LARGE]: ErrorSeverity.INFO,
    [ErrorTypes.INVALID_FILE_TYPE]: ErrorSeverity.INFO,
    [ErrorTypes.FILE_CORRUPT]: ErrorSeverity.ERROR,
    [ErrorTypes.NETWORK]: ErrorSeverity.WARNING,
    [ErrorTypes.TIMEOUT]: ErrorSeverity.WARNING,
    [ErrorTypes.SYSTEM]: ErrorSeverity.CRITICAL,
    [ErrorTypes.MEMORY]: ErrorSeverity.CRITICAL,
    [ErrorTypes.DISK]: ErrorSeverity.CRITICAL,
    [ErrorTypes.UNKNOWN]: ErrorSeverity.ERROR
  },

  // Retry configuration
  retry: {
    [ErrorTypes.SERVICE_UNAVAILABLE]: { maxAttempts: 3, delay: 1000, backoff: 'exponential' },
    [ErrorTypes.SERVICE_TIMEOUT]: { maxAttempts: 2, delay: 500, backoff: 'linear' },
    [ErrorTypes.NETWORK]: { maxAttempts: 3, delay: 1000, backoff: 'exponential' },
    [ErrorTypes.TIMEOUT]: { maxAttempts: 2, delay: 500, backoff: 'linear' },
    [ErrorTypes.DB_CONNECTION]: { maxAttempts: 5, delay: 2000, backoff: 'exponential' },
    [ErrorTypes.DB_TIMEOUT]: { maxAttempts: 3, delay: 1000, backoff: 'exponential' }
  },

  // User-friendly messages
  userMessages: {
    [ErrorTypes.VALIDATION]: 'Please check your input and try again.',
    [ErrorTypes.UNAUTHORIZED]: 'Please log in to continue.',
    [ErrorTypes.FORBIDDEN]: 'You do not have permission to perform this action.',
    [ErrorTypes.NOT_FOUND]: 'The requested resource was not found.',
    [ErrorTypes.RATE_LIMIT]: 'Too many requests. Please try again later.',
    [ErrorTypes.SERVICE_UNAVAILABLE]: 'Service temporarily unavailable. Please try again later.',
    [ErrorTypes.DB_CONNECTION]: 'System temporarily unavailable. Please try again later.',
    [ErrorTypes.INSUFFICIENT_FUNDS]: 'Insufficient funds for this transaction.',
    [ErrorTypes.FILE_TOO_LARGE]: 'The file is too large. Please upload a smaller file.',
    [ErrorTypes.INVALID_FILE_TYPE]: 'Invalid file type. Please upload a supported format.'
  }
};

// ============================================================================
// CUSTOM ERROR CLASS
// ============================================================================

export class AppError extends Error {
  constructor(message, type = ErrorTypes.UNKNOWN, metadata = {}) {
    super(message);
    this.name = 'AppError';
    this.type = type;
    this.metadata = metadata;
    this.timestamp = new Date().toISOString();
    this.severity = ErrorMappings.severity[type] || ErrorSeverity.ERROR;
    this.httpStatus = ErrorMappings.httpStatus[type] || 500;
    this.retry = ErrorMappings.retry[type];
    this.userMessage = ErrorMappings.userMessages[type] || 'An unexpected error occurred.';

    // Capture stack trace
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      success: false,
      error: {
        type: this.type,
        message: this.message,
        userMessage: this.userMessage,
        timestamp: this.timestamp,
        requestId: this.metadata.requestId,
        ...(process.env.NODE_ENV !== 'production' && {
          stack: this.stack,
          metadata: this.metadata
        })
      }
    };
  }
}

// ============================================================================
// ERROR HANDLER FUNCTIONS
// ============================================================================

/**
 * Handle error and format response
 * @param {Error} error - Error object
 * @param {Object} req - Request object
 * @param {Object} res - Response object
 * @param {Function} next - Next middleware
 */
export const errorHandler = (error, req, res, next) => {
  // Log error
  logError(error, req);

  // Format error response
  const response = formatErrorResponse(error, req);

  // Send response
  res.status(response.error.httpStatus || 500).json(response);

  // Trigger alerts for critical errors
  if (isCriticalError(error)) {
    triggerAlert(error, req);
  }
};

/**
 * Format error for response
 * @param {Error} error - Error object
 * @param {Object} req - Request object
 * @returns {Object} Formatted error response
 */
export const formatErrorResponse = (error, req) => {
  const baseResponse = {
    success: false,
    timestamp: new Date().toISOString(),
    requestId: req?.id || req?.requestId
  };

  // Handle AppError instances
  if (error instanceof AppError) {
    return {
      ...baseResponse,
      error: {
        type: error.type,
        message: error.message,
        userMessage: error.userMessage,
        httpStatus: error.httpStatus,
        ...(process.env.NODE_ENV !== 'production' && {
          stack: error.stack,
          metadata: error.metadata
        })
      }
    };
  }

  // Handle Mongoose errors
  if (error.name === 'ValidationError') {
    return {
      ...baseResponse,
      error: {
        type: ErrorTypes.VALIDATION,
        message: 'Validation failed',
        userMessage: 'Please check your input and try again.',
        httpStatus: 400,
        details: Object.values(error.errors).map(e => ({
          field: e.path,
          message: e.message
        }))
      }
    };
  }

  if (error.name === 'CastError') {
    return {
      ...baseResponse,
      error: {
        type: ErrorTypes.TYPE,
        message: `Invalid ${error.path}: ${error.value}`,
        userMessage: 'Invalid data format.',
        httpStatus: 400
      }
    };
  }

  if (error.code === 11000) {
    const field = Object.keys(error.keyPattern)[0];
    return {
      ...baseResponse,
      error: {
        type: ErrorTypes.ALREADY_EXISTS,
        message: `${field} already exists`,
        userMessage: `This ${field} is already in use.`,
        httpStatus: 409
      }
    };
  }

  // Handle JWT errors
  if (error.name === 'JsonWebTokenError') {
    return {
      ...baseResponse,
      error: {
        type: ErrorTypes.INVALID_TOKEN,
        message: 'Invalid token',
        userMessage: 'Please log in again.',
        httpStatus: 401
      }
    };
  }

  if (error.name === 'TokenExpiredError') {
    return {
      ...baseResponse,
      error: {
        type: ErrorTypes.TOKEN_EXPIRED,
        message: 'Token expired',
        userMessage: 'Your session has expired. Please log in again.',
        httpStatus: 401
      }
    };
  }

  // Handle unknown errors
  return {
    ...baseResponse,
    error: {
      type: ErrorTypes.UNKNOWN,
      message: error.message || 'An unexpected error occurred',
      userMessage: 'An unexpected error occurred. Please try again later.',
      httpStatus: 500,
      ...(process.env.NODE_ENV !== 'production' && {
        stack: error.stack,
        name: error.name,
        code: error.code
      })
    }
  };
};

/**
 * Log error to console and monitoring service
 * @param {Error} error - Error object
 * @param {Object} req - Request object
 */
export const logError = (error, req) => {
  const errorLog = {
    timestamp: new Date().toISOString(),
    type: error.type || error.name,
    message: error.message,
    stack: error.stack,
    severity: error.severity || ErrorSeverity.ERROR,
    requestId: req?.id || req?.requestId,
    userId: req?.user?.id,
    tenantId: req?.user?.tenantId,
    path: req?.path,
    method: req?.method,
    ip: req?.ip,
    userAgent: req?.headers?.['user-agent']
  };

  // Log to console with appropriate level
  const severity = error.severity || ErrorSeverity.ERROR;

  switch (severity) {
    case ErrorSeverity.DEBUG:
      console.debug('[ERROR]', errorLog);
      break;
    case ErrorSeverity.INFO:
      console.info('[ERROR]', errorLog);
      break;
    case ErrorSeverity.WARNING:
      console.warn('[ERROR]', errorLog);
      break;
    case ErrorSeverity.ERROR:
      console.error('[ERROR]', errorLog);
      break;
    case ErrorSeverity.CRITICAL:
    case ErrorSeverity.FATAL:
      console.error('[CRITICAL]', errorLog);
      break;
    default:
      console.error('[ERROR]', errorLog);
  }

  // In production, send to logging service
  if (process.env.NODE_ENV === 'production') {
    // sendToLoggingService(errorLog);
  }
};

/**
 * Check if error is critical
 * @param {Error} error - Error object
 * @returns {boolean} True if critical
 */
export const isCriticalError = (error) => {
  const severity = error.severity || ErrorSeverity.ERROR;
  return severity >= ErrorSeverity.CRITICAL;
};

/**
 * Trigger alert for critical errors
 * @param {Error} error - Error object
 * @param {Object} req - Request object
 */
export const triggerAlert = (error, req) => {
  const alert = {
    timestamp: new Date().toISOString(),
    type: error.type || error.name,
    message: error.message,
    severity: error.severity,
    requestId: req?.id || req?.requestId,
    userId: req?.user?.id,
    tenantId: req?.user?.tenantId,
    path: req?.path
  };

  console.warn('[ALERT] Critical error detected:', alert);

  // In production, send alerts
  if (process.env.NODE_ENV === 'production') {
    // sendToAlertingService(alert);
    // sendToSMS(alert);
    // sendToEmail(alert);
  }
};

// ============================================================================
// RETRY MECHANISM
// ============================================================================

/**
 * Retry a failed operation with configurable backoff
 * @param {Function} operation - Async operation to retry
 * @param {Object} options - Retry options
 * @returns {Promise} Operation result
 */
export const withRetry = async (operation, options = {}) => {
  const {
    maxAttempts = 3,
    delay = 1000,
    backoff = 'exponential',
    onRetry = null
  } = options;

  let lastError;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;

      if (attempt === maxAttempts) {
        throw error;
      }

      // Calculate next delay
      let nextDelay = delay;
      if (backoff === 'exponential') {
        nextDelay = delay * Math.pow(2, attempt - 1);
      } else if (backoff === 'linear') {
        nextDelay = delay * attempt;
      }

      // Add jitter to prevent thundering herd
      nextDelay = nextDelay * (0.5 + Math.random());

      if (onRetry) {
        onRetry({ attempt, error, nextDelay });
      }

      await new Promise(resolve => setTimeout(resolve, nextDelay));
    }
  }

  throw lastError;
};

/**
 * Check if error is retryable
 * @param {Error} error - Error object
 * @returns {boolean} True if retryable
 */
export const isRetryable = (error) => {
  const retryableTypes = [
    ErrorTypes.SERVICE_UNAVAILABLE,
    ErrorTypes.SERVICE_TIMEOUT,
    ErrorTypes.NETWORK,
    ErrorTypes.TIMEOUT,
    ErrorTypes.DB_CONNECTION,
    ErrorTypes.DB_TIMEOUT
  ];

  return retryableTypes.includes(error.type) ||
         error.message.includes('ECONNRESET') ||
         error.message.includes('ETIMEDOUT');
};

// ============================================================================
// ERROR CREATION HELPERS
// ============================================================================

/**
 * Create validation error
 * @param {string} message - Error message
 * @param {Object} metadata - Additional metadata
 * @returns {AppError} Validation error
 */
export const createValidationError = (message, metadata = {}) => {
  return new AppError(message, ErrorTypes.VALIDATION, metadata);
};

/**
 * Create unauthorized error
 * @param {string} message - Error message
 * @param {Object} metadata - Additional metadata
 * @returns {AppError} Unauthorized error
 */
export const createUnauthorizedError = (message = 'Authentication required', metadata = {}) => {
  return new AppError(message, ErrorTypes.UNAUTHORIZED, metadata);
};

/**
 * Create forbidden error
 * @param {string} message - Error message
 * @param {Object} metadata - Additional metadata
 * @returns {AppError} Forbidden error
 */
export const createForbiddenError = (message = 'Insufficient permissions', metadata = {}) => {
  return new AppError(message, ErrorTypes.FORBIDDEN, metadata);
};

/**
 * Create not found error
 * @param {string} message - Error message
 * @param {Object} metadata - Additional metadata
 * @returns {AppError} Not found error
 */
export const createNotFoundError = (message = 'Resource not found', metadata = {}) => {
  return new AppError(message, ErrorTypes.NOT_FOUND, metadata);
};

/**
 * Create conflict error
 * @param {string} message - Error message
 * @param {Object} metadata - Additional metadata
 * @returns {AppError} Conflict error
 */
export const createConflictError = (message = 'Resource already exists', metadata = {}) => {
  return new AppError(message, ErrorTypes.CONFLICT, metadata);
};

/**
 * Create rate limit error
 * @param {string} message - Error message
 * @param {Object} metadata - Additional metadata
 * @returns {AppError} Rate limit error
 */
export const createRateLimitError = (message = 'Too many requests', metadata = {}) => {
  return new AppError(message, ErrorTypes.RATE_LIMIT, metadata);
};

/**
 * Create service unavailable error
 * @param {string} message - Error message
 * @param {Object} metadata - Additional metadata
 * @returns {AppError} Service unavailable error
 */
export const createServiceUnavailableError = (message = 'Service temporarily unavailable', metadata = {}) => {
  return new AppError(message, ErrorTypes.SERVICE_UNAVAILABLE, metadata);
};

/**
 * Create business rule error
 * @param {string} message - Error message
 * @param {Object} metadata - Additional metadata
 * @returns {AppError} Business rule error
 */
export const createBusinessRuleError = (message, metadata = {}) => {
  return new AppError(message, ErrorTypes.BUSINESS_RULE, metadata);
};

// ============================================================================
// ASYNC ERROR WRAPPER
// ============================================================================

/**
 * Wrap async route handler to catch errors
 * @param {Function} fn - Async route handler
 * @returns {Function} Wrapped handler
 */
export const catchAsync = (fn) => {
  return (req, res, next) => {
    fn(req, res, next).catch(next);
  };
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  AppError,
  errorHandler,
  formatErrorResponse,
  logError,
  isCriticalError,
  triggerAlert,
  withRetry,
  isRetryable,
  createValidationError,
  createUnauthorizedError,
  createForbiddenError,
  createNotFoundError,
  createConflictError,
  createRateLimitError,
  createServiceUnavailableError,
  createBusinessRuleError,
  catchAsync,
  ErrorTypes,
  ErrorSeverity
};
