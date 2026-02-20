const mongoose = require('mongoose');

test('mongoose works', () => {
    const schema = new mongoose.Schema({ name: String });
    const Model = mongoose.model('SimpleTest', schema);
    
    console.log('Model type:', typeof Model);
    console.log('Model is function:', typeof Model === 'function');
    
    expect(typeof Model).toBe('function');
});
