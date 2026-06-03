/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - MFA BACKUP CODE MODEL                                         ║
 * ║ [MULTI-FACTOR AUTHENTICATION | ACCOUNT RECOVERY | FORENSIC SECURITY]     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * @team Collaboration Notes:
 * - One-time use backup codes for MFA recovery
 * - Cryptographically secure random generation
 * - Automatic expiration and usage tracking
 * - Forensic audit trail for all backup code operations
 * - 101/10 security standard
 *
 * @last_updated: 2026-03-18
 * @lead_architect: Wilson Khanyezi
 */

import mongoose from 'mongoose';
import crypto from 'crypto';

const MFABackupCodeSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'User ID is required'],
    index: true
  },

  code: {
    type: String,
    required: [true, 'Backup code is required'],
    unique: true,
    uppercase: true,
    trim: true
  },

  // Hashed version for verification (stored for forensic audit)
  codeHash: {
    type: String,
    required: true
  },

  status: {
    type: String,
    enum: ['active', 'used', 'expired', 'revoked'],
    default: 'active',
    index: true
  },

  type: {
    type: String,
    enum: ['backup', 'recovery', 'emergency'],
    default: 'backup'
  },

  generatedAt: {
    type: Date,
    default: Date.now,
    index: true
  },

  expiresAt: {
    type: Date,
    default: () => new Date(Date.now() + 365 * 24 * 60 * 60 * 1000) // 1 year default
  },

  usedAt: {
    type: Date
  },

  usedBy: {
    type: String, // IP address or device info
  },

  revokedAt: {
    type: Date
  },

  revokedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },

  revokedReason: {
    type: String,
    enum: ['user_request', 'security_breach', 'admin_action', 'expired']
  },

  metadata: {
    generatedBy: {
      type: String,
      default: 'system'
    },
    generatedFromIP: String,
    generatedFromUA: String,
    deviceInfo: mongoose.Schema.Types.Mixed,
    notes: String
  },

  // Chain of custody for forensic audit
  chainOfCustody: [{
    action: {
      type: String,
      enum: ['generated', 'viewed', 'used', 'revoked', 'expired']
    },
    timestamp: {
      type: Date,
      default: Date.now
    },
    performedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    ipAddress: String,
    userAgent: String,
    reason: String,
    forensicHash: String
  }],

  // Cryptographic integrity
  forensicHash: {
    type: String,
    required: true
  },

  previousHash: {
    type: String
  },

  // Timestamps
  createdAt: {
    type: Date,
    default: Date.now,
    immutable: true
  },

  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      delete ret.codeHash;
      delete ret.__v;
      delete ret.chainOfCustody;
      ret.code = `••••••${ret.code.slice(-4)}`; // Mask code
      return ret;
    }
  }
});

// ============================================================================
// INDEXES
// ============================================================================

MFABackupCodeSchema.index({ userId: 1, status: 1 });
MFABackupCodeSchema.index({ code: 1 }, { unique: true });
MFABackupCodeSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });
MFABackupCodeSchema.index({ status: 1, expiresAt: 1 });

// ============================================================================
// MIDDLEWARE
// ============================================================================

/**
 * Generate cryptographic hashes before saving
 */
MFABackupCodeSchema.pre('save', async function(next) {
  try {
    // Update timestamp
    this.updatedAt = new Date();

    // Generate code if not provided
    if (!this.code) {
      this.code = this.generateBackupCode();
    }

    // Hash the code for secure storage
    if (this.isModified('code') || !this.codeHash) {
      const salt = crypto.randomBytes(16).toString('hex');
      const hash = crypto
        .createHash('sha256')
        .update(this.code + salt + (this.userId?.toString() || ''))
        .digest('hex');
      this.codeHash = `${salt}:${hash}`;
    }

    // Generate forensic hash for chain of custody
    const dataForHash = {
      userId: this.userId?.toString(),
      code: this.code,
      status: this.status,
      generatedAt: this.generatedAt,
      expiresAt: this.expiresAt,
      previousHash: this.previousHash || null
    };

    this.forensicHash = crypto
      .createHash('sha256')
      .update(JSON.stringify(dataForHash))
      .digest('hex');

    next();
  } catch (error) {
    next(error);
  }
});

// ============================================================================
// INSTANCE METHODS
// ============================================================================

/**
 * Generate a cryptographically secure backup code
 * @returns {string} 12-character alphanumeric code
 */
MFABackupCodeSchema.methods.generateBackupCode = function() {
  // Format: XXXX-XXXX-XXXX (12 characters total)
  const generateSegment = () => {
    return crypto.randomBytes(4).toString('hex').toUpperCase().substring(0, 4);
  };

  return `${generateSegment()}-${generateSegment()}-${generateSegment()}`;
};

/**
 * Verify a provided code against stored hash
 * @param {string} providedCode - Code to verify
 * @returns {boolean} True if code matches
 */
MFABackupCodeSchema.methods.verifyCode = function(providedCode) {
  if (!this.codeHash) return false;

  const [salt, storedHash] = this.codeHash.split(':');
  const hashToVerify = crypto
    .createHash('sha256')
    .update(providedCode + salt + (this.userId?.toString() || ''))
    .digest('hex');

  return hashToVerify === storedHash;
};

