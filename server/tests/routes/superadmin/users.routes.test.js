/* eslint-disable */
import { expect } from 'chai';
import request from 'supertest';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import jwt from 'jsonwebtoken';
import app from '../../testApp.js';  // Fixed path: from tests/routes/superadmin/ to tests/

describe('SuperAdmin Users Routes', function() {
  let mongoServer;
  let superAdminToken;
  let regularToken;
  let testUser;

  before(async function() {
    this.timeout(10000);

    mongoServer = await MongoMemoryServer.create();
    const mongoUri = mongoServer.getUri();

    await mongoose.connect(mongoUri);

    process.env.JWT_SECRET = 'test-secret-key';

    const User = (await import('../../../models/User.js')).default;
    const Tenant = (await import('../../../models/Tenant.js')).default;

    const testTenant = await Tenant.create({
      name: 'Test Tenant',
      slug: 'test-tenant',
      subscription: 'enterprise',
      status: 'active'
    });

    const superAdmin = await User.create({
      email: 'super@admin.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'super_admin',
      tenantId: testTenant._id,
      firstName: 'Super',
      lastName: 'Admin',
      isActive: true
    });

    const regularUser = await User.create({
      email: 'regular@user.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'user',
      tenantId: testTenant._id,
      firstName: 'Regular',
      lastName: 'User',
      isActive: true
    });

    testUser = await User.create({
      email: 'test@user.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'user',
      tenantId: testTenant._id,
      firstName: 'Test',
      lastName: 'User',
      isActive: true
    });

    superAdminToken = jwt.sign(
      { id: superAdmin._id.toString(), role: 'super_admin' },
      process.env.JWT_SECRET
    );

    regularToken = jwt.sign(
      { id: regularUser._id.toString(), role: 'user' },
      process.env.JWT_SECRET
    );
  });

  after(async function() {
    await mongoose.disconnect();
    await mongoServer.stop();
  });

  it('should deny access for regular users', async function() {
    await request(app)
      .get('/api/superadmin/users')
      .set('Authorization', `Bearer ${regularToken}`)
      .expect(403);
  });

  it('should allow access for super admin', async function() {
    await request(app)
      .get('/api/superadmin/users')
      .set('Authorization', `Bearer ${superAdminToken}`)
      .expect(200);
  });

  it('should return user by ID', async function() {
    await request(app)
      .get(`/api/superadmin/users/${testUser._id}`)
      .set('Authorization', `Bearer ${superAdminToken}`)
      .expect(200);
  });

  it('should create new user', async function() {
    await request(app)
      .post('/api/superadmin/users')
      .set('Authorization', `Bearer ${superAdminToken}`)
      .send({
        email: 'new@user.com',
        firstName: 'New',
        lastName: 'User',
        role: 'user'
      })
      .expect(201);
  });
});
