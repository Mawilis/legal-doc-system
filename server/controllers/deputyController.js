// server/controllers/deputyController.js

const Deputy = require('../models/deputyModel');
const User = require('../models/userModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

// Note: All functions in this controller are for administrative use and should be
// protected by admin-only middleware in the routes.

/**
 * @desc    Create a new deputy profile for an existing user
 * @route   POST /api/deputies
 * @access  Private/Admin
 */
exports.createDeputyProfile = async (req, res, next) => {
    const { userId, badgeNumber, serviceRegion, fieldContactNumber } = req.body;

    try {
        // 1. Validate that the user exists and has the 'deputy' role.
        const user = await User.findById(userId);
        if (!user) {
            return next(new CustomError(`User with ID ${userId} not found.`, 404));
        }
        if (user.role !== 'deputy') {
            return next(new CustomError(`User ${user.name} does not have the 'deputy' role.`, 400));
        }

        // 2. Create the new deputy profile, linking it to the user account.
        const deputyProfile = await Deputy.create({
            user: userId,
            badgeNumber,
            serviceRegion,
            fieldContactNumber,
        });

        // Populate the user details in the response
        const fullProfile = await Deputy.findById(deputyProfile._id).populate('user', 'name email role');

        logger.info(`Deputy profile created for user: ${user.email} (Badge: ${badgeNumber})`);

        res.status(201).json({
            success: true,
            data: fullProfile,
        });
    } catch (error) {
        // This will catch errors like a duplicate badgeNumber or a user already having a profile.
        logger.error(`Error creating deputy profile: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get all deputy profiles
 * @route   GET /api/deputies
 * @access  Private/Admin
 */
exports.getAllDeputies = async (req, res, next) => {
    try {
        // Find all deputy profiles and populate their linked user information.
        const deputies = await Deputy.find().populate('user', 'name email role');

        res.status(200).json({
            success: true,
            count: deputies.length,
            data: deputies,
        });
    } catch (error) {
        logger.error(`Error fetching all deputies: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get a single deputy profile by its ID
 * @route   GET /api/deputies/:id
 * @access  Private/Admin
 */
exports.getDeputyById = async (req, res, next) => {
    try {
        const deputy = await Deputy.findById(req.params.id).populate('user', 'name email role');

        if (!deputy) {
            return next(new CustomError(`Deputy profile not found with id of ${req.params.id}`, 404));
        }

        res.status(200).json({
            success: true,
            data: deputy,
        });
    } catch (error) {
        logger.error(`Error fetching deputy by ID: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Update a deputy's profile information
 * @route   PUT /api/deputies/:id
 * @access  Private/Admin
 */
exports.updateDeputyProfile = async (req, res, next) => {
    try {
        // We only allow updating deputy-specific fields here.
        // User-level details (name, email) should be updated via the userController.
        const { badgeNumber, serviceRegion, fieldContactNumber } = req.body;
        const updateData = { badgeNumber, serviceRegion, fieldContactNumber };

        const deputy = await Deputy.findByIdAndUpdate(req.params.id, updateData, {
            new: true,
            runValidators: true,
        }).populate('user', 'name email role');

        if (!deputy) {
            return next(new CustomError(`Deputy profile not found with id of ${req.params.id}`, 404));
        }

        logger.info(`Deputy profile updated for: ${deputy.user.email}`);

        res.status(200).json({
            success: true,
            data: deputy,
        });
    } catch (error) {
        logger.error(`Error updating deputy profile: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Delete a deputy profile
 * @route   DELETE /api/deputies/:id
 * @access  Private/Admin
 */
exports.deleteDeputyProfile = async (req, res, next) => {
    try {
        const deputy = await Deputy.findById(req.params.id);

        if (!deputy) {
            return next(new CustomError(`Deputy profile not found with id of ${req.params.id}`, 404));
        }

        // Important Note: This only deletes the deputy *profile*.
        // It does NOT delete the associated user account. The user account
        // would need to be deleted separately via the userController.
        // This allows for "de-provisioning" a deputy without deleting the user's login history.

        await deputy.remove();

        logger.info(`Deputy profile deleted for user ID: ${deputy.user}`);

        res.status(200).json({
            success: true,
            data: {},
        });
    } catch (error) {
        logger.error(`Error deleting deputy profile: ${error.message}`);
        next(error);
    }
};
