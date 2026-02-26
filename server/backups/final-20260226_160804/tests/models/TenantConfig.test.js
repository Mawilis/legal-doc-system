/* eslint-disable */
/* eslint-disable */
import { expect } from "chai";
import mongoose from "mongoose";
import TenantConfig, { TENANT_STATUS, DATA_RESIDENCY } from '../../models/TenantConfig.js';
describe('TenantConfig Model - Multi-Tenant Configuration', function() {
  const testTenantId = 'test-tenant-12345678';

  before(async () => {
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/legal_doc_test');
    }
    await TenantConfig.deleteMany({});
  });

  after(async () => {
    await TenantConfig.deleteMany({});
  });

  beforeEach(async () => {
    await TenantConfig.deleteMany({});
  });

  describe('🏗️ Tenant Provisioning', function() {
    it('should create a valid tenant with minimal fields', async function() {
      const tenant = new TenantConfig({
        tenantId: testTenantId,
        name: 'Test Law Firm',
        contactEmail: 'info@testlaw.co.za',
      });

      const saved = await tenant.save();
      expect(saved.tenantId).to.equal(testTenantId);
      expect(saved.name).to.equal('Test Law Firm');
      expect(saved.contactEmail).to.equal('info@testlaw.co.za');
      expect(saved.status).to.equal(TENANT_STATUS.ACTIVE);
    });

    it('should require a unique tenantId', async function() {
      const tenant1 = new TenantConfig({
        tenantId: testTenantId,
        name: 'Firm 1',
        contactEmail: 'firm1@test.com',
      });
      await tenant1.save();

      const tenant2 = new TenantConfig({
        tenantId: testTenantId,
        name: 'Firm 2',
        contactEmail: 'firm2@test.com',
      });

      try {
        await tenant2.save();
        assert.fail('Should have thrown duplicate key error');
      } catch (error) {
        expect(error.code).to.equal(11000); // MongoDB duplicate key error
      }
    });
  });

  describe('🔐 Security & API Management', function() {
    it('should find tenant by API key via static method', async function() {
      const apiKey = 'test-api-key-12345';

      const tenant = new TenantConfig({
        tenantId: testTenantId,
        name: 'Test Law Firm',
        contactEmail: 'info@testlaw.co.za',
        apiConfig: {
          apiKeys: [
            {
              keyId: 'key-123',
              keyHash: apiKey,
              name: 'Test Key',
            },
          ],
        },
      });
      await tenant.save();

      const found = await TenantConfig.findByApiKey(apiKey);
      expect(found).to.not.be.null;
      expect(found.tenantId).to.equal(testTenantId);
    });

    it('should validate IP whitelist correctly', async function() {
      const tenant = new TenantConfig({
        tenantId: testTenantId,
        name: 'Test Law Firm',
        contactEmail: 'info@testlaw.co.za',
        securitySettings: {
          ipWhitelist: ['192.168.1.1', '10.0.0.1'],
        },
      });

      expect(tenant.isIpAllowed('192.168.1.1')).to.be.true;
      expect(tenant.isIpAllowed('10.0.0.1')).to.be.true;
      expect(tenant.isIpAllowed('192.168.1.2')).to.be.false;
    });
  });

  describe('⚖️ Compliance & Residency', function() {
    it('should enforce default data residency (ZA)', async function() {
      const tenant = new TenantConfig({
        tenantId: testTenantId,
        name: 'Test Law Firm',
        contactEmail: 'info@testlaw.co.za',
      });

      expect(tenant.dataResidency.primary).to.equal(DATA_RESIDENCY.ZA);
      expect(tenant.dataResidency.backup).to.equal(DATA_RESIDENCY.ZA);
      expect(tenant.dataResidency.processing).to.be.an('array').that.includes(DATA_RESIDENCY.ZA);
    });

    it('should correctly store POPIA compliance settings', async function() {
      const tenant = new TenantConfig({
        tenantId: testTenantId,
        name: 'Test Law Firm',
        contactEmail: 'info@testlaw.co.za',
        complianceSettings: {
          popia: {
            enabled: true,
            piiRedaction: true,
            dataSubjectRights: true,
            breachNotification: true,
          },
        },
      });

      expect(tenant.complianceSettings.popia.enabled).to.be.true;
      expect(tenant.complianceSettings.popia.piiRedaction).to.be.true;
      expect(tenant.complianceSettings.popia.dataSubjectRights).to.be.true;
      expect(tenant.complianceSettings.popia.breachNotification).to.be.true;
    });
  });
});
