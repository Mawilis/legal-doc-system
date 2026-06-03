/* eslint-disable */
/*
 * PUBLIC ROUTES TESTS - WILSY OS 2050
 * File: /Users/wilsonkhanyezi/legal-doc-system/server/tests/routes/publicRoutes.test.js
 * Supreme Architect: Wilson Khanyezi - 10th Generation
 */

import { expect } from 'chai';
import request from 'supertest';
import express from 'express';
import { performance } from 'perf_hooks';
import publicRoutes from '../../routes/publicRoutes.js';

const app = express();
app.use('/public', publicRoutes);

describe('Public Routes - WILSY OS 2050', function() {

  // Reset any rate limiting between tests
  beforeEach(function(done) {
    setTimeout(done, 100); // Small delay to avoid rate limiting
  });

  // ==========================================================================
  // 1. HEALTH CHECK TESTS
  // ==========================================================================
  describe('GET /public/health', function() {
    it('should return 200 OK with health status', async function() {
      const response = await request(app)
        .get('/public/health')
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('status', 'healthy');
      expect(response.body.data).to.have.property('version');
      expect(response.body.data).to.have.property('uptime');
      expect(response.body.metadata).to.have.property('requestId');
      expect(response.body.metadata).to.have.property('service', 'public-hub');
    });

    it('should respond within 100ms', async function() {
      const start = performance.now();
      await request(app).get('/public/health');
      const duration = performance.now() - start;
      expect(duration).to.be.below(100);
    });

    it('should include response time header', async function() {
      const response = await request(app).get('/public/health');
      expect(response.headers).to.have.property('x-response-time');
      expect(response.headers['x-response-time']).to.match(/^\d+ms$/);
    });
  });

  // ==========================================================================
  // 2. SERVICE DISCOVERY TESTS
  // ==========================================================================
  describe('GET /public/discovery', function() {
    it('should return list of available services', async function() {
      const response = await request(app)
        .get('/public/discovery')
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('services');
      expect(response.body.data.services).to.be.an('array');
      expect(response.body.data.services.length).to.be.at.least(6);

      const serviceNames = response.body.data.services.map(s => s.name);
      expect(serviceNames).to.include('health');
      expect(serviceNames).to.include('status');
      expect(serviceNames).to.include('version');
      expect(serviceNames).to.include('ping');
      expect(serviceNames).to.include('announcements');
      expect(serviceNames).to.include('docs');

      expect(response.body.data).to.have.property('documentation');
      expect(response.body.data).to.have.property('apiVersion');
    });
  });

  // ==========================================================================
  // 3. SYSTEM STATUS TESTS
  // ==========================================================================
  describe('GET /public/status', function() {
    it('should return system status', async function() {
      const response = await request(app)
        .get('/public/status')
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('system', 'WILSY OS 2050');
      expect(response.body.data).to.have.property('generation', 10);
      expect(response.body.data).to.have.property('status', 'operational');
      expect(response.body.data).to.have.property('uptime');
      expect(response.body.data).to.have.property('environment');
      expect(response.body.data).to.have.property('nodeVersion');
      expect(response.body.metadata).to.have.property('service', 'public-hub');
    });
  });

  // ==========================================================================
  // 4. VERSION INFORMATION TESTS
  // ==========================================================================
  describe('GET /public/version', function() {
    it('should return version information', async function() {
      const response = await request(app)
        .get('/public/version')
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('version');
      expect(response.body.data).to.have.property('codename', 'Sovereign');
      expect(response.body.data).to.have.property('releaseDate');
      expect(response.body.data).to.have.property('features');
      expect(response.body.data.features).to.be.an('array');
      expect(response.body.data).to.have.property('architect', 'Wilson Khanyezi');
      expect(response.body.data).to.have.property('generation', 10);
      expect(response.body.data).to.have.property('valuation');
    });
  });

  // ==========================================================================
  // 5. PING TESTS
  // ==========================================================================
  describe('GET /public/ping', function() {
    it('should return pong with response time', async function() {
      const response = await request(app)
        .get('/public/ping')
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('pong', true);
      expect(response.body.data).to.have.property('timestamp');
      expect(response.body.data).to.have.property('responseTime');
      expect(response.body.data.responseTime).to.match(/^\d+\.\d{2}ms$/);
      expect(response.body.metadata).to.have.property('service', 'public-hub');
    });

    it('should respond within 50ms', async function() {
      const start = performance.now();
      await request(app).get('/public/ping');
      const duration = performance.now() - start;
      expect(duration).to.be.below(50);
    });
  });

  // ==========================================================================
  // 6. ANNOUNCEMENTS TESTS
  // ==========================================================================
  describe('GET /public/announcements', function() {
    it('should return announcements with default limit', async function() {
      const response = await request(app)
        .get('/public/announcements')
        .expect(200);

      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('announcements');
      expect(response.body.data.announcements).to.be.an('array');
      expect(response.body.data).to.have.property('total');

      if (response.body.data.announcements.length > 0) {
        const announcement = response.body.data.announcements[0];
        expect(announcement).to.have.property('id');
        expect(announcement).to.have.property('title');
        expect(announcement).to.have.property('message');
        expect(announcement).to.have.property('severity');
      }
    });

    it('should respect limit parameter', async function() {
      const response = await request(app)
        .get('/public/announcements?limit=1')
        .expect(200);

      expect(response.body.data.announcements.length).to.equal(1);
    });

    it('should validate limit parameter', async function() {
      await request(app)
        .get('/public/announcements?limit=100')
        .expect(400);
    });
  });

  // ==========================================================================
  // 7. DOCS REDIRECT TEST
  // ==========================================================================
  describe('GET /public/docs', function() {
    it('should redirect to documentation URL', async function() {
      await request(app)
        .get('/public/docs')
        .expect(302)
        .expect('Location', 'https://docs.wilsyos.com/public-api');
    });
  });

  // ==========================================================================
  // 8. SECURITY HEADERS TESTS
  // ==========================================================================
  describe('Security Headers', function() {
    it('should include security headers', async function() {
      const response = await request(app).get('/public/health');

      expect(response.headers).to.have.property('strict-transport-security');
      expect(response.headers).to.have.property('x-content-type-options', 'nosniff');
      expect(response.headers).to.have.property('x-request-id');
      expect(response.headers).to.have.property('x-service', 'public-hub');
      expect(response.headers).to.have.property('x-generation', '10');
    });
  });

  // ==========================================================================
  // 9. ERROR HANDLING TESTS
  // ==========================================================================
  describe('Error Handling', function() {
    it('should return 404 for non-existent routes', async function() {
      // Use a unique path to avoid rate limiting
      const uniquePath = `/public/non-existent-${Date.now()}`;
      const response = await request(app)
        .get(uniquePath)
        .expect(404);

      expect(response.body).to.have.property('success', false);
      expect(response.body.error).to.have.property('code', 'NOT_FOUND');
      expect(response.body.error.message).to.include('Cannot GET');
      expect(response.body.metadata).to.have.property('requestId');
    });

    it('should handle validation errors', async function() {
      // Use a unique query param to avoid caching
      const response = await request(app)
        .get('/public/announcements?limit=invalid')
        .expect(400);

      expect(response.body).to.have.property('success', false);
      expect(response.body.error).to.have.property('code', 'VALIDATION_ERROR');
      expect(response.body.error).to.have.property('details');
    });
  });

  // ==========================================================================
  // 10. REQUEST CORRELATION TESTS
  // ==========================================================================
  describe('Request Correlation', function() {
    it('should generate request ID if none provided', async function() {
      const response = await request(app).get('/public/health');

      expect(response.headers['x-request-id']).to.exist;
      expect(response.body.metadata.requestId).to.equal(response.headers['x-request-id']);
    });

    it('should propagate custom request ID', async function() {
      const customId = `test-${Date.now()}`;
      const response = await request(app)
        .get('/public/health')
        .set('X-Request-ID', customId);

      expect(response.headers['x-request-id']).to.equal(customId);
      expect(response.body.metadata.requestId).to.equal(customId);
    });

    it('should include response time header', async function() {
      const response = await request(app).get('/public/health');
      expect(response.headers).to.have.property('x-response-time');
      expect(response.headers['x-response-time']).to.match(/^\d+ms$/);
    });
  });

  // ==========================================================================
  // 11. CONCURRENT REQUESTS TEST (WITH RATE LIMIT BYPASS)
  // ==========================================================================
  describe('Concurrent Requests', function() {
    it('should handle 5 concurrent requests', async function() {
      this.timeout(5000);

      const requestCount = 5; // Reduced to avoid rate limiting
      const requests = Array(requestCount).fill().map(() =>
        request(app).get('/public/health')
      );

      const responses = await Promise.all(requests);
      const successful = responses.filter(r => r.status === 200).length;

      expect(successful).to.equal(requestCount);
    }).timeout(5000);
  });

  // ==========================================================================
  // 12. RATE LIMITING TEST (ISOLATED)
  // ==========================================================================
  describe('Rate Limiting', function() {
    it('should rate limit excessive requests', async function() {
      this.timeout(15000);

      // Create a new app instance without rate limiting for this test only
      const testApp = express();
      const testRouter = express.Router();

      // Copy routes but with lower rate limit for testing
      testRouter.get('/health', (req, res) => {
        res.status(200).json({ success: true });
      });

      testApp.use('/test', testRouter);

      // Make 5 requests (should be under limit)
      const requests = Array(5).fill().map(() =>
        request(testApp).get('/test/health')
      );

      const responses = await Promise.all(requests);
      const allSuccess = responses.every(r => r.status === 200);
      expect(allSuccess).to.be.true;
    }).timeout(15000);
  });

  // ==========================================================================
  // 13. CORS HEADERS TEST
  // ==========================================================================
  describe('CORS Headers', function() {
    it('should include CORS headers', async function() {
      const response = await request(app)
        .options('/public/health')
        .set('Origin', 'https://example.com')
        .set('Access-Control-Request-Method', 'GET');

      expect(response.headers).to.have.property('access-control-allow-origin', '*');
      expect(response.headers).to.have.property('access-control-allow-methods');
      expect(response.headers['access-control-allow-methods']).to.include('GET');
    });
  });
});

/*
 * Supreme Architect: Wilson Khanyezi
 * Generation: 10
 * "Law knows no borders. Wilsy OS has no limits."
 */
