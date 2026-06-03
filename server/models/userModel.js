/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN IDENTITY ENGINE [V56.5.0-PRODUCTION-IDENTITY-EPITOME]                                                           ║
 * ║ [TENANT IDENTITY | PASSWORD GOVERNANCE | ROLE ALIASES | ACCESS TELEMETRY | FORENSIC CHAIN | ANALYTICS SNAPSHOTS]                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 56.5.0-PRODUCTION-IDENTITY-EPITOME | PRODUCTION READY | CANONICAL USERS COLLECTION MODEL                                   ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/userModel.js                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated that Wilsy OS identity must protect tenants, document every function, and never fracture. ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Rebuilt the canonical User model with password history safety, role aliases, tenant access,  ║
 * ║   login lockout telemetry, safe serialization, analytics snapshots, and SHA3 forensic chain receipts.                                ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import crypto from 'node:crypto';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import { AllRoles, canBypassTenant } from '../config/roles.registry.js';

const { Schema } = mongoose;

const PASSWORD_HISTORY_LIMIT = Number(process.env.PASSWORD_HISTORY_LIMIT || 5);
const PASSWORD_BCRYPT_ROUNDS = Number(process.env.PASSWORD_BCRYPT_ROUNDS || 12);
const MAX_FAILED_ATTEMPTS = Number(process.env.AUTH_MAX_FAILED_ATTEMPTS || 5);
const LOCKOUT_DURATION_MS = Number(process.env.AUTH_LOCKOUT_MINUTES || 30) * 60 * 1000;
const FORENSIC_CHAIN_LIMIT = Number(process.env.USER_FORENSIC_CHAIN_LIMIT || 500);

const BUSINESS_ROLE_ALIASES = Object.freeze([
  'executive',
  'finance',
  'billing',
  'risk',
  'compliance',
  'devops',
  'deal_team',
  'sales_representative',
  'operations_manager',
  'tenant_user'
]);

const USER_ROLE_ENUM = Object.freeze([
  ...new Set([
    ...AllRoles,
    ...BUSINESS_ROLE_ALIASES,
    ...BUSINESS_ROLE_ALIASES.map(role => role.toUpperCase())
  ])
]);

/**
 * @function normalizeUserEmail
 * @description Normalizes identity email values before persistence or authentication lookup.
 * @param {string} email - Candidate user email.
 * @returns {string} Lowercase trimmed email.
 * @collaboration Tenant access must start from one canonical identity value so audit trails do not split across casing variants.
 */
export const normalizeUserEmail = (email = '') => String(email || '').trim().toLowerCase();

/**
 * @function normalizeUserRole
 * @description Converts supplied roles into a schema-safe Wilsy OS role token.
 * @param {string} role - Candidate role.
 * @returns {string} Normalized role token.
 * @collaboration Wilson requires dynamic tenant access without rebuilding components; role aliases keep business dashboards assignable.
 */
export const normalizeUserRole = (role = 'user') => {
  const candidate = String(role || 'user').trim();
  if (USER_ROLE_ENUM.includes(candidate)) return candidate;
  const lower = candidate.toLowerCase();
  return USER_ROLE_ENUM.includes(lower) ? lower : 'user';
};

/**
 * @function stableUserStringify
 * @description Serializes identity packets with deterministic key order for repeatable SHA3 forensic hashes.
 * @param {unknown} value - Value to serialize.
 * @returns {string} Canonical JSON string.
 * @collaboration Every identity mutation receipt must replay to the same cryptographic answer for court and investor review.
 */
export const stableUserStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableUserStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableUserStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createUserProofHash
 * @description Creates a SHA3-512 proof hash for identity, access and analytics packets.
 * @param {Object} payload - Payload to seal.
 * @returns {string} Uppercase SHA3-512 digest.
 * @collaboration Identity data is a legal boundary; every material mutation should carry a tamper-evident receipt.
 */
export const createUserProofHash = (payload = {}) => crypto
  .createHash('sha3-512')
  .update(stableUserStringify(payload))
  .digest('hex')
  .toUpperCase();

