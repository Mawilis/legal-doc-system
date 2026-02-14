/* eslint-env jest */
const { PerformanceMonitor } = require('../utils/performance');

describe('PerformanceMonitor', () => {
    it('should measure function execution time', async () => {
        const pm = new PerformanceMonitor();
        const result = await pm.measure('test', async () => {
            await new Promise(resolve => setTimeout(resolve, 10));
            return 'done';
        });
        expect(result).toBe('done');
    });

    it('should start and end timers', () => {
        const pm = new PerformanceMonitor();
        pm.startTimer('test');
        const duration = pm.endTimer('test');
        expect(duration).toBeGreaterThanOrEqual(0);
    });
});
