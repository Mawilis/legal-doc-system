/* eslint-disable */
/*
 * WILSY OS: HEALTH CHECK CRON JOB
 * Regular system health monitoring and alerting
 */

import cron from 'node-cron.js';
import { getSystemHealth } from '../services/system/HealthService.js';
import { sendAlert } from '../services/alerting/AlertService.js';
import loggerRaw from '../utils/logger.js';
const logger = loggerRaw.default || loggerRaw;
import quantumLogger from '../utils/quantumLogger.js';
import { metrics } from '../utils/metricsCollector.js';

// Schedule health check every 5 minutes
export const scheduleHealthChecks = () => {
  cron.schedule(
    '*/5 * * * *',
    async () => {
      const startTime = Date.now();

      logger.info('Running scheduled health check');

      try {
        const health = await getSystemHealth({
          depth: 'standard',
          includePredictive: true,
        });

        const duration = Date.now() - startTime;

        // Log health check
        await quantumLogger.log({
          event: 'CRON_HEALTH_CHECK',
          status: health.status,
          issues: health.issues.length,
          warnings: health.warnings.length,
          duration,
          timestamp: new Date().toISOString(),
        });

        metrics.gauge(
          'cron.health.status',
          health.status === 'OPTIMAL'
            ? 4
            : health.status === 'HEALTHY'
              ? 3
              : health.status === 'DEGRADED'
                ? 2
                : health.status === 'CRITICAL'
                  ? 1
                  : 0
        );

        // Send alerts for critical issues
        if (health.status === 'CRITICAL') {
          await sendAlert({
            severity: 'CRITICAL',
            title: 'System Health Critical',
            message: `Health check detected critical issues`,
            details: health.issues,
            timestamp: new Date().toISOString(),
          });
        } else if (health.status === 'DEGRADED' && health.warnings.length > 0) {
          await sendAlert({
            severity: 'WARNING',
            title: 'System Health Degraded',
            message: `Health check detected ${health.warnings.length} warnings`,
            details: health.warnings,
            timestamp: new Date().toISOString(),
          });
        }

        logger.info('Scheduled health check completed', {
          status: health.status,
          duration,
          issues: health.issues.length,
        });
      } catch (error) {
        logger.error('Scheduled health check failed', {
          error: error.message,
          duration: Date.now() - startTime,
        });

        metrics.increment('cron.health.error');
      }
    },
    {
      scheduled: true,
      timezone: 'Africa/Johannesburg',
    }
  );

  logger.info('Health check cron scheduled for every 5 minutes');
};

export default {
  scheduleHealthChecks,
};
