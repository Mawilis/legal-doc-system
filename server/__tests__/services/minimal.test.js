const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

describe('Minimal Test', () => {
    let mongoServer;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        console.log('✅ MongoDB connected');
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    test('database works', async () => {
        // Define schema
        const testSchema = new mongoose.Schema({
            name: { type: String, required: true }
        });

        // Create model - this returns a Model constructor
        const Test = mongoose.model('Test', testSchema);
        
        // Verify Test is a function (constructor)
        console.log('Test type:', typeof Test);
        console.log('Test prototype:', !!Test.prototype);
        
        // Create document using the model constructor
        const doc = new Test({ name: 'test' });
        await doc.save();
        
        // Verify it worked
        expect(doc.name).toBe('test');
        expect(doc._id).toBeDefined();
        
        // Find the document
        const found = await Test.findOne({ name: 'test' });
        expect(found).toBeDefined();
        expect(found.name).toBe('test');
        
        console.log('✅ Test passed');
    });
});