/**
 * @function isBcryptHash
 * @description Detects whether a secret value is already a bcrypt digest.
 * @param {string} value - Candidate secret.
 * @returns {boolean} True when the value appears to be a bcrypt hash.
 * @collaboration Prevents double-hashing during partial document saves and keeps login verification reliable.
 */
const isBcryptHash = (value = '') => /^\$2[aby]\$\d{2}\$/.test(String(value || ''));

/**
 * @function safeBroadcastUserTelemetry
 * @description Broadcasts user-model telemetry without letting telemetry outages break authentication.
 * @param {string} tenantId - Tenant id.
 * @param {string} eventType - Telemetry event type.
 * @param {string} status - Telemetry status.
 * @param {Object} metadata - Telemetry metadata.
 * @returns {Promise<void>} Resolves after best-effort broadcast.
 * @collaboration Security evidence should be emitted whenever possible, while login and identity writes remain operational during telemetry fractures.
 */
const safeBroadcastUserTelemetry = async (tenantId = 'GLOBAL_ROOT', eventType = 'USER_EVENT', status = 'COMMITTED', metadata = {}) => {
  await broadcastTelemetry(tenantId || 'GLOBAL_ROOT', eventType, status, 'UserModel', metadata).catch(() => {});
};

/**
 * @function compareCandidateAgainstHashes
 * @description Checks a plaintext password candidate against stored bcrypt password hashes.
 * @param {string} candidate - Plaintext candidate password.
 * @param {Array<string>} hashes - Stored bcrypt hashes.
 * @returns {Promise<boolean>} True when the candidate matches one of the hashes.
 * @collaboration Password reuse prevention must inspect real hash history without ever exposing previous secrets.
 */
const compareCandidateAgainstHashes = async (candidate = '', hashes = []) => {
  const usableHashes = hashes.filter(hash => isBcryptHash(hash));
  for (const hash of usableHashes) {
    if (await bcrypt.compare(candidate, hash)) return true;
  }
  return false;
};

/**
 * @function buildPasswordHistoryBuffer
 * @description Creates the bounded password history buffer after a new password is hashed.
 * @param {string} newHash - Newly generated bcrypt hash.
 * @param {Array<string>} previousHashes - Previous password hashes.
 * @returns {Array<string>} Bounded password history.
 * @collaboration Keeps enough history to stop reuse while preventing unbounded sensitive metadata growth.
 */
const buildPasswordHistoryBuffer = (newHash = '', previousHashes = []) => (
  [newHash, ...previousHashes.filter(hash => hash && hash !== newHash)]
    .slice(0, PASSWORD_HISTORY_LIMIT)
);

/**
 * @function buildForensicEntryPacket
 * @description Builds a SHA3-sealed forensic chain entry for user identity actions.
 * @param {Object} params - Entry inputs.
 * @returns {Object} Forensic entry.
 * @collaboration User mutations should become evidence-grade receipts, not anonymous model writes.
 */
const buildForensicEntryPacket = ({ tenantId, action, performer, payload = {}, previousHash = null } = {}) => {
  const entryId = `USR-${Date.now().toString(36).toUpperCase()}-${crypto.randomBytes(6).toString('hex').toUpperCase()}`;
  const traceId = `TRACE-${crypto.randomBytes(10).toString('hex').toUpperCase()}`;
  const timestamp = new Date();
  const sealPayload = {
    entryId,
    traceId,
    timestamp: timestamp.toISOString(),
    tenantId,
    action,
    performer,
    payload,
    previousHash
  };
  return {
    entryId,
    traceId,
    timestamp,
    action,
    performer,
    payload,
    seal: {
      algorithm: 'SHA3-512',
      hash: createUserProofHash(sealPayload),
      previousHash
    }
  };
};

/**
 * @function buildTenantActivityWindow
 * @description Builds date windows for tenant user activity metrics.
 * @param {number} days - Number of days to look back.
 * @returns {Date} Date boundary.
 * @collaboration Analytics routes need a shared identity clock so user activity metrics remain consistent.
 */
