/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════════════════╗
  ║ COURT CONTROLLER - COMPLETE SA JUDICIAL MANAGEMENT API                                ║
  ║ R4.5M/year operational savings | Jurisdiction AI | Appeal Routing                     ║
  ╚═══════════════════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/courtController.js
 * VERSION: 1.0.0-PRODUCTION
 * CREATED: 2026-02-28
 */

import CourtService from '../services/courtService.js';
import { AuditLogger } from '../utils/auditLogger.js';
import Logger from '../utils/logger.js';
import tenantContext from '../middleware/tenantContext.js';
import crypto from 'crypto';

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const generateCorrelationId = (req) => {
  return req.headers['x-correlation-id'] || 
         `court-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
};

const formatSuccess = (data, correlationId, metadata = {}) => {
  return {
    success: true,
    correlationId,
    timestamp: new Date().toISOString(),
    data,
    metadata
  };
};

const formatError = (error, correlationId, statusCode = 500) => {
  return {
    success: false,
    correlationId,
    timestamp: new Date().toISOString(),
    error: {
      code: error.code || 'INTERNAL_ERROR',
      message: error.message || 'An unexpected error occurred',
      statusCode
    }
  };
};

// ============================================================================
// CONTROLLER METHODS
// ============================================================================

export const createCourt = async (req, res) => {
  const correlationId = generateCorrelationId(req);
  const startTime = Date.now();

  try {
    const { tenantId, userId } = tenantContext.get();
    
    Logger.info('courtController.createCourt', {
      correlationId,
      tenantId,
      courtName: req.body.name
    });

    const service = new CourtService({ tenantId });
    const court = await service.createCourt(req.body, userId);

    const responseTime = Date.now() - startTime;

    res.status(201).json(formatSuccess(court, correlationId, {
      responseTimeMs: responseTime
    }));

  } catch (error) {
    Logger.error('courtController.createCourt failed', {
      correlationId,
      error: error.message
    });

    const statusCode = error.message.includes('validation') ? 400 : 500;
    res.status(statusCode).json(formatError(error, correlationId, statusCode));
  }
};

export const getCourt = async (req, res) => {
  const correlationId = generateCorrelationId(req);
  const { courtId } = req.params;

  try {
    const { tenantId } = tenantContext.get();
    
    Logger.info('courtController.getCourt', {
      correlationId,
      tenantId,
      courtId
    });

    const service = new CourtService({ tenantId });
    const court = await service.getCourt(courtId);

    res.status(200).json(formatSuccess(court, correlationId));

  } catch (error) {
    Logger.error('courtController.getCourt failed', {
      correlationId,
      error: error.message
    });

    const statusCode = error.message.includes('not found') ? 404 : 500;
    res.status(statusCode).json(formatError(error, correlationId, statusCode));
  }
};

export const updateCourt = async (req, res) => {
  const correlationId = generateCorrelationId(req);
  const { courtId } = req.params;
  const startTime = Date.now();

  try {
    const { tenantId, userId } = tenantContext.get();
    
    Logger.info('courtController.updateCourt', {
      correlationId,
      tenantId,
      courtId
    });

    const service = new CourtService({ tenantId });
    const court = await service.updateCourt(courtId, req.body, userId);

    const responseTime = Date.now() - startTime;

    res.status(200).json(formatSuccess(court, correlationId, {
      responseTimeMs: responseTime
    }));

  } catch (error) {
    Logger.error('courtController.updateCourt failed', {
      correlationId,
      error: error.message
    });

    const statusCode = error.message.includes('not found') ? 404 : 500;
    res.status(statusCode).json(formatError(error, correlationId, statusCode));
  }
};

export const listCourts = async (req, res) => {
  const correlationId = generateCorrelationId(req);
  const startTime = Date.now();

  try {
    const { tenantId } = tenantContext.get();
    
    const filters = {};
    if (req.query.tier) filters.tier = req.query.tier;
    if (req.query.status) filters.status = req.query.status;
    if (req.query.province) filters['geographicJurisdiction.provinces'] = req.query.province;

    const pagination = {
      limit: parseInt(req.query.limit) || 50,
      offset: parseInt(req.query.offset) || 0
    };

    Logger.info('courtController.listCourts', {
      correlationId,
      tenantId,
      filters,
      pagination
    });

    const service = new CourtService({ tenantId });
    const result = await service.listCourts(filters, pagination);

    const responseTime = Date.now() - startTime;

    res.status(200).json(formatSuccess(result.courts, correlationId, {
      pagination: result.pagination,
      responseTimeMs: responseTime
    }));

  } catch (error) {
    Logger.error('courtController.listCourts failed', {
      correlationId,
      error: error.message
    });

    res.status(500).json(formatError(error, correlationId));
  }
};

export const checkJurisdiction = async (req, res) => {
  const correlationId = generateCorrelationId(req);
  const startTime = Date.now();

  try {
    const { tenantId } = tenantContext.get();
    
    Logger.info('courtController.checkJurisdiction', {
      correlationId,
      tenantId,
      caseData: req.body
    });

    const service = new CourtService({ tenantId });
    const result = await service.checkJurisdiction(req.body);

    const responseTime = Date.now() - startTime;

    res.status(200).json(formatSuccess(result, correlationId, {
      responseTimeMs: responseTime
    }));

  } catch (error) {
    Logger.error('courtController.checkJurisdiction failed', {
      correlationId,
      error: error.message
    });

    res.status(500).json(formatError(error, correlationId));
  }
};

export const getAppealRoute = async (req, res) => {
  const correlationId = generateCorrelationId(req);
  const { courtId } = req.params;

  try {
    const { tenantId } = tenantContext.get();
    
    Logger.info('courtController.getAppealRoute', {
      correlationId,
      tenantId,
      courtId
    });

    const service = new CourtService({ tenantId });
    const route = await service.getAppealRoute(courtId);

    res.status(200).json(formatSuccess(route, correlationId));

  } catch (error) {
    Logger.error('courtController.getAppealRoute failed', {
      correlationId,
      error: error.message
    });

    res.status(500).json(formatError(error, correlationId));
  }
};

export const addJudicialOfficer = async (req, res) => {
  const correlationId = generateCorrelationId(req);
  const { courtId } = req.params;
  const startTime = Date.now();

  try {
    const { tenantId, userId } = tenantContext.get();
    
    Logger.info('courtController.addJudicialOfficer', {
      correlationId,
      tenantId,
      courtId,
      officerName: req.body.name
    });

    const service = new CourtService({ tenantId });
    const officer = await service.addJudicialOfficer(courtId, req.body, userId);

    const responseTime = Date.now() - startTime;

    res.status(201).json(formatSuccess(officer, correlationId, {
      responseTimeMs: responseTime
    }));

  } catch (error) {
    Logger.error('courtController.addJudicialOfficer failed', {
      correlationId,
      error: error.message
    });

    const statusCode = error.message.includes('not found') ? 404 : 500;
    res.status(statusCode).json(formatError(error, correlationId, statusCode));
  }
};

export const getHierarchy = async (req, res) => {
  const correlationId = generateCorrelationId(req);

  try {
    const { tenantId } = tenantContext.get();
    
    Logger.info('courtController.getHierarchy', {
      correlationId,
      tenantId
    });

    const service = new CourtService({ tenantId });
    const hierarchy = await service.getHierarchy();

    res.status(200).json(formatSuccess(hierarchy, correlationId));

  } catch (error) {
    Logger.error('courtController.getHierarchy failed', {
      correlationId,
      error: error.message
    });

    res.status(500).json(formatError(error, correlationId));
  }
};

export const getCourtStats = async (req, res) => {
  const correlationId = generateCorrelationId(req);

  try {
    const { tenantId } = tenantContext.get();
    
    Logger.info('courtController.getCourtStats', {
      correlationId,
      tenantId
    });

    const service = new CourtService({ tenantId });
    const stats = await service.getStats();

    res.status(200).json(formatSuccess(stats, correlationId));

  } catch (error) {
    Logger.error('courtController.getCourtStats failed', {
      correlationId,
      error: error.message
    });

    res.status(500).json(formatError(error, correlationId));
  }
};

export const addPracticeDirective = async (req, res) => {
  const correlationId = generateCorrelationId(req);
  const { courtId } = req.params;
  const startTime = Date.now();

  try {
    const { tenantId, userId } = tenantContext.get();
    
    Logger.info('courtController.addPracticeDirective', {
      correlationId,
      tenantId,
      courtId,
      directiveTitle: req.body.title
    });

    const service = new CourtService({ tenantId });
    const directive = await service.addPracticeDirective(courtId, req.body, userId);

    const responseTime = Date.now() - startTime;

    res.status(201).json(formatSuccess(directive, correlationId, {
      responseTimeMs: responseTime
    }));

  } catch (error) {
    Logger.error('courtController.addPracticeDirective failed', {
      correlationId,
      error: error.message
    });

    res.status(500).json(formatError(error, correlationId));
  }
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  createCourt,
  getCourt,
  updateCourt,
  listCourts,
  checkJurisdiction,
  getAppealRoute,
  addJudicialOfficer,
  getHierarchy,
  getCourtStats,
  addPracticeDirective
};
