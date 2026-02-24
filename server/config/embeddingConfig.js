/* eslint-disable */
/*
 * File: /Users/wilsonkhanyezi/legal-doc-system/server/config/embeddingConfig.js
 * PATH: /server/config/embeddingConfig.js
 * STATUS: QUANTUM-FORTIFIED | ENTERPRISE-GRADE | HYPER-SCALE
 * VERSION: 42.0.0 (Wilsy OS Embedding Configuration)
 * -----------------------------------------------------------------------------
 */

module.exports = {
  // Model configuration
  model: {
    default: process.env.DEFAULT_EMBEDDING_MODEL || 'legal-bert',
    dimension: parseInt(process.env.EMBEDDING_DIMENSION) || 768,
    available: ['legal-bert', 'legal-roberta', 'legal-electra', 'universal', 'mini-lm', 'custom'],
    fallback: 'mini-lm',
  },

  // Hardware acceleration
  hardware: {
    enableGpu: process.env.ENABLE_GPU === 'true',
    gpuMemoryFraction: parseFloat(process.env.GPU_MEMORY_FRACTION) || 0.8,
    cudaDevices: process.env.CUDA_VISIBLE_DEVICES || '0',
    enableTensorCores: process.env.ENABLE_TENSOR_CORES === 'true',
    enableMixedPrecision: process.env.ENABLE_MIXED_PRECISION === 'true',
  },

  // Performance tuning
  performance: {
    concurrency: parseInt(process.env.WORKER_CONCURRENCY) || 4,
    batchSize: parseInt(process.env.EMBEDDING_BATCH_SIZE) || 32,
    preloadModels: process.env.PRELOAD_MODELS === 'true',
    rateLimit: {
      enabled: process.env.ENABLE_RATE_LIMITING === 'true',
      max: parseInt(process.env.RATE_LIMIT_MAX) || 100,
      duration: parseInt(process.env.RATE_LIMIT_DURATION) || 1000,
    },
    stalledInterval: parseInt(process.env.STALLED_INTERVAL_MS) || 30000,
    maxStalledCount: parseInt(process.env.MAX_STALLED_COUNT) || 2,
    lockDuration: parseInt(process.env.LOCK_DURATION_MS) || 60000,
    lockRenewTime: parseInt(process.env.LOCK_RENEW_TIME_MS) || 30000,
  },

  // Caching
  cache: {
    enabled: process.env.ENABLE_CACHING !== 'false',
    ttl: parseInt(process.env.CACHE_TTL_SECONDS) || 86400,
    strategy: process.env.CACHE_STRATEGY || 'multi-level',
    compression: process.env.CACHE_COMPRESSION || 'zstd',
    maxSize: parseInt(process.env.CACHE_MAX_SIZE) || 100000,
  },

  // Circuit breaker
  circuitBreaker: {
    timeout: parseInt(process.env.CIRCUIT_BREAKER_TIMEOUT) || 30000,
    errorThreshold: parseInt(process.env.CIRCUIT_BREAKER_THRESHOLD) || 50,
    resetTimeout: parseInt(process.env.CIRCUIT_BREAKER_RESET) || 60000,
    volumeThreshold: parseInt(process.env.CIRCUIT_BREAKER_VOLUME) || 5,
  },

  // Quality control
  quality: {
    minStd: parseFloat(process.env.MIN_EMBEDDING_STD) || 0.01,
    validateDimensions: process.env.VALIDATE_DIMENSIONS !== 'false',
    enableValidation: process.env.ENABLE_EMBEDDING_VALIDATION !== 'false',
  },

  // Storage
  storage: {
    compressVectors: process.env.COMPRESS_VECTORS === 'true',
    compressionLevel: parseInt(process.env.COMPRESSION_LEVEL) || 3,
    vectorDb: process.env.VECTOR_DB || 'milvus',
    storeInMongo: process.env.STORE_IN_MONGO === 'true',
    storeInRedis: process.env.STORE_IN_REDIS !== 'false',
  },

  // Monitoring
  monitoring: {
    metricsPort: parseInt(process.env.METRICS_PORT) || 9094,
    enablePrometheus: process.env.ENABLE_PROMETHEUS !== 'false',
    logPerformance: process.env.LOG_PERFORMANCE === 'true',
    slowJobThreshold: parseInt(process.env.SLOW_JOB_THRESHOLD) || 5000,
  },

  // Tenant isolation
  tenant: {
    enableQuotas: process.env.ENABLE_TENANT_QUOTAS === 'true',
    defaultQuota: parseInt(process.env.DEFAULT_TENANT_QUOTA) || 1000000,
    enableIsolation: process.env.ENABLE_TENANT_ISOLATION !== 'false',
  },
};