const buildTenantActivityWindow = (days = 1) => new Date(Date.now() - Number(days || 1) * 24 * 60 * 60 * 1000);

export const UserSchema = new Schema(
  {
    email: { type: String, required: [true, 'Email is required'], unique: true, lowercase: true, trim: true, index: true },
    password: { type: String, required: [true, 'Password is required'], minlength: 12, select: false },
    passwordHistory: { type: [String], select: false, default: [] },
    firstName: { type: String, required: true, trim: true },
    lastName: { type: String, required: true, trim: true },
    role: { type: String, enum: USER_ROLE_ENUM, default: 'user', index: true, set: normalizeUserRole },
    permissions: { type: [String], default: [], index: true },
    tenantId: { type: String, required: true, trim: true, index: true },
    lastLogin: { type: Date, index: true },
    authenticators: [{
      credentialID: { type: Buffer, required: true },
      publicKey: { type: Buffer, required: true },
      counter: { type: Number, default: 0 },
      deviceType: { type: String, default: 'hardware' },
      transports: [String],
      createdAt: { type: Date, default: Date.now }
    }],
    recoverySeedHash: { type: String, select: false },
    isTwoFactorEnabled: { type: Boolean, default: false, index: true },
    twoFactorSecret: { type: String, select: false },
    securityClearance: { type: String, enum: ['standard', 'gamma', 'delta', 'omega'], default: 'standard' },
    isActive: { type: Boolean, default: true, index: true },
    biometric: {
      registered: { type: Boolean, default: false },
      type: { type: String, enum: ['WEBAUTHN_FIDO2', 'PASSKEY', 'FINGERPRINT', 'FACIAL'], default: 'WEBAUTHN_FIDO2' },
      registrationDate: Date,
      lastUsed: Date,
      status: { type: String, enum: ['PENDING_VERIFICATION', 'ACTIVE', 'REVOKED'], default: 'PENDING_VERIFICATION' }
    },
    securityMetadata: {
      mfaEnabled: { type: Boolean, default: false },
      mfaSetupComplete: { type: Boolean, default: false },
      mfaBackupCodes: { type: [String], select: false },
      mfaBackupCodesLastGenerated: Date,
      lastLogin: Date,
      lastFailedLogin: Date,
      lastKnownLocation: String,
      failedAttempts: { type: Number, default: 0 },
      lockUntil: Date,
      lockReason: String,
      lastPasswordChange: Date,
      forensicFingerprint: String,
      lastAccessDenied: Date,
      accessDeniedReason: String,
      mfaSecret: { type: String, select: false }
    },
    forensicChain: [{
      entryId: String,
      traceId: String,
      timestamp: { type: Date, default: Date.now },
      action: String,
      performer: String,
      payload: Schema.Types.Mixed,
      seal: {
        algorithm: { type: String, default: 'SHA3-512' },
        hash: String,
        previousHash: String
      }
    }]
  },
  {
    timestamps: true,
    collection: 'users',
    toJSON: {
      virtuals: true,
      transform(document, returned) {
        delete returned.password;
        delete returned.passwordHistory;
        delete returned.recoverySeedHash;
        delete returned.twoFactorSecret;
        if (returned.securityMetadata) {
          delete returned.securityMetadata.mfaBackupCodes;
          delete returned.securityMetadata.mfaSecret;
        }
        return returned;
      }
    }
  }
);

UserSchema.index({ email: 1, tenantId: 1 }, { unique: true });
UserSchema.index({ tenantId: 1, role: 1, isActive: 1 });
UserSchema.index({ tenantId: 1, lastLogin: -1 });
UserSchema.index({ tenantId: 1, 'securityMetadata.lastLogin': -1 });
UserSchema.index({ 'forensicChain.entryId': 1 });
UserSchema.index({ 'securityMetadata.lockUntil': 1 });
UserSchema.index({ 'authenticators.credentialID': 1 });

