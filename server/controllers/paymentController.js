'use strict';
const asyncHandler = require('express-async-handler');

// @desc    Get payment
// @route   GET /api/payments
exports.getAll = asyncHandler(async (req, res) => {
    res.status(200).json({ success: true, message: 'payment API Online' });
});

exports.create = asyncHandler(async (req, res) => res.status(201).json({ success: true, data: req.body }));
exports.getOne = asyncHandler(async (req, res) => res.status(200).json({ success: true, data: { id: req.params.id } }));
exports.update = asyncHandler(async (req, res) => res.status(200).json({ success: true, data: req.body }));
exports.remove = asyncHandler(async (req, res) => res.status(200).json({ success: true, message: 'Deleted' }));

// Auth Specifics (prevents undefined exports)
exports.register = asyncHandler(async (req, res) => res.status(201).json({ token: 'mock' }));
exports.login = asyncHandler(async (req, res) => res.status(200).json({ token: 'mock' }));
exports.getMe = asyncHandler(async (req, res) => res.status(200).json({ user: {} }));
exports.logout = asyncHandler(async (req, res) => res.status(200).json({ message: 'out' }));
