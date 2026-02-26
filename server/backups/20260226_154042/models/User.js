/* eslint-disable */
/*
 * =================================================================================
 *  ██╗   ██╗███████╗███████╗██████╗      ███╗   ███╗ ██████╗ ██████╗ ███████╗██╗
 *  ██║   ██║██╔════╝██╔════╝██╔══██╗     ████╗ ████║██╔═══██╗██╔══██╗██╔════╝██║
 *  ██║   ██║███████╗█████╗  ██████╔╝     ██╔████╔██║██║   ██║██║  ██║█████╗  ██║
 *  ██║   ██║╚════██║██╔══╝  ██╔══██╗     ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  ██║
 *  ╚██████╔╝███████║███████╗██║  ██║     ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗███████╗
 *   ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝     ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝
 *
 *  ██╗  ██╗██╗   ██╗██╗     ███████╗███╗   ███╗███████╗███╗   ██╗████████╗██╗  ██╗
 *  ██║  ██║╚██╗ ██╔╝██║     ██╔════╝████╗ ████║██╔════╝████╗  ██║╚══██╔══╝██║  ██║
 *  ███████║ ╚████╔╝ ██║     █████╗  ██╔████╔██║█████╗  ██╔██╗ ██║   ██║   ███████║
 *  ██╔══██║  ╚██╔╝  ██║     ██╔══╝  ██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║   ██╔══██║
 *  ██║  ██║   ██║   ███████╗███████╗██║ ╚═╝ ██║███████╗██║ ╚████║   ██║   ██║  ██║
 *  ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚══════╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝
 * =================================================================================
 * WILSY OS QUANTUM USER MODEL V25.0 - HYPER-SECURE MULTI-TENANT IDENTITY COLOSSUS
 * =================================================================================
 *
 * FILE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/User.js
 * CHIEF ARCHITECT: Wilson Khanyezi (wilsy.wk@gmail.com, +27 69 046 5710)
 * VERSION: 25.0.0 (ES Module)
 * STATUS: PRODUCTION-READY | LEGALLY CERTIFIED | HYPER-SECURE | PAN-AFRICAN READY
 * ES MODULE CONVERSION: 2026-02-25 - Converted from CommonJS to ES Module
 * =================================================================================
 */

import mongoose from "mongoose";
import bcrypt from 'bcrypt.js';
import crypto from "crypto";
import validator from 'validator.js';
import dotenv from 'dotenv.js';

dotenv.config();

// =================================================================================
// QUANTUM ENVIRONMENT VALIDATION V25.0
// =================================================================================
const validateUserEnvironment = () => {
  const requiredVars = [
    'JWT_SECRET',
    'USER_ENCRYPTION_KEY',
    'PASSWORD_HASH_SALT_ROUNDS',
    'BIOMETRIC_ENCRYPTION_KEY',
    'BIOMETRIC_ENCRYPTION_IV',
    'WEBAUTHN_RP_ID',
    'REDIS_URL',
    'AUDIT_ENCRYPTION_KEY',
  ];

  const missingVars = requiredVars.filter((varName) => !process.env[varName]);

  if (missingVars.length > 0) {
    console.error(
      `[User Model] CRITICAL: Missing environment variables: ${missingVars.join(', ')}`
    );

    if (process.env.NODE_ENV === 'development') {
      console.warn(
        '[User Model] Development mode: Using fallback values. THIS IS INSECURE FOR PRODUCTION!'
      );

      if (!process.env.USER_ENCRYPTION_KEY) {
        process.env.USER_ENCRYPTION_KEY = crypto.randomBytes(32).toString('hex');
      }
      if (!process.env.PASSWORD_HASH_SALT_ROUNDS) {
        process.env.PASSWORD_HASH_SALT_ROUNDS = '12';
      }
    } else {
      throw new Error(
        `CRITICAL: Missing user security environment variables: ${missingVars.join(', ')}`
      );
    }
  }

  if (process.env.USER_ENCRYPTION_KEY) {
    const keyBuffer = Buffer.from(process.env.USER_ENCRYPTION_KEY, 'hex');
    if (keyBuffer.length !== 32) {
      throw new Error('USER_ENCRYPTION_KEY must be 64-character hex string (32 bytes) for AES-256');
    }
  }

  if (process.env.BIOMETRIC_ENCRYPTION_KEY) {
    const keyBuffer = Buffer.from(process.env.BIOMETRIC_ENCRYPTION_KEY, 'hex');
    if (keyBuffer.length !== 32) {
      throw new Error('BIOMETRIC_ENCRYPTION_KEY must be 64-character hex string (32 bytes)');
    }
  }

  console.log('[User Model] ✅ Environment validated successfully with biometric integration');
};

validateUserEnvironment();

// =================================================================================
// QUANTUM ENCRYPTION SERVICE V25.0 - AES-256-GCM WITH KEY ROTATION
// =================================================================================
class UserEncryptionService {
  constructor() {
    this.algorithm = 'aes-256-gcm';
    this.key = Buffer.from(process.env.USER_ENCRYPTION_KEY, 'hex');
    this.ivLength = 16;
    this.authTagLength = 16;
    this.keyVersion = 'v1';
  }