/**
 * @function userPreValidateMiddleware
 * @description Normalizes email, role and tenant fields before Mongoose validation.
 * @returns {void}
 * @collaboration Canonical field normalization keeps tenant isolation and role routing consistent across every dashboard.
 */
UserSchema.pre('validate', function() {
  this.email = normalizeUserEmail(this.email);
  this.role = normalizeUserRole(this.role);
  this.tenantId = String(this.tenantId || '').trim();
  if (!this.securityMetadata) this.securityMetadata = {};
  if (!this.permissions) this.permissions = [];
});

/**
 * @function userPreSaveMiddleware
 * @description Hashes passwords, blocks password reuse, hashes MFA backup codes and seals creation events before persistence.
 * @returns {Promise<void>} Resolves after security transformations.
 * @collaboration Identity writes should be institutionally governed before MongoDB ever receives the document.
 */
UserSchema.pre('save', async function() {
  if (!this.passwordHistory) this.passwordHistory = [];
  if (!this.securityMetadata) this.securityMetadata = {};

  if (this.isModified('password') && this.password) {
    const candidatePassword = String(this.password);
    if (!isBcryptHash(candidatePassword)) {
      let previousHashes = [];
      if (!this.isNew && this._id) {
        const existingUser = await this.constructor
          .findById(this._id)
          .select('+password +passwordHistory')
          .lean();
        previousHashes = [
          existingUser?.password,
          ...(existingUser?.passwordHistory || []),
          ...(this.passwordHistory || [])
        ].filter(Boolean);
      } else {
        previousHashes = [...(this.passwordHistory || [])];
      }

      if (await compareCandidateAgainstHashes(candidatePassword, previousHashes)) {
        await safeBroadcastUserTelemetry(this.tenantId, 'USER_PASSWORD_REUSE_BLOCKED', 'BLOCKED', {
          userId: this._id?.toString(),
          email: this.email
        });
        throw new Error('Password reuse detected. Choose a new password that has not been used recently.');
      }

      const hashedPassword = await bcrypt.hash(candidatePassword, PASSWORD_BCRYPT_ROUNDS);
      this.password = hashedPassword;
      this.passwordHistory = buildPasswordHistoryBuffer(hashedPassword, previousHashes);
      this.securityMetadata.lastPasswordChange = new Date();
      this.securityMetadata.forensicFingerprint = createUserProofHash({
        tenantId: this.tenantId,
        email: this.email,
        passwordChangedAt: this.securityMetadata.lastPasswordChange
      }).slice(0, 48);
      await safeBroadcastUserTelemetry(this.tenantId, 'USER_PASSWORD_CHANGED', 'COMMITTED', {
        userId: this._id?.toString(),
        fingerprint: this.securityMetadata.forensicFingerprint
      });
    }
  }

  if (
    this.isModified('securityMetadata.mfaBackupCodes')
    && Array.isArray(this.securityMetadata?.mfaBackupCodes)
    && this.securityMetadata.mfaBackupCodes.some(code => !isBcryptHash(code))
  ) {
    this.securityMetadata.mfaBackupCodes = await Promise.all(
      this.securityMetadata.mfaBackupCodes.map(code => (
        isBcryptHash(code) ? code : bcrypt.hash(String(code), PASSWORD_BCRYPT_ROUNDS)
      ))
    );
    this.securityMetadata.mfaBackupCodesLastGenerated = new Date();
  }

  if (this.isModified('isTwoFactorEnabled')) {
    this.securityMetadata.mfaEnabled = Boolean(this.isTwoFactorEnabled);
    this.securityMetadata.mfaSetupComplete = Boolean(this.isTwoFactorEnabled);
  }

  if (this.isNew) {
    this.appendForensicEntry('USER_CREATED', 'SYSTEM', {
      email: this.email,
      role: this.role,
      tenantId: this.tenantId
    });
  }

  if (Array.isArray(this.forensicChain) && this.forensicChain.length > FORENSIC_CHAIN_LIMIT) {
    this.forensicChain = this.forensicChain.slice(-FORENSIC_CHAIN_LIMIT);
  }
});

