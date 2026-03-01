#!/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ REDACT SENSITIVE UTILITY - POPIA COMPLIANCE                               ║
  ║ Automatically redacts PII from logs and exports                          ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/redactSensitive.js
 * VERSION: 1.0.0-PRODUCTION
 * CREATED: 2026-03-01
 */

// ============================================================================
// REDACTION PATTERNS
// ============================================================================

export const REDACT_FIELDS = [
  'idNumber',
  'passportNumber',
  'driversLicense',
  'email',
  'phone',
  'cellphone',
  'mobile',
  'ipAddress',
  'userAgent',
  'biometricData',
  'signatureImage',
  'certificatePrivateKey',
  'authenticationData',
  'otp',
  'password',
  'token',
  'accessToken',
  'refreshToken',
  'apiKey',
  'secret',
  'privateKey',
  'creditCard',
  'bankAccount',
  'taxId',
];

const REDACTION_PATTERNS = [
  { pattern: /\b[\w\.-]+@[\w\.-]+\.\w+\b/g, replacement: '[EMAIL REDACTED]' },
  { pattern: /\b\d{13}\b/g, replacement: '[ID NUMBER REDACTED]' },
  { pattern: /\b(\+27|0)[1-9][0-9]{8}\b/g, replacement: '[PHONE REDACTED]' },
  { pattern: /\b\d{16}\b/g, replacement: '[CARD REDACTED]' },
  { pattern: /\b[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}\b/g, replacement: '[IBAN REDACTED]' },
  { pattern: /\b[0-9]{9,18}\b/g, replacement: '[ACCOUNT REDACTED]' },
];

// ============================================================================
// REDACTION FUNCTIONS
// ============================================================================

/**
 * Redact sensitive information from an object or string
 */
export const redactSensitive = (data, customFields = []) => {
  if (!data) return data;

  const fieldsToRedact = [...REDACT_FIELDS, ...customFields];

  // Handle primitive types
  if (typeof data !== 'object' || data === null) {
    return redactString(String(data));
  }

  // Handle arrays
  if (Array.isArray(data)) {
    return data.map((item) => redactSensitive(item, customFields));
  }

  // Handle objects
  const redacted = {};

  for (const [key, value] of Object.entries(data)) {
    // Check if this field should be redacted
    if (fieldsToRedact.some((field) => key.toLowerCase().includes(field.toLowerCase()))) {
      redacted[key] = '[REDACTED]';
    }
    // Recursively redact nested objects
    else if (value && typeof value === 'object') {
      redacted[key] = redactSensitive(value, customFields);
    }
    // Redact strings that match patterns
    else if (typeof value === 'string') {
      redacted[key] = redactString(value);
    }
    // Keep other values as is
    else {
      redacted[key] = value;
    }
  }

  return redacted;
};

/**
 * Redact sensitive patterns from a string
 */
export const redactString = (str) => {
  if (!str || typeof str !== 'string') return str;

  let redacted = str;

  for (const { pattern, replacement } of REDACTION_PATTERNS) {
    redacted = redacted.replace(pattern, replacement);
  }

  return redacted;
};

/**
 * Check if a value contains sensitive information
 */
export const containsSensitive = (value, fields = []) => {
  if (!value) return false;

  const allFields = [...REDACT_FIELDS, ...fields];
  const valueStr = JSON.stringify(value).toLowerCase();

  return allFields.some(
    (field) =>
      valueStr.includes(field.toLowerCase()) ||
      REDACTION_PATTERNS.some(({ pattern }) => pattern.test(valueStr))
  );
};

/**
 * Get all redaction patterns
 */
export const getRedactionPatterns = () => {
  return [...REDACTION_PATTERNS];
};

// ============================================================================
// EXPORTS - SINGLE EXPORT BLOCK
// ============================================================================

export default redactSensitive;
