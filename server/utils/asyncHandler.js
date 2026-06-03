/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║  SOVEREIGN ASYNC HANDLER - WILSY OS 2050                                  ║
 * ║  Enterprise-grade async error boundary with forensic capabilities         ║
 * ║  Supreme Architect: Wilson Khanyezi - 10th Generation                     ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import { performance } from 'perf_hooks';

/**
 * Sovereign Async Handler with performance tracking and error enrichment
 * @param {Function} fn - Async route handler function
 */
export const asyncHandler = (fn) => {
  return (req, res, next) => {
    const startTime = performance.now();

    // Execute the handler and catch errors for the global error boundary
    Promise.resolve(fn(req, res, next)).catch((err) => {
      // Enrich error with high-resolution timing data
      const duration = performance.now() - startTime;
      err.executionDuration = `${duration.toFixed(2)}ms`;
      err.requestId = req.id || req.requestId;
      next(err);
    });
  };
};

export default asyncHandler;
