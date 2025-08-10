// ~/server/controllers/userController.js

const User = require('../models/userModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Fetch all users with pagination, search, and sorting (admin only).
 * @route   GET /api/admin/users
 * @access  Private/Admin
 */
exports.getAllUsers = async (req, res, next) => {
    try {
        // --- Filtering, Sorting, and Pagination Parameters ---
        const page = parseInt(req.query.page, 10) || 1;
        const limit = parseInt(req.query.limit, 10) || 10;
        const sort = req.query.sort || '-createdAt'; // Default to newest first

        // Keyword search for name or email
        const keyword = req.query.keyword
            ? {
                $or: [
                    { name: { $regex: req.query.keyword, $options: 'i' } },
                    { email: { $regex: req.query.keyword, $options: 'i' } },
                ],
            }
            : {};

        // --- Database Query ---
        const users = await User.find(keyword)
            .select('-password') // Exclude password from the result
            .sort(sort)
            .skip((page - 1) * limit)
            .limit(limit);

        const total = await User.countDocuments(keyword);

        // --- Send Response ---
        res.status(200).json({
            success: true,
            count: users.length,
            total,
            page,
            pages: Math.ceil(total / limit),
            data: users,
        });
    } catch (err) {
        logger.error(`Admin fetch all users failed: ${err.message}`);
        next(err);
    }
};

/**
 * @desc    Get a single user by ID.
 * @route   GET /api/admin/users/:id
 * @access  Private/Admin
 */
exports.getUserById = async (req, res, next) => {
    try {
        const user = await User.findById(req.params.id).select('-password');
        if (!user) return next(new CustomError(`User not found with id of ${req.params.id}`, 404));
        res.status(200).json({ success: true, data: user });
    } catch (err) {
        logger.error(`Admin get user by ID failed: ${err.message}`);
        next(err);
    }
};

/**
 * @desc    Create a new user (admin only).
 * @route   POST /api/admin/users
 * @access  Private/Admin
 */
exports.createUser = async (req, res, next) => {
    try {
        const { name, email, password, role } = req.body;
        const newUser = await User.create({ name, email, password, role });

        // Do not send the password back in the response
        const { password: _, ...userData } = newUser._doc;

        logger.info(`Admin created user: ${newUser.email}`);
        res.status(201).json({ success: true, data: userData });
    } catch (err) { // ✅ Corrected this block
        logger.error(`Admin create user failed: ${err.message}`);
        next(err);
    }
};

/**
 * @desc    Update a user's details (admin only).
 * @route   PUT /api/admin/users/:id
 * @access  Private/Admin
 */
exports.updateUser = async (req, res, next) => {
    try {
        // Exclude password from being updated through this route
        const { name, email, role } = req.body;
        const updatedUser = await User.findByIdAndUpdate(req.params.id, { name, email, role }, {
            new: true,
            runValidators: true
        }).select('-password');

        if (!updatedUser) return next(new CustomError('User not found', 404));

        logger.info(`Admin updated user: ${updatedUser.email}`);
        res.status(200).json({ success: true, data: updatedUser });
    } catch (err) {
        logger.error(`Admin update user failed: ${err.message}`);
        next(err);
    }
};

/**
 * @desc    Delete a user (admin only).
 * @route   DELETE /api/admin/users/:id
 * @access  Private/Admin
 */
exports.deleteUser = async (req, res, next) => {
    try {
        const user = await User.findById(req.params.id);
        if (!user) return next(new CustomError('User not found', 404));

        // Prevent an admin from deleting themselves
        if (req.user.id === user.id) {
            return next(new CustomError('Admins cannot delete their own account.', 403));
        }

        await User.deleteOne({ _id: user._id });

        logger.warn(`Admin deleted user: ${user.email}`);
        res.status(200).json({ success: true, message: 'User removed' });
    } catch (err) {
        logger.error(`Admin delete user failed: ${err.message}`);
        next(err);
    }
};

/**
 * @desc    Update user permissions (admin only).
 * @route   PUT /api/admin/users/:id/permissions
 * @access  Private/Admin
 */
exports.updatePermissions = async (req, res, next) => {
    try {
        const { permissions } = req.body;
        const user = await User.findByIdAndUpdate(
            req.params.id,
            { permissions },
            { new: true, runValidators: true }
        ).select('-password');

        if (!user) return next(new CustomError('User not found', 404));

        logger.info(`Admin updated permissions for user: ${user.email}`);
        res.status(200).json({ success: true, data: user });
    } catch (err) {
        logger.error(`Admin update permissions failed: ${err.message}`);
        next(err);
    }
};

/**
 * @desc    Assign a user to a team (admin only).
 * @route   PUT /api/admin/users/:id/team
 * @access  Private/Admin
 */
exports.assignUserToTeam = async (req, res, next) => {
    try {
        const { team } = req.body;
        const user = await User.findByIdAndUpdate(
            req.params.id,
            { team },
            { new: true, runValidators: true }
        ).select('-password');

        if (!user) return next(new CustomError('User not found', 404));

        logger.info(`Admin assigned user ${user.email} to team ${team}`);
        res.status(200).json({ success: true, data: user });
    } catch (err) {
        logger.error(`Admin assign user to team failed: ${err.message}`);
        next(err);
    }
};
