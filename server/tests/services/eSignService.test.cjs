/* eslint-env mocha */
/* eslint-disable */
const { expect } = require('chai');
const sinon = require('sinon');
const mongoose = require('mongoose');
const crypto = require('crypto');

let ESignService,
  SIGNATURE_STATUS,
  SIGNATURE_TYPES,
  SIGNATURE_PROVIDERS,
  RETENTION_POLICIES,
  VERIFICATION_LEVELS,
  DATA_RESIDENCY;
let ElectronicSignature, DocumentTemplate;
let tenantContext, auditLogger, logger;

before(async () => {
  const eSignModule = await import('../../services/eSignService.js');
  ESignService = eSignModule.ESignService;
  SIGNATURE_STATUS = eSignModule.SIGNATURE_STATUS;
  SIGNATURE_TYPES = eSignModule.SIGNATURE_TYPES;
  SIGNATURE_PROVIDERS = eSignModule.SIGNATURE_PROVIDERS;
  RETENTION_POLICIES = eSignModule.RETENTION_POLICIES;
  VERIFICATION_LEVELS = eSignModule.VERIFICATION_LEVELS;
  DATA_RESIDENCY = eSignModule.DATA_RESIDENCY;

  const electronicSignatureModule = await import('../../models/ElectronicSignature.js');
  ElectronicSignature = electronicSignatureModule.default;

  const documentTemplateModule = await import('../../models/DocumentTemplate.js');
  DocumentTemplate = documentTemplateModule.DocumentTemplate;

  const tenantContextModule = await import('../../middleware/tenantContext.js');
  tenantContext = tenantContextModule;

  const auditLoggerModule = await import('../../utils/auditLogger.js');
  auditLogger = auditLoggerModule.default;

  const loggerModule = await import('../../utils/logger.js');
  logger = loggerModule.default;
});

