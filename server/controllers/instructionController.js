const Instruction = require('../models/instructionModel');

// Create a new instruction
exports.createInstruction = async (req, res, next) => {
    try {
        const { title, description } = req.body;

        const newInstruction = await Instruction.create({
            title,
            description,
            owner: req.user.id, // Assuming req.user is populated by auth middleware
        });

        res.status(201).json(newInstruction);
    } catch (error) {
        next({ status: 400, message: 'Error creating instruction', error });
    }
};

// Get a specific instruction by ID
exports.getInstructionById = async (req, res, next) => {
    try {
        const instruction = await Instruction.findById(req.params.instructionId);

        if (!instruction) {
            return res.status(404).json({ message: 'Instruction not found' });
        }

        // Ensure the user has access to this instruction (based on ownership)
        if (instruction.owner.toString() !== req.user.id) {
            return res.status(403).json({ message: 'Not authorized to access this instruction' });
        }

        res.status(200).json(instruction);
    } catch (error) {
        next({ status: 500, message: 'Error fetching instruction', error });
    }
};

// Get all instructions for the authenticated user
exports.getAllInstructions = async (req, res, next) => {
    try {
        const instructions = await Instruction.find({ owner: req.user.id });
        res.status(200).json(instructions);
    } catch (error) {
        next({ status: 500, message: 'Error fetching instructions', error });
    }
};

// Update an instruction by ID
exports.updateInstruction = async (req, res, next) => {
    try {
        const { title, description } = req.body;

        const instruction = await Instruction.findById(req.params.instructionId);

        if (!instruction) {
            return res.status(404).json({ message: 'Instruction not found' });
        }

        // Ensure the user has access to update this instruction
        if (instruction.owner.toString() !== req.user.id) {
            return res.status(403).json({ message: 'Not authorized to update this instruction' });
        }

        // Update instruction fields
        instruction.title = title || instruction.title;
        instruction.description = description || instruction.description;
        await instruction.save();

        res.status(200).json(instruction);
    } catch (error) {
        next({ status: 500, message: 'Error updating instruction', error });
    }
};

// Delete an instruction by ID
exports.deleteInstruction = async (req, res, next) => {
    try {
        const instruction = await Instruction.findByIdAndDelete(req.params.instructionId);

        if (!instruction) {
            return res.status(404).json({ message: 'Instruction not found' });
        }

        // Ensure the user has access to delete this instruction
        if (instruction.owner.toString() !== req.user.id) {
            return res.status(403).json({ message: 'Not authorized to delete this instruction' });
        }

        res.status(200).json({ message: 'Instruction deleted successfully' });
    } catch (error) {
        next({ status: 500, message: 'Error deleting instruction', error });
    }
};
