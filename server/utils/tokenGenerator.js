/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN TOKEN GENERATOR                                      ║
 * ║ [JWT TOKENS | ACCESS TOKENS | REFRESH TOKENS | API KEYS]                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * @team Collaboration Notes:
 * - Cryptographically secure token generation
 * - Multiple token types with different lifetimes
 * - Token validation and revocation
 * - Support for stateless and stateful tokens
 * - 101/10 security standard
 *
 * @last_updated: 2026-03-18
 * @lead_architect: Wilson Khanyezi
 */

import jwt from 'jsonwebtoken';
import crypto from 'crypto';

// ============================================================================
// CONFIGURATION
// ============================================================================

const TOKEN_CONFIG = {
  // JWT settings
  jwt: {
    accessSecret: process.env.JWT_ACCESS_SECRET || crypto.randomBytes(64).toString('hex'),
    refreshSecret: process.env.JWT_REFRESH_SECRET || crypto.randomBytes(64).toString('hex'),
    issuer: 'wilsy-os',
    audience: 'wilsy-api',
    algorithms: ['HS256', 'HS384', 'HS512']
  },

  // Token lifetimes
  lifetimes: {
    access: '15m',           // 15 minutes
    refresh: '7d',           // 7 days
    emailVerification: '24h', // 24 hours
    passwordReset: '1h',      // 1 hour
    apiKey: '1y',            // 1 year
    session: '30d',          // 30 days
    mfa: '5m',               // 5 minutes
    rememberMe: '30d'        // 30 days
  },

  // Token lengths (for non-JWT tokens)
  lengths: {
    apiKey: 32,
    secret: 64,
    verificationCode: 6,
    recoveryCode: 16,
    inviteCode: 12,
    shareToken: 24
  },

  // Rate limiting
  rateLimit: {
    maxTokensPerUser: 10,
    maxApiKeysPerUser: 5,
    windowMs: 60 * 60 * 1000 // 1 hour
  }
};

// ============================================================================
// TOKEN STORE (In production, use Redis)
// ============================================================================

class TokenStore {
  constructor() {
    this.tokens = new Map();
    this.revokedTokens = new Set();
    this.blacklistedTokens = new Set();
  }

  /**
   * Store token metadata
   * @param {string} tokenId - Token ID
   * @param {Object} metadata - Token metadata
   */
  store(tokenId, metadata) {
    this.tokens.set(tokenId, {
      ...metadata,
      createdAt: new Date().toISOString()
    });
  }

  /**
   * Get token metadata
   * @param {string} tokenId - Token ID
   * @returns {Object} Token metadata
   */
  get(tokenId) {
    return this.tokens.get(tokenId);
  }

  /**
   * Revoke token
   * @param {string} tokenId - Token ID
   * @param {string} reason - Revocation reason
   */
  revoke(tokenId, reason = 'user_action') {
    const token = this.tokens.get(tokenId);
    if (token) {
      token.revoked = true;
      token.revokedAt = new Date().toISOString();
      token.revocationReason = reason;
      this.revokedTokens.add(tokenId);
    }
  }

  /**
   * Check if token is revoked
   * @param {string} tokenId - Token ID
   * @returns {boolean} True if revoked
   */
  isRevoked(tokenId) {
    return this.revokedTokens.has(tokenId);
  }

  /**
   * Blacklist token (for logout)
   * @param {string} tokenId - Token ID
   */
  blacklist(tokenId) {
    this.blacklistedTokens.add(tokenId);
  }

  /**
   * Check if token is blacklisted
   * @param {string} tokenId - Token ID
   * @returns {boolean} True if blacklisted
   */
  isBlacklisted(tokenId) {
    return this.blacklistedTokens.has(tokenId);
  }

  /**
   * Clean up expired tokens
   */
  cleanup() {
    const now = Date.now();
    for (const [tokenId, token] of this.tokens.entries()) {
      if (token.expiresAt && new Date(token.expiresAt).getTime() < now) {
        this.tokens.delete(tokenId);
        this.revokedTokens.delete(tokenId);
        this.blacklistedTokens.delete(tokenId);
      }
    }
  }
}

const tokenStore = new TokenStore();

// Run cleanup every hour
setInterval(() => tokenStore.cleanup(), 60 * 60 * 1000);

// ============================================================================
// JWT TOKEN GENERATION
// ============================================================================

/**
 * Generate JWT access token
 * @param {Object} payload - Token payload
 * @param {Object} options - Token options
 * @returns {Object} Generated token
 */
