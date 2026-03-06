#!/* eslint-disable */
/* ╔═══════════════════════════════════════════════════════════════════════════╗
  ║ VALIDATION MIDDLEWARE - INVESTOR-GRADE MODULE                             ║
  ║ Input validation | POPIA compliance | XSS prevention                     ║
  ╚═══════════════════════════════════════════════════════════════════════════╝ */

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/validation.js
 * VERSION: 1.0.0-PRODUCTION
 * CREATED: 2026-03-01
 */

import { body, validationResult } from 'express-validator';
import { redactSensitive } from '../utils/redactSensitive.js';
import logger from '../utils/logger.js';

// ============================================================================
// VALIDATION RULES
// ============================================================================

export const validateSignatureRequest = [
  body('documentId')
    .notEmpty()
    .withMessage('Document ID is required')
    .isString()
    .withMessage('Document ID must be a string')
    .trim()
    .escape(),

  body('signers')
    .isArray({ min: 1 })
    .withMessage('At least one signer is required')
    .custom((signers) => {
      for (const signer of signers) {
        if (!signer.email) {
          throw new Error('Each signer must have an email');
        }
        if (!signer.name) {
          throw new Error('Each signer must have a name');
        }
        // Basic email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(signer.email)) {
          throw new Error(`Invalid email format: ${signer.email}`);
        }
      }
      return true;
    }),

  body('options.signatureType')
    .optional()
    .isIn(['electronic', 'digital', 'advanced', 'qualified', 'biometric'])
    .withMessage('Invalid signature type'),

  body('options.provider')
    .optional()
    .isIn(['docusign', 'hellosign', 'adobe_sign', 'za_sign', 'custom'])
    .withMessage('Invalid signature provider'),

  body('options.verificationLevel')
    .optional()
    .isIn(['basic', 'standard', 'advanced', 'qualified'])
    .withMessage('Invalid verification level'),

  body('options.expiresAt').optional().isISO8601().withMessage('Invalid expiration date')
    .toDate(),

  // Handle validation errors
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      const redactedErrors = redactSensitive(errors.array(), ['email']);

      logger.warn('Validation failed', {
        path: req.path,
        errors: redactedErrors,
        correlationId: req.correlationId,
      });

      return res.status(422).json({
        error: 'Validation failed',
        code: 'VALIDATION_ERROR',
        details: redactedErrors,
        correlationId: req.correlationId,
      });
    }
    next();
  },
];

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const sanitizeInput = (input) => {
  if (typeof input === 'string') {
    return input.trim().replace(/[<>]/g, '');
  }
  return input;
};