  encrypt(text) {
    try {
      const iv = crypto.randomBytes(this.ivLength);
      const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);

      let encrypted = cipher.update(text, 'utf8', 'hex');
      encrypted += cipher.final('hex');

      const authTag = cipher.getAuthTag();

      return {
        encrypted,
        iv: iv.toString('hex'),
        tag: authTag.toString('hex'),
        algorithm: this.algorithm,
        keyVersion: this.keyVersion,
        encryptedAt: new Date().toISOString(),
      };
    } catch (error) {
      console.error('[User Encryption] Encryption failed:', error);
      throw new Error('User data encryption failed');
    }
  }

  decrypt(encryptedObj) {
    try {
      if (!encryptedObj || !encryptedObj.encrypted) {
        return encryptedObj;
      }

      const algorithm = encryptedObj.algorithm || this.algorithm;
      const iv = Buffer.from(encryptedObj.iv, 'hex');
      const authTag = Buffer.from(encryptedObj.tag, 'hex');

      let key = this.key;
      if (encryptedObj.keyVersion === 'v2' && process.env.USER_ENCRYPTION_KEY_V2) {
        key = Buffer.from(process.env.USER_ENCRYPTION_KEY_V2, 'hex');
      }

      const decipher = crypto.createDecipheriv(algorithm, key, iv);
      decipher.setAuthTag(authTag);

      let decrypted = decipher.update(encryptedObj.encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');

      return decrypted;
    } catch (error) {
      console.error('[User Encryption] Decryption failed:', error);
      throw new Error('User data decryption failed - Possible tampering detected');
    }
  }

  hashForIndex(data) {
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  encryptField(value) {
    if (!value || typeof value !== 'string') return value;
    const encrypted = this.encrypt(value);
    return JSON.stringify(encrypted);
  }

  decryptField(value) {
    if (!value) return null;
    try {
      const encryptedObj = JSON.parse(value);
      return this.decrypt(encryptedObj);
    } catch (error) {
      return value;
    }
  }
}

const userEncryption = new UserEncryptionService();

// =================================================================================
// QUANTUM USER SCHEMA V25.0 - HYPER-ENHANCED MULTI-TENANT IDENTITY
// =================================================================================
const UserSchema = new mongoose.Schema(
  {
    email: {
      type: String,
      required: [true, 'Email is required for legal communications under ECT Act'],
      unique: true,
      lowercase: true,
      trim: true,
      validate: {
        validator: function (v) {
          const email = v || this.get('email');
          return validator.isEmail(email);
        },
        message: 'Please provide a valid email address (POPIA Section 1: Personal Information)',
      },
      index: true,
      set: function (v) {
        if (!v) return v;
        const normalized = validator.normalizeEmail(v, {
          gmail_remove_dots: false,
          gmail_remove_subaddress: false,
        });
        return userEncryption.encryptField(normalized);
      },
      get: function (v) {
        return userEncryption.decryptField(v);
      },
    },

    firstName: {
      type: String,
      required: [true, 'First name is required for legal identification under FICA'],
      trim: true,
      minlength: [2, 'First name must be at least 2 characters'],
      maxlength: [50, 'First name cannot exceed 50 characters'],
      validate: {
        validator: function (v) {
          return /^[A-Za-zÀ-ÿ\s'-]+$/.test(v);
        },
        message: 'First name contains invalid characters',
      },
      set: function (v) {
        if (!v) return v;
        return userEncryption.encryptField(v.trim());
      },
      get: function (v) {
        return userEncryption.decryptField(v);
      },
    },

    lastName: {
      type: String,
      required: [true, 'Last name is required for legal identification under FICA'],
      trim: true,
      minlength: [2, 'Last name must be at least 2 characters'],
      maxlength: [50, 'Last name cannot exceed 50 characters'],
      set: function (v) {
        if (!v) return v;
        return userEncryption.encryptField(v.trim());
      },
      get: function (v) {
        return userEncryption.decryptField(v);
      },
    },

    phoneNumber: {
      type: String,
      validate: {
        validator: function (v) {
          const phone = v || this.get('phoneNumber');
          return /^(\+27|0)[1-9]\d{8}$/.test(phone?.replace(/\s/g, ''));
        },
        message: 'Please provide a valid South African phone number',
      },
      set: function (v) {
        if (!v) return v;
        return userEncryption.encryptField(v.replace(/\s/g, ''));
      },
      get: function (v) {
        return userEncryption.decryptField(v);
      },
    },

    idNumber: {
      type: String,
      validate: {
        validator: function (v) {
          if (!/^\d{13}$/.test(v)) return false;
          const month = parseInt(v.substring(2, 4));
          const day = parseInt(v.substring(4, 6));
          if (month < 1 || month > 12 || day < 1 || day > 31) return false;
          return true;
        },
        message: 'Invalid South African ID number format',
      },
      set: function (v) {
        if (!v) return v;
        return userEncryption.encryptField(v);
      },
      get: function (v) {
        return userEncryption.decryptField(v);
      },
    },

    tenantId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Tenant',
      required: [true, 'Tenant ID is required for multi-tenant data sovereignty'],
      index: true,
      validate: {
        validator: function (v) {
          return mongoose.Types.ObjectId.isValid(v);
        },
        message: 'Invalid tenant ID format',
      },
    },

    legalFirmId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'LegalFirm',
      required: [true, 'Legal firm association is required for LPC compliance'],
      index: true,
    },

    role: {
      type: String,
      enum: [
        'SUPER_ADMIN',
        'SYSTEM_ADMIN',
        'FIRM_OWNER',
        'MANAGING_PARTNER',
        'SENIOR_PARTNER',
        'PARTNER',
        'SALARIED_PARTNER',
        'ASSOCIATE',
        'LEGAL_PRACTITIONER',
        'CANDIDATE_ATTORNEY',
        'PARALEGAL',
        'CLIENT',
        'AUDITOR',
        'COMPLIANCE_OFFICER',
        'SUPPORT_STAFF',
      ],
      default: 'LEGAL_PRACTITIONER',
      required: true,
      index: true,
    },

    permissions: {
      type: Map,
      of: [String],
      default: new Map(),
    },

    biometric: {
      registered: {
        type: Boolean,
        default: false,
        index: true,
      },
      registrationDate: {
        type: Date,
        index: true,
        validate: {
          validator: function (v) {
            return !v || v <= new Date();
          },
          message: 'Registration date cannot be in the future',
        },
      },
      type: {
        type: String,
        enum: ['WEBAUTHN', 'FINGERPRINT', 'FACIAL', 'IRIS', 'BEHAVIORAL', 'MULTI_MODAL', 'NONE'],
        default: 'NONE',
      },
      lastUsed: {
        type: Date,
        index: true,
      },
      status: {
        type: String,
        enum: ['ACTIVE', 'SUSPENDED', 'REVOKED', 'EXPIRED', 'PENDING_REVIEW', 'LOCKED'],
        default: 'PENDING_REVIEW',
        index: true,
      },
      consentId: {
        type: String,
        index: true,
        validate: {
          validator: function (v) {
            return !v || v.startsWith('BIOMETRIC_CONSENT_');
          },
          message: 'Invalid consent ID format',
        },
      },
      security: {
        maxFailedAttempts: {
          type: Number,
          default: parseInt(process.env.BIOMETRIC_MAX_FAILED_ATTEMPTS) || 5,
          min: 3,
          max: 10,
        },
        lockoutDuration: {
          type: Number,
          default: parseInt(process.env.BIOMETRIC_LOCKOUT_DURATION) || 900,
          min: 300,
          max: 86400,
        },
        sessionTimeout: {
          type: Number,
          default: parseInt(process.env.BIOMETRIC_SESSION_TIMEOUT) || 3600,
          min: 300,
          max: 86400,
        },
        lastSecurityReview: Date,
        nextSecurityReview: {
          type: Date,
          default: function () {
            const next = new Date();
            next.setDate(next.getDate() + 90);
            return next;
          },
        },
        encryptionKeyVersion: {
          type: String,
          default: 'v1',
        },
      },
      statistics: {
        totalAuthentications: {
          type: Number,
          default: 0,
          min: 0,
        },
        successfulAuthentications: {
          type: Number,
          default: 0,
          min: 0,
        },
        failedAuthentications: {
          type: Number,
          default: 0,
          min: 0,
        },
        averageAuthTime: {
          type: Number,
          default: 0,
          min: 0,
        },
        lastSuccessfulAuth: Date,
        lastFailedAuth: Date,
        consecutiveFailures: {
          type: Number,
          default: 0,
          min: 0,
        },
      },
      registeredDevices: {
        type: Number,
        default: 0,
        min: 0,
        max: parseInt(process.env.MAX_BIOMETRIC_DEVICES) || 5,
      },
      compliance: {
        popiaConsentGiven: {
          type: Boolean,
          default: false,
        },
        popiaConsentDate: Date,
        popiaConsentVersion: {
          type: String,
          default: '2.0',
        },
        informationOfficerApproved: {
          type: Boolean,
          default: false,
        },
        approvalDate: Date,
        approvedBy: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'User',
        },
        dataProcessingRegistered: {
          type: Boolean,
          default: false,
        },
        ectActCompliant: {
          type: Boolean,
          default: false,
        },
        cybercrimesActCompliant: {
          type: Boolean,
          default: false,
        },
      },
      auditTrail: [
        {
          action: String,
          timestamp: Date,
          deviceId: String,
          ipAddress: String,
          location: String,
          success: Boolean,
        },
      ],
    },

    consent: {
      biometric: {
        granted: {
          type: Boolean,
          default: false,
          index: true,
        },
        grantedAt: {
          type: Date,
          validate: {
            validator: function (v) {
              return !v || v <= new Date();
            },
          },
        },
        consentId: {
          type: String,
          index: true,
        },
        revokedAt: Date,
        revocationReason: {
          type: String,
          enum: [
            'USER_REQUEST',
            'COMPLIANCE_REQUIREMENT',
            'SECURITY_INCIDENT',
            'SYSTEM_POLICY',
            'EXPIRED',
          ],
        },
        termsVersion: String,
        ipAddress: String,
        userAgent: String,
      },
      dataProcessing: {
        granted: {
          type: Boolean,
          default: false,
        },
        grantedAt: Date,
        purposes: [
          {
            type: String,
            enum: [
              'AUTHENTICATION',
              'DOCUMENT_SIGNING',
              'CLIENT_COMMUNICATION',
              'BILLING',
              'COMPLIANCE_REPORTING',
              'LEGAL_PROCESSING',
              'MARKETING',
              'RESEARCH',
              'SYSTEM_IMPROVEMENT',
            ],
          },
        ],
        expiryDate: Date,
        lawfulBasis: {
          type: String,
          enum: [
            'CONSENT',
            'CONTRACT',
            'LEGAL_OBLIGATION',
            'VITAL_INTERESTS',
            'PUBLIC_TASK',
            'LEGITIMATE_INTEREST',
          ],
          default: 'CONSENT',
        },
      },
      marketing: {
        granted: Boolean,
        grantedAt: Date,
        channels: [
          {
            type: String,
            enum: ['EMAIL', 'SMS', 'PUSH_NOTIFICATION', 'PHONE', 'POSTAL'],
          },
        ],
        preferences: {
          frequency: {
            type: String,
            enum: ['WEEKLY', 'MONTHLY', 'QUARTERLY', 'NEVER'],
            default: 'MONTHLY',
          },
          categories: [String],
        },
      },
      thirdPartySharing: {
        granted: Boolean,
        companies: [
          {
            name: String,
            purpose: String,
            grantedAt: Date,
            expiryDate: Date,
          },
        ],
      },
    },

    password: {
      type: String,
      required: [true, 'Password is required for account security'],
      minlength: [12, 'Password must be at least 12 characters (Cybersecurity Best Practice)'],
      select: false,
      validate: {
        validator: function (v) {
          const hasUpper = /[A-Z]/.test(v);
          const hasLower = /[a-z]/.test(v);
          const hasDigit = /\d/.test(v);
          const hasSpecial = /[@$!%*?&#]/.test(v);
          const noSpaces = !/\s/.test(v);
          const noSequential = !/(.)\1{2,}/.test(v);
          const noCommon = !/(password|123456|qwerty|admin|letmein|welcome|monkey)/i.test(v);
          const noPersonalInfo =
            !new RegExp(this.firstName || '', 'i').test(v) &&
            !new RegExp(this.lastName || '', 'i').test(v);

          return (
            hasUpper &&
            hasLower &&
            hasDigit &&
            hasSpecial &&
            noSpaces &&
            noSequential &&
            noCommon &&
            noPersonalInfo &&
            v.length >= 12
          );
        },
        message:
          'Password must contain: uppercase, lowercase, number, special character, no spaces/repeats/common patterns/personal info',
      },
    },

    passwordHistory: [
      {
        hash: String,
        changedAt: Date,
        usedBefore: Boolean,
      },
    ],

    passwordChangedAt: {
      type: Date,
      select: false,
    },

    passwordExpiresAt: {
      type: Date,
      default: function () {
        const expires = new Date();
        expires.setDate(expires.getDate() + 90);
        return expires;
      },
    },

    passwordResetToken: {
      type: String,
      select: false,
    },

    passwordResetExpires: {
      type: Date,
      select: false,
    },

    mfa: {
      enabled: {
        type: Boolean,
        default: true,
      },
      methods: {
        totp: {
          enabled: Boolean,
          secret: {
            type: String,
            select: false,
          },
          verifiedAt: Date,
          backupCodes: [
            {
              code: String,
              used: Boolean,
              usedAt: Date,
            },
          ],
        },
        sms: {
          enabled: Boolean,
          phoneNumber: String,
          verifiedAt: Date,
          lastCodeSent: Date,
          codeAttempts: Number,
        },
        email: {
          enabled: Boolean,
          verifiedAt: Date,
          lastCodeSent: Date,
        },
        hardwareToken: {
          enabled: Boolean,
          tokenId: String,
          registeredAt: Date,
          lastUsed: Date,
        },
      },
      primaryMethod: {
        type: String,
        enum: ['TOTP', 'SMS', 'EMAIL', 'BIOMETRIC', 'HARDWARE_TOKEN'],
        default: 'TOTP',
      },
      lastVerifiedAt: Date,
      failureCount: {
        type: Number,
        default: 0,
        min: 0,
      },
      lockoutUntil: Date,
      recoveryEmail: String,
      recoveryPhone: String,
    },

    attorneyNumber: {
      type: String,
      unique: true,
      sparse: true,
      trim: true,
      uppercase: true,
      validate: {
        validator: function (v) {
          return /^[A-Z]\d{5}\/\d{4}$/.test(v);
        },
        message: 'Invalid attorney number format (expected: A12345/2020) - LPC Rule 3.5',
      },
      index: true,
      set: function (v) {
        if (!v) return v;
        return userEncryption.encryptField(v);
      },
      get: function (v) {
        return userEncryption.decryptField(v);
      },
    },

    lpcRegistrationDate: Date,
    lpcExpiryDate: Date,
    lpcStatus: {
      type: String,
      enum: ['ACTIVE', 'SUSPENDED', 'STRUCK_OFF', 'NON_PRACTISING', 'PENDING'],
      default: 'PENDING',
    },

    practiceAreas: [
      {
        type: String,
        enum: [
          'ADMINISTRATIVE_LAW',
          'ADR_MEDIATION',
          'BANKING_FINANCE',
          'COMMERCIAL_LAW',
          'CONSTITUTIONAL_LAW',
          'CONSTRUCTION_LAW',
          'CONSUMER_PROTECTION',
          'CORPORATE_LAW',
          'CRIMINAL_LAW',
          'EMPLOYMENT_LAW',
          'ENVIRONMENTAL_LAW',
          'FAMILY_LAW',
          'HEALTHCARE_LAW',
          'IMMIGRATION_LAW',
          'INSOLVENCY_LAW',
          'INSURANCE_LAW',
          'INTELLECTUAL_PROPERTY',
          'INTERNATIONAL_LAW',
          'LABOUR_LAW',
          'LITIGATION',
          'MARITIME_LAW',
          'MERGERS_ACQUISITIONS',
          'MINING_LAW',
          'PROPERTY_LAW',
          'TAX_LAW',
          'TELECOMS_LAW',
          'TRUSTS_ESTATES',
        ],
        index: true,
      },
    ],

    yearsOfPractice: {
      type: Number,
      min: [0, 'Years of practice cannot be negative'],
      max: [70, 'Maximum 70 years of practice'],
      default: 0,
    },

    specialization: String,
    qualifications: [
      {
        degree: String,
        institution: String,
        year: Number,
        verified: Boolean,
      },
    ],

    identityVerified: {
      type: Boolean,
      default: false,
      index: true,
    },

    identityVerificationLevel: {
      type: String,
      enum: ['NOT_VERIFIED', 'BASIC', 'ENHANCED', 'SUPERVISED', 'CERTIFIED'],
      default: 'NOT_VERIFIED',
      index: true,
    },

    identityVerificationDate: Date,
    identityVerifiedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },

    ficaVerified: {
      type: Boolean,
      default: false,
      index: true,
    },

    ficaVerificationDate: Date,
    ficaVerifiedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },

    ficaDocuments: [
      {
        documentType: {
          type: String,
          enum: [
            'ID_BOOK',
            'PASSPORT',
            'PROOF_OF_RESIDENCE',
            'COMPANY_REGISTRATION',
            'TAX_CERTIFICATE',
            'BANK_STATEMENT',
          ],
        },
        documentUrl: {
          type: String,
          set: function (v) {
            return userEncryption.encryptField(v);
          },
          get: function (v) {
            return userEncryption.decryptField(v);
          },
        },
        verifiedAt: Date,
        verifiedBy: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'User',
        },
        expiresAt: Date,
        status: {
          type: String,
          enum: ['PENDING', 'APPROVED', 'REJECTED', 'EXPIRED'],
          default: 'PENDING',
        },
        rejectionReason: String,
      },
    ],

    amlRiskRating: {
      type: String,
      enum: ['LOW', 'MEDIUM', 'HIGH', 'PROHIBITED'],
      default: 'MEDIUM',
      index: true,
    },

    pepStatus: {
      type: Boolean,
      default: false,
      index: true,
    },

    sessions: [
      {
        sessionId: {
          type: String,
          required: true,
          index: true,
        },
        authMethod: {
          type: String,
          enum: ['PASSWORD', 'BIOMETRIC', 'MFA', 'SSO', 'API_KEY'],
          required: true,
        },
        deviceInfo: {
          userAgent: String,
          ipAddress: {
            type: String,
            set: function (v) {
              return userEncryption.encryptField(v);
            },
            get: function (v) {
              return userEncryption.decryptField(v);
            },
          },
          location: {
            country: String,
            city: String,
            coordinates: {
              lat: Number,
              lng: Number,
            },
          },
          deviceId: String,
          deviceType: String,
          os: String,
          browser: String,
          screenResolution: String,
        },
        biometricEvidenceId: {
          type: String,
          index: true,
        },
        issuedAt: {
          type: Date,
          default: Date.now,
        },
        expiresAt: Date,
        lastActivity: {
          type: Date,
          default: Date.now,
        },
        active: {
          type: Boolean,
          default: true,
        },
        metadata: mongoose.Schema.Types.Mixed,
        auditTrail: [
          {
            action: String,
            timestamp: Date,
            resource: String,
            success: Boolean,
          },
        ],
      },
    ],

    currentSessionId: {
      type: String,
      index: true,
    },

    maxConcurrentSessions: {
      type: Number,
      default: parseInt(process.env.MAX_CONCURRENT_SESSIONS) || 5,
      min: 1,
      max: 10,
    },

    lastLoginAt: {
      type: Date,
      index: true,
    },

    lastActivityAt: {
      type: Date,
      default: Date.now,
      index: true,
    },

    lastPasswordChange: Date,
    lastMfaSetup: Date,
    lastBiometricUse: Date,

    loginCount: {
      type: Number,
      default: 0,
      min: 0,
    },

    failedLoginAttempts: {
      type: Number,
      default: 0,
      select: false,
    },

    accountLockedUntil: {
      type: Date,
      select: false,
    },

    suspiciousActivityDetected: {
      type: Boolean,
      default: false,
      index: true,
    },

    securityAlerts: [
      {
        type: {
          type: String,
          enum: [
            'LOGIN_ATTEMPT',
            'PASSWORD_CHANGE',
            'BIOMETRIC_CHANGE',
            'LOCATION_CHANGE',
            'DEVICE_CHANGE',
          ],
        },
        detectedAt: Date,
        severity: {
          type: String,
          enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        },
        resolved: {
          type: Boolean,
          default: false,
        },
        resolvedAt: Date,
        resolvedBy: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'User',
        },
      },
    ],

    subscriptionId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Subscription',
      index: true,
    },

    billingInfo: {
      paymentMethod: {
        type: String,
        enum: ['CREDIT_CARD', 'DEBIT_ORDER', 'BANK_TRANSFER', 'EWALLET', 'NONE'],
      },
      billingAddress: {
        street: String,
        city: String,
        province: String,
        postalCode: String,
        country: {
          type: String,
          default: 'South Africa',
        },
      },
      vatNumber: String,
      taxExempt: {
        type: Boolean,
        default: false,
      },
    },

    status: {
      type: String,
      enum: ['ACTIVE', 'SUSPENDED', 'TERMINATED', 'ON_LEAVE', 'PENDING', 'LOCKED', 'ARCHIVED'],
      default: 'PENDING',
      index: true,
    },

    statusReason: String,
    statusChangedAt: Date,
    statusChangedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },

    metadata: {
      type: Map,
      of: mongoose.Schema.Types.Mixed,
      default: new Map(),
    },

    preferences: {
      language: {
        type: String,
        default: 'en',
        enum: ['en', 'af', 'zu', 'xh', 'nso', 'st', 'tn', 'ts', 'ss', 've'],
      },
      timezone: {
        type: String,
        default: 'Africa/Johannesburg',
      },
      dateFormat: {
        type: String,
        default: 'DD/MM/YYYY',
        enum: ['DD/MM/YYYY', 'MM/DD/YYYY', 'YYYY-MM-DD'],
      },
      notifications: {
        email: {
          type: Boolean,
          default: true,
        },
        push: {
          type: Boolean,
          default: true,
        },
        sms: {
          type: Boolean,
          default: false,
        },
      },
      accessibility: {
        highContrast: {
          type: Boolean,
          default: false,
        },
        fontSize: {
          type: String,
          enum: ['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE'],
          default: 'MEDIUM',
        },
        screenReader: {
          type: Boolean,
          default: false,
        },
      },
    },

    auditLog: [
      {
        action: {
          type: String,
          required: true,
          enum: [
            'CREATED',
            'UPDATED',
            'DELETED',
            'LOGIN',
            'LOGOUT',
            'PASSWORD_CHANGED',
            'MFA_ENABLED',
            'BIOMETRIC_REGISTERED',
            'ROLE_CHANGED',
            'STATUS_CHANGED',
            'CONSENT_CHANGED',
            'DOCUMENT_ACCESSED',
            'PAYMENT_MADE',
            'SUBSCRIPTION_CHANGED',
          ],
        },
        timestamp: {
          type: Date,
          default: Date.now,
        },
        performedBy: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'User',
        },
        ipAddress: String,
        userAgent: String,
        changes: mongoose.Schema.Types.Mixed,
        resourceId: mongoose.Schema.Types.ObjectId,
        resourceType: String,
        severity: {
          type: String,
          enum: ['INFO', 'WARNING', 'ERROR', 'CRITICAL'],
          default: 'INFO',
        },
      },
    ],

    createdBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },

    updatedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },

    isDeleted: {
      type: Boolean,
      default: false,
      index: true,
    },

    deletedAt: Date,
    deletedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },

    deletionReason: String,

    version: {
      type: Number,
      default: 1,
    },

    migratedFrom: {
      type: mongoose.Schema.Types.Mixed,
    },
  },
  {
    timestamps: true,
    toJSON: {
      virtuals: true,
      transform: function (doc, ret) {
        delete ret.password;
        delete ret.passwordHistory;
        delete ret.passwordResetToken;
        delete ret.passwordResetExpires;
        delete ret.failedLoginAttempts;
        delete ret.accountLockedUntil;
        delete ret.__v;
        delete ret.mfa?.methods?.totp?.secret;
        delete ret.mfa?.methods?.backupCodes;
        delete ret.sessions;
        delete ret.auditLog;
        delete ret.isDeleted;
        delete ret.deletedAt;
        delete ret.deletedBy;
        delete ret.version;

        if (ret.email) {
          const email = ret.email;
          const [local, domain] = email.split('@');
          if (local && domain) {
            ret.email = `${local.charAt(0)}*@${domain}`;
          }
        }

        if (ret.phoneNumber) {
          const phone = ret.phoneNumber || '';
          ret.phoneNumber = phone.replace(/(\d{3})\d{4}(\d{3})/, '$1*$2');
        }

        if (ret.idNumber) {
          ret.idNumber = '*-*-*';
        }

        ret.fullName = doc.fullName;
        ret.displayRole = doc.displayRole;
        ret.biometricSummary = doc.biometricSummary;
        ret.accountAge = doc.accountAge;
        ret.requiresReauthentication = doc.requiresReauthentication;

        if (doc.subscriptionId && doc.populated('subscriptionId')) {
          ret.subscription = {
            status: doc.subscriptionId.status,
            planType: doc.subscriptionId.planType,
            features: doc.subscriptionId.features,
          };
        }

        return ret;
      },
    },
    toObject: {
      virtuals: true,
    },
    minimize: false,
    collection: 'users',
    strict: 'throw',
    optimisticConcurrency: true,
  }
);

