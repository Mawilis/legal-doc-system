/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 🧪 TENANT AUDIT LOG MODEL TEST - WILSY OS 2050                            ║
  ║ Validates forensic chain, compliance, and integrity                      ║
  ║ Supreme Architect: Wilson Khanyezi - 10th Generation                     ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

const mongoose = require('mongoose');
const { expect } = require('chai');
const TenantAuditLog = require('../../server/models/TenantAuditLog');

describe('TenantAuditLog Model (Supreme Command Center)', function() {
  before(async function() {
    await mongoose.connect('mongodb://127.0.0.1:27017/wilsy_test', {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });
    await TenantAuditLog.deleteMany({});
  });

  after(async function() {
    await mongoose.connection.close();
  });

  it('should create a new audit log with forensic hash', async function() {
    const log = await TenantAuditLog.create({
      tenantId: new mongoose.Types.ObjectId(),
      action: 'TENANT_CREATED',
      performedBy: new mongoose.Types.ObjectId(),
      metadata: { ipAddress: '127.0.0.1', userAgent: 'MochaTest' }
    });

    expect(log.forensicHash).to.be.a('string');
    expect(log.previousHash).to.equal('GENESIS');
  });

  it('should chain forensic hashes correctly', async function() {
    const tenantId = new mongoose.Types.ObjectId();
    const userId = new mongoose.Types.ObjectId();

    const firstLog = await TenantAuditLog.create({
      tenantId,
      action: 'TENANT_CREATED',
      performedBy: userId,
      metadata: { ipAddress: '127.0.0.1', userAgent: 'MochaTest' }
    });

    const secondLog = await TenantAuditLog.create({
      tenantId,
      action: 'TENANT_UPDATED',
      performedBy: userId,
      metadata: { ipAddress: '127.0.0.1', userAgent: 'MochaTest' }
    });

    expect(secondLog.previousHash).to.equal(firstLog.forensicHash);
  });

  it('should enforce retention period of 7 years', async function() {
    const log = await TenantAuditLog.create({
      tenantId: new mongoose.Types.ObjectId(),
      action: 'TENANT_CREATED',
      performedBy: new mongoose.Types.ObjectId(),
      metadata: { ipAddress: '127.0.0.1', userAgent: 'MochaTest' }
    });

    const now = new Date();
    const diffYears = (log.retentionPeriod.getFullYear() - now.getFullYear());
    expect(diffYears).to.be.at.least(7);
  });

  it('should verify chain integrity using static method', async function() {
    const tenantId = new mongoose.Types.ObjectId();
    const userId = new mongoose.Types.ObjectId();

    await TenantAuditLog.create({
      tenantId,
      action: 'TENANT_CREATED',
      performedBy: userId,
      metadata: { ipAddress: '127.0.0.1', userAgent: 'MochaTest' }
    });

    await TenantAuditLog.create({
      tenantId,
      action: 'TENANT_UPDATED',
      performedBy: userId,
      metadata: { ipAddress: '127.0.0.1', userAgent: 'MochaTest' }
    });

    const isValid = await TenantAuditLog.verifyChain(tenantId);
    expect(isValid).to.be.true;
  });
});
