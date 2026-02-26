/* eslint-disable */
/*
 * WILSY OS: GATEWAY CONFIGURATION - CENTRALIZED GATEWAY SETTINGS
 * ============================================================================
 *
 * This file centralizes all gateway configuration for easy management
 * and consistent access across the international gateway middleware.
 *
 * @version 42.0.0
 * ============================================================================
 */

import dotenv from 'dotenv.js';
import path from "path";

// Load environment variables
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

export const GATEWAY_CONFIG = Object.freeze({
  // Rate limits (requests per hour)
  rateLimits: {
    free: parseInt(process.env.INTERNATIONAL_FREE_RATE_LIMIT) || 10,
    basic: parseInt(process.env.INTERNATIONAL_BASIC_RATE_LIMIT) || 100,
    premium: parseInt(process.env.INTERNATIONAL_PREMIUM_RATE_LIMIT) || 500,
    ultra_premium: parseInt(process.env.INTERNATIONAL_ULTRA_PREMIUM_RATE_LIMIT) || 2000,
    enterprise: parseInt(process.env.INTERNATIONAL_ENTERPRISE_RATE_LIMIT) || 10000,
  },

  // Price multipliers
  multipliers: {
    free: parseFloat(process.env.INTERNATIONAL_FREE_MULTIPLIER) || 1,
    basic: parseFloat(process.env.INTERNATIONAL_BASIC_MULTIPLIER) || 2,
    premium: parseFloat(process.env.INTERNATIONAL_PREMIUM_MULTIPLIER) || 5,
    ultra_premium: parseFloat(process.env.INTERNATIONAL_ULTRA_PREMIUM_MULTIPLIER) || 10,
    enterprise: parseFloat(process.env.INTERNATIONAL_ENTERPRISE_MULTIPLIER) || 20,
  },

  // Base price
  basePrice: parseFloat(process.env.INTERNATIONAL_BASE_QUERY_PRICE) || 10,

  // Cache TTLs (seconds)
  cacheTTL: {
    analysis: parseInt(process.env.INTERNATIONAL_CACHE_TTL_ANALYSIS) || 7200,
    profile: parseInt(process.env.INTERNATIONAL_CACHE_TTL_PROFILE) || 3600,
    trending: parseInt(process.env.INTERNATIONAL_CACHE_TTL_TRENDING) || 1800,
  },

  // Window sizes (seconds)
  windows: {
    standard: 3600, // 1 hour
    burst: 60, // 1 minute
    daily: 86400, // 24 hours
  },

  // Monthly budget limits (USD)
  monthlyBudgets: {
    basic: 1000,
    premium: 5000,
    ultra_premium: 20000,
    enterprise: 100000,
  },

  // Operation costs multipliers
  operationCosts: {
    standard: 1,
    compare: 2,
    batch: 5,
    deep: 1.5,
    comprehensive: 2,
    history: 1.2,
  },

  // Supported currencies
  currencies: ['USD', 'EUR', 'GBP', 'ZAR'],

  // Gateway features by tier
  features: {
    free: {
      maxJurisdictions: 2,
      maxDepth: 'standard',
      exportFormats: ['json'],
      cacheEnabled: true,
    },
    basic: {
      maxJurisdictions: 5,
      maxDepth: 'deep',
      exportFormats: ['json', 'csv'],
      cacheEnabled: true,
    },
    premium: {
      maxJurisdictions: 10,
      maxDepth: 'comprehensive',
      exportFormats: ['json', 'csv', 'pdf'],
      cacheEnabled: true,
      priority: true,
    },
    ultra_premium: {
      maxJurisdictions: 20,
      maxDepth: 'forensic',
      exportFormats: ['json', 'csv', 'pdf', 'docx'],
      cacheEnabled: true,
      priority: true,
      dedicated: true,
    },
    enterprise: {
      maxJurisdictions: 50,
      maxDepth: 'forensic',
      exportFormats: ['json', 'csv', 'pdf', 'docx', 'xml'],
      cacheEnabled: true,
      priority: true,
      dedicated: true,
      custom: true,
    },
  },
});