// =================================================================================
// QUANTUM INDEXES V25.0
// =================================================================================
UserSchema.index({ email: 1, tenantId: 1 }, { unique: true });
UserSchema.index({ attorneyNumber: 1 }, { sparse: true, unique: true });
UserSchema.index({ 'metadata.searchableName': 1 });
UserSchema.index({ tenantId: 1, legalFirmId: 1, role: 1, status: 1 });
UserSchema.index({ tenantId: 1, lastActivityAt: -1 });
UserSchema.index({ legalFirmId: 1, status: 1, role: 1 });
UserSchema.index({ 'biometric.registered': 1, 'biometric.status': 1, status: 1 });
UserSchema.index({ 'biometric.registrationDate': -1 });
UserSchema.index({ 'consent.biometric.granted': 1, status: 1 });
UserSchema.index({ identityVerified: 1, ficaVerified: 1 });
UserSchema.index({ amlRiskRating: 1, pepStatus: 1 });
UserSchema.index({ 'sessions.sessionId': 1 });
UserSchema.index({ 'sessions.active': 1, 'sessions.expiresAt': 1 });
UserSchema.index({ lastLoginAt: -1 });
UserSchema.index({ suspiciousActivityDetected: 1, status: 1 });
UserSchema.index({ subscriptionId: 1, status: 1 });
UserSchema.index({ 'billingInfo.vatNumber': 1 });
UserSchema.index(
  {
    firstName: 'text',
    lastName: 'text',
    email: 'text',
    practiceAreas: 'text',
    attorneyNumber: 'text',
  },
  {
    weights: {
      firstName: 10,
      lastName: 10,
      email: 5,
      attorneyNumber: 8,
      practiceAreas: 3,
    },
    name: 'user_search_index',
    default_language: 'english',
  }
);
UserSchema.index(
  { deletedAt: 1 },
  {
    expireAfterSeconds: 0,
    partialFilterExpression: { isDeleted: true },
  }
);
UserSchema.index(
  { 'sessions.expiresAt': 1 },
  {
    expireAfterSeconds: 0,
    partialFilterExpression: { 'sessions.active': true },
  }
);

