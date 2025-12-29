'use strict';
const asyncHandler = require('express-async-handler');
const Document = require('../models/documentModel');

// @desc    Get All Documents
exports.getAll = asyncHandler(async (req, res) => {
    // If admin/sheriff, see all. Else see own.
    const filter = {};
    // Uncomment for strict RBAC:
    // if (req.user.role !== 'admin' && req.user.role !== 'sheriff') {
    //     filter.createdBy = req.user.id;
    // }
    
    const docs = await Document.find(filter).sort({ createdAt: -1 });
    res.status(200).json({ success: true, count: docs.length, data: docs });
});

// @desc    Create Document
exports.create = asyncHandler(async (req, res) => {
    const doc = await Document.create({
        ...req.body,
        createdBy: req.user.id
    });
    res.status(201).json({ success: true, data: doc });
});

// @desc    Get One Document
exports.getOne = asyncHandler(async (req, res) => {
    const doc = await Document.findById(req.params.id);
    if (!doc) {
        res.status(404); throw new Error('Document not found');
    }
    res.status(200).json({ success: true, data: doc });
});

exports.update = asyncHandler(async (req, res) => {
    const doc = await Document.findByIdAndUpdate(req.params.id, req.body, { new: true });
    res.status(200).json({ success: true, data: doc });
});

exports.remove = asyncHandler(async (req, res) => {
    await Document.findByIdAndDelete(req.params.id);
    res.status(200).json({ success: true, message: 'Deleted' });
});
