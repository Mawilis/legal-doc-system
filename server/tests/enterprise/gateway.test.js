/* eslint-disable */
import { expect } from 'chai';
import request from 'supertest';
import jwt from 'jsonwebtoken';
import { performance } from 'perf_hooks';
import app from '../../enterprise/apiGateway.js';

describe('SOVEREIGN GATEWAY - ENTERPRISE VALIDATION', function() {
  this.timeout(30000);

  // ==========================================================================
  // TIER 1: PROTOCOL SECURITY & HEADERS
  // ==========================================================================
  describe('Tier 1 - Security Headers', () => {
    it('should include x-sovereign-gateway header', async () => {
      const res = await request(app)
        .get('/api/public/health')
        .expect(200);

      expect(res.headers).to.have.property('x-sovereign-gateway', 'Wilsy-OS-Sovereign-v8.0');
      expect(res.headers).to.have.property('x-sovereign-generation', '10');
    });

    it('should propagate correlation IDs', async () => {
      const customId = `SOV-TEST-${Date.now()}`;
      const res = await request(app)
        .get('/api/public/health')
        .set('x-sovereign-correlation-id', customId)
        .expect(200);

      expect(res.headers['x-sovereign-correlation-id']).to.equal(customId);
      expect(res.body.correlationId).to.equal(customId);
    });

    it('should generate correlation ID if none provided', async () => {
      const res = await request(app)
        .get('/api/public/health')
        .expect(200);

      expect(res.headers['x-sovereign-correlation-id']).to.match(/^SOV-/);
      expect(res.body.correlationId).to.equal(res.headers['x-sovereign-correlation-id']);
    });
  });

  // ==========================================================================
  // TIER 2: GATEWAY HEALTH
  // ==========================================================================
  describe('Tier 2 - Health Check', () => {
    it('should return healthy status', async () => {
      const res = await request(app)
        .get('/api/public/health')
        .expect(200);

      expect(res.body).to.have.property('success', true);
      expect(res.body).to.have.property('status', 'healthy');
      expect(res.body).to.have.property('gateway', 'Sovereign');
    });

    it('should respond within 50ms', async () => {
      const start = performance.now();
      await request(app).get('/api/public/health');
      const duration = performance.now() - start;
      expect(duration).to.be.below(50);
    });
  });

  // ==========================================================================
  // TIER 3: ROUTE MOUNTING
  // ==========================================================================
  describe('Tier 3 - Route Mounting', () => {
    it('should mount auth routes', async () => {
      await request(app)
        .post('/api/auth/login')
        .send({ email: 'test@example.com', password: 'password' })
        .expect(200);
    });

    it('should mount analytics routes', async () => {
      const token = jwt.sign({ sub: 'user', role: 'user' }, 'sovereign-jwt-secret-2026');
      await request(app)
        .get('/api/analytics/dashboard')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);
    });

    it('should mount test endpoint', async () => {
      await request(app)
        .get('/api/test')
        .expect(200);
    });
  });

  // ==========================================================================
  // TIER 4: RATE LIMITING
  // ==========================================================================
  describe('Tier 4 - Rate Limiting', () => {
    it('should include rate limit headers', async () => {
      const res = await request(app)
        .get('/api/public/health')
        .expect(200);

      expect(res.headers).to.have.property('ratelimit-limit');
      expect(res.headers).to.have.property('ratelimit-remaining');
      expect(res.headers).to.have.property('ratelimit-reset');
    });
  });

  // ==========================================================================
  // TIER 5: PAYLOAD SECURITY
  // ==========================================================================
  describe('Tier 5 - Payload Security', () => {
    it('should reject malformed JSON', async () => {
      await request(app)
        .post('/api/auth/login')
        .set('Content-Type', 'application/json')
        .send('{malformed json')
        .expect(400);
    });

    it('should reject oversized payloads', async () => {
      const largePayload = { data: 'x'.repeat(2 * 1024 * 1024) }; // 2MB

      await request(app)
        .post('/api/auth/login')
        .send(largePayload)
        .expect(413);
    });
  });

  // ==========================================================================
  // TIER 6: AUTHENTICATION
  // ==========================================================================
  describe('Tier 6 - Authentication', () => {
    it('should require auth for protected routes', async () => {
      await request(app)
        .get('/api/analytics/dashboard')
        .expect(401);
    });

    it('should accept valid tokens', async () => {
      const token = jwt.sign({ sub: 'user', role: 'user' }, 'sovereign-jwt-secret-2026');

      await request(app)
        .get('/api/analytics/dashboard')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);
    });

    it('should reject expired tokens', async () => {
      const token = jwt.sign(
        { sub: 'user', role: 'user' },
        'sovereign-jwt-secret-2026',
        { expiresIn: '0s' }
      );

      await request(app)
        .get('/api/analytics/dashboard')
        .set('Authorization', `Bearer ${token}`)
        .expect(401);
    });
  });

  // ==========================================================================
  // TIER 12: CACHE INVALIDATION
  // ==========================================================================
  describe('Tier 12 - Cache Invalidation', () => {
    it('should require admin privileges', async () => {
      const token = jwt.sign({ sub: 'user', role: 'user' }, 'sovereign-jwt-secret-2026');

      await request(app)
        .post('/api/cache/invalidate')
        .set('Authorization', `Bearer ${token}`)
        .expect(403);
    });

    it('should allow admin with correct key', async () => {
      const token = jwt.sign({ sub: 'admin', role: 'admin' }, 'sovereign-jwt-secret-2026');

      await request(app)
        .post('/api/cache/invalidate')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);
    });
  });

  // ==========================================================================
  // TIER 13: GATEWAY INFO
  // ==========================================================================
  describe('Tier 13 - Gateway Info', () => {
    it('should return gateway information', async () => {
      const res = await request(app)
        .get('/api/info')
        .expect(200);

      expect(res.body).to.have.property('name', 'Wilsy OS Gateway');
      expect(res.body).to.have.property('tiers', 14);
      expect(res.body).to.have.property('routing', 'Active');
    });
  });

  // ==========================================================================
  // TIER 14: ERROR HANDLING
  // ==========================================================================
  describe('Tier 14 - Error Handling', () => {
    it('should return 404 for unknown routes', async () => {
      const res = await request(app)
        .get('/api/unknown-route')
        .expect(404);

      expect(res.body).to.have.property('error', 'NOT_FOUND');
      expect(res.body).to.have.property('correlationId');
    });

    it('should preserve correlation ID in errors', async () => {
      const customId = `SOV-ERROR-${Date.now()}`;
      const res = await request(app)
        .get('/api/unknown-route')
        .set('x-sovereign-correlation-id', customId)
        .expect(404);

      expect(res.body.correlationId).to.equal(customId);
    });

    it('should handle OPTIONS preflight correctly', async () => {
      const res = await request(app)
        .options('/api/test')
        .set('Origin', 'http://localhost:3000')
        .set('Access-Control-Request-Method', 'GET');

      expect(res.status).to.equal(204);
      expect(res.headers).to.have.property('access-control-allow-origin');
    });
  });
});
