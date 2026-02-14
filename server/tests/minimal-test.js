/* eslint-env jest */

describe('Minimal Test', () => {
    it('should import lpcService', () => {
        const lpcService = require('../services/lpcService');
        expect(lpcService).toBeDefined();
        console.log('✅ lpcService imported successfully');
    });
});
