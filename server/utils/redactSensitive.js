/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN SENSITIVE DATA REDACTION UTILITY                     ║
 * ║ [PII PROTECTION | GDPR COMPLIANCE | POPIA COMPLIANCE | AUDIT SAFETY]     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * @team Collaboration Notes:
 * - Redacts personally identifiable information (PII)
 * - GDPR and POPIA compliant data protection
 * - Multiple redaction levels for different contexts
 * - Preserves data structure while protecting sensitive fields
 * - 101/10 privacy standard
 *
 * @last_updated: 2026-03-18
 * @lead_architect: Wilson Khanyezi
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

const REDACTION_CONFIG = {
  // Default redaction level
  defaultLevel: 'medium',

  // Redaction levels
  levels: {
    low: {
      name: 'Low',
      description: 'Redact only most sensitive fields',
      maskLength: 4
    },
    medium: {
      name: 'Medium',
      description: 'Redact all PII, show last 4 characters',
      maskLength: 4
    },
    high: {
      name: 'High',
      description: 'Full redaction of all sensitive fields',
      maskLength: 0
    },
    audit: {
      name: 'Audit',
      description: 'Maximum redaction for audit logs',
      maskLength: 0
    }
  },

  // Sensitive field patterns
  sensitivePatterns: {
    // Identity fields
    idNumber: /\b\d{13}\b|\b\d{2}[01]\d[0-3]\d\d{7}\b/g,
    passport: /\b[A-Z]{2}\d{7}\b|\b\d{9}\b/g,
    driverLicense: /\b\d{13}\b|\b[A-Z0-9]{8,12}\b/g,

    // Contact information
    email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    phone: /\b(\+?\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b/g,

    // Financial information
    creditCard: /\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{16}\b/g,
    bankAccount: /\b\d{10,12}\b/g,
    routingNumber: /\b\d{9}\b/g,

    // Authentication
    password: /password|passwd|pwd|secret|token|api[_-]?key/gi,

    // Biometric
    fingerprint: /fingerprint|biometric|faceid|touchid/gi,

    // Location
    coordinates: /-?\d{1,3}\.\d+,-?\d{1,3}\.\d+/g,
    address: /\d{1,5}\s+\w+\s+\w+\s*(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|court|ct|circle|cir)/gi
  },

  // Field names to always redact (case insensitive)
  sensitiveFields: [
    'password',
    'passwd',
    'pwd',
    'secret',
    'token',
    'apiKey',
    'api_key',
    'apikey',
    'accessToken',
    'refreshToken',
    'jwt',
    'authorization',
    'creditCard',
    'credit_card',
    'ccNumber',
    'ccv',
    'cvv',
    'pin',
    'ssn',
    'socialSecurity',
    'taxId',
    'idNumber',
    'passport',
    'driverLicense',
    'bankAccount',
    'routingNumber',
    'iban',
    'swift',
    'bic',
    'fingerprint',
    'biometric',
    'faceId',
    'touchId',
    'privateKey',
    'publicKey',
    'seed',
    'mnemonic',
    'recoveryPhrase'
  ],

  // Fields to partially redact (show last N characters)
  partialFields: [
    'email',
    'phone',
    'username',
    'name',
    'firstName',
    'lastName',
    'address',
    'city',
    'country'
  ],

  // Fields to keep as is (safe fields)
  safeFields: [
    'id',
    '_id',
    'createdAt',
    'updatedAt',
    'timestamp',
    'date',
    'status',
    'type',
    'category',
    'tags',
    'metadata',
    'version',
    'count',
    'total',
    'limit',
    'offset',
    'page'
  ]
};

// ============================================================================
// REDACTION STRATEGIES
// ============================================================================

/**
 * Redact a value based on its type and field name
 * @param {*} value - Value to redact
 * @param {string} fieldName - Field name
 * @param {string} level - Redaction level
 * @returns {*} Redacted value
 */
const redactValue = (value, fieldName, level = REDACTION_CONFIG.defaultLevel) => {
  const config = REDACTION_CONFIG.levels[level] || REDACTION_CONFIG.levels.medium;

  // Handle null/undefined
  if (value === null || value === undefined) {
    return value;
  }

  // Handle different types
  if (typeof value === 'string') {
    return redactString(value, fieldName, level);
  }

  if (typeof value === 'number') {
    return redactNumber(value, fieldName, level);
  }

  if (typeof value === 'boolean') {
    return value; // Booleans are safe
  }

  if (Array.isArray(value)) {
    return value.map(item => redactValue(item, fieldName, level));
  }

  if (typeof value === 'object') {
    return redactObject(value, level);
  }

  return value;
};

/**
 * Redact a string value
 * @param {string} value - String to redact
 * @param {string} fieldName - Field name
 * @param {string} level - Redaction level
 * @returns {string} Redacted string
 */
const redactString = (value, fieldName, level) => {
  const config = REDACTION_CONFIG.levels[level] || REDACTION_CONFIG.levels.medium;

  // Check if field should be fully redacted
  if (isSensitiveField(fieldName)) {
    return '[REDACTED]';
  }

  // Check if field should be partially redacted
  if (shouldPartiallyRedact(fieldName) && config.maskLength > 0) {
    return maskString(value, config.maskLength);
  }

  // Check for sensitive patterns in the string itself
  let redacted = value;
  for (const [type, pattern] of Object.entries(REDACTION_CONFIG.sensitivePatterns)) {
    redacted = redacted.replace(pattern, (match) => {
      return maskString(match, config.maskLength);
    });
  }

  return redacted;
};

/**
 * Redact a number value
 * @param {number} value - Number to redact
 * @param {string} fieldName - Field name
 * @param {string} level - Redaction level
 * @returns {number|string} Redacted value
 */
const redactNumber = (value, fieldName, level) => {
  if (isSensitiveField(fieldName)) {
    return 0;
  }
  return value;
};

/**
 * Redact an object recursively
 * @param {Object} obj - Object to redact
 * @param {string} level - Redaction level
 * @returns {Object} Redacted object
 */
const redactObject = (obj, level) => {
  const redacted = {};

  for (const [key, value] of Object.entries(obj)) {
    redacted[key] = redactValue(value, key, level);
  }

  return redacted;
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Check if a field is sensitive and should be fully redacted
 * @param {string} fieldName - Field name
 * @returns {boolean} True if sensitive
 */
const isSensitiveField = (fieldName) => {
  const lowerField = fieldName.toLowerCase();
  return REDACTION_CONFIG.sensitiveFields.some(field =>
    lowerField.includes(field.toLowerCase())
  );
};

/**
 * Check if a field should be partially redacted
 * @param {string} fieldName - Field name
 * @returns {boolean} True if partial redaction
 */
const shouldPartiallyRedact = (fieldName) => {
  const lowerField = fieldName.toLowerCase();
  return REDACTION_CONFIG.partialFields.some(field =>
    lowerField.includes(field.toLowerCase())
  );
};

/**
 * Mask a string, showing only last N characters
 * @param {string} str - String to mask
 * @param {number} visibleChars - Number of characters to show
 * @returns {string} Masked string
 */
const maskString = (str, visibleChars = 4) => {
  if (!str) return str;
  if (str.length <= visibleChars) return '*'.repeat(str.length);

  const visible = str.slice(-visibleChars);
  const masked = '*'.repeat(str.length - visibleChars);
  return masked + visible;
};

/**
 * Mask email address
 * @param {string} email - Email to mask
 * @returns {string} Masked email
 */
const maskEmail = (email) => {
  const [local, domain] = email.split('@');
  if (!domain) return maskString(email);

  const maskedLocal = maskString(local, 2);
  return `${maskedLocal}@${domain}`;
};

/**
 * Mask phone number
 * @param {string} phone - Phone number to mask
 * @returns {string} Masked phone
 */
const maskPhone = (phone) => {
  const cleaned = phone.replace(/[^\d+]/g, '');
  if (cleaned.length <= 4) return maskString(phone);

  const visible = cleaned.slice(-4);
  const masked = '*'.repeat(cleaned.length - 4);
  return masked + visible;
};

// ============================================================================
// MAIN REDACTION FUNCTIONS
// ============================================================================

/**
 * Redact sensitive data from an object
 * @param {Object} data - Data to redact
 * @param {Object} options - Redaction options
 * @returns {Object} Redacted data
 */
export const redactSensitive = (data, options = {}) => {
  const {
    level = REDACTION_CONFIG.defaultLevel,
    preserveStructure = true,
    deepRedact = true
  } = options;

  if (!data) return data;

  try {
    // Handle primitives
    if (typeof data !== 'object') {
      return redactValue(data, '', level);
    }

    // Handle arrays
    if (Array.isArray(data)) {
      return data.map(item => redactSensitive(item, options));
    }

    // Handle objects
    const redacted = {};

    for (const [key, value] of Object.entries(data)) {
      // Skip internal fields if not preserving structure
      if (!preserveStructure && key.startsWith('_')) {
        continue;
      }

      redacted[key] = redactValue(value, key, level);
    }

    return redacted;
  } catch (error) {
    console.error('[REDACT] Error redacting data:', error);
    return { error: 'Redaction failed', original: data };
  }
};

/**
 * Redact data for logging (maximum redaction)
 * @param {Object} data - Data to redact for logs
 * @returns {Object} Redacted data
 */
export const redactForLogging = (data) => {
  return redactSensitive(data, { level: 'audit', preserveStructure: false });
};

/**
 * Redact data for API responses (medium redaction)
 * @param {Object} data - Data to redact for API
 * @returns {Object} Redacted data
 */
export const redactForAPI = (data) => {
  return redactSensitive(data, { level: 'medium', preserveStructure: true });
};

/**
 * Redact data for debugging (low redaction)
 * @param {Object} data - Data to redact for debugging
 * @returns {Object} Redacted data
 */
export const redactForDebug = (data) => {
  return redactSensitive(data, { level: 'low', preserveStructure: true });
};

/**
 * Redact data for audit trails (high redaction)
 * @param {Object} data - Data to redact for audit
 * @returns {Object} Redacted data
 */
export const redactForAudit = (data) => {
  return redactSensitive(data, { level: 'audit', preserveStructure: false });
};

// ============================================================================
// SPECIFIC REDACTION FUNCTIONS
// ============================================================================

/**
 * Redact user data
 * @param {Object} user - User object
 * @returns {Object} Redacted user
 */
export const redactUser = (user) => {
  if (!user) return user;

  const redacted = { ...user };

  // Always redact these fields
  redacted.password = '[REDACTED]';
  redacted.passwordHash = '[REDACTED]';
  redacted.twoFactorSecret = '[REDACTED]';
  redacted.resetToken = '[REDACTED]';
  redacted.verificationToken = '[REDACTED]';

  // Partially redact email
  if (redacted.email) {
    redacted.email = maskEmail(redacted.email);
  }

  // Partially redact phone
  if (redacted.phone) {
    redacted.phone = maskPhone(redacted.phone);
  }

  // Partially redact names
  if (redacted.firstName) {
    redacted.firstName = maskString(redacted.firstName, 1);
  }

  if (redacted.lastName) {
    redacted.lastName = maskString(redacted.lastName, 1);
  }

  return redacted;
};

/**
 * Redact transaction data
 * @param {Object} transaction - Transaction object
 * @returns {Object} Redacted transaction
 */
export const redactTransaction = (transaction) => {
  if (!transaction) return transaction;

  const redacted = { ...transaction };

  // Partially redact account numbers
  if (redacted.sourceAccount) {
    redacted.sourceAccount = maskString(redacted.sourceAccount, 4);
  }

  if (redacted.destinationAccount) {
    redacted.destinationAccount = maskString(redacted.destinationAccount, 4);
  }

  // Amount is safe to show
  // Reference numbers can be partially shown
  if (redacted.reference) {
    redacted.reference = maskString(redacted.reference, 6);
  }

  return redacted;
};

/**
 * Redact document data
 * @param {Object} document - Document object
 * @returns {Object} Redacted document
 */
export const redactDocument = (document) => {
  if (!document) return document;

  const redacted = { ...document };

  // Redact content if sensitive
  if (redacted.content && redacted.sensitive) {
    redacted.content = '[REDACTED CONTENT]';
  }

  // Redact metadata
  if (redacted.metadata) {
    redacted.metadata = redactSensitive(redacted.metadata, { level: 'medium' });
  }

  return redacted;
};

// ============================================================================
// STRING-BASED REDACTION
// ============================================================================

/**
 * Redact sensitive patterns from a string
 * @param {string} text - Text to redact
 * @param {string} level - Redaction level
 * @returns {string} Redacted text
 */
export const redactText = (text, level = REDACTION_CONFIG.defaultLevel) => {
  if (!text || typeof text !== 'string') return text;

  let redacted = text;
  const config = REDACTION_CONFIG.levels[level] || REDACTION_CONFIG.levels.medium;

  for (const [type, pattern] of Object.entries(REDACTION_CONFIG.sensitivePatterns)) {
    redacted = redacted.replace(pattern, (match) => {
      return maskString(match, config.maskLength);
    });
  }

  return redacted;
};

// ============================================================================
// HEADER REDACTION
// ============================================================================

/**
 * Redact sensitive headers
 * @param {Object} headers - HTTP headers
 * @returns {Object} Redacted headers
 */
export const redactHeaders = (headers) => {
  if (!headers) return headers;

  const redacted = { ...headers };
  const sensitiveHeaders = [
    'authorization',
    'cookie',
    'set-cookie',
    'x-api-key',
    'x-auth-token',
    'x-csrf-token',
    'x-session-id'
  ];

  for (const header of sensitiveHeaders) {
    if (redacted[header]) {
      redacted[header] = '[REDACTED]';
    }
    if (redacted[header.toLowerCase()]) {
      redacted[header.toLowerCase()] = '[REDACTED]';
    }
  }

  return redacted;
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get redaction configuration
 * @returns {Object} Redaction config
 */
export const getRedactionConfig = () => {
  return {
    levels: REDACTION_CONFIG.levels,
    defaultLevel: REDACTION_CONFIG.defaultLevel,
    sensitiveFields: [...REDACTION_CONFIG.sensitiveFields],
    partialFields: [...REDACTION_CONFIG.partialFields],
    safeFields: [...REDACTION_CONFIG.safeFields]
  };
};

/**
 * Add custom sensitive field
 * @param {string} fieldName - Field name to add
 */
export const addSensitiveField = (fieldName) => {
  if (!REDACTION_CONFIG.sensitiveFields.includes(fieldName)) {
    REDACTION_CONFIG.sensitiveFields.push(fieldName);
  }
};

/**
 * Add custom partial field
 * @param {string} fieldName - Field name to add
 */
export const addPartialField = (fieldName) => {
  if (!REDACTION_CONFIG.partialFields.includes(fieldName)) {
    REDACTION_CONFIG.partialFields.push(fieldName);
  }
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  redactSensitive,
  redactForLogging,
  redactForAPI,
  redactForDebug,
  redactForAudit,
  redactUser,
  redactTransaction,
  redactDocument,
  redactText,
  redactHeaders,
  getRedactionConfig,
  addSensitiveField,
  addPartialField,
  maskEmail,
  maskPhone,
  maskString,
  REDACTION_CONFIG
};