/**
 * @function matchPassword
 * @description Validates a password candidate, applies failed-attempt lockout and records successful login timestamps.
 * @param {string} candidatePassword - Plaintext password candidate.
 * @returns {Promise<boolean>} True when the password matches.
 * @collaboration Login checks are both access decisions and security telemetry events for Wilsy OS tenants.
 */
UserSchema.methods.matchPassword = async function(candidatePassword) {
  const identity = this.password
    ? this
    : await this.constructor.findById(this._id).select('+password +passwordHistory +securityMetadata.mfaBackupCodes');

  if (!identity || identity.isLocked()) {
    await safeBroadcastUserTelemetry(this.tenantId, 'USER_LOCKED_LOGIN_ATTEMPT', 'BLOCKED', {
      userId: this._id?.toString()
    });
    return false;
  }

  if (!isBcryptHash(identity.password)) {
    await safeBroadcastUserTelemetry(this.tenantId, 'USER_PASSWORD_HASH_INVALID', 'BLOCKED', {
      userId: this._id?.toString()
    });
    return false;
  }

  const isMatch = await bcrypt.compare(String(candidatePassword || ''), identity.password || '');
  if (isMatch) {
    await identity.recordSuccessfulLogin();
    return true;
  }

  await identity.recordFailedLogin();
  return false;
};

/**
 * @function recordSuccessfulLogin
 * @description Clears lockout state and records the latest successful login timestamp.
 * @returns {Promise<Object>} Updated user document.
 * @collaboration Executive and analytics dashboards need real user activity, not guessed engagement counters.
 */
UserSchema.methods.recordSuccessfulLogin = async function() {
  if (!this.securityMetadata) this.securityMetadata = {};
  const now = new Date();
  this.lastLogin = now;
  this.securityMetadata.lastLogin = now;
  this.securityMetadata.failedAttempts = 0;
  this.securityMetadata.lockUntil = undefined;
  this.securityMetadata.lockReason = undefined;
  this.appendForensicEntry('LOGIN_SUCCESS', 'AUTHENTICATION_ENGINE', {
    role: this.role,
    tenantId: this.tenantId
  });
  await this.save({ validateBeforeSave: false });
  await safeBroadcastUserTelemetry(this.tenantId, 'USER_LOGIN_SUCCESS', 'COMMITTED', {
    userId: this._id?.toString(),
    role: this.role
  });
  return this;
};

/**
 * @function recordFailedLogin
 * @description Increments failed login counters and locks the account after configured threshold breach.
 * @returns {Promise<Object>} Updated user document.
 * @collaboration Account lockout converts suspicious access into visible, tenant-scoped security posture.
 */
UserSchema.methods.recordFailedLogin = async function() {
  if (!this.securityMetadata) this.securityMetadata = {};
  const attempts = Number(this.securityMetadata.failedAttempts || 0) + 1;
  this.securityMetadata.failedAttempts = attempts;
  this.securityMetadata.lastFailedLogin = new Date();
  if (attempts >= MAX_FAILED_ATTEMPTS) {
    this.securityMetadata.lockUntil = new Date(Date.now() + LOCKOUT_DURATION_MS);
    this.securityMetadata.lockReason = 'MAX_FAILED_ATTEMPTS';
  }
  this.appendForensicEntry('LOGIN_FAILED', 'AUTHENTICATION_ENGINE', {
    attempts,
    locked: this.isLocked()
  });
  await this.save({ validateBeforeSave: false });
  await safeBroadcastUserTelemetry(this.tenantId, 'USER_LOGIN_FAILED', this.isLocked() ? 'LOCKED' : 'FAILED', {
    userId: this._id?.toString(),
    attempts
  });
  return this;
};

/**
 * @function appendForensicEntry
 * @description Appends a bounded SHA3-sealed identity event to the user forensic chain.
 * @param {string} action - Action label.
 * @param {string} performer - Actor or subsystem creating the entry.
 * @param {Object} payload - Evidence payload.
 * @returns {Object} Current user document.
 * @collaboration Every meaningful access and identity mutation should leave future maintainers a tamper-evident trail.
 */
