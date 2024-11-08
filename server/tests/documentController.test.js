const request = require('supertest');
const app = require('../server');  // Assuming your main server file is named server.js
const Document = require('../models/documentModel');
const mongoose = require('mongoose');

beforeAll(async () => {
    // Connect to a test database
    const MONGO_URI = process.env.MONGO_URI_TEST;
    await mongoose.connect(MONGO_URI, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
    });
});

afterAll(async () => {
    // Disconnect after tests
    await mongoose.connection.close();
});

describe('Document Controller', () => {
    let token;

    beforeEach(async () => {
        // Mock user login and obtain JWT token
        const res = await request(app)
            .post('/api/users/login')
            .send({ email: 'testuser@example.com', password: 'password' });
        token = res.body.token;
    });

    it('should create a new document', async () => {
        const res = await request(app)
            .post('/api/documents')
            .set('Authorization', `Bearer ${token}`)
            .send({ title: 'New Document', content: 'Document content' });

        expect(res.statusCode).toEqual(201);
        expect(res.body.title).toBe('New Document');
    });

    it('should update a document service status', async () => {
        const newDoc = new Document({ title: 'Service Update Test', content: 'Some content' });ß
        await newDoc.save();

        const res = await request(app)
            .put(`/api/documents/${newDoc._id}/status`)
            .set('Authorization', `Bearer ${token}`)
            .send({ status: 'Served' });

        expect(res.statusCode).toEqual(200);
        expect(res.body.serviceStatus).toBe('Served');
    });
});
