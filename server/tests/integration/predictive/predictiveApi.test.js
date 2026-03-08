/* eslint-disable */
import { expect } from 'chai';
import request from 'supertest';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import app from '../../../app.js';

describe('🔗 Predictive API Integration Tests', () => {
  let mongoServer;

  before(async () => {
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    await mongoose.connect(uri);
  });

  after(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
  });

  describe('POST /api/predictive/analyze', () => {
    it('should analyze template successfully', async () => {
      const response = await request(app)
        .post('/api/predictive/analyze')
        .set('Authorization', 'Bearer test-token')
        .set('X-Tenant-ID', 'test-tenant')
        .send({
          template: {
            templateId: '123e4567-e89b-12d3-a456-426614174000',
            content: 'Test legal document content',
            type: 'contract',
            jurisdiction: 'ZA'
          }
        });

      expect(response.status).to.equal(202);
      expect(response.body).to.have.property('requestId');
      expect(response.body).to.have.property('analysis');
      expect(response.body.analysis).to.have.property('confidence');
    });
  });

  describe('GET /api/predictive/forecast', () => {
    it('should generate forecast with query parameters', async () => {
      const response = await request(app)
        .get('/api/predictive/forecast')
        .query({ horizon: 24, jurisdictions: 'ZA,US,EU' })
        .set('Authorization', 'Bearer test-token')
        .set('X-Tenant-ID', 'test-tenant');

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('data');
      expect(response.body.data).to.have.property('jurisdictions');
    });
  });

  describe('POST /api/predictive/roi', () => {
    it('should calculate ROI', async () => {
      const response = await request(app)
        .post('/api/predictive/roi')
        .set('Authorization', 'Bearer test-token')
        .set('X-Tenant-ID', 'test-tenant')
        .send({
          implementationCost: 15000000,
          clients: 100,
          clientSegment: 'enterprise'
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('data');
      expect(response.body.data).to.have.property('projectedROI');
    });
  });

  describe('GET /api/predictive/evidence', () => {
    it('should generate forensic evidence', async () => {
      const response = await request(app)
        .get('/api/predictive/evidence')
        .set('Authorization', 'Bearer test-token')
        .set('X-Tenant-ID', 'test-tenant');

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('data');
      expect(response.body.data).to.have.property('evidenceId');
      expect(response.body.data).to.have.property('legalCompliance');
    });
  });

  describe('GET /api/predictive/metrics', () => {
    it('should return prometheus metrics', async () => {
      const response = await request(app)
        .get('/api/predictive/metrics')
        .set('Authorization', 'Bearer test-token')
        .set('X-Tenant-ID', 'test-tenant');

      expect(response.status).to.equal(200);
      expect(response.text).to.include('predictive_api_requests_total');
    });
  });
});
