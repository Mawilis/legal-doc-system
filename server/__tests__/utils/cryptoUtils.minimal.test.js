/* eslint-env jest */
const cryptoUtils = require('../../utils/cryptoUtils');

describe('CRYPTO UTILITIES - MINIMAL EXPORT TEST', () => {
    test('all exports should be defined', () => {
        console.log('Exports:', Object.keys(cryptoUtils));
        
        expect(cryptoUtils.REDACT_FIELDS).toBeDefined();
        expect(cryptoUtils.generateHash).toBeDefined();
        expect(cryptoUtils.createDigitalSignature).toBeDefined();
        expect(cryptoUtils.verifySignature).toBeDefined();
        expect(cryptoUtils.redactSensitive).toBeDefined();
        expect(cryptoUtils.generateRandomBytes).toBeDefined();
        expect(cryptoUtils.calculateHMAC).toBeDefined();
    });

    test('generateHash should work', () => {
        const hash = cryptoUtils.generateHash('test');
        expect(hash).toBeDefined();
        expect(hash.length).toBe(64);
        console.log('✅ generateHash works:', hash.substring(0, 10) + '...');
    });
});
