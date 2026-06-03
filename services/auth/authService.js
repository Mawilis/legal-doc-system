/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN IDENTITY PROVIDER [V43.1.0-FORTRESS]                                                                              ║
 * ║ [JWT + REFRESH TOKEN | ROLE ISOLATION | BIOMETRIC READY | FORENSIC LOGGING]                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 43.1.0-FORTRESS | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                  ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/services/auth/authService.js                                                     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import dotenv from 'dotenv';
import User from '../../server/models/userModel.js';
import { broadcastTelemetry } from '../../server/utils/telemetryHelper.js';

dotenv.config();

const router = express.Router();

const JWT_SECRET = process.env.JWT_SECRET || 'WILSY-SOVEREIGN-DEFAULT-CHANGE-IN-PRODUCTION';
const JWT_EXPIRES = process.env.JWT_EXPIRES || '8h';
const REFRESH_EXPIRES = process.env.REFRESH_EXPIRES || '7d';

// ====================== TOKEN GENERATORS ======================
const generateAccessToken = (user) => {
  return jwt.sign(
    {
      id: user._id,
      email: user.email,
      role: user.role,
      tenantId: user.tenantId
    },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES }
  );
};

const generateRefreshToken = (user) => {
  return jwt.sign(
    { id: user._id },
    JWT_SECRET,
    { expiresIn: REFRESH_EXPIRES }
  );
};

// ====================== REGISTER ======================
router.post('/register', async (req, res) => {
  try {
    const { firstName, lastName, email, password, role, tenantId } = req.body;

    if (!firstName || !lastName || !email || !password) {
      return res.status(400).json({ success: false, message: 'Missing required fields' });
    }

    const existing = await User.findOne({ email });
    if (existing) {
      return res.status(409).json({ success: false, message: 'Email already registered' });
    }

    const newUser = await User.create({
      firstName,
      lastName,
      email,
      password,
      role: role || 'user',
      tenantId: tenantId || 'WILSY_ROOT'
    });

    await newUser.appendForensicEntry('USER_REGISTRATION', 'SYSTEM', { email });

    const accessToken = generateAccessToken(newUser);
    const refreshToken = generateRefreshToken(newUser);

    res.status(201).json({
      success: true,
      message: 'Sovereign Identity Anchored',
      accessToken,
      refreshToken,
      user: {
        id: newUser._id,
        firstName: newUser.firstName,
        lastName: newUser.lastName,
        email: newUser.email,
        role: newUser.role,
        tenantId: newUser.tenantId
      }
    });

    await broadcastTelemetry(tenantId || 'WILSY_ROOT', 'IDENTITY', 'USER_REGISTERED', 'AuthService', { userId: newUser._id });

  } catch (err) {
    console.error('Register Error:', err);
    res.status(500).json({ success: false, message: 'Registration fracture occurred' });
  }
});

// ====================== LOGIN ======================
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    const user = await User.findOne({ email }).select('+password');
    if (!user || !user.isActive) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    if (user.isLocked && user.isLocked()) {
      return res.status(423).json({ success: false, message: 'Account temporarily locked' });
    }

    const isMatch = await user.matchPassword(password);
    if (!isMatch) {
      await user.incrementFailures();
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    // Reset failures on successful login
    user.securityMetadata.failedAttempts = 0;
    user.securityMetadata.lastLogin = new Date();
    await user.save();

    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user);

    await user.appendForensicEntry('LOGIN_SUCCESS', 'USER', { ip: req.ip });

    res.json({
      success: true,
      accessToken,
      refreshToken,
      user: {
        id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        role: user.role,
        tenantId: user.tenantId,
        securityClearance: user.securityClearance
      }
    });

  } catch (err) {
    console.error('Login Error:', err);
    res.status(500).json({ success: false, message: 'Authentication fracture' });
  }
});

// ====================== REFRESH TOKEN ======================
router.post('/refresh', async (req, res) => {
  const { refreshToken } = req.body;

  if (!refreshToken) return res.status(401).json({ success: false, message: 'Refresh token required' });

  try {
    const decoded = jwt.verify(refreshToken, JWT_SECRET);
    const user = await User.findById(decoded.id);

    if (!user || !user.isActive) {
      return res.status(401).json({ success: false, message: 'Invalid refresh token' });
    }

    const newAccessToken = generateAccessToken(user);
    const newRefreshToken = generateRefreshToken(user);

    res.json({
      success: true,
      accessToken: newAccessToken,
      refreshToken: newRefreshToken
    });
  } catch (err) {
    res.status(401).json({ success: false, message: 'Invalid or expired refresh token' });
  }
});

// ====================== ME (Session Hydration) ======================
router.get('/me', async (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) return res.status(401).json({ success: false, message: 'No token provided' });

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    const user = await User.findById(decoded.id).select('-password -recoverySeedHash');

    if (!user) return res.status(404).json({ success: false, message: 'User not found' });

    res.json({ success: true, user });
  } catch (err) {
    res.status(401).json({ success: false, message: 'Invalid token' });
  }
});

export default router;
