/* eslint-disable */
import { expect } from 'chai';
import request from 'supertest';
import jwt from 'jsonwebtoken';
import app from '../testApp.js';

describe('SuperAdmin Audit Routes', function() {
  let superToken;

  before(function() {
    process.env.JWT_SECRET = 'test-secret-key';
    superToken = jwt.sign(
      { id: 'superadmin-id', role: 'SUPER_ADMIN', tenantId: 'tenant-id' },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );
  });

  describe('GET /api/superadmin/audit/logs', function() {
    it('should return audit logs for superadmin', async function() {
      const response = await request(app)
        .get('/api/superadmin/audit/logs')
        .set('Authorization', `Bearer ${superToken}`)
        .query({ limit: 10, skip: 0 })
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.be.an('array');
      expect(response.body).to.have.property('total');
    });

    it('should filter logs by date range', async function() {
      const response = await request(app)
        .get('/api/superadmin/audit/logs')
        .set('Authorization', `Bearer ${superToken}`)
        .query({
          startDate: '2025-01-01',
          endDate: '2025-12-31',
          limit: 10
        })
        .expect(200);

      expect(response.body).to.have.property('success', true);
    });

    it('should filter logs by action type', async function() {
      const response = await request(app)
        .get('/api/superadmin/audit/logs')
        .set('Authorization', `Bearer ${superToken}`)
        .query({ action: 'USER_LOGIN', limit: 10 })
        .expect(200);

      expect(response.body).to.have.property('success', true);
    });

    it('should filter logs by tenant ID', async function() {
      const response = await request(app)
        .get('/api/superadmin/audit/logs')
        .set('Authorization', `Bearer ${superToken}`)
        .query({ tenantId: 'tenant-123', limit: 10 })
        .expect(200);

      expect(response.body).to.have.property('success', true);
    });

    it('should return 400 for invalid date format', async function() {
      const response = await request(app)
        .get('/api/superadmin/audit/logs')
        .set('Authorization', `Bearer ${superToken}`)
        .query({ startDate: 'invalid-date' })
        .expect(400);

      expect(response.body).to.have.property('error');
    });

    it('should return 403 for non-superadmin role', async function() {
      const userToken = jwt.sign(
        { id: 'user-id', role: 'USER_VIEWER', tenantId: 'tenant-id' },
        process.env.JWT_SECRET,
        { expiresIn: '1h' }
      );

      await request(app)
        .get('/api/superadmin/audit/logs')
        .set('Authorization', `Bearer ${userToken}`)
        .expect(403);
    });

    it('should return 401 without token', async function() {
      await request(app)
        .get('/api/superadmin/audit/logs')
        .expect(401);
    });

    it('should handle invalid token', async function() {
      await request(app)
        .get('/api/superadmin/audit/logs')
        .set('Authorization', 'Bearer invalid.token')
        .expect(401);
    });
  });
});
