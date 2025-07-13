// server/tests/user.test.js
const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../app');
const User = require('../models/userModel');

let adminToken;
let createdUserId;

const timestamp = Date.now();
const adminUser = {
    name: 'Admin User',
    email: `admin-${timestamp}@example.com`,
    password: 'adminpass123',
    role: 'admin'
};

const newUser = {
    name: 'Test User',
    email: `testuser-${timestamp}@example.com`,
    password: 'password123',
    role: 'user'
};

beforeAll(async () => {
    console.log('🧹 Cleaning up users...');
    await User.deleteMany({ email: /@example\.com$/ });

    console.log('👤 Creating admin user directly...');
    const admin = await new User(adminUser).save();
    console.log('✅ Admin saved to DB:', admin.email);

    console.log('🔐 Logging in as admin...');
    const loginRes = await request(app).post('/api/auth/login').send({
        email: admin.email,
        password: adminUser.password
    });

    adminToken = loginRes.body.token;
    console.log('🔑 Admin Token:', adminToken);

    const userExists = await User.findOne({ email: admin.email });
    console.log('🟢 Confirmed user exists in DB:', userExists.email);
});

afterAll(async () => {
    console.log('🧹 Final cleanup...');
    if (mongoose.connection.readyState === 1) {
        await User.deleteMany({ email: /@example\.com$/ });
        await mongoose.disconnect();
    } else {
        console.warn('⚠️ Skipped cleanup: Mongoose not connected');
    }
});

describe('User API (Admin Only)', () => {
    it('should create a new user as admin', async () => {
        const res = await request(app)
            .post('/api/users')
            .set('Authorization', `Bearer ${adminToken}`)
            .send(newUser);

        console.log('🧪 Create user response:', res.body);
        expect(res.statusCode).toBe(201);
        expect(res.body.data.email).toBe(newUser.email);
    });

    it('should get all users', async () => {
        const res = await request(app)
            .get('/api/users')
            .set('Authorization', `Bearer ${adminToken}`);

        console.log('📋 Get users response:', res.statusCode, res.body);
        expect(res.statusCode).toBe(200);
        expect(res.body.count).toBeGreaterThan(0);
    });

    it('should update a user', async () => {
        const user = await User.findOne({ email: newUser.email });
        const res = await request(app)
            .put(`/api/users/${user._id}`)
            .set('Authorization', `Bearer ${adminToken}`)
            .send({ name: 'Updated User' });

        console.log('✏️ Update user response:', res.statusCode, res.body);
        expect(res.statusCode).toBe(200);
        expect(res.body.data.name).toBe('Updated User');
    });

    it('should delete a user', async () => {
        const user = await User.findOne({ email: newUser.email });
        const res = await request(app)
            .delete(`/api/users/${user._id}`)
            .set('Authorization', `Bearer ${adminToken}`);

        console.log('🗑️ Delete user response:', res.statusCode);
        expect(res.statusCode).toBe(200);
    });
});