// =================================================================================
// QUANTUM VIRTUAL PROPERTIES V25.0
// =================================================================================
UserSchema.virtual('fullName').get(function () {
  const firstName = this.get('firstName') || '';
  const lastName = this.get('lastName') || '';
  return `${firstName} ${lastName}`.trim();
});

UserSchema.virtual('displayRole').get(function () {
  const roleMap = {
    SUPER_ADMIN: 'Sovereign Administrator',
    SYSTEM_ADMIN: 'System Administrator',
    FIRM_OWNER: 'Law Firm Owner',
    MANAGING_PARTNER: 'Managing Partner',
    SENIOR_PARTNER: 'Senior Partner',
    PARTNER: 'Partner',
    SALARIED_PARTNER: 'Salaried Partner',
    ASSOCIATE: 'Associate Attorney',
    LEGAL_PRACTITIONER: 'Legal Practitioner',
    CANDIDATE_ATTORNEY: 'Candidate Attorney',
    PARALEGAL: 'Paralegal',
    CLIENT: 'Client',
    AUDITOR: 'Auditor',
    COMPLIANCE_OFFICER: 'Compliance Officer',
    SUPPORT_STAFF: 'Support Staff',
  };
  return roleMap[this.role] || this.role;
});

UserSchema.virtual('biometricSummary').get(function () {
  return {
    enabled: this.biometric.registered,
    type: this.biometric.type,
    registrationDate: this.biometric.registrationDate,
    lastUsed: this.biometric.lastUsed,
    status: this.biometric.status,
    compliance: {
      popiaConsent: this.biometric.compliance.popiaConsentGiven,
      informationOfficerApproved: this.biometric.compliance.informationOfficerApproved,
      ectActCompliant: this.biometric.compliance.ectActCompliant,
    },
    statistics: this.biometric.statistics,
    registeredDevices: this.biometric.registeredDevices,
  };
});

