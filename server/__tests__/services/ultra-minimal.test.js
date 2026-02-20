const mongoose = require('mongoose');

describe('Ultra Minimal Test', () => {
    test('mongoose is available', () => {
        expect(mongoose).toBeDefined();
        expect(mongoose.Schema).toBeDefined();
        expect(mongoose.model).toBeDefined();
    });

    test('can create schema and model', () => {
        const schema = new mongoose.Schema({ name: String });
        const Model = mongoose.model('Test', schema);
        expect(Model).toBeDefined();
        
        // In Mongoose 8, the model is an object
        expect(typeof Model).toBe('object');
        
        // Check that it has the expected methods
        expect(Model.prototype).toBeDefined();
        expect(Model.prototype.constructor).toBeDefined();
        expect(Model.prototype.save).toBeDefined();
        
        // Test we can create an instance
        const doc = new Model({ name: 'test' });
        expect(doc).toBeDefined();
        expect(doc.name).toBe('test');
        
        // Verify it has the expected methods
        expect(typeof doc.save).toBe('function');
    });
});
