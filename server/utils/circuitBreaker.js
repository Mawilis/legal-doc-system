/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ CIRCUIT BREAKER - FAULT TOLERANCE                                         ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

class CircuitBreaker {
  constructor(name, options = {}) {
    this.name = name;
    this.failureCount = 0;
    this.successCount = 0;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.nextAttempt = Date.now();
    
    this.options = {
      timeout: options.timeout || 30000,
      errorThresholdPercentage: options.errorThresholdPercentage || 50,
      resetTimeout: options.resetTimeout || 30000,
      ...options
    };
  }

  async fire(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() > this.nextAttempt) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error(`Circuit breaker is OPEN for ${this.name}`);
      }
    }

    try {
      const result = await Promise.race([
        fn(),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), this.options.timeout)
        )
      ]);
      
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    this.successCount++;
    
    if (this.state === 'HALF_OPEN') {
      this.state = 'CLOSED';
    }
  }

  onFailure() {
    this.failureCount++;
    
    const errorRate = (this.failureCount / (this.failureCount + this.successCount)) * 100;
    
    if (errorRate >= this.options.errorThresholdPercentage || this.state === 'HALF_OPEN') {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.options.resetTimeout;
    }
  }

  getStatus() {
    return {
      name: this.name,
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      nextAttempt: this.nextAttempt
    };
  }
}

export { CircuitBreaker };
