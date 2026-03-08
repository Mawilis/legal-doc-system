/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     ██╗     ║
  ║ ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     ██║     ║
  ║ ██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     ██║     ║
  ║ ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     ██║     ║
  ║ ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗███████╗║
  ║  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝║
  ║                                                                           ║
  ║              ENTERPRISE API GATEWAY CONTROLLER                           ║
  ║                 (Routing Layer - No Business Logic)                       ║
  ║                                                                           ║
  ║  COLLABORATION: Lead Architect - Wilson Khanyezi                         ║
  ║  VERSION: 1.0.0-CONTROLLER                                               ║
  ║  PURPOSE: HTTP Request Routing to Service Layer                          ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { EnterpriseGateway } from '../../enterprise/apiGateway.js';

// Singleton instance of the service layer
let gatewayInstance = null;

/**
 * @class EnterpriseGatewayController
 * @description CONTROLLER LAYER ONLY - Routes requests to service layer
 * No business logic here - pure routing and HTTP handling
 */
export class EnterpriseGatewayController {
  constructor() {
    // Initialize service layer on first use
    if (!gatewayInstance) {
      gatewayInstance = new EnterpriseGateway({
        cacheSizeLimit: 300,
        defaultQpsLimit: 1000
      });
    }
    this.service = gatewayInstance;
  }

  /**
   * @route POST /api/enterprise/tenant
   * @description Register a new tenant
   */
  async registerTenant(req, res) {
    try {
      const { tenantId, tier } = req.body;
      const tenant = this.service.registerTenant(tenantId, tier);
      res.status(201).json({
        success: true,
        data: tenant,
        message: 'Tenant registered successfully'
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        error: error.message
      });
    }
  }

  /**
   * @route POST /api/enterprise/authenticate
   * @description Authenticate a request
   */
  async authenticate(req, res) {
    try {
      const { tenantId, apiKey, signature, message } = req.body;
      const result = await this.service.authenticate(
        tenantId, apiKey, signature, message
      );
      
      if (result.authenticated) {
        res.status(200).json({
          success: true,
          data: result
        });
      } else {
        res.status(401).json({
          success: false,
          error: result.reason
        });
      }
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  /**
   * @route GET /api/enterprise/ratelimit/:tenantId
   * @description Check rate limit
   */
  async checkRateLimit(req, res) {
    try {
      const { tenantId } = req.params;
      const result = this.service.checkRateLimit(tenantId);
      
      res.status(200).json({
        success: true,
        data: result,
        headers: {
          'X-RateLimit-Limit': result.limit,
          'X-RateLimit-Remaining': result.remaining,
          'X-RateLimit-Reset': result.retryAfter || 0
        }
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  /**
   * @route POST /api/enterprise/cache/get
   * @description Get cached result
   */
  async getCachedResult(req, res) {
    try {
      const { queryId } = req.body;
      const result = await this.service.getCachedResult(queryId);
      
      if (result) {
        res.status(200).json({
          success: true,
          data: result,
          source: 'cache'
        });
      } else {
        res.status(404).json({
          success: false,
          error: 'Not found in cache'
        });
      }
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  /**
   * @route POST /api/enterprise/cache/set
   * @description Set cache value
   */
  async setCache(req, res) {
    try {
      const { queryId, data, confidence } = req.body;
      this.service.setCache(queryId, data, confidence);
      
      res.status(200).json({
        success: true,
        message: 'Cache set successfully'
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  /**
   * @route GET /api/enterprise/metrics
   * @description Get gateway metrics
   */
  async getMetrics(req, res) {
    try {
      const metrics = this.service.getMetrics();
      res.status(200).json({
        success: true,
        data: metrics
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  /**
   * @route GET /api/enterprise/health
   * @description Health check
   */
  async health(req, res) {
    try {
      const health = this.service.health();
      const statusCode = health.status === 'OPERATIONAL' ? 200 : 503;
      
      res.status(statusCode).json({
        success: true,
        data: health
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  /**
   * @route POST /api/enterprise/cache/clear
   * @description Clear cache (testing only)
   */
  async clearCache(req, res) {
    try {
      this.service.clearCache();
      res.status(200).json({
        success: true,
        message: 'Cache cleared'
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }
}

// Export controller instance factory
export const createController = () => new EnterpriseGatewayController();
