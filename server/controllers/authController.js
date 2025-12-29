'use strict';
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const asyncHandler = require('express-async-handler');
const User = require('../models/userModel');

// Generate JWT
const generateToken = (id) => {
    return jwt.sign({ id }, process.env.JWT_SECRET || 'devsecret', { expiresIn: '30d' });
};

// @desc    Login User
// @route   POST /api/auth/login
exports.login = asyncHandler(async (req, res) => {
    const { email, password } = req.body;
    
    // Explicitly select password
    const user = await User.findOne({ email }).select('+password');

    if (user && (await bcrypt.compare(password, user.password))) {
        // ✅ FIX: Send structure matching frontend expectation
        res.json({
            success: true,
            accessToken: generateToken(user._id), // Renamed from 'token'
            user: {                               // Nested object
                _id: user._id,
                name: user.name,
                email: user.email,
                role: user.role
            }
        });
    } else {
        res.status(401);
        throw new Error('Invalid email or password');
    }
});

// @desc    Register User
// @route   POST /api/auth/register
exports.register = asyncHandler(async (req, res) => {
    const { name, email, password, role } = req.body;
    if (!name || !email || !password) {
        res.status(400); throw new Error('Please add all fields');
    }

    const userExists = await User.findOne({ email });
    if (userExists) {
        res.status(400); throw new Error('User already exists');
    }

    const user = await User.create({ name, email, password, role });

    if (user) {
        res.status(201).json({
            success: true,
            accessToken: generateToken(user._id),
            user: {
                _id: user._id,
                name: user.name,
                email: user.email,
                role: user.role
            }
        });
    } else {
        res.status(400); throw new Error('Invalid user data');
    }
});

// @desc    Get Me
// @route   GET /api/auth/me
exports.getMe = asyncHandler(async (req, res) => {
    const user = await User.findById(req.user.id);
    res.status(200).json({
        success: true,
        user: user
    });
});

exports.logout = asyncHandler(async (req, res) => {
    res.status(200).json({ success: true, message: 'Logged out' });
});
