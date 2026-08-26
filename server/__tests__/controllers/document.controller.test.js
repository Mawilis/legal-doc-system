/* eslint-disable */
import mongoose from 'mongoose';
import { expect } from 'chai';
import documentController from '../../controllers/documentController.js';
import Document from '../../models/Document.js';

const mockResponse = () => {
  const res = { statusCode: 200, body: null };
  res.status = function (s) {
    this.statusCode = s;
    return this;
  };
  res.json = function (d) {
    this.body = d;
    return this;
  };
  return res;
};

describe('📄 SOVEREIGN DOCUMENT CONTROLLER', function () {
  const mockTenantId = new mongoose.Types.ObjectId();
  const mockUserId = new mongoose.Types.ObjectId();

  before(async function () {
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect('mongodb://127.0.0.1:27017/wilsy_os_test_db');
    }
  });

  after(async function () {
    await mongoose.connection.db.dropDatabase();
    await mongoose.connection.close();
  });

  beforeEach(async () => await Document.deleteMany({}));

  it('Should forge a document artifact with quantum encryption metadata', async function () {
    const req = {
      tenantId: mockTenantId,
      user: { id: mockUserId },
      body: { title: 'NDA', classification: 'QUANTUM' },
      file: { size: 100, mimetype: 'text/plain', originalname: 'a.txt' },
    };
    const res = mockResponse();
    await documentController.uploadDocument(req, res);
    expect(res.statusCode).to.equal(201);
  });

  it('Should retrieve a document and trigger view audit', async function () {
    const doc = await Document.create({
      title: 'Secret',
      tenantId: mockTenantId,
      createdBy: mockUserId,
    });
    const req = {
      tenantId: mockTenantId,
      user: { id: mockUserId },
      params: { documentId: doc._id },
      get: () => 'Test',
    };
    const res = mockResponse();
    await documentController.getDocument(req, res);
    const updated = await Document.findById(doc._id);
    expect(updated.accessCount).to.equal(1);
  });

  it('Should return isolated documents for the specific tenant', async function () {
    await Document.create({ title: 'Doc A', tenantId: mockTenantId, createdBy: mockUserId });
    await Document.create({
      title: 'Doc B',
      tenantId: new mongoose.Types.ObjectId(),
      createdBy: mockUserId,
    });
    const req = { tenantId: mockTenantId, query: { limit: 10 } };
    const res = mockResponse();
    await documentController.searchDocuments(req, res);
    expect(res.body.data.pagination.total).to.equal(1);
  });
});
