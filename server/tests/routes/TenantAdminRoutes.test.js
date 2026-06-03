/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 🧪 TENANT ADMIN ROUTES TEST - WILSY OS 2050                               ║
  ║ Validates tenant admin API endpoints, validation, and compliance          ║
  ║ Supreme Architect: Wilson Khanyezi - 10th Generation                      ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

const mongoose = require('mongoose');
const { expect } = require('chai');
const request = require('supertest');
const app = require('../../server'); // Express app entry
const User = require('../../server/models/User');
const TenantAuditLog = require('../../server/models/TenantAuditLog');

describe('TenantAdminRoutes (Supreme Command Center)', function() {
  let agent;
  let tenantId;
  let adminToken;

  before(async function() {
    await mongoose.connect('mongodb://127.0.0.1:27017/wilsy_test', {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });
    await User.deleteMany({});
    await TenantAuditLog.deleteMany({});
    tenantId = new mongoose.Types.ObjectId();
    adminToken = 'mocked-jwt-token'; // replace with real JWT in integration
    agent = request(app);
  });

  after(async function() {
    await mongoose.connection.close();
  });

  it('GET /dashboard should return tenant stats', async function() {
    const res = await agent
      .get('/api/tenant-admin/dashboard')
      .set('Authorization', `Bearer ${adminToken}`);
    expect(res.status).to.equal(200);
    expect(res.body.success).to.be.true;
    expect(res.body.data.stats).to.have.keys(['totalUsers','activeUsers','pendingInvitations','activePercentage']);
  });

  it('POST /users should validate input', async function() {
    const res = await agent
      .post('/api/tenant-admin/users')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({ email: 'not-an-email', name: '', role: 'invalid' });
    expect(res.status).to.equal(400);
    expect(res.body.success).to.be.false;
    expect(res.body.errors).to.be.an('array');
  });

  it('POST /users should create invitation and log audit', async function() {
    const res = await agent
      .post('/api/tenant-admin/users')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({ email: 'newuser@wilsy.co.za', name: 'New User', role: 'USER_VIEWER', sendInvite: true });
    expect(res.status).to.equal(201);
    expect(res.body.success).to.be.true;

    const log = await TenantAuditLog.findOne({ action: 'USER_INVITED' });
    expect(log).to.exist;
    expect(log.complianceTags).to.include('POPIA');
  });

  it('PUT /users/:id should update user and log audit', async function() {
    const user = await User.create({ email: 'update@wilsy.co.za', name: 'Update Me', role: 'USER_VIEWER', tenantId });
    const res = await agent
      .put(`/api/tenant-admin/users/${user._id}`)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({ name: 'Updated Name' });
    expect(res.status).to.equal(200);
    expect(res.body.success).to.be.true;

    const log = await TenantAuditLog.findOne({ action: 'USER_UPDATED', targetUser: user._id });
    expect(log).to.exist;
    expect(log.changes.after.name).to.equal('Updated Name');
  });

  it('DELETE /users/:id should deactivate user and log audit', async function() {
    const user = await User.create({ email: 'delete@wilsy.co.za', name: 'Delete Me', role: 'USER_VIEWER', tenantId });
    const res = await agent
      .delete(`/api/tenant-admin/users/${user._id}`)
      .set('Authorization', `Bearer ${adminToken}`);
    expect(res.status).to.equal(200);
    expect(res.body.success).to.be.true;

    const log = await TenantAuditLog.findOne({ action: 'USER_REMOVED', targetUser: user._id });
    expect(log).to.exist;
    expect(log.changes.before.email).to.equal('delete@wilsy.co.za');
  });

  it('GET /audit/verify should validate forensic chain', async function() {
    const res = await agent
      .get('/api/tenant-admin/audit/verify')
      .set('Authorization', `Bearer ${adminToken}`);
    expect(res.status).to.equal(200);
    expect(res.body.success).to.be.true;
    expect(res.body.data).to.have.property('isValid');
  });
});
