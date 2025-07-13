const Template = require('../models/templateModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Create a new document template
 * @route   POST /api/templates
 * @access  Private/Admin
 */
exports.createTemplate = async (req, res, next) => {
    try {
        req.body.createdBy = req.user.id;

        if (!req.body.fields || !Array.isArray(req.body.fields) || req.body.fields.length === 0) {
            return next(new CustomError('A template must include at least one field.', 400));
        }

        const newTemplate = await Template.create(req.body);

        logger.info(`New template created: "${newTemplate.name}"`);
        res.status(201).json({
            success: true,
            data: newTemplate,
        });
    } catch (error) {
        logger.error(`Error creating template: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get all document templates
 * @route   GET /api/templates
 * @access  Private/Admin
 */
exports.getAllTemplates = async (req, res, next) => {
    try {
        const templates = await Template.find().populate('createdBy', 'name email').sort('name');

        res.status(200).json({
            success: true,
            count: templates.length,
            data: templates,
        });
    } catch (error) {
        logger.error(`Error fetching all templates: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get a single template by its ID
 * @route   GET /api/templates/:id
 * @access  Private/Admin
 */
exports.getTemplateById = async (req, res, next) => {
    try {
        const template = await Template.findById(req.params.id).populate('createdBy', 'name email');

        if (!template) {
            return next(new CustomError(`Template not found with id ${req.params.id}`, 404));
        }

        res.status(200).json({
            success: true,
            data: template,
        });
    } catch (error) {
        logger.error(`Error fetching template by ID: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Update a document template
 * @route   PUT /api/templates/:id
 * @access  Private/Admin
 */
exports.updateTemplate = async (req, res, next) => {
    try {
        const template = await Template.findById(req.params.id);

        if (!template) {
            return next(new CustomError(`Template not found with id ${req.params.id}`, 404));
        }

        // Allow only creator or admin
        if (template.createdBy.toString() !== req.user.id && req.user.role !== 'ADMIN') {
            return next(new CustomError('User not authorized to update this template.', 403));
        }

        // Update fields
        const updates = { ...req.body };
        delete updates.createdBy; // Prevent reassignment of creator

        const updatedTemplate = await Template.findByIdAndUpdate(req.params.id, updates, {
            new: true,
            runValidators: true,
        });

        logger.info(`Template updated: "${updatedTemplate.name}"`);
        res.status(200).json({
            success: true,
            data: updatedTemplate,
        });
    } catch (error) {
        logger.error(`Error updating template: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Delete a document template
 * @route   DELETE /api/templates/:id
 * @access  Private/Admin
 */
exports.deleteTemplate = async (req, res, next) => {
    try {
        const template = await Template.findById(req.params.id);

        if (!template) {
            return next(new CustomError(`Template not found with id ${req.params.id}`, 404));
        }

        if (template.createdBy.toString() !== req.user.id && req.user.role !== 'ADMIN') {
            return next(new CustomError('User not authorized to delete this template.', 403));
        }

        // Optionally: Add logic to check if template is linked to active documents

        await template.remove();

        logger.info(`Template deleted: "${template.name}"`);
        res.status(200).json({
            success: true,
            data: {},
        });
    } catch (error) {
        logger.error(`Error deleting template: ${error.message}`);
        next(error);
    }
};
