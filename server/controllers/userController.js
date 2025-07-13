// server/controllers/userController.js

const User = require('../models/userModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

// Note: These functions are intended for administrative purposes and should be
// protected by both `protect` and `authorize('admin')` middleware in the routes.

/**
 * @desc    Get all users
 * @route   GET /api/users
 * @access  Private/Admin
 */
exports.getAllUsers = async (req, res, next) => {
    try {
        const users = await User.find().select('-password');

        res.status(200).json({
            success: true,
            count: users.length,
            data: users,
        });
    } catch (error) {
        logger.error(`Error fetching all users: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get a single user by ID
 * @route   GET /api/users/:id
 * @access  Private/Admin
 */
exports.getUserById = async (req, res, next) => {
    try {
        const user = await User.findById(req.params.id).select('-password');

        if (!user) {
            return next(new CustomError(`User not found with id of ${req.params.id}`, 404));
        }

        res.status(200).json({
            success: true,
            data: user,
        });
    } catch (error) {
        logger.error(`Error fetching user by ID: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Create a new user (by an admin)
 * @route   POST /api/users
 * @access  Private/Admin
 */
exports.createUser = async (req, res, next) => {
    try {
        const { name, email, password, role } = req.body;

        const user = await User.create({ name, email, password, role });

        const userResponse = { ...user._doc };
        delete userResponse.password;

        logger.info(`Admin created new user: ${user.email}`);

        res.status(201).json({
            success: true,
            data: userResponse,
        });
    } catch (error) {
        logger.error(`Error creating user by admin: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Update a user's details (by an admin)
 * @route   PUT /api/users/:id
 * @access  Private/Admin
 */
exports.updateUser = async (req, res, next) => {
    try {
        const { name, email, role } = req.body;
        const updateData = { name, email, role };

        const user = await User.findByIdAndUpdate(req.params.id, updateData, {
            new: true,
            runValidators: true,
        }).select('-password');

        if (!user) {
            return next(new CustomError(`User not found with id of ${req.params.id}`, 404));
        }

        logger.info(`Admin updated user profile: ${user.email}`);

        res.status(200).json({
            success: true,
            data: user,
        });
    } catch (error) {
        logger.error(`Error updating user by admin: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Delete a user (by an admin)
 * @route   DELETE /api/users/:id
 * @access  Private/Admin
 */
exports.deleteUser = async (req, res, next) => {
    try {
        const user = await User.findById(req.params.id);

        if (!user) {
            return next(new CustomError(`User not found with id of ${req.params.id}`, 404));
        }

        // Prevent admin from deleting their own account
        if (req.user.id === user.id) {
            return next(new CustomError('Admins cannot delete their own account.', 400));
        }

        // ✅ FIX: Avoid deprecated `remove()` method
        await User.deleteOne({ _id: user._id });

        logger.info(`Admin deleted user: ${user.email}`);

        res.status(200).json({
            success: true,
            data: {},
        });
    } catch (error) {
        logger.error(`Error deleting user by admin: ${error.message}`);
        next(error);
    }
};