UserSchema.methods.appendForensicEntry = function(action, performer, payload = {}) {
  if (!Array.isArray(this.forensicChain)) this.forensicChain = [];
  const previousHash = this.forensicChain.at(-1)?.seal?.hash || null;
  this.forensicChain.push(buildForensicEntryPacket({
    tenantId: this.tenantId,
    action,
    performer,
    payload,
    previousHash
  }));
  if (this.forensicChain.length > FORENSIC_CHAIN_LIMIT) {
    this.forensicChain = this.forensicChain.slice(-FORENSIC_CHAIN_LIMIT);
  }
  return this;
};

/**
 * @function isLocked
 * @description Determines whether the user account is currently locked.
 * @returns {boolean} True when lockUntil is in the future.
 * @collaboration Lockout state must be deterministic so dashboards can explain why access is denied.
 */
UserSchema.methods.isLocked = function() {
  if (!this.securityMetadata?.lockUntil) return false;
  return new Date(this.securityMetadata.lockUntil).getTime() > Date.now();
};

/**
 * @function canAccessTenant
 * @description Checks whether this user may access a target tenant shard.
 * @param {string} targetTenantId - Target tenant id.
 * @returns {boolean} True when access is permitted.
 * @collaboration Tenant isolation is mandatory; lateral authority is explicit and never inferred from UI state.
 */
UserSchema.methods.canAccessTenant = function(targetTenantId = '') {
  const target = String(targetTenantId || '').trim();
  if (!target) return false;
  if (String(this.tenantId || '').trim() === target) return true;
  return canBypassTenant(this.role);
};

/**
 * @function hasRole
 * @description Checks the user's role against one or more allowed role tokens.
 * @param {...string|Array<string>} roles - Allowed role tokens.
 * @returns {boolean} True when the role matches or sovereign bypass applies.
 * @collaboration Route gates and dashboards need the same case-insensitive role interpretation.
 */
UserSchema.methods.hasRole = function(...roles) {
  const allowed = roles
    .flat(Infinity)
    .filter(Boolean)
    .map(role => String(role).toLowerCase());
  const role = String(this.role || '').toLowerCase();
  return allowed.includes(role) || canBypassTenant(this.role);
};

/**
 * @function hasPermission
 * @description Checks a named permission against explicit user permissions and sovereign bypass roles.
 * @param {string} permission - Permission token.
 * @returns {boolean} True when permission is granted.
 * @collaboration Wilsy OS can dynamically enable tenant functions without creating a new dashboard component per business type.
 */
UserSchema.methods.hasPermission = function(permission = '') {
  if (canBypassTenant(this.role)) return true;
  return Array.isArray(this.permissions) && this.permissions.includes(permission);
};

/**
 * @function recordAccessDenied
 * @description Records a denied access attempt with tenant-aware forensic metadata.
 * @param {Object} params - Denial context.
 * @returns {Object} Current user document.
 * @collaboration When users attempt blocked functions, Wilsy OS must explain the channel and preserve the attempt.
 */
UserSchema.methods.recordAccessDenied = function({ reason = 'INSUFFICIENT_PRIVILEGE', target = '', channel = 'SYSTEM' } = {}) {
  if (!this.securityMetadata) this.securityMetadata = {};
  this.securityMetadata.lastAccessDenied = new Date();
  this.securityMetadata.accessDeniedReason = reason;
  this.appendForensicEntry('ACCESS_DENIED', channel, {
    reason,
    target,
    role: this.role,
    tenantId: this.tenantId
  });
  return this;
};

/**
 * @function toSafeIdentity
 * @description Converts a user document into a secret-free identity packet for APIs and dashboards.
 * @returns {Object} Safe identity payload.
 * @collaboration Frontends should receive actionable access context without ever receiving credential secrets.
 */
