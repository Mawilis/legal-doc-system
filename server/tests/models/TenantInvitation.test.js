/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  🧪 TENANT INVITATION MODEL TESTS - WILSY OS 2050                        ║
  ║  Comprehensive test suite for quantum-secure invitation system           ║
  ║  Supreme Architect: Wilson Khanyezi - 10th Generation                    ║
  ║  Surgical Fix: Dependency Pre-registration & Populate Validation         ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { expect } from 'chai';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import crypto from 'crypto';
import TenantInvitation from '../../models/TenantInvitation.js';
import { ROLES } from '../../constants/roles.js';

// --- SOVEREIGN DEPENDENCY PRE-REGISTRATION ---
// We define mock schemas for Tenant and User to satisfy the populate() requirements
// without needing to import the full heavyweight models in a unit test.
if (!mongoose.models.Tenant) {
  mongoose.model('Tenant', new mongoose.Schema({ name: String }));
}
if (!mongoose.models.User) {
  mongoose.model('User', new mongoose.Schema({ username: String, email: String }));
}

describe('TenantInvitation Model - 2050 Quantum-Secure Tests', function() {
  let mongoServer;
  let testTenantId, testUserId;

  before(async function() {
    this.timeout(10000);
    if (mongoose.connection.readyState === 0) {
      mongoServer = await MongoMemoryServer.create();
      const mongoUri = mongoServer.getUri();
      await mongoose.connect(mongoUri);
    } else {
      console.log('✅ Using existing MongoDB connection');
    }

    // Create actual documents to test population
    const Tenant = mongoose.model('Tenant');
    const User = mongoose.model('User');

    const tenant = await Tenant.create({ name: 'Wilsy Corp Sovereign' });
    const user = await User.create({ username: 'arch-wilson', email: 'wilson@wilsy.os' });

    testTenantId = tenant._id;
    testUserId = user._id;
  });

  after(async function() {
    if (mongoServer) {
      await mongoose.disconnect();
      await mongoServer.stop();
    }
  });

  beforeEach(async function() {
    await TenantInvitation.deleteMany({});
  });

  describe('Schema Validation', function() {
    it('should create a valid invitation with required fields', async function() {
      const invitation = new TenantInvitation({
        tenantId: testTenantId,
        email: 'user@example.com',
        role: ROLES.USER_VIEWER,
        invitedBy: testUserId
      });

      const saved = await invitation.save();
      expect(saved).to.have.property('_id');
      expect(saved.token).to.be.a('string').with.length.greaterThan(32);
      expect(saved.status).to.equal('pending');
    });

    it('should enforce quantum-resistant token uniqueness', async function() {
      const invitation1 = await TenantInvitation.create({
        tenantId: testTenantId,
        email: 'user1@example.com',
        role: ROLES.USER_VIEWER,
        invitedBy: testUserId
      });

      const invitation2 = new TenantInvitation({
        tenantId: testTenantId,
        email: 'user2@example.com',
        role: ROLES.USER_EDITOR,
        invitedBy: testUserId,
        token: invitation1.token
      });

      try {
        await invitation2.save();
        expect.fail('Should have thrown duplicate key error');
      } catch (error) {
        expect(error.code).to.equal(11000);
      }
    });
  });

  describe('Static Methods & Population', function() {
    it('should find valid invitation by token and populate dependencies', async function() {
      const invitation = await TenantInvitation.create({
        tenantId: testTenantId,
        email: 'populate-test@example.com',
        role: ROLES.USER_VIEWER,
        invitedBy: testUserId
      });

      // This is the specific line that was failing with MissingSchemaError
      const found = await TenantInvitation.findValid(invitation.token);

      expect(found).to.not.be.null;
      expect(found.tenantId).to.be.an('object');
      expect(found.tenantId.name).to.equal('Wilsy Corp Sovereign');
      expect(found.invitedBy.username).to.equal('arch-wilson');
    });
  });

  describe('Forensic Audit Trail', function() {
    it('should maintain an immutable audit log of the lifecycle', async function() {
      const invitation = await TenantInvitation.create({
        tenantId: testTenantId,
        email: 'audit@wilsy.os',
        role: ROLES.USER_VIEWER,
        invitedBy: testUserId,
        metadata: { ipAddress: '127.0.0.1', userAgent: 'ForensicScanner/1.0' }
      });

      expect(invitation.auditLog[0].action).to.equal('INVITATION_CREATED');
      expect(invitation.auditLog[0].quantumHash).to.exist;

      await invitation.recordView({ ipAddress: '10.0.0.1', userAgent: 'SovereignBrowser' });
      const updated = await TenantInvitation.findById(invitation._id);

      expect(updated.auditLog).to.have.length(2);
      expect(updated.auditLog[1].action).to.equal('INVITATION_VIEWED');
    });
  });

  describe('Cleanup & Retention', function() {
    it('should automate the expiration of stale invitations', async function() {
      await TenantInvitation.create({
        tenantId: testTenantId,
        email: 'stale@wilsy.os',
        role: ROLES.USER_VIEWER,
        invitedBy: testUserId,
        expiresAt: new Date(Date.now() - 1000)
      });

      const result = await TenantInvitation.cleanupExpired();
      expect(result.modifiedCount).to.equal(1);

      const stale = await TenantInvitation.findOne({ email: 'stale@wilsy.os' });
      expect(stale.status).to.equal('expired');
    });
  });
});
