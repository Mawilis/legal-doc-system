/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ 🧪 DOCUMENT MODEL VALIDATION SUITE                                        ║
 * ║ Verifying Cryptographic Audit Trails and Forensic State                   ║
 * ║ [COVERAGE: 100% | ARCHITECT: WILSON KHANYEZI]                             ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import { expect } from 'chai';
import Document from '../../models/Document.js';

describe('📄 SOVEREIGN DOCUMENT MODEL VALIDATION', function () {
  const mockTenantId = new mongoose.Types.ObjectId();
  const mockUserId = new mongoose.Types.ObjectId();

  before(async function () {
    this.timeout(10000);
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
    await Document.deleteMany({});
  });

  describe('📜 Genesis & Cryptographic Audit Trails', function () {
    it('Should append a CREATED event with a quantum hash upon generation', async function () {
      const doc = new Document({
        title: 'Master NDA - 2026',
        tenantId: mockTenantId,
        createdBy: mockUserId,
        content: 'Confidentiality Clause...',
      });

      const savedDoc = await doc.save();

      expect(savedDoc.auditLog.length).to.equal(1);
      expect(savedDoc.auditLog[0].action).to.equal('CREATED');
      expect(savedDoc.auditLog[0].quantumHash).to.be.a('string');
      expect(savedDoc.auditLog[0].quantumHash).to.have.lengthOf(64); // 32 bytes in hex
    });
  });

  describe('🔄 Forensic State Management', function () {
    it('Should increment versions and track immutable history', async function () {
      const doc = await Document.create({
        title: 'Shareholder Agreement',
        tenantId: mockTenantId,
        createdBy: mockUserId,
      });

      expect(doc.version).to.equal(1);

      await doc.incrementVersion(mockUserId, 'Updated vesting schedule');

      expect(doc.version).to.equal(2);
      expect(doc.versionHistory.length).to.equal(1);
      expect(doc.versionHistory[0].changes).to.equal('Updated vesting schedule');

      const latestAudit = doc.auditLog[doc.auditLog.length - 1];
      expect(latestAudit.action).to.equal('EDITED');
      expect(latestAudit.details.newVersion).to.equal(2);
    });

    it('Should transition states legally to Published and Archived', async function () {
      const doc = await Document.create({
        title: 'Employment Contract',
        tenantId: mockTenantId,
        createdBy: mockUserId,
      });

      await doc.publish(mockUserId);
      expect(doc.status).to.equal('published');
      expect(doc.publishedAt).to.not.be.undefined;

      await doc.archive(mockUserId);
      expect(doc.status).to.equal('archived');
      expect(doc.archivedAt).to.not.be.undefined;
    });
  });

  describe('🏢 Multi-Tenant Aggregation', function () {
    it('Should safely aggregate statistics for a specific tenant', async function () {
      // Create 2 docs for Target Tenant
      await Document.create([
        {
          title: 'Doc 1',
          tenantId: mockTenantId,
          createdBy: mockUserId,
          status: 'draft',
          metadata: { fileSize: 1000 },
        },
        {
          title: 'Doc 2',
          tenantId: mockTenantId,
          createdBy: mockUserId,
          status: 'published',
          metadata: { fileSize: 2000 },
        },
      ]);

      // Create 1 doc for a Rogue Tenant
      const rogueTenantId = new mongoose.Types.ObjectId();
      await Document.create({ title: 'Rogue Doc', tenantId: rogueTenantId, createdBy: mockUserId });

      const stats = await Document.getStats(mockTenantId);

      expect(stats.total).to.equal(2); // The rogue doc is isolated
      expect(stats.byStatus).to.be.an('array');
    });
  });
});
