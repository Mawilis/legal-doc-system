const mongoose = require('mongoose');

describe('Working Test', () => {
    test('mongoose basics work', () => {
        // Basic mongoose functionality
        expect(mongoose).toBeDefined();
        expect(mongoose.Schema).toBeDefined();
        
        // Create schema and model
        const schema = new mongoose.Schema({ name: String });
        const Model = mongoose.model('Test', schema);
        
        // In Mongoose 8, Model is a function
        expect(typeof Model).toBe('function');
        
        // Create instance
        const doc = new Model({ name: 'test' });
        expect(doc).toBeDefined();
        expect(doc.name).toBe('test');
        
        // Check methods
        expect(typeof doc.save).toBe('function');
        expect(typeof doc.validate).toBe('function');
    });
});
