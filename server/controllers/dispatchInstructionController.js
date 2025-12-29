/**
 * dispatchInstructionController.js
 * --------------------------------
 * - Validates per service type (server-side)
 * - Schedules SLA jobs
 * - Generates return artifacts (scaffold)
 * - AUTOMATED AUDIT TRAIL to Ledger Microservice
 */
const DispatchInstruction = require('../models/DispatchInstruction');
const axios = require('axios');

// --- BILLION-DOLLAR AUDIT TRAIL HELPER ---
async function logToLedger(type, actor, desc, meta) {
    try {
        // Fire and forget - don't slow down the main user
        axios.post('http://localhost:6000/events', {
            eventType: type,
            actor: actor,
            description: desc,
            meta: meta
        }).catch(err => console.error('❌ Ledger Sync Failed (Network):', err.message));
    } catch (e) {
        console.error('❌ Ledger Error:', e.message);
    }
}

// Minimal server-side service-type validation
function validatePerType(body) {
  const required = (fields) => {
    for (const f of fields) {
      if (body[f] === undefined || body[f] === null || body[f] === '') {
        return `Missing required field: ${f}`;
      }
    }
    return null;
  };

  switch (body.serviceType) {
    case 'urgent_service_rule_6_12':
      return required(['urgentReason', 'deadlineAt', 'ruleReference']);
    case 'writ_execution_movables':
      return required(['orderRef', 'securityPlan', 'warehouseProvider']);
    case 'writ_execution_immovables':
      return required(['deedInfo', 'noticesServed', 'valuationMethod']);
    case 'ejectment_eviction':
      return required(['evictionOrderRef', 'socialWorkerNeeded', 'locksmithNeeded']);
    case 'substituted_service':
      return required(['courtOrderAuthorizing']) || (Array.isArray(body.mediaChannels) && body.mediaChannels.length > 0 ? null : 'mediaChannels required');
    case 'corporate_service':
      return required(['registeredOfficeAddress', 'cipcVerified']);
    default:
      return null;
  }
}

// SLA scheduling stubs
async function scheduleSLAJobs(instruction) {
  const firstAttemptHours = instruction.urgency !== 'normal' ? 4 : 48;
  const completionDays = instruction.serviceType.includes('writ') || instruction.serviceType.includes('eviction') ? 5 : 10;
  return { firstAttemptHours, completionDays };
}

// Return generation scaffold
async function generateReturns(instruction) {
  const baseUrl = 'https://files.example.com/returns';
  return {
    returnOfServicePdfUrl: `${baseUrl}/${instruction._id}-return.pdf`,
    affidavitPdfUrl:
      instruction.serviceType === 'urgent_service_rule_6_12'
        ? `${baseUrl}/${instruction._id}-affidavit-urgency.pdf`
        : undefined,
  };
}

exports.createInstruction = async (req, res) => {
  try {
    // Global required fields
    const requiredFields = [
      'title', 'documentCode', 'caseNumber', 'classification', 'court',
      'plaintiff', 'defendant', 'serviceType', 'serviceAddress',
      'urgency', 'distanceKm', 'attemptsPlanned'
    ];
    // Note: attemptPlan and pricingPreview might be strictly validated or constructed server-side
    
    for (const f of requiredFields) {
      if (req.body[f] === undefined || req.body[f] === null || req.body[f] === '') {
        return res.status(400).json({ message: `Missing required field: ${f}` });
      }
    }

    // Per-type validation
    const perTypeError = validatePerType(req.body);
    if (perTypeError) return res.status(400).json({ message: perTypeError });

    const instruction = new DispatchInstruction(req.body);
    await instruction.save();

    // --- 🚀 AUTOMATED AUDIT LOG ---
    logToLedger(
        'INSTRUCTION_CREATED', 
        'SYSTEM_DISPATCHER', 
        `Created Case: ${req.body.caseNumber}`, 
        { instructionId: instruction._id }
    );

    // Schedule SLA jobs
    const slaInfo = await scheduleSLAJobs(instruction);

    // Pre-generate return URLs (scaffold)
    const returns = await generateReturns(instruction);
    if (returns.returnOfServicePdfUrl) instruction.returnOfServicePdfUrl = returns.returnOfServicePdfUrl;
    if (returns.affidavitPdfUrl) instruction.affidavitPdfUrl = returns.affidavitPdfUrl;
    await instruction.save();

    return res.status(201).json({
      instruction,
      sla: slaInfo,
      returns,
    });
  } catch (err) {
    return res.status(400).json({ message: err.message });
  }
};

exports.getInstruction = async (req, res) => {
  try {
    const { id } = req.params;
    const instruction = await DispatchInstruction.findById(id);
    if (!instruction) return res.status(404).json({ message: 'Not found' });
    return res.status(200).json(instruction);
  } catch (err) {
    return res.status(400).json({ message: err.message });
  }
};

exports.listInstructions = async (req, res) => {
  try {
    const items = await DispatchInstruction.find().sort({ createdAt: -1 }).limit(100);
    return res.status(200).json(items);
  } catch (err) {
    return res.status(400).json({ message: err.message });
  }
};
