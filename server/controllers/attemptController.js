const crypto = require('crypto');
const Attempt = require('../models/Attempt');
const DispatchInstruction = require('../models/DispatchInstruction');

function computeAttemptHash(payload) {
  const core = {
    instructionId: String(payload.instructionId),
    at: new Date(payload.at).toISOString(),
    gps: { lat: Number(payload.gps.lat), lng: Number(payload.gps.lng), accuracy: Number(payload.gps.accuracy || 0) },
    outcome: payload.outcome,
    notes: payload.notes || '',
    evidence: (payload.evidence || []).map((e) => ({
      type: e.type,
      url: e.url || '',
      text: e.text || '',
      capturedAt: e.capturedAt ? new Date(e.capturedAt).toISOString() : '',
    })),
  };
  const serialized = JSON.stringify(core);
  return crypto.createHash('sha256').update(serialized).digest('hex');
}

exports.createAttempt = async (req, res) => {
  try {
    const { id: instructionId } = req.params;
    const { at, gps, outcome, notes, evidence, window } = req.body;

    if (!at || !gps || gps.lat === undefined || gps.lng === undefined || !outcome) {
      return res.status(400).json({ message: 'Missing required attempt fields' });
    }

    const instruction = await DispatchInstruction.findById(instructionId);
    if (!instruction) return res.status(404).json({ message: 'Instruction not found' });

    const hash = computeAttemptHash({ instructionId, at, gps, outcome, notes, evidence, window });

    const attempt = new Attempt({
      instructionId, at, gps, outcome, notes,
      evidence: Array.isArray(evidence) ? evidence : [],
      window: window || null,
      hash,
    });
    await attempt.save();

    if (outcome === 'served') {
      instruction.status = 'completed';
    } else {
      if (instruction.status === 'created' || instruction.status === 'Pending Dispatch') instruction.status = 'in_progress';
    }
    await instruction.save();

    return res.status(201).json({ attempt, instructionStatus: instruction.status });
  } catch (err) {
    return res.status(400).json({ message: err.message });
  }
};

exports.listAttempts = async (req, res) => {
  try {
    const { id: instructionId } = req.params;
    const attempts = await Attempt.find({ instructionId }).sort({ at: 1 });
    return res.status(200).json(attempts);
  } catch (err) {
    return res.status(400).json({ message: err.message });
  }
};