describe('E-Signature Service - Forensic Test Suite', function () {
  let eSignService;
  let sandbox;
  let testTenantId;
  let testUserId;
  let testDocument;
  let testSigners;

  before(async () => {
    eSignService = new ESignService();
    sandbox = sinon.createSandbox();
    testTenantId = `tenant-${crypto.randomBytes(4).toString('hex')}`;
    testUserId = `user-${crypto.randomBytes(4).toString('hex')}`;
  });

  beforeEach(async () => {
    sandbox.stub(tenantContext, 'getCurrentTenant').returns(testTenantId);
    sandbox.stub(tenantContext, 'getCurrentUser').returns(testUserId);
    sandbox.stub(auditLogger, 'log').resolves();
    sandbox.stub(logger, 'info').returns();
    sandbox.stub(logger, 'error').returns();
    sandbox.stub(logger, 'warn').returns();

    testDocument = await DocumentTemplate.create({
      tenantId: testTenantId,
      name: 'Test Contract',
      templateId: `TMP-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
      templateType: 'contract',
      practiceArea: 'corporate',
      content: { raw: 'Test content', format: 'handlebars' },
      audit: { createdBy: testUserId },
      status: 'active',
    });

    testSigners = [
      { email: 'signer1@example.com', name: 'John Doe', role: 'signer', order: 1 },
      { email: 'signer2@example.com', name: 'Jane Smith', role: 'witness', order: 2 },
    ];
  });

  afterEach(async () => {
    sandbox.restore();
    await ElectronicSignature.deleteMany({});
    await DocumentTemplate.deleteMany({});
  });

  describe('1. SIGNATURE REQUEST CREATION', () => {
    it('should create a signature request with tenant isolation', async () => {
      const result = await eSignService.createSignatureRequest(
        testDocument.templateId,
        testSigners
      );
      expect(result).to.have.property('success', true);
      expect(result).to.have.property('signatureId').that.is.a('string');
      expect(result).to.have.property('status', SIGNATURE_STATUS.PENDING);
    });

    it('should enforce tenant isolation', async () => {
      const result = await eSignService.createSignatureRequest(
        testDocument.templateId,
        testSigners
      );
      sandbox.restore();
      sandbox.stub(tenantContext, 'getCurrentTenant').returns('different-tenant');

      try {
        await eSignService.getSignatureStatus(result.signatureId);
        expect.fail('Should have thrown error');
      } catch (error) {
        expect(error.message).to.include('not found');
      }
    });

    it('should generate forensic hash', async () => {
      const result = await eSignService.createSignatureRequest(
        testDocument.templateId,
        testSigners
      );
      const signature = await ElectronicSignature.findOne({ signatureId: result.signatureId });
      expect(signature.forensicHash).to.exist;
      expect(signature.forensicHash).to.match(/^[a-f0-9]{64}$/);
    });

    it('should set correct retention policy', async () => {
      const result = await eSignService.createSignatureRequest(
        testDocument.templateId,
        testSigners,
        { retentionPolicy: RETENTION_POLICIES.COMPANIES_ACT_7_YEARS }
      );
      const signature = await ElectronicSignature.findOne({ signatureId: result.signatureId });
      expect(signature.retentionPolicy).to.equal(RETENTION_POLICIES.COMPANIES_ACT_7_YEARS);
    });
  });

  describe('2. SIGNATURE PROCESS', () => {
    let signatureId;

    beforeEach(async () => {
      const result = await eSignService.createSignatureRequest(
        testDocument.templateId,
        testSigners
      );
      signatureId = result.signatureId;
    });

    it('should sign a document with proper proof', async () => {
      const result = await eSignService.signDocument(signatureId, { email: testSigners[0].email });
      expect(result).to.have.property('success', true);
      expect(result).to.have.property('signedAt');
      expect(result).to.have.property('status', SIGNATURE_STATUS.SIGNED);
    });

    it('should prevent signing by non-signers', async () => {
      try {
        await eSignService.signDocument(signatureId, { email: 'unauthorized@example.com' });
        expect.fail('Should have thrown error');
      } catch (error) {
        expect(error.message).to.include('not found');
      }
    });
  });

  describe('3. SIGNATURE VERIFICATION', () => {
    let signatureId;

    beforeEach(async () => {
      const result = await eSignService.createSignatureRequest(
        testDocument.templateId,
        testSigners
      );
      signatureId = result.signatureId;
      await eSignService.signDocument(signatureId, { email: testSigners[0].email });
    });

    it('should verify a valid signature', async () => {
      const verification = await eSignService.verifySignature(signatureId);
      expect(verification.verified).to.be.true;
    });

    it('should detect tampered signatures', async () => {
      const signature = await ElectronicSignature.findOne({ signatureId });
      signature.signedBy = 'tampered@example.com';
      await signature.save();

      const verification = await eSignService.verifySignature(signatureId);
      expect(verification.verified).to.be.false;
    });
  });

  describe('4. RETENTION AND POPIA COMPLIANCE', () => {
    it('should include retention metadata', async () => {
      const result = await eSignService.createSignatureRequest(
        testDocument.templateId,
        testSigners
      );
      const signature = await ElectronicSignature.findOne({ signatureId: result.signatureId });
      expect(signature.retentionPolicy).to.exist;
      expect(signature.retentionStart).to.exist;
      expect(signature.retentionEnd).to.exist;
      expect(signature.dataResidency).to.equal(DATA_RESIDENCY.ZA);
    });
  });

  describe('5. SIGNATURE HISTORY', () => {
    it('should maintain complete signature history', async () => {
      const result = await eSignService.createSignatureRequest(
        testDocument.templateId,
        testSigners
      );
      await eSignService.signDocument(result.signatureId, { email: testSigners[0].email });

      const history = await eSignService.getSignatureHistory(result.signatureId);
      expect(history).to.have.property('history').that.is.an('array');
      expect(history.history.length).to.be.at.least(2);
    });
  });

  describe('6. PROVIDER INTEGRATION', () => {
    it('should have configured providers', () => {
      expect(eSignService.providers).to.exist;
      expect(eSignService.providers.size).to.be.greaterThan(0);
    });
  });

  describe('7. HEALTH CHECK', () => {
    it('should return health status', async () => {
      const health = await eSignService.health();
      expect(health).to.have.property('status', 'healthy');
      expect(health).to.have.property('providers').that.is.an('array');
    });
  });
});
