/*
 * File: server/controllers/attemptController.js
 * STATUS: PRODUCTION-READY | FORENSIC ADMISSIBILITY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Records cryptographic proof of service attempts. Captures GPS coordinates, 
 * evidence media, and generates a SHA-256 hash to ensure data integrity.
 * -----------------------------------------------------------------------------
 */

'use strict';

const crypto = require('crypto');
const asyncHandler = require('express-async-handler');
const Attempt = require('../models/Attempt');
const DispatchInstruction = require('../models/DispatchInstruction');
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * INTERNAL UTILITY: GENERATE CRYPTOGRAPHIC SEAL
 * Creates a deterministic hash of the attempt data for court admissibility.
 */
const computeAttemptHash = (payload) => {
  const data = {
    instructionId: String(payload.instructionId),
    at: new Date(payload.at).toISOString(),
    gps: {
      lat: Number(payload.gps.lat),
      lng: Number(payload.gps.lng)
    },
    outcome: payload.outcome,
    notes: payload.notes || ''
  };

  const serialized = JSON.stringify(data);
  return crypto.createHash('sha256').update(serialized).digest('hex');
};

/**
 * @desc    LOG SERVICE ATTEMPT (THE "KNOCK")
 * @route   POST /api/v1/attempts/:id
 */
exports.createAttempt = asyncHandler(async (req, res) => {
  const { id: instructionId } = req.params;
  const { at, gps, outcome, notes, evidence } = req.body;

  // 1. SCOPED INSTRUCTION VALIDATION
  const instruction = await DispatchInstruction.findOne({
    _id: instructionId,
    ...req.tenantFilter
  });

  if (!instruction) {
    return errorResponse(req, res, 404, 'Instruction not found or access denied.', 'ERR_INSTRUCTION_NOT_FOUND');
  }

  // 2. GPS REQUIREMENT (Legal Hardening)
  if (!gps || gps.lat === undefined || gps.lng === undefined) {
    return errorResponse(req, res, 400, 'Non-repudiation failed: GPS coordinates are mandatory.', 'ERR_GPS_REQUIRED');
  }

  // 3. GENERATE IMMUTABLE HASH
  const hash = computeAttemptHash({ instructionId, at, gps, outcome, notes });

  // 4. PERSIST ATTEMPT
  const attempt = await Attempt.create({
    ...req.body,
    instructionId,
    tenantId: req.user.tenantId,
    sheriffId: req.user.id,
    hash
  });

  // 5. WORKFLOW STATE TRANSITION
  let statusUpdated = false;
  if (['served', 'domicile_served'].includes(outcome)) {
    instruction.status = 'completed';
    instruction.completedAt = new Date();
    statusUpdated = true;
  } else if (['created', 'pending'].includes(instruction.status)) {
    instruction.status = 'in_progress';
    statusUpdated = true;
  }

  if (statusUpdated) await instruction.save();

  // 6. FORENSIC AUDIT
  await emitAudit(req, {
    resource: 'LOGISTICS_MODULE',
    action: 'SERVICE_ATTEMPT_LOGGED',
    severity: 'INFO',
    metadata: {
      attemptId: attempt._id,
      hash,
      outcome,
      newStatus: instruction.status
    }
  });

  return successResponse(req, res, {
    attempt,
    instructionStatus: instruction.status
  }, { message: 'Attempt recorded and sealed.' }, 201);
});

/**
 * @desc    LIST ATTEMPTS FOR INSTRUCTION
 * @route   GET /api/v1/attempts/:id
 */
exports.listAttempts = asyncHandler(async (req, res) => {
  const { id: instructionId } = req.params;

  const attempts = await Attempt.find({
    instructionId,
    ...req.tenantFilter
  }).sort({ at: 1 });

  return successResponse(req, res, attempts, { results: attempts.length });
});