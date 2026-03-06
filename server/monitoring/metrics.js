#!/* eslint-disable */
/* ╔═══════════════════════════════════════════════════════════════════════════╗
  ║ METRICS COLLECTOR - PRODUCTION MONITORING                                 ║
  ╚═══════════════════════════════════════════════════════════════════════════╝ */

class MetricsCollector {
  constructor() {
    this.metrics = {
      documentGenerations: [],
      templateCompilations: [],
      errors: [],
      performance: {},
    };
  }

  static getInstance() {
    if (!MetricsCollector.instance) {
      MetricsCollector.instance = new MetricsCollector();
    }
    return MetricsCollector.instance;
  }

  recordDocumentGeneration(data) {
    this.metrics.documentGenerations.push({
      ...data,
      timestamp: new Date().toISOString(),
    });

    // Keep only last 1000 records
    if (this.metrics.documentGenerations.length > 1000) {
      this.metrics.documentGenerations.shift();
    }
  }

  recordError(error) {
    this.metrics.errors.push({
      message: error.message,
      code: error.code,
      timestamp: new Date().toISOString(),
    });
  }

  getSnapshot() {
    return {
      totalGenerations: this.metrics.documentGenerations.length,
      totalErrors: this.metrics.errors.length,
      recentGenerations: this.metrics.documentGenerations.slice(-10),
      recentErrors: this.metrics.errors.slice(-10),
    };
  }

  reset() {
    this.metrics = {
      documentGenerations: [],
      templateCompilations: [],
      errors: [],
      performance: {},
    };
  }
}

export { MetricsCollector };
