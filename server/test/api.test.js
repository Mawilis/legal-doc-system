const request = require('supertest');
const app = require('../server.js');

describe('Wilsy OS Server API', () => {
  describe('Health Endpoint', () => {
    it('should return operational status', async () => {
      const res = await request(app).get('/health');
      expect(res.statusCode).toEqual(200);
      expect(res.body.status).toEqual('OPERATIONAL');
      expect(res.body.system).toEqual('Wilsy OS Legal Engine');
    });
  });

  describe('Security Headers', () => {
    it('should have security headers', async () => {
      const res = await request(app).get('/health');
      expect(res.headers['x-powered-by']).toBeUndefined();
      expect(res.headers['x-frame-options']).toEqual('DENY');
    });
  });
});
