/* eslint-disable */
import { expect } from 'chai';
import request from 'supertest';
import fs from 'fs';
import path from 'path';
import express from 'express';
import bodyParser from 'body-parser';
import PredictiveEngineService from '../../services/PredictiveEngineService.js';
import TimeSeriesAnalyzer from '../../algorithms/predictive/TimeSeriesAnalyzer.js';
import LegalTrendDetector from '../../algorithms/predictive/LegalTrendDetector.js';
import RegulatoryForecaster from '../../algorithms/predictive/RegulatoryForecaster.js';
import routes from '../../routes/predictive.js';

describe('🔗 Predictive Engine Integration Suite', function () {
  this.timeout(120000); // 2 minutes

  let app;
  let service;
  let testTemplate;
  const snapshotDir = path.resolve(process.cwd(), 'test-snapshots');

  before(async () => {
    if (fs.existsSync(snapshotDir)) {
      fs.rmSync(snapshotDir, { recursive: true, force: true });
    }
    fs.mkdirSync(snapshotDir, { recursive: true });

    service = new PredictiveEngineService({ snapshotDir, modelDir: path.resolve(process.cwd(), 'test-models') });

    app = express();
    app.use(bodyParser.json({ limit: '1mb' }));
    app.use('/api/predict', routes);

    testTemplate = {
      templateId: 'integration-test-001',
      practiceArea: 'corporate',
      jurisdiction: 'ZA',
      content: { raw: 'Test template content about ESG and compliance' },
      usageStats: { timesUsed: 120, lastUsedAt: new Date().toISOString() },
      versionHistory: [
        { version: 1, createdAt: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(), changelog: 'Initial' },
        { version: 2, createdAt: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString(), changelog: 'Update' }
      ]
    };
  });

  after(async () => {
    try { fs.rmSync(snapshotDir, { recursive: true, force: true }); } catch (e) {}
    try { fs.rmSync(path.resolve(process.cwd(), 'test-models'), { recursive: true, force: true }); } catch (e) {}
  });

  describe('API Endpoints', () => {
    it('POST /api/predict/analyze should accept template and return accepted response', async () => {
      const res = await request(app)
        .post('/api/predict/analyze')
        .send({ template: testTemplate })
        .expect(202);

      expect(res.body).to.have.property('status', 'accepted');
      expect(res.body).to.have.property('templateId', testTemplate.templateId);
      expect(res.body).to.have.property('datasetHash');
      expect(res.body).to.have.property('snapshotPath');
      expect(fs.existsSync(res.body.snapshotPath)).to.be.true;
    });

    it('GET /api/predict/:id should return stored prediction', async () => {
      const templateId = testTemplate.templateId;
      const res = await request(app).get(`/api/predict/${templateId}`).expect(200);
      expect(res.body).to.have.property('templateId', templateId);
      expect(res.body).to.have.property('prediction');
    });

    it('GET /api/predict/health should return service health', async () => {
      const res = await request(app).get('/api/predict/health').expect(200);
      expect(res.body).to.have.property('status', 'ok');
    });
  });

  describe('Core Algorithm Sanity', () => {
    it('TimeSeriesAnalyzer should forecast and detect seasonality', async () => {
      const ts = new TimeSeriesAnalyzer();
      const data = Array.from({ length: 12 }, (_, i) => 100 + 5 * Math.sin(i * 0.5) + i * 0.2);
      const forecast = await ts.forecast(data, 6);
      expect(forecast).to.have.property('forecast');
      expect(Array.isArray(forecast.forecast)).to.be.true;
    });
  });
});
