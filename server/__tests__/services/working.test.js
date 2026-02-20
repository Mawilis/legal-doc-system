/**
 * @jest-environment node
 */
'use strict';

// 1. FORBID JEST FROM MOCKING MONGOOSE
jest.unmock('mongoose');
const mongoose = require('mongoose');

describe('Wilsy OS - Core Model Integrity', () => {
    
    // Clear registry to avoid name collisions
    beforeAll(() => {
        mongoose.models = {};
        mongoose.modelSchemas = {};
    });

    test('Mongoose Compiler Integrity: Should return Function (Constructor)', () => {
        const schema = new mongoose.Schema({ 
            testField: String 
        });
        
        // Use a unique name to ensure a fresh compile
        const ModelName = 'IntegrityTest_' + Date.now();
        const TestModel = mongoose.model(ModelName, schema);

        console.log('INTERNAL TYPE CHECK:', typeof TestModel);
        
        // This is the production-ready requirement
        expect(typeof TestModel).toBe('function');
        
        const instance = new TestModel({ testField: 'validated' });
        expect(instance.testField).toBe('validated');
    });
});
