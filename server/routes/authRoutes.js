// File: server/routes/authRoutes.js
// -----------------------------------------------------------------------------
// COLLABORATION NOTES:
// - Auth routes for login and refresh.
// - Login issues an accessToken (short‑lived).
// - Refresh issues a new accessToken by validating a refresh token (HttpOnly cookie).
// - In production, store refresh tokens securely (DB or cache) and rotate them.
// -----------------------------------------------------------------------------

'use strict';

const express = require('express');
const jwt = require('jsonwebtoken');
const router = express.Router();

const JWT_SECRET = process.env.JWT_SECRET || 'your_billion_dollar_secret_key';
const REFRESH_SECRET = process.env.REFRESH_SECRET || 'your_refresh_secret_key';
const ACCESS_TTL_SEC = parseInt(process.env.ACCESS_TTL_SEC || '1800', 10); // 30 min
const REFRESH_TTL_SEC = parseInt(process.env.REFRESH_TTL_SEC || '1209600', 10); // 14 days

// Mock user lookup (replace with real DB)
async function findUserByEmail(email) {
    // Example user
    return { id: 'u123', email, tenantId: '650c1f1e1f1e1f1e1f1e1f1e', role: 'sheriff' };
}

function signAccessToken(user) {
    return jwt.sign({ sub: user.id, email: user.email, tenantId: user.tenantId, role: user.role }, JWT_SECRET, { expiresIn: ACCESS_TTL_SEC });
}

function signRefreshToken(user) {
    return jwt.sign({ sub: user.id }, REFRESH_SECRET, { expiresIn: REFRESH_TTL_SEC });
}

// Login: returns access token + sets refresh cookie
router.post('/login', express.json(), async (req, res) => {
    const { email, password } = req.body || {};
    if (!email || !password) return res.status(400).json({ message: 'Email and password required' });

    const user = await findUserByEmail(email);
    // TODO: verify password securely
    if (!user) return res.status(401).json({ message: 'Invalid credentials' });

    const accessToken = signAccessToken(user);
    const refreshToken = signRefreshToken(user);

    // HttpOnly refresh cookie
    res.cookie('rt', refreshToken, {
        httpOnly: true,
        secure: false, // set true behind TLS in production
        sameSite: 'lax',
        maxAge: REFRESH_TTL_SEC * 1000
    });

    return res.json({ accessToken, user, tenantId: user.tenantId });
});

// Refresh: issues new access token using HttpOnly refresh cookie
router.post('/refresh', async (req, res) => {
    const refreshToken = req.cookies?.rt;
    if (!refreshToken) return res.status(401).json({ message: 'No refresh token' });

    try {
        const decoded = jwt.verify(refreshToken, REFRESH_SECRET);
        // TODO: fetch user by decoded.sub and validate token rotation/revocation
        const user = { id: decoded.sub, email: 'placeholder@example.com', tenantId: '650c1f1e1f1e1f1e1f1e1f1e', role: 'sheriff' };
        const accessToken = signAccessToken(user);
        return res.json({ accessToken, user, tenantId: user.tenantId });
    } catch (err) {
        console.error('🔴 [AuthRoutes] Refresh failed:', err.message);
        return res.status(401).json({ message: 'Invalid refresh token' });
    }
});

module.exports = router;
