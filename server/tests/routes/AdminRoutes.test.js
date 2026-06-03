/* eslint-disable */
import { expect } from 'chai';
import request from 'supertest';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import jwt from 'jsonwebtoken';
import app from '../testApp.js';
import User from '../../models/User.js';
import Tenant from '../../models/Tenant.js';
import { ROLES } from '../../constants/roles.js';

describe('Admin Routes - Sovereign Control Plane', function() {
  let mongoServer;
  let superAdminToken;
  let globalAdminToken;
  let complianceAdminToken;
  let securityAdminToken;
  let regularUserToken;
  let testTenant;
  let superAdmin;
  let globalAdmin;
  let complianceAdmin;
  let securityAdmin;
  let regularUser;

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

    // Create a test tenant
    testTenant = await Tenant.create({
      name: 'Acme Corp',
      slug: 'acme-corp',
      subscription: 'enterprise',
      status: 'active'
    });

    // Create SUPER_ADMIN user (Gen 1)
    superAdmin = await User.create({
      email: 'superadmin@wilsyos.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'SUPER_ADMIN',
      tenantId: testTenant._id,
      firstName: 'Super',
      lastName: 'Admin',
      isActive: true
    });

    // Create GLOBAL_ADMIN user (Gen 2)
    globalAdmin = await User.create({
      email: 'globaladmin@wilsyos.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'GLOBAL_ADMIN',
      tenantId: testTenant._id,
      firstName: 'Global',
      lastName: 'Admin',
      isActive: true
    });

    // Create COMPLIANCE_ADMIN user (Gen 3)
    complianceAdmin = await User.create({
      email: 'compliance@wilsyos.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'COMPLIANCE_ADMIN',
      tenantId: testTenant._id,
      firstName: 'Compliance',
      lastName: 'Admin',
      isActive: true
    });

    // Create SECURITY_ADMIN user (Gen 4)
    securityAdmin = await User.create({
      email: 'security@wilsyos.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'SECURITY_ADMIN',
      tenantId: testTenant._id,
      firstName: 'Security',
      lastName: 'Admin',
      isActive: true
    });

    // Create regular user
    regularUser = await User.create({
      email: 'user@acme.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4p7Q1Q8qjK',
      role: 'USER_VIEWER',
      tenantId: testTenant._id,
      firstName: 'Regular',
      lastName: 'User',
      isActive: true
    });

    // Generate tokens
    superAdminToken = jwt.sign(
      {
        id: superAdmin._id.toString(),
        email: superAdmin.email,
        role: superAdmin.role,
        tenantId: superAdmin.tenantId.toString()
      },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    globalAdminToken = jwt.sign(
      {
        id: globalAdmin._id.toString(),
        email: globalAdmin.email,
        role: globalAdmin.role,
        tenantId: globalAdmin.tenantId.toString()
      },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    complianceAdminToken = jwt.sign(
      {
        id: complianceAdmin._id.toString(),
        email: complianceAdmin.email,
        role: complianceAdmin.role,
        tenantId: complianceAdmin.tenantId.toString()
      },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    securityAdminToken = jwt.sign(
      {
        id: securityAdmin._id.toString(),
        email: securityAdmin.email,
        role: securityAdmin.role,
        tenantId: securityAdmin.tenantId.toString()
      },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    regularUserToken = jwt.sign(
      {
        id: regularUser._id.toString(),
        email: regularUser.email,
        role: regularUser.role,
        tenantId: regularUser.tenantId.toString()
      },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );
  });

  after(async function() {
    await mongoose.disconnect();
    if (mongoServer) {
      await mongoServer.stop();
    }
  });

  // ===========================================================================
  // 1. DASHBOARD INTELLIGENCE TESTS
  // ===========================================================================
  describe('Dashboard Intelligence - Sovereign Command Center', function() {
    describe('GET /api/admin/dashboard/stats', function() {
      it('should allow SUPER_ADMIN to access dashboard stats', async function() {
        const response = await request(app)
          .get('/api/admin/dashboard/stats')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);

        expect(response.body).to.have.property('status', 'success');
      });

      it('should allow GLOBAL_ADMIN to access dashboard stats', async function() {
        const response = await request(app)
          .get('/api/admin/dashboard/stats')
          .set('Authorization', `Bearer ${globalAdminToken}`)
          .expect(200);

        expect(response.body).to.have.property('status', 'success');
      });

      it('should deny COMPLIANCE_ADMIN access to dashboard stats', async function() {
        await request(app)
          .get('/api/admin/dashboard/stats')
          .set('Authorization', `Bearer ${complianceAdminToken}`)
          .expect(403);
      });

      it('should deny regular user access to dashboard stats', async function() {
        await request(app)
          .get('/api/admin/dashboard/stats')
          .set('Authorization', `Bearer ${regularUserToken}`)
          .expect(403);
      });

      it('should return 401 without token', async function() {
        await request(app)
          .get('/api/admin/dashboard/stats')
          .expect(401);
      });
    });

    describe('GET /api/admin/dashboard/health', function() {
      it('should allow SUPER_ADMIN to access system health', async function() {
        const response = await request(app)
          .get('/api/admin/dashboard/health')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);

        expect(response.body).to.have.property('status', 'success');
      });

      it('should allow GLOBAL_ADMIN to access system health', async function() {
        await request(app)
          .get('/api/admin/dashboard/health')
          .set('Authorization', `Bearer ${globalAdminToken}`)
          .expect(200);
      });

      it('should deny SECURITY_ADMIN access to system health', async function() {
        await request(app)
          .get('/api/admin/dashboard/health')
          .set('Authorization', `Bearer ${securityAdminToken}`)
          .expect(403);
      });
    });

    describe('GET /api/admin/dashboard/billing', function() {
      it('should allow SUPER_ADMIN to access billing analytics', async function() {
        await request(app)
          .get('/api/admin/dashboard/billing')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);
      });

      it('should allow GLOBAL_ADMIN to access billing analytics', async function() {
        await request(app)
          .get('/api/admin/dashboard/billing')
          .set('Authorization', `Bearer ${globalAdminToken}`)
          .expect(200);
      });
    });
  });

  // ===========================================================================
  // 2. FORENSIC AUDIT LENS TESTS
  // ===========================================================================
  describe('Forensic Audit Lens - Sovereign Transparency', function() {
    describe('GET /api/admin/audits', function() {
      it('should allow SUPER_ADMIN to access system audits', async function() {
        await request(app)
          .get('/api/admin/audits')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);
      });

      it('should allow COMPLIANCE_ADMIN to access system audits', async function() {
        await request(app)
          .get('/api/admin/audits')
          .set('Authorization', `Bearer ${complianceAdminToken}`)
          .expect(200);
      });

      it('should deny GLOBAL_ADMIN access to system audits', async function() {
        await request(app)
          .get('/api/admin/audits')
          .set('Authorization', `Bearer ${globalAdminToken}`)
          .expect(403);
      });

      it('should validate query parameters', async function() {
        await request(app)
          .get('/api/admin/audits')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .query({ limit: 10, severity: 'critical' })
          .expect(200);
      });

      it('should reject invalid limit parameter', async function() {
        await request(app)
          .get('/api/admin/audits')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .query({ limit: 10000 })
          .expect(400);
      });
    });

    describe('GET /api/admin/audits/export', function() {
      it('should allow SUPER_ADMIN to export audit reports', async function() {
        await request(app)
          .get('/api/admin/audits/export')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .query({
            format: 'pdf',
            startDate: '2024-01-01T00:00:00Z',
            endDate: '2024-12-31T23:59:59Z'
          })
          .expect(200);
      });

      it('should reject invalid format parameter', async function() {
        await request(app)
          .get('/api/admin/audits/export')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .query({
            format: 'invalid',
            startDate: '2024-01-01T00:00:00Z',
            endDate: '2024-12-31T23:59:59Z'
          })
          .expect(400);
      });
    });
  });

  // ===========================================================================
  // 3. TENANT GOVERNANCE TESTS
  // ===========================================================================
  describe('Tenant Governance - Ecosystem Management', function() {
    describe('GET /api/admin/tenants', function() {
      it('should allow SUPER_ADMIN to list all tenants', async function() {
        await request(app)
          .get('/api/admin/tenants')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);
      });

      it('should allow GLOBAL_ADMIN to list all tenants', async function() {
        await request(app)
          .get('/api/admin/tenants')
          .set('Authorization', `Bearer ${globalAdminToken}`)
          .expect(200);
      });

      it('should deny COMPLIANCE_ADMIN access to tenant list', async function() {
        await request(app)
          .get('/api/admin/tenants')
          .set('Authorization', `Bearer ${complianceAdminToken}`)
          .expect(403);
      });
    });

    describe('POST /api/admin/tenants', function() {
      it('should allow SUPER_ADMIN to create a tenant', async function() {
        const newTenant = {
          name: 'New Firm',
          adminEmail: 'admin@newfirm.com',
          plan: 'enterprise',
          jurisdiction: 'ZA'
        };

        await request(app)
          .post('/api/admin/tenants')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send(newTenant)
          .expect(201);
      });

      it('should deny GLOBAL_ADMIN tenant creation', async function() {
        const newTenant = {
          name: 'Another Firm',
          adminEmail: 'admin@anotherfirm.com',
          plan: 'pro'
        };

        await request(app)
          .post('/api/admin/tenants')
          .set('Authorization', `Bearer ${globalAdminToken}`)
          .send(newTenant)
          .expect(403);
      });

      it('should validate required fields', async function() {
        await request(app)
          .post('/api/admin/tenants')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({})
          .expect(400);
      });
    });

    describe('POST /api/admin/tenants/:tenantId/suspend', function() {
      it('should allow SUPER_ADMIN to suspend a tenant', async function() {
        await request(app)
          .post(`/api/admin/tenants/${testTenant._id}/suspend`)
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({
            reason: 'Non-payment',
            duration: '30d'
          })
          .expect(200);
      });

      it('should require suspension reason', async function() {
        await request(app)
          .post(`/api/admin/tenants/${testTenant._id}/suspend`)
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({})
          .expect(400);
      });
    });

    describe('POST /api/admin/tenants/:tenantId/activate', function() {
      it('should allow SUPER_ADMIN to activate a tenant', async function() {
        await request(app)
          .post(`/api/admin/tenants/${testTenant._id}/activate`)
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({ reason: 'Payment received' })
          .expect(200);
      });
    });
  });

  // ===========================================================================
  // 4. USER SOVEREIGNTY TESTS
  // ===========================================================================
  describe('User Sovereignty - Global Identity Control', function() {
    describe('GET /api/admin/users', function() {
      it('should allow SUPER_ADMIN to list all users', async function() {
        await request(app)
          .get('/api/admin/users')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);
      });

      it('should allow GLOBAL_ADMIN to list all users', async function() {
        await request(app)
          .get('/api/admin/users')
          .set('Authorization', `Bearer ${globalAdminToken}`)
          .expect(200);
      });

      it('should support search queries', async function() {
        await request(app)
          .get('/api/admin/users')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .query({ q: 'admin', role: 'SUPER_ADMIN' })
          .expect(200);
      });
    });

    describe('GET /api/admin/users/:userId', function() {
      it('should allow SUPER_ADMIN to get user profile', async function() {
        await request(app)
          .get(`/api/admin/users/${regularUser._id}`)
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);
      });

      it('should return 404 for non-existent user', async function() {
        const fakeId = new mongoose.Types.ObjectId();
        await request(app)
          .get(`/api/admin/users/${fakeId}`)
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(404);
      });
    });

    describe('PATCH /api/admin/users/:userId', function() {
      it('should allow SUPER_ADMIN to update user', async function() {
        await request(app)
          .patch(`/api/admin/users/${regularUser._id}`)
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({ firstName: 'Updated', role: 'USER_ADMIN' })
          .expect(200);
      });

      it('should deny GLOBAL_ADMIN user updates', async function() {
        await request(app)
          .patch(`/api/admin/users/${regularUser._id}`)
          .set('Authorization', `Bearer ${globalAdminToken}`)
          .send({ firstName: 'Hacked' })
          .expect(403);
      });
    });

    describe('DELETE /api/admin/users/:userId', function() {
      it('should require nuclear confirmation for deletion', async function() {
        await request(app)
          .delete(`/api/admin/users/${regularUser._id}`)
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({
            confirmation: 'WRONG_CODE',
            reason: 'Test deletion'
          })
          .expect(400);
      });

      it('should require deletion reason', async function() {
        await request(app)
          .delete(`/api/admin/users/${regularUser._id}`)
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({ confirmation: 'CONFIRM_ATOMIC_DELETION' })
          .expect(400);
      });
    });
  });

  // ===========================================================================
  // 5. EMERGENCY PROTOCOLS TESTS
  // ===========================================================================
  describe('Emergency Protocols - Crisis Management', function() {
    describe('POST /api/admin/emergency/lockdown', function() {
      it('should allow SUPER_ADMIN to initiate lockdown', async function() {
        await request(app)
          .post('/api/admin/emergency/lockdown')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({
            reason: 'Security incident',
            scope: 'platform-wide'
          })
          .expect(200);
      });

      it('should deny SECURITY_ADMIN lockdown initiation', async function() {
        await request(app)
          .post('/api/admin/emergency/lockdown')
          .set('Authorization', `Bearer ${securityAdminToken}`)
          .send({ reason: 'Test' })
          .expect(403);
      });
    });

    describe('POST /api/admin/emergency/recover', function() {
      it('should require recovery confirmation', async function() {
        await request(app)
          .post('/api/admin/emergency/recover')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({
            confirmation: 'WRONG_CODE',
            recoveryPoint: new Date().toISOString()
          })
          .expect(400);
      });
    });
  });

  // ===========================================================================
  // 6. CRYPTOGRAPHIC CONTROL TESTS
  // ===========================================================================
  describe('Cryptographic Control - Key Governance', function() {
    describe('POST /api/admin/crypto/rotate-keys', function() {
      it('should allow SUPER_ADMIN to rotate keys', async function() {
        await request(app)
          .post('/api/admin/crypto/rotate-keys')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({ keyType: 'jwt', strategy: 'rolling' })
          .expect(200);
      });

      it('should allow SECURITY_ADMIN to rotate keys', async function() {
        await request(app)
          .post('/api/admin/crypto/rotate-keys')
          .set('Authorization', `Bearer ${securityAdminToken}`)
          .send({ keyType: 'aes', strategy: 'immediate' })
          .expect(200);
      });
    });

    describe('GET /api/admin/crypto/status', function() {
      it('should allow SUPER_ADMIN to check crypto status', async function() {
        await request(app)
          .get('/api/admin/crypto/status')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);
      });

      it('should allow SECURITY_ADMIN to check crypto status', async function() {
        await request(app)
          .get('/api/admin/crypto/status')
          .set('Authorization', `Bearer ${securityAdminToken}`)
          .expect(200);
      });
    });
  });

  // ===========================================================================
  // 7. COMPLIANCE OVERSIGHT TESTS
  // ===========================================================================
  describe('Compliance Oversight - Regulatory Governance', function() {
    describe('GET /api/admin/compliance/status', function() {
      it('should allow SUPER_ADMIN to check compliance status', async function() {
        await request(app)
          .get('/api/admin/compliance/status')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);
      });

      it('should allow COMPLIANCE_ADMIN to check compliance status', async function() {
        await request(app)
          .get('/api/admin/compliance/status')
          .set('Authorization', `Bearer ${complianceAdminToken}`)
          .expect(200);
      });
    });

    describe('POST /api/admin/compliance/scan', function() {
      it('should allow SUPER_ADMIN to initiate compliance scan', async function() {
        await request(app)
          .post('/api/admin/compliance/scan')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({ scope: 'full' })
          .expect(200);
      });
    });
  });

  // ===========================================================================
  // 8. PERFORMANCE COMMAND TESTS
  // ===========================================================================
  describe('Performance Command - System Optimization', function() {
    describe('GET /api/admin/performance/metrics', function() {
      it('should allow SUPER_ADMIN to view performance metrics', async function() {
        await request(app)
          .get('/api/admin/performance/metrics')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);
      });

      it('should allow GLOBAL_ADMIN to view performance metrics', async function() {
        await request(app)
          .get('/api/admin/performance/metrics')
          .set('Authorization', `Bearer ${globalAdminToken}`)
          .expect(200);
      });
    });

    describe('POST /api/admin/performance/optimize', function() {
      it('should allow SUPER_ADMIN to execute optimization', async function() {
        await request(app)
          .post('/api/admin/performance/optimize')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .send({
            optimizationType: 'database',
            strategy: 'balanced'
          })
          .expect(200);
      });
    });
  });

  // ===========================================================================
  // 9. HEALTH & DIAGNOSTICS TESTS
  // ===========================================================================
  describe('Health & Diagnostics - Sovereign Monitoring', function() {
    describe('GET /api/admin/health', function() {
      it('should allow SUPER_ADMIN to access sovereign health', async function() {
        const response = await request(app)
          .get('/api/admin/health')
          .set('Authorization', `Bearer ${superAdminToken}`)
          .expect(200);

        expect(response.body).to.have.property('status', 'sovereign');
        expect(response.body).to.have.property('system', 'Wilsy-OS-10G-Admin-Control-Plane');
        expect(response.body).to.have.property('version', '10.0.0-GENERATIONAL');
        expect(response.body.metrics).to.have.property('valuation', 'R500,000,000 control plane value');
      });

      it('should allow GLOBAL_ADMIN to access sovereign health', async function() {
        await request(app)
          .get('/api/admin/health')
          .set('Authorization', `Bearer ${globalAdminToken}`)
          .expect(200);
      });

      it('should allow SECURITY_ADMIN to access sovereign health', async function() {
        await request(app)
          .get('/api/admin/health')
          .set('Authorization', `Bearer ${securityAdminToken}`)
          .expect(200);
      });

      it('should deny regular user access to sovereign health', async function() {
        await request(app)
          .get('/api/admin/health')
          .set('Authorization', `Bearer ${regularUserToken}`)
          .expect(403);
      });
    });
  });

  // ===========================================================================
  // 10. SOVEREIGN BOUNDARY TESTS
  // ===========================================================================
  describe('Sovereign Boundary - 404 Handler', function() {
    it('should return 404 for undefined admin routes', async function() {
      const response = await request(app)
        .get('/api/admin/non-existent-route')
        .set('Authorization', `Bearer ${superAdminToken}`)
        .expect(404);

      expect(response.body).to.have.property('code', 'ADMIN_404_ROUTE_NOT_FOUND');
      expect(response.body).to.have.property('status', 'error');
      expect(response.body.security).to.have.property('action', 'administrative_boundary_defense_activated');
    });

    it('should log forensic audit for boundary violation', async function() {
      await request(app)
        .get('/api/admin/hacking-attempt')
        .set('Authorization', `Bearer ${regularUserToken}`)
        .expect(404);
    });
  });

  // ===========================================================================
  // 11. RATE LIMITING TESTS
  // ===========================================================================
  describe('Rate Limiting - Sovereign Throttle', function() {
    it('should enforce rate limits for admin actions', async function() {
      // Make many requests quickly to trigger rate limit
      const promises = [];
      for (let i = 0; i < 110; i++) {
        promises.push(
          request(app)
            .get('/api/admin/health')
            .set('Authorization', `Bearer ${superAdminToken}`)
        );
      }

      const responses = await Promise.all(promises);
      const rateLimited = responses.some(r => r.status === 429);
      expect(rateLimited).to.be.true;
    });
  });
});
