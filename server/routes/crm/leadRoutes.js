/**
 * ============================================================================
 * WILSY OS - CRM LEAD ROUTES
 * ============================================================================
 *
 * @file         leadRoutes.js
 * @directory    server/routes/crm/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @epitome      Governs multi-tenant lead management, pipeline valuation, and predictive scoring.
 * @version      1.0.0
 * @since        2026-07-24
 *
 * @collaboration
 * - LeadController: server/controllers/crm/LeadController.js
 * - AuthMiddleware: server/middleware/auth.middleware.js
 * - Kernel: server/src/enterprise/kernel/EnterpriseKernel.js
 *
 * @description
 * This file defines the RESTful API routes for managing leads within the CRM subsystem.
 * It ensures secure, multi-tenant isolation and integrates with the LeadController
 * for handling requests.
 */

const express = require('express');
const router = express.Router();
const LeadController = require('../controllers/crm/LeadController');
const leadService = require('../services/crm/LeadService');
const leadController = new LeadController(leadService);
const { authenticateRequest } = require('../../middleware/auth.middleware');

router.post('/leads', authenticateRequest, leadController.createLead);
router.get('/leads/:id', authenticateRequest, leadController.getLead);
router.put('/leads/:id', authenticateRequest, leadController.updateLead);
router.delete('/leads/:id', authenticateRequest, leadController.deleteLead);

module.exports = router;