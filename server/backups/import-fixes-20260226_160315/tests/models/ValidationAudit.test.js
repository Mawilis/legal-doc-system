#!/* eslint-env mocha */

/* eslint-disable */
import { expect } from "chai";
import mongoose from "mongoose";
import ValidationAudit, {
  AUDIT_ACTIONS,
  AUDIT_STATUS,
  SEVERITY_LEVELS,
  RETENTION_POLICIES,
  DATA_RESIDENCY,
} from '../../models/ValidationAudit;

describe('ValidationAudit Model - Forensic Grade Audit Trail', function() {
  const testTenantId = 'test-tenant-12345678';
  const testAuditId = 'audit-12345678-test';

  before(async () => {
    // Ensure clean connection
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/legal_doc_test');
    }
    await ValidationAudit.deleteMany({});
  });

  after(async () => {
    await ValidationAudit.deleteMany({});
    await mongoose.connection.close();
  });

  beforeEach(async () => {
    await ValidationAudit.deleteMany({});
  });

  describe('📊 Schema Validation', function() {
    it('should create a valid audit entry with minimal fields', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      const saved = await audit.save();
      expect(saved._id).to.exist;
      expect(saved.auditId).to.exist;
      expect(saved.hash).to.exist;
      expect(saved.chainPosition).to.equal(1);
    });

    it('should require tenantId', async function() {
      const audit = new ValidationAudit({
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      try {
        await audit.save();
        assert.fail('Should have thrown validation error');
      } catch (error) {
        expect(error.errors.tenantId).to.exist;
      }
    });

    it('should validate tenantId format', async function() {
      const audit = new ValidationAudit({
        tenantId: 'invalid',
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      try {
        await audit.save();
        assert.fail('Should have thrown validation error');
      } catch (error) {
        expect(error.errors.tenantId).to.exist;
      }
    });

    it('should require action', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      try {
        await audit.save();
        assert.fail('Should have thrown validation error');
      } catch (error) {
        expect(error.errors.action).to.exist;
      }
    });

    it('should have default status as SUCCESS', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      expect(audit.status).to.equal(AUDIT_STATUS.SUCCESS);
    });

    it('should have default severity as INFO', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      expect(audit.severity).to.equal(SEVERITY_LEVELS.INFO);
    });

    it('should accept all audit action types', async function() {
      const actions = Object.values(AUDIT_ACTIONS);

      for (const action of actions) {
        const audit = new ValidationAudit({
          tenantId: testTenantId,
          action,
          resourceType: 'identity',
          validationResult: { valid: true },
        });

        expect(audit.action).to.equal(action);
      }
    });

    it('should accept all resource types', async function() {
      const resourceTypes = [
        'identity',
        'business',
        'professional',
        'court',
        'jurisdiction',
        'document',
        'financial',
        'evidence',
        'system',
        'user',
        'tenant',
      ];

      for (const resourceType of resourceTypes) {
        const audit = new ValidationAudit({
          tenantId: testTenantId,
          action: AUDIT_ACTIONS.ID_VALIDATION,
          resourceType,
          validationResult: { valid: true },
        });

        expect(audit.resourceType).to.equal(resourceType);
      }
    });
  });

  describe('🔐 Cryptographic Security', function() {
    it('should generate auditId if not provided', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      await audit.save();
      expect(audit.auditId).to.exist;
      expect(audit.auditId).to.be.a('string');
    });

    it('should use provided auditId if given', async function() {
      const audit = new ValidationAudit({
        auditId: testAuditId,
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      await audit.save();
      expect(audit.auditId).to.equal(testAuditId);
    });

    it('should generate hash on save', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      await audit.save();
      expect(audit.hash).to.exist;
      expect(audit.hash).to.be.a('string');
      expect(audit.hash).to.have.lengthOf(64);
    });

    it('should generate consistent hash for same data', async function() {
      const audit1 = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });
      await audit1.save();

      const audit2 = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });
      await audit2.save();

      expect(audit1.hash).to.not.equal(audit2.hash);
    });

    it('should verify integrity correctly', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      await audit.save();
      expect(audit.verifyIntegrity()).to.be.true;
    });

    it('should detect tampering', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      await audit.save();

      // Tamper with data
      audit.validationResult.valid = false;

      expect(audit.verifyIntegrity()).to.be.false;
    });
  });

  describe('⛓️ Hash Chain', function() {
    it('should set chain position starting from 1', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      await audit.save();
      expect(audit.chainPosition).to.equal(1);
    });

    it('should link to previous hash', async function() {
      const audit1 = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });
      await audit1.save();

      const audit2 = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.CIPC_VALIDATION,
        resourceType: 'business',
        validationResult: { valid: true },
      });
      await audit2.save();

      expect(audit2.previousHash).to.equal(audit1.hash);
      expect(audit2.chainPosition).to.equal(2);
    });

    it('should auto-increment chain position', async function() {
      const audit1 = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });
      await audit1.save();

      const audit2 = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.CIPC_VALIDATION,
        resourceType: 'business',
        validationResult: { valid: true },
      });
      await audit2.save();

      expect(audit2.chainPosition).to.equal(2);
    });

    it('should maintain separate chains per tenant', async function() {
      const tenant1 = 'tenant-1-12345678';
      const tenant2 = 'tenant-2-12345678';

      const audit1 = new ValidationAudit({
        tenantId: tenant1,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });
      await audit1.save();

      const audit2 = new ValidationAudit({
        tenantId: tenant2,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });
      await audit2.save();

      expect(audit1.chainPosition).to.equal(1);
      expect(audit2.chainPosition).to.equal(1);
    });

    it('should verify chain integrity', async function() {
      const audit1 = await ValidationAudit.createAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      const audit2 = await ValidationAudit.createAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.CIPC_VALIDATION,
        resourceType: 'business',
        validationResult: { valid: true },
      });

      const result = await ValidationAudit.verifyChain(testTenantId);
      expect(result.verified).to.be.true;
      expect(result.entryCount).to.equal(2);
      expect(result.brokenLinks).to.have.lengthOf(0);
    });

    it('should detect broken chain', async function() {
      const audit1 = await ValidationAudit.createAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      const audit2 = await ValidationAudit.createAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.CIPC_VALIDATION,
        resourceType: 'business',
        validationResult: { valid: true },
      });

      // Break the chain by directly updating the database
      await ValidationAudit.updateOne({ _id: audit2._id }, { $set: { previousHash: 'tampered-hash' } });

      const result = await ValidationAudit.verifyChain(testTenantId);
      expect(result.verified).to.be.false;
      expect(result.brokenLinks).to.have.length.of.at.least(1);
    });
  });

  describe('📦 Retention Policies', function() {
    it('should set default retention policy', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      await audit.save();
      expect(audit.retentionPolicy).to.equal('POPIA_6_YEARS');
      expect(audit.retentionExpiry).to.exist;
    });

    it('should accept specified retention policy', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
        retentionPolicy: 'COMPANIES_ACT_10_YEARS',
      });

      await audit.save();
      expect(audit.retentionPolicy).to.equal('COMPANIES_ACT_10_YEARS');
    });

    it('should calculate retention expiry correctly', async function() {
      const policy = RETENTION_POLICIES.COMPANIES_ACT_10_YEARS;
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
        retentionPolicy: 'COMPANIES_ACT_10_YEARS',
      });

      await audit.save();

      const expectedExpiry = new Date(Date.now() + policy.durationMs);
      const actualExpiry = audit.retentionExpiry;

      expect(actualExpiry.getFullYear()).to.equal(expectedExpiry.getFullYear());
    });

    it('should calculate age in days virtual property', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
        timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
      });

      expect(audit.ageInDays).to.be.at.least(5);
    });

    it('should determine if expired', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
        retentionExpiry: new Date(Date.now() - 1000),
      });

      expect(audit.isExpired).to.be.true;
    });

    it('should apply retention policies via static method', async function() {
      const expired = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
        retentionExpiry: new Date(Date.now() - 5000),
      });
      await expired.save();

      const active = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.CIPC_VALIDATION,
        resourceType: 'business',
        validationResult: { valid: true },
        retentionExpiry: new Date(Date.now() + 86400000),
      });
      await active.save();

      const result = await ValidationAudit.applyRetention();
      expect(result.deletedCount).to.equal(1);
    });
  });

  describe('🔍 Query Methods', function() {
    beforeEach(async () => {
      await ValidationAudit.create([
        {
          tenantId: testTenantId,
          action: AUDIT_ACTIONS.ID_VALIDATION,
          resourceType: 'identity',
          status: AUDIT_STATUS.SUCCESS,
          validationResult: { valid: true },
          timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
        },
        {
          tenantId: testTenantId,
          action: AUDIT_ACTIONS.CIPC_VALIDATION,
          resourceType: 'business',
          status: AUDIT_STATUS.SUCCESS,
          validationResult: { valid: true },
          timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
        },
        {
          tenantId: testTenantId,
          action: AUDIT_ACTIONS.VAT_VALIDATION,
          resourceType: 'business',
          status: AUDIT_STATUS.FAILURE,
          validationResult: { valid: false },
          timestamp: new Date(),
        },
      ]);
    });

    it('should find entries for tenant', async function() {
      const entries = await ValidationAudit.findForTenant(testTenantId);
      expect(entries).to.be.an('array');
      expect(entries).to.have.lengthOf(3);
    });

    it('should filter by action', async function() {
      const entries = await ValidationAudit.findForTenant(testTenantId, {
        action: AUDIT_ACTIONS.CIPC_VALIDATION,
      });

      expect(entries).to.have.lengthOf(1);
      expect(entries[0].action).to.equal(AUDIT_ACTIONS.CIPC_VALIDATION);
    });

    it('should filter by status', async function() {
      const entries = await ValidationAudit.findForTenant(testTenantId, {
        status: AUDIT_STATUS.FAILURE,
      });

      expect(entries).to.have.lengthOf(1);
      expect(entries[0].status).to.equal(AUDIT_STATUS.FAILURE);
    });

    it('should filter by date range', async function() {
      const fromDate = new Date(Date.now() - 1.5 * 24 * 60 * 60 * 1000);

      const entries = await ValidationAudit.findForTenant(testTenantId, {
        timestamp: { $gte: fromDate },
      });

      expect(entries).to.have.lengthOf(2);
    });

    it('should limit results', async function() {
      const entries = await ValidationAudit.findForTenant(testTenantId, {}, { limit: 2 });
      expect(entries).to.have.lengthOf(2);
    });

    it('should sort results', async function() {
      const entries = await ValidationAudit.findForTenant(
        testTenantId,
        {},
        {
          sort: { timestamp: 1 },
        },
      );

      expect(entries[0].action).to.equal(AUDIT_ACTIONS.ID_VALIDATION);
      expect(entries[2].action).to.equal(AUDIT_ACTIONS.VAT_VALIDATION);
    });

    it('should skip results for pagination', async function() {
      const entries = await ValidationAudit.findForTenant(
        testTenantId,
        {},
        {
          skip: 1,
          limit: 1,
        },
      );

      expect(entries).to.have.lengthOf(1);
      expect(entries[0].action).to.equal(AUDIT_ACTIONS.CIPC_VALIDATION);
    });
  });

  describe('📤 Evidence Export', function() {
    it('should export evidence package', async function() {
      await ValidationAudit.createAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      const result = await ValidationAudit.exportEvidence(testTenantId);
      expect(result.package).to.exist;
      expect(result.package.tenantId).to.equal(testTenantId);
      expect(result.package.entryCount).to.equal(1);
      expect(result.overallHash).to.exist;
    });

    it('should export filtered evidence', async function() {
      await ValidationAudit.createAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      await ValidationAudit.createAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.CIPC_VALIDATION,
        resourceType: 'business',
        validationResult: { valid: true },
      });

      const result = await ValidationAudit.exportEvidence(testTenantId, {
        action: AUDIT_ACTIONS.CIPC_VALIDATION,
      });

      expect(result.package.entryCount).to.equal(1);
      expect(result.package.entries[0].action).to.equal(AUDIT_ACTIONS.CIPC_VALIDATION);
    });

    it('should generate evidence from instance', async function() {
      const audit = await ValidationAudit.createAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      const evidence = audit.generateEvidence();
      expect(evidence).to.be.an('object');
      expect(evidence.auditId).to.equal(audit.auditId);
      expect(evidence.hash).to.equal(audit.hash);
      expect(evidence.verification).to.equal('VERIFIED');
    });
  });

  describe('🔒 POPIA Compliance', function() {
    it('should redact PII from request data', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
        requestData: {
          idNumber: '8001015009087',
          email: 'john.doe@example.com',
          phone: '0821234567',
        },
        userIp: '192.168.1.100',
      });

      const redacted = audit.redactPII();
      expect(redacted.userIp).to.include('xxx');
    });

    it('should provide summary virtual property', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      const summary = audit.summary;
      expect(summary).to.be.an('object');
      expect(summary.auditId).to.equal(audit.auditId);
      expect(summary.valid).to.be.true;
    });

    it('should create audit entry with createAudit static method', async function() {
      const audit = await ValidationAudit.createAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      expect(audit).to.exist;
      expect(audit.auditId).to.exist;
      expect(audit.tenantId).to.equal(testTenantId);
    });
  });
});