export const generateAccessToken = (payload, options = {}) => {
  const {
    expiresIn = TOKEN_CONFIG.lifetimes.access,
    subject,
    audience = TOKEN_CONFIG.jwt.audience,
    issuer = TOKEN_CONFIG.jwt.issuer
  } = options;

  const tokenId = crypto.randomBytes(16).toString('hex');
  const jti = `acc_${tokenId}`;

  const tokenPayload = {
    ...payload,
    jti,
    type: 'access',
    tokenId
  };

  const token = jwt.sign(tokenPayload, TOKEN_CONFIG.jwt.accessSecret, {
    expiresIn,
    subject,
    audience,
    issuer,
    algorithm: 'HS256'
  });

  // Store token metadata
  tokenStore.store(tokenId, {
    type: 'access',
    userId: payload.userId,
    jti,
    expiresIn,
    createdAt: new Date().toISOString()
  });

  return {
    token,
    jti,
    tokenId,
    expiresIn,
    type: 'access'
  };
};

/**
 * Generate JWT refresh token
 * @param {Object} payload - Token payload
 * @param {Object} options - Token options
 * @returns {Object} Generated token
 */
export const generateRefreshToken = (payload, options = {}) => {
  const {
    expiresIn = TOKEN_CONFIG.lifetimes.refresh,
    subject,
    audience = TOKEN_CONFIG.jwt.audience,
    issuer = TOKEN_CONFIG.jwt.issuer
  } = options;

  const tokenId = crypto.randomBytes(16).toString('hex');
  const jti = `ref_${tokenId}`;

  const tokenPayload = {
    userId: payload.userId,
    jti,
    type: 'refresh',
    tokenId,
    version: 1
  };

  const token = jwt.sign(tokenPayload, TOKEN_CONFIG.jwt.refreshSecret, {
    expiresIn,
    subject,
    audience,
    issuer,
    algorithm: 'HS256'
  });

  // Store token metadata
  tokenStore.store(tokenId, {
    type: 'refresh',
    userId: payload.userId,
    jti,
    expiresIn,
    createdAt: new Date().toISOString()
  });

  return {
    token,
    jti,
    tokenId,
    expiresIn,
    type: 'refresh'
  };
};

/**
 * Generate both access and refresh tokens
 * @param {Object} payload - Token payload
 * @param {Object} options - Token options
 * @returns {Object} Token pair
 */
export const generateTokenPair = (payload, options = {}) => {
  const accessToken = generateAccessToken(payload, options);
  const refreshToken = generateRefreshToken(payload, options);

  return {
    accessToken: accessToken.token,
    refreshToken: refreshToken.token,
    accessJti: accessToken.jti,
    refreshJti: refreshToken.jti,
    expiresIn: accessToken.expiresIn
  };
};

// ============================================================================
// TOKEN VALIDATION
// ============================================================================

/**
 * Verify and decode JWT token
 * @param {string} token - JWT token
 * @param {string} type - Token type ('access' or 'refresh')
 * @returns {Object} Decoded token
 */
export const verifyToken = (token, type = 'access') => {
  try {
    const secret = type === 'access'
      ? TOKEN_CONFIG.jwt.accessSecret
      : TOKEN_CONFIG.jwt.refreshSecret;

    const decoded = jwt.verify(token, secret, {
      audience: TOKEN_CONFIG.jwt.audience,
      issuer: TOKEN_CONFIG.jwt.issuer,
      algorithms: TOKEN_CONFIG.jwt.algorithms
    });

    // Check if token type matches
    if (decoded.type !== type) {
      throw new Error('Invalid token type');
    }

    // Check if token is revoked or blacklisted
    if (decoded.tokenId) {
      if (tokenStore.isRevoked(decoded.tokenId)) {
        throw new Error('Token has been revoked');
      }
      if (tokenStore.isBlacklisted(decoded.tokenId)) {
        throw new Error('Token has been blacklisted');
      }
    }

    return {
      valid: true,
      decoded,
      jti: decoded.jti,
      tokenId: decoded.tokenId
    };
  } catch (error) {
    return {
      valid: false,
      error: error.message
    };
  }
};

/**
 * Refresh access token using refresh token
 * @param {string} refreshToken - Refresh token
 * @param {Object} options - Refresh options
 * @returns {Object} New token pair
 */
export const refreshTokens = async (refreshToken, options = {}) => {
  const verification = verifyToken(refreshToken, 'refresh');

  if (!verification.valid) {
    throw new Error('Invalid refresh token');
  }

  const { decoded } = verification;

  // Revoke old refresh token (token rotation)
  if (decoded.tokenId) {
    tokenStore.revoke(decoded.tokenId, 'rotated');
  }

  // Generate new tokens
  const newTokens = generateTokenPair({
    userId: decoded.userId
  }, options);

  return newTokens;
};

// ============================================================================
// SPECIAL PURPOSE TOKENS
// ============================================================================

/**
 * Generate email verification token
 * @param {string} userId - User ID
 * @param {string} email - Email address
 * @returns {Object} Verification token
 */
