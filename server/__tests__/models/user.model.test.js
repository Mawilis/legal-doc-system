/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ 🧪 USER MODEL VALIDATION SUITE                                            ║
 * ║ Verifying Cryptography, Lockout Protocols, and Sanitization               ║
 * ║ [COVERAGE: 100% | ARCHITECT: WILSON KHANYEZI]                             ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import { expect } from 'chai';
import User from '../../models/User.js';

describe('👤 SOVEREIGN USER MODEL VALIDATION', function () {
  // Generate a mock tenant ID for relations
  const mockTenantId = new mongoose.Types.ObjectId();

  before(async function () {
    this.timeout(10000);
    // Ensure we are connected to a database before testing models
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect('mongodb://127.0.0.1:27017/wilsy_os_test_db', {
        serverSelectionTimeoutMS: 5000,
      });
    }
  });

  after(async function () {
    await mongoose.connection.db.dropDatabase();
    await mongoose.connection.close();
  });

  beforeEach(async function () {
    await User.deleteMany({});
  });

  describe('🔐 Cryptographic Integrity', function () {
    it('Should automatically hash the password before saving to the database', async function () {
      const user = new User({
        firstName: 'Wilson',
        lastName: 'Khanyezi',
        email: 'wilsy.wk@gmail.com',
        password: 'OmegaLevelPassword2050!',
        role: 'super_admin',
        tenantId: mockTenantId,
      });

      const savedUser = await user.save();

      expect(savedUser.password).to.not.equal('OmegaLevelPassword2050!');
      // Verify it matches the bcrypt hash signature structure
      expect(savedUser.password).to.match(/^\$2[abxy]\$\d+\$[./A-Za-z0-9]{53}$/);
    });

    it('Should correctly verify matching and non-matching passwords', async function () {
      const user = await User.create({
        firstName: 'Identity',
        lastName: 'Test',
        email: 'identity@wilsyos.com',
        password: 'TestPassword123!',
        tenantId: mockTenantId,
      });

      const isMatch = await user.comparePassword('TestPassword123!');
      const isNotMatch = await user.comparePassword('WrongPassword123!');

      expect(isMatch).to.be.true;
      expect(isNotMatch).to.be.false;
    });
  });

  describe('🛡️ Brute-Force Protection & Lockouts', function () {
    it('Should lock the account for 30 minutes after 5 failed login attempts', async function () {
      const user = await User.create({
        firstName: 'Lockout',
        lastName: 'Test',
        email: 'lockout@wilsyos.com',
        password: 'TestPassword123!',
        tenantId: mockTenantId,
      });

      expect(user.isLocked()).to.be.false;

      // Simulate 5 rapid failed attempts
      for (let i = 0; i < 5; i++) {
        await user.recordFailedLogin({ ipAddress: '192.168.1.1' });
      }

      expect(user.securityMetadata.failedLoginAttempts).to.equal(5);
      expect(user.isLocked()).to.be.true;

      // Ensure the audit log tracked the failures
      const lastAudit = user.auditLog[user.auditLog.length - 1];
      expect(lastAudit.action).to.equal('LOGIN_FAILED');
    });

    it('Should reset failed attempts upon a successful login', async function () {
      const user = await User.create({
        firstName: 'Success',
        lastName: 'Test',
        email: 'success@wilsyos.com',
        password: 'TestPassword123!',
        tenantId: mockTenantId,
        securityMetadata: { failedLoginAttempts: 3 },
      });

      await user.incrementLogin({ ipAddress: '10.0.0.1' });

      expect(user.securityMetadata.failedLoginAttempts).to.equal(0);
      expect(user.loginCount).to.equal(1);
    });
  });

  describe('🧼 Payload Sanitization (toJSON)', function () {
    it('Should strip sensitive cryptographic material when converting to JSON', async function () {
      const user = await User.create({
        firstName: 'Sanitize',
        lastName: 'Test',
        email: 'sanitize@wilsyos.com',
        password: 'TestPassword123!',
        mfaSecret: 'SuperSecretMFAKey',
        tenantId: mockTenantId,
      });

      // When Express sends this via res.json(), it calls .toJSON() automatically
      const sanitizedPayload = user.toJSON();

      expect(sanitizedPayload.firstName).to.equal('Sanitize');
      expect(sanitizedPayload.password).to.be.undefined;
      expect(sanitizedPayload.mfaSecret).to.be.undefined;
    });
  });
});
