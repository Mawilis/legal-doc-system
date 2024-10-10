const User = require('../models/userModel');
const CustomError = require('../utils/customError');

// Create a new user (Admin-Only)
const createUser = async (req, res, next) => {
    console.log('Inside createUser function');
    try {
        const { name, email, password, role } = req.body;
        const user = new User({ name, email, password, role });
        await user.save();
        // Emit the 'user-created' event using req.io if it's set up correctly
        if (req.io) {
            req.io.emit('user-created', user);
        } else {
            console.warn("Socket.IO not available. 'user-created' event not emitted.");
        }

        res.status(201).json(user);
    } catch (err) {
        console.error('Error in createUser function:', err);
        next(new CustomError('Failed to create user', 500));
    }
};

// Get all users (Admin-Only)
const getAllUsers = async (req, res, next) => {
    console.log('Inside getAllUsers function');
    try {
        const users = await User.find({});
        res.status(200).json(users);
    } catch (err) {
        console.error('Error in getAllUsers function:', err);
        next(new CustomError('Failed to fetch users', 500));
    }
};

// Get user by ID (Admin-Only)
const getUserById = async (req, res, next) => {
    console.log('Inside getUserById function');
    try {
        const user = await User.findById(req.params.userId);
        if (!user) return next(new CustomError('User not found', 404));
        res.status(200).json(user);
    } catch (err) {
        console.error('Error in getUserById function:', err);
        next(err);
    }
};

// Update user (Admin-Only)
const updateUser = async (req, res, next) => {
    console.log('Inside updateUser function');
    try {
        const user = await User.findByIdAndUpdate(req.params.userId, req.body, { new: true });
        if (!user) return next(new CustomError('User not found', 404));

        req.io.emit('user-updated', user);  // Real-time update
        res.status(200).json(user);
    } catch (err) {
        console.error('Error in updateUser function:', err);
        next(err);
    }
};

// Delete user (Admin-Only)
const deleteUser = async (req, res, next) => {
    console.log('Inside deleteUser function');
    try {
        const user = await User.findByIdAndDelete(req.params.userId);
        if (!user) return next(new CustomError('User not found', 404));

        req.io.emit('user-deleted', user);  // Real-time update
        res.status(200).json({ message: 'User deleted' });
    } catch (err) {
        console.error('Error in deleteUser function:', err);
        next(err);
    }
};

// Export all functions as an object
module.exports = {
    createUser,
    getAllUsers,
    getUserById,
    updateUser,
    deleteUser
};