UserSchema.virtual('accountAge').get(function () {
  if (!this.createdAt) return 0;
  const now = new Date();
  const created = new Date(this.createdAt);
  const diffTime = now - created;
  return Math.floor(diffTime / (1000 * 60 * 60 * 24));
});

UserSchema.virtual('requiresReauthentication').get(function () {
  if (!this.lastActivityAt) return true;
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  return this.lastActivityAt < thirtyDaysAgo;
});

UserSchema.virtual('isAccountLocked').get(function () {
  if (!this.accountLockedUntil) return false;
  return Date.now() < this.accountLockedUntil.getTime();
});

UserSchema.virtual('isPasswordExpired').get(function () {
  if (!this.passwordExpiresAt) return false;
  return new Date() > this.passwordExpiresAt;
});

UserSchema.virtual('daysUntilPasswordExpiry').get(function () {
  if (!this.passwordExpiresAt) return null;
  const now = new Date();
  const expiry = new Date(this.passwordExpiresAt);
  const diffTime = expiry - now;
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
});

UserSchema.virtual('activeSessionCount').get(function () {
  if (!this.sessions) return 0;
  return this.sessions.filter((session) => session.active && session.expiresAt > new Date()).length;
});

// =================================================================================
// QUANTUM MIDDLEWARE V25.0
// =================================================================================
UserSchema.pre('validate', function (next) {
  if (this.isModified('firstName') || this.isModified('lastName')) {
    const firstName = this.get('firstName') || '';
    const lastName = this.get('lastName') || '';
    this.metadata.set('fullName', `${firstName} ${lastName}`);
    this.metadata.set('searchableName', `${lastName}, ${firstName}`);
  }

  if (this.role && this.attorneyNumber) {
    const attorneyRoles = [
      'FIRM_OWNER',
      'MANAGING_PARTNER',
      'SENIOR_PARTNER',
      'PARTNER',
      'SALARIED_PARTNER',
      'ASSOCIATE',
      'LEGAL_PRACTITIONER',
      'CANDIDATE_ATTORNEY',
    ];

    if (attorneyRoles.includes(this.role) && !this.attorneyNumber) {
      this.invalidate('attorneyNumber', 'Attorney number required for legal practitioner roles');
    }
  }

  if (this.phoneNumber && !/^(\+27|0)[1-9]\d{8}$/.test(this.phoneNumber.replace(/\s/g, ''))) {
    this.invalidate('phoneNumber', 'Invalid South African phone number format');
  }

  next();
});