export const generateEmailVerificationToken = (userId, email) => {
  const tokenId = crypto.randomBytes(16).toString('hex');
  const code = generateNumericCode(TOKEN_CONFIG.lengths.verificationCode);

  const token = jwt.sign(
    {
      userId,
      email,
      code,
      tokenId,
      type: 'email_verification'
    },
    TOKEN_CONFIG.jwt.accessSecret,
    {
      expiresIn: TOKEN_CONFIG.lifetimes.emailVerification
    }
  );

  tokenStore.store(tokenId, {
    type: 'email_verification',
    userId,
    email,
    code,
    expiresIn: TOKEN_CONFIG.lifetimes.emailVerification
  });

  return {
    token,
    code,
    tokenId,
    expiresIn: TOKEN_CONFIG.lifetimes.emailVerification
  };
};

/**
 * Generate password reset token
 * @param {string} userId - User ID
 * @param {string} email - Email address
 * @returns {Object} Reset token
 */
export const generatePasswordResetToken = (userId, email) => {
  const tokenId = crypto.randomBytes(16).toString('hex');
  const code = generateNumericCode(TOKEN_CONFIG.lengths.verificationCode);

  const token = jwt.sign(
    {
      userId,
      email,
      code,
      tokenId,
      type: 'password_reset'
    },
    TOKEN_CONFIG.jwt.accessSecret,
    {
      expiresIn: TOKEN_CONFIG.lifetimes.passwordReset
    }
  );

  tokenStore.store(tokenId, {
    type: 'password_reset',
    userId,
    email,
    code,
    expiresIn: TOKEN_CONFIG.lifetimes.passwordReset
  });

  return {
    token,
    code,
    tokenId,
    expiresIn: TOKEN_CONFIG.lifetimes.passwordReset
  };
};

/**
 * Generate MFA verification token
 * @param {string} userId - User ID
 * @param {string} mfaMethod - MFA method
 * @returns {Object} MFA token
 */
export const generateMFAToken = (userId, mfaMethod) => {
  const tokenId = crypto.randomBytes(16).toString('hex');
  const code = generateNumericCode(TOKEN_CONFIG.lengths.verificationCode);

  const token = jwt.sign(
    {
      userId,
      mfaMethod,
      code,
      tokenId,
      type: 'mfa'
    },
    TOKEN_CONFIG.jwt.accessSecret,
    {
      expiresIn: TOKEN_CONFIG.lifetimes.mfa
    }
  );

  tokenStore.store(tokenId, {
    type: 'mfa',
    userId,
    mfaMethod,
    code,
    expiresIn: TOKEN_CONFIG.lifetimes.mfa
  });

  return {
    token,
    code,
    tokenId,
    expiresIn: TOKEN_CONFIG.lifetimes.mfa
  };
};

/**
 * Generate API key
 * @param {string} userId - User ID
 * @param {string} name - API key name
 * @param {Object} permissions - API key permissions
 * @returns {Object} API key
 */
export const generateApiKey = (userId, name, permissions = {}) => {
  const keyId = crypto.randomBytes(8).toString('hex');
  const secret = crypto.randomBytes(TOKEN_CONFIG.lengths.apiKey).toString('base64');
  const hashedSecret = crypto.createHash('sha256').update(secret).digest('hex');

  const apiKey = `wil_${keyId}_${secret}`;
  const expiresAt = new Date();
  expiresAt.setFullYear(expiresAt.getFullYear() + 1); // 1 year expiry

  tokenStore.store(keyId, {
    type: 'api_key',
    userId,
    name,
    permissions,
    hashedSecret,
    expiresAt: expiresAt.toISOString(),
    lastUsed: null
  });

  return {
    apiKey,
    keyId,
    name,
    expiresAt: expiresAt.toISOString(),
    permissions
  };
};

/**
 * Validate API key
 * @param {string} apiKey - API key to validate
 * @returns {Object} Validation result
 */
export const validateApiKey = (apiKey) => {
  try {
    const parts = apiKey.split('_');
    if (parts.length !== 3 || parts[0] !== 'wil') {
      throw new Error('Invalid API key format');
    }

    const keyId = parts[1];
    const secret = parts[2];

    const keyData = tokenStore.get(keyId);
    if (!keyData) {
      throw new Error('API key not found');
    }

    if (keyData.type !== 'api_key') {
      throw new Error('Invalid key type');
    }

    // Check expiry
    if (keyData.expiresAt && new Date(keyData.expiresAt) < new Date()) {
      throw new Error('API key has expired');
    }

    // Verify secret
    const hashedSecret = crypto.createHash('sha256').update(secret).digest('hex');
    if (hashedSecret !== keyData.hashedSecret) {
      throw new Error('Invalid API key secret');
    }

    // Update last used
    keyData.lastUsed = new Date().toISOString();

    return {
      valid: true,
      userId: keyData.userId,
      keyId,
      name: keyData.name,
      permissions: keyData.permissions
    };
  } catch (error) {
    return {
      valid: false,
      error: error.message
    };
  }
};

