/**
 * @jest-environment node
 */
'use strict';

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

describe('Simple Model Test', () => {
    let mongoServer;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        console.log('✅ Database connected');
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    test('Mongoose works', () => {
        expect(mongoose).toBeDefined();
        expect(mongoose.Schema).toBeDefined();
    });

    test('Can create schema and model', () => {
        const schema = new mongoose.Schema({ name: String });
        const Model = mongoose.model('Test', schema);
        
        // In Mongoose 8, Model is a function
        console.log('Model type:', typeof Model);
        
        // Create instance
        const doc = new Model({ name: 'test' });
        expect(doc).toBeDefined();
        expect(doc.name).toBe('test');
    });
});
