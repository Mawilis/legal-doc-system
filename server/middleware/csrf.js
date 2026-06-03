/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN CSRF PROTECTION MIDDLEWARE                          ║
 * ║ [CROSS-SITE REQUEST FORGERY PREVENTION | TOKEN MANAGEMENT]               ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * @team Collaboration Notes:
 * - Implements double-submit cookie pattern for CSRF protection
 * - Generates and validates cryptographically secure CSRF tokens
 * - Supports both session-based and stateless validation
 * - Configurable for different HTTP methods
 * - 101/10 security standard
 *
 * @last_updated: 2026-03-18
 * @lead_architect: Wilson Khanyezi
 */

import crypto from 'crypto';

// ============================================================================
// CONFIGURATION
// ============================================================================

const CSRF_TOKEN_LENGTH = 32;
const CSRF_COOKIE_NAME = 'XSRF-TOKEN';
const CSRF_HEADER_NAME = 'x-csrf-token';
const CSRF_TOKEN_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours

// Store for CSRF tokens (in production, use Redis)
const tokenStore = new Map();

// Methods that require CSRF protection
const PROTECTED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE'];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Generate a cryptographically secure CSRF token
 * @param {string} sessionId - Session identifier
 * @returns {string} CSRF token
 */
const generateToken = (sessionId) => {
  const randomBytes = crypto.randomBytes(CSRF_TOKEN_LENGTH);
  const token = randomBytes.toString('hex');

  // Store token with expiry
  tokenStore.set(token, {
    sessionId,
    createdAt: Date.now(),
    expiresAt: Date.now() + CSRF_TOKEN_EXPIRY
  });

  // Clean up expired tokens periodically
  setTimeout(() => {
    tokenStore.delete(token);
  }, CSRF_TOKEN_EXPIRY);

  return token;
};

/**
 * Validate a CSRF token
 * @param {string} token - Token to validate
 * @param {string} sessionId - Session identifier
 * @returns {boolean} True if token is valid
 */
const validateToken = (token, sessionId) => {
  const stored = tokenStore.get(token);

  if (!stored) return false;
  if (stored.sessionId !== sessionId) return false;
  if (stored.expiresAt < Date.now()) {
    tokenStore.delete(token);
    return false;
  }

  return true;
};

/**
 * Extract token from request
 * @param {Object} req - Express request object
 * @returns {string|null} Extracted token or null
 */
const extractTokenFromRequest = (req) => {
  // Check header first
  let token = req.headers[CSRF_HEADER_NAME];

  // Check body if not in header
  if (!token && req.body && req.body._csrf) {
    token = req.body._csrf;
    delete req.body._csrf; // Remove from body after extraction
  }

  // Check query if not found
  if (!token && req.query && req.query._csrf) {
    token = req.query._csrf;
  }

  return token;
};

/**
 * Get session identifier from request
 * @param {Object} req - Express request object
 * @returns {string} Session identifier
 */
const getSessionId = (req) => {
  // Try to get from authenticated user
  if (req.user && req.user._id) {
    return req.user._id.toString();
  }

  // Try to get from session
  if (req.session && req.session.id) {
    return req.session.id;
  }

  // Fallback to IP + User-Agent
  const ip = req.ip || req.connection.remoteAddress || 'unknown';
  const ua = req.headers['user-agent'] || 'unknown';
  return crypto.createHash('sha256').update(`${ip}|${ua}`).digest('hex');
};

// ============================================================================
// CSRF MIDDLEWARE
// ============================================================================

/**
 * CSRF protection middleware
 * @param {Object} options - Configuration options
 * @returns {Function} Express middleware
 */
