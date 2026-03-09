/**
 * File: services/auth/index.js
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Identity Provider (IdP) Microservice
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - The Central Authority for Identity.
 * - SECURITY: Bcrypt hashing, JWT issuance, Cookie/Header support.
 * - ROUTES: Login, Register, Verify, Session Hydration (/me).
 * - SCHEMA: Defines User model internally to ensure standalone stability.
 * -----------------------------------------------------------------------------
 */

'use strict';

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs'); // Ensure 'bcryptjs' is installed
const mongoose = require('mongoose');

// --- CONFIGURATION ---
const PORT = process.env.AUTH_PORT || 4000;
const MONGO_URI = process.env.MONGO_URI || process.env.MONGODB_URI   POST /register
 * @desc    Create a new account (Bootstrap)
 */
app.post('/register', async (req, res) => {
    try {
        const { name, email, password, role, tenantId } = req.body;

        const existing = await User.findOne({ email });
        if (existing) return res.status(400).json({ message: 'Email already exists' });

        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        const newUser = await User.create({
            name,
            email,
            password: hashedPassword,
            role: role || 'lawyer',
            tenantId: tenantId || 'default'
        });

        const token = generateToken(newUser);

        res.status(201).json({
            success: true,
            token,
            user: {
                id: newUser._id,
                name: newUser.name,
                email: newUser.email,
                role: newUser.role,
                tenantId: newUser.tenantId
            }
        });
        console.log(`👤 [Auth] New User Registered: ${email}`);

    } catch (err) {
        console.error('Register Error:', err);
        res.status(500).json({ message: 'Registration failed' });
    }
});

/**
 * @route   POST /login
 * @desc    Authenticate user & issue JWT
 */
app.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        // 1. Find User
        const user = await User.findOne({ email });
        if (!user) return res.status(401).json({ message: 'Invalid credentials' });

        // 2. Verify Password
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) return res.status(401).json({ message: 'Invalid credentials' });

        // 3. Issue Token
        const token = generateToken(user);

        // Update Last Login
        user.lastLogin = new Date();
        await user.save();

        res.cookie('token', token, { httpOnly: true, secure: false });

        res.json({
            success: true,
            token,
            user: {
                id: user._id,
                name: user.name,
                email: user.email,
                role: user.role,
                tenantId: user.tenantId
            }
        });
        console.log(`🔓 [Auth] Login Success: ${email} (${user.role})`);

    } catch (err) {
        console.error('Login Error:', err);
        res.status(500).json({ message: 'Login service error' });
    }
});

/**
 * @route   GET /me
 * @desc    Hydrate session context (Used by AuthContext)
 */
app.get('/me', async (req, res) => {
    const token = req.headers.authorization?.split(' ')[1] || req.cookies.token;
    if (!token) return res.status(401).json({ message: 'No token provided' });

    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        const user = await User.findById(decoded.id).select('-password');

        if (!user) return res.status(404).json({ message: 'User not found' });

        res.json(user);
    } catch (err) {
        res.status(401).json({ message: 'Invalid token' });
    }
});

/**
 * @route   POST /verify
 * @desc    Internal validation endpoint for Gateway
 */
app.post('/verify', (req, res) => {
    const token = req.body.token || req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ valid: false });

    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        res.json({ valid: true, user: decoded });
    } catch (e) {
        res.status(401).json({ valid: false });
    }
});

// --- ERROR HANDLING ---
app.all(/(.*)/, (req, res) => {
    res.status(404).json({ message: 'Auth Service: Endpoint Not Found' });
});

// --- BOOTSTRAP ---
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🔑 [Auth Service] Active on Port ${PORT}`);
});