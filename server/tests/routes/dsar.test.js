const request = require('supertest');
const express = require('express');
const mongoose = require('mongoose');
const dsarRoutes = require('../../routes/dsar');

const app = express();
app.use(express.json());
app.use('/api/dsar', dsarRoutes);

describe('DSAR Routes', () => {
  beforeAll(async () => {
    await mongoose.connect(process.env.MONGO_URI_TEST);
  });

  afterAll(async () => {
    await mongoose.connection.close();
  });

  test('POST /api/dsar/submit - should create new DSAR request', async () => {
    const response = await request(app)
      .post('/api/dsar/submit')
      .set('Authorization', 'Bearer test-token')
      .set('X-Tenant-Id', 'test-tenant-123')
      .send({
        dsarType: 'ACCESS',
        dataSubject: {
          email: 'test@example.com',
          phone: '+27123456789',
          fullName: 'Test User'
        },
        scope: { documents: true, profile: true },
        preferredContactMethod: 'email',
        verificationMethods: ['email', 'sms']
      });
    
    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.data.dsarId).toBeDefined();
  });
});
