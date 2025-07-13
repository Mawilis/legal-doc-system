const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../app');
const User = require('../models/userModel');

describe('Authentication API Endpoints', () => {
    const timestamp = Date.now();
    const email = `test-${timestamp}@example.com`;
    const testUser = {
        name: 'Test User',
        email,
        password: 'password123',
    };

    beforeAll(async () => {
        if (mongoose.connection.readyState === 0) {
            await mongoose.connect(process.env.MONGO_URI);
            console.log('✅ Connected to test MongoDB');
        }
    });

    afterAll(async () => {
        console.log('🧹 Cleaning up test database...');
        await User.deleteMany({ email });
        if (mongoose.connection.readyState === 1) {
            await mongoose.disconnect();
            console.log('✅ Disconnected from test database');
        }
    });

    describe('POST /api/auth/register', () => {
        it('should register a new user successfully with valid data', async () => {
            const res = await request(app).post('/api/auth/register').send(testUser);
            console.log('✅ Registered user:', res.body);
            expect(res.statusCode).toBe(201);
            expect(res.body.success).toBe(true);
            expect(res.body.data.email).toBe(testUser.email);
        });

        it('should fail to register a user with a duplicate email', async () => {
            const res = await request(app).post('/api/auth/register').send(testUser);
            console.log('❌ Duplicate registration response:', res.body);
            expect(res.statusCode).toBe(400); // Or 422, if that’s what your controller uses
            expect(res.body.success).toBe(false);
        });

        it('should fail to register with a missing password', async () => {
            const res = await request(app)
                .post('/api/auth/register')
                .send({ name: 'No Password', email: `no-pass-${timestamp}@example.com` });

            expect(res.statusCode).toBe(422); // Or 400 if that's what your controller returns
            expect(res.body.success).toBe(false);
        });
    });

    describe('POST /api/auth/login', () => {
        it('should log in a registered user successfully', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({ email: testUser.email, password: testUser.password });

            console.log('🔑 Login token:', res.body.token);
            expect(res.statusCode).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body).toHaveProperty('token');
        });

        it('should fail to log in with an incorrect password', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({ email: testUser.email, password: 'wrongpassword' });

            expect(res.statusCode).toBe(401);
            expect(res.body.success).toBe(false);
        });
    });
});