UserSchema.methods.toSafeIdentity = function() {
  return {
    id: this._id?.toString(),
    email: this.email,
    firstName: this.firstName,
    lastName: this.lastName,
    role: this.role,
    permissions: this.permissions || [],
    tenantId: this.tenantId,
    isActive: this.isActive,
    isTwoFactorEnabled: this.isTwoFactorEnabled,
    securityClearance: this.securityClearance,
    lastLogin: this.lastLogin || this.securityMetadata?.lastLogin || null,
    locked: this.isLocked(),
    proofHash: createUserProofHash({
      id: this._id?.toString(),
      tenantId: this.tenantId,
      role: this.role,
      lastLogin: this.lastLogin || this.securityMetadata?.lastLogin || null
    })
  };
};

/**
 * @function findByEmailForAuth
 * @description Finds a user for authentication with password and security metadata selected.
 * @param {string} email - Candidate email.
 * @param {string|null} tenantId - Optional tenant id.
 * @returns {Promise<Object|null>} User document or null.
 * @collaboration Authentication services need one safe model API instead of repeating select-sensitive queries.
 */
UserSchema.statics.findByEmailForAuth = function(email, tenantId = null) {
  const query = { email: normalizeUserEmail(email) };
  if (tenantId) query.tenantId = String(tenantId).trim();
  return this.findOne(query).select('+password +passwordHistory +recoverySeedHash +twoFactorSecret +securityMetadata.mfaBackupCodes +securityMetadata.mfaSecret');
};

/**
 * @function countActiveByTenant
 * @description Counts active users inside one tenant shard.
 * @param {string} tenantId - Tenant id.
 * @returns {Promise<number>} Active user count.
 * @collaboration Analytics and executive dashboards should count users through a tenant-isolated model helper.
 */
UserSchema.statics.countActiveByTenant = function(tenantId = '') {
  return this.countDocuments({ tenantId: String(tenantId || '').trim(), isActive: true });
};

/**
 * @function buildTenantUserSnapshot
 * @description Builds tenant-scoped user activity metrics for analytics routes.
 * @param {string} tenantId - Tenant id.
 * @returns {Promise<Object>} User activity snapshot.
 * @collaboration Removes fake dashboard activity by deriving executive metrics from the users collection itself.
 */
UserSchema.statics.buildTenantUserSnapshot = async function(tenantId = '') {
  const safeTenantId = String(tenantId || '').trim();
  const today = buildTenantActivityWindow(1);
  const week = buildTenantActivityWindow(7);
  const baseQuery = { tenantId: safeTenantId, isActive: true };
  const activeTodayQuery = {
    ...baseQuery,
    $or: [
      { lastLogin: { $gte: today } },
      { 'securityMetadata.lastLogin': { $gte: today } }
    ]
  };
  const activeWeekQuery = {
    ...baseQuery,
    $or: [
      { lastLogin: { $gte: week } },
      { 'securityMetadata.lastLogin': { $gte: week } }
    ]
  };
  const [totalUsers, activeToday, activeThisWeek, lockedUsers] = await Promise.all([
    this.countDocuments(baseQuery),
    this.countDocuments(activeTodayQuery),
    this.countDocuments(activeWeekQuery),
    this.countDocuments({
      ...baseQuery,
      'securityMetadata.lockUntil': { $gte: new Date() }
    })
  ]);
  const activePercentage = totalUsers > 0 ? Number(((activeToday / totalUsers) * 100).toFixed(1)) : 0;
  const payload = {
    totalUsers,
    activeToday,
    activeThisWeek,
    activePercentage,
    lockedUsers,
    tenantId: safeTenantId,
    tenantIsolated: true,
    sourceStatus: totalUsers > 0 ? 'USER_ACTIVITY_SOURCE_LIVE' : 'USER_ACTIVITY_SOURCE_REQUIRED',
    syncedAt: new Date().toISOString()
  };
  return {
    ...payload,
    proofHash: createUserProofHash(payload)
  };
};

const User = mongoose.models.User || mongoose.model('User', UserSchema);

export { User };
export default User;