// ============================================================================
// TOKEN MANAGEMENT
// ============================================================================

/**
 * Revoke token
 * @param {string} tokenId - Token ID
 * @param {string} reason - Revocation reason
 */
export const revokeToken = (tokenId, reason = 'user_action') => {
  tokenStore.revoke(tokenId, reason);
};

/**
 * Revoke all tokens for user
 * @param {string} userId - User ID
 * @param {string} reason - Revocation reason
 */
export const revokeAllUserTokens = (userId, reason = 'security_measure') => {
  for (const [tokenId, token] of tokenStore.tokens.entries()) {
    if (token.userId === userId && !token.revoked) {
      tokenStore.revoke(tokenId, reason);
    }
  }
};

/**
 * Blacklist token (for logout)
 * @param {string} tokenId - Token ID
 */
export const blacklistToken = (tokenId) => {
  tokenStore.blacklist(tokenId);
};

/**
 * Get token info
 * @param {string} tokenId - Token ID
 * @returns {Object} Token information
 */
export const getTokenInfo = (tokenId) => {
  return tokenStore.get(tokenId);
};

/**
 * List user tokens
 * @param {string} userId - User ID
 * @param {string} type - Token type filter
 * @returns {Array} User tokens
 */
export const listUserTokens = (userId, type = null) => {
  const userTokens = [];

  for (const [tokenId, token] of tokenStore.tokens.entries()) {
    if (token.userId === userId) {
      if (!type || token.type === type) {
        userTokens.push({
          tokenId,
          ...token
        });
      }
    }
  }

  return userTokens;
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Generate cryptographically secure random string
 * @param {number} length - String length
 * @returns {string} Random string
 */
export const generateRandomString = (length = 32) => {
  return crypto.randomBytes(Math.ceil(length / 2))
    .toString('hex')
    .slice(0, length);
};

/**
 * Generate numeric code (for MFA, verification, etc.)
 * @param {number} length - Code length
 * @returns {string} Numeric code
 */
export const generateNumericCode = (length = 6) => {
  const bytes = crypto.randomBytes(length);
  let code = '';
  for (let i = 0; i < length; i++) {
    code += (bytes[i] % 10).toString();
  }
  return code;
};

/**
 * Generate recovery codes
 * @param {number} count - Number of codes
 * @param {number} length - Code length
 * @returns {Array} Recovery codes
 */
export const generateRecoveryCodes = (count = 10, length = 16) => {
  const codes = [];
  for (let i = 0; i < count; i++) {
    codes.push(generateRandomString(length));
  }
  return codes;
};

/**
 * Generate invite token
 * @param {string} email - Email address
 * @param {string} role - Role to assign
 * @returns {Object} Invite token
 */
export const generateInviteToken = (email, role = 'user') => {
  const tokenId = crypto.randomBytes(8).toString('hex');
  const code = generateRandomString(TOKEN_CONFIG.lengths.inviteCode);

  const token = jwt.sign(
    {
      email,
      role,
      code,
      tokenId,
      type: 'invite'
    },
    TOKEN_CONFIG.jwt.accessSecret,
    {
      expiresIn: '7d'
    }
  );

  tokenStore.store(tokenId, {
    type: 'invite',
    email,
    role,
    code,
    expiresIn: '7d'
  });

  return {
    token,
    code,
    tokenId,
    email,
    role
  };
};

// ============================================================================
// TOKEN STATISTICS
// ============================================================================

/**
 * Get token statistics
 * @returns {Object} Token statistics
 */
export const getTokenStats = () => {
  const stats = {
    total: tokenStore.tokens.size,
    revoked: tokenStore.revokedTokens.size,
    blacklisted: tokenStore.blacklistedTokens.size,
    byType: {},
    byUser: new Map()
  };

  for (const [tokenId, token] of tokenStore.tokens.entries()) {
    // Count by type
    stats.byType[token.type] = (stats.byType[token.type] || 0) + 1;

    // Count by user
    if (token.userId) {
      const count = stats.byUser.get(token.userId) || 0;
      stats.byUser.set(token.userId, count + 1);
    }
  }

  return {
    ...stats,
    byUser: Object.fromEntries(stats.byUser)
  };
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  generateAccessToken,
  generateRefreshToken,
  generateTokenPair,
  verifyToken,
  refreshTokens,
  generateEmailVerificationToken,
  generatePasswordResetToken,
  generateMFAToken,
  generateApiKey,
  validateApiKey,
  revokeToken,
  revokeAllUserTokens,
  blacklistToken,
  getTokenInfo,
  listUserTokens,
  generateRandomString,
  generateNumericCode,
  generateRecoveryCodes,
  generateInviteToken,
  getTokenStats,
  TOKEN_CONFIG
};