UserSchema.pre('save', async function (next) {
  if (this.isModified('password')) {
    try {
      const saltRounds = parseInt(process.env.PASSWORD_HASH_SALT_ROUNDS) || 12;
      const salt = await bcrypt.genSalt(saltRounds);
      const hash = await bcrypt.hash(this.password, salt);

      if (!this.passwordHistory) this.passwordHistory = [];
      this.passwordHistory.push({
        hash: hash,
        changedAt: new Date(),
        usedBefore: await this.checkPasswordHistory(this.password),
      });

      if (this.passwordHistory.length > 5) {
        this.passwordHistory = this.passwordHistory.slice(-5);
      }

      this.password = hash;
      this.passwordChangedAt = new Date();
      this.passwordExpiresAt = new Date(Date.now() + 90 * 24 * 60 * 60 * 1000);

      this.passwordResetToken = undefined;
      this.passwordResetExpires = undefined;
    } catch (error) {
      return next(new Error(`Password hashing failed: ${error.message}`));
    }
  }

  if (this.isModified('biometric.registered') || this.isNew) {
    try {
      const BiometricCredential = mongoose.model('BiometricCredential');
      const credentialCount = await BiometricCredential.countDocuments({
        userId: this._id,
        status: { $in: ['active', 'pending_activation'] },
      });

      if (credentialCount > 0 && !this.biometric.registered) {
        this.biometric.registered = true;
        this.biometric.registrationDate = new Date();
        this.biometric.registeredDevices = credentialCount;
      }
    } catch (error) {
      console.warn('[User Model] Could not sync biometric credentials:', error.message);
    }
  }

  this.version = (this.version || 0) + 1;

  next();
});

