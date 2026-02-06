/*
 * File: server/controllers/feeController.js
 * STATUS: PRODUCTION-READY | FINANCIAL REFERENCE GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Governs the firm's price list and court tariffs. Manages hourly rates, 
 * fixed legal fees, and disbursements with strict price-change auditing.
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const Fee = require('../models/Fee');
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * @desc    REGISTER NEW FEE ITEM / TARIFF
 * @route   POST /api/v1/fees
 */
exports.createFee = asyncHandler(async (req, res) => {
    const { code, description, amount, type } = req.body;

    // 1. DATA INTEGRITY CHECK
    if (!code || !amount) {
        return errorResponse(req, res, 400, 'Fee code and amount are required for registry.', 'ERR_FEE_INPUT');
    }

    // 2. COLLISION DETECTION (Tenant-Scoped)
    const exists = await Fee.findOne({
        code: code.toUpperCase(),
        ...req.tenantFilter
    });

    if (exists) {
        return errorResponse(req, res, 400, `Fee code '${code}' already exists in your firm's registry.`, 'ERR_DUPLICATE_FEE');
    }

    // 3. ATOMIC CREATION
    const fee = await Fee.create({
        ...req.body,
        tenantId: req.user.tenantId,
        createdBy: req.user.id,
        code: code.toUpperCase(),
        currency: 'ZAR',
        active: true
    });

    // 4. FORENSIC AUDIT
    await emitAudit(req, {
        resource: 'BILLING_ENGINE',
        action: 'FEE_CREATED',
        severity: 'INFO',
        metadata: { feeId: fee._id, code: fee.code, amount: fee.amount }
    });

    return successResponse(req, res, fee, { message: 'Fee item successfully registered.' }, 201);
});

/**
 * @desc    GET PRICE LIST (Paginated & Filtered)
 * @route   GET /api/v1/fees
 */
exports.getAllFees = asyncHandler(async (req, res) => {
    const { type, search, page = 1, limit = 50 } = req.query;

    const query = { ...req.tenantFilter, active: true };

    if (type) query.type = type;
    if (search) {
        query.$or = [
            { code: { $regex: search, $options: 'i' } },
            { description: { $regex: search, $options: 'i' } }
        ];
    }

    const skip = (parseInt(page) - 1) * parseInt(limit);
    const fees = await Fee.find(query)
        .sort({ code: 1 })
        .skip(skip)
        .limit(parseInt(limit));

    const total = await Fee.countDocuments(query);

    return successResponse(req, res, fees, {
        pagination: {
            total,
            page: parseInt(page),
            pages: Math.ceil(total / parseInt(limit))
        }
    });
});

/**
 * @desc    GET SINGLE FEE ITEM
 * @route   GET /api/v1/fees/:id
 */
exports.getFee = asyncHandler(async (req, res) => {
    const fee = await Fee.findOne({
        _id: req.params.id,
        ...req.tenantFilter
    });

    if (!fee) {
        return errorResponse(req, res, 404, 'Fee item not found in firm registry.', 'ERR_FEE_NOT_FOUND');
    }

    return successResponse(req, res, fee);
});

/**
 * @desc    UPDATE FEE METADATA / PRICE
 * @route   PATCH /api/v1/fees/:id
 */
exports.updateFee = asyncHandler(async (req, res) => {
    const { amount, description, active } = req.body;

    const fee = await Fee.findOne({ _id: req.params.id, ...req.tenantFilter });

    if (!fee) {
        return errorResponse(req, res, 404, 'Fee item not found.', 'ERR_FEE_NOT_FOUND');
    }

    const oldAmount = fee.amount;
    const isPriceChange = amount !== undefined && Number(amount) !== oldAmount;

    // 1. UPDATE FIELDS
    if (description) fee.description = description;
    if (active !== undefined) fee.active = active;
    if (isPriceChange) fee.amount = Number(amount);

    await fee.save();

    // 2. AUDIT WITH ESCALATION FOR PRICE CHANGES
    await emitAudit(req, {
        resource: 'BILLING_ENGINE',
        action: isPriceChange ? 'FEE_PRICE_UPDATED' : 'FEE_DETAILS_UPDATED',
        severity: isPriceChange ? 'WARNING' : 'INFO',
        metadata: {
            feeId: fee._id,
            code: fee.code,
            oldAmount,
            newAmount: fee.amount
        }
    });

    return successResponse(req, res, fee, { message: 'Fee registry updated.' });
});

/**
 * @desc    DEACTIVATE FEE ITEM (Soft Delete)
 * @route   DELETE /api/v1/fees/:id
 */
exports.deleteFee = asyncHandler(async (req, res) => {
    // In legal accounting, we deactivate to maintain referential integrity
    const fee = await Fee.findOneAndUpdate(
        { _id: req.params.id, ...req.tenantFilter },
        { active: false },
        { new: true }
    );

    if (!fee) {
        return errorResponse(req, res, 404, 'Fee item not found.', 'ERR_FEE_NOT_FOUND');
    }

    await emitAudit(req, {
        resource: 'BILLING_ENGINE',
        action: 'FEE_DEACTIVATED',
        severity: 'WARNING',
        metadata: { feeId: fee._id, code: fee.code }
    });

    return successResponse(req, res, null, { message: 'Fee item removed from active registry.' });
});