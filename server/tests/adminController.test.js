// ~/server/tests/adminController.test.js

const request = require('supertest');
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const app = require('../server'); // Assuming your main server file exports the app
const User = require('../models/userModel'); // Assuming your user model
const jwt = require('jsonwebtoken');

// --- Test Suite for the Admin Controller ---
describe('Admin Controller API Endpoints', () => {
    let mongoServer;
    let adminToken;
    let userToken;
    let testUserId;

    // --- Setup: Runs once before all tests in this suite ---
    beforeAll(async () => {
        // 1. Start an in-memory MongoDB server for a clean testing environment.
        mongoServer = await MongoMemoryServer.create();
        const mongoUri = mongoServer.getUri();
        await mongoose.connect(mongoUri);

        // 2. Create mock users with different roles.
        const adminUser = await User.create({
            name: 'Admin User',
            email: 'admin@test.com',
            password: 'password123',
            role: 'admin',
        });

        const regularUser = await User.create({
            name: 'Regular User',
            email: 'user@test.com',
            password: 'password123',
            role: 'user',
        });
        testUserId = regularUser._id;

        // 3. Generate JWTs for the mock users.
        adminToken = jwt.sign({ id: adminUser._id, role: 'admin' }, process.env.JWT_SECRET, { expiresIn: '1h' });
        userToken = jwt.sign({ id: regularUser._id, role: 'user' }, process.env.JWT_SECRET, { expiresIn: '1h' });
    });

    // --- Teardown: Runs once after all tests in this suite ---
    afterAll(async () => {
        // Clean up by disconnecting from and stopping the in-memory database.
        await mongoose.disconnect();
        await mongoServer.stop();
    });


    // --- Test Case: GET /api/admin/stats ---
    describe('GET /api/admin/stats', () => {
        /**
         * Test for a successful request by an authenticated admin.
         */
        it('should return system stats for an admin user', async () => {
            const res = await request(app)
                .get('/api/admin/stats')
                .set('Authorization', `Bearer ${adminToken}`); // Use the admin's token

            // Assertions
            expect(res.statusCode).toBe(200);
            expect(res.body).toHaveProperty('success', true);
            expect(res.body).toHaveProperty('data');
            expect(res.body.data).toHaveProperty('userCount');
            expect(res.body.data).toHaveProperty('documentCount');
        });

        /**
         * Test for a failed request by a non-admin user.
         */
        it('should return a 403 Forbidden error for a non-admin user', async () => {
            const res = await request(app)
                .get('/api/admin/stats')
                .set('Authorization', `Bearer ${userToken}`); // Use the regular user's token

            // Assertions
            expect(res.statusCode).toBe(403);
            expect(res.body).toHaveProperty('success', false);
            expect(res.body).toHaveProperty('message', 'User role user is not authorized to access this route');
        });

        /**
         * Test for a failed request without authentication.
         */
        it('should return a 401 Unauthorized error if no token is provided', async () => {
            const res = await request(app).get('/api/admin/stats');

            // Assertions
            expect(res.statusCode).toBe(401);
            expect(res.body).toHaveProperty('success', false);
            expect(res.body).toHaveProperty('message', 'Not authorized, no token');
        });
    });

    // --- Test Case: User Management ---
    describe('User Management Endpoints', () => {
        it('POST /api/admin/users - should allow an admin to create a new user', async () => {
            const res = await request(app)
                .post('/api/admin/users')
                .set('Authorization', `Bearer ${adminToken}`)
                .send({
                    name: 'New Test User',
                    email: 'new@test.com',
                    password: 'password123',
                    role: 'user',
                });

            expect(res.statusCode).toBe(201);
            expect(res.body).toHaveProperty('success', true);
            expect(res.body.data).toHaveProperty('email', 'new@test.com');
        });

        it('PUT /api/admin/users/:id - should allow an admin to update a user', async () => {
            const res = await request(app)
                .put(`/api/admin/users/${testUserId}`)
                .set('Authorization', `Bearer ${adminToken}`)
                .send({ name: 'Updated Name' });

            expect(res.statusCode).toBe(200);
            expect(res.body).toHaveProperty('success', true);
            expect(res.body.data).toHaveProperty('name', 'Updated Name');
        });

        it('DELETE /api/admin/users/:id - should allow an admin to delete a user', async () => {
            const res = await request(app)
                .delete(`/api/admin/users/${testUserId}`)
                .set('Authorization', `Bearer ${adminToken}`);

            expect(res.statusCode).toBe(200);
            expect(res.body).toHaveProperty('success', true);
            expect(res.body).toHaveProperty('message', 'User removed');
        });

        it('DELETE /api/admin/users/:id - should be forbidden for non-admins', async () => {
            const res = await request(app)
                .delete(`/api/admin/users/${testUserId}`)
                .set('Authorization', `Bearer ${userToken}`);

            expect(res.statusCode).toBe(403);
        });
    });
});