UserSchema.post('save', async function (doc) {
  try {
    const LegalFirm = mongoose.model('LegalFirm');
    await LegalFirm.findByIdAndUpdate(doc.legalFirmId, {
      $addToSet: { users: doc._id },
    });

    if (process.env.ENABLE_AUDIT_LOGGING === 'true') {
      try {
        const auditService = (await import('../services/auditService.js')).default;
        await auditService.log(null, {
          action: `USER_${doc.isNew ? 'CREATED' : 'UPDATED'}`,
          resourceType: 'USER',
          resourceId: doc._id,
          resourceLabel: `${doc.fullName} (${doc.email})`,
          metadata: {
            userId: doc._id,
            tenantId: doc.tenantId,
            legalFirmId: doc.legalFirmId,
            role: doc.role,
            status: doc.status,
          },
          severity: 'INFO',
        });
      } catch (auditError) {
        console.warn('[User Model] Audit logging failed:', auditError.message);
      }
    }
  } catch (error) {
    console.error('[User Model] Post-save operations failed:', error.message);
  }
});

UserSchema.pre('remove', async function (next) {
  this.status = 'TERMINATED';
  this.isDeleted = true;
  this.deletedAt = new Date();
  await this.save();
  next(new Error('Users cannot be hard deleted. Use termination status with soft delete.'));
});

// =================================================================================
// QUANTUM INSTANCE METHODS V25.0
// =================================================================================
UserSchema.methods.checkPassword = async function (candidatePassword) {
  if (!this.password) return false;
  return await bcrypt.compare(candidatePassword, this.password);
};

UserSchema.methods.checkPasswordHistory = async function (candidatePassword) {
  if (!this.passwordHistory || this.passwordHistory.length === 0) return false;

  for (const record of this.passwordHistory) {
    if (await bcrypt.compare(candidatePassword, record.hash)) {
      return true;
    }
  }

  return false;
};

UserSchema.methods.createPasswordResetToken = function () {
  const resetToken = crypto.randomBytes(32).toString('hex');

  this.passwordResetToken = crypto.createHash('sha256').update(resetToken).digest('hex');

  this.passwordResetExpires = new Date(Date.now() + 10 * 60 * 1000);

  return resetToken;
};

UserSchema.methods.lockAccount = function (durationMinutes = 15) {
  this.accountLockedUntil = new Date(Date.now() + durationMinutes * 60 * 1000);
  this.failedLoginAttempts = 0;
  this.suspiciousActivityDetected = true;

  this.securityAlerts.push({
    type: 'LOGIN_ATTEMPT',
    detectedAt: new Date(),
    severity: 'HIGH',
    resolved: false,
  });
};

UserSchema.methods.recordSuccessfulLogin = function (sessionData) {
  this.lastLoginAt = new Date();
  this.lastActivityAt = new Date();
  this.loginCount += 1;
  this.failedLoginAttempts = 0;
  this.suspiciousActivityDetected = false;

  if (sessionData) {
    if (!this.sessions) this.sessions = [];
    this.sessions.push(sessionData);

    if (this.sessions.length > this.maxConcurrentSessions) {
      this.sessions.sort((a, b) => a.issuedAt - b.issuedAt);
      this.sessions.shift();
    }
  }
};

