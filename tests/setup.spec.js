/* eslint-disable */
/**
 * tests/setup.spec.js
 * Quick assertions to verify the test bootstrap is active and usable.
 */

import { expect } from 'chai';

describe('test environment bootstrap', () => {
    it('provides DOM globals', () => {
        expect(typeof globalThis.window).to.equal('object');
        expect(typeof globalThis.document).to.equal('object');
        expect(typeof globalThis.navigator).to.equal('object');
        expect(typeof globalThis.navigator.userAgent).to.equal('string');
    });

    it('provides storage mocks', () => {
        expect(globalThis.localStorage).to.be.an('object');
        expect(typeof globalThis.localStorage.setItem).to.equal('function');
        globalThis.localStorage.setItem('x', '1');
        expect(globalThis.localStorage.getItem('x')).to.equal('1');
        globalThis.localStorage.removeItem('x');
        expect(globalThis.localStorage.getItem('x')).to.equal(null);
    });

    it('provides performance and raf shims', () => {
        expect(typeof globalThis.performance.now).to.equal('function');
        expect(typeof globalThis.requestAnimationFrame).to.equal('function');
        expect(typeof globalThis.cancelAnimationFrame).to.equal('function');
    });

    it('provides a fetch polyfill', async () => {
        expect(typeof globalThis.fetch).to.equal('function');
        const res = await globalThis.fetch('/');
        expect(res).to.have.property('ok');
    });
});
