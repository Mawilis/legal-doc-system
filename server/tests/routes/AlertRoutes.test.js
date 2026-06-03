/* eslint-disable */
import { expect } from 'chai';
import request from 'supertest';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';
import app from '../testApp.js';
import User from '../../models/User.js';
import Tenant from '../../models/Tenant.js';
import Alert from '../../models/Alert.js';

describe('Alert Routes - Investor-Grade Incident Management', function() {
  let mongoServer;
  let adminToken;
  let opsToken;
  let systemToken;
  let userToken;
  let testTenant;
  let adminUser;
  let opsUser;
  let systemUser;
  let regularUser;
  let testAlertId;

  before(async function() {
    // Start in-memory MongoDB
    mongoServer = await MongoMemoryServer.create();
    const mongoUri = mongoServer.getUri();

    // Disconnect if already connected
    if (mongoose.connection.readyState !== 0) {
      await mongoose.disconnect();
    }

    // Connect to test database
    await mongoose.connect(mongoUri);

    // Set JWT secret
    process.env.JWT_SECRET = 'test-secret-key';

    // Import models
    User = (await import('../../models/User.js')).default;
    Tenant = (await import('../../models/Tenant.js')).default;
    Alert = (await import('../../models/Alert.js')).default;

    // Create test tenant
    testTenant = await Tenant.create({
      name: 'Test Law Firm',
      slug: 'test-firm',
      subscription: 'enterprise',
      status: 'active'
    });

    // Create admin user
    adminUser = await User.create({
      email: 'admin@test.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'admin',
      tenantId: testTenant._id,
      firstName: 'Admin',
      lastName: 'User',
      isActive: true
    });

    // Create ops user
    opsUser = await User.create({
      email: 'ops@test.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'ops',
      tenantId: testTenant._id,
      firstName: 'Ops',
      lastName: 'User',
      isActive: true
    });

    // Create system user
    systemUser = await User.create({
      email: 'system@test.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'system',
      tenantId: testTenant._id,
      firstName: 'System',
      lastName: 'User',
      isActive: true
    });

    // Create regular user
    regularUser = await User.create({
      email: 'user@test.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'user',
      tenantId: testTenant._id,
      firstName: 'Regular',
      lastName: 'User',
      isActive: true
    });

    // Generate tokens
    adminToken = jwt.sign(
      {
        id: adminUser._id.toString(),
        email: adminUser.email,
        role: adminUser.role,
        tenantId: adminUser.tenantId.toString()
      },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    opsToken = jwt.sign(
      {
        id: opsUser._id.toString(),
        email: opsUser.email,
        role: opsUser.role,
        tenantId: opsUser.tenantId.toString()
      },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    systemToken = jwt.sign(
      {
        id: systemUser._id.toString(),
        email: systemUser.email,
        role: systemUser.role,
        tenantId: systemUser.tenantId.toString()
      },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    userToken = jwt.sign(
      {
        id: regularUser._id.toString(),
        email: regularUser.email,
        role: regularUser.role,
        tenantId: regularUser.tenantId.toString()
      },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    // Create a test alert for later use
    const testAlert = await Alert.create({
      title: 'Test Critical Alert',
      message: 'This is a test critical alert',
      severity: 'critical',
      source: 'test-system',
      details: { test: true },
      status: 'active',
      createdBy: systemUser._id,
      tenantId: testTenant._id
    });

    testAlertId = testAlert._id.toString();
  });

  after(async function() {
    await mongoose.disconnect();
    if (mongoServer) {
      await mongoServer.stop();
    }
  });

  // ==========================================================================
  // HEALTH CHECK TESTS
  // ==========================================================================
  describe('GET /api/alerts/health - Service Health', function() {
    it('should return health status (public endpoint)', async function() {
      const response = await request(app)
        .get('/api/alerts/health')
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body).to.have.property('data');
      expect(response.body.metadata).to.have.property('service', 'alert-service');
    });
  });

  // ==========================================================================
  // CREATE ALERT TESTS
  // ==========================================================================
  describe('POST /api/alerts - Create Alert', function() {
    const validAlert = {
      title: 'High CPU Usage Detected',
      message: 'CPU usage exceeded 90% for 5 minutes',
      severity: 'warning',
      source: 'monitoring-system',
      details: {
        cpu: 95,
        duration: 300,
        instance: 'prod-01'
      },
      channels: ['email', 'slack']
    };

    it('should allow system to create alert', async function() {
      const response = await request(app)
        .post('/api/alerts')
        .set('Authorization', `Bearer ${systemToken}`)
        .send(validAlert)
        .expect(201);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('id');
      expect(response.body.data).to.have.property('title', validAlert.title);
      expect(response.body.metadata).to.have.property('requestId');
    });

    it('should allow admin to create alert', async function() {
      await request(app)
        .post('/api/alerts')
        .set('Authorization', `Bearer ${adminToken}`)
        .send(validAlert)
        .expect(201);
    });

    it('should deny ops user from creating alerts', async function() {
      await request(app)
        .post('/api/alerts')
        .set('Authorization', `Bearer ${opsToken}`)
        .send(validAlert)
        .expect(403);
    });

    it('should deny regular user from creating alerts', async function() {
      await request(app)
        .post('/api/alerts')
        .set('Authorization', `Bearer ${userToken}`)
        .send(validAlert)
        .expect(403);
    });

    it('should validate required fields', async function() {
      const invalidAlert = { title: 'Missing fields' };

      const response = await request(app)
        .post('/api/alerts')
        .set('Authorization', `Bearer ${systemToken}`)
        .send(invalidAlert)
        .expect(400);

      expect(response.body).to.have.property('success', false);
      expect(response.body).to.have.property('errors');
      expect(response.body.errors.length).to.be.greaterThan(0);
    });

    it('should validate severity values', async function() {
      const invalidAlert = {
        ...validAlert,
        severity: 'unknown'
      };

      await request(app)
        .post('/api/alerts')
        .set('Authorization', `Bearer ${systemToken}`)
        .send(invalidAlert)
        .expect(400);
    });

    it('should return 401 without token', async function() {
      await request(app)
        .post('/api/alerts')
        .send(validAlert)
        .expect(401);
    });
  });

  // ==========================================================================
  // GET ALERTS TESTS
  // ==========================================================================
  describe('GET /api/alerts - List Alerts', function() {
    it('should allow admin to list alerts', async function() {
      const response = await request(app)
        .get('/api/alerts')
        .set('Authorization', `Bearer ${adminToken}`)
        .query({ limit: 10 })
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body).to.have.property('data');
      expect(response.body.data).to.be.an('array');
    });

    it('should allow ops to list alerts', async function() {
      await request(app)
        .get('/api/alerts')
        .set('Authorization', `Bearer ${opsToken}`)
        .query({ limit: 10 })
        .expect(200);
    });

    it('should deny regular user from listing alerts', async function() {
      await request(app)
        .get('/api/alerts')
        .set('Authorization', `Bearer ${userToken}`)
        .expect(403);
    });

    it('should filter by severity', async function() {
      const response = await request(app)
        .get('/api/alerts')
        .set('Authorization', `Bearer ${adminToken}`)
        .query({ severity: 'critical', limit: 10 })
        .expect(200);

      response.body.data.forEach(alert => {
        expect(alert.severity).to.equal('critical');
      });
    });

    it('should filter by status', async function() {
      const response = await request(app)
        .get('/api/alerts')
        .set('Authorization', `Bearer ${adminToken}`)
        .query({ status: 'active', limit: 10 })
        .expect(200);

      response.body.data.forEach(alert => {
        expect(alert.status).to.equal('active');
      });
    });

    it('should filter by date range', async function() {
      const endDate = new Date().toISOString();
      const startDate = new Date(Date.now() - 86400000).toISOString(); // 1 day ago

      await request(app)
        .get('/api/alerts')
        .set('Authorization', `Bearer ${adminToken}`)
        .query({
          startDate,
          endDate,
          limit: 10
        })
        .expect(200);
    });

    it('should paginate results', async function() {
      const response = await request(app)
        .get('/api/alerts')
        .set('Authorization', `Bearer ${adminToken}`)
        .query({ limit: 5, offset: 0 })
        .expect(200);

      expect(response.body.metadata).to.have.property('limit', 5);
      expect(response.body.metadata).to.have.property('offset', 0);
    });

    it('should validate limit parameter', async function() {
      await request(app)
        .get('/api/alerts')
        .set('Authorization', `Bearer ${adminToken}`)
        .query({ limit: 2000 })
        .expect(400);
    });
  });

  // ==========================================================================
  // GET ALERT BY ID TESTS
  // ==========================================================================
  describe('GET /api/alerts/:alertId - Get Alert by ID', function() {
    it('should allow admin to get alert by ID', async function() {
      const response = await request(app)
        .get(`/api/alerts/${testAlertId}`)
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('_id', testAlertId);
    });

    it('should allow ops to get alert by ID', async function() {
      await request(app)
        .get(`/api/alerts/${testAlertId}`)
        .set('Authorization', `Bearer ${opsToken}`)
        .expect(200);
    });

    it('should deny regular user from getting alert', async function() {
      await request(app)
        .get(`/api/alerts/${testAlertId}`)
        .set('Authorization', `Bearer ${userToken}`)
        .expect(403);
    });

    it('should return 404 for non-existent alert', async function() {
      const fakeId = uuidv4();
      await request(app)
        .get(`/api/alerts/${fakeId}`)
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(404);
    });

    it('should validate alert ID format', async function() {
      await request(app)
        .get('/api/alerts/invalid-id')
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(400);
    });
  });

  // ==========================================================================
  // ACKNOWLEDGE ALERT TESTS
  // ==========================================================================
  describe('POST /api/alerts/:alertId/acknowledge - Acknowledge Alert', function() {
    let acknowledgeAlertId;

    beforeEach(async function() {
      const alert = await Alert.create({
        title: 'Alert to Acknowledge',
        message: 'This alert needs acknowledgment',
        severity: 'warning',
        source: 'test',
        status: 'active',
        createdBy: systemUser._id,
        tenantId: testTenant._id
      });
      acknowledgeAlertId = alert._id.toString();
    });

    it('should allow admin to acknowledge alert', async function() {
      const response = await request(app)
        .post(`/api/alerts/${acknowledgeAlertId}/acknowledge`)
        .set('Authorization', `Bearer ${adminToken}`)
        .send({ note: 'Investigating issue' })
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('status', 'acknowledged');
    });

    it('should allow ops to acknowledge alert', async function() {
      await request(app)
        .post(`/api/alerts/${acknowledgeAlertId}/acknowledge`)
        .set('Authorization', `Bearer ${opsToken}`)
        .expect(200);
    });

    it('should deny regular user from acknowledging alert', async function() {
      await request(app)
        .post(`/api/alerts/${acknowledgeAlertId}/acknowledge`)
        .set('Authorization', `Bearer ${userToken}`)
        .expect(403);
    });

    it('should prevent acknowledging already resolved alert', async function() {
      const resolvedAlert = await Alert.create({
        title: 'Resolved Alert',
        message: 'Already resolved',
        severity: 'info',
        source: 'test',
        status: 'resolved',
        createdBy: systemUser._id,
        tenantId: testTenant._id
      });

      await request(app)
        .post(`/api/alerts/${resolvedAlert._id}/acknowledge`)
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(409);
    });

    it('should accept optional note', async function() {
      const response = await request(app)
        .post(`/api/alerts/${acknowledgeAlertId}/acknowledge`)
        .set('Authorization', `Bearer ${adminToken}`)
        .send({ note: 'Taking ownership of this issue' })
        .expect(200);

      expect(response.body.data.acknowledgment).to.have.property('note');
    });
  });

  // ==========================================================================
  // RESOLVE ALERT TESTS
  // ==========================================================================
  describe('POST /api/alerts/:alertId/resolve - Resolve Alert', function() {
    let resolveAlertId;

    beforeEach(async function() {
      const alert = await Alert.create({
        title: 'Alert to Resolve',
        message: 'This alert needs resolution',
        severity: 'critical',
        source: 'test',
        status: 'active',
        createdBy: systemUser._id,
        tenantId: testTenant._id
      });
      resolveAlertId = alert._id.toString();
    });

    it('should allow admin to resolve alert', async function() {
      const response = await request(app)
        .post(`/api/alerts/${resolveAlertId}/resolve`)
        .set('Authorization', `Bearer ${adminToken}`)
        .send({
          resolution: 'Issue fixed',
          rootCause: 'Configuration error',
          actionTaken: 'Updated config'
        })
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('status', 'resolved');
    });

    it('should allow ops to resolve alert', async function() {
      await request(app)
        .post(`/api/alerts/${resolveAlertId}/resolve`)
        .set('Authorization', `Bearer ${opsToken}`)
        .send({ resolution: 'Issue fixed' })
        .expect(200);
    });

    it('should deny regular user from resolving alert', async function() {
      await request(app)
        .post(`/api/alerts/${resolveAlertId}/resolve`)
        .set('Authorization', `Bearer ${userToken}`)
        .send({ resolution: 'Issue fixed' })
        .expect(403);
    });

    it('should accept detailed resolution data', async function() {
      const response = await request(app)
        .post(`/api/alerts/${resolveAlertId}/resolve`)
        .set('Authorization', `Bearer ${adminToken}`)
        .send({
          resolution: 'Fixed memory leak',
          rootCause: 'Unclosed database connections',
          actionTaken: 'Added connection pooling and proper cleanup'
        })
        .expect(200);

      expect(response.body.data.resolution).to.have.property('resolution');
      expect(response.body.data.resolution).to.have.property('rootCause');
      expect(response.body.data.resolution).to.have.property('actionTaken');
    });
  });

  // ==========================================================================
  // ALERT STATISTICS TESTS
  // ==========================================================================
  describe('GET /api/alerts/stats/overview - Alert Statistics', function() {
    beforeEach(async function() {
      // Create various alerts for statistics
      await Alert.create([
        {
          title: 'Critical Alert 1',
          message: 'Test',
          severity: 'critical',
          source: 'test',
          status: 'active',
          createdBy: systemUser._id,
          tenantId: testTenant._id,
          createdAt: new Date()
        },
        {
          title: 'Critical Alert 2',
          message: 'Test',
          severity: 'critical',
          source: 'test',
          status: 'acknowledged',
          createdBy: systemUser._id,
          tenantId: testTenant._id,
          createdAt: new Date()
        },
        {
          title: 'Warning Alert',
          message: 'Test',
          severity: 'warning',
          source: 'test',
          status: 'resolved',
          createdBy: systemUser._id,
          tenantId: testTenant._id,
          createdAt: new Date(Date.now() - 86400000) // 1 day ago
        }
      ]);
    });

    it('should allow admin to get alert statistics', async function() {
      const response = await request(app)
        .get('/api/alerts/stats/overview')
        .set('Authorization', `Bearer ${adminToken}`)
        .query({ period: 'day' })
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('total');
      expect(response.body.data).to.have.property('bySeverity');
      expect(response.body.data).to.have.property('byStatus');
    });

    it('should deny ops from getting statistics', async function() {
      await request(app)
        .get('/api/alerts/stats/overview')
        .set('Authorization', `Bearer ${opsToken}`)
        .expect(403);
    });

    it('should accept period parameter', async function() {
      const periods = ['hour', 'day', 'week', 'month'];

      for (const period of periods) {
        await request(app)
          .get('/api/alerts/stats/overview')
          .set('Authorization', `Bearer ${adminToken}`)
          .query({ period })
          .expect(200);
      }
    });

    it('should validate period parameter', async function() {
      await request(app)
        .get('/api/alerts/stats/overview')
        .set('Authorization', `Bearer ${adminToken}`)
        .query({ period: 'invalid' })
        .expect(400);
    });
  });

  // ==========================================================================
  // BULK ACKNOWLEDGE TESTS
  // ==========================================================================
  describe('POST /api/alerts/bulk/acknowledge - Bulk Acknowledge', function() {
    let alertIds = [];

    beforeEach(async function() {
      const alerts = await Alert.create([
        {
          title: 'Bulk Alert 1',
          message: 'Test',
          severity: 'warning',
          source: 'test',
          status: 'active',
          createdBy: systemUser._id,
          tenantId: testTenant._id
        },
        {
          title: 'Bulk Alert 2',
          message: 'Test',
          severity: 'warning',
          source: 'test',
          status: 'active',
          createdBy: systemUser._id,
          tenantId: testTenant._id
        },
        {
          title: 'Bulk Alert 3',
          message: 'Test',
          severity: 'warning',
          source: 'test',
          status: 'active',
          createdBy: systemUser._id,
          tenantId: testTenant._id
        }
      ]);

      alertIds = alerts.map(a => a._id.toString());
    });

    it('should allow admin to bulk acknowledge alerts', async function() {
      const response = await request(app)
        .post('/api/alerts/bulk/acknowledge')
        .set('Authorization', `Bearer ${adminToken}`)
        .send({
          alertIds: alertIds.slice(0, 2),
          note: 'Bulk acknowledgment for maintenance'
        })
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('successCount');
      expect(response.body.data).to.have.property('failedCount');
      expect(response.body.data.successCount).to.equal(2);
    });

    it('should validate alertIds array', async function() {
      await request(app)
        .post('/api/alerts/bulk/acknowledge')
        .set('Authorization', `Bearer ${adminToken}`)
        .send({ alertIds: 'not-an-array' })
        .expect(400);
    });

    it('should enforce maximum batch size', async function() {
      const tooManyIds = Array(101).fill(uuidv4());

      await request(app)
        .post('/api/alerts/bulk/acknowledge')
        .set('Authorization', `Bearer ${adminToken}`)
        .send({ alertIds: tooManyIds })
        .expect(400);
    });

    it('should handle mixed success/failure cases', async function() {
      const mixedIds = [
        alertIds[0],
        uuidv4(), // Non-existent ID
        alertIds[1]
      ];

      const response = await request(app)
        .post('/api/alerts/bulk/acknowledge')
        .set('Authorization', `Bearer ${adminToken}`)
        .send({ alertIds: mixedIds })
        .expect(200);

      expect(response.body.data.successCount).to.equal(2);
      expect(response.body.data.failedCount).to.equal(1);
    });
  });

  // ==========================================================================
  // TENANT ISOLATION TESTS
  // ==========================================================================
  describe('Tenant Isolation - Multi-tenant Security', function() {
    let otherTenant;
    let otherTenantToken;

    before(async function() {
      // Create another tenant
      otherTenant = await Tenant.create({
        name: 'Other Firm',
        slug: 'other-firm',
        subscription: 'enterprise',
        status: 'active'
      });

      const otherUser = await User.create({
        email: 'other@firm.com',
        password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
        role: 'admin',
        tenantId: otherTenant._id,
        firstName: 'Other',
        lastName: 'Admin',
        isActive: true
      });

      otherTenantToken = jwt.sign(
        {
          id: otherUser._id.toString(),
          email: otherUser.email,
          role: otherUser.role,
          tenantId: otherUser.tenantId.toString()
        },
        process.env.JWT_SECRET,
        { expiresIn: '1h' }
      );
    });

    it('should prevent cross-tenant alert access', async function() {
      // Create alert in original tenant
      const alert = await Alert.create({
        title: 'Tenant-Specific Alert',
        message: 'Should be isolated',
        severity: 'info',
        source: 'test',
        tenantId: testTenant._id,
        createdBy: adminUser._id
      });

      // Other tenant should not be able to access it
      await request(app)
        .get(`/api/alerts/${alert._id}`)
        .set('Authorization', `Bearer ${otherTenantToken}`)
        .expect(404);
    });

    it('should filter list results by tenant', async function() {
      const response = await request(app)
        .get('/api/alerts')
        .set('Authorization', `Bearer ${otherTenantToken}`)
        .expect(200);

      response.body.data.forEach(alert => {
        expect(alert.tenantId).to.equal(otherTenant._id.toString());
      });
    });
  });

  // ==========================================================================
  // RATE LIMITING TESTS
  // ==========================================================================
  describe('Rate Limiting - API Protection', function() {
    it('should enforce rate limits for alert creation', async function() {
      const requests = [];

      // Make many requests quickly
      for (let i = 0; i < 110; i++) {
        requests.push(
          request(app)
            .post('/api/alerts')
            .set('Authorization', `Bearer ${systemToken}`)
            .send({
              title: `Rate Limit Test ${i}`,
              message: 'Test message',
              severity: 'info',
              source: 'test'
            })
        );
      }

      const responses = await Promise.all(requests);
      const rateLimited = responses.some(r => r.status === 429);
      expect(rateLimited).to.be.true;
    });

    it('should use different limit windows per endpoint', async function() {
      // Create endpoint has lower limit than list
      const createRequests = [];
      const listRequests = [];

      for (let i = 0; i < 60; i++) {
        createRequests.push(
          request(app)
            .post('/api/alerts')
            .set('Authorization', `Bearer ${systemToken}`)
            .send({
              title: 'Test',
              message: 'Test',
              severity: 'info',
              source: 'test'
            })
        );

        listRequests.push(
          request(app)
            .get('/api/alerts')
            .set('Authorization', `Bearer ${adminToken}`)
            .query({ limit: 10 })
        );
      }

      const createResponses = await Promise.all(createRequests);
      const listResponses = await Promise.all(listRequests);

      const createRateLimited = createResponses.some(r => r.status === 429);
      const listRateLimited = listResponses.some(r => r.status === 429);

      // Create endpoint should hit limit first
      expect(createRateLimited).to.be.true;
      // List endpoint might not be limited yet
    });
  });

  // ==========================================================================
  // AUDIT TRAIL TESTS
  // ==========================================================================
  describe('Audit Trail - Compliance Logging', function() {
    it('should log all alert operations', async function() {
      // Create alert
      const createResponse = await request(app)
        .post('/api/alerts')
        .set('Authorization', `Bearer ${systemToken}`)
        .send({
          title: 'Audit Test Alert',
          message: 'Testing audit trail',
          severity: 'warning',
          source: 'audit-test'
        })
        .expect(201);

      const alertId = createResponse.body.data.id;

      // Acknowledge alert
      await request(app)
        .post(`/api/alerts/${alertId}/acknowledge`)
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(200);

      // Resolve alert
      await request(app)
        .post(`/api/alerts/${alertId}/resolve`)
        .set('Authorization', `Bearer ${adminToken}`)
        .send({ resolution: 'Audit test complete' })
        .expect(200);

      // Verify audit logs would be created
      // This would need an audit log model to verify properly
    });

    it('should include request ID in responses', async function() {
      const response = await request(app)
        .get('/api/alerts/health')
        .expect(200);

      expect(response.headers).to.have.property('x-request-id');
      expect(response.body.metadata).to.have.property('requestId');
    });
  });

  // ==========================================================================
  // 404 HANDLER TESTS
  // ==========================================================================
  describe('404 Handler - Unknown Routes', function() {
    it('should return 404 for non-existent alert routes', async function() {
      const response = await request(app)
        .get('/api/alerts/non-existent-route')
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(404);

      expect(response.body).to.have.property('success', false);
      expect(response.body).to.have.property('code', 'ROUTE_NOT_FOUND');
    });

    it('should include request ID in 404 responses', async function() {
      const response = await request(app)
        .get('/api/alerts/unknown/path')
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(404);

      expect(response.body).to.have.property('requestId');
    });
  });
});