/**
 * Mark code as used
 * @param {Object} options - Usage options
 * @param {string} options.ipAddress - IP address where code was used
 * @param {string} options.userAgent - User agent of the device
 * @param {mongoose.Types.ObjectId} options.performedBy - User who performed action
 */
MFABackupCodeSchema.methods.markAsUsed = async function(options = {}) {
  this.status = 'used';
  this.usedAt = new Date();
  this.usedBy = options.ipAddress || 'unknown';

  // Add to chain of custody
  this.chainOfCustody.push({
    action: 'used',
    timestamp: new Date(),
    performedBy: options.performedBy || this.userId,
    ipAddress: options.ipAddress,
    userAgent: options.userAgent,
    forensicHash: crypto.randomBytes(16).toString('hex')
  });

  await this.save();
};

/**
 * Revoke a backup code
 * @param {Object} options - Revocation options
 */
MFABackupCodeSchema.methods.revoke = async function(options = {}) {
  this.status = 'revoked';
  this.revokedAt = new Date();
  this.revokedBy = options.revokedBy;
  this.revokedReason = options.reason || 'user_request';

  this.chainOfCustody.push({
    action: 'revoked',
    timestamp: new Date(),
    performedBy: options.revokedBy,
    ipAddress: options.ipAddress,
    reason: options.reason,
    forensicHash: crypto.randomBytes(16).toString('hex')
  });

  await this.save();
};

/**
 * Check if code is expired
 * @returns {boolean} True if expired
 */
MFABackupCodeSchema.methods.isExpired = function() {
  return this.expiresAt < new Date();
};

/**
 * Get masked code for display
 * @returns {string} Masked code (e.g., "••••-••••-ABC1")
 */
MFABackupCodeSchema.methods.getMaskedCode = function() {
  const parts = this.code.split('-');
  const lastSegment = parts[2] || '';
  return `••••-••••-${lastSegment}`;
};

// ============================================================================
// STATIC METHODS
// ============================================================================

/**
 * Generate a batch of backup codes for a user
 * @param {Object} options - Generation options
 * @param {mongoose.Types.ObjectId} options.userId - User ID
 * @param {number} options.count - Number of codes to generate
 * @param {Object} options.metadata - Additional metadata
 * @returns {Array} Generated backup code documents
 */
MFABackupCodeSchema.statics.generateBatch = async function(options = {}) {
  const {
    userId,
    count = 10,
    type = 'backup',
    expiresIn = 365 * 24 * 60 * 60 * 1000, // 1 year
    metadata = {}
  } = options;

  if (!userId) {
    throw new Error('User ID is required to generate backup codes');
  }

  const codes = [];
  const expiresAt = new Date(Date.now() + expiresIn);

  for (let i = 0; i < count; i++) {
    const backupCode = new this({
      userId,
      type,
      expiresAt,
      metadata: {
        ...metadata,
        generatedAt: new Date(),
        batchIndex: i + 1
      }
    });

    // Generate the code
    backupCode.code = backupCode.generateBackupCode();

    // Add to chain of custody
    backupCode.chainOfCustody.push({
      action: 'generated',
      timestamp: new Date(),
      performedBy: userId,
      ...metadata
    });

    await backupCode.save();
    codes.push(backupCode);
  }

  return codes;
};

/**
 * Verify and use a backup code
 * @param {Object} options - Verification options
 * @returns {Object} Result of verification
 */
MFABackupCodeSchema.statics.verifyAndUse = async function(options = {}) {
  const {
    userId,
    code,
    ipAddress,
    userAgent
  } = options;

  // Find active codes for this user
  const backupCode = await this.findOne({
    userId,
    status: 'active',
    expiresAt: { $gt: new Date() }
  });

  if (!backupCode) {
    return {
      valid: false,
      reason: 'No active backup codes found'
    };
  }

  // Verify the code
  if (!backupCode.verifyCode(code)) {
    return {
      valid: false,
      reason: 'Invalid backup code'
    };
  }

  // Mark as used
  await backupCode.markAsUsed({
    ipAddress,
    userAgent,
    performedBy: userId
  });

  return {
    valid: true,
    code: backupCode.getMaskedCode(),
    usedAt: backupCode.usedAt
  };
};

/**
 * Get active backup codes for a user
 * @param {mongoose.Types.ObjectId} userId - User ID
 * @returns {Array} Active backup codes
 */
MFABackupCodeSchema.statics.getActiveCodes = async function(userId) {
  return this.find({
    userId,
    status: 'active',
    expiresAt: { $gt: new Date() }
  }).sort({ generatedAt: 1 });
};

/**
 * Revoke all backup codes for a user
 * @param {Object} options - Revocation options
 */
MFABackupCodeSchema.statics.revokeAllForUser = async function(options = {}) {
  const {
    userId,
    revokedBy,
    reason = 'security_measure',
    ipAddress
  } = options;

  const result = await this.updateMany(
    {
      userId,
      status: 'active'
    },
    {
      $set: {
        status: 'revoked',
        revokedAt: new Date(),
        revokedBy,
        revokedReason: reason
      },
      $push: {
        chainOfCustody: {
          action: 'revoked',
          timestamp: new Date(),
          performedBy: revokedBy,
          ipAddress,
          reason
        }
      }
    }
  );

  return result;
};

const MFABackupCode = mongoose.model('MFABackupCode', MFABackupCodeSchema);
export default MFABackupCode;