UserSchema.methods.recordFailedLogin = function () {
  this.failedLoginAttempts += 1;
  this.lastActivityAt = new Date();

  const maxAttempts = parseInt(process.env.MAX_LOGIN_ATTEMPTS) || 5;
  if (this.failedLoginAttempts >= maxAttempts) {
    this.lockAccount();
  }
};

UserSchema.methods.hasPermission = function (permission) {
  if (this.role === 'SUPER_ADMIN') return true;

  const rolePermissions = this.permissions.get(this.role) || [];
  return rolePermissions.includes(permission) || rolePermissions.includes('*');
};

UserSchema.methods.getActiveSubscription = async function () {
  if (!this.subscriptionId) return null;

  try {
    const Subscription = mongoose.model('Subscription');
    const subscription = await Subscription.findOne({
      _id: this.subscriptionId,
      status: { $in: ['ACTIVE', 'TRIAL', 'GRACE_PERIOD'] },
    });

    return subscription;
  } catch (error) {
    console.error('[User Model] Failed to get subscription:', error.message);
    return null;
  }
};

// =================================================================================
// QUANTUM STATIC METHODS V25.0
// =================================================================================
UserSchema.statics.findActiveByLegalFirm = async function (legalFirmId, options = {}) {
  const {
    roles = [],
    includeInactive = false,
    limit = 100,
    skip = 0,
    sort = { lastName: 1, firstName: 1 },
  } = options;

  const query = {
    legalFirmId,
    isDeleted: false,
  };

  if (!includeInactive) {
    query.status = 'ACTIVE';
  }

  if (roles.length > 0) {
    query.role = { $in: roles };
  }

  return await this.find(query)
    .populate('subscriptionId', 'status planType features')
    .populate('createdBy', 'firstName lastName email')
    .sort(sort)
    .limit(limit)
    .skip(skip);
};

UserSchema.statics.getUserStatistics = async function (legalFirmId) {
  const stats = await this.aggregate([
    {
      $match: {
        legalFirmId: new mongoose.Types.ObjectId(legalFirmId),
        isDeleted: false,
      },
    },
    {
      $facet: {
        statusStats: [
          {
            $group: {
              _id: '$status',
              count: { $sum: 1 },
            },
          },
        ],
        roleStats: [
          {
            $group: {
              _id: '$role',
              count: { $sum: 1 },
              activeCount: {
                $sum: { $cond: [{ $eq: ['$status', 'ACTIVE'] }, 1, 0] },
              },
            },
          },
        ],
        biometricStats: [
          {
            $group: {
              _id: '$biometric.registered',
              count: { $sum: 1 },
              activeUsers: {
                $sum: { $cond: [{ $eq: ['$status', 'ACTIVE'] }, 1, 0] },
              },
            },
          },
        ],
        ficaStats: [
          {
            $group: {
              _id: '$ficaVerified',
              count: { $sum: 1 },
            },
          },
        ],
        monthlyGrowth: [
          {
            $group: {
              _id: {
                year: { $year: '$createdAt' },
                month: { $month: '$createdAt' },
              },
              newUsers: { $sum: 1 },
            },
          },
          { $sort: { '_id.year': 1, '_id.month': 1 } },
          { $limit: 12 },
        ],
      },
    },
  ]);

  return (
    stats[0] || {
      statusStats: [],
      roleStats: [],
      biometricStats: [],
      ficaStats: [],
      monthlyGrowth: [],
    }
  );
};

UserSchema.statics.findUsersNeedingAttention = async function (legalFirmId) {
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const passwordExpiryThreshold = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

  return await this.find({
    legalFirmId,
    isDeleted: false,
    $or: [
      { status: 'LOCKED' },
      { status: 'SUSPENDED' },
      { accountLockedUntil: { $gt: new Date() } },
      { passwordExpiresAt: { $lt: passwordExpiryThreshold } },
      { lastActivityAt: { $lt: thirtyDaysAgo }, status: 'ACTIVE' },
      { suspiciousActivityDetected: true },
    ],
  })
    .select(
      'firstName lastName email role status lastActivityAt passwordExpiresAt accountLockedUntil suspiciousActivityDetected'
    )
    .sort({ status: 1, lastActivityAt: 1 })
    .limit(50);
};

UserSchema.statics.searchUsers = async function (filters = {}) {
  const {
    legalFirmId,
    tenantId,
    searchTerm,
    roles = [],
    statuses = ['ACTIVE'],
    hasBiometric = null,
    ficaVerified = null,
    page = 1,
    limit = 20,
    sortBy = 'lastName',
    sortOrder = 'asc',
  } = filters;

  const query = {
    isDeleted: false,
  };

  if (legalFirmId) query.legalFirmId = legalFirmId;
  if (tenantId) query.tenantId = tenantId;
  if (roles.length > 0) query.role = { $in: roles };
  if (statuses.length > 0) query.status = { $in: statuses };

  if (hasBiometric !== null) {
    query['biometric.registered'] = hasBiometric;
  }

  if (ficaVerified !== null) {
    query.ficaVerified = ficaVerified;
  }

  if (searchTerm) {
    query.$text = { $search: searchTerm };
  }

  const sortOptions = {};
  sortOptions[sortBy] = sortOrder === 'asc' ? 1 : -1;

  const skip = (page - 1) * limit;

  const [users, total] = await Promise.all([
    this.find(query)
      .populate('subscriptionId', 'status planType')
      .sort(sortOptions)
      .skip(skip)
      .limit(limit),
    this.countDocuments(query),
  ]);

  return {
    users,
    pagination: {
      page,
      limit,
      total,
      pages: Math.ceil(total / limit),
      hasMore: page * limit < total,
    },
  };
};

// =================================================================================
// QUANTUM MODEL REGISTRATION (ES MODULE EXPORT)
// =================================================================================
const User = mongoose.models.User || mongoose.model('User', UserSchema);

export default User;