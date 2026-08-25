/**
 * ============================================================================
 * WILSY OS - CRM LEAD CONTROLLER
 * ============================================================================
 *
 * @file         LeadController.js
 * @directory    server/controllers/crm/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @epitome      Governs multi-tenant lead management, pipeline valuation, and predictive scoring.
 * @version      1.0.0
 * @since        2026-07-24
 *
 * @collaboration
 * - LeadService: server/services/crm/LeadService.js
 * - AuthMiddleware: server/middleware/auth.middleware.js
 * - Kernel: server/src/enterprise/kernel/EnterpriseKernel.js
 *
 * @description
 * This controller handles all CRUD operations for leads within the CRM subsystem.
 * It ensures secure, multi-tenant isolation and integrates with the LeadService
 * for business logic execution.
 */

const LeadService = require('../services/crm/LeadService');
const { authenticateRequest } = require('../../middleware/auth.middleware');
const { EnterpriseKernelError } = require('../../src/enterprise/kernel/EnterpriseKernel');

class LeadController {
  constructor(leadService) {
    this.leadService = leadService;
  }

  async createLead(req, res, next) {
    try {
      const leadData = req.body;
      const lead = await this.leadService.ingestLead(leadData);
      res.status(201).json(lead);
    } catch (error) {
      next(new EnterpriseKernelError('CRM_LEAD_CREATE_FAILURE', error.message));
    }
  }

  async getLead(req, res, next) {
    try {
      const leadId = req.params.id;
      const lead = await this.leadService.retrieveLead(leadId);
      res.status(200).json(lead);
    } catch (error) {
      next(new EnterpriseKernelError('CRM_LEAD_RETRIEVE_FAILURE', error.message));
    }
  }

  async updateLead(req, res, next) {
    try {
      const leadId = req.params.id;
      const leadData = req.body;
      const lead = await this.leadService.updateLead(leadId, leadData);
      res.status(200).json(lead);
    } catch (error) {
      next(new EnterpriseKernelError('CRM_LEAD_UPDATE_FAILURE', error.message));
    }
  }

  async deleteLead(req, res, next) {
    try {
      const leadId = req.params.id;
      await this.leadService.removeLead(leadId);
      res.status(204).send();
    } catch (error) {
      next(new EnterpriseKernelError('CRM_LEAD_DELETE_FAILURE', error.message));
    }
  }
}

module.exports = LeadController;