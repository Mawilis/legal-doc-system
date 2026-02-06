/*
 * File: server/controllers/dispatchInstructionController.js
 * STATUS: PRODUCTION-READY | LEGAL COMPLIANCE GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Manages complex legal instructions. Enforces service-type specific 
 * validation, calculates performance SLAs, and manages the lifecycle of 
 * high-stakes court mandates (Writs, Evictions, Urgent Services).
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const DispatchInstruction = require('../models/DispatchInstruction');
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * INTERNAL COMPLIANCE VALIDATOR
 * Ensures that the specific legal requirements for various service types are met.
 */
const validateLegalRequirements = (body) => {
  const check = (fields) => {
    const missing = fields.filter(f => !body[f]);
    return missing.length > 0 ? `Missing legal prerequisites: ${missing.join(', ')}` : null;
  };

  const typeRules = {
    'urgent_service_rule_6_12': ['urgentReason', 'deadlineAt', 'ruleReference'],
    'writ_execution_movables': ['orderRef', 'securityPlan', 'warehouseProvider'],
    'writ_execution_immovables': ['deedInfo', 'noticesServed'],
    'ejectment_eviction': ['evictionOrderRef', 'locksmithNeeded'],
    'corporate_service': ['registeredOfficeAddress', 'cipcVerified']
  };

  return typeRules[body.serviceType] ? check(typeRules[body.serviceType]) : null;
};

/**
 * SLA SCHEDULER ENGINE
 * Determines the target completion times based on urgency and legal complexity.
 */
const calculateSLA = (instruction) => {
  const isUrgent = instruction.urgency === 'urgent';
  const isComplex = ['ejectment_eviction', 'writ_execution_immovables'].includes(instruction.serviceType);

  return {
    firstAttemptDeadlineHours: isUrgent ? 4 : 48,
    completionDeadlineDays: isComplex ? 5 : 10
  };
};

/**
 * @desc    CREATE COMPLEX INSTRUCTION
 * @route   POST /api/v1/dispatch-instructions
 */
exports.createInstruction = asyncHandler(async (req, res) => {
  // 1. LEGAL COMPLIANCE CHECK
  const complianceError = validateLegalRequirements(req.body);
  if (complianceError) {
    return errorResponse(req, res, 400, complianceError, 'ERR_LEGAL_COMPLIANCE_FAILED');
  }

  // 2. ATOMIC REGISTRY
  const instruction = await DispatchInstruction.create({
    ...req.body,
    tenantId: req.user.tenantId,
    createdBy: req.user.id
  });

  // 3. GENERATE SLA CONTEXT
  const sla = calculateSLA(instruction);

  // 4. FORENSIC AUDIT
  await emitAudit(req, {
    resource: 'LOGISTICS_MODULE',
    action: 'COMPLEX_INSTRUCTION_ISSUED',
    severity: req.body.urgency === 'urgent' ? 'WARN' : 'INFO',
    metadata: {
      instructionId: instruction._id,
      serviceType: req.body.serviceType,
      sla
    }
  });

  return successResponse(req, res, { instruction, sla }, { message: 'Legal instruction successfully validated and issued.' }, 201);
});

/**
 * @desc    GET INSTRUCTION DETAILS
 * @route   GET /api/v1/dispatch-instructions/:id
 */
exports.getInstruction = asyncHandler(async (req, res) => {
  const instruction = await DispatchInstruction.findOne({
    _id: req.params.id,
    ...req.tenantFilter
  });

  if (!instruction) {
    return errorResponse(req, res, 404, 'Instruction not found or access denied.', 'ERR_INSTRUCTION_NOT_FOUND');
  }

  return successResponse(req, res, instruction);
});

/**
 * @desc    LIST INSTRUCTIONS (Firm-Scoped)
 * @route   GET /api/v1/dispatch-instructions
 */
exports.listInstructions = asyncHandler(async (req, res) => {
  const { page = 1, limit = 50, serviceType } = req.query;

  const query = { ...req.tenantFilter };
  if (serviceType) query.serviceType = serviceType;

  const skip = (parseInt(page) - 1) * parseInt(limit);
  const instructions = await DispatchInstruction.find(query)
    .sort({ createdAt: -1 })
    .skip(skip)
    .limit(parseInt(limit));

  const total = await DispatchInstruction.countDocuments(query);

  return successResponse(req, res, instructions, {
    pagination: {
      total,
      page: parseInt(page),
      pages: Math.ceil(total / parseInt(limit))
    }
  });
});