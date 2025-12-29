/**
 * File: services/auth/index.js
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - Purpose: Auth microservice, Express 5.0 + Node 25 compatible.
 * - Fix: Removed deprecated wildcard `*` routes. Using regex `(.*)` for catch‑all.
 * - CORS: Registered first so Express 5 handles OPTIONS preflight automatically.
 * - Engineers:
 *   • Replace mock login logic with real User.findOne + bcrypt.
 *   • JWT_SECRET must match Gateway for token verification.
 *   • In production, set cookie `secure: true` behind TLS.
 * -----------------------------------------------------------------------------
 */

'use strict';

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const mongoose = require('mongoose');

// --- CONFIGURATION ---
const PORT = process.env.PORT || 4000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/legal-tech';
const JWT_SECRET = process.env.JWT_SECRET || 'your_billion_dollar_secret_key';

// --- APP INIT ---
const app = express();

// --- MIDDLEWARE (Bleeding Edge Fix) ---
app.use(cors({
    origin: [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:3001',
        'http://127.0.0.1:3001'
    ],
    credentials: true,
    methods: ['GET', 'POST', 'OPTIONS']
}));

app.use(express.json());
app.use(cookieParser());

// --- DATABASE ---
mongoose.connect(MONGO_URI)
    .then(() => console.log('✅ [Auth Service] DB Connected'))
    .catch(err => console.error('❌ [Auth Service] DB Error:', err.message));

// --- ROUTES ---

/**
 * @route   POST /login
 * @desc    Authenticate user & issue JWT
 */
app.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        // Demo logic: replace with User.findOne + bcrypt.compare
        if (email === 'wilsonkhanyezi@gmail.com') {
            const token = jwt.sign(
                {
                    id: 'user_123',
                    email,
                    role: 'admin',
                    tenantId: '650c1f1e1f1e1f1e1f1e1f1e'
                },
                JWT_SECRET,
                { expiresIn: '24h' }
            );

            res.cookie('token', token, { httpOnly: true, secure: false }); // secure: true in prod

            return res.status(200).json({
                success: true,
                token,
                user: { email, name: 'Wilson Khanyezi', role: 'admin' }
            });
        }

        res.status(401).json({ message: 'Invalid credentials' });
    } catch (error) {
        console.error('Login Error:', error);
        res.status(500).json({ message: 'Internal Server Error' });
    }
});

/**
 * @route   POST /verify
 * @desc    Internal validation endpoint for Gateway/Microservices
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

// --- GLOBAL ERROR HANDLER (Express 5 Catch-All) ---
app.all(/(.*)/, (req, res) => {
    res.status(404).json({ message: 'Auth Endpoint Not Found' });
});

// --- START SERVER ---
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🔑 [Auth Service] Online on Port ${PORT} (Express 5.0)`);
});