export const csrfProtection = (options = {}) => {
  const {
    cookieName = CSRF_COOKIE_NAME,
    headerName = CSRF_HEADER_NAME,
    protectedMethods = PROTECTED_METHODS,
    setTokenOnGet = true
  } = options;

  return (req, res, next) => {
    // Skip CSRF for non-protected methods
    if (!protectedMethods.includes(req.method)) {
      if (setTokenOnGet && req.method === 'GET') {
        // Generate and set CSRF token for GET requests
        const sessionId = getSessionId(req);
        const token = generateToken(sessionId);

        // Set cookie
        res.cookie(cookieName, token, {
          httpOnly: false, // Must be accessible to JavaScript
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'strict',
          maxAge: CSRF_TOKEN_EXPIRY,
          path: '/'
        });

        // Attach token to request for convenience
        req.csrfToken = token;
      }
      return next();
    }

    // For protected methods, validate CSRF token
    const sessionId = getSessionId(req);
    const cookieToken = req.cookies?.[cookieName];
    const requestToken = extractTokenFromRequest(req);

    // Log CSRF attempt for forensic audit
    const logCSRFAttempt = () => {
      console.warn('[CSRF] Potential CSRF attack detected:', {
        ip: req.ip,
        path: req.path,
        method: req.method,
        sessionId,
        hasCookieToken: !!cookieToken,
        hasRequestToken: !!requestToken,
        userAgent: req.headers['user-agent'],
        timestamp: new Date().toISOString()
      });
    };

    // Check if tokens exist
    if (!cookieToken || !requestToken) {
      logCSRFAttempt();
      return res.status(403).json({
        success: false,
        error: 'CSRF_TOKEN_MISSING',
        message: 'CSRF token is missing'
      });
    }

    // Validate cookie token
    if (!validateToken(cookieToken, sessionId)) {
      logCSRFAttempt();
      return res.status(403).json({
        success: false,
        error: 'CSRF_TOKEN_INVALID',
        message: 'Invalid or expired CSRF token'
      });
    }

    // Validate request token matches cookie token
    if (cookieToken !== requestToken) {
      logCSRFAttempt();
      return res.status(403).json({
        success: false,
        error: 'CSRF_TOKEN_MISMATCH',
        message: 'CSRF token mismatch'
      });
    }

    // Generate new token for next request
    const newToken = generateToken(sessionId);
    res.cookie(cookieName, newToken, {
      httpOnly: false,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: CSRF_TOKEN_EXPIRY,
      path: '/'
    });

    req.csrfToken = newToken;
    next();
  };
};

// ============================================================================
// CSRF ERROR HANDLER
// ============================================================================

/**
 * CSRF error handler middleware
 * Catches CSRF-related errors and formats response
 */
export const csrfErrorHandler = (err, req, res, next) => {
  if (err.code === 'EBADCSRFTOKEN') {
    console.warn('[CSRF] Invalid CSRF token detected:', {
      ip: req.ip,
      path: req.path,
      userAgent: req.headers['user-agent'],
      timestamp: new Date().toISOString()
    });

    return res.status(403).json({
      success: false,
      error: 'CSRF_VALIDATION_FAILED',
      message: 'Invalid CSRF token'
    });
  }
  next(err);
};

// ============================================================================
// TOKEN MANAGEMENT API
// ============================================================================

/**
 * Get a new CSRF token (for AJAX requests)
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
export const getCsrfToken = (req, res) => {
  const sessionId = getSessionId(req);
  const token = generateToken(sessionId);

  res.cookie(CSRF_COOKIE_NAME, token, {
    httpOnly: false,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: CSRF_TOKEN_EXPIRY,
    path: '/'
  });

  res.json({
    success: true,
    data: {
      csrfToken: token,
      headerName: CSRF_HEADER_NAME,
      cookieName: CSRF_COOKIE_NAME
    }
  });
};

/**
 * Clear CSRF token (on logout)
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
export const clearCsrfToken = (req, res) => {
  const token = req.cookies?.[CSRF_COOKIE_NAME];
  if (token) {
    tokenStore.delete(token);
  }

  res.clearCookie(CSRF_COOKIE_NAME);
};

// ============================================================================
// DOUBLE SUBMIT COOKIE VALIDATOR
// ============================================================================

/**
 * Double submit cookie validator for stateless CSRF protection
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Next middleware
 */
export const doubleSubmitCookie = (req, res, next) => {
  if (!PROTECTED_METHODS.includes(req.method)) {
    return next();
  }

  const cookieToken = req.cookies?.[CSRF_COOKIE_NAME];
  const headerToken = req.headers[CSRF_HEADER_NAME];

  if (!cookieToken || !headerToken || cookieToken !== headerToken) {
    console.warn('[CSRF] Double submit cookie validation failed:', {
      ip: req.ip,
      path: req.path,
      method: req.method,
      timestamp: new Date().toISOString()
    });

    return res.status(403).json({
      success: false,
      error: 'CSRF_VALIDATION_FAILED',
      message: 'CSRF validation failed'
    });
  }

  next();
};

// ============================================================================
// SAME-SITE COOKIE ENFORCER
// ============================================================================

/**
 * Enforces SameSite cookie attribute
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Next middleware
 */
export const enforceSameSite = (req, res, next) => {
  // Store original cookie method
  const originalCookie = res.cookie;

  // Override cookie method
  res.cookie = function(name, value, options = {}) {
    // Ensure SameSite is set for cookies that should be protected
    if (name === CSRF_COOKIE_NAME || name.includes('session') || name.includes('token')) {
      options.sameSite = options.sameSite || 'strict';
      options.secure = options.secure ?? process.env.NODE_ENV === 'production';
      options.httpOnly = options.httpOnly ?? true;
    }

    return originalCookie.call(this, name, value, options);
  };

  next();
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  csrfProtection,
  csrfErrorHandler,
  getCsrfToken,
  clearCsrfToken,
  doubleSubmitCookie,
  enforceSameSite,
  generateToken,
  validateToken
};
