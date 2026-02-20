const mongoose = require('mongoose');

describe('Final Test', () => {
    beforeAll(() => {
        // Ensure mongoose is properly loaded
        console.log('Mongoose version:', mongoose.version);
    });

    test('mongoose model is constructor', () => {
        const schema = new mongoose.Schema({ name: String });
        const Model = mongoose.model('FinalTest', schema);
        
        console.log('Model type:', typeof Model);
        console.log('Model prototype:', !!Model.prototype);
        console.log('Model constructor:', Model.constructor.name);
        
        expect(typeof Model).toBe('function');
        expect(Model.prototype).toBeDefined();
    });
});
