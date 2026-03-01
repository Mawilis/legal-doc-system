#!/* eslint-env mocha */
/* eslint-disable no-undef, no-unused-expressions */

import mongoose from 'mongoose';
import { expect } from 'chai';
import crypto from 'crypto';
import RetentionPolicy from '../../models/RetentionPolicy.js.js';

describe('RetentionPolicy Model', function() {
  this.timeout(10000);
  
  const testTenantId = 'test-tenant-12345678';
  const testUserId = 'test-user-87654321';

  const validPolicyData = {
    policyName: 'Standard Litigation Retention',
    description: 'Standard 7-year retention for litigation matters',
    matterType: 'litigation',
    tenantId: testTenantId,
    retentionYears: 7,
    legalBasis: 'COMPANIES_ACT_24',
    legalReference: 'Companies Act 71 of 2008 §24',
    jurisdiction: 'ZA',
    createdBy: testUserId
  };

  before(async function() {
    // Connect to test database
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect('mongodb://localhost:27017/wilsy_test', {
        useNewUrlParser: true,
        useUnifiedTopology: true
      });
    }
  });

  after(async function() {
    // Clean up
    await mongoose.connection.dropDatabase();
    await mongoose.disconnect();
  });

  beforeEach(async function() {
    await RetentionPolicy.deleteMany({});
  });

  describe('Schema Validation', function() {
    it('should create valid policy', async function() {
      const policy = new RetentionPolicy(validPolicyData);
      const saved = await policy.save();
      
      expect(saved).to.have.property('policyId');
      expect(saved.policyName).to.equal(validPolicyData.policyName);
      expect(saved.retentionYears).to.equal(7);
      expect(saved.forensicHash).to.be.a('string').with.length(64);
    });

    it('should require policy name', async function() {
      const invalidData = { ...validPolicyData, policyName: undefined };
      const policy = new RetentionPolicy(invalidData);
      
      try {
        await policy.save();
        assert.fail('Should have thrown validation error');
      } catch (error) {
        expect(error.errors.policyName).to.exist;
      }
    });

    it('should require tenant ID', async function() {
      const invalidData = { ...validPolicyData, tenantId: undefined };
      const policy = new RetentionPolicy(invalidData);
      
      try {
        await policy.save();
        assert.fail('Should have thrown validation error');
      } catch (error) {
        expect(error.errors.tenantId).to.exist;
      }
    });

    it('should validate tenant ID format', async function() {
      const invalidData = { ...validPolicyData, tenantId: 'invalid' };
      const policy = new RetentionPolicy(invalidData);
      
      try {
        await policy.save();
        assert.fail('Should have thrown validation error');
      } catch (error) {
        expect(error.errors.tenantId).to.exist;
      }
    });

    it('should validate matter type enum', async function() {
      const invalidData = { ...validPolicyData, matterType: 'invalid' };
      const policy = new RetentionPolicy(invalidData);
      
      try {
        await policy.save();
        assert.fail('Should have thrown validation error');
      } catch (error) {
        expect(error.errors.matterType).to.exist;
      }
    });
  });

  describe('Retention Calculations', function() {
    it('should calculate retention end date correctly', function() {
      const policy = new RetentionPolicy(validPolicyData);
      const startDate = new Date('2026-01-01');
      const endDate = policy.calculateRetentionEndDate(startDate);
      
      expect(endDate.getFullYear()).to.equal(2033); // 2026 + 7 years
    });

    it('should handle months and days', function() {
      const policy = new RetentionPolicy({
        ...validPolicyData,
        retentionYears: 1,
        retentionMonths: 6,
        retentionDays: 15
      });
      
      const startDate = new Date('2026-01-01');
      const endDate = policy.calculateRetentionEndDate(startDate);
      
      expect(endDate.getFullYear()).to.equal(2027);
      expect(endDate.getMonth()).to.equal(6); // July (0-indexed)
      expect(endDate.getDate()).to.equal(16); // +15 days from 1st
    });

    it('should return retention in days virtual', function() {
      const policy = new RetentionPolicy({
        ...validPolicyData,
        retentionYears: 2,
        retentionMonths: 3,
        retentionDays: 10
      });
      
      // 2*365 + 3*30 + 10 = 730 + 90 + 10 = 830
      expect(policy.retentionInDays).to.equal(830);
    });
  });

  describe('Forensic Integrity', function() {
    it('should generate forensic hash on save', async function() {
      const policy = new RetentionPolicy(validPolicyData);
      const saved = await policy.save();
      
      expect(saved.forensicHash).to.be.a('string').with.length(64);
    });

    it('should link versions with hash chain', async function() {
      const policy = new RetentionPolicy(validPolicyData);
      const v1 = await policy.save();
      
      const v2 = await v1.createNewVersion(
        { policyName: 'Updated Litigation Policy' },
        testUserId
      );
      
      expect(v2.previousHash).to.equal(v1.forensicHash);
      expect(v2.version).to.equal(2);
    });

    it('should verify integrity', async function() {
      const policy = new RetentionPolicy(validPolicyData);
      const saved = await policy.save();
      
      expect(saved.verifyIntegrity()).to.be.true;
    });

    it('should detect tampering', async function() {
      const policy = new RetentionPolicy(validPolicyData);
      const saved = await policy.save();
      
      // Tamper with data
      saved.policyName = 'Tampered Name';
      
      expect(saved.verifyIntegrity()).to.be.false;
    });
  });

  describe('Static Methods', function() {
    it('getActivePolicy should return active policy', async function() {
      const policy = new RetentionPolicy(validPolicyData);
      await policy.save();
      
      const active = await RetentionPolicy.getActivePolicy(
        testTenantId,
        'litigation'
      );
      
      expect(active).to.exist;
      expect(active.policyName).to.equal(validPolicyData.policyName);
    });

    it('getDefaultPolicy should return default policy', async function() {
      const policy = new RetentionPolicy({
        ...validPolicyData,
        isDefault: true
      });
      await policy.save();
      
      const defaultPolicy = await RetentionPolicy.getDefaultPolicy(testTenantId);
      
      expect(defaultPolicy).to.exist;
      expect(defaultPolicy.isDefault).to.be.true;
    });

    it('getExpiringPolicies should return policies needing review', async function() {
      const pastReview = new RetentionPolicy({
        ...validPolicyData,
        reviewDate: new Date(Date.now() - 86400000) // Yesterday
      });
      await pastReview.save();
      
      const expiring = await RetentionPolicy.getExpiringPolicies(testTenantId, 30);
      
      expect(expiring.length).to.be.greaterThan(0);
    });
  });

  describe('Compliance Report', function() {
    it('should generate compliance report', async function() {
      await new RetentionPolicy(validPolicyData).save();
      
      const report = await RetentionPolicy.getComplianceReport(testTenantId);
      
      expect(report.totalPolicies).to.equal(1);
      expect(report.activePolicies).to.equal(1);
      expect(report.byMatterType.litigation).to.equal(1);
      expect(report.byJurisdiction.ZA).to.equal(1);
    });
  });

  describe('Error Handling', function() {
    it('should handle duplicate policy names gracefully', async function() {
      const policy1 = new RetentionPolicy(validPolicyData);
      await policy1.save();
      
      const policy2 = new RetentionPolicy(validPolicyData);
      try {
        await policy2.save();
        assert.fail('Should have thrown duplicate key error');
      } catch (error) {
        expect(error.code).to.equal(11000); // Duplicate key error code
      }
    });
  });
});
