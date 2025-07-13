// server/tests/document.test.js
const request = require('supertest');
const app = require('../app');
const mongoose = require('mongoose');
const User = require('../models/userModel');
const Document = require('../models/documentModel');

describe('Document API Endpoints', () => {
    let token;

    const testUser = {
        name: 'Doc Test User',
        email: 'doctest@example.com',
        password: 'password123',
    };

    beforeAll(async () => {
        if (mongoose.connection.readyState === 0) {
            await mongoose.connect(process.env.MONGO_URI);
        }
    });

    beforeEach(async () => {
        await Document.deleteMany();
        await User.deleteMany({ email: testUser.email });

        // Register user
        await request(app).post('/api/auth/register').send(testUser);

        // Login user
        const loginRes = await request(app)
            .post('/api/auth/login')
            .send({ email: testUser.email, password: testUser.password });

        token = loginRes.body.token;
        console.log('🔑 Refreshed Token:', token);
    });

    afterAll(async () => {
        console.log('🧹 Cleaning up test database...');
        if (mongoose.connection.readyState === 1) {
            for (const name of Object.keys(mongoose.connection.collections)) {
                const collection = mongoose.connection.collections[name];
                await collection.deleteMany({});
                console.log(`🧹 Cleared collection: ${name}`);
            }
            await mongoose.disconnect();
            console.log('✅ Disconnected from test database');
        } else {
            console.warn('⚠️ Skipped cleanup: Mongoose not connected');
        }
    });

    it('should create a new document for an authenticated user', async () => {
        const res = await request(app)
            .post('/api/documents')
            .set('Authorization', `Bearer ${token}`)
            .send({
                title: 'Test Summons',
                caseNumber: 'CASE-001',
                documentType: 'Combined Summons',
                content: 'This is the content of the test summons.',
                client: 'Test Law Firm',
            });

        expect(res.statusCode).toEqual(201);
        expect(res.body.success).toBe(true);
        expect(res.body.data).toHaveProperty('caseNumber', 'CASE-001');
    });

    it('should fail to create a document without a token', async () => {
        const res = await request(app)
            .post('/api/documents')
            .send({
                title: 'Unauthorized Document',
                caseNumber: 'CASE-002',
                documentType: 'Notice of Motion',
                content: 'This should fail.',
                client: 'Test Law Firm',
            });

        expect(res.statusCode).toEqual(401);
    });

    it('should fetch all documents', async () => {
        const docPayload = {
            title: 'Doc 1',
            caseNumber: 'CASE-101',
            documentType: 'Other',
            content: '...',
            client: 'Firm A',
        };

        console.log('📨 Sending token:', token);

        const createRes = await request(app)
            .post('/api/documents')
            .set('Authorization', `Bearer ${token}`)
            .send(docPayload);

        console.log('📥 Document create response:', createRes.statusCode, createRes.body);
        expect(createRes.statusCode).toEqual(201);

        await new Promise((resolve) => setTimeout(resolve, 100)); // slight delay to ensure DB consistency

        const fetchRes = await request(app)
            .get('/api/documents')
            .set('Authorization', `Bearer ${token}`);

        console.log('📄 Fetch response body:', fetchRes.body);

        expect(fetchRes.statusCode).toEqual(200);
        expect(fetchRes.body.success).toBe(true);
        expect(fetchRes.body.count).toBe(1);
        expect(fetchRes.body.data[0].caseNumber).toBe('CASE-101');
    });
});
