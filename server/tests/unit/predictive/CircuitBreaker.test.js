/* eslint-disable */
import { expect } from 'chai';
import { QuantumCircuitBreaker } from '../../../utils/circuitBreaker.js';

describe('🛡️ QuantumCircuitBreaker - Unit Tests', () => {
  let breaker;

  beforeEach(() => {
    breaker = new QuantumCircuitBreaker({
      failureThreshold: 3,
      timeout: 100,
      cooldown: 1000
    });
  });

  it('should start in CLOSED state', () => {
    expect(breaker.state).to.equal('CLOSED');
  });

  it('should execute successful operations', async () => {
    const result = await breaker.execute(async () => 'success');
    expect(result).to.equal('success');
    expect(breaker.failures).to.equal(0);
  });

  it('should open after threshold failures', async () => {
    const failingFn = async () => { throw new Error('fail'); };
    
    for (let i = 0; i < 3; i++) {
      try {
        await breaker.execute(failingFn);
      } catch (e) {}
    }
    
    expect(breaker.state).to.equal('OPEN');
    expect(breaker.failures).to.equal(3);
  });

  it('should use fallback when open', async () => {
    for (let i = 0; i < 3; i++) {
      try {
        await breaker.execute(async () => { throw new Error('fail'); });
      } catch (e) {}
    }
    
    const fallback = async () => 'fallback';
    const result = await breaker.execute(
      async () => { throw new Error('fail'); },
      { fallback }
    );
    
    expect(result).to.equal('fallback');
  });

  it('should provide metrics', () => {
    const metrics = breaker.getMetrics();
    expect(metrics).to.have.property('state');
    expect(metrics).to.have.property('failures');
    expect(metrics).to.have.property('successRate');
  });
});
