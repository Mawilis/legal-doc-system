/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ QUEUE CONFIGURATION - INVESTOR-GRADE MODULE                               ║
  ║ BullMQ configuration for all workers                                      ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { Queue, Worker, QueueScheduler } from 'bullmq';

export const redisConfig = {
  connection: {
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD,
    retryStrategy: (times) => Math.min(times * 50, 2000),
    maxRetriesPerRequest: 3
  }
};

export const defaultJobOptions = {
  attempts: 3,
  backoff: {
    type: 'exponential',
    delay: 5000
  },
  removeOnComplete: 100,
  removeOnFail: 500
};

export const createQueue = (name) => new Queue(name, {
  ...redisConfig,
  defaultJobOptions
});

export const createWorker = (name, processor) => new Worker(name, processor, {
  ...redisConfig,
  concurrency: 5,
  limiter: {
    max: 100,
    duration: 1000
  }
});

export const createScheduler = (name) => new QueueScheduler(name, redisConfig);

export default {
  redisConfig,
  defaultJobOptions,
  createQueue,
  createWorker,
  createScheduler
};
