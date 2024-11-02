// File: ~legal-doc-system/tests/userModel.test.js

const mongoose = require('mongoose');
const User = require('../models/userModel');
const { MongoMemoryServer } = require('mongodb-memory-server');

let mongoServer;

beforeAll(async () => {
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    await mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true });
});

afterAll(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
});

describe('User Model', () => {
    it('should hash the password before saving', async () => {
        const user = new User({ name: 'John Doe', email: 'john@example.com', password: 'Password1!' });
        await user.save();
        expect(user.password).not.toBe('Password1!');
    });

    it('should validate password correctly', async () => {
        const user = new User({ name: 'Jane Doe', email: 'jane@example.com', password: 'Password1!' });
        await user.save();

        const isValid = await user.comparePassword('Password1!');
        expect(isValid).toBe(true);
    });

    it('should create a password reset token', () => {
        const user = new User({ name: 'Jake', email: 'jake@example.com', password: 'Password1!' });
        const resetToken = user.createPasswordResetToken();
        expect(resetToken).toBeDefined();
        expect(user.passwordResetToken).not.toBe(resetToken); // Stored hashed version of resetToken
    });
});
