// server/controllers/instructionController.js

const Instruction = require('../models/instructionModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Get all instructions
 * @route   GET /api/instructions
 * @access  Private
 */
exports.getAllInstructions = async (req, res, next) => {
    try {
        // Find all instructions and sort them by the most recently created.
        // We use .populate() to get details from the referenced models.
        const instructions = await Instruction.find()
            .populate({
                path: 'document',
                select: 'title caseNumber status', // Only select these fields from the document
            })
            .populate('createdBy', 'name') // Get the creator's name
            .populate('assignedTo', 'name') // Get the assignee's name
            .sort({ createdAt: -1 });

        res.status(200).json({
            success: true,
            count: instructions.length,
            data: instructions,
        });
    } catch (error) {
        logger.error(`Error fetching all instructions: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get a single instruction by its ID
 * @route   GET /api/instructions/:id
 * @access  Private
 */
exports.getInstructionById = async (req, res, next) => {
    try {
        const instruction = await Instruction.findById(req.params.id)
            .populate({
                path: 'document',
                select: 'title caseNumber status documentType',
            })
            .populate('createdBy', 'name email')
            .populate('assignedTo', 'name email');

        if (!instruction) {
            return next(new CustomError(`Instruction not found with id of ${req.params.id}`, 404));
        }

        res.status(200).json({
            success: true,
            data: instruction,
        });
    } catch (error) {
        logger.error(`Error fetching instruction by ID: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Create a new instruction
 * @route   POST /api/instructions
 * @access  Private
 */
exports.createInstruction = async (req, res, next) => {
    try {
        // Securely assign the logged-in user as the creator of the instruction.
        req.body.createdBy = req.user.id;

        // The request body should contain `document` (the ID of the document)
        // and `assignedTo` (the ID of the deputy).
        const newInstruction = await Instruction.create(req.body);

        logger.info(`New instruction created for document ${newInstruction.document} by ${req.user.email}`);

        // Our 'post-save' middleware on the model will automatically update the document's status.

        res.status(201).json({
            success: true,
            data: newInstruction,
        });
    } catch (error) {
        // Mongoose validation errors can be detailed. We log them for debugging.
        logger.error(`Error creating instruction: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Update an instruction (e.g., change assignee or special instructions)
 * @route   PUT /api/instructions/:id
 * @access  Private
 */
exports.updateInstruction = async (req, res, next) => {
    try {
        let instruction = await Instruction.findById(req.params.id);

        if (!instruction) {
            return next(new CustomError(`Instruction not found with id of ${req.params.id}`, 404));
        }

        // Authorization: Only the user who created the instruction or an admin can update it.
        if (instruction.createdBy.toString() !== req.user.id && req.user.role !== 'admin') {
            return next(new CustomError(`User ${req.user.id} is not authorized to update this instruction.`, 403));
        }

        instruction = await Instruction.findByIdAndUpdate(req.params.id, req.body, {
            new: true,
            runValidators: true,
        });

        logger.info(`Instruction updated: ${instruction._id}`);

        res.status(200).json({
            success: true,
            data: instruction,
        });
    } catch (error) {
        logger.error(`Error updating instruction: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Delete an instruction
 * @route   DELETE /api/instructions/:id
 * @access  Private (Admin Only)
 */
exports.deleteInstruction = async (req, res, next) => {
    try {
        const instruction = await Instruction.findById(req.params.id);

        if (!instruction) {
            return next(new CustomError(`Instruction not found with id of ${req.params.id}`, 404));
        }

        // This is a sensitive action, so we use role-based authorization.
        if (req.user.role !== 'admin') {
            return next(new CustomError('Only admins can delete instructions.', 403));
        }

        await instruction.remove();

        logger.info(`Instruction deleted: ${instruction._id}`);

        res.status(200).json({
            success: true,
            data: {},
        });
    } catch (error) {
        logger.error(`Error deleting instruction: ${error.message}`);
        next(error);
    }
};
