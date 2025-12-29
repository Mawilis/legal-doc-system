const Dispatch = require('../models/Dispatch');

exports.createDispatch = async (req, res) => {
  try {
    // 1. Auto-Calculate Totals if missing (Backend Safety)
    const payload = req.body;
    
    // 2. Create Record
    const dispatch = await Dispatch.create(payload);
    
    res.status(201).json({ success: true, data: dispatch });
  } catch (err) {
    console.error('Dispatch Error:', err);
    res.status(400).json({ success: false, message: err.message });
  }
};

exports.getAllDispatches = async (req, res) => {
  const list = await Dispatch.find().sort({ createdAt: -1 });
  res.json({ success: true, data: list });
};
