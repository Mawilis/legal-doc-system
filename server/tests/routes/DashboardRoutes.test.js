/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 🧪 DASHBOARD ROUTES TESTS - WILSY OS 2050                                 ║
  ║ Validates dashboard endpoints with JWT auth                               ║
  ║ Supreme Architect: Wilson Khanyezi - 10th Generation                      ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { expect } from 'chai';
import request from 'supertest';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import jwt from 'jsonwebtoken';
import { ROLES } from '../../constants/roles.js';
import app from '../testApp.js';

let User, Tenant, Document;

describe('Dashboard Routes - 2050 Analytics & Metrics', function() {
  let mongoServer;
  let testTenant;
  let testUser;
  let authToken;

  before(async function() {
    mongoServer = await MongoMemoryServer.create();
    const mongoUri = mongoServer.getUri();

    if (mongoose.connection.readyState !== 0) {
      await mongoose.disconnect();
    }
    await mongoose.connect(mongoUri);

    process.env.JWT_SECRET = 'test-secret-key';

    User = (await import('../../models/User.js')).default;
    Tenant = (await import('../../models/Tenant.js')).default;
    Document = (await import('../../models/Document.js')).default;

    testTenant = await Tenant.create({
      name: 'Test Tenant',
      slug: 'test-tenant',
      subscription: 'enterprise',
      status: 'active'
    });

    testUser = await User.create({
      email: 'admin@test.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: ROLES.TENANT_ADMIN,
      tenantId: testTenant._id,
      firstName: 'Test',
      lastName: 'Admin',
      isActive: true
    });

    authToken = jwt.sign(
      {
        id: testUser._id.toString(),
        email: testUser.email,
        role: testUser.role,
        tenantId: testUser.tenantId.toString()
      },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );
  });

  after(async function() {
    await mongoose.disconnect();
    if (mongoServer) await mongoServer.stop();
  });

  beforeEach(async function() {
    if (Document) await Document.deleteMany({});
  });

  describe('GET /api/dashboard/metrics', function() {
    it('should return dashboard metrics for authenticated user', async function() {
      await Document.create([
        { title: 'Doc 1', tenantId: testTenant._id, createdBy: testUser._id, status: 'published', createdAt: new Date() },
        { title: 'Doc 2', tenantId: testTenant._id, createdBy: testUser._id, status: 'draft', createdAt: new Date() },
        { title: 'Doc 3', tenantId: testTenant._id, createdBy: testUser._id, status: 'published', createdAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000) }
      ]);

      const response = await request(app)
        .get('/api/dashboard/metrics')
        .set('Authorization', `Bearer ${authToken}`)
        .set('x-tenant-id', testTenant._id.toString())
        .expect(200);

      expect(response.body.success).to.be.true;
      expect(response.body.data.totalDocuments).to.equal(3);
    });

    it('should return 401 without auth token', async function() {
      await request(app)
        .get('/api/dashboard/metrics')
        .set('x-tenant-id', testTenant._id.toString())
        .expect(401);
    });
  });

  describe('Error Handling', function() {
    it('should handle expired tokens', async function() {
      const expiredToken = jwt.sign(
        { id: testUser._id.toString() },
        process.env.JWT_SECRET,
        { expiresIn: '0s' }
      );

      const res = await request(app)
        .get('/api/dashboard/metrics')
        .set('Authorization', `Bearer ${expiredToken}`)
        .set('x-tenant-id', testTenant._id.toString())
        .expect(401);

      expect(res.body.success).to.be.false;
      expect(res.body.message).to.equal('Token expired');
    });

    it('should handle malformed tokens', async function() {
      const res = await request(app)
        .get('/api/dashboard/metrics')
        .set('Authorization', 'Bearer malformed.token.here')
        .set('x-tenant-id', testTenant._id.toString())
        .expect(401);

      expect(res.body.success).to.be.false;
      expect(res.body.message).to.equal('Invalid token');
    });
  });
});